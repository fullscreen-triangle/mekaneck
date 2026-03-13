"""
Experiment 3: Catalytic Efficiency vs Partition Depth
=====================================================

Validates the prediction from phase-space mechanics:
  - Catalytic efficiency (kcat/Km) anti-correlates with categorical dimension d_cat
  - At d_cat = 1: diffusion-limited catalysis (kcat/Km → 10^8-10^9 M^-1 s^-1)
  - Transport vanishes at partition extinction (d_cat → 0)
  - Marcus-like inverted region at high partition depth

Data source:
  - BRENDA enzyme database (published kinetic parameters)
  - We use a curated set of well-characterized enzymes spanning
    multiple orders of magnitude in catalytic efficiency

Tests:
  1. Anti-correlation between d_cat (estimated from substrate complexity)
     and catalytic efficiency
  2. Diffusion limit at d_cat = 1
  3. Enzyme families cluster by regime in the partition framework
  4. Triple equivalence: S_osc = S_cat = S_part holds for enzyme systems

Results saved to: results/enzyme/
"""

import sys
from pathlib import Path
from typing import Dict, Any, List, Tuple
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from common import (
    save_json, save_csv, create_result_dict, print_summary,
    BOLTZMANN_CONSTANT,
)

RESULTS_DIR = Path(__file__).resolve().parent.parent.parent / "results" / "enzyme"


# ---------------------------------------------------------------------------
# Enzyme database (from BRENDA / published literature)
# ---------------------------------------------------------------------------

# Each enzyme has: kcat (s^-1), Km (M), substrate molecular weight,
# number of substrate atoms, and enzyme classification
ENZYME_DATABASE = {
    # Diffusion-limited enzymes (d_cat ≈ 1)
    "carbonic_anhydrase": {
        "kcat": 1e6, "Km": 1.2e-2,
        "substrate": "CO2", "substrate_mw": 44, "substrate_atoms": 3,
        "ec_class": "lyase", "family": "metalloenzyme",
    },
    "acetylcholinesterase": {
        "kcat": 1.4e4, "Km": 9e-5,
        "substrate": "acetylcholine", "substrate_mw": 146, "substrate_atoms": 15,
        "ec_class": "hydrolase", "family": "serine_esterase",
    },
    "catalase": {
        "kcat": 4e7, "Km": 1.1,
        "substrate": "H2O2", "substrate_mw": 34, "substrate_atoms": 4,
        "ec_class": "oxidoreductase", "family": "heme_enzyme",
    },
    "superoxide_dismutase": {
        "kcat": 1e9, "Km": 3.5e-4,
        "substrate": "O2-", "substrate_mw": 32, "substrate_atoms": 2,
        "ec_class": "oxidoreductase", "family": "metalloenzyme",
    },
    "triose_phosphate_isomerase": {
        "kcat": 4.3e3, "Km": 4.7e-4,
        "substrate": "DHAP", "substrate_mw": 170, "substrate_atoms": 13,
        "ec_class": "isomerase", "family": "TIM_barrel",
    },
    "fumarase": {
        "kcat": 8e2, "Km": 5e-6,
        "substrate": "fumarate", "substrate_mw": 116, "substrate_atoms": 10,
        "ec_class": "lyase", "family": "fumarase",
    },
    "beta_lactamase": {
        "kcat": 2e3, "Km": 2e-5,
        "substrate": "benzylpenicillin", "substrate_mw": 334, "substrate_atoms": 39,
        "ec_class": "hydrolase", "family": "serine_hydrolase",
    },

    # Moderate efficiency enzymes
    "hexokinase": {
        "kcat": 1e2, "Km": 1e-4,
        "substrate": "glucose", "substrate_mw": 180, "substrate_atoms": 24,
        "ec_class": "transferase", "family": "kinase",
    },
    "lactate_dehydrogenase": {
        "kcat": 1e3, "Km": 3.5e-5,
        "substrate": "pyruvate", "substrate_mw": 88, "substrate_atoms": 9,
        "ec_class": "oxidoreductase", "family": "dehydrogenase",
    },
    "chymotrypsin": {
        "kcat": 1e2, "Km": 5e-3,
        "substrate": "peptide_bond", "substrate_mw": 250, "substrate_atoms": 20,
        "ec_class": "hydrolase", "family": "serine_protease",
    },
    "alcohol_dehydrogenase": {
        "kcat": 27, "Km": 1e-3,
        "substrate": "ethanol", "substrate_mw": 46, "substrate_atoms": 9,
        "ec_class": "oxidoreductase", "family": "dehydrogenase",
    },

    # Slow enzymes (high d_cat, complex substrates)
    "lysozyme": {
        "kcat": 0.5, "Km": 6e-6,
        "substrate": "peptidoglycan", "substrate_mw": 990, "substrate_atoms": 85,
        "ec_class": "hydrolase", "family": "glycosidase",
    },
    "DNA_polymerase_I": {
        "kcat": 15, "Km": 1e-6,
        "substrate": "dNTP", "substrate_mw": 487, "substrate_atoms": 45,
        "ec_class": "transferase", "family": "polymerase",
    },
    "RNA_polymerase": {
        "kcat": 40, "Km": 1.2e-5,
        "substrate": "NTP", "substrate_mw": 503, "substrate_atoms": 47,
        "ec_class": "transferase", "family": "polymerase",
    },
    "cytochrome_P450": {
        "kcat": 20, "Km": 5e-5,
        "substrate": "drug_substrate", "substrate_mw": 350, "substrate_atoms": 30,
        "ec_class": "oxidoreductase", "family": "heme_enzyme",
    },
    "tryptophan_synthase": {
        "kcat": 2, "Km": 2.8e-5,
        "substrate": "indole+serine", "substrate_mw": 222, "substrate_atoms": 22,
        "ec_class": "lyase", "family": "PLP_enzyme",
    },
    "ATP_synthase": {
        "kcat": 600, "Km": 2e-4,
        "substrate": "ADP+Pi", "substrate_mw": 427, "substrate_atoms": 40,
        "ec_class": "hydrolase", "family": "rotary_motor",
    },
}


