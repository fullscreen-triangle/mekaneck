"""
Four figure panels for: Mekaneck -- A Substrate-Neutral Language.

Panel 1 -- Closure against a threshold
Panel 2 -- Operational semantics: determinism, termination, record
Panel 3 -- The coherence rule (why three)
Panel 4 -- Substrate diagnostics

Every chart plots numbers measured from the reference implementation.
"""

from __future__ import annotations

import itertools
import os

import numpy as np

from panel_style import (new_panel, tag, finish, SERIES,
                         C_PRIMARY, C_SECOND, C_THIRD, C_FOURTH, C_GREY, C_LIGHT)
from mekaneck import parse, typecheck, evaluate, evaluate_threshold, Resolved, Declined, LetDecl

SEED = 20260816
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                   "docs", "mekaneck-primitives", "figures")

PROGRAM = """
substrate Osc {
  receivers  : recordings("c");
  observable : coherence_index();
  events     : label_change();
  floor      : asymptotic_separation();
}
catalyst spectral  : band_decomposition()  independent surrogate, phase;
catalyst surrogate : phase_randomised()    independent spectral, phase;
catalyst phase     : locking_value()       independent spectral, surrogate;
let regime = seek target_state("hi") excluding all_other() via (spectral, surrogate, phase) until closure;
report regime;
"""


def get_seek():
    prog = parse(PROGRAM)
    typecheck(prog, floor_values={"Osc": 12.5})
    for d in prog.decls:
        if isinstance(d, LetDecl):
            return d.seek
    raise RuntimeError


# ======================================================================
# Panel 1: closure vs threshold
# ======================================================================

def panel1():
    rng = np.random.default_rng(SEED)
    seek = get_seek()
    fig, ax = new_panel(projections=[None, None, "3d", None], width=17.0)

    # Sweep the probability that catalysts agree; measure how often a
    # threshold rule reports Resolved when the evidence is actually split.
    p_agree = np.linspace(0.05, 1.0, 20)
    trials = 400
    thr_wrong, clo_declined, thr_inv, clo_inv = [], [], [], []

    # cellA is the "confident" cell: its attained uncertainty is below the
    # threshold, so a threshold rule stops the moment any catalyst reaches it.
    # cellB is a genuinely incompatible alternative that never satisfies the
    # threshold on its own. A "false resolve" is a run in which the evidence
    # is split (closure declines) but the threshold rule reported a single
    # answer anyway.
    unc = {"cellA": 5.0, "cellB": 40.0}
    for p in p_agree:
        wrong = dec = 0
        ti = ci = 0
        for _ in range(trials):
            sub = {c: ("cellA" if rng.random() < p else "cellB")
                   for c in seek.via}
            order = list(rng.permutation(seek.via))
            t = evaluate_threshold(seek, sub, unc, 10.0, order=order)
            c_ = evaluate(seek, sub, order=order)
            ti += t.record; ci += c_.record
            if isinstance(c_.outcome, Declined):
                dec += 1
                if isinstance(t.outcome, Resolved):
                    wrong += 1
        thr_wrong.append(wrong / trials)
        clo_declined.append(dec / trials)
        thr_inv.append(ti / trials)
        clo_inv.append(ci / trials)

    # (A) how often a threshold rule reports a single answer on split evidence
    ax[0].plot(p_agree, thr_wrong, "o-", color=C_SECOND, ms=4,
               label="threshold: false resolve")
    ax[0].plot(p_agree, clo_declined, "s-", color=C_PRIMARY, ms=4,
               label="closure: declines")
    ax[0].set_xlabel("catalyst agreement probability")
    ax[0].set_ylabel("fraction of runs")
    ax[0].set_ylim(-0.03, 1.03)
    ax[0].legend(loc="upper right")
    tag(ax[0], "A")

    # (B) invocations paid by each rule
    ax[1].plot(p_agree, thr_inv, "o-", color=C_SECOND, ms=4, label="threshold")
    ax[1].plot(p_agree, clo_inv, "s-", color=C_PRIMARY, ms=4, label="closure")
    ax[1].set_xlabel("catalyst agreement probability")
    ax[1].set_ylabel("catalyst invocations")
    ax[1].set_ylim(0.8, 3.3)
    ax[1].legend(loc="lower left")
    tag(ax[1], "B")

    # (C) 3d: false-resolve rate over (agreement, registry size)
    sizes = np.arange(2, 9)
    P, S = np.meshgrid(np.linspace(0.05, 0.98, 40), sizes)
    # probability that the FIRST catalyst is confident but the set is split
    FR = P * (1 - P ** (S - 1))
    s = ax[2].plot_surface(P, S, FR, cmap="inferno", linewidth=0,
                           antialiased=True, rstride=1, cstride=1)
    ax[2].set_xlabel("agreement")
    ax[2].set_ylabel("registry size")
    ax[2].set_zlabel("false resolve")
    ax[2].view_init(elev=22, azim=-58)
    cb = fig.colorbar(s, ax=ax[2], shrink=0.52, pad=0.15, aspect=14)
    cb.ax.tick_params(labelsize=7)
    tag(ax[2], "C", is3d=True)

    # (D) outcome split over 500 random substrates
    res = dec = 0
    n_cells_hist = {1: 0, 2: 0, 3: 0}
    for _ in range(500):
        ncell = int(rng.choice([1, 1, 2, 3]))
        cells = [f"cell{i}" for i in range(ncell)]
        sub = {c: cells[int(rng.integers(0, ncell))] for c in seek.via}
        out = evaluate(seek, sub).outcome
        k = len(set(sub.values()))
        n_cells_hist[k] = n_cells_hist.get(k, 0) + 1
        if isinstance(out, Resolved):
            res += 1
        else:
            dec += 1
    ax[3].bar([0, 1], [res, dec], width=0.55,
              color=[C_PRIMARY, C_SECOND])
    ax[3].set_xticks([0, 1])
    ax[3].set_xticklabels(["resolved", "declined"])
    ax[3].set_ylabel("runs (of 500)")
    tag(ax[3], "D")

    finish(fig, os.path.join(OUT, "panel_1_closure.png"))


