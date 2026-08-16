"""
Validation for: Mekaneck -- A Substrate-Neutral Language for
Individuation-Structured Inquiry.

Checks:
  1. Parsing: well-formed accepted; exclusion-free seek REJECTED  (Cor 4.4)
  2. Typing: positivity rule (T-Seek-Pos)                          (Def 5.3)
  3. Typing: coherence rule, >= 3 mutually independent             (Def 5.4)
  4. Progress + preservation over random programs                  (Thm 6.1, 6.2)
  5. Determinism modulo substrate                                  (Thm 6.4)
  6. Termination bound                                             (Thm 6.5)
  7. Monotone record                                               (Thm 6.3)
  8. Dichotomy: Resolved xor Declined                              (Thm 6.7)
  9. Closure strictly stronger than threshold                      (Thm 6.6)
 10. Diagnostics: separation eta, floor estimators                 (Sec 9)

Results are written to results/mekaneck_results.json
"""

from __future__ import annotations

import itertools
import json
import os
import random

import numpy as np

from mekaneck import (
    parse, typecheck, evaluate, evaluate_threshold,
    MckSyntaxError, MckTypeError, Resolved, Declined, LetDecl,
)

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
SEED = 20260816


# ----------------------------------------------------------------------
# Program fixtures
# ----------------------------------------------------------------------

GOOD_PROGRAM = """
# Individuate a coherence regime against the rest of the record.
substrate Osc {
  receivers  : recordings("cohort-A");
  observable : coherence_index();
  events     : label_change();
  floor      : asymptotic_separation();
}

catalyst spectral  : band_decomposition()  independent surrogate, phase;
catalyst surrogate : phase_randomised()    independent spectral, phase;
catalyst phase     : locking_value()       independent spectral, surrogate;

let regime =
  seek        target_state("high-coherence")
  excluding   all_other_states()
  via         (spectral, surrogate, phase)
  until       closure;

report regime;
"""

NO_EXCLUSION_PROGRAM = """
substrate Osc {
  receivers  : recordings("cohort-A");
  observable : coherence_index();
  events     : label_change();
  floor      : asymptotic_separation();
}
catalyst spectral  : band_decomposition() independent surrogate, phase;
catalyst surrogate : phase_randomised()   independent spectral, phase;
catalyst phase     : locking_value()      independent spectral, surrogate;

let regime =
  seek      target_state("high-coherence")
  via       (spectral, surrogate, phase)
  until     closure;

report regime;
"""

TWO_CATALYST_PROGRAM = """
substrate Osc {
  receivers  : recordings("c");
  observable : coherence_index();
  events     : label_change();
  floor      : asymptotic_separation();
}
catalyst a : f() independent b;
catalyst b : g() independent a;

let r = seek t() excluding rest() via (a, b) until closure;
report r;
"""

NON_INDEPENDENT_PROGRAM = """
substrate Osc {
  receivers  : recordings("c");
  observable : coherence_index();
  events     : label_change();
  floor      : asymptotic_separation();
}
catalyst a : f() independent b;
catalyst b : g() independent a;
catalyst c : h();

let r = seek t() excluding rest() via (a, b, c) until closure;
report r;
"""


def first_seek(prog):
    for d in prog.decls:
        if isinstance(d, LetDecl):
            return d.seek
    return None


# ----------------------------------------------------------------------
# Check 1: parsing
# ----------------------------------------------------------------------

def check_parsing():
    good_ok, good_err = True, None
    try:
        parse(GOOD_PROGRAM)
    except Exception as e:
        good_ok, good_err = False, str(e)

    rejected, msg = False, None
    try:
        parse(NO_EXCLUSION_PROGRAM)
    except MckSyntaxError as e:
        rejected, msg = True, str(e)

    return {
        "claim": "well-formed programs parse; seek without 'excluding' is rejected",
        "theorem": "Prop 4.1, Thm 4.3, Cor 4.4",
        "good_program_parses": good_ok,
        "good_program_error": good_err,
        "exclusion_free_rejected": rejected,
        "rejection_message": msg,
        "pass": bool(good_ok and rejected),
    }


# ----------------------------------------------------------------------
# Check 2 & 3: typing rules
# ----------------------------------------------------------------------

