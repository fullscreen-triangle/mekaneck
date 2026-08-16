"""
Recompute, with the same seeds as the panel scripts, every quantity that a
caption needs to quote. Writes results/panel_stats.json.

Nothing here is plotted; this exists so that captions state measured numbers
rather than approximations.
"""

from __future__ import annotations

import itertools
import json
import math
import os
import random

import numpy as np
from scipy.stats import binom

from validate_algebra import (Regime, generate_cascades, kappa, compose_mult,
                              type_averaged_kappas, separation_ratio,
                              floor_asymptotic, pearson, rmse, LAWS)
from validate_kernel import Kernel, mkchunk
from mekaneck import (parse, typecheck, evaluate, evaluate_threshold,
                      Resolved, Declined, LetDecl)

SEED = 20260816
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")

REGIMES = [
    Regime("separated", {"A->B": 0.55, "B->C": 0.30, "C->A": 0.08, "A->C": 0.42},
           0.03, 10.0, 100.0),
    Regime("intermediate", {"A->B": 0.36, "B->C": 0.30, "C->A": 0.24, "A->C": 0.33},
           0.08, 10.0, 100.0),
    Regime("compressed", {"A->B": 0.300, "B->C": 0.302, "C->A": 0.299, "A->C": 0.301},
           0.12, 10.0, 100.0),
]

R = {}


# ======================================================================
# ALGEBRA
# ======================================================================

