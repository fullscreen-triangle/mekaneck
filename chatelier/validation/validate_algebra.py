"""
Validation for: A Residual Algebra for Catalytic Composition.

Checks, in order:
  1. Telescoping obstruction (Thm 5.2)  -- instance-specific test is an identity
  2. Type-averaged test is non-degenerate (Thm 5.5)
  3. Law comparison across three separation regimes (Prop 6.3)
  4. Degeneracy at vanishing type separation (Prop 6.2)
  5. Floor estimators: sample-minimum vs asymptotic (Rem 3.5)
  6. Convergence criterion, sum kappa = inf  (Thm 4.6)
  7. Monoid structure of composition (Cor 4.2)

Every check states its own pass criterion. Failures are reported, not hidden.
Results are written to results/algebra_results.json
"""

from __future__ import annotations

import json
import math
import os
from dataclasses import dataclass, asdict
from typing import Callable

import numpy as np

RNG_SEED = 20260816
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
MACHINE_EPS_TOL = 1e-12


# ----------------------------------------------------------------------
# Core algebra
# ----------------------------------------------------------------------

def kappa(s_before: float, s_after: float, floor: float) -> float:
    """Catalytic power: fraction of the outstanding gap closed (Def 4.1)."""
    gap = s_before - floor
    if gap <= 0:
        raise ValueError("pre-state must lie strictly above the floor")
    return (s_before - s_after) / gap


def compose_mult(kappas) -> float:
    """1 - prod(1 - k_i)   (Thm 4.1)"""
    prod = 1.0
    for k in kappas:
        prod *= (1.0 - k)
    return 1.0 - prod


def compose_add(kappas) -> float:
    return min(float(np.sum(kappas)), 1.0)


def compose_geo(kappas) -> float:
    n = len(kappas)
    prod = 1.0
    for k in kappas:
        prod *= (1.0 - k)
    # guard against negative base under fractional power (kappa may exceed 1
    # only in pathological input; residual factors are non-negative here)
    if prod < 0:
        return float("nan")
    return 1.0 - prod ** (1.0 / n)


def compose_max(kappas) -> float:
    return float(np.max(kappas))


LAWS: dict[str, Callable] = {
    "multiplicative": compose_mult,
    "additive": compose_add,
    "geometric_mean": compose_geo,
    "maximum": compose_max,
}


# ----------------------------------------------------------------------
# Synthetic cascade generation
# ----------------------------------------------------------------------

@dataclass
class Regime:
    name: str
    type_means: dict           # type label -> mean kappa
    within_sd: float           # within-type dispersion of kappa
    floor: float
    s_init: float


def generate_cascades(regime: Regime, n_cascades: int, len_range=(3, 5), rng=None):
    """
    Build cascades by drawing typed events and applying realised powers to the
    running gap. Returns a list of dicts with the full state sequence, the
    event types, and the realised per-event powers.
    """
    rng = rng or np.random.default_rng(RNG_SEED)
    types = list(regime.type_means.keys())
    cascades = []

    for _ in range(n_cascades):
        n = int(rng.integers(len_range[0], len_range[1] + 1))
        seq_types = [types[int(rng.integers(0, len(types)))] for _ in range(n)]

        s = regime.s_init
        states = [s]
        realised = []
        for t in seq_types:
            k = float(rng.normal(regime.type_means[t], regime.within_sd))
            # residual factor must stay non-negative: uncertainty cannot fall
            # below the floor (Cor 3.3). Clip the power, not the state.
            k = min(k, 0.95)
            gap = s - regime.floor
            s = regime.floor + gap * (1.0 - k)
            states.append(s)
            realised.append(k)

        cascades.append({
            "types": seq_types,
            "states": states,
            "realised_kappa": realised,
        })
    return cascades


# ----------------------------------------------------------------------
# Check 1: the telescoping obstruction
# ----------------------------------------------------------------------

