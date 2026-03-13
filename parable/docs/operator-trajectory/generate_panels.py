"""
Generate 6 panel figures for the Operator Trajectory paper.
Each panel: 1 row x 4 columns, figsize=(20,5), DPI=200, light style.
"""

import matplotlib
matplotlib.use("Agg")
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
from matplotlib.colors import Normalize
from matplotlib import cm
import os
import gc

# ---------------------------------------------------------------------------
# STYLE
# ---------------------------------------------------------------------------
plt.rcParams["font.family"] = "monospace"
plt.rcParams["font.size"] = 8
plt.rcParams["axes.labelsize"] = 9
plt.rcParams["axes.titlesize"] = 10
plt.rcParams["figure.facecolor"] = "#ffffff"
plt.rcParams["axes.facecolor"] = "#ffffff"
plt.rcParams["axes.edgecolor"] = "#cccccc"
plt.rcParams["axes.grid"] = True
plt.rcParams["grid.alpha"] = 0.4
plt.rcParams["grid.color"] = "#cccccc"
plt.rcParams["text.color"] = "#1a1a1a"
plt.rcParams["axes.labelcolor"] = "#1a1a1a"
plt.rcParams["xtick.color"] = "#333333"
plt.rcParams["ytick.color"] = "#333333"

COLORS = {
    "primary": "#1f77b4",
    "secondary": "#d62728",
    "tertiary": "#2ca02c",
    "quaternary": "#ff7f0e",
    "accent1": "#9467bd",
    "accent2": "#17becf",
}

OUT = os.path.join(os.path.dirname(__file__), "figures")
os.makedirs(OUT, exist_ok=True)

np.random.seed(42)

# ---------------------------------------------------------------------------
# VALIDATION DATA
# ---------------------------------------------------------------------------
PARTITION_CAP = {1: 2, 2: 8, 3: 18, 4: 32, 5: 50, 6: 72, 7: 98}

REGIME_BOUNDS = [
    ("turbulent", 0.0, 0.301),
    ("aperture_dominated", 0.301, 0.501),
    ("cascade", 0.501, 0.800),
    ("coherent", 0.800, 0.950),
    ("phase_locked", 0.950, 1.0),
]

REGIME_COUNTS = {
    "turbulent": 301,
    "aperture_dominated": 200,
    "cascade": 299,
    "coherent": 150,
    "phase_locked": 51,
}

SYNC_ONSET = [
    (0.5, 0.318, 0.105, 0.108, 0.114),
    (1.0, 0.637, 0.068, 0.070, 0.075),
    (2.0, 1.273, 0.107, 0.110, 0.115),
    (4.0, 2.547, 0.066, 0.068, 0.071),
    (8.0, 5.093, 0.073, 0.077, 0.083),
]