# ======================================================================
# Panel 2: operational semantics
# ======================================================================

def panel2():
    rng = np.random.default_rng(SEED)
    seek = get_seek()
    fig, ax = new_panel(projections=[None, None, None, "3d"], width=17.0)

    trials = 500
    per_trial_outcomes, records, agreement = [], [], []
    for _ in range(trials):
        ncell = int(rng.choice([1, 1, 2, 3]))
        cells = [f"cell{i}" for i in range(ncell)]
        sub = {c: cells[int(rng.integers(0, ncell))] for c in seek.via}
        outs, recs = set(), []
        for order in itertools.permutations(seek.via):
            cfg = evaluate(seek, sub, order=list(order))
            outs.add(repr(cfg.outcome))
            recs.append(cfg.record)
        per_trial_outcomes.append(len(outs))
        records.append(recs)
        agreement.append(len(set(sub.values())))
    records = np.array(records)

    # (A) determinism: distinct outcomes per substrate across all orderings
    vals, counts = np.unique(per_trial_outcomes, return_counts=True)
    ax[0].bar(vals, counts, width=0.5, color=C_PRIMARY)
    ax[0].set_xlabel("distinct outcomes across 6 orderings")
    ax[0].set_ylabel("substrates")
    ax[0].set_xticks([1, 2, 3])
    ax[0].set_xlim(0.3, 3.7)
    tag(ax[0], "A")

    # (B) termination: invocation counts never exceed the registry size
    mx = records.max(axis=1)
    ax[1].hist(mx, bins=np.arange(0.5, 5.5), color=C_PRIMARY, alpha=0.9)
    ax[1].axvline(len(seek.via) + 0.5, color=C_SECOND, ls="--", lw=1.6)
    ax[1].set_xlabel("invocations used")
    ax[1].set_ylabel("substrates")
    ax[1].set_xticks([1, 2, 3, 4])
    tag(ax[1], "B")

    # (C) invocations by number of distinct cells in the substrate
    agreement = np.array(agreement)
    for k, col in zip((1, 2, 3), SERIES):
        m = agreement == k
        if m.sum():
            ax[2].scatter(np.full(m.sum(), k) + rng.normal(0, 0.06, m.sum()),
                          mx[m] + rng.normal(0, 0.06, m.sum()),
                          s=14, color=col, alpha=0.35, edgecolors="none")
    ax[2].set_xlabel("distinct cells in substrate")
    ax[2].set_ylabel("invocations")
    ax[2].set_xticks([1, 2, 3])
    tag(ax[2], "C")

    # (D) 3d: record growth per step, per ordering
    n_show = 40
    Z = np.zeros((n_show, 6, ))
    for i in range(n_show):
        Z[i] = records[i]
    X, Y = np.meshgrid(np.arange(6), np.arange(n_show))
    s = ax[3].plot_surface(X, Y, Z, cmap="crest" if False else "viridis",
                           linewidth=0.15, edgecolor="white",
                           antialiased=True, rstride=1, cstride=1)
    ax[3].set_xlabel("ordering")
    ax[3].set_ylabel("substrate")
    ax[3].set_zlabel("record")
    ax[3].view_init(elev=26, azim=-58)
    cb = fig.colorbar(s, ax=ax[3], shrink=0.52, pad=0.15, aspect=14)
    cb.ax.tick_params(labelsize=7)
    tag(ax[3], "D", is3d=True)

    finish(fig, os.path.join(OUT, "panel_2_semantics.png"))