def check_typing():
    prog = parse(GOOD_PROGRAM)

    typed_ok, typed_err = True, None
    try:
        typecheck(prog, floor_values={"Osc": 12.5})
    except Exception as e:
        typed_ok, typed_err = False, str(e)

    # positivity: floor <= 0 must be rejected
    pos_rejected, pos_msg = False, None
    try:
        typecheck(parse(GOOD_PROGRAM), floor_values={"Osc": 0.0})
    except MckTypeError as e:
        pos_rejected, pos_msg = True, str(e)

    neg_rejected = False
    try:
        typecheck(parse(GOOD_PROGRAM), floor_values={"Osc": -3.0})
    except MckTypeError:
        neg_rejected = True

    # coherence: 2 catalysts must be rejected
    two_rejected, two_msg = False, None
    try:
        typecheck(parse(TWO_CATALYST_PROGRAM), floor_values={"Osc": 5.0})
    except MckTypeError as e:
        two_rejected, two_msg = True, str(e)

    # coherence: 3 catalysts but not mutually independent must be rejected
    nonindep_rejected, ni_msg = False, None
    try:
        typecheck(parse(NON_INDEPENDENT_PROGRAM), floor_values={"Osc": 5.0})
    except MckTypeError as e:
        nonindep_rejected, ni_msg = True, str(e)

    return {
        "claim": "positivity and coherence rules enforced at compile time",
        "theorem": "Def 5.3 (T-Seek-Pos), Def 5.4 (T-Seek-Coh), Thm 7.2",
        "conforming_program_types": typed_ok,
        "conforming_error": typed_err,
        "zero_floor_rejected": pos_rejected,
        "zero_floor_message": pos_msg,
        "negative_floor_rejected": neg_rejected,
        "two_catalysts_rejected": two_rejected,
        "two_catalysts_message": two_msg,
        "non_mutually_independent_rejected": nonindep_rejected,
        "non_independent_message": ni_msg,
        "pass": bool(typed_ok and pos_rejected and neg_rejected
                     and two_rejected and nonindep_rejected),
    }


# ----------------------------------------------------------------------
# Check 4-8: semantics over random substrates
# ----------------------------------------------------------------------

def random_substrate(rng, catalysts, n_cells):
    cells = [f"cell{i}" for i in range(n_cells)]
    return {c: rng.choice(cells) for c in catalysts}


def check_semantics():
    rng = random.Random(SEED)
    prog = parse(GOOD_PROGRAM)
    typecheck(prog, floor_values={"Osc": 12.5})
    seek = first_seek(prog)
    catalysts = seek.via

    n_trials = 500
    determinism_violations = 0
    termination_violations = 0
    record_violations = 0
    dichotomy_violations = 0
    progress_violations = 0
    resolved_count = 0
    declined_count = 0

    for _ in range(n_trials):
        n_cells = rng.choice([1, 1, 2, 3])
        sub = random_substrate(rng, catalysts, n_cells)

        outcomes = []
        for order in itertools.permutations(catalysts):
            cfg = evaluate(seek, sub, order=list(order))

            # progress: evaluation must produce a value, never stall
            if cfg.outcome is None:
                progress_violations += 1

            # preservation: the value is of type Outcome
            if not isinstance(cfg.outcome, (Resolved, Declined)):
                progress_violations += 1

            # termination bound (Thm 6.5)
            if cfg.record > len(catalysts):
                termination_violations += 1

            # monotone record (Thm 6.3)
            recs = [t["record"] for t in cfg.trace]
            if recs != sorted(recs) or any(
                    recs[i + 1] - recs[i] != 1 for i in range(len(recs) - 1)):
                record_violations += 1

            # dichotomy (Thm 6.7)
            if isinstance(cfg.outcome, Resolved):
                if len(cfg.reached) != 1:
                    dichotomy_violations += 1
            elif isinstance(cfg.outcome, Declined):
                if len(cfg.reached) < 2:
                    dichotomy_violations += 1

            outcomes.append(repr(cfg.outcome))

        # determinism modulo substrate (Thm 6.4)
        if len(set(outcomes)) != 1:
            determinism_violations += 1

        if outcomes[0].startswith("Resolved"):
            resolved_count += 1
        else:
            declined_count += 1

    return {
        "claim": "progress, preservation, determinism, termination, record, dichotomy",
        "theorem": "Thm 6.1, 6.2, 6.3, 6.4, 6.5, 6.7",
        "n_trials": n_trials,
        "n_orderings_per_trial": 6,
        "progress_or_preservation_violations": progress_violations,
        "determinism_violations": determinism_violations,
        "termination_bound_violations": termination_violations,
        "record_monotonicity_violations": record_violations,
        "dichotomy_violations": dichotomy_violations,
        "outcomes_resolved": resolved_count,
        "outcomes_declined": declined_count,
        "both_branches_exercised": bool(resolved_count > 0 and declined_count > 0),
        "pass": bool(progress_violations == 0 and determinism_violations == 0
                     and termination_violations == 0 and record_violations == 0
                     and dichotomy_violations == 0
                     and resolved_count > 0 and declined_count > 0),
    }


