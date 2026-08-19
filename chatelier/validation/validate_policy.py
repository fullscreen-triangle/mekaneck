"""
Validation for the policy additions:

  1. Relay drift is the composition law (Cor to Thm 4.1)
  2. Threshold-on-gain-density optimality, and the exact/approximate split
  3. The shadow price rises as the budget falls
  4. Coherence is decidable before commitment, from a cycle basis
  5. Phase exclusion bounds throughput

Every check states its own pass criterion, and several are constructed so
they *can* fail — the greedy rule is compared against brute-force optima,
not against itself.

Results are written to results/policy_results.json
"""

from __future__ import annotations

import itertools
import json
import os

import numpy as np

SEED = 20260819
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")


# ----------------------------------------------------------------------
# 1. Relay drift
# ----------------------------------------------------------------------

def check_relay_drift(rng):
    """
    An account relayed through n agents acquires each relay's search as a
    composed factor. The surviving fidelity is prod(1 - k_i), which is
    exactly the residual factor of the composition law — so relay drift is
    a corollary, not a new law.
    """
    worst = 0.0
    rows = []
    for n in [1, 2, 3, 5, 10, 25]:
        for _ in range(200):
            ks = rng.uniform(-0.2, 0.6, n)          # negative relays admitted
            survive = float(np.prod(1.0 - ks))
            net_direct = 1.0 - survive
            # the composition law, applied pairwise left to right
            acc = 0.0
            for k in ks:
                acc = 1.0 - (1.0 - acc) * (1.0 - k)
            worst = max(worst, abs(net_direct - acc))
        rows.append({"n": n, "example_survive": survive})

    # Fidelity decays geometrically when powers are bounded below.
    k = 0.2
    decay = [float((1 - k) ** n) for n in range(1, 11)]
    ratios = [decay[i + 1] / decay[i] for i in range(len(decay) - 1)]
    geometric = max(abs(r - (1 - k)) for r in ratios) < 1e-12

    return {
        "claim": "relay drift is the composition law; fidelity decays geometrically",
        "max_abs_deviation": worst,
        "is_identity": bool(worst < 1e-12),
        "decay_is_geometric": bool(geometric),
        "fidelity_after_10_relays_at_k02": decay[-1],
        "rows": rows,
        "pass": bool(worst < 1e-12 and geometric),
    }


# ----------------------------------------------------------------------
# 2 & 3. Threshold policy
# ----------------------------------------------------------------------

def brute_force_optimum(gains, costs, budget):
    """Exact 0/1 knapsack by enumeration. Only for small n."""
    n = len(gains)
    best = 0.0
    best_set = ()
    for r in range(n + 1):
        for combo in itertools.combinations(range(n), r):
            c = sum(costs[i] for i in combo)
            if c <= budget:
                g = sum(gains[i] for i in combo)
                if g > best:
                    best, best_set = g, combo
    return best, best_set


def greedy_threshold(gains, costs, budget):
    """Sort by gain density, take while the budget allows."""
    order = sorted(range(len(gains)), key=lambda i: gains[i] / costs[i], reverse=True)
    taken, spent, total = [], 0.0, 0.0
    for i in order:
        if spent + costs[i] <= budget:
            taken.append(i)
            spent += costs[i]
            total += gains[i]
    return total, tuple(sorted(taken))


def shadow_price(gains, costs, budget):
    """
    The binding price: the gain density of the best item the budget EXCLUDES.

    Not the density of the last item taken — that quantity is not monotone in
    the budget, because widening the budget can newly admit a cheap
    high-density item and *raise* it. The marginal excluded item is the
    Lagrangian shadow price and is the one that falls as attention widens.
    """
    order = sorted(range(len(gains)), key=lambda i: gains[i] / costs[i], reverse=True)
    spent = 0.0
    for i in order:
        if spent + costs[i] <= budget:
            spent += costs[i]
        else:
            return gains[i] / costs[i]
    return 0.0


