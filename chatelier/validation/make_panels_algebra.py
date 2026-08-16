"""
Four figure panels for: A Residual Algebra for Catalytic Composition.

Panel 1 -- The derived floor and its estimators
Panel 2 -- The telescoping obstruction
Panel 3 -- Type-averaged testing and law comparison
Panel 4 -- Composition geometry and convergence

Every chart plots computed numbers. No tables, no conceptual diagrams.
Each panel has four charts in a row, at least one of them 3d.
"""

from __future__ import annotations

import os
import numpy as np

from panel_style import (new_panel, tag, finish, SERIES,
                         C_PRIMARY, C_SECOND, C_THIRD, C_FOURTH, C_GREY, C_LIGHT)
from validate_algebra import (Regime, generate_cascades, kappa, compose_mult,
                              compose_add, compose_geo, compose_max,
                              type_averaged_kappas, separation_ratio,
                              floor_asymptotic, pearson, LAWS)

SEED = 20260816
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                   "docs", "catalyst-algebra", "figures")

REGIMES = [
    Regime("separated", {"A->B": 0.55, "B->C": 0.30, "C->A": 0.08, "A->C": 0.42},
           0.03, 10.0, 100.0),
    Regime("intermediate", {"A->B": 0.36, "B->C": 0.30, "C->A": 0.24, "A->C": 0.33},
           0.08, 10.0, 100.0),
    Regime("compressed", {"A->B": 0.300, "B->C": 0.302, "C->A": 0.299, "A->C": 0.301},
           0.12, 10.0, 100.0),
]


# ======================================================================
# Panel 1: the derived floor
# ======================================================================

def panel1():
    rng = np.random.default_rng(SEED)
    fig, ax = new_panel(projections=[None, None, None, "3d"], width=17.0)

    # (A) Estimator ERROR on the floored process, log scale. On a linear
    # axis both estimators look identical because both converge; the error
    # is where they differ. The sample minimum is bounded strictly ABOVE
    # the true floor (positive error at every n, Prop 4.8); the asymptotic
    # estimator straddles zero.
    sizes = np.unique(np.logspace(1.7, 3.6, 18).astype(int))
    sm_err, as_err = [], []
    for n in sizes:
        sub = np.unique(np.linspace(40, n, 10).astype(int))
        stages = [10.0 + 40.0 * rng.random(m) ** 3 for m in sub]
        sm_err.append(np.min(np.concatenate(stages)) - 10.0)
        as_err.append(abs(floor_asymptotic(stages) - 10.0))
    ax[0].loglog(sizes, np.clip(sm_err, 1e-14, None), "o--", color=C_PRIMARY,
                 ms=4, mfc="white", lw=1.1, label="sample min")
    ax[0].loglog(sizes, np.clip(as_err, 1e-14, None), "o-", color=C_SECOND,
                 ms=4, lw=1.6, label="asymptotic")
    ax[0].set_xlabel("sample size $n$")
    ax[0].set_ylabel(r"$|\hat\beta-\beta_{\rm true}|$")
    ax[0].legend(loc="upper right")
    tag(ax[0], "A")

    # (B) The falsifiability point: signed estimate on an UNFLOORED process.
    # The sample minimum is strictly positive at every n (it cannot be
    # otherwise); the asymptotic estimator takes negative values, which is
    # the only way a positivity claim can be contradicted by data.
    sizes_b = np.unique(np.logspace(1.7, 3.6, 22).astype(int))
    sm_u, as_u = [], []
    for n in sizes_b:
        sub = np.unique(np.linspace(40, n, 10).astype(int))
        stages = [40.0 * rng.random(m) ** 3 for m in sub]
        sm_u.append(np.min(np.concatenate(stages)))
        as_u.append(floor_asymptotic(stages))
    sm_u, as_u = np.asarray(sm_u), np.asarray(as_u)
    scale = max(np.abs(as_u).max(), 1e-12) * 1.35
    ax[1].axhspan(-scale, 0, color=C_LIGHT, alpha=0.5, lw=0)
    ax[1].axhline(0.0, color="black", lw=1.0)
    ax[1].semilogx(sizes_b, sm_u, "o--", color=C_PRIMARY, ms=4, mfc="white",
                   lw=1.1, label="sample min")
    ax[1].semilogx(sizes_b, as_u, "o-", color=C_SECOND, ms=4, lw=1.6,
                   label="asymptotic")
    ax[1].set_xlabel("sample size $n$")
    ax[1].set_ylabel(r"$\hat\beta$  (no true floor)")
    ax[1].set_ylim(-scale, scale)
    ax[1].legend(loc="upper right")
    tag(ax[1], "B")

    # (C) floor misestimation inflates kappa (Prop 4.8). Domain restricted
    # so no curve passes through its pole.
    for sb, col, lab in ((70.0, C_PRIMARY, r"$S_b=70$"),
                         (30.0, C_FOURTH, r"$S_b=30$"),
                         (15.0, C_SECOND, r"$S_b=15$")):
        gap = sb - 10.0
        eps = np.linspace(-4, 0.75 * gap, 300)
        ax[2].plot(eps, 0.4 * gap / (gap - eps), color=col, label=lab)
    ax[2].axhline(0.4, color=C_GREY, ls="--", lw=0.9)
    ax[2].axvline(0.0, color=C_GREY, ls=":", lw=0.9)
    ax[2].set_xlabel(r"floor error $\varepsilon$")
    ax[2].set_ylabel(r"observed $\kappa$  (true $0.4$)")
    ax[2].set_xlim(-4, 12)
    ax[2].set_ylim(0.2, 1.05)
    ax[2].legend(loc="upper left")
    tag(ax[2], "C")

    # (D) 3d: relative error in kappa over (floor error, gap).
    E, G = np.meshgrid(np.linspace(-4, 10, 60), np.linspace(12, 90, 60))
    Z = E / (G - E)                      # gap > eps everywhere on this domain
    s = ax[3].plot_surface(E, G, Z, cmap="RdBu_r", linewidth=0,
                           antialiased=True, rstride=1, cstride=1,
                           vmin=-0.5, vmax=0.5)
    ax[3].set_xlabel(r"$\varepsilon$")
    ax[3].set_ylabel(r"gap $S_b-\beta$")
    ax[3].set_zlabel(r"rel. error in $\kappa$")
    ax[3].set_zlim(-0.5, 1.0)
    ax[3].view_init(elev=22, azim=-56)
    cb = fig.colorbar(s, ax=ax[3], shrink=0.52, pad=0.12, aspect=14)
    cb.ax.tick_params(labelsize=7)
    tag(ax[3], "D", is3d=True)

    finish(fig, os.path.join(OUT, "panel_1_floor.png"))


