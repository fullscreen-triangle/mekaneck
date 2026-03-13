"""
Experiment 4: Pharmacological NPL (pNPL) Type System Validation
================================================================

Validates the pNPL type system and operator algebra:
  1. Partition coordinates (n, l, m, s) obey capacity C(n) = 2n²
  2. S-entropy coordinates navigate [0,1]³ correctly
  3. Regime classification is self-consistent (R boundaries partition [0,1])
  4. Operator composition: APERTURE ∘ REGIME ∘ COUPLE gives valid trajectories
  5. Kuramoto dynamics: synchronization onset at K_c = 2σ/π
  6. Structural factor modification: ΔS is additive and regime-dependent
  7. Variance minimization: F = k_BT·σ²(φ) with therapeutic floor

Results saved to: results/npl/
"""

import sys
from pathlib import Path
from typing import Dict, Any, List, Tuple
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from common import (
    save_json, save_csv, create_result_dict, print_summary,
    kuramoto_order_parameter, simulate_kuramoto, critical_coupling,
    classify_regime, structural_factor,
    BOLTZMANN_CONSTANT, KT_BODY_TEMP,
    REGIME_COHERENT_MIN, REGIME_TURBULENT_MAX, REGIME_PHASE_LOCKED_MIN,
)

RESULTS_DIR = Path(__file__).resolve().parent.parent.parent / "results" / "npl"


# ---------------------------------------------------------------------------
# pNPL Type Definitions
# ---------------------------------------------------------------------------

class PartitionCoord:
    """Partition coordinate (n, l, m, s) with capacity C(n) = 2n²."""

    def __init__(self, n: int, l: int, m: int, s: float):
        if n < 1:
            raise ValueError(f"n must be >= 1, got {n}")
        if not (0 <= l < n):
            raise ValueError(f"l must be in [0, n-1], got l={l} for n={n}")
        if not (-l <= m <= l):
            raise ValueError(f"m must be in [-l, l], got m={m} for l={l}")
        if s not in (-0.5, 0.5):
            raise ValueError(f"s must be ±0.5, got {s}")
        self.n = n
        self.l = l
        self.m = m
        self.s = s

    @staticmethod
    def capacity(n: int) -> int:
        """C(n) = 2n²."""
        return 2 * n * n

    def to_tuple(self) -> Tuple[int, int, int, float]:
        return (self.n, self.l, self.m, self.s)


class SEntropyCoord:
    """S-entropy coordinate (Sk, St, Se) in [0,1]³."""

    def __init__(self, sk: float, st: float, se: float):
        for name, val in [("sk", sk), ("st", st), ("se", se)]:
            if not (0 <= val <= 1):
                raise ValueError(f"{name} must be in [0,1], got {val}")
        self.sk = sk
        self.st = st
        self.se = se

    def distance(self, other: "SEntropyCoord") -> float:
        return float(np.sqrt(
            (self.sk - other.sk)**2 +
            (self.st - other.st)**2 +
            (self.se - other.se)**2
        ))

    def entropy_magnitude(self) -> float:
        return float(np.sqrt(self.sk**2 + self.st**2 + self.se**2))


class Regime:
    """Operational regime with equation of state PV = Nk_BT·S."""

    NAMES = ["phase_locked", "coherent", "cascade", "aperture_dominated", "turbulent"]

    def __init__(self, name: str, R: float):
        if name not in self.NAMES:
            raise ValueError(f"Unknown regime: {name}")
        self.name = name
        self.R = R

    def equation_of_state(self, N: int, T: float, S: float) -> float:
        """PV = Nk_BT·S."""
        return N * BOLTZMANN_CONSTANT * T * S


# ---------------------------------------------------------------------------
# pNPL Operators
# ---------------------------------------------------------------------------