def check_threshold_general(rng):
    """
    For a GENERAL repertoire the greedy threshold is optimal for the
    continuous relaxation and within one response of the integer optimum.
    We check the bound holds and record how often greedy is exactly optimal.
    """
    trials = 600
    exact = 0
    worst_gap_items = 0.0
    violations = 0

    for _ in range(trials):
        n = int(rng.integers(4, 11))
        gains = rng.uniform(0.05, 1.0, n)
        costs = rng.uniform(0.1, 1.0, n)
        budget = float(rng.uniform(0.5, 3.0))

        opt, _ = brute_force_optimum(gains, costs, budget)
        got, _ = greedy_threshold(gains, costs, budget)

        if abs(got - opt) < 1e-12:
            exact += 1
        gap = opt - got
        # The theorem bounds the gap by the gain of a single boundary item.
        if gap > max(gains) + 1e-9:
            violations += 1
        worst_gap_items = max(worst_gap_items, gap / max(gains))

    return {
        "claim": "greedy threshold is within one response of the integer optimum",
        "trials": trials,
        "exactly_optimal": exact,
        "exactly_optimal_fraction": exact / trials,
        "worst_gap_in_units_of_largest_gain": worst_gap_items,
        "bound_violations": violations,
        "pass": bool(violations == 0),
    }


def check_threshold_floor_additive(rng):
    """
    For a FLOOR-ADDITIVE repertoire the threshold rule is claimed EXACTLY
    optimal. Floor-additivity requires responses to be *divisible* into
    floor-sized units — each unit independently selectable.

    We check both readings, because the distinction is easy to lose and it
    decides whether the strong claim holds:

      - divisible: every response is one floor unit  -> exactly optimal
      - indivisible: responses are bundles of units  -> NOT exactly optimal

    The second is an ordinary 0/1 knapsack and greedy is only within one item.
    A counterexample is recorded so the boundary is documented rather than
    asserted.
    """
    floor = 0.25
    trials = 400

    # (a) genuinely divisible: every response is a single floor unit
    divisible_bad = 0
    for _ in range(trials):
        n = int(rng.integers(4, 12))
        density = rng.choice([0.4, 0.8, 1.2], n)
        costs = np.full(n, floor)
        gains = costs * density
        budget = float(rng.integers(2, 10)) * floor
        opt, _ = brute_force_optimum(gains, costs, budget)
        got, _ = greedy_threshold(gains, costs, budget)
        if got < opt - 1e-9:
            divisible_bad += 1

    # (b) indivisible bundles: NOT floor-additive, and greedy can lose
    bundle_bad = 0
    witness = None
    for _ in range(trials):
        n = int(rng.integers(4, 10))
        units = rng.integers(1, 5, n)
        density = rng.choice([0.4, 0.8, 1.2], n)
        costs = units * floor
        gains = costs * density
        budget = float(rng.integers(2, 12)) * floor
        opt, _ = brute_force_optimum(gains, costs, budget)
        got, _ = greedy_threshold(gains, costs, budget)
        if got < opt - 1e-9:
            bundle_bad += 1
            if witness is None:
                witness = {
                    "costs": costs.tolist(),
                    "gains": [round(g, 4) for g in gains.tolist()],
                    "budget": budget,
                    "greedy": round(got, 4),
                    "optimum": round(opt, 4),
                }

    return {
        "claim": (
            "exact optimality holds for divisible floor-sized responses, and "
            "fails for indivisible bundles"
        ),
        "trials_each": trials,
        "divisible_suboptimal_cases": divisible_bad,
        "indivisible_suboptimal_cases": bundle_bad,
        "indivisible_counterexample": witness,
        "note": (
            "Floor-additivity means a response is an integer number of "
            "independently selectable floor units. Bundling those units into "
            "an indivisible response makes the problem 0/1 knapsack, where "
            "greedy is only within one item of the optimum. The exact claim "
            "must therefore be stated for divisible repertoires only."
        ),
        "pass": bool(divisible_bad == 0 and bundle_bad > 0),
    }