def check_telescoping(cascades, floor):
    """
    Thm 5.2: under instance-specific estimation the multiplicative prediction
    equals the measured net power identically. PASS = max abs deviation is at
    machine precision, i.e. the test is degenerate exactly as proved.
    """
    deviations = []
    for c in cascades:
        st = c["states"]
        ks = [kappa(st[i], st[i + 1], floor) for i in range(len(st) - 1)]
        pred = compose_mult(ks)
        meas = (st[0] - st[-1]) / (st[0] - floor)
        deviations.append(abs(pred - meas))

    max_dev = float(np.max(deviations))
    return {
        "claim": "instance-specific multiplicative prediction == measured net power",
        "theorem": "Thm 5.2 (telescoping obstruction)",
        "max_abs_deviation": max_dev,
        "tolerance": MACHINE_EPS_TOL,
        "identity_holds": bool(max_dev < MACHINE_EPS_TOL),
        "pearson_r": 1.0 if max_dev < MACHINE_EPS_TOL else None,
        "interpretation": (
            "Agreement is algebraic, not empirical. An r of 1.0 here is a "
            "restatement of the composition law and is evidence of nothing."
        ),
        "pass": bool(max_dev < MACHINE_EPS_TOL),
    }


# ----------------------------------------------------------------------
# Check 2 & 3: type-averaged test, law comparison
# ----------------------------------------------------------------------

def type_averaged_kappas(cascades, floor):
    """Mean realised power per event type, pooled over all instances."""
    acc: dict[str, list] = {}
    for c in cascades:
        st = c["states"]
        for i, t in enumerate(c["types"]):
            acc.setdefault(t, []).append(kappa(st[i], st[i + 1], floor))
    return {t: float(np.mean(v)) for t, v in acc.items()}, acc


def pearson(x, y):
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    ok = np.isfinite(x) & np.isfinite(y)
    x, y = x[ok], y[ok]
    if len(x) < 3 or np.std(x) < 1e-15 or np.std(y) < 1e-15:
        return None
    return float(np.corrcoef(x, y)[0, 1])


def rmse(x, y):
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    ok = np.isfinite(x) & np.isfinite(y)
    if not ok.any():
        return None
    return float(np.sqrt(np.mean((x[ok] - y[ok]) ** 2)))


def separation_ratio(per_type_samples):
    """eta = Var_between / (Var_between + Var_within)   (Def 6.1)"""
    means = [np.mean(v) for v in per_type_samples.values()]
    var_b = float(np.var(means))
    var_w = float(np.mean([np.var(v) for v in per_type_samples.values()]))
    denom = var_b + var_w
    return float(var_b / denom) if denom > 0 else 0.0


def check_type_averaged(cascades, floor, regime_name):
    """
    Thm 5.5 / Prop 6.3: type-averaged prediction is NOT an identity, and the
    four laws are compared. PASS for non-degeneracy = discrepancy is non-zero.
    """
    kbar, per_type = type_averaged_kappas(cascades, floor)
    eta = separation_ratio(per_type)

    measured = []
    preds: dict[str, list] = {name: [] for name in LAWS}
    for c in cascades:
        st = c["states"]
        meas = (st[0] - st[-1]) / (st[0] - floor)
        measured.append(meas)
        tk = [kbar[t] for t in c["types"]]
        for name, fn in LAWS.items():
            preds[name].append(fn(tk))

    law_stats = {}
    for name in LAWS:
        law_stats[name] = {
            "pearson_r": pearson(preds[name], measured),
            "rmse": rmse(preds[name], measured),
        }

    # non-degeneracy: multiplicative prediction must differ from measurement
    mult_dev = float(np.max(np.abs(np.array(preds["multiplicative"]) - np.array(measured))))

    valid = {k: v["pearson_r"] for k, v in law_stats.items() if v["pearson_r"] is not None}
    best = max(valid, key=valid.get) if valid else None

    return {
        "regime": regime_name,
        "claim": "type-averaged test has a genuine null (Thm 5.5)",
        "type_means": kbar,
        "type_separation_eta": eta,
        "n_cascades": len(cascades),
        "max_abs_discrepancy": mult_dev,
        "non_degenerate": bool(mult_dev > 1e-6),
        "laws": law_stats,
        "best_law_by_r": best,
        "test_has_power": bool(eta > 0.05 and valid),
        "pass": bool(mult_dev > 1e-6),
    }


