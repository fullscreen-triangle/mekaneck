"""
ConsciousnessValidator: Validates consciousness equations.

Tests C = P_decay ∩ T_decay and consciousness dynamics.
"""

from typing import Dict, Any
import numpy as np
from pathlib import Path

from .base_validator import BaseValidator
from ..core.types import MentalState, SCoord
from ..operators.neural_ops import CONSCIOUSNESS, evolve_mental_state, consciousness_time_series
from ..engine.poincare_computer import PoincareComputer


class ConsciousnessValidator(BaseValidator):
    """
    Validates consciousness equations.

    Tests:
    1. Consciousness = P_decay * T_decay * gamma * gamma_f
    2. Consciousness in [0, 1]
    3. Dream state (P_decay = 0 implies C = 0)
    4. Awake state (high P_decay implies high C)
    5. Consciousness emergence from Kuramoto synchronization
    """

    def __init__(
        self,
        simulation_time: float = 10.0,
        output_dir: Path = None,
    ):
        super().__init__(output_dir)
        self.simulation_time = simulation_time

    def test_consciousness_formula(self) -> Dict[str, Any]:
        """Test C = P_decay * T_decay * gamma * gamma_f."""
        n_tests = 100
        all_correct = True

        for _ in range(n_tests):
            p_decay = np.random.uniform(0, 1)
            t_decay = np.random.uniform(0, 1)
            gamma = np.random.uniform(0, 1)
            gamma_f = np.random.uniform(0, 1)

            expected = p_decay * t_decay * gamma * gamma_f
            actual = CONSCIOUSNESS(p_decay, t_decay, gamma, gamma_f)

            if abs(expected - actual) > 1e-10:
                all_correct = False
                break

        return {"n_tests": n_tests, "formula_correct": all_correct}

    def test_consciousness_bounds(self) -> Dict[str, Any]:
        """Test that consciousness is always in [0, 1]."""
        n_tests = 100
        all_in_bounds = True

        for _ in range(n_tests):
            state = MentalState(
                gamma=np.random.uniform(0, 1),
                gamma_f=np.random.uniform(0, 1),
                M=np.random.uniform(-10, 10),
                p_decay=np.random.uniform(0, 1),
                t_decay=np.random.uniform(0, 1),
            )

            if not (0 <= state.consciousness <= 1):
                all_in_bounds = False
                break

        return {"n_tests": n_tests, "all_in_bounds": all_in_bounds}

    def test_dream_state(self) -> Dict[str, Any]:
        """Test that P_decay = 0 implies near-zero consciousness."""
        state = MentalState(
            gamma=0.9,
            gamma_f=0.9,
            M=0.0,
            p_decay=0.0,  # Dream state
            t_decay=0.9,
        )

        return {
            "p_decay": state.p_decay,
            "consciousness": state.consciousness,
            "is_dreaming": state.is_dreaming,
            "consciousness_near_zero": state.consciousness < 0.01,
        }

    def test_awake_state(self) -> Dict[str, Any]:
        """Test that high P_decay gives high consciousness."""
        state = MentalState(
            gamma=0.9,
            gamma_f=0.9,
            M=0.0,
            p_decay=1.0,  # Fully awake
            t_decay=0.9,
        )

        return {
            "p_decay": state.p_decay,
            "consciousness": state.consciousness,
            "is_awake": state.is_awake,
            "consciousness_high": state.consciousness > 0.5,
        }

    def test_consciousness_emergence(self) -> Dict[str, Any]:
        """Test consciousness emergence from Kuramoto synchronization."""
        computer = PoincareComputer(n_oscillators=50, coupling_strength=1.0)

        initial_state = MentalState.initial(
            s_coord=SCoord(sk=0.5, st=0.5, se=0.5)
        )

        result = computer.compute_consciousness(
            initial_state,
            target_consciousness=0.7,
            max_iterations=500,
        )

        return {
            "target": 0.7,
            "achieved": result.final_state.consciousness,
            "success": result.success,
            "iterations": result.iterations,
        }

    def run_validation(self) -> Dict[str, Any]:
        """Run complete consciousness validation."""
        print("=" * 70)
        print("CONSCIOUSNESS VALIDATION")
        print("=" * 70)

        print("\n1. Testing consciousness formula...")
        formula_results = self.test_consciousness_formula()

        print("2. Testing consciousness bounds...")
        bounds_results = self.test_consciousness_bounds()

        print("3. Testing dream state...")
        dream_results = self.test_dream_state()

        print("4. Testing awake state...")
        awake_results = self.test_awake_state()

        print("5. Testing consciousness emergence...")
        emergence_results = self.test_consciousness_emergence()

        claims_validated = {
            "formula_correct": formula_results["formula_correct"],
            "always_in_bounds": bounds_results["all_in_bounds"],
            "dream_gives_low_C": dream_results["consciousness_near_zero"],
            "awake_gives_high_C": awake_results["consciousness_high"],
            "emergence_works": emergence_results["success"],
        }

        results = self._create_result_dict(
            parameters={"simulation_time": self.simulation_time},
            results={
                "formula": formula_results,
                "bounds": bounds_results,
                "dream": dream_results,
                "awake": awake_results,
                "emergence": emergence_results,
            },
            claims_validated=claims_validated,
        )

        self.save_results(results)
        self.print_summary(results)

        return results