# ===================================================================
# PANEL 1 — Partition Coordinate Space
# ===================================================================
def panel1():
    fig = plt.figure(figsize=(20, 5), facecolor="#ffffff")

    # 1a — 3D scatter of partition states (n,l,m) for n=1..5
    ax = fig.add_subplot(1, 4, 1, projection="3d")
    clist = [COLORS["primary"], COLORS["secondary"], COLORS["tertiary"],
             COLORS["quaternary"], COLORS["accent1"]]
    for n in range(1, 6):
        for ell in range(n):
            for m in range(-ell, ell + 1):
                for _ in range(2):  # s = ±1/2
                    ax.scatter(n, ell, m, c=clist[n - 1],
                               s=(abs(m) + 1) * 18, alpha=0.7, edgecolors="none")
    ax.set_xlabel("n")
    ax.set_ylabel("l")
    ax.set_zlabel("m")
    ax.set_title("Partition States")
    ax.set_facecolor("#0a0a0a")

    # 1b — Bar chart C(n)=2n^2
    ax2 = fig.add_subplot(1, 4, 2)
    ns = np.arange(1, 11)
    caps = 2 * ns ** 2
    colors_bar = [COLORS["primary"] if n <= 7 else COLORS["accent1"] for n in ns]
    ax2.bar(ns, caps, color=colors_bar, edgecolor="#999999", width=0.6)
    n_cont = np.linspace(1, 10, 200)
    ax2.plot(n_cont, 2 * n_cont ** 2, color=COLORS["secondary"], lw=1.5, ls="--")
    for n_v in range(1, 8):
        ax2.plot(n_v, 2 * n_v ** 2, "o", color=COLORS["quaternary"], ms=5, zorder=5)
    ax2.set_xlabel("n")
    ax2.set_ylabel("C(n)")
    ax2.set_title("Partition Capacity")

    # 1c — 3D surface: M(K_levels, k_branching)
    ax3 = fig.add_subplot(1, 4, 3, projection="3d")
    K_arr = np.arange(1, 11)
    k_arr = np.arange(2, 11)
    K_g, k_g = np.meshgrid(K_arr, k_arr)
    M_val = K_g * np.log(k_g) / np.log(3)
    ax3.plot_surface(K_g, k_g, M_val, cmap="viridis", alpha=0.85, edgecolor="none")
    ax3.set_xlabel("K")
    ax3.set_ylabel("k")
    ax3.set_zlabel("M")
    ax3.set_title("Partition Depth")
    ax3.set_facecolor("#0a0a0a")

    # 1d — Heatmap: state density (l, m) for n=5
    ax4 = fig.add_subplot(1, 4, 4)
    n = 5
    ell_max = n - 1  # 0..4
    m_range = np.arange(-(n - 1), n)  # -4..4
    grid = np.zeros((ell_max + 1, len(m_range)))
    for ell in range(n):
        for m in range(-ell, ell + 1):
            mi = m - m_range[0]
            grid[ell, mi] = 2  # 2 spin states
    im = ax4.imshow(grid, cmap="YlOrRd", aspect="auto",
                    extent=[m_range[0] - 0.5, m_range[-1] + 0.5, ell_max + 0.5, -0.5])
    ax4.set_xlabel("m")
    ax4.set_ylabel("l")
    ax4.set_title("State Density n=5")
    plt.colorbar(im, ax=ax4, label="degeneracy")

    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "panel1_partition_coordinate_space.png"), dpi=200,
                facecolor="#ffffff", bbox_inches="tight")
    plt.close(fig)
    gc.collect()
    print("Panel 1 saved.")