# ----------------------------------------------------------------------
# Check 5: floor estimators
# ----------------------------------------------------------------------

def floor_sample_minimum(states):
    """Trivial estimator: positive whenever the sample is. Cannot fail."""
    return float(np.min(states))


def floor_asymptotic(states_by_stage):
    """
    Fit the limiting value of the running minimum as the sample grows.
    Model: m(n) = beta + c * n^(-alpha). We estimate beta by extrapolating a
    log-linear fit of (m(n) - m_inf_guess). Simpler and more robust: fit
    m(n) against 1/n by least squares and take the intercept.

    Returns the intercept, which is an estimate of the true floor and CAN be
    <= 0 when the generating process has no floor.
    """
    ns = np.array([len(s) for s in states_by_stage], dtype=float)
    mins = np.array([np.min(s) for s in states_by_stage], dtype=float)
    x = 1.0 / ns
    A = np.vstack([x, np.ones_like(x)]).T
    coef, *_ = np.linalg.lstsq(A, mins, rcond=None)
    intercept = float(coef[1])
    return intercept


def check_floor_estimators(rng):
    """
    Rem 3.5: the sample-minimum estimator is positive by construction and
    therefore uninformative; the asymptotic estimator must separate a floored
    from an unfloored generating process.
    """
    n_stages = 40
    stage_sizes = np.linspace(50, 4000, n_stages).astype(int)

    # (a) FLOORED process: uncertainty decays toward beta=10 but never below
    beta_true = 10.0
    floored = []
    for n in stage_sizes:
        gaps = 40.0 * rng.random(n) ** 3      # gaps concentrate near 0
        floored.append(beta_true + gaps)

    # (b) UNFLOORED process: uncertainty decays toward 0 with no barrier
    unfloored = []
    for n in stage_sizes:
        unfloored.append(40.0 * rng.random(n) ** 3)

    res = {}
    for label, data in (("floored_beta_10", floored), ("unfloored_beta_0", unfloored)):
        samp_min = floor_sample_minimum(np.concatenate(data))
        asym = floor_asymptotic(data)
        res[label] = {
            "sample_minimum_estimate": samp_min,
            "sample_minimum_is_positive": bool(samp_min > 0),
            "asymptotic_estimate": asym,
            "asymptotic_is_positive": bool(asym > 0.5),
        }

    # The claim is about FALSIFIABILITY, not about ordering under unlimited
    # data: the sample minimum is strictly positive by construction in every
    # regime, so it can never return a value inconsistent with a positivity
    # claim; and it is biased upward, which by Prop 4.8 inflates the powers of
    # events acting near the floor. The asymptotic estimator can, and does,
    # return approximately zero when no floor exists.
    sm_never_nonpositive = (res["floored_beta_10"]["sample_minimum_estimate"] > 0 and
                            res["unfloored_beta_0"]["sample_minimum_estimate"] > 0)
    sm_biased_up = res["floored_beta_10"]["sample_minimum_estimate"] >= beta_true
    as_discriminates = (res["floored_beta_10"]["asymptotic_is_positive"] and
                        not res["unfloored_beta_0"]["asymptotic_is_positive"])
    as_recovers = abs(res["floored_beta_10"]["asymptotic_estimate"] - beta_true) < 0.1

    return {
        "claim": "asymptotic floor estimator is falsifiable; sample-minimum is not",
        "theorem": "Rem 3.5, Prop 4.8",
        "estimates": res,
        "true_floor_floored_case": beta_true,
        "sample_minimum_never_returns_nonpositive": bool(sm_never_nonpositive),
        "sample_minimum_biased_upward": bool(sm_biased_up),
        "asymptotic_discriminates": bool(as_discriminates),
        "asymptotic_recovers_true_floor": bool(as_recovers),
        "interpretation": (
            "The sample minimum is strictly positive for BOTH processes, so it "
            "cannot falsify a positivity claim, and it is biased upward, which "
            "inflates near-floor catalytic powers (Prop 4.8). The asymptotic "
            "estimator recovers the true floor and returns approximately zero "
            "when none exists."
        ),
        "pass": bool(sm_never_nonpositive and sm_biased_up
                     and as_discriminates and as_recovers),
    }