# ======================================================================
# Panel 2: the telescoping obstruction
# ======================================================================

def panel2():
    rng = np.random.default_rng(SEED)
    fig, ax = new_panel(projections=[None, None, "3d", None])

    cascades = generate_cascades(REGIMES[0], 1500, (3, 5), rng)
    floor = REGIMES[0].floor

    inst_pred, meas, lens = [], [], []
    for c in cascades:
        st = c["states"]
        ks = [kappa(st[i], st[i + 1], floor) for i in range(len(st) - 1)]
        inst_pred.append(compose_mult(ks))
        meas.append((st[0] - st[-1]) / (st[0] - floor))
        lens.append(len(ks))
    inst_pred, meas, lens = map(np.asarray, (inst_pred, meas, lens))

    kbar, per_type = type_averaged_kappas(cascades, floor)
    ta_pred = np.array([compose_mult([kbar[t] for t in c["types"]]) for c in cascades])

    # (A) instance-specific: exact identity, all mass on the diagonal
    ax[0].plot([0, 1], [0, 1], color=C_GREY, lw=1.0, ls="--")
    ax[0].scatter(meas, inst_pred, s=7, color=C_PRIMARY, alpha=0.5,
                  edgecolors="none")
    ax[0].set_xlabel("measured net $\\kappa$")
    ax[0].set_ylabel("instance-specific pred.")
    ax[0].set_xlim(0, 1); ax[0].set_ylim(0, 1)
    tag(ax[0], "A")

    # (B) same axes, type-averaged: real scatter
    ax[1].plot([0, 1], [0, 1], color=C_GREY, lw=1.0, ls="--")
    ax[1].scatter(meas, ta_pred, s=7, color=C_SECOND, alpha=0.5,
                  edgecolors="none")
    ax[1].set_xlabel("measured net $\\kappa$")
    ax[1].set_ylabel("type-averaged pred.")
    ax[1].set_xlim(0, 1); ax[1].set_ylim(0, 1)
    tag(ax[1], "B")

    # (C) 3d: residual deviation vs measured, by cascade length
    dev_inst = np.abs(inst_pred - meas)
    dev_ta = np.abs(ta_pred - meas)
    for L, col in zip((3, 4, 5), SERIES):
        m = lens == L
        ax[2].scatter(meas[m], np.full(m.sum(), L), dev_inst[m],
                      s=5, color=C_LIGHT, alpha=0.55, edgecolors="none")
        ax[2].scatter(meas[m], np.full(m.sum(), L), dev_ta[m],
                      s=6, color=col, alpha=0.65, edgecolors="none")
    ax[2].set_xlabel("measured $\\kappa$")
    ax[2].set_ylabel("length")
    ax[2].set_zlabel("|deviation|")
    ax[2].set_yticks([3, 4, 5])
    ax[2].view_init(elev=20, azim=-62)
    tag(ax[2], "C", is3d=True)

    # (D) deviation magnitude: log scale, machine-eps vs real
    bins = np.logspace(-17, 0, 45)
    ax[3].hist(np.clip(dev_inst, 1e-17, None), bins=bins, color=C_PRIMARY,
               alpha=0.85, label="instance")
    ax[3].hist(np.clip(dev_ta, 1e-17, None), bins=bins, color=C_SECOND,
               alpha=0.75, label="type-avg")
    ax[3].set_xscale("log")
    ax[3].set_xlabel("|prediction $-$ measurement|")
    ax[3].set_ylabel("count")
    ax[3].legend(loc="upper left")
    tag(ax[3], "D")

    finish(fig, os.path.join(OUT, "panel_2_telescoping.png"))