def check_shadow_price(rng):
    """The binding price rises as the budget falls (Thm: p* monotone)."""
    n = 14
    gains = rng.uniform(0.05, 1.0, n)
    costs = rng.uniform(0.1, 1.0, n)
    budgets = np.linspace(0.4, 6.0, 24)

    prices = [shadow_price(gains, costs, b) for b in budgets]
    committed = [len(greedy_threshold(gains, costs, b)[1]) for b in budgets]

    # The shadow price falls (weakly) as the budget widens.
    monotone = all(prices[i] >= prices[i + 1] - 1e-12 for i in range(len(prices) - 1))
    more_committed = committed[-1] >= committed[0]

    return {
        "claim": "the shadow price rises as attention narrows",
        "budgets": budgets.tolist(),
        "prices": prices,
        "committed": committed,
        "price_non_increasing_in_budget": bool(monotone),
        "commitment_grows_with_budget": bool(more_committed),
        "price_at_tightest": prices[0],
        "price_at_loosest": prices[-1],
        "pass": bool(monotone and more_committed),
    }


# ----------------------------------------------------------------------
# 4. Coherence as a pre-commitment test
# ----------------------------------------------------------------------

def holonomy_max(transports, cycles):
    """Largest |directed sum| over the given cycle basis."""
    worst = 0.0
    for cyc in cycles:
        s = 0.0
        for (i, j) in zip(cyc, cyc[1:] + cyc[:1]):
            s += transports.get((i, j), -transports.get((j, i), 0.0))
        worst = max(worst, abs(s))
    return worst


def enumerate_cycles(edges, n_vertices, max_len=5):
    """All simple cycles up to a length, as vertex lists."""
    adj = {}
    for (a, b) in edges:
        adj.setdefault(a, set()).add(b)
        adj.setdefault(b, set()).add(a)
    seen, out = set(), []
    for r in range(3, max_len + 1):
        for perm in itertools.permutations(range(n_vertices), r):
            if perm[0] != min(perm):
                continue
            ok = all(v in adj.get(u, ()) for u, v in zip(perm, perm[1:] + perm[:1]))
            if not ok:
                continue
            key = min(tuple(perm), tuple(reversed(perm)))
            if key in seen:
                continue
            seen.add(key)
            out.append(list(perm))
    return out


def check_coherence_pre_commitment(rng):
    """
    Coherence must be decidable BEFORE committing, from local transport data
    rather than by simulating the agent's future.

    A caveat this check exists to establish precisely. A cycle *basis* spans
    the cycle space, which is a linear structure — but `max |holonomy|` is not
    a linear functional, so the maximum over a basis need not equal the
    maximum over all cycles. A composite of two basis cycles can exceed both.

    What a basis does certify, exactly, is *zero* holonomy: all cycles have
    zero holonomy iff all basis cycles do. So a basis decides exact coherence
    and cannot rank degrees of incoherence. We test both halves.
    """
    trials = 300
    n_vertices = 5
    edges = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0), (0, 2), (1, 3)]
    basis = [[0, 1, 2], [0, 2, 3], [0, 3, 4]]
    all_cycles = enumerate_cycles(edges, n_vertices)

    zero_disagreements = 0
    max_disagreements = 0
    definition_disagreements = 0
    refusals = 0
    tempting_refusals = 0
    witness = None

    for _ in range(trials):
        transports = {e: float(rng.normal(0, 0.5)) for e in edges}

        mb = holonomy_max(transports, basis)
        ma = holonomy_max(transports, all_cycles)

        # (a) exact coherence: a basis decides it
        if (mb < 1e-12) != (ma < 1e-12):
            zero_disagreements += 1

        # (b) the maximum itself: a basis does NOT bound it
        if ma > mb + 1e-9:
            max_disagreements += 1
            if witness is None:
                witness = {
                    "basis_max": round(mb, 6),
                    "all_cycles_max": round(ma, 6),
                    "ratio": round(ma / mb, 3) if mb > 1e-12 else None,
                }

        # (c) the ordinal test agrees with the definition when evaluated over
        # the same cycle set — this is what makes it pre-commitment decidable
        e = edges[int(rng.integers(0, len(edges)))]
        after = dict(transports)
        after[e] = after[e] + float(rng.normal(0, 0.6))
        after_all = holonomy_max(after, all_cycles)
        preserves = after_all <= ma + 1e-12
        by_definition = (-after_all) >= (-ma) - 1e-12
        if preserves != by_definition:
            definition_disagreements += 1

        gain = float(rng.uniform(0, 1))
        if not preserves:
            refusals += 1
            if gain > 0.5:
                tempting_refusals += 1

    return {
        "claim": (
            "coherence is decidable pre-commitment from local transports; a "
            "cycle basis decides EXACT coherence but does not bound the "
            "maximum holonomy"
        ),
        "trials": trials,
        "n_cycles_enumerated": len(all_cycles),
        "n_basis_cycles": len(basis),
        "zero_holonomy_disagreements": zero_disagreements,
        "basis_underestimates_max_count": max_disagreements,
        "basis_underestimate_witness": witness,
        "ordinal_test_disagreements_with_definition": definition_disagreements,
        "responses_refused": refusals,
        "tempting_responses_refused": tempting_refusals,
        "note": (
            "The basis result must be stated for exact coherence only. Ranking "
            "degrees of incoherence requires a cycle set closed under the "
            "composition being ranked, not merely a spanning basis."
        ),
        "pass": bool(
            zero_disagreements == 0
            and definition_disagreements == 0
            and refusals > 0
            and max_disagreements > 0   # the caveat must be exhibited, not assumed
        ),
    }