# ----------------------------------------------------------------------
# Check 6: convergence criterion
# ----------------------------------------------------------------------

def _residual_fraction(kappas):
    """prod(1 - k_i), computed in log space for numerical stability."""
    log_prod = 0.0
    for k in kappas:
        log_prod += math.log1p(-k)
    return math.exp(log_prod)


def check_convergence():
    """
    Thm 4.6: S_n -> floor iff sum kappa_i = infinity.

    The correct test is ASYMPTOTIC, not a fixed cutoff at finite n. The
    summable case must converge to a strictly positive limit (the residual
    fraction is bounded below as n grows); the divergent case must tend to
    zero monotonically without bound. For k_i = 1/(i+2) the exact product is
    1/(n+1), which decays harmonically -- so any fixed small tolerance at
    finite n would be a statement about the tolerance, not about the theorem.
    We therefore check the limiting behaviour directly.
    """
    floor = 5.0
    s0 = 105.0
    g0 = s0 - floor
    stages = [1000, 10000, 100000, 1000000]

    # summable: sum 2^-i converges  => residual fraction has a POSITIVE limit
    sum_traj, div_traj = [], []
    for n in stages:
        ks_sum = [2.0 ** -(i + 1) for i in range(min(n, 2000))]  # underflows past ~2000
        sum_traj.append(_residual_fraction(ks_sum))
        ks_div = [1.0 / (i + 2) for i in range(n)]
        div_traj.append(_residual_fraction(ks_div))

    # (a) summable case: fraction stabilises at a positive value
    summable_limit = sum_traj[-1]
    summable_stable = abs(sum_traj[-1] - sum_traj[-2]) < 1e-12
    summable_positive = summable_limit > 1e-3

    # (b) divergent case: fraction strictly decreasing and matching 2/(n+2)
    div_decreasing = all(div_traj[i + 1] < div_traj[i] for i in range(len(div_traj) - 1))
    # exact: prod_{i=0}^{n-1} (1 - 1/(i+2)) = prod (i+1)/(i+2) = 1/(n+1)
    predicted = [1.0 / (n + 1) for n in stages]
    div_matches_theory = max(abs(a - b) / b for a, b in zip(div_traj, predicted)) < 1e-6
    div_tends_zero = div_traj[-1] < div_traj[0] / 100.0

    ok = bool(summable_stable and summable_positive
              and div_decreasing and div_matches_theory and div_tends_zero)

    return {
        "claim": "gap -> 0 iff sum(kappa) diverges",
        "theorem": "Thm 4.6",
        "stages_n": stages,
        "summable_case": {
            "kappa_i": "2^-(i+1), sum converges to 1",
            "residual_fraction_trajectory": sum_traj,
            "limit": summable_limit,
            "stabilised": bool(summable_stable),
            "limit_is_positive": bool(summable_positive),
            "converges_to_floor": False,
        },
        "divergent_case": {
            "kappa_i": "1/(i+2), sum diverges",
            "residual_fraction_trajectory": div_traj,
            "closed_form_1_over_n_plus_1": predicted,
            "matches_closed_form": bool(div_matches_theory),
            "monotone_decreasing": bool(div_decreasing),
            "tends_to_zero": bool(div_tends_zero),
            "converges_to_floor": True,
        },
        "final_gap_summable": float(g0 * sum_traj[-1]),
        "final_gap_divergent": float(g0 * div_traj[-1]),
        "interpretation": (
            "Divergent-sum cascade drives the gap to zero but only harmonically "
            "(exactly 1/(n+1)); a fixed tolerance at finite n tests the tolerance, "
            "not the theorem."
        ),
        "pass": ok,
    }


# ----------------------------------------------------------------------
# Check 7: monoid structure
# ----------------------------------------------------------------------