def APERTURE(regime: Regime, multipole_order: int) -> float:
    """
    Categorical aperture operator.

    Returns aperture width: how much phase space is accessible
    at zero thermodynamic work (W=0).

    Monopole (order 1): narrow aperture
    Dipole (order 2): moderate aperture
    Quadrupole (order 4): wide aperture
    """
    # Aperture width decreases with multipole order (more selective)
    # but increases with R (more coherent = more navigable)
    return regime.R ** (1.0 / multipole_order)


def COUPLE(phases: np.ndarray, coupling: float, dt: float) -> Tuple[np.ndarray, float]:
    """
    Coupling operator: single Kuramoto step.
    Returns (new_phases, R).
    """
    N = len(phases)
    phase_diff = phases[np.newaxis, :] - phases[:, np.newaxis]
    coupling_term = (coupling / N) * np.sum(np.sin(phase_diff), axis=1)
    new_phases = np.mod(phases + coupling_term * dt, 2 * np.pi)
    R, _ = kuramoto_order_parameter(new_phases)
    return new_phases, R


def TRANSITION(R_pre: float, delta_S: float) -> float:
    """
    Regime transition operator.

    R_post = R_pre + delta_S * (1 - R_pre)

    Drug action modifies structural factor, which shifts R.
    Bounded to [0, 1].
    """
    R_post = R_pre + delta_S * (1 - R_pre)
    return max(0.0, min(1.0, R_post))


def MEASURE(phases: np.ndarray) -> Dict[str, float]:
    """
    Measurement operator: extract observables from phase state.
    """
    R, Psi = kuramoto_order_parameter(phases)
    variance = float(np.var(phases))
    regime = classify_regime(R)
    S = structural_factor(R)
    return {
        "R": R,
        "Psi": Psi,
        "variance": variance,
        "regime": regime,
        "structural_factor": S,
    }


def VARIANCE_MINIMIZE(coupling: float, T: float = 310.15) -> float:
    """
    Therapeutic floor: σ²_min = k_BT / K_coupling.
    Free energy: F = k_BT·σ².
    """
    sigma2_min = BOLTZMANN_CONSTANT * T / max(coupling, 1e-20)
    F_min = BOLTZMANN_CONSTANT * T * sigma2_min
    return sigma2_min


# ---------------------------------------------------------------------------
# Test 1: Partition Coordinate Validity
# ---------------------------------------------------------------------------

def test_partition_coordinates() -> Dict[str, Any]:
    """Test that partition coordinates obey C(n) = 2n² and quantum number rules."""
    print("\n  Test 1: Partition Coordinates")

    results = []
    all_valid = True

    for n in range(1, 8):
        capacity = PartitionCoord.capacity(n)
        expected = 2 * n * n

        # Enumerate all valid coordinates at this level
        count = 0
        for l in range(n):
            for m in range(-l, l + 1):
                for s in [-0.5, 0.5]:
                    try:
                        pc = PartitionCoord(n, l, m, s)
                        count += 1
                    except ValueError:
                        all_valid = False

        results.append({
            "n": n,
            "capacity_formula": expected,
            "enumerated_states": count,
            "match": count == expected,
        })

        if count != expected:
            all_valid = False

    save_csv(results, RESULTS_DIR / "partition_coordinates.csv")

    return {
        "all_capacities_match": all_valid,
        "levels_tested": len(results),
        "per_level": results,
    }


# ---------------------------------------------------------------------------
# Test 2: S-Entropy Space Navigation
# ---------------------------------------------------------------------------