# ===================================================================
# PANEL 2 — S-Entropy Coordinate Space
# ===================================================================
def panel2():
    fig = plt.figure(figsize=(20, 5), facecolor="#ffffff")

    # 2a — 3D scatter 1000 random points
    ax = fig.add_subplot(1, 4, 1, projection="3d")
    pts = np.random.rand(1000, 3)
    mag = np.linalg.norm(pts, axis=1)
    sc = ax.scatter(pts[:, 0], pts[:, 1], pts[:, 2], c=mag, cmap="plasma",
                    s=8, alpha=0.3, edgecolors="none")
    ax.set_xlabel("S_k")
    ax.set_ylabel("S_t")
    ax.set_zlabel("S_e")
    ax.set_title("S-Entropy Space")
    ax.set_facecolor("#0a0a0a")

    # 2b — 3D trajectory
    ax2 = fig.add_subplot(1, 4, 2, projection="3d")
    t = np.linspace(0, 1, 300)
    start = np.array([0.8, 0.2, 0.9])
    end = np.array([0.3, 0.5, 0.4])
    traj = start[None, :] + t[:, None] * (end - start)[None, :]
    # add curvature
    traj[:, 0] += 0.15 * np.sin(np.pi * t)
    traj[:, 1] += 0.10 * np.sin(2 * np.pi * t)
    traj[:, 2] += -0.08 * np.sin(1.5 * np.pi * t)
    ax2.scatter(*traj.T, c=t, cmap="viridis", s=6, edgecolors="none")
    ax2.plot(*traj[0], "o", color=COLORS["secondary"], ms=8)
    ax2.plot(*traj[-1], "*", color=COLORS["quaternary"], ms=12)
    ax2.set_xlabel("S_k")
    ax2.set_ylabel("S_t")
    ax2.set_zlabel("S_e")
    ax2.set_title("Therapeutic Trajectory")
    ax2.set_facecolor("#0a0a0a")

    # 2c — Heatmap: distance matrix
    ax3 = fig.add_subplot(1, 4, 3)
    sample = np.random.rand(20, 3)
    D = np.sqrt(((sample[:, None, :] - sample[None, :, :]) ** 2).sum(axis=2))
    im = ax3.imshow(D, cmap="viridis", aspect="equal")
    ax3.set_xlabel("Point j")
    ax3.set_ylabel("Point i")
    ax3.set_title("Distance Matrix")
    plt.colorbar(im, ax=ax3, label="d(S_i,S_j)")

    # 2d — Contour: T(S_k, S_e)
    ax4 = fig.add_subplot(1, 4, 4)
    sk = np.linspace(0, 1, 200)
    se = np.linspace(0, 1, 200)
    SK, SE = np.meshgrid(sk, se)
    T0 = 310.0
    T = T0 * np.exp(SE - 0.5)
    cs = ax4.contourf(SK, SE, T, levels=30, cmap="coolwarm")
    ax4.contour(SK, SE, T, levels=10, colors="#333333", linewidths=0.4, alpha=0.5)
    ax4.set_xlabel("S_k")
    ax4.set_ylabel("S_e")
    ax4.set_title("Temperature T(S_k,S_e)")
    plt.colorbar(cs, ax=ax4, label="T (K)")

    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "panel2_s_entropy_coordinate_space.png"), dpi=200,
                facecolor="#ffffff", bbox_inches="tight")
    plt.close(fig)
    gc.collect()
    print("Panel 2 saved.")