def algebra():
    a = {}

    # ---- Panel 1 (same construction as make_panels_algebra.panel1) ----
    rng = np.random.default_rng(SEED)
    sizes = np.unique(np.logspace(1.7, 3.6, 18).astype(int))
    sm_err, as_err = [], []
    for n in sizes:
        sub = np.unique(np.linspace(40, n, 10).astype(int))
        stages = [10.0 + 40.0 * rng.random(m) ** 3 for m in sub]
        sm_err.append(np.min(np.concatenate(stages)) - 10.0)
        as_err.append(abs(floor_asymptotic(stages) - 10.0))
    a["p1A"] = {
        "n_min": int(sizes.min()), "n_max": int(sizes.max()),
        "n_points": len(sizes),
        "sample_min_err_first": float(sm_err[0]),
        "sample_min_err_last": float(sm_err[-1]),
        "sample_min_err_median": float(np.median(sm_err)),
        "asym_err_first": float(as_err[0]),
        "asym_err_last": float(as_err[-1]),
        "asym_err_median": float(np.median(as_err)),
        "sample_min_all_positive": bool(np.all(np.array(sm_err) > 0)),
    }

    sizes_b = np.unique(np.logspace(1.7, 3.6, 22).astype(int))
    sm_u, as_u = [], []
    for n in sizes_b:
        sub = np.unique(np.linspace(40, n, 10).astype(int))
        stages = [40.0 * rng.random(m) ** 3 for m in sub]
        sm_u.append(np.min(np.concatenate(stages)))
        as_u.append(floor_asymptotic(stages))
    sm_u, as_u = np.asarray(sm_u), np.asarray(as_u)
    a["p1B"] = {
        "n_points": len(sizes_b),
        "sample_min_min": float(sm_u.min()), "sample_min_max": float(sm_u.max()),
        "sample_min_n_negative": int((sm_u <= 0).sum()),
        "asym_min": float(as_u.min()), "asym_max": float(as_u.max()),
        "asym_n_negative": int((as_u < 0).sum()),
        "asym_frac_negative": float((as_u < 0).mean()),
    }

    # C: kappa inflation, true kappa 0.4
    a["p1C"] = {}
    for sb in (70.0, 30.0, 15.0):
        gap = sb - 10.0
        for e in (2.0, 5.0):
            if e < gap:
                a["p1C"][f"Sb{int(sb)}_eps{int(e)}"] = float(0.4 * gap / (gap - e))
    a["p1D"] = {
        "eps_range": [-4, 10], "gap_range": [12, 90],
        "max_rel_err": float(10.0 / (12.0 - 10.0)),
        "min_rel_err": float(-4.0 / (90.0 + 4.0)),
    }

    # ---- Panel 2 ----
    rng = np.random.default_rng(SEED)
    cascades = generate_cascades(REGIMES[0], 1500, (3, 5), rng)
    floor = REGIMES[0].floor
    inst, meas, lens = [], [], []
    for c in cascades:
        st = c["states"]
        ks = [kappa(st[i], st[i + 1], floor) for i in range(len(st) - 1)]
        inst.append(compose_mult(ks))
        meas.append((st[0] - st[-1]) / (st[0] - floor))
        lens.append(len(ks))
    inst, meas, lens = map(np.asarray, (inst, meas, lens))
    kbar, per_type = type_averaged_kappas(cascades, floor)
    ta = np.array([compose_mult([kbar[t] for t in c["types"]]) for c in cascades])
    dev_i, dev_t = np.abs(inst - meas), np.abs(ta - meas)
    a["p2"] = {
        "n_cascades": len(cascades),
        "len_min": int(lens.min()), "len_max": int(lens.max()),
        "inst_max_dev": float(dev_i.max()),
        "inst_median_dev": float(np.median(dev_i)),
        "inst_r": 1.0,
        "ta_max_dev": float(dev_t.max()),
        "ta_median_dev": float(np.median(dev_t)),
        "ta_r": float(pearson(ta, meas)),
        "ta_rmse": float(rmse(ta, meas)),
        "orders_of_magnitude": float(np.log10(np.median(dev_t) /
                                              max(np.median(dev_i), 1e-18))),
        "meas_min": float(meas.min()), "meas_max": float(meas.max()),
    }

    # ---- Panel 3 ----
    rng = np.random.default_rng(SEED)
    p3 = {}
    for reg in REGIMES:
        cs = generate_cascades(reg, 3000, (3, 5), rng)
        kb, pt = type_averaged_kappas(cs, reg.floor)
        eta = separation_ratio(pt)
        m = np.array([(c["states"][0] - c["states"][-1]) /
                      (c["states"][0] - reg.floor) for c in cs])
        laws = {}
        for name, fn in LAWS.items():
            pred = np.array([fn([kb[t] for t in c["types"]]) for c in cs])
            laws[name] = {"r": pearson(pred, m), "rmse": rmse(pred, m)}
        within = {t: float(np.std(v)) for t, v in pt.items()}
        p3[reg.name] = {
            "eta": eta, "n": len(cs), "type_means": kb,
            "within_sd_mean": float(np.mean(list(within.values()))),
            "type_mean_spread": float(max(kb.values()) - min(kb.values())),
            "laws": laws,
        }
    a["p3"] = p3

    # ---- Panel 4 ----
    kfix = 0.3
    a["p4"] = {
        "kappa_fixed": kfix,
        "mult_at_n12": float(1 - (1 - kfix) ** 12),
        "add_saturates_at_n": int(math.ceil(1.0 / kfix)),
        "geo_equals_max_at_const_kappa": True,
        "summable_limit": float(np.exp(np.sum(np.log1p(
            -np.array([2.0 ** -(i + 1) for i in range(2000)]))))),
        "divergent_at_1e6": float(1.0 / (10 ** 6 + 1)),
        "marginal_k05_step10": float(0.5 * 0.5 ** 9),
        "marginal_k015_step10": float(0.15 * 0.85 ** 9),
    }
    R["algebra"] = a


# ======================================================================
# KERNEL
# ======================================================================