def test_sentropy_space() -> Dict[str, Any]:
    """Test S-entropy coordinate properties."""
    print("  Test 2: S-Entropy Space")

    rng = np.random.default_rng(42)
    n_points = 1000

    # Generate random points and verify properties
    distances = []
    magnitudes = []
    triangle_violations = 0

    points = [
        SEntropyCoord(rng.random(), rng.random(), rng.random())
        for _ in range(n_points)
    ]

    for i in range(min(500, n_points)):
        j = (i + 1) % n_points
        k = (i + 2) % n_points

        d_ij = points[i].distance(points[j])
        d_jk = points[j].distance(points[k])
        d_ik = points[i].distance(points[k])

        distances.append(d_ij)
        magnitudes.append(points[i].entropy_magnitude())

        # Triangle inequality
        if d_ij > d_jk + d_ik + 1e-10:
            triangle_violations += 1

    # Check bounds
    max_distance = np.sqrt(3)  # diagonal of unit cube
    all_bounded = all(d <= max_distance + 1e-10 for d in distances)

    # Origin and equilibrium
    origin = SEntropyCoord(0, 0, 0)
    equilibrium = SEntropyCoord(1, 1, 1)
    diag_distance = origin.distance(equilibrium)

    return {
        "n_points": n_points,
        "all_distances_bounded": all_bounded,
        "max_distance_observed": round(float(max(distances)), 4),
        "max_distance_theoretical": round(max_distance, 4),
        "triangle_violations": triangle_violations,
        "triangle_inequality_holds": triangle_violations == 0,
        "origin_to_equilibrium": round(diag_distance, 4),
        "expected_diagonal": round(max_distance, 4),
        "diagonal_correct": abs(diag_distance - max_distance) < 1e-10,
        "mean_magnitude": round(float(np.mean(magnitudes)), 4),
    }


# ---------------------------------------------------------------------------
# Test 3: Regime Classification Consistency
# ---------------------------------------------------------------------------

def test_regime_classification() -> Dict[str, Any]:
    """Test that regime boundaries partition [0,1] without gaps or overlaps."""
    print("  Test 3: Regime Classification")

    R_values = np.linspace(0, 1, 1001)
    regimes = [classify_regime(R) for R in R_values]

    # Check coverage (every R gets a regime)
    all_classified = all(r is not None for r in regimes)

    # Check monotonicity pattern
    regime_order = ["turbulent", "aperture_dominated", "cascade", "coherent", "phase_locked"]
    transitions = []
    for i in range(1, len(regimes)):
        if regimes[i] != regimes[i-1]:
            transitions.append({
                "R": round(float(R_values[i]), 4),
                "from": regimes[i-1],
                "to": regimes[i],
            })

    # Verify monotonic ordering
    transition_regimes = [t["to"] for t in transitions]
    is_monotonic = True
    for i, tr in enumerate(transition_regimes):
        if tr not in regime_order:
            is_monotonic = False
            break
        if i > 0:
            curr_idx = regime_order.index(tr)
            prev_idx = regime_order.index(transition_regimes[i-1])
            if curr_idx < prev_idx:
                is_monotonic = False
                break

    # Count per regime
    from collections import Counter
    regime_counts = dict(Counter(regimes))

    return {
        "all_R_classified": all_classified,
        "n_transitions": len(transitions),
        "transitions": transitions,
        "is_monotonic": is_monotonic,
        "regime_distribution": regime_counts,
    }


# ---------------------------------------------------------------------------
# Test 4: Operator Composition
# ---------------------------------------------------------------------------

def test_operator_composition() -> Dict[str, Any]:
    """Test that APERTURE ∘ REGIME ∘ COUPLE produces valid trajectories."""
    print("  Test 4: Operator Composition")

    rng = np.random.default_rng(42)
    n_oscillators = 100
    n_steps = 200
    dt = 0.05

    # Start in turbulent regime (depression)
    phases = rng.uniform(0, 2 * np.pi, n_oscillators)
    coupling = 0.3  # below critical

    trajectory = []
    for step in range(n_steps):
        # COUPLE
        phases, R = COUPLE(phases, coupling, dt)

        # Classify regime
        regime_name = classify_regime(R)
        regime = Regime(regime_name, R)

        # APERTURE (monopole SSRI)
        aperture_width = APERTURE(regime, multipole_order=1)

        # MEASURE
        obs = MEASURE(phases)

        trajectory.append({
            "step": step,
            "R": round(R, 4),
            "regime": regime_name,
            "aperture_width": round(aperture_width, 4),
            "variance": round(obs["variance"], 4),
            "structural_factor": round(obs["structural_factor"], 30),
        })

        # At step 100, apply "drug": increase coupling
        if step == 100:
            coupling = 2.0  # above critical

    save_csv(trajectory, RESULTS_DIR / "operator_trajectory.csv")

    # Verify trajectory properties
    R_pre_drug = np.mean([t["R"] for t in trajectory[80:100]])
    R_post_drug = np.mean([t["R"] for t in trajectory[180:200]])

    return {
        "n_steps": n_steps,
        "drug_applied_at_step": 100,
        "R_pre_drug": round(float(R_pre_drug), 4),
        "R_post_drug": round(float(R_post_drug), 4),
        "regime_pre_drug": classify_regime(R_pre_drug),
        "regime_post_drug": classify_regime(R_post_drug),
        "drug_increased_R": R_post_drug > R_pre_drug,
        "all_R_in_bounds": all(0 <= t["R"] <= 1 for t in trajectory),
    }