# ===================================================================
# PANEL 3 — Trajectory-Terminus-Memory Triples
# ===================================================================
def panel3():
    fig = plt.figure(figsize=(20, 5), facecolor="#ffffff")

    terminus = np.array([0.4, 0.5, 0.35])
    t = np.linspace(0, 1, 400)

    # trajectory 1
    s1 = np.array([0.1, 0.9, 0.8])
    g1 = s1[None, :] + t[:, None] * (terminus - s1)[None, :]
    g1[:, 0] += 0.2 * np.sin(2 * np.pi * t)
    g1[:, 1] += -0.15 * np.sin(3 * np.pi * t)

    # trajectory 2
    s2 = np.array([0.9, 0.1, 0.7])
    g2 = s2[None, :] + t[:, None] * (terminus - s2)[None, :]
    g2[:, 0] += -0.25 * np.sin(np.pi * t)
    g2[:, 2] += 0.18 * np.sin(2.5 * np.pi * t)

    # 3a — 3D two trajectories converging
    ax = fig.add_subplot(1, 4, 1, projection="3d")
    ax.plot(*g1.T, color=COLORS["primary"], lw=1.5, alpha=0.8)
    ax.plot(*g2.T, color=COLORS["secondary"], lw=1.5, alpha=0.8)
    ax.plot(*terminus, "*", color=COLORS["quaternary"], ms=14, zorder=5)
    ax.set_xlabel("S_k")
    ax.set_ylabel("S_t")
    ax.set_zlabel("S_e")
    ax.set_title("Converging Trajectories")
    ax.set_facecolor("#0a0a0a")

    # 3b — Accumulated memory M(t)
    ax2 = fig.add_subplot(1, 4, 2)
    dg1 = np.diff(g1, axis=0)
    dg2 = np.diff(g2, axis=0)
    dH1 = np.linalg.norm(dg1, axis=1)
    dH2 = np.linalg.norm(dg2, axis=1)
    M1 = np.concatenate([[0], np.cumsum(dH1)])
    M2 = np.concatenate([[0], np.cumsum(dH2)])
    ax2.plot(t, M1, color=COLORS["primary"], lw=1.5, label=r"$\gamma_1$")
    ax2.plot(t, M2, color=COLORS["secondary"], lw=1.5, label=r"$\gamma_2$")
    ax2.axhline(M1[-1], color=COLORS["primary"], ls=":", alpha=0.5)
    ax2.axhline(M2[-1], color=COLORS["secondary"], ls=":", alpha=0.5)
    ax2.set_xlabel("t")
    ax2.set_ylabel("M(t)")
    ax2.set_title("Accumulated Memory")
    ax2.legend(fontsize=7)

    # 3c — Scatter: endpoints colored by M
    ax3 = fig.add_subplot(1, 4, 3)
    endpoints_sk = np.random.rand(50) * 0.3 + 0.25
    endpoints_se = np.random.rand(50) * 0.3 + 0.2
    mem_vals = np.random.rand(50) * 1.5 + 0.5
    sc = ax3.scatter(endpoints_sk, endpoints_se, c=mem_vals, cmap="viridis", s=40,
                     edgecolors="#999999", linewidths=0.3)
    ax3.set_xlabel("S_k")
    ax3.set_ylabel("S_e")
    ax3.set_title("Endpoint Memory")
    plt.colorbar(sc, ax=ax3, label="M")

    # 3d — 3D surface: Poincaré near-return ||γ(t)-γ(0)||
    ax4 = fig.add_subplot(1, 4, 4)
    tt = np.linspace(0, 50, 5000)
    traj_x = 0.5 + 0.3 * np.sin(tt) + 0.01 * tt * np.cos(0.3 * tt)
    traj_y = 0.5 + 0.3 * np.cos(tt * 1.1) + 0.008 * tt * np.sin(0.2 * tt)
    traj_z = 0.5 + 0.2 * np.sin(tt * 0.7) + 0.005 * tt
    origin = np.array([traj_x[0], traj_y[0], traj_z[0]])
    dist = np.sqrt((traj_x - origin[0]) ** 2 + (traj_y - origin[1]) ** 2 +
                   (traj_z - origin[2]) ** 2)
    ax4.plot(tt, dist, color=COLORS["tertiary"], lw=0.6, alpha=0.8)
    ax4.set_xlabel("t")
    ax4.set_ylabel(r"$||\gamma(t)-\gamma(0)||$")
    ax4.set_title(u"Poincar\u00e9 Return")

    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "panel3_trajectory_terminus_memory.png"), dpi=200,
                facecolor="#ffffff", bbox_inches="tight")
    plt.close(fig)
    gc.collect()
    print("Panel 3 saved.")