def kernel():
    k = {}
    rng = random.Random(SEED)

    # ---- Panel 1 ----
    from make_panels_kernel import run_with_failure_rate
    rates = np.linspace(0, 1, 21)
    n_chunks, reps = 60, 12
    emitted, errored = [], []
    for p in rates:
        e, er = [], []
        for _ in range(reps):
            v, x, _ = run_with_failure_rate(p, n_chunks, rng)
            e.append(v); er.append(x)
        emitted.append(np.mean(e)); errored.append(np.mean(er))
    ff = [((1 - p) ** np.arange(n_chunks)).sum() if p > 0 else n_chunks
          for p in rates]
    k["p1"] = {
        "n_chunks": n_chunks, "reps": reps, "n_rates": len(rates),
        "inert_min_evaluated": float(np.min(emitted)),
        "inert_max_evaluated": float(np.max(emitted)),
        "inert_constant": bool(np.allclose(emitted, n_chunks)),
        "failfast_at_p05": float(ff[list(rates).index(0.5)]),
        "failfast_at_p10": float(ff[-1]),
        "errors_at_p05": float(errored[list(rates).index(0.5)]),
        "single_failure_inert": n_chunks,
    }

    # ---- Panel 2 ----
    rng = random.Random(SEED)

    def contribution(name, taus, per=2):
        return {t: {mkchunk(f"{name}:{t}:{i}", lambda: 0) for i in range(per)}
                for t in taus}

    universe = ["a", "b", "c", "d", "e"]
    orders_tested, distinct = [], []
    for n_contrib in range(2, 6):
        contribs = [contribution(f"C{i}", rng.sample(universe, 3))
                    for i in range(n_contrib)]
        fps = set()
        for perm in itertools.permutations(range(n_contrib)):
            kk = Kernel()
            for i in perm:
                kk.merge(contribs[i])
            fps.add(kk.fingerprint())
        orders_tested.append(math.factorial(n_contrib))
        distinct.append(len(fps))

    base = contribution("B", ["a", "b", "c"])
    k2 = Kernel()
    idem = []
    for _ in range(12):
        k2.merge(base)
        idem.append(sum(len(n.chunks) for n in k2.nodes.values()))

    k0 = Kernel(); k0.merge(contribution("X", ["a", "b", "c"]))
    ref = k0.fingerprint()

    def hexdist(x, y):
        return sum(1 for p, q in zip(x, y) if p != q) / len(x)

    reord, changed = [], []
    for _ in range(30):
        kk = Kernel()
        items = list(contribution("X", ["a", "b", "c"]).items())
        rng.shuffle(items)
        for t, c in items:
            kk.merge({t: c})
        reord.append(hexdist(ref, kk.fingerprint()))
    for i in range(30):
        kk = Kernel()
        cc = contribution("X", ["a", "b", "c"])
        cc["a"] = {mkchunk(f"X:a:mut{i}", lambda: 0), mkchunk("X:a:1", lambda: 0)}
        kk.merge(cc)
        changed.append(hexdist(ref, kk.fingerprint()))

    k["p2"] = {
        "total_orders_tested": int(sum(orders_tested)),
        "max_orders": int(max(orders_tested)),
        "distinct_protocols": sorted(set(distinct)),
        "idempotent_first": idem[0], "idempotent_last": idem[-1],
        "naive_last": 6 * 12,
        "reorder_dist_max": float(max(reord)),
        "changed_dist_mean": float(np.mean(changed)),
        "changed_dist_min": float(min(changed)),
        "digest_hex_len": len(ref),
    }

    # ---- Panel 3 ----
    from make_panels_kernel import branching_run
    runs = [branching_run(s, True) for s in range(300)]
    paths = [p for _, p in runs]
    counts = {}
    ent = []
    for i, p in enumerate(paths, 1):
        counts[p] = counts.get(p, 0) + 1
        pr = np.array(list(counts.values()), float) / i
        ent.append(float(-(pr * np.log2(pr)).sum()))
    stores = [tuple(kk.read("n7")) for kk, _ in runs]
    k["p3"] = {
        "n_runs": len(runs),
        "distinct_trajectories": len(set(paths)),
        "distinct_protocols": len(set(kk.fingerprint() for kk, _ in runs)),
        "distinct_terminal_stores": len(set(stores)),
        "final_entropy_bits": ent[-1],
        "entropy_at_50": ent[49],
        "path_len": len(paths[0]),
    }

    # ---- Panel 4 ----
    rng = random.Random(SEED)
    per = 3
    sizes = np.arange(4, 61, 4)
    execs, chunks_done = [], []
    for n in sizes:
        kk = Kernel()
        kk.merge({f"n{i}": {mkchunk(f"n{i}c{j}", lambda: 1) for j in range(per)}
                  for i in range(n)})
        e = 0
        while kk.ready_nodes():
            kk.run_node(rng.choice(kk.ready_nodes()))
            e += 1
        execs.append(e); chunks_done.append(kk.record)
    lat = []
    for trial in range(120):
        kk = Kernel()
        kk.merge({f"n{i}": {mkchunk(f"n{i}c0", lambda: 1)} for i in range(12)})
        while kk.ready_nodes():
            kk.run_node(rng.choice(kk.ready_nodes()))
        kk.merge({f"n{rng.randrange(12)}": {mkchunk(f"late{trial}", lambda: 1)}})
        st = 0
        while kk.ready_nodes():
            kk.run_node(rng.choice(kk.ready_nodes()))
            st += 1
        lat.append(st)
    k["p4"] = {
        "chunks_per_node": per,
        "execs_equal_nodes": bool(list(execs) == list(sizes)),
        "max_nodes": int(sizes.max()),
        "record_at_max": int(chunks_done[-1]),
        "latency_max": int(max(lat)), "latency_min": int(min(lat)),
        "latency_mean": float(np.mean(lat)),
        "n_starved": int(sum(1 for x in lat if x == 0)),
        "trials": len(lat),
    }
    R["kernel"] = k