# ======================================================================
# Panel 3: type separation and law comparison
# ======================================================================

def panel3():
    rng = np.random.default_rng(SEED)
    fig, ax = new_panel(projections=[None, None, "3d", None])

    data = {}
    for reg in REGIMES:
        cs = generate_cascades(reg, 3000, (3, 5), rng)
        kbar, per_type = type_averaged_kappas(cs, reg.floor)
        eta = separation_ratio(per_type)
        meas = np.array([(c["states"][0] - c["states"][-1]) /
                         (c["states"][0] - reg.floor) for c in cs])
        preds = {n: np.array([f([kbar[t] for t in c["types"]]) for c in cs])
                 for n, f in LAWS.items()}
        data[reg.name] = dict(eta=eta, meas=meas, preds=preds,
                              per_type=per_type, kbar=kbar)

    # (A) within-type kappa distributions: separated (blue) vs compressed
    # (red). Separated type means are spread; compressed ones collapse onto
    # a common value while the within-type spread grows.
    for i, (name, col) in enumerate((("separated", C_PRIMARY),
                                     ("compressed", C_SECOND))):
        pt = data[name]["per_type"]
        for j, (t, vals) in enumerate(sorted(pt.items())):
            pos = j + (i - 0.5) * 0.34
            vp = ax[0].violinplot([vals], positions=[pos], widths=0.30,
                                  showextrema=False, showmedians=True)
            for body in vp["bodies"]:
                body.set_facecolor(col)
                body.set_edgecolor(col)
                body.set_alpha(0.55)
            vp["cmedians"].set_color(col)
            vp["cmedians"].set_linewidth(1.4)
    ax[0].set_xticks(range(4))
    ax[0].set_xticklabels(sorted(data["separated"]["per_type"]), rotation=30)
    ax[0].set_ylabel(r"$\kappa$ by event type")
    tag(ax[0], "A")

    # (B) r by law across eta
    etas = [data[r.name]["eta"] for r in REGIMES]
    for (law, col) in zip(LAWS, SERIES):
        rs = [pearson(data[r.name]["preds"][law], data[r.name]["meas"])
              for r in REGIMES]
        ax[1].plot(etas, rs, "o-", color=col, ms=5, label=law[:9])
    ax[1].set_xscale("log")
    ax[1].set_xlabel(r"type separation $\eta$")
    ax[1].set_ylabel(r"Pearson $r$")
    ax[1].legend(loc="lower right")
    tag(ax[1], "B")

    # (C) 3d: prediction surface vs measurement across regimes
    for k, (reg, col) in enumerate(zip(REGIMES, SERIES)):
        d = data[reg.name]
        m, p = d["meas"], d["preds"]["multiplicative"]
        idx = rng.choice(len(m), 700, replace=False)
        ax[2].scatter(m[idx], np.full(700, k), p[idx], s=5, color=col,
                      alpha=0.55, edgecolors="none")
        line = np.linspace(m.min(), m.max(), 20)
        ax[2].plot(line, np.full(20, k), line, color="black", lw=0.9, alpha=0.7)
    ax[2].set_xlabel("measured")
    ax[2].set_ylabel("regime")
    ax[2].set_zlabel("predicted")
    ax[2].set_yticks([0, 1, 2])
    ax[2].set_yticklabels(["sep", "int", "cmp"], fontsize=7)
    ax[2].view_init(elev=18, azim=-66)
    tag(ax[2], "C", is3d=True)

    # (D) RMSE by law and regime
    w = 0.2
    xs = np.arange(3)
    for i, (law, col) in enumerate(zip(LAWS, SERIES)):
        vals = [float(np.sqrt(np.mean((data[r.name]["preds"][law] -
                                       data[r.name]["meas"]) ** 2)))
                for r in REGIMES]
        ax[3].bar(xs + (i - 1.5) * w, vals, w, color=col, label=law[:9])
    ax[3].set_xticks(xs)
    ax[3].set_xticklabels(["sep", "int", "cmp"])
    ax[3].set_ylabel("RMSE")
    ax[3].legend(loc="upper left", ncol=2)
    tag(ax[3], "D")

    finish(fig, os.path.join(OUT, "panel_3_separation.png"))