# ----------------------------------------------------------------------
# Check 9: closure vs threshold
# ----------------------------------------------------------------------

def check_closure_vs_threshold():
    """
    Thm 6.6: a threshold rule stops after one catalyst that is internally
    consistent; closure continues and discovers the incompatible cell.
    """
    prog = parse(GOOD_PROGRAM)
    typecheck(prog, floor_values={"Osc": 12.5})
    seek = first_seek(prog)

    # spectral and surrogate agree; phase reaches an incompatible cell
    substrate = {"spectral": "cellA", "surrogate": "cellA", "phase": "cellB"}
    uncertainty = {"cellA": 5.0, "cellB": 40.0}     # cellA looks confident
    theta = 10.0

    thr = evaluate_threshold(seek, substrate, uncertainty, theta,
                             order=["spectral", "surrogate", "phase"])
    clo = evaluate(seek, substrate, order=["spectral", "surrogate", "phase"])

    threshold_stopped_early = thr.record < clo.record
    threshold_says_resolved = isinstance(thr.outcome, Resolved)
    closure_says_declined = isinstance(clo.outcome, Declined)

    return {
        "claim": "threshold terminates on a self-consistent line; closure does not",
        "theorem": "Thm 6.6, Cor 6.8",
        "substrate": substrate,
        "uncertainty": uncertainty,
        "theta": theta,
        "threshold_outcome": repr(thr.outcome),
        "threshold_invocations": thr.record,
        "closure_outcome": repr(clo.outcome),
        "closure_invocations": clo.record,
        "threshold_stopped_early": threshold_stopped_early,
        "threshold_reports_resolved": threshold_says_resolved,
        "closure_reports_declined": closure_says_declined,
        "interpretation": (
            "The threshold rule reports a confident answer after two agreeing "
            "sources; closure invokes the third and reports a contested outcome. "
            "Declination is a normal termination, not an error."
        ),
        "pass": bool(threshold_stopped_early and threshold_says_resolved
                     and closure_says_declined),
    }


# ----------------------------------------------------------------------
# Check 10: diagnostics
# ----------------------------------------------------------------------

def separation_eta(per_type):
    means = [np.mean(v) for v in per_type.values()]
    var_b = float(np.var(means))
    var_w = float(np.mean([np.var(v) for v in per_type.values()]))
    d = var_b + var_w
    return float(var_b / d) if d > 0 else 0.0