# ===================================================================
# PANEL 4 — Operator Composition and Drug Action
# ===================================================================
def panel4():
    fig = plt.figure(figsize=(20, 5), facecolor="#ffffff")

    # Build the R(t) trajectory: 200 steps, drug at step 100
    steps = np.arange(201)
    R = np.zeros(201)
    # Pre-drug: low R with noise
    R[:100] = 0.135 + 0.06 * np.random.randn(100)
    R[:100] = np.clip(R[:100], 0.01, 0.30)
    # Transition
    R[100] = 0.5
    # Post-drug: ramp to high R
    for i in range(101, 201):
        R[i] = R[i - 1] + (0.999 - R[i - 1]) * 0.08 + 0.005 * np.random.randn()
    R = np.clip(R, 0, 1)
    R[0] = 0.135
    R[-1] = 0.999

    # Variance proxy
    var = 0.02 / (R + 0.01) + 0.001 * np.random.rand(201)

    # Regime classification
    def classify(r):
        for name, lo, hi in REGIME_BOUNDS:
            if r < hi or name == "phase_locked":
                return name
        return "phase_locked"

    regimes = [classify(r) for r in R]
    regime_colors = {
        "turbulent": COLORS["secondary"],
        "aperture_dominated": COLORS["quaternary"],
        "cascade": COLORS["tertiary"],
        "coherent": COLORS["accent2"],
        "phase_locked": COLORS["primary"],
    }

    # 4a — 3D trajectory (step, R, variance) colored by regime
    ax = fig.add_subplot(1, 4, 1, projection="3d")
    for i in range(len(steps) - 1):
        ax.plot(steps[i:i + 2], R[i:i + 2], var[i:i + 2],
                color=regime_colors[regimes[i]], lw=1.2)
    ax.scatter([100], [R[100]], [var[100]], color=COLORS["secondary"], s=60,
               marker="^", zorder=5)
    ax.set_xlabel("step")
    ax.set_ylabel("R")
    ax.set_zlabel("var")
    ax.set_title("Operator Trajectory 3D")
    ax.set_facecolor("#0a0a0a")

    # 4b — R(t) with regime background
    ax2 = fig.add_subplot(1, 4, 2)
    for i in range(len(steps) - 1):
        ax2.axvspan(steps[i], steps[i + 1], color=regime_colors[regimes[i]], alpha=0.15)
    ax2.plot(steps, R, color=COLORS["primary"], lw=1.2)
    ax2.axvline(100, color=COLORS["secondary"], ls="--", lw=1, alpha=0.8)
    ax2.set_xlabel("step")
    ax2.set_ylabel("R(t)")
    ax2.set_title("Order Parameter R(t)")

    # 4c — Heatmap: R_post(R_pre, delta_S)
    ax3 = fig.add_subplot(1, 4, 3)
    rp = np.linspace(0.1, 0.9, 40)
    ds = np.linspace(-0.5, 0.5, 40)
    RP, DS = np.meshgrid(rp, ds)
    R_post = np.clip(RP + DS * (1 - RP), 0, 1)
    im = ax3.imshow(R_post, cmap="viridis", aspect="auto",
                    extent=[ds[0], ds[-1], rp[-1], rp[0]])
    ax3.set_xlabel(r"$\Delta S$")
    ax3.set_ylabel(r"$R_{pre}$")
    ax3.set_title(r"$R_{post}$ Structural Factor")
    plt.colorbar(im, ax=ax3, label=r"$R_{post}$")

    # 4d — Bar: regime distribution
    ax4 = fig.add_subplot(1, 4, 4)
    names = list(REGIME_COUNTS.keys())
    counts = [REGIME_COUNTS[n] for n in names]
    short = ["turb", "aper", "casc", "coh", "p_lock"]
    bars = ax4.bar(short, counts, color=[regime_colors[n] for n in names],
                   edgecolor="#999999", width=0.6)
    ax4.set_ylabel("count")
    ax4.set_title("Regime Distribution")

    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "panel4_operator_composition_drug.png"), dpi=200,
                facecolor="#ffffff", bbox_inches="tight")
    plt.close(fig)
    gc.collect()
    print("Panel 4 saved.")