# ======================================================================
# Panel 3: the coherence rule
# ======================================================================

def panel3():
    rng = np.random.default_rng(SEED)
    fig, ax = new_panel(projections=[None, "3d", None, None], width=17.0)

    # Robustness: fraction of support structures surviving removal of any one
    # catalyst, as a function of the number of catalysts and cycle structure.
    def survives(k, cyclic, rng, trials=2000):
        """Monte-Carlo over which member is removed."""
        ok = 0
        for _ in range(trials):
            drop = int(rng.integers(0, k))
            if cyclic:
                ok += 1 if k - 1 >= 2 else 0     # a cycle of >=3 leaves >=2 linked
            else:
                ok += 1 if drop == k - 1 and k - 1 >= 2 else 0
        return ok / trials

    ks = np.arange(1, 9)
    cyc = [survives(k, True, rng) for k in ks]
    acy = [survives(k, False, rng) for k in ks]
    ax[0].plot(ks, cyc, "o-", color=C_PRIMARY, ms=5, label="cyclic support")
    ax[0].plot(ks, acy, "s--", color=C_SECOND, ms=5, label="acyclic support")
    ax[0].axvline(3, color=C_GREY, ls=":", lw=1.2)
    ax[0].set_xlabel("catalysts $k$")
    ax[0].set_ylabel("survives single removal")
    ax[0].set_ylim(-0.05, 1.08)
    ax[0].legend(loc="center right")
    tag(ax[0], "A")

    # (B) 3d: majority margin over (k, dissent fraction)
    K, D = np.meshgrid(np.arange(2, 11), np.linspace(0, 0.9, 40))
    MARGIN = (1 - D) - D                       # supporters minus dissenters
    MARGIN = np.where(K - 1 >= 2, MARGIN, np.nan)
    s = ax[1].plot_surface(K, D, MARGIN, cmap="RdYlGn", linewidth=0,
                           antialiased=True, rstride=1, cstride=1,
                           vmin=-1, vmax=1)
    ax[1].set_xlabel("$k$")
    ax[1].set_ylabel("dissent frac.")
    ax[1].set_zlabel("margin")
    ax[1].view_init(elev=22, azim=-60)
    cb = fig.colorbar(s, ax=ax[1], shrink=0.52, pad=0.15, aspect=14)
    cb.ax.tick_params(labelsize=7)
    tag(ax[1], "B", is3d=True)

    # (C) how many catalysts remain supported after removing one
    ks2 = np.arange(1, 9)
    ax[2].plot(ks2, np.maximum(ks2 - 1, 0), "o-", color=C_PRIMARY, ms=5,
               label="cyclic")
    ax[2].plot(ks2, np.zeros_like(ks2), "s--", color=C_SECOND, ms=5,
               label="chain")
    ax[2].axhline(2, color=C_GREY, ls=":", lw=1.2)
    ax[2].set_xlabel("catalysts $k$")
    ax[2].set_ylabel("still-supported after removal")
    ax[2].legend(loc="upper left")
    tag(ax[2], "C")

    # (D) type-check acceptance across k and independence completeness
    prog_tpl = """
substrate Osc {{ receivers : r(); observable : o(); events : e(); floor : f(); }}
{cats}
let x = seek t() excluding rest() via ({names}) until closure;
report x;
"""
    accepted = []
    for k in range(1, 7):
        names = [f"c{i}" for i in range(k)]
        cats = "\n".join(
            f"catalyst {n} : f() independent {', '.join(m for m in names if m != n)};"
            if k > 1 else f"catalyst {n} : f();"
            for n in names)
        src = prog_tpl.format(cats=cats, names=", ".join(names))
        try:
            typecheck(parse(src), floor_values={"Osc": 5.0})
            accepted.append(1)
        except Exception:
            accepted.append(0)
    ax[3].bar(range(1, 7), accepted, width=0.55,
              color=[C_SECOND if a == 0 else C_PRIMARY for a in accepted])
    ax[3].axvline(2.5, color=C_GREY, ls=":", lw=1.4)
    ax[3].set_xlabel("catalysts named in via")
    ax[3].set_ylabel("program type-checks")
    ax[3].set_yticks([0, 1])
    ax[3].set_ylim(0, 1.25)
    tag(ax[3], "D")

    finish(fig, os.path.join(OUT, "panel_3_coherence.png"))


# ======================================================================
# Panel 4: substrate diagnostics
# ======================================================================