# ======================================================================
# Panel 4: composition geometry and convergence
# ======================================================================

def panel4():
    fig, ax = new_panel(projections=[None, "3d", None, None])

    # (A) the four laws as functions of n at fixed kappa
    ns = np.arange(1, 13)
    kfix = 0.3
    ax[0].plot(ns, 1 - (1 - kfix) ** ns, "o-", color=C_PRIMARY, ms=4,
               label="mult")
    ax[0].plot(ns, np.minimum(kfix * ns, 1), "s-", color=C_SECOND, ms=4,
               label="add")
    # At constant kappa the geometric-mean law reduces to kappa itself and so
    # coincides exactly with the maximum law; dash it so both remain visible.
    ax[0].plot(ns, 1 - ((1 - kfix) ** ns) ** (1 / ns), "^--", color=C_THIRD,
               ms=5, lw=2.2, label="geo")
    ax[0].plot(ns, np.full_like(ns, kfix, dtype=float), "d-", color=C_FOURTH,
               ms=4, lw=1.0, label="max")
    ax[0].set_xlabel("cascade length $n$")
    ax[0].set_ylabel(r"net $\kappa$")
    ax[0].legend(loc="lower right", ncol=2)
    tag(ax[0], "A")

    # (B) 3d: composition surface for two catalysts
    K1, K2 = np.meshgrid(np.linspace(0, 0.95, 60), np.linspace(0, 0.95, 60))
    NET = 1 - (1 - K1) * (1 - K2)
    s = ax[1].plot_surface(K1, K2, NET, cmap="viridis", linewidth=0,
                           antialiased=True, alpha=0.95, rstride=1, cstride=1)
    ax[1].contour(K1, K2, NET, levels=8, colors="white", linewidths=0.4,
                  offset=None)
    ax[1].set_xlabel(r"$\kappa_1$")
    ax[1].set_ylabel(r"$\kappa_2$")
    ax[1].set_zlabel(r"$\kappa_1\diamond\kappa_2$")
    ax[1].view_init(elev=26, azim=-52)
    fig.colorbar(s, ax=ax[1], shrink=0.55, pad=0.10)
    tag(ax[1], "B", is3d=True)

    # (C) convergence: summable vs divergent residual fraction
    stages = np.unique(np.logspace(0, 6, 60).astype(int))
    summable = []
    divergent = []
    for n in stages:
        ks = np.array([2.0 ** -(i + 1) for i in range(min(n, 2000))])
        summable.append(np.exp(np.sum(np.log1p(-ks))))
        divergent.append(1.0 / (n + 1))
    ax[2].loglog(stages, summable, color=C_PRIMARY, label=r"$\sum\kappa<\infty$")
    ax[2].loglog(stages, divergent, color=C_SECOND, label=r"$\sum\kappa=\infty$")
    ax[2].set_xlabel("$n$")
    ax[2].set_ylabel("residual gap fraction")
    ax[2].legend(loc="lower left")
    tag(ax[2], "C")

    # (D) marginal contribution decays geometrically (Prop 4.5)
    ns = np.arange(1, 16)
    for kv, col in ((0.5, C_PRIMARY), (0.3, C_SECOND), (0.15, C_THIRD)):
        marg = kv * (1 - kv) ** (ns - 1)
        ax[3].semilogy(ns, marg, "o-", color=col, ms=4,
                       label=rf"$\kappa={kv}$")
    ax[3].set_xlabel("event index")
    ax[3].set_ylabel("marginal gain")
    ax[3].legend(loc="upper right")
    tag(ax[3], "D")

    finish(fig, os.path.join(OUT, "panel_4_composition.png"))


def main():
    os.makedirs(OUT, exist_ok=True)
    print("algebra panels:")
    panel1(); panel2(); panel3(); panel4()


if __name__ == "__main__":
    main()