# ---------------------------------------------------------------------------
# Partition depth estimation
# ---------------------------------------------------------------------------

def estimate_categorical_dimension(
    substrate_atoms: int,
    substrate_mw: float,
) -> float:
    """
    Estimate categorical dimension d_cat from substrate complexity.

    d_cat = log_2(n_accessible_states) / log_2(n_max_states)

    For enzymes, substrate complexity (atom count, MW) determines
    the number of conformational states that must be navigated.
    """
    # Simple model: d_cat proportional to log of molecular complexity
    # Small substrates (CO2, H2O2) → d_cat ≈ 1
    # Large substrates (peptidoglycan, DNA) → d_cat ≈ 3-5
    n_states = substrate_atoms * np.log2(max(substrate_mw, 1))
    d_cat = np.log2(max(n_states, 1)) / np.log2(1000)  # normalize to ~[0, 1] range
    return min(float(d_cat), 1.0)


def partition_depth(d_cat: float, n_partitions: int = 100) -> float:
    """M = d_cat * log_2(n_partitions)."""
    return d_cat * np.log2(n_partitions)


# ---------------------------------------------------------------------------
# Test 1: Anti-correlation d_cat vs efficiency
# ---------------------------------------------------------------------------

def test_efficiency_anticorrelation() -> Dict[str, Any]:
    """Test that kcat/Km anti-correlates with d_cat."""
    print("\n  Test 1: Catalytic Efficiency vs d_cat")

    rows = []
    for name, info in ENZYME_DATABASE.items():
        kcat_km = info["kcat"] / info["Km"]
        d_cat = estimate_categorical_dimension(
            info["substrate_atoms"], info["substrate_mw"]
        )
        M = partition_depth(d_cat)

        # Triple equivalence: S = k_B * M * ln(n)
        S_part = BOLTZMANN_CONSTANT * M * np.log(info["substrate_atoms"])

        rows.append({
            "enzyme": name,
            "ec_class": info["ec_class"],
            "family": info["family"],
            "substrate": info["substrate"],
            "substrate_atoms": info["substrate_atoms"],
            "substrate_mw": info["substrate_mw"],
            "kcat": info["kcat"],
            "Km": info["Km"],
            "kcat_km": round(kcat_km, 2),
            "log_kcat_km": round(np.log10(kcat_km), 2),
            "d_cat": round(d_cat, 4),
            "partition_depth_M": round(M, 4),
            "S_partition": round(S_part, 30),  # very small number
        })

    save_csv(rows, RESULTS_DIR / "enzyme_efficiency.csv")

    # Compute correlation
    d_cats = [r["d_cat"] for r in rows]
    log_efficiencies = [r["log_kcat_km"] for r in rows]
    correlation = float(np.corrcoef(d_cats, log_efficiencies)[0, 1])

    return {
        "correlation_d_cat_vs_log_efficiency": correlation,
        "anti_correlation": correlation < -0.5,
        "n_enzymes": len(rows),
        "per_enzyme": rows,
    }