# ===================================================================
# PANEL 5 — Synchronization Onset and Critical Coupling
# ===================================================================
def panel5():
    fig = plt.figure(figsize=(20, 5), facecolor="#ffffff")

    # Quick Kuramoto for the surface
    def kuramoto_R(K, sigma, N=100, dt=0.01, T=10.0):
        omega = np.random.randn(N) * sigma
        theta = np.random.uniform(0, 2 * np.pi, N)
        steps = int(T / dt)
        for _ in range(steps):
            z = np.exp(1j * theta)
            r_complex = z.mean()
            R_val = np.abs(r_complex)
            psi = np.angle(r_complex)
            theta += dt * (omega + K * R_val * np.sin(psi - theta))
        z = np.exp(1j * theta)
        return np.abs(z.mean())

    # 5a — 3D surface R(K, sigma)
    ax = fig.add_subplot(1, 4, 1, projection="3d")
    K_vals = np.linspace(0, 10, 20)
    sig_vals = np.array([0.5, 1, 2, 4, 8])
    KK, SS = np.meshgrid(K_vals, sig_vals)
    RR = np.zeros_like(KK)
    for i in range(len(sig_vals)):
        for j in range(len(K_vals)):
            RR[i, j] = kuramoto_R(KK[i, j], SS[i, j], N=50, dt=0.02, T=5.0)
    ax.plot_surface(KK, SS, RR, cmap="viridis", alpha=0.85, edgecolor="none")
    ax.set_xlabel("K")
    ax.set_ylabel(r"$\sigma_\omega$")
    ax.set_zlabel("R")
    ax.set_title("Sync Surface R(K,σ)")
    ax.set_facecolor("#0a0a0a")

    # 5b — Grouped bar: R_below, R_at, R_above for each freq_std
    ax2 = fig.add_subplot(1, 4, 2)
    x = np.arange(len(SYNC_ONSET))
    w = 0.22
    for idx, (label, col) in enumerate(zip(
            ["R_below", "R_at", "R_above"],
            [COLORS["primary"], COLORS["tertiary"], COLORS["secondary"]])):
        vals = [row[2 + idx] for row in SYNC_ONSET]
        ax2.bar(x + idx * w, vals, w, color=col, label=label, edgecolor="#999999")
    ax2.set_xticks(x + w)
    ax2.set_xticklabels([f"{row[0]}" for row in SYNC_ONSET], fontsize=7)
    ax2.set_xlabel(r"$\sigma_\omega$")
    ax2.set_ylabel("R")
    ax2.set_title("Sync Onset by Condition")
    ax2.legend(fontsize=6)

    # 5c — Scatter: K_c vs freq_std
    ax3 = fig.add_subplot(1, 4, 3)
    sigmas = [row[0] for row in SYNC_ONSET]
    Kcs = [row[1] for row in SYNC_ONSET]
    ax3.scatter(sigmas, Kcs, color=COLORS["primary"], s=60, zorder=5,
                edgecolors=COLORS["quaternary"], linewidths=0.8)
    sig_line = np.linspace(0, 10, 200)
    ax3.plot(sig_line, 2 * sig_line / np.pi, color=COLORS["secondary"], lw=1.5,
             ls="--", label=r"$K_c=2\sigma/\pi$")
    for s, k in zip(sigmas, Kcs):
        ax3.axvline(s, color="#bbbbbb", lw=0.4, alpha=0.5)
    ax3.set_xlabel(r"$\sigma_\omega$")
    ax3.set_ylabel(r"$K_c$")
    ax3.set_title("Critical Coupling")
    ax3.legend(fontsize=7)

    # 5d — Log-log: sigma^2_min vs K
    ax4 = fig.add_subplot(1, 4, 4)
    K_range = np.logspace(-1, 2, 200)
    sigma2_min_at_K1 = 4.28e-21
    sigma2 = sigma2_min_at_K1 / K_range  # slope = -1 on log-log
    ax4.loglog(K_range, sigma2, color=COLORS["primary"], lw=1.5)
    kBT = 1.38e-23 * 310  # k_B * T
    ax4.axhline(kBT, color=COLORS["quaternary"], ls="--", lw=1, alpha=0.7, label=r"$k_BT$")
    ax4.set_xlabel("K")
    ax4.set_ylabel(r"$\sigma^2_{min}$")
    ax4.set_title(r"Variance Floor (slope$=-1$)")
    ax4.legend(fontsize=7)

    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "panel5_synchronization_onset.png"), dpi=200,
                facecolor="#ffffff", bbox_inches="tight")
    plt.close(fig)
    gc.collect()
    print("Panel 5 saved.")