# ======================================================================
# MEKANECK
# ======================================================================

def mck():
    m = {}
    from make_panels_mekaneck import get_seek
    seek = get_seek()

    # ---- Panel 1 ----
    rng = np.random.default_rng(SEED)
    p_agree = np.linspace(0.05, 1.0, 20)
    trials = 400
    unc = {"cellA": 5.0, "cellB": 40.0}
    thr_wrong, clo_dec, thr_inv, clo_inv = [], [], [], []
    for p in p_agree:
        w = d = 0; ti = ci = 0
        for _ in range(trials):
            sub = {c: ("cellA" if rng.random() < p else "cellB") for c in seek.via}
            order = list(rng.permutation(seek.via))
            t = evaluate_threshold(seek, sub, unc, 10.0, order=order)
            c_ = evaluate(seek, sub, order=order)
            ti += t.record; ci += c_.record
            if isinstance(c_.outcome, Declined):
                d += 1
                if isinstance(t.outcome, Resolved):
                    w += 1
        thr_wrong.append(w / trials); clo_dec.append(d / trials)
        thr_inv.append(ti / trials); clo_inv.append(ci / trials)
    thr_wrong, clo_dec = np.array(thr_wrong), np.array(clo_dec)

    res = dec = 0
    for _ in range(500):
        nc = int(rng.choice([1, 1, 2, 3]))
        cells = [f"cell{i}" for i in range(nc)]
        sub = {c: cells[int(rng.integers(0, nc))] for c in seek.via}
        if isinstance(evaluate(seek, sub).outcome, Resolved):
            res += 1
        else:
            dec += 1

    m["p1"] = {
        "trials_per_level": trials, "levels": len(p_agree),
        "curves_identical": bool(np.allclose(thr_wrong, clo_dec)),
        "max_abs_diff": float(np.max(np.abs(thr_wrong - clo_dec))),
        "peak_rate": float(clo_dec.max()),
        "peak_at_agreement": float(p_agree[int(clo_dec.argmax())]),
        "rate_at_p1": float(clo_dec[0]), "rate_at_p10": float(clo_dec[-1]),
        "thr_inv_at_low": float(thr_inv[0]), "thr_inv_at_high": float(thr_inv[-1]),
        "clo_inv_peak": float(max(clo_inv)),
        "resolved_500": res, "declined_500": dec,
    }

    # ---- Panel 2 ----
    rng = np.random.default_rng(SEED)
    outs_per, recs, cells_n = [], [], []
    for _ in range(500):
        nc = int(rng.choice([1, 1, 2, 3]))
        cells = [f"cell{i}" for i in range(nc)]
        sub = {c: cells[int(rng.integers(0, nc))] for c in seek.via}
        o, r = set(), []
        for order in itertools.permutations(seek.via):
            cfg = evaluate(seek, sub, order=list(order))
            o.add(repr(cfg.outcome)); r.append(cfg.record)
        outs_per.append(len(o)); recs.append(r)
        cells_n.append(len(set(sub.values())))
    recs = np.array(recs); cells_n = np.array(cells_n)
    mx = recs.max(axis=1)
    m["p2"] = {
        "n_substrates": 500, "orderings": 6, "evaluations": 3000,
        "all_deterministic": bool(set(outs_per) == {1}),
        "max_invocations": int(mx.max()),
        "bound": len(seek.via),
        "n_over_bound": int((mx > len(seek.via)).sum()),
        "invocations_equal_cells": bool(np.all(mx == cells_n)),
        "hist_1": int((mx == 1).sum()), "hist_2": int((mx == 2).sum()),
        "hist_3": int((mx == 3).sum()),
    }

    # ---- Panel 3 ----
    prog_tpl = """
substrate Osc {{ receivers : r(); observable : o(); events : e(); floor : f(); }}
{cats}
let x = seek t() excluding rest() via ({names}) until closure;
report x;
"""
    accepted = {}
    for kk in range(1, 7):
        names = [f"c{i}" for i in range(kk)]
        cats = "\n".join(
            f"catalyst {n} : f() independent {', '.join(x for x in names if x != n)};"
            if kk > 1 else f"catalyst {n} : f();" for n in names)
        src = prog_tpl.format(cats=cats, names=", ".join(names))
        try:
            typecheck(parse(src), floor_values={"Osc": 5.0})
            accepted[kk] = 1
        except Exception:
            accepted[kk] = 0
    m["p3"] = {
        "accepted_by_k": accepted,
        "first_accepted_k": min(k for k, v in accepted.items() if v),
        "robust_k3_q02": float(1 - binom.cdf(1, 3, 0.8)),
        "robust_k2_q02": float(1 - binom.cdf(1, 2, 0.8)),
        "robust_k5_q02": float(1 - binom.cdf(1, 5, 0.8)),
        "robust_k3_q04": float(1 - binom.cdf(1, 3, 0.6)),
    }

    # ---- Panel 4 ----
    rng = np.random.default_rng(SEED)

    def eta_of(pt):
        mns = [np.mean(v) for v in pt.values()]
        vb = float(np.var(mns)); vw = float(np.mean([np.var(v) for v in pt.values()]))
        return vb / (vb + vw) if vb + vw > 0 else 0.0

    spreads = np.linspace(0.0, 0.25, 25)
    etas = [eta_of({f"t{i}": rng.normal(0.30 + sp * (i - 1.5), 0.08, 500)
                    for i in range(4)}) for sp in spreads]
    etas = np.array(etas)
    below = spreads[etas < 0.05]
    sizes = np.unique(np.logspace(1.7, 3.6, 20).astype(int))
    sm_u, as_u = [], []
    for n in sizes:
        sub = np.unique(np.linspace(40, n, 10).astype(int))
        stages = [40.0 * rng.random(mm) ** 3 for mm in sub]
        sm_u.append(np.min(np.concatenate(stages)))
        as_u.append(floor_asymptotic(stages))
    sm_u, as_u = np.asarray(sm_u), np.asarray(as_u)
    m["p4"] = {
        "eta_at_zero_spacing": float(etas[0]),
        "eta_at_max_spacing": float(etas[-1]),
        "spacing_crossing_005": float(below.max()) if len(below) else None,
        "sample_min_all_positive": bool(np.all(sm_u > 0)),
        "sample_min_min": float(sm_u.min()),
        "asym_n_negative": int((as_u < 0).sum()),
        "asym_most_negative": float(as_u.min()),
        "n_sizes": len(sizes),
    }
    R["mekaneck"] = m


def main():
    os.makedirs(OUT, exist_ok=True)
    algebra(); kernel(); mck()
    p = os.path.join(OUT, "panel_stats.json")
    with open(p, "w", encoding="utf-8") as f:
        json.dump(R, f, indent=2)
    print("wrote", p)
    print(json.dumps(R, indent=2)[:3000])


if __name__ == "__main__":
    main()