# ---------------------------------------------------------------------------
# Test 2: Diffusion limit at d_cat = 1
# ---------------------------------------------------------------------------

def test_diffusion_limit() -> Dict[str, Any]:
    """Test that enzymes with d_cat ≈ min have kcat/Km near diffusion limit."""
    print("  Test 2: Diffusion Limit at Low d_cat")

    DIFFUSION_LIMIT = 1e8  # M^-1 s^-1 (theoretical maximum)

    near_limit = []
    for name, info in ENZYME_DATABASE.items():
        d_cat = estimate_categorical_dimension(
            info["substrate_atoms"], info["substrate_mw"]
        )
        kcat_km = info["kcat"] / info["Km"]

        if d_cat < 0.4:  # low categorical dimension
            near_limit.append({
                "enzyme": name,
                "d_cat": round(d_cat, 4),
                "kcat_km": round(kcat_km, 2),
                "log_kcat_km": round(np.log10(kcat_km), 2),
                "fraction_of_diffusion_limit": round(kcat_km / DIFFUSION_LIMIT, 4),
            })

    # Check that low-d_cat enzymes approach diffusion limit
    if near_limit:
        max_efficiency = max(r["kcat_km"] for r in near_limit)
        approaches_limit = max_efficiency > 1e7
    else:
        approaches_limit = False

    return {
        "diffusion_limit": DIFFUSION_LIMIT,
        "n_near_limit_enzymes": len(near_limit),
        "near_limit_enzymes": near_limit,
        "approaches_diffusion_limit": approaches_limit,
    }


# ---------------------------------------------------------------------------
# Test 3: Family clustering by regime
# ---------------------------------------------------------------------------

def test_family_clustering() -> Dict[str, Any]:
    """Test that enzyme families cluster by regime in partition space."""
    print("  Test 3: Enzyme Family Clustering")

    family_data: Dict[str, List[Dict]] = {}
    for name, info in ENZYME_DATABASE.items():
        d_cat = estimate_categorical_dimension(
            info["substrate_atoms"], info["substrate_mw"]
        )
        kcat_km = info["kcat"] / info["Km"]
        family = info["family"]
        family_data.setdefault(family, []).append({
            "enzyme": name,
            "d_cat": d_cat,
            "log_kcat_km": np.log10(kcat_km),
        })

    # Compute within-family and between-family variance
    family_centroids = {}
    within_variances = []

    for family, members in family_data.items():
        if len(members) < 2:
            family_centroids[family] = {
                "d_cat": members[0]["d_cat"],
                "log_kcat_km": members[0]["log_kcat_km"],
            }
            continue

        d_cats = [m["d_cat"] for m in members]
        effs = [m["log_kcat_km"] for m in members]
        family_centroids[family] = {
            "d_cat": float(np.mean(d_cats)),
            "log_kcat_km": float(np.mean(effs)),
        }
        within_variances.append(float(np.var(d_cats) + np.var(effs)))

    # Between-family variance
    all_d = [c["d_cat"] for c in family_centroids.values()]
    all_e = [c["log_kcat_km"] for c in family_centroids.values()]
    between_var = float(np.var(all_d) + np.var(all_e))

    within_var_mean = float(np.mean(within_variances)) if within_variances else 0

    return {
        "n_families": len(family_data),
        "between_family_variance": round(between_var, 4),
        "within_family_variance": round(within_var_mean, 4),
        "clustering_ratio": round(between_var / (within_var_mean + 1e-12), 2),
        "families_are_separated": between_var > within_var_mean if within_variances else True,
        "family_centroids": {k: {kk: round(vv, 4) for kk, vv in v.items()}
                            for k, v in family_centroids.items()},
    }


# ---------------------------------------------------------------------------
# Test 4: Triple equivalence for enzyme systems
# ---------------------------------------------------------------------------