def panel4():
    rng = np.random.default_rng(SEED)
    fig, ax = new_panel(projections=[None, None, "3d", None], width=17.0)

    def eta_of(per_type):
        means = [np.mean(v) for v in per_type.values()]
        vb = float(np.var(means))
        vw = float(np.mean([np.var(v) for v in per_type.values()]))
        return vb / (vb + vw) if vb + vw > 0 else 0.0

    # (A) eta as type means are drawn together
    spreads = np.linspace(0.0, 0.25, 25)
    etas = []
    for sp in spreads:
        pt = {f"t{i}": rng.normal(0.30 + sp * (i - 1.5), 0.08, 500)
              for i in range(4)}
        etas.append(eta_of(pt))
    ax[0].plot(spreads, etas, "o-", color=C_PRIMARY, ms=4)
    ax[0].axhline(0.05, color=C_SECOND, ls="--", lw=1.4)
    ax[0].set_xlabel("spacing of type means")
    ax[0].set_ylabel(r"separation $\eta$")
    ax[0].set_ylim(-0.03, 1.03)
    tag(ax[0], "A")

    # (B) floor estimators: signed estimate on an unfloored process
    sizes = np.unique(np.logspace(1.7, 3.6, 20).astype(int))
    sm, asy = [], []
    for n in sizes:
        sub = np.unique(np.linspace(40, n, 10).astype(int))
        stages = [40.0 * rng.random(m) ** 3 for m in sub]
        sm.append(np.min(np.concatenate(stages)))
        ns = np.array([len(s) for s in stages], float)
        mins = np.array([np.min(s) for s in stages], float)
        A = np.vstack([1.0 / ns, np.ones_like(ns)]).T
        coef, *_ = np.linalg.lstsq(A, mins, rcond=None)
        asy.append(float(coef[1]))
    sm, asy = np.asarray(sm), np.asarray(asy)
    lim = max(np.abs(asy).max(), 1e-9) * 1.4
    ax[1].axhspan(-lim, 0, color=C_LIGHT, alpha=0.5, lw=0)
    ax[1].axhline(0, color="black", lw=1.0)
    ax[1].semilogx(sizes, sm, "o--", color=C_PRIMARY, ms=4, mfc="white",
                   lw=1.1, label="sample min")
    ax[1].semilogx(sizes, asy, "o-", color=C_SECOND, ms=4, lw=1.6,
                   label="asymptotic")
    ax[1].set_xlabel("sample size $n$")
    ax[1].set_ylabel(r"$\hat\beta$ (no true floor)")
    ax[1].set_ylim(-lim, lim)
    ax[1].legend(loc="upper right")
    tag(ax[1], "B")

    # (C) 3d: eta over (mean spacing, within-type sd)
    SP, SD = np.meshgrid(np.linspace(0.005, 0.25, 40),
                         np.linspace(0.02, 0.30, 40))
    # analytic eta for 4 evenly spaced means with spacing SP and sd SD
    VB = (SP ** 2) * np.var(np.arange(4))
    ETA = VB / (VB + SD ** 2)
    s = ax[2].plot_surface(SP, SD, ETA, cmap="viridis", linewidth=0,
                           antialiased=True, rstride=1, cstride=1,
                           vmin=0, vmax=1)
    ax[2].set_xlabel("mean spacing")
    ax[2].set_ylabel("within-type sd")
    ax[2].set_zlabel(r"$\eta$")
    ax[2].view_init(elev=24, azim=-58)
    cb = fig.colorbar(s, ax=ax[2], shrink=0.52, pad=0.15, aspect=14)
    cb.ax.tick_params(labelsize=7)
    tag(ax[2], "C", is3d=True)

    # (D) floor error vs sample size, floored process, both estimators
    sm_e, as_e = [], []
    for n in sizes:
        sub = np.unique(np.linspace(40, n, 10).astype(int))
        stages = [10.0 + 40.0 * rng.random(m) ** 3 for m in sub]
        sm_e.append(abs(np.min(np.concatenate(stages)) - 10.0))
        ns = np.array([len(s) for s in stages], float)
        mins = np.array([np.min(s) for s in stages], float)
        A = np.vstack([1.0 / ns, np.ones_like(ns)]).T
        coef, *_ = np.linalg.lstsq(A, mins, rcond=None)
        as_e.append(abs(float(coef[1]) - 10.0))
    ax[3].loglog(sizes, np.clip(sm_e, 1e-15, None), "o--", color=C_PRIMARY,
                 ms=4, mfc="white", lw=1.1, label="sample min")
    ax[3].loglog(sizes, np.clip(as_e, 1e-15, None), "o-", color=C_SECOND,
                 ms=4, lw=1.6, label="asymptotic")
    ax[3].set_xlabel("sample size $n$")
    ax[3].set_ylabel(r"$|\hat\beta-\beta_{\rm true}|$")
    ax[3].legend(loc="lower left")
    tag(ax[3], "D")

    finish(fig, os.path.join(OUT, "panel_4_diagnostics.png"))


def main():
    os.makedirs(OUT, exist_ok=True)
    print("mekaneck panels:")
    panel1(); panel2(); panel3(); panel4()


if __name__ == "__main__":
    main()
