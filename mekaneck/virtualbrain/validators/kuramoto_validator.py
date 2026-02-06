"""
KuramotoValidator: Validates Kuramoto synchronization dynamics.

Tests the Kuramoto model implementation and phase coherence computation.
"""

from typing import Dict, Any
import numpy as np
from pathlib import Path

from .base_validator import BaseValidator
from ..operators.dynamics_ops import (
    KuramotoState,
    KURAMOTO,
    PHASE_LOCK,
    simulate_kuramoto,
    critical_coupling,
)


class KuramotoValidator(BaseValidator):
    """
    Validates Kuramoto oscillator dynamics.

    Tests:
    1. Phase coherence computation (R in [0, 1])
    2. Synchronization onset above critical coupling
    3. Desynchronization below critical coupling
    4. Order parameter convergence
    """

    def __init__(
        self,
        n_oscillators: int = 100,
        simulation_time: float = 10.0,
        output_dir: Path = None,
    ):
        super().__init__(output_dir)
        self.n_oscillators = n_oscillators
        self.simulation_time = simulation_time

    def test_phase_coherence_bounds(self) -> Dict[str, Any]:
        """Test that R is always in [0, 1]."""
        all_valid = True
        n_tests = 100

        for _ in range(n_tests):
            phases = np.random.uniform(0, 2 * np.pi, self.n_oscillators)
            R, Psi = PHASE_LOCK(phases)

            if not (0 <= R <= 1):
                all_valid = False
                break

        # Test edge cases
        uniform = np.zeros(self.n_oscillators)  # All same phase
        R_uniform, _ = PHASE_LOCK(uniform)

        spread = np.linspace(0, 2 * np.pi, self.n_oscillators, endpoint=False)
        R_spread, _ = PHASE_LOCK(spread)

        return {
            "random_tests": n_tests,
            "all_valid": all_valid,
            "R_uniform": float(R_uniform),
            "R_spread": float(R_spread),
            "uniform_near_1": abs(R_uniform - 1.0) < 0.01,
            "spread_near_0": R_spread < 0.1,
        }

    def test_synchronization_onset(self) -> Dict[str, Any]:
        """Test synchronization above critical coupling."""
        frequency_std = 2.0
        K_c = critical_coupling(frequency_std, self.n_oscillators)

        # Above critical
        state_above = KuramotoState.random(
            self.n_oscillators,
            frequency_std=frequency_std,
            coupling=K_c * 2,
        )

        times, R_above, _ = simulate_kuramoto(state_above, self.simulation_time, dt=0.01)
        final_R_above = R_above[-1]

        # Below critical
        state_below = KuramotoState.random(
            self.n_oscillators,
            frequency_std=frequency_std,
            coupling=K_c * 0.5,
        )

        times, R_below, _ = simulate_kuramoto(state_below, self.simulation_time, dt=0.01)
        final_R_below = R_below[-1]

        return {
            "critical_coupling": float(K_c),
            "coupling_above": float(K_c * 2),
            "coupling_below": float(K_c * 0.5),
            "R_final_above": float(final_R_above),
            "R_final_below": float(final_R_below),
            "synchronized_above": final_R_above > 0.5,
            "desynchronized_below": final_R_below < 0.5,
        }

    def test_order_parameter_convergence(self) -> Dict[str, Any]:
        """Test that order parameter converges."""
        state = KuramotoState.random(self.n_oscillators, coupling=1.0)

        times, R_values, _ = simulate_kuramoto(state, self.simulation_time * 2, dt=0.01)

        # Check convergence: variance in last quarter should be small
        n_points = len(R_values)
        last_quarter = R_values[3 * n_points // 4 :]
        variance = np.var(last_quarter)

        return {
            "final_R": float(R_values[-1]),
            "variance_last_quarter": float(variance),
            "converged": variance < 0.01,
        }

    def run_validation(self) -> Dict[str, Any]:
        """Run complete Kuramoto validation."""
        print("=" * 70)
        print("KURAMOTO DYNAMICS VALIDATION")
        print("=" * 70)

        print("\n1. Testing phase coherence bounds...")
        bounds_results = self.test_phase_coherence_bounds()

        print("2. Testing synchronization onset...")
        sync_results = self.test_synchronization_onset()

        print("3. Testing order parameter convergence...")
        convergence_results = self.test_order_parameter_convergence()

        claims_validated = {
            "coherence_in_bounds": bounds_results["all_valid"],
            "uniform_gives_R_1": bounds_results["uniform_near_1"],
            "spread_gives_R_0": bounds_results["spread_near_0"],
            "sync_above_critical": sync_results["synchronized_above"],
            "desync_below_critical": sync_results["desynchronized_below"],
            "order_param_converges": convergence_results["converged"],
        }

        results = self._create_result_dict(
            parameters={
                "n_oscillators": self.n_oscillators,
                "simulation_time": self.simulation_time,
            },
            results={
                "bounds": bounds_results,
                "synchronization": sync_results,
                "convergence": convergence_results,
            },
            claims_validated=claims_validated,
        )

        self.save_results(results)
        self.print_summary(results)

        return results