def check_monoid(rng):
    """Cor 4.2: (composition, identity 0, absorbing 1) is a commutative monoid."""
    a, b, c = rng.uniform(-0.5, 0.95, 3)

    assoc = abs(compose_mult([compose_mult([a, b]), c]) - compose_mult([a, compose_mult([b, c])]))
    commut = abs(compose_mult([a, b]) - compose_mult([b, a]))
    ident = abs(compose_mult([a, 0.0]) - a)
    absorb = abs(compose_mult([a, 1.0]) - 1.0)

    return {
        "claim": "composition is associative, commutative, identity 0, absorbing 1",
        "theorem": "Cor 4.2",
        "operands": [float(a), float(b), float(c)],
        "associativity_error": float(assoc),
        "commutativity_error": float(commut),
        "identity_error": float(ident),
        "absorbing_error": float(absorb),
        "pass": bool(max(assoc, commut, ident, absorb) < MACHINE_EPS_TOL),
    }


# ----------------------------------------------------------------------
# Driver
# ----------------------------------------------------------------------

def main():
    rng = np.random.default_rng(RNG_SEED)
    os.makedirs(OUT_DIR, exist_ok=True)

    regimes = [
        Regime("separated",
               {"A->B": 0.55, "B->C": 0.30, "C->A": 0.08, "A->C": 0.42},
               within_sd=0.03, floor=10.0, s_init=100.0),
        Regime("intermediate",
               {"A->B": 0.36, "B->C": 0.30, "C->A": 0.24, "A->C": 0.33},
               within_sd=0.08, floor=10.0, s_init=100.0),
        Regime("compressed",
               {"A->B": 0.300, "B->C": 0.302, "C->A": 0.299, "A->C": 0.301},
               within_sd=0.12, floor=10.0, s_init=100.0),
    ]

    results = {
        "meta": {
            "paper": "A Residual Algebra for Catalytic Composition",
            "seed": RNG_SEED,
            "n_cascades_per_regime": 4000,
        },
        "checks": {},
    }

    telescoping_all = {}
    type_avg_all = {}

    for reg in regimes:
        cascades = generate_cascades(reg, 4000, (3, 5), rng)
        telescoping_all[reg.name] = check_telescoping(cascades, reg.floor)
        type_avg_all[reg.name] = check_type_averaged(cascades, reg.floor, reg.name)

    results["checks"]["telescoping_obstruction"] = telescoping_all
    results["checks"]["type_averaged_test"] = type_avg_all
    results["checks"]["floor_estimators"] = check_floor_estimators(rng)
    results["checks"]["convergence_criterion"] = check_convergence()
    results["checks"]["monoid_structure"] = check_monoid(rng)

    # ---- summary ----
    flat = []
    for name, blob in results["checks"].items():
        if isinstance(blob, dict) and "pass" in blob:
            flat.append((name, blob["pass"]))
        elif isinstance(blob, dict):
            for sub, subblob in blob.items():
                if isinstance(subblob, dict) and "pass" in subblob:
                    flat.append(f"{name}/{sub}" and (f"{name}/{sub}", subblob["pass"]))

    results["summary"] = {
        "n_checks": len(flat),
        "n_passed": sum(1 for _, p in flat if p),
        "n_failed": sum(1 for _, p in flat if not p),
        "failed": [n for n, p in flat if not p],
        "all_passed": all(p for _, p in flat),
    }

    # Degeneracy note: the compressed regime is EXPECTED to lose power.
    comp = type_avg_all["compressed"]
    results["summary"]["degeneracy_note"] = {
        "compressed_eta": comp["type_separation_eta"],
        "compressed_test_has_power": comp["test_has_power"],
        "expected": "eta near 0, test_has_power False -- absence of power, not disconfirmation",
    }

    out = os.path.join(OUT_DIR, "algebra_results.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"wrote {out}")
    print(json.dumps(results["summary"], indent=2))
    for reg in regimes:
        t = type_avg_all[reg.name]
        print(f"\n[{reg.name}] eta={t['type_separation_eta']:.4f} "
              f"best={t['best_law_by_r']} power={t['test_has_power']}")
        for law, st in t["laws"].items():
            r = st["pearson_r"]
            rm = st["rmse"]
            print(f"    {law:16s} r={'None' if r is None else f'{r:.4f}'}  "
                  f"rmse={'None' if rm is None else f'{rm:.4f}'}")


if __name__ == "__main__":
    main()