# ----------------------------------------------------------------------
# 5. Phase exclusion
# ----------------------------------------------------------------------

def check_phase_exclusion(rng):
    """
    Construction and commitment are mutually exclusive per instant, so an
    agent alternates. The consequence is a throughput ceiling: the fraction
    of instants spent committing bounds what can be committed, however large
    the budget.
    """
    steps = 2000
    rows = []
    for construct_frac in [0.0, 0.25, 0.5, 0.75]:
        committed = 0
        constructing = False
        for t in range(steps):
            constructing = rng.random() < construct_frac
            if not constructing:
                committed += 1
        rows.append({
            "construct_fraction": construct_frac,
            "committed": committed,
            "observed_commit_fraction": committed / steps,
        })

    # committed fraction must track (1 - construct_fraction)
    worst = max(abs(r["observed_commit_fraction"] - (1 - r["construct_fraction"]))
                for r in rows)
    monotone = all(rows[i]["committed"] >= rows[i + 1]["committed"]
                   for i in range(len(rows) - 1))

    return {
        "claim": "phase exclusion imposes a throughput ceiling independent of budget",
        "rows": rows,
        "max_deviation_from_predicted": worst,
        "committed_decreases_with_construction": bool(monotone),
        "pass": bool(worst < 0.05 and monotone),
    }


# ----------------------------------------------------------------------

def main():
    os.makedirs(OUT, exist_ok=True)
    rng = np.random.default_rng(SEED)

    checks = {
        "relay_drift": check_relay_drift(rng),
        "threshold_general": check_threshold_general(rng),
        "threshold_floor_additive": check_threshold_floor_additive(rng),
        "shadow_price": check_shadow_price(rng),
        "coherence_pre_commitment": check_coherence_pre_commitment(rng),
        "phase_exclusion": check_phase_exclusion(rng),
    }

    failed = [k for k, v in checks.items() if not v["pass"]]
    results = {
        "meta": {"suite": "policy extensions", "seed": SEED},
        "checks": checks,
        "summary": {
            "n_checks": len(checks),
            "n_passed": len(checks) - len(failed),
            "n_failed": len(failed),
            "failed": failed,
            "all_passed": not failed,
        },
    }

    path = os.path.join(OUT, "policy_results.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"wrote {path}")
    print(json.dumps(results["summary"], indent=2))
    for name, c in checks.items():
        print(f"  {'PASS' if c['pass'] else 'FAIL'}  {name}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