def check_diagnostics():
    rng = np.random.default_rng(SEED)

    separated = {f"t{i}": rng.normal(0.1 + 0.2 * i, 0.02, 400) for i in range(4)}
    compressed = {f"t{i}": rng.normal(0.30 + 0.001 * i, 0.12, 400) for i in range(4)}

    eta_sep = separation_eta(separated)
    eta_comp = separation_eta(compressed)

    # ---- floor estimators (Rem 9.3) ---------------------------------
    # The claim is NOT that the sample minimum can never order two processes
    # given unlimited data. It is that the sample minimum is positive by
    # construction and biased upward, so its positivity is uninformative in
    # the finite-sample regime an experimenter actually occupies. We test
    # both regimes and report the contrast.
    def sample_min(stages):
        return float(np.min(np.concatenate(stages)))

    def asymptotic(stages):
        ns = np.array([len(s) for s in stages], float)
        mins = np.array([np.min(s) for s in stages], float)
        A = np.vstack([1.0 / ns, np.ones_like(ns)]).T
        coef, *_ = np.linalg.lstsq(A, mins, rcond=None)
        return float(coef[1])

    def build(sizes, floor_val):
        return [floor_val + 40.0 * rng.random(n) ** 3 for n in sizes]

    regimes = {}
    for label, sizes in (
        ("realistic_n_50_to_400", np.linspace(50, 400, 12).astype(int)),
        ("large_n_50_to_4000", np.linspace(50, 4000, 40).astype(int)),
    ):
        floored, unfloored = build(sizes, 10.0), build(sizes, 0.0)
        sm_f, sm_u = sample_min(floored), sample_min(unfloored)
        as_f, as_u = asymptotic(floored), asymptotic(unfloored)
        regimes[label] = {
            "total_samples": int(np.sum(sizes)),
            "sample_minimum_floored": sm_f,
            "sample_minimum_unfloored": sm_u,
            "sample_minimum_reports_positive_floor_for_unfloored": bool(sm_u > 0),
            "sample_minimum_relative_error_unfloored": float(sm_u),
            "asymptotic_floored": as_f,
            "asymptotic_unfloored": as_u,
            "asymptotic_correct": bool(as_f > 0.5 and as_u <= 0.5),
        }

    # Core, regime-independent facts:
    #  (a) sample minimum is ALWAYS strictly positive -- it can never return
    #      a non-positive value, so it cannot falsify a positivity claim;
    #  (b) sample minimum is biased UPWARD for the floored process;
    #  (c) the asymptotic estimator recovers the true floor and returns
    #      approximately zero when there is none.
    sm_never_nonpositive = all(
        r["sample_minimum_floored"] > 0 and r["sample_minimum_unfloored"] > 0
        for r in regimes.values())
    sm_biased_up = all(r["sample_minimum_floored"] >= 10.0 for r in regimes.values())
    as_correct_everywhere = all(r["asymptotic_correct"] for r in regimes.values())
    as_recovers_floor = abs(regimes["large_n_50_to_4000"]["asymptotic_floored"] - 10.0) < 0.1

    return {
        "claim": "eta detects uninformative bindings; asymptotic floor is falsifiable "
                 "while the sample minimum cannot return a non-positive value",
        "theorem": "Prop 9.2, Rem 9.3",
        "eta_separated": eta_sep,
        "eta_compressed": eta_comp,
        "separated_binding_informative": bool(eta_sep > 0.5),
        "compressed_binding_flagged": bool(eta_comp < 0.05),
        "floor_estimators_by_regime": regimes,
        "sample_minimum_never_returns_nonpositive": bool(sm_never_nonpositive),
        "sample_minimum_biased_upward": bool(sm_biased_up),
        "asymptotic_correct_in_all_regimes": bool(as_correct_everywhere),
        "asymptotic_recovers_true_floor": bool(as_recovers_floor),
        "interpretation": (
            "The sample minimum returns a strictly positive value for BOTH a "
            "floored and an unfloored process in every regime, so it cannot "
            "falsify a positivity claim; it is also biased upward, which by "
            "Prop 4.8 of the algebra inflates the powers of events acting near "
            "the floor. With very large samples it happens to order the two "
            "processes correctly, but ordering is not falsification. The "
            "asymptotic estimator recovers the true floor and returns "
            "approximately zero when none exists."
        ),
        "pass": bool(eta_sep > 0.5 and eta_comp < 0.05
                     and sm_never_nonpositive and sm_biased_up
                     and as_correct_everywhere and as_recovers_floor),
    }


# ----------------------------------------------------------------------
# Driver
# ----------------------------------------------------------------------

def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    checks = {
        "parsing_and_mandatory_exclusion": check_parsing(),
        "typing_rules": check_typing(),
        "operational_semantics": check_semantics(),
        "closure_vs_threshold": check_closure_vs_threshold(),
        "substrate_diagnostics": check_diagnostics(),
    }

    failed = [n for n, c in checks.items() if not c["pass"]]
    results = {
        "meta": {
            "paper": "Mekaneck: A Substrate-Neutral Language for Individuation-Structured Inquiry",
            "language": ".mck",
            "seed": SEED,
        },
        "checks": checks,
        "summary": {
            "n_checks": len(checks),
            "n_passed": len(checks) - len(failed),
            "n_failed": len(failed),
            "failed": failed,
            "all_passed": not failed,
        },
    }

    out = os.path.join(OUT_DIR, "mekaneck_results.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"wrote {out}")
    print(json.dumps(results["summary"], indent=2))
    for name, c in checks.items():
        print(f"  {'PASS' if c['pass'] else 'FAIL'}  {name:34s} [{c['theorem']}]")


if __name__ == "__main__":
    main()
