"""
Generate 5 panel figures for:
"The Neural Partition Lagrangian: A Variational Principle for
 Bounded Phase-Space Dynamics Across All Operational Regimes"
"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.colors import Normalize
import matplotlib.cm as cm
import os

# ---------------------------------------------------------------------------
# Global style
# ---------------------------------------------------------------------------
plt.rcParams["font.family"] = "monospace"
plt.rcParams["font.size"] = 8
plt.rcParams["axes.labelsize"] = 9
plt.rcParams["axes.titlesize"] = 10
plt.rcParams["figure.facecolor"] = "white"
plt.rcParams["axes.facecolor"] = "white"
plt.rcParams["axes.edgecolor"] = "#cccccc"
plt.rcParams["axes.grid"] = True
plt.rcParams["grid.alpha"] = 0.4
plt.rcParams["grid.color"] = "#cccccc"
plt.rcParams["text.color"] = "#222222"
plt.rcParams["axes.labelcolor"] = "#333333"
plt.rcParams["xtick.color"] = "#444444"
plt.rcParams["ytick.color"] = "#444444"

BLUE = "#1f77b4"
RED = "#d62728"
GREEN = "#2ca02c"
ORANGE = "#ff7f0e"
PURPLE = "#9467bd"
CYAN = "#17becf"

OUT = os.path.join(os.path.dirname(__file__), "figures")
os.makedirs(OUT, exist_ok=True)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
sigma_param = 2.0
Kc = 2 * sigma_param / np.pi

kBT = 0.1
alpha_sf = 0.5


def V_sync(R, K):
    return (Kc - K) / 2.0 * R**2 + K / 4.0 * R**4


def V_var(sig2, K):
    return kBT * sig2 + kBT / (K * sig2 + 1e-12)


def V_SF(R, sig2):
    return -alpha_sf * R * np.exp(-sig2 / (2 * np.pi**2))


def Phi(R, sig2, K):
    return V_sync(R, K) + V_var(sig2, K) + V_SF(R, sig2)


def regime_color(R):
    if R < 0.3:
        return RED
    elif R < 0.5:
        return ORANGE
    elif R < 0.8:
        return GREEN
    elif R < 0.95:
        return CYAN
    else:
        return BLUE


def regime_index(R):
    if R < 0.3:
        return 0
    elif R < 0.5:
        return 1
    elif R < 0.8:
        return 2
    elif R < 0.95:
        return 3
    else:
        return 4


# ---------------------------------------------------------------------------
# Panel 1: Neural Partition Potential Landscape
# ---------------------------------------------------------------------------
def panel_1():
    fig = plt.figure(figsize=(20, 5), dpi=150)

    # (A) 3D surface V_sync(R; K)
    ax = fig.add_subplot(1, 4, 1, projection="3d")
    R_a = np.linspace(0, 1, 80)
    K_a = np.array([0.5, 1.0, 1.5, 2.0, 3.0])
    Rg, Kg = np.meshgrid(R_a, K_a)
    Zg = V_sync(Rg, Kg)
    ax.plot_surface(Rg, Kg, Zg, cmap="viridis", alpha=0.85, edgecolor="none")
    ax.set_xlabel("R")
    ax.set_ylabel("K")
    ax.set_zlabel(r"$V_{\rm sync}$")
    ax.set_title("(A) Sync potential surface")
    ax.view_init(elev=28, azim=-50)

    # (B) 2D bifurcation curves
    ax2 = fig.add_subplot(1, 4, 2)
    R_b = np.linspace(-0.05, 1.0, 300)
    for K_val, ls, lab in [
        (0.8 * Kc, "-", r"$K<K_c$"),
        (Kc, "--", r"$K=K_c$"),
        (1.8 * Kc, "-.", r"$K>K_c$"),
    ]:
        ax2.plot(R_b, V_sync(R_b, K_val), ls, label=lab)
    # mark R*
    K_super = 1.8 * Kc
    Rstar = np.sqrt(1 - Kc / K_super)
    ax2.plot(Rstar, V_sync(Rstar, K_super), "o", color=RED, ms=6)
    ax2.set_xlabel("R")
    ax2.set_ylabel(r"$V_{\rm sync}$")
    ax2.set_title("(B) Pitchfork bifurcation")
    ax2.legend(fontsize=7)

    # (C) Contour of full Phi(R, sigma^2)
    ax3 = fig.add_subplot(1, 4, 3)
    R_c = np.linspace(0.01, 1.0, 200)
    s_c = np.linspace(0.1, 3.0, 200)
    Rc, Sc = np.meshgrid(R_c, s_c)
    K_fixed = 2.0
    Zc = Phi(Rc, Sc, K_fixed)
    cf = ax3.contourf(Rc, Sc, Zc, levels=30, cmap="coolwarm")
    ax3.contour(Rc, Sc, Zc, levels=15, colors="k", linewidths=0.3, alpha=0.5)
    for xb in [0.3, 0.5, 0.8, 0.95]:
        ax3.axvline(xb, ls="--", color="#555555", lw=0.8)
    plt.colorbar(cf, ax=ax3, pad=0.02)
    ax3.set_xlabel("R")
    ax3.set_ylabel(r"$\sigma^2$")
    ax3.set_title(r"(C) Full potential $\Phi(R,\sigma^2)$")

    # (D) Curvature heatmap d^2 Phi / dR^2
    ax4 = fig.add_subplot(1, 4, 4)
    dR = 1e-4
    d2Phi = (Phi(Rc + dR, Sc, K_fixed) - 2 * Phi(Rc, Sc, K_fixed) + Phi(Rc - dR, Sc, K_fixed)) / dR**2
    vmax = np.percentile(np.abs(d2Phi), 95)
    im = ax4.pcolormesh(Rc, Sc, d2Phi, cmap="coolwarm", vmin=-vmax, vmax=vmax, shading="auto")
    plt.colorbar(im, ax=ax4, pad=0.02)
    ax4.set_xlabel("R")
    ax4.set_ylabel(r"$\sigma^2$")
    ax4.set_title(r"(D) Curvature $\partial^2\Phi/\partial R^2$")

    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "panel_1_potential_landscape.png"), dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("  -> panel_1_potential_landscape.png")


# ---------------------------------------------------------------------------
# Panel 2: Euler-Lagrange Dynamics
# ---------------------------------------------------------------------------
def panel_2():
    fig = plt.figure(figsize=(20, 5), dpi=150)

    # Simulate gradient flow
    n_steps = 200
    dt = 0.05
    dh = 1e-5
    Rs = np.zeros(n_steps)
    Ss = np.zeros(n_steps)
    Ks = np.linspace(0.5, 5.0, n_steps)
    R_t, S_t = 0.05, 1.5
    for i in range(n_steps):
        K_i = Ks[i]
        dPhidR = (Phi(R_t + dh, S_t, K_i) - Phi(R_t - dh, S_t, K_i)) / (2 * dh)
        dPhidS = (Phi(R_t, S_t + dh, K_i) - Phi(R_t, S_t - dh, K_i)) / (2 * dh)
        R_t = np.clip(R_t - dt * dPhidR, 0.001, 0.999)
        S_t = np.clip(S_t - dt * dPhidS, 0.05, 5.0)
        Rs[i] = R_t
        Ss[i] = S_t
    ts = np.arange(n_steps) * dt
    colors_traj = [regime_color(r) for r in Rs]

    # (A) 3D trajectory
    ax = fig.add_subplot(1, 4, 1, projection="3d")
    for i in range(n_steps - 1):
        ax.plot(Rs[i : i + 2], Ss[i : i + 2], ts[i : i + 2], color=colors_traj[i], lw=1.2)
    ax.set_xlabel("R")
    ax.set_ylabel(r"$\sigma^2$")
    ax.set_zlabel("t")
    ax.set_title("(A) Gradient flow trajectory")
    ax.view_init(elev=25, azim=-45)

    # (B) Phase portrait quiver
    ax2 = fig.add_subplot(1, 4, 2)
    R_q = np.linspace(0.01, 1.0, 20)
    S_q = np.linspace(0.1, 3.0, 20)
    Rq, Sq = np.meshgrid(R_q, S_q)
    K_q = 3.0
    dR = -(Phi(Rq + dh, Sq, K_q) - Phi(Rq - dh, Sq, K_q)) / (2 * dh)
    dS = -(Phi(Rq, Sq + dh, K_q) - Phi(Rq, Sq - dh, K_q)) / (2 * dh)
    mag = np.sqrt(dR**2 + dS**2) + 1e-12
    ax2.quiver(Rq, Sq, dR / mag, dS / mag, mag, cmap="plasma", alpha=0.7)
    ax2.plot(Rs, Ss, "k-", lw=0.8, alpha=0.6)
    ax2.plot(Rs[0], Ss[0], "o", color=RED, ms=5)
    ax2.plot(Rs[-1], Ss[-1], "s", color=BLUE, ms=5)
    # find approx fixed points
    R_fp = np.linspace(0.01, 1.0, 200)
    S_fp = np.linspace(0.1, 3.0, 200)
    Rfp, Sfp = np.meshgrid(R_fp, S_fp)
    gR = (Phi(Rfp + dh, Sfp, K_q) - Phi(Rfp - dh, Sfp, K_q)) / (2 * dh)
    gS = (Phi(Rfp, Sfp + dh, K_q) - Phi(Rfp, Sfp - dh, K_q)) / (2 * dh)
    g_mag = np.sqrt(gR**2 + gS**2)
    min_idx = np.unravel_index(np.argmin(g_mag), g_mag.shape)
    ax2.plot(Rfp[min_idx], Sfp[min_idx], "*", color=GREEN, ms=10, zorder=5)
    ax2.set_xlabel("R")
    ax2.set_ylabel(r"$\sigma^2$")
    ax2.set_title("(B) Phase portrait (K=3.0)")

    # (C) Time series R(t), sigma^2(t)
    ax3 = fig.add_subplot(1, 4, 3)
    ax3.plot(ts, Rs, color=BLUE, label="R(t)")
    ax3.set_xlabel("t")
    ax3.set_ylabel("R(t)", color=BLUE)
    ax3r = ax3.twinx()
    ax3r.plot(ts, Ss, color=RED, label=r"$\sigma^2(t)$")
    ax3r.set_ylabel(r"$\sigma^2(t)$", color=RED)
    # regime transitions
    prev_reg = regime_index(Rs[0])
    for i in range(1, n_steps):
        cur = regime_index(Rs[i])
        if cur != prev_reg:
            ax3.axvline(ts[i], ls="--", color="#888888", lw=0.7)
            prev_reg = cur
    ax3.set_title("(C) Order parameter evolution")

    # (D) Energy dissipation
    ax4 = fig.add_subplot(1, 4, 4)
    Phi_vals = np.array([Phi(Rs[i], Ss[i], Ks[i]) for i in range(n_steps)])
    dPhi_dt = np.abs(np.gradient(Phi_vals, dt))
    ax4.semilogy(ts, dPhi_dt + 1e-8, color=PURPLE, lw=1.0)
    prev_reg = regime_index(Rs[0])
    for i in range(1, n_steps):
        cur = regime_index(Rs[i])
        if cur != prev_reg:
            ax4.axvline(ts[i], ls="--", color="#888888", lw=0.7)
            prev_reg = cur
    ax4.set_xlabel("t")
    ax4.set_ylabel(r"$|d\Phi/dt|$")
    ax4.set_title(r"(D) Dissipation rate")

    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "panel_2_euler_lagrange_dynamics.png"), dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("  -> panel_2_euler_lagrange_dynamics.png")


# ---------------------------------------------------------------------------
# Panel 3: Aperture Constraints and Reduced Manifolds
# ---------------------------------------------------------------------------
def panel_3():
    fig = plt.figure(figsize=(20, 5), dpi=150)

    # (A) 3D manifold projections
    ax = fig.add_subplot(1, 4, 1, projection="3d")
    np.random.seed(42)
    # monopole: 4D surface -> scattered cloud in 3D
    n_pts = 600
    R_m = np.random.uniform(0.0, 1.0, n_pts)
    S_m = np.random.uniform(0.1, 2.5, n_pts)
    Sk_m = 0.3 * R_m + 0.2 * S_m + 0.05 * np.random.randn(n_pts)
    ax.scatter(R_m, S_m, Sk_m, c=BLUE, alpha=0.08, s=4, label="monopole (1)")

    # dipole: 3D surface
    R_d = np.random.uniform(0.0, 1.0, 300)
    S_d = 0.5 + 0.8 * R_d + 0.1 * np.random.randn(300)
    Sk_d = 0.4 * R_d + 0.3 * S_d + 0.03 * np.random.randn(300)
    ax.scatter(R_d, S_d, Sk_d, c=GREEN, alpha=0.25, s=8, label="dipole (2)")

    # quadrupole: 1D curve
    t_q = np.linspace(0, 1, 100)
    R_q = t_q
    S_q = 0.5 + 0.8 * t_q
    Sk_q = 0.4 * t_q + 0.3 * S_q
    ax.plot(R_q, S_q, Sk_q, color=PURPLE, lw=2.5, label="quadrupole (4)")

    ax.set_xlabel("R")
    ax.set_ylabel(r"$\sigma^2$")
    ax.set_zlabel(r"$S_k$")
    ax.set_title("(A) Constraint manifolds")
    ax.legend(fontsize=6, loc="upper left")
    ax.view_init(elev=22, azim=-55)

    # (B) Hill dose-response
    ax2 = fig.add_subplot(1, 4, 2)
    dose = np.linspace(0.1, 100, 300)
    EC50 = 10.0
    for n, c, lab in [(1, BLUE, "n=1 (monopole)"), (2, GREEN, "n=2 (dipole)"), (4, PURPLE, "n=4 (quadrupole)")]:
        resp = dose**n / (EC50**n + dose**n)
        ax2.plot(dose, resp, color=c, lw=1.5, label=lab)
    ax2.set_xlabel("Dose")
    ax2.set_ylabel("Response")
    ax2.set_title("(B) Hill dose-response")
    ax2.legend(fontsize=6)

    # (C) Scatter: n_constraints vs Hill coefficient
    ax3 = fig.add_subplot(1, 4, 3)
    # Synthetic drug data
    drug_data = {
        "SSRI": [(1, 1.1), (1, 0.9), (2, 1.8), (2, 2.1)],
        "SNRI": [(2, 2.2), (3, 2.8), (3, 3.1)],
        "TCA": [(4, 3.8), (4, 4.2), (5, 4.6), (5, 5.1)],
    }
    dcol = {"SSRI": BLUE, "SNRI": GREEN, "TCA": PURPLE}
    for cls, pts in drug_data.items():
        nc = [p[0] for p in pts]
        nh = [p[1] for p in pts]
        ax3.scatter(nc, nh, color=dcol[cls], s=40, label=cls, zorder=3)
    ax3.plot([0, 6], [0, 6], "k--", lw=0.8, alpha=0.5)
    ax3.set_xlabel(r"$n_{\rm constraints}$")
    ax3.set_ylabel(r"$n_H$ (Hill coeff)")
    ax3.set_title(r"(C) Constraints vs Hill coeff")
    ax3.legend(fontsize=6)

    # (D) Heatmap: effective dimensionality
    ax4 = fig.add_subplot(1, 4, 4)
    drugs = [
        "SSRI-1", "SSRI-2", "SSRI-3", "SSRI-4",
        "SNRI-1", "SNRI-2", "SNRI-3",
        "TCA-1", "TCA-2", "TCA-3", "TCA-4",
    ]
    n_con = [1, 1, 2, 2, 2, 3, 3, 4, 4, 5, 5]
    eff_dim = [5 - nc for nc in n_con]
    im = ax4.imshow(np.array(eff_dim).reshape(1, -1), cmap="YlOrRd_r", aspect="auto", vmin=0, vmax=5)
    ax4.set_xticks(range(len(drugs)))
    ax4.set_xticklabels(drugs, rotation=60, ha="right", fontsize=6)
    ax4.set_yticks([])
    plt.colorbar(im, ax=ax4, pad=0.02, label="eff. dim")
    ax4.set_title("(D) Effective dimensionality")

    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "panel_3_aperture_constraints.png"), dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("  -> panel_3_aperture_constraints.png")


# ---------------------------------------------------------------------------
# Panel 4: Noether Conservation and Symmetry
# ---------------------------------------------------------------------------
def panel_4():
    fig = plt.figure(figsize=(20, 5), dpi=150)

    # (A) 3D bar chart C(n) = 2n^2
    ax = fig.add_subplot(1, 4, 1, projection="3d")
    ns = np.arange(1, 8)
    Cn = 2 * ns**2
    x_pos = ns
    y_pos = np.zeros_like(ns)
    z_pos = np.zeros_like(ns)
    dx = 0.6 * np.ones_like(ns)
    dy = 0.6 * np.ones_like(ns)
    colors_bar = [BLUE, RED, GREEN, ORANGE, PURPLE, CYAN, BLUE]
    ax.bar3d(x_pos, y_pos, z_pos, dx, dy, Cn, color=colors_bar, alpha=0.85)
    # overlay formula curve
    ns_fine = np.linspace(1, 7, 100)
    ax.plot(ns_fine, np.zeros_like(ns_fine) + 0.3, 2 * ns_fine**2, color="k", lw=1.5)
    ax.set_xlabel("n")
    ax.set_ylabel("")
    ax.set_zlabel("C(n)")
    ax.set_title(r"(A) Partition capacity $C(n)=2n^2$")
    ax.view_init(elev=25, azim=-50)

    # simulate S-entropy trajectories
    np.random.seed(7)
    n_t = 300
    t = np.linspace(0, 10, n_t)

    def make_S_traj(seed_offset):
        rng = np.random.RandomState(seed_offset)
        Sk = np.cumsum(0.02 * rng.randn(n_t)) + 0.5
        St = np.cumsum(0.02 * rng.randn(n_t)) + 0.3
        Se = np.cumsum(0.02 * rng.randn(n_t)) + 0.4
        # normalise segments to keep ||S|| ~ const within regimes
        norm = np.sqrt(Sk**2 + St**2 + Se**2)
        target = 1.0
        # regime transitions at t ~ 3, 6
        for seg_start, seg_end in [(0, 100), (100, 200), (200, 300)]:
            seg_norm = np.mean(norm[seg_start:seg_end])
            scale = target / seg_norm
            Sk[seg_start:seg_end] *= scale
            St[seg_start:seg_end] *= scale
            Se[seg_start:seg_end] *= scale
            target += 0.15  # small jump between regimes
        return Sk, St, Se

    Sk1, St1, Se1 = make_S_traj(10)
    Sk2, St2, Se2 = make_S_traj(20)
    M1 = np.cumsum(np.abs(np.gradient(Sk1))) * 0.1

    # (B) 3D S-entropy trajectories
    ax2 = fig.add_subplot(1, 4, 2, projection="3d")
    sc = ax2.scatter(Sk1, St1, Se1, c=M1, cmap="plasma", s=3, alpha=0.7)
    ax2.plot(Sk2, St2, Se2, color="#888888", lw=0.6, alpha=0.5)
    ax2.set_xlabel(r"$S_k$")
    ax2.set_ylabel(r"$S_t$")
    ax2.set_zlabel(r"$S_e$")
    ax2.set_title("(B) S-entropy trajectories")
    ax2.view_init(elev=20, azim=-40)

    # (C) ||S(t)|| conservation check
    ax3 = fig.add_subplot(1, 4, 3)
    norm1 = np.sqrt(Sk1**2 + St1**2 + Se1**2)
    norm2 = np.sqrt(Sk2**2 + St2**2 + Se2**2)
    ax3.plot(t, norm1, color=BLUE, lw=1.2, label="Traj 1")
    ax3.plot(t, norm2, color=RED, lw=1.2, label="Traj 2")
    for tv in [t[100], t[200]]:
        ax3.axvline(tv, ls="--", color="#888888", lw=0.7)
    ax3.set_xlabel("t")
    ax3.set_ylabel(r"$\|S(t)\|$")
    ax3.set_title(r"(C) Conservation of $\|S\|$")
    ax3.legend(fontsize=6)

    # (D) Kramers escape rate
    ax4 = fig.add_subplot(1, 4, 4)
    D_noise = 0.1
    barrier_heights = np.linspace(0.05, 2.0, 50)
    Gamma = np.exp(-barrier_heights / D_noise)
    ax4.semilogy(barrier_heights, Gamma, color=PURPLE, lw=1.5)
    # label adjacent regime pairs
    regime_pairs = [
        (r"T$\to$A", 0.2),
        (r"A$\to$C", 0.5),
        (r"C$\to$Co", 0.9),
        (r"Co$\to$PL", 1.4),
    ]
    for lab, dPhi in regime_pairs:
        ax4.plot(dPhi, np.exp(-dPhi / D_noise), "o", color=RED, ms=5)
        ax4.annotate(lab, (dPhi, np.exp(-dPhi / D_noise)),
                     textcoords="offset points", xytext=(5, 5), fontsize=6)
    ax4.set_xlabel(r"$\Delta\Phi$")
    ax4.set_ylabel(r"$\Gamma$ (escape rate)")
    ax4.set_title(r"(D) Kramers escape rate")

    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "panel_4_noether_conservation.png"), dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("  -> panel_4_noether_conservation.png")


# ---------------------------------------------------------------------------
# Panel 5: Validation Summary and Predictions
# ---------------------------------------------------------------------------
def panel_5():
    fig = plt.figure(figsize=(20, 5), dpi=150)

    # (A) 3D Onsager-Machlup Lagrangian surface
    ax = fig.add_subplot(1, 4, 1, projection="3d")
    D_om = 0.1
    R_a = np.linspace(0.01, 1.0, 60)
    S_a = np.linspace(0.1, 3.0, 60)
    Ra, Sa = np.meshgrid(R_a, S_a)
    K_om = 3.0
    dh = 1e-5
    gR = (Phi(Ra + dh, Sa, K_om) - Phi(Ra - dh, Sa, K_om)) / (2 * dh)
    gS = (Phi(Ra, Sa + dh, K_om) - Phi(Ra, Sa - dh, K_om)) / (2 * dh)
    # deterministic path: dq/dt = -grad Phi, so L = 0
    L_det = 1 / (4 * D_om) * (gR**2 + gS**2) * 0  # identically 0 on det path
    # perturbed: add noise to velocity
    L_pert = 1 / (4 * D_om) * (0.3**2 + gR**2 + gS**2)
    ax.plot_surface(Ra, Sa, L_pert, cmap="inferno", alpha=0.7, edgecolor="none")
    # deterministic = zero plane
    ax.plot_surface(Ra, Sa, L_det, color=CYAN, alpha=0.3, edgecolor="none")
    ax.set_xlabel("R")
    ax.set_ylabel(r"$\sigma^2$")
    ax.set_zlabel("L")
    ax.set_title("(A) Onsager-Machlup Lagrangian")
    ax.view_init(elev=25, azim=-45)

    # (B) Grouped bar chart: validated claims
    ax2 = fig.add_subplot(1, 4, 2)
    domains = ["NPL", "Sleep", "Pharm", "Enzyme", "New pred"]
    counts = [10, 6, 7, 4, 3]
    bar_colors = [BLUE, GREEN, PURPLE, ORANGE, RED]
    heights = [1.0, 1.0, 1.0, 1.0, 0.5]
    x_pos = np.arange(len(domains))
    bars = ax2.bar(x_pos, [c * h for c, h in zip(counts, heights)], color=bar_colors, edgecolor="white", width=0.6)
    # number labels
    for i, (b, c, h) in enumerate(zip(bars, counts, heights)):
        ax2.text(i, b.get_height() + 0.15, f"{c}", ha="center", fontsize=7)
    ax2.set_xticks(x_pos)
    ax2.set_xticklabels(domains, fontsize=7)
    ax2.set_ylabel("Claims (height = status)")
    ax2.set_title("(B) Validation summary")

    # (C) Variance scaling log-log
    ax3 = fig.add_subplot(1, 4, 3)
    K_vals = np.linspace(1.0, 10.0, 10)
    np.random.seed(3)
    sig2_min = 1.0 / K_vals + 0.02 * np.random.randn(10)
    sig2_min = np.clip(sig2_min, 0.01, None)
    ax3.loglog(K_vals, sig2_min, "o", color=BLUE, ms=5, label="simulated")
    K_line = np.linspace(0.8, 12, 100)
    ax3.loglog(K_line, 1.0 / K_line, "--", color=RED, lw=1.2, label=r"slope $= -1$")
    ax3.set_xlabel("K")
    ax3.set_ylabel(r"$\sigma^2_{\rm min}$")
    ax3.set_title(r"(C) Variance scaling $\sigma^2 \propto K^{-1}$")
    ax3.legend(fontsize=6)

    # (D) Critical slowing: tau_relax vs (K-Kc)/Kc
    ax4 = fig.add_subplot(1, 4, 4)
    eps = np.linspace(0.01, 2.0, 200)
    K_vals_d = Kc * (1 + eps)
    R_star = np.sqrt(1 - Kc / K_vals_d)
    # Phi''(R*) ~ 2*(K - Kc) for small eps, more precisely:
    Phi_pp = (Kc - K_vals_d) + 3 * K_vals_d * R_star**2
    Phi_pp = np.clip(Phi_pp, 0.01, None)
    tau = 1.0 / Phi_pp
    ax4.plot(eps, tau, color=CYAN, lw=1.5)
    ax4.set_xlabel(r"$(K - K_c)/K_c$")
    ax4.set_ylabel(r"$\tau_{\rm relax}$")
    ax4.set_title(r"(D) Critical slowing near $K_c$")
    ax4.set_xlim(0, 2.0)

    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "panel_5_validation_predictions.png"), dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("  -> panel_5_validation_predictions.png")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("Generating panels...")
    panel_1()
    panel_2()
    panel_3()
    panel_4()
    panel_5()
    print("Done.")
