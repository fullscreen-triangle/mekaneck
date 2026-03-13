"""
Shared utilities for validation experiments.

Provides data download, result saving, Kuramoto dynamics,
and regime classification used across all experiments.
"""

import json
import csv
import time
import hashlib
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Dict, Any, List, Tuple, Optional
import numpy as np


# ---------------------------------------------------------------------------
# Constants from the framework
# ---------------------------------------------------------------------------

BOLTZMANN_CONSTANT: float = 1.381e-23  # J/K
KT_BODY_TEMP: float = BOLTZMANN_CONSTANT * 310.15  # k_B T at 37°C

# Regime boundaries (Kuramoto order parameter R)
REGIME_COHERENT_MIN: float = 0.8
REGIME_TURBULENT_MAX: float = 0.3
REGIME_PHASE_LOCKED_MIN: float = 0.95

# Sleep stage → predicted regime mapping
SLEEP_STAGE_REGIMES: Dict[str, str] = {
    "W": "coherent",        # Wake: R > 0.8
    "N1": "cascade",        # Light sleep onset: hierarchical
    "N2": "cascade",        # Light sleep: spindles = intermediate sync
    "N3": "phase_locked",   # Deep sleep: slow-wave, R > 0.95
    "REM": "turbulent",     # REM: desynchronized, R < 0.3
}

# EEG frequency bands (Hz)
FREQ_BANDS: Dict[str, Tuple[float, float]] = {
    "delta": (0.5, 4.0),
    "theta": (4.0, 8.0),
    "alpha": (8.0, 13.0),
    "beta": (13.0, 30.0),
    "gamma": (30.0, 45.0),
}


# ---------------------------------------------------------------------------
# Numpy-safe JSON encoder
# ---------------------------------------------------------------------------

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, np.bool_):
            return bool(obj)
        if isinstance(obj, Path):
            return str(obj)
        return super().default(obj)


# ---------------------------------------------------------------------------
# Result saving
# ---------------------------------------------------------------------------

def save_json(data: Dict[str, Any], filepath: Path) -> Path:
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2, cls=NumpyEncoder)
    print(f"  [saved] {filepath}")
    return filepath


def save_csv(rows: List[Dict[str, Any]], filepath: Path) -> Path:
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        return filepath
    fieldnames = list(rows[0].keys())
    with open(filepath, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"  [saved] {filepath}")
    return filepath


def create_result_dict(
    experiment_name: str,
    parameters: Dict[str, Any],
    results: Dict[str, Any],
    claims_validated: Dict[str, bool],
) -> Dict[str, Any]:
    return {
        "experiment": experiment_name,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "parameters": parameters,
        "results": results,
        "claims_validated": claims_validated,
    }


def print_summary(results: Dict[str, Any]) -> None:
    print("\n" + "=" * 70)
    print(f"VALIDATION SUMMARY: {results.get('experiment', 'unknown')}")
    print("=" * 70)
    if "claims_validated" in results:
        claims = results["claims_validated"]
        for claim, validated in claims.items():
            status = "[OK]  " if validated else "[FAIL]"
            print(f"  {status} {claim}")
        n_pass = sum(claims.values())
        n_total = len(claims)
        print(f"\n  Overall: {n_pass}/{n_total} ({n_pass/n_total:.0%})")
    print("=" * 70)


# ---------------------------------------------------------------------------
# Kuramoto dynamics (standalone, no virtualbrain dependency)
# ---------------------------------------------------------------------------

def kuramoto_order_parameter(phases: np.ndarray) -> Tuple[float, float]:
    """Compute R and Psi from phase array."""
    z = np.mean(np.exp(1j * phases))
    return float(np.abs(z)), float(np.angle(z))


def simulate_kuramoto(
    n_oscillators: int,
    coupling: float,
    duration: float,
    dt: float = 0.01,
    mean_freq: float = 10.0,
    freq_std: float = 2.0,
    seed: Optional[int] = None,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Simulate Kuramoto model, return (times, R_values).
    """
    rng = np.random.default_rng(seed)
    phases = rng.uniform(0, 2 * np.pi, n_oscillators)
    omegas = rng.normal(mean_freq, freq_std, n_oscillators) * 2 * np.pi

    n_steps = int(duration / dt)
    times = np.linspace(0, duration, n_steps)
    R_values = np.zeros(n_steps)

    for i in range(n_steps):
        R, _ = kuramoto_order_parameter(phases)
        R_values[i] = R
        phase_diff = phases[np.newaxis, :] - phases[:, np.newaxis]
        coupling_term = (coupling / n_oscillators) * np.sum(np.sin(phase_diff), axis=1)
        phases = np.mod(phases + (omegas + coupling_term) * dt, 2 * np.pi)

    return times, R_values


def critical_coupling(freq_std: float) -> float:
    """K_c = 2 * sigma_omega / pi."""
    return 2 * freq_std / np.pi


# ---------------------------------------------------------------------------
# Regime classification
# ---------------------------------------------------------------------------

def classify_regime(R: float) -> str:
    """Classify operational regime from Kuramoto order parameter R."""
    if R >= REGIME_PHASE_LOCKED_MIN:
        return "phase_locked"
    elif R >= REGIME_COHERENT_MIN:
        return "coherent"
    elif R <= REGIME_TURBULENT_MAX:
        return "turbulent"
    elif R <= 0.5:
        return "aperture_dominated"
    else:
        return "cascade"


def structural_factor(R: float, n_partitions: int = 100) -> float:
    """
    Compute structural factor S = k_B * M * ln(n).

    M (partition depth) is proportional to R for neural systems.
    """
    M = R * np.log2(n_partitions)
    return BOLTZMANN_CONSTANT * M * np.log(n_partitions)


# ---------------------------------------------------------------------------
# Data download helpers
# ---------------------------------------------------------------------------

def download_file(url: str, dest: Path, chunk_size: int = 8192) -> Path:
    """Download a file from URL to dest. Returns dest path."""
    import urllib.request
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        print(f"  [cached] {dest}")
        return dest
    print(f"  [downloading] {url}")
    urllib.request.urlretrieve(url, dest)
    print(f"  [done] {dest}")
    return dest