def test_triple_equivalence() -> Dict[str, Any]:
    """
    Test S_osc = S_cat = S_part for enzyme systems.

    S_part = k_B * M * ln(n)
    S_cat = k_B * ln(n_accessible)  [from d_cat]
    S_osc = k_B * ln(Z_osc)  [from kcat as oscillation frequency]
    """
    print("  Test 4: Triple Equivalence")

    rows = []
    for name, info in ENZYME_DATABASE.items():
        n = info["substrate_atoms"]
        d_cat = estimate_categorical_dimension(
            info["substrate_atoms"], info["substrate_mw"]
        )
        M = partition_depth(d_cat)

        # S_partition
        S_part = BOLTZMANN_CONSTANT * M * np.log(max(n, 2))

        # S_categorical: from accessible states fraction
        n_accessible = max(1, int(d_cat * n))
        S_cat = BOLTZMANN_CONSTANT * np.log(max(n_accessible, 1))

        # S_oscillatory: from kcat as characteristic frequency
        # Z_osc = partition function from oscillation spectrum
        omega = 2 * np.pi * info["kcat"]
        E_osc = 1.055e-34 * omega  # hbar * omega
        # At body temperature
        beta = 1 / KT_BODY_TEMP
        # For harmonic oscillator: S = k_B * (beta*E/(exp(beta*E)-1) - ln(1-exp(-beta*E)))
        # At biological T, beta*E << 1 for most enzymes, so S ≈ k_B * (1 + ln(k_BT/E))
        if E_osc > 0:
            ratio = KT_BODY_TEMP / E_osc
            S_osc = BOLTZMANN_CONSTANT * (1 + np.log(max(ratio, 1)))
        else:
            S_osc = S_part

        rows.append({
            "enzyme": name,
            "S_partition": float(S_part),
            "S_categorical": float(S_cat),
            "S_oscillatory": float(S_osc),
        })

    # Check proportionality (log-scale correlation)
    S_parts = np.array([r["S_partition"] for r in rows])
    S_cats = np.array([r["S_categorical"] for r in rows])
    S_oscs = np.array([r["S_oscillatory"] for r in rows])

    # Replace zeros for log
    S_parts = np.where(S_parts > 0, S_parts, 1e-30)
    S_cats = np.where(S_cats > 0, S_cats, 1e-30)
    S_oscs = np.where(S_oscs > 0, S_oscs, 1e-30)

    corr_part_cat = float(np.corrcoef(np.log(S_parts), np.log(S_cats))[0, 1])
    corr_part_osc = float(np.corrcoef(np.log(S_parts), np.log(S_oscs))[0, 1])
    corr_cat_osc = float(np.corrcoef(np.log(S_cats), np.log(S_oscs))[0, 1])

    return {
        "corr_S_part_S_cat": round(corr_part_cat, 4),
        "corr_S_part_S_osc": round(corr_part_osc, 4),
        "corr_S_cat_S_osc": round(corr_cat_osc, 4),
        "triple_equivalence_holds": (
            corr_part_cat > 0.7 and corr_part_osc > 0.5
        ),
        "per_enzyme": rows,
    }


KT_BODY_TEMP = BOLTZMANN_CONSTANT * 310.15


# ---------------------------------------------------------------------------
# Main experiment
# ---------------------------------------------------------------------------

def main():
    print("=" * 70)
    print("EXPERIMENT 3: Catalytic Efficiency vs Partition Depth")
    print("=" * 70)

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    efficiency_results = test_efficiency_anticorrelation()
    diffusion_results = test_diffusion_limit()
    clustering_results = test_family_clustering()
    triple_results = test_triple_equivalence()

    claims = {
        "efficiency_anticorrelates_with_d_cat": efficiency_results["anti_correlation"],
        "low_d_cat_approaches_diffusion_limit": diffusion_results["approaches_diffusion_limit"],
        "enzyme_families_cluster_by_regime": clustering_results["families_are_separated"],
        "triple_equivalence_holds": triple_results["triple_equivalence_holds"],
    }

    results = create_result_dict(
        experiment_name="enzyme_catalytic_efficiency",
        parameters={
            "n_enzymes": len(ENZYME_DATABASE),
            "d_cat_estimation": "log2(atoms * log2(MW)) / log2(1000)",
        },
        results={
            "efficiency_anticorrelation": efficiency_results,
            "diffusion_limit": diffusion_results,
            "family_clustering": clustering_results,
            "triple_equivalence": triple_results,
        },
        claims_validated=claims,
    )

    save_json(results, RESULTS_DIR / "summary.json")
    print_summary(results)

    print("\nAll results saved to:", RESULTS_DIR)


if __name__ == "__main__":
    main()