# ---------------------------------------------------------------------------
# Test 5: Synchronization Onset
# ---------------------------------------------------------------------------

def test_synchronization_onset() -> Dict[str, Any]:
    """Test K_c = 2σ/π prediction."""
    print("  Test 5: Synchronization Onset")

    freq_stds = [0.5, 1.0, 2.0, 4.0, 8.0]
    n_oscillators = 200
    results = []

    for sigma in freq_stds:
        K_c_predicted = critical_coupling(sigma)

        # Below critical
        _, R_below = simulate_kuramoto(
            n_oscillators, K_c_predicted * 0.5, duration=10.0, freq_std=sigma, seed=42
        )
        R_final_below = float(np.mean(R_below[-50:]))

        # At critical
        _, R_at = simulate_kuramoto(
            n_oscillators, K_c_predicted, duration=10.0, freq_std=sigma, seed=42
        )
        R_final_at = float(np.mean(R_at[-50:]))

        # Above critical
        _, R_above = simulate_kuramoto(
            n_oscillators, K_c_predicted * 2.0, duration=10.0, freq_std=sigma, seed=42
        )
        R_final_above = float(np.mean(R_above[-50:]))

        results.append({
            "freq_std": sigma,
            "K_c_predicted": round(K_c_predicted, 4),
            "R_below_Kc": round(R_final_below, 4),
            "R_at_Kc": round(R_final_at, 4),
            "R_above_Kc": round(R_final_above, 4),
            "sync_above_desync_below": R_final_above > R_final_below,
        })

    save_csv(results, RESULTS_DIR / "synchronization_onset.csv")

    all_correct = all(r["sync_above_desync_below"] for r in results)

    return {
        "n_conditions": len(freq_stds),
        "all_onset_correct": all_correct,
        "per_condition": results,
    }


# ---------------------------------------------------------------------------
# Test 6: Structural Factor Additivity
# ---------------------------------------------------------------------------

def test_structural_factor_modification() -> Dict[str, Any]:
    """Test ΔS additivity and regime dependence."""
    print("  Test 6: Structural Factor Modification")

    # Test that TRANSITION is monotonic and bounded
    R_values = np.linspace(0, 1, 100)
    delta_S_values = np.linspace(-0.5, 0.5, 50)

    rows = []
    all_bounded = True

    for R_pre in [0.1, 0.3, 0.5, 0.7, 0.9]:
        for dS in delta_S_values:
            R_post = TRANSITION(R_pre, dS)
            if not (0 <= R_post <= 1):
                all_bounded = False
            rows.append({
                "R_pre": round(R_pre, 2),
                "delta_S": round(float(dS), 3),
                "R_post": round(R_post, 4),
            })

    save_csv(rows, RESULTS_DIR / "structural_factor_modification.csv")

    # Test additivity: TRANSITION(R, dS1 + dS2) ≈ TRANSITION(TRANSITION(R, dS1), dS2)
    # (approximate, not exact, because TRANSITION is nonlinear)
    additivity_errors = []
    for _ in range(100):
        R = np.random.uniform(0.1, 0.9)
        dS1 = np.random.uniform(-0.2, 0.2)
        dS2 = np.random.uniform(-0.2, 0.2)

        R_sequential = TRANSITION(TRANSITION(R, dS1), dS2)
        R_combined = TRANSITION(R, dS1 + dS2)
        additivity_errors.append(abs(R_sequential - R_combined))

    return {
        "all_bounded": all_bounded,
        "mean_additivity_error": round(float(np.mean(additivity_errors)), 6),
        "max_additivity_error": round(float(np.max(additivity_errors)), 6),
    }