# ===================================================================
# PANEL 6 — Frequency Hierarchy and Consciousness
# ===================================================================
def panel6():
    fig = plt.figure(figsize=(20, 5), facecolor="#ffffff")

    # 6a — 3D surface: gear cascade frequencies
    ax = fig.add_subplot(1, 4, 1, projection="3d")
    levels = np.arange(1, 9)
    f_ins = np.array([1e13, 1e10, 1e6])
    ratios = np.array([1, 1e-1, 1e-3, 1e-5, 1e-7, 1e-10, 1e-13, 1e-15])
    LL, FF = np.meshgrid(levels, np.log10(f_ins))
    ZZ = np.zeros_like(LL, dtype=float)
    for i, f0 in enumerate(f_ins):
        for j, r in enumerate(ratios):
            ZZ[i, j] = np.log10(f0 * r + 1e-30)
    ax.plot_surface(LL, FF, ZZ, cmap="viridis", alpha=0.85, edgecolor="none")
    ax.set_xlabel("Level")
    ax.set_ylabel("log₁₀(f_in)")
    ax.set_zlabel("log₁₀(f)")
    ax.set_title("Gear Cascade")
    ax.set_facecolor("#0a0a0a")

    # 6b — Log-scale bar: timescale hierarchy
    ax2 = fig.add_subplot(1, 4, 2)
    tau_labels = [r"$\tau_\rho$", r"$\tau_{H+}$", r"$\tau_{config}$",
                  r"$\tau_{state}$", r"$\tau_{drug}$"]
    taus = [1e-15, 1e-14, 1e-1, 1e0, 1e3]
    colors_hier = [COLORS["primary"], COLORS["secondary"], COLORS["tertiary"],
                   COLORS["quaternary"], COLORS["accent1"]]
    ax2.bar(tau_labels, taus, color=colors_hier, edgecolor="#999999", width=0.6)
    ax2.set_yscale("log")
    ax2.set_ylabel(r"$\tau$ (s)")
    ax2.set_title("Timescale Hierarchy")

    # 6c — Consciousness decay intersection
    ax3 = fig.add_subplot(1, 4, 3)
    t_ms = np.linspace(0, 300, 500)
    P_decay = np.exp(-t_ms / 50.0)
    T_decay = np.exp(-t_ms / 100.0)
    ax3.plot(t_ms, P_decay, color=COLORS["primary"], lw=1.5, label="P_decay (50ms)")
    ax3.plot(t_ms, T_decay, color=COLORS["secondary"], lw=1.5, label="T_decay (100ms)")
    # intersection region: where both > threshold
    threshold = 0.2
    mask = (P_decay > threshold) & (T_decay > threshold)
    ax3.fill_between(t_ms, 0, 1, where=mask, color=COLORS["accent1"],
                     alpha=0.15, label="Consciousness window")
    ax3.set_xlabel("t (ms)")
    ax3.set_ylabel("amplitude")
    ax3.set_title("Decay Intersection")
    ax3.legend(fontsize=6)

    # 6d — Heatmap: adiabatic coupling matrix
    ax4 = fig.add_subplot(1, 4, 4)
    tau_vals = np.array([1e-15, 1e-14, 1e-1, 1e0, 1e3])
    coupling = np.zeros((5, 5))
    for i in range(5):
        for j in range(5):
            coupling[i, j] = np.log10(max(tau_vals[i], tau_vals[j]) /
                                      min(tau_vals[i], tau_vals[j]) + 1e-30)
    im = ax4.imshow(coupling, cmap="YlOrRd", aspect="equal")
    ax4.set_xticks(range(5))
    ax4.set_xticklabels(tau_labels, fontsize=7)
    ax4.set_yticks(range(5))
    ax4.set_yticklabels(tau_labels, fontsize=7)
    ax4.set_title("Adiabatic Coupling")
    plt.colorbar(im, ax=ax4, label=r"$\log_{10}$ ratio")

    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "panel6_frequency_hierarchy.png"), dpi=200,
                facecolor="#ffffff", bbox_inches="tight")
    plt.close(fig)
    gc.collect()
    print("Panel 6 saved.")


# ===================================================================
# MAIN
# ===================================================================
if __name__ == "__main__":
    panel1()
    panel2()
    panel3()
    panel4()
    panel5()
    panel6()
    print(f"\nAll panels saved to: {OUT}")