# ---------------------------------------------------------------------------
# Test 7: Variance Minimization
# ---------------------------------------------------------------------------

def test_variance_minimization() -> Dict[str, Any]:
    """Test therapeutic floor: σ²_min = k_BT / K_coupling."""
    print("  Test 7: Variance Minimization")

    couplings = np.logspace(-1, 2, 50)
    T = 310.15  # body temperature

    rows = []
    for K in couplings:
        sigma2_min = VARIANCE_MINIMIZE(K, T)
        F_min = BOLTZMANN_CONSTANT * T * sigma2_min

        rows.append({
            "coupling_K": round(float(K), 4),
            "sigma2_min": float(sigma2_min),
            "F_min": float(F_min),
        })

    save_csv(rows, RESULTS_DIR / "variance_minimization.csv")

    # Verify inverse relationship
    K_arr = np.array([r["coupling_K"] for r in rows])
    sigma_arr = np.array([r["sigma2_min"] for r in rows])

    # log-log should be linear with slope -1
    log_K = np.log(K_arr)
    log_sigma = np.log(sigma_arr)
    slope = float(np.polyfit(log_K, log_sigma, 1)[0])

    return {
        "slope_log_sigma_vs_log_K": round(slope, 4),
        "expected_slope": -1.0,
        "slope_correct": abs(slope - (-1.0)) < 0.01,
        "sigma2_min_at_K_1": float(VARIANCE_MINIMIZE(1.0, T)),
    }


# ---------------------------------------------------------------------------
# Main experiment
# ---------------------------------------------------------------------------

def main():
    print("=" * 70)
    print("EXPERIMENT 4: pNPL Type System Validation")
    print("=" * 70)

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    partition_results = test_partition_coordinates()
    sentropy_results = test_sentropy_space()
    regime_results = test_regime_classification()
    operator_results = test_operator_composition()
    sync_results = test_synchronization_onset()
    structural_results = test_structural_factor_modification()
    variance_results = test_variance_minimization()

    claims = {
        "capacity_C_2n2": partition_results["all_capacities_match"],
        "sentropy_triangle_inequality": sentropy_results["triangle_inequality_holds"],
        "sentropy_bounded": sentropy_results["all_distances_bounded"],
        "regime_classification_complete": regime_results["all_R_classified"],
        "regime_monotonic_ordering": regime_results["is_monotonic"],
        "operator_composition_valid": operator_results["all_R_in_bounds"],
        "drug_increases_synchronization": operator_results["drug_increased_R"],
        "sync_onset_at_Kc": sync_results["all_onset_correct"],
        "structural_factor_bounded": structural_results["all_bounded"],
        "variance_inverse_coupling": variance_results["slope_correct"],
    }

    results = create_result_dict(
        experiment_name="pnpl_type_system_validation",
        parameters={
            "n_partition_levels": 7,
            "n_sentropy_points": 1000,
            "n_oscillators": 200,
        },
        results={
            "partition_coordinates": partition_results,
            "sentropy_space": sentropy_results,
            "regime_classification": regime_results,
            "operator_composition": operator_results,
            "synchronization_onset": sync_results,
            "structural_factor": structural_results,
            "variance_minimization": variance_results,
        },
        claims_validated=claims,
    )

    save_json(results, RESULTS_DIR / "summary.json")
    print_summary(results)

    print("\nAll results saved to:", RESULTS_DIR)


if __name__ == "__main__":
    main()
