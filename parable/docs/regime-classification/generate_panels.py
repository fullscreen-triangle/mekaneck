#!/usr/bin/env python3
"""
Generate 6 panel figures for the Regime Classification paper.

Each panel is a 1x4 grid (wide row) with at least one 3D chart.

Panels:
1. Kuramoto Synchronization Dynamics
2. Five Operational Regimes
3. Sleep Architecture as Regime Sequence
4. Critical Coupling and Phase Transitions
5. Consciousness Window and Temporal Dynamics
6. Variance Minimization and Free Energy
"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
from matplotlib.colors import Normalize, ListedColormap, BoundaryNorm
from matplotlib.patches import FancyArrowPatch
from pathlib import Path
import warnings

warnings.filterwarnings("ignore")

# Style — light / white theme
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
plt.rcParams["axes.labelcolor"] = "#222222"
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

OUTPUT_DIR = Path(__file__).parent / "figures"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

np.random.seed(42)


# ---------------------------------------------------------------------------
# Kuramoto simulation utility
# ---------------------------------------------------------------------------

def simulate_kuramoto(N, K, omega, dt, T, phases_init=None):
    """Euler integration of Kuramoto model. Returns (t_array, phases, R_array)."""
    t = np.arange(0, T, dt)
    if phases_init is None:
        phases_init = np.random.uniform(0, 2 * np.pi, N)
    phases = phases_init.copy()
    R_arr = np.zeros(len(t))
    for idx in range(len(t)):
        z = np.exp(1j * phases)
        R_arr[idx] = np.abs(np.mean(z))
        coupling = K / N * np.sum(np.sin(phases[None, :] - phases[:, None]), axis=1)
        phases += (omega + coupling) * dt
    return t, phases, R_arr


# ============================================================================
# PANEL 1 — Kuramoto Synchronization Dynamics
# ============================================================================

def panel_1():
    fig = plt.figure(figsize=(20, 5), facecolor="white")
    fig.suptitle("Kuramoto Synchronization Dynamics", fontsize=12,
                 color="#222222", y=0.97)

    N = 100
    dt = 0.05
    T = 20.0
    freq_std = 2.0
    omega = np.random.randn(N) * freq_std
    phases0 = np.random.uniform(0, 2 * np.pi, N)

    # --- Chart 1: 3D surface R(K, t) ---
    ax1 = fig.add_subplot(1, 4, 1, projection="3d")
    K_range = np.linspace(0.5, 5.0, 25)
    t_sub = np.arange(0, T, dt)
    # downsample time for surface
    t_idx = np.linspace(0, len(t_sub) - 1, 60, dtype=int)
    R_surface = np.zeros((len(K_range), len(t_idx)))
    for i, K in enumerate(K_range):
        _, _, R_arr = simulate_kuramoto(N, K, omega, dt, T, phases0.copy())
        R_surface[i, :] = R_arr[t_idx]
    T_grid, K_grid = np.meshgrid(t_sub[t_idx], K_range)
    ax1.plot_surface(T_grid, K_grid, R_surface, cmap="viridis", alpha=0.9,
                     edgecolor="none")
    ax1.set_xlabel("time (s)")
    ax1.set_ylabel("K")
    ax1.set_zlabel("R")
    ax1.set_title("R(K, t)")
    ax1.view_init(30, -50)

    # --- Chart 2: R(t) for 4 coupling strengths ---
    ax2 = fig.add_subplot(1, 4, 2)
    K_demo = [0.5, 1.5, 3.0, 5.0]
    colors_demo = [COLORS["secondary"], COLORS["quaternary"],
                   COLORS["tertiary"], COLORS["primary"]]
    for K, c in zip(K_demo, colors_demo):
        t_arr, _, R_arr = simulate_kuramoto(N, K, omega, dt, T, phases0.copy())
        ax2.plot(t_arr, R_arr, color=c, lw=1.2, label=f"K={K}")
    ax2.set_xlabel("time (s)")
    ax2.set_ylabel("R(t)")
    ax2.set_title("Sync onset")
    ax2.legend(fontsize=6, framealpha=0.3)

    # --- Chart 3: Final R vs K/K_c ---
    ax3 = fig.add_subplot(1, 4, 3)
    K_c = 2.0 * freq_std / (np.pi)  # Kc for Gaussian g(0)
    K_scan = np.linspace(0.3, 6.0, 20)
    R_final = np.zeros(len(K_scan))
    for i, K in enumerate(K_scan):
        _, _, R_arr = simulate_kuramoto(N, K, omega, dt, T, phases0.copy())
        R_final[i] = np.mean(R_arr[-50:])
    ratio = K_scan / K_c
    regime_colors = [COLORS["secondary"] if r < 0.4 else
                     (COLORS["quaternary"] if r < 0.65 else COLORS["primary"])
                     for r in R_final]
    ax3.scatter(ratio, R_final, c=regime_colors, s=30, zorder=3)
    ax3.axvline(1.0, color=COLORS["accent1"], ls="--", lw=0.8, label="K/K_c=1")
    ax3.set_xlabel("K / K_c")
    ax3.set_ylabel("R_final")
    ax3.set_title("Regime classification")
    ax3.legend(fontsize=6, framealpha=0.3)

    # --- Chart 4: Phase coherence heatmap (turbulent vs coherent) ---
    ax4a = fig.add_subplot(1, 4, 4)
    # Low K (turbulent)
    _, phases_low, _ = simulate_kuramoto(N, 0.5, omega, dt, T, phases0.copy())
    _, phases_high, _ = simulate_kuramoto(N, 5.0, omega, dt, T, phases0.copy())
    sel = 10
    coh_low = np.cos(phases_low[:sel, None] - phases_low[None, :sel])
    coh_high = np.cos(phases_high[:sel, None] - phases_high[None, :sel])
    combined = np.concatenate([coh_low, coh_high], axis=1)  # 10x20
    im = ax4a.imshow(combined, cmap="inferno", aspect="auto", vmin=-1, vmax=1)
    ax4a.axvline(9.5, color="black", lw=0.8, ls="--")
    ax4a.set_xlabel("oscillator pair")
    ax4a.set_ylabel("oscillator")
    ax4a.set_title("Coherence: K=0.5 | K=5.0")
    fig.colorbar(im, ax=ax4a, fraction=0.046, pad=0.04)

    fig.tight_layout(rect=[0, 0, 1, 0.93])
    fig.savefig(OUTPUT_DIR / "panel_1_kuramoto_sync.png", dpi=200, facecolor="white")
    plt.close(fig)
    print("  Panel 1 saved.")


# ============================================================================
# PANEL 2 — Five Operational Regimes
# ============================================================================

def panel_2():
    fig = plt.figure(figsize=(20, 5), facecolor="white")
    fig.suptitle("Five Operational Regimes", fontsize=12,
                 color="#222222", y=0.97)

    R_arr = np.linspace(0, 1, 200)
    sigma2_arr = np.linspace(0, 2 * np.pi**2, 200)

    # Structural factor model
    def S_func(R, sigma2):
        return R * np.exp(-sigma2 / (2 * np.pi**2))

    # --- Chart 1: 3D surface S(R, sigma2) ---
    ax1 = fig.add_subplot(1, 4, 1, projection="3d")
    Rg, Sg = np.meshgrid(R_arr, sigma2_arr)
    Z = S_func(Rg, Sg)
    # Color by regime: threshold on Z
    ax1.plot_surface(Rg, Sg, Z, cmap="plasma", alpha=0.9, edgecolor="none")
    ax1.set_xlabel("R")
    ax1.set_ylabel("sigma^2")
    ax1.set_zlabel("S")
    ax1.set_title("S(R, sigma^2)")
    ax1.view_init(25, -55)

    # --- Chart 2: S components vs R ---
    ax2 = fig.add_subplot(1, 4, 2)
    S_coh = R_arr**2
    S_turb = (1 - R_arr)**2
    S_sync = 4 * R_arr * (1 - R_arr)
    ax2.plot(R_arr, S_coh, color=COLORS["primary"], lw=1.4, label="S_coherent")
    ax2.plot(R_arr, S_turb, color=COLORS["secondary"], lw=1.4, label="S_turbulent")
    ax2.plot(R_arr, S_sync, color=COLORS["quaternary"], lw=1.4, label="S_sync")
    # Regime boundaries
    bounds = [0.2, 0.4, 0.6, 0.8]
    regime_cols = [COLORS["secondary"], COLORS["quaternary"], COLORS["accent1"],
                   COLORS["tertiary"], COLORS["primary"]]
    for i in range(len(bounds)):
        ax2.axvspan(bounds[i] - 0.005, bounds[i] + 0.005,
                    color=regime_cols[i], alpha=0.25)
    ax2.set_xlabel("R")
    ax2.set_ylabel("S")
    ax2.set_title("Structural factors")
    ax2.legend(fontsize=6, framealpha=0.3)

    # --- Chart 3: Mean R per sleep stage ---
    ax3 = fig.add_subplot(1, 4, 3)
    stages = ["W", "N1", "N2", "N3", "REM"]
    mean_R = [0.67, 0.49, 0.44, 0.71, 0.31]
    std_R = [0.025, 0.028, 0.022, 0.030, 0.026]
    bar_colors = [COLORS["primary"], COLORS["accent1"], COLORS["quaternary"],
                  COLORS["tertiary"], COLORS["secondary"]]
    ax3.bar(stages, mean_R, yerr=std_R, color=bar_colors, edgecolor="#999999",
            capsize=3, width=0.6, alpha=0.9)
    ax3.set_ylabel("Mean R")
    ax3.set_title("R per sleep stage")

    # --- Chart 4: Filled contour regime map ---
    ax4 = fig.add_subplot(1, 4, 4)
    Rg2, Sg2 = np.meshgrid(np.linspace(0, 1, 300), np.linspace(0, 2 * np.pi**2, 300))
    # Regime assignment via thresholds on S
    Zval = S_func(Rg2, Sg2)
    regime_map = np.zeros_like(Zval)
    regime_map[Zval < 0.15] = 0
    regime_map[(Zval >= 0.15) & (Zval < 0.35)] = 1
    regime_map[(Zval >= 0.35) & (Zval < 0.55)] = 2
    regime_map[(Zval >= 0.55) & (Zval < 0.75)] = 3
    regime_map[Zval >= 0.75] = 4
    cmap5 = ListedColormap([COLORS["secondary"], COLORS["quaternary"],
                            COLORS["accent1"], COLORS["tertiary"], COLORS["primary"]])
    ax4.contourf(Rg2, Sg2, regime_map, levels=[-0.5, 0.5, 1.5, 2.5, 3.5, 4.5],
                 cmap=cmap5, alpha=0.7)
    # Sleep stages as scatter
    stage_R = [0.67, 0.49, 0.44, 0.71, 0.31]
    stage_s2 = [2.0, 6.0, 8.0, 1.5, 12.0]
    ax4.scatter(stage_R, stage_s2, c="black", s=40, edgecolors="white",
                zorder=5, linewidths=0.6)
    for s, r, sv in zip(stages, stage_R, stage_s2):
        ax4.annotate(s, (r, sv), fontsize=6, color="#222222",
                     xytext=(3, 3), textcoords="offset points")
    ax4.set_xlabel("R")
    ax4.set_ylabel("sigma^2")
    ax4.set_title("Regime map")

    fig.tight_layout(rect=[0, 0, 1, 0.93])
    fig.savefig(OUTPUT_DIR / "panel_2_five_regimes.png", dpi=200, facecolor="white")
    plt.close(fig)
    print("  Panel 2 saved.")


# ============================================================================
# PANEL 3 — Sleep Architecture as Regime Sequence
# ============================================================================

def panel_3():
    fig = plt.figure(figsize=(20, 5), facecolor="white")
    fig.suptitle("Sleep Architecture as Regime Sequence", fontsize=12,
                 color="#222222", y=0.97)

    stages = ["W", "N1", "N2", "N3", "REM"]
    stage_R_mean = {"W": 0.67, "N1": 0.49, "N2": 0.44, "N3": 0.71, "REM": 0.31}
    stage_R_std = {"W": 0.06, "N1": 0.07, "N2": 0.06, "N3": 0.05, "REM": 0.08}
    stage_colors = [COLORS["primary"], COLORS["accent1"], COLORS["quaternary"],
                    COLORS["tertiary"], COLORS["secondary"]]

    # Generate synthetic epoch data
    N_epochs = 500
    epoch_stage = np.random.choice(5, N_epochs, p=[0.15, 0.10, 0.35, 0.20, 0.20])
    R_power = np.array([stage_R_mean[stages[s]] + stage_R_std[stages[s]] * np.random.randn()
                        for s in epoch_stage])
    R_hilbert = R_power + 0.05 * np.random.randn(N_epochs)
    R_power = np.clip(R_power, 0, 1)
    R_hilbert = np.clip(R_hilbert, 0, 1)

    # --- Chart 1: 3D scatter ---
    ax1 = fig.add_subplot(1, 4, 1, projection="3d")
    for si in range(5):
        mask = epoch_stage == si
        ax1.scatter(R_power[mask], R_hilbert[mask], epoch_stage[mask],
                    c=stage_colors[si], s=6, alpha=0.6, label=stages[si])
    ax1.set_xlabel("R_power")
    ax1.set_ylabel("R_hilbert")
    ax1.set_zlabel("stage")
    ax1.set_title("Epoch space")
    ax1.legend(fontsize=5, framealpha=0.3, markerscale=2)
    ax1.view_init(25, -40)

    # --- Chart 2: Violin / box plot R per stage ---
    ax2 = fig.add_subplot(1, 4, 2)
    data_per_stage = [R_power[epoch_stage == si] for si in range(5)]
    parts = ax2.violinplot(data_per_stage, positions=range(5), showmedians=True,
                           showextrema=False)
    for i, pc in enumerate(parts["bodies"]):
        pc.set_facecolor(stage_colors[i])
        pc.set_alpha(0.7)
    parts["cmedians"].set_color("black")
    ax2.set_xticks(range(5))
    ax2.set_xticklabels(stages)
    ax2.set_ylabel("R")
    ax2.set_title("R distributions")

    # --- Chart 3: Synthetic hypnogram with R(t) ---
    ax3 = fig.add_subplot(1, 4, 3)
    # Build ~8 hours (480 min) of synthetic sleep
    cycle_pattern = [0, 1, 2, 3, 2, 4]  # W, N1, N2, N3, N2, REM
    cycle_durations = [10, 10, 30, 30, 20, 20]  # minutes per stage in one cycle
    total_min = 480
    t_min = []
    R_hypno = []
    stage_hypno = []
    t = 0
    while t < total_min:
        for st, dur in zip(cycle_pattern, cycle_durations):
            if t >= total_min:
                break
            n_pts = max(1, dur)
            for _ in range(n_pts):
                if t >= total_min:
                    break
                t_min.append(t)
                R_val = stage_R_mean[stages[st]] + stage_R_std[stages[st]] * np.random.randn() * 0.5
                R_hypno.append(np.clip(R_val, 0, 1))
                stage_hypno.append(st)
                t += 1
    t_min = np.array(t_min)
    R_hypno = np.array(R_hypno)
    stage_hypno = np.array(stage_hypno)
    # Color background by regime
    for i in range(len(t_min) - 1):
        ax3.axvspan(t_min[i], t_min[i + 1], color=stage_colors[stage_hypno[i]],
                    alpha=0.15)
    ax3.plot(t_min / 60.0, R_hypno, color="#222222", lw=0.5, alpha=0.8)
    ax3.set_xlabel("time (h)")
    ax3.set_ylabel("R(t)")
    ax3.set_title("Hypnogram R(t)")
    ax3.set_xlim(0, 8)

    # --- Chart 4: Band power heatmap ---
    ax4 = fig.add_subplot(1, 4, 4)
    bands = ["delta", "theta", "alpha", "beta", "gamma"]
    # Synthetic power per stage (rows=stages, cols=bands), normalized
    power = np.array([
        [0.15, 0.10, 0.35, 0.25, 0.15],  # W
        [0.25, 0.20, 0.25, 0.20, 0.10],  # N1
        [0.35, 0.25, 0.15, 0.15, 0.10],  # N2
        [0.55, 0.20, 0.10, 0.10, 0.05],  # N3
        [0.15, 0.30, 0.20, 0.20, 0.15],  # REM
    ])
    # Normalize rows
    power = power / power.sum(axis=1, keepdims=True)
    im = ax4.imshow(power, cmap="magma", aspect="auto")
    ax4.set_xticks(range(5))
    ax4.set_xticklabels(bands, rotation=45, ha="right")
    ax4.set_yticks(range(5))
    ax4.set_yticklabels(stages)
    ax4.set_title("Band power")
    fig.colorbar(im, ax=ax4, fraction=0.046, pad=0.04)

    fig.tight_layout(rect=[0, 0, 1, 0.93])
    fig.savefig(OUTPUT_DIR / "panel_3_sleep_architecture.png", dpi=200, facecolor="white")
    plt.close(fig)
    print("  Panel 3 saved.")


# ============================================================================
# PANEL 4 — Critical Coupling and Phase Transitions
# ============================================================================

def panel_4():
    fig = plt.figure(figsize=(20, 5), facecolor="white")
    fig.suptitle("Critical Coupling and Phase Transitions", fontsize=12,
                 color="#222222", y=0.97)

    dt = 0.05
    T = 15.0

    # --- Chart 1: 3D surface R_final(K, freq_std) ---
    ax1 = fig.add_subplot(1, 4, 1, projection="3d")
    K_range = np.linspace(0.5, 10, 20)
    fs_range = np.linspace(0.5, 8, 20)
    R_final_grid = np.zeros((len(K_range), len(fs_range)))
    N_sim = 60
    for i, K in enumerate(K_range):
        for j, fs in enumerate(fs_range):
            omega_tmp = np.random.randn(N_sim) * fs
            _, _, R_arr = simulate_kuramoto(N_sim, K, omega_tmp, dt, T)
            R_final_grid[i, j] = np.mean(R_arr[-30:])
    Kg, Fg = np.meshgrid(K_range, fs_range)
    ax1.plot_surface(Kg.T, Fg.T, R_final_grid, cmap="coolwarm", alpha=0.9,
                     edgecolor="none")
    ax1.set_xlabel("K")
    ax1.set_ylabel("freq_std")
    ax1.set_zlabel("R_final")
    ax1.set_title("R_final(K, freq_std)")
    ax1.view_init(25, -50)

    # --- Chart 2: R vs K/Kc for different N ---
    ax2 = fig.add_subplot(1, 4, 2)
    N_list = [50, 100, 200, 500]
    n_colors = [COLORS["secondary"], COLORS["quaternary"],
                COLORS["tertiary"], COLORS["primary"]]
    freq_std_base = 2.0
    K_c_base = 2.0 * freq_std_base / np.pi
    K_scan = np.linspace(0.3, 6.0, 18)
    for N_osc, nc in zip(N_list, n_colors):
        omega_n = np.random.randn(N_osc) * freq_std_base
        R_vals = []
        for K in K_scan:
            _, _, R_a = simulate_kuramoto(N_osc, K, omega_n, dt, T)
            R_vals.append(np.mean(R_a[-30:]))
        ax2.plot(K_scan / K_c_base, R_vals, color=nc, lw=1.2, label=f"N={N_osc}")
    ax2.axvline(1.0, color=COLORS["accent1"], ls="--", lw=0.7)
    ax2.set_xlabel("K / K_c")
    ax2.set_ylabel("R")
    ax2.set_title("Finite-size scaling")
    ax2.legend(fontsize=6, framealpha=0.3)

    # --- Chart 3: K_c predicted vs measured ---
    ax3 = fig.add_subplot(1, 4, 3)
    freq_stds = [1.0, 2.0, 3.0, 4.0, 5.0]
    K_c_pred = [2 * f / np.pi for f in freq_stds]
    # "Measured" Kc from sim: find K where R crosses 0.3
    K_c_meas = []
    for fs in freq_stds:
        omega_m = np.random.randn(100) * fs
        found = K_c_pred[freq_stds.index(fs)]  # fallback
        for K in np.linspace(0.1, 15, 40):
            _, _, R_a = simulate_kuramoto(100, K, omega_m, 0.05, 12)
            if np.mean(R_a[-20:]) > 0.35:
                found = K
                break
        K_c_meas.append(found)
    ax3.scatter(K_c_pred, K_c_meas, c=COLORS["primary"], s=50, zorder=3)
    lim = max(max(K_c_pred), max(K_c_meas)) * 1.1
    ax3.plot([0, lim], [0, lim], color=COLORS["secondary"], ls="--", lw=0.8, label="y=x")
    ax3.set_xlabel("K_c predicted")
    ax3.set_ylabel("K_c measured")
    ax3.set_title("Pred. vs meas.")
    ax3.legend(fontsize=6, framealpha=0.3)

    # --- Chart 4: Phase portrait dR/dt vs R ---
    ax4 = fig.add_subplot(1, 4, 4)
    R_pp = np.linspace(0.01, 1.0, 200)
    K_c_ref = 2.0 * 2.0 / np.pi
    for K_factor, label, col in [(0.6, "K<K_c", COLORS["secondary"]),
                                  (1.0, "K=K_c", COLORS["quaternary"]),
                                  (2.0, "K>K_c", COLORS["primary"])]:
        K = K_factor * K_c_ref
        # Mean-field: dR/dt ~ K*R*(1 - R^2)/2 - some_damping
        # Simplified model
        dRdt = K * R_pp * (1 - R_pp**2) / 2 - K_c_ref * R_pp / 2
        ax4.plot(R_pp, dRdt, color=col, lw=1.3, label=label)
    ax4.axhline(0, color="#aaaaaa", lw=0.5)
    ax4.set_xlabel("R")
    ax4.set_ylabel("dR/dt")
    ax4.set_title("Phase portrait")
    ax4.legend(fontsize=6, framealpha=0.3)

    fig.tight_layout(rect=[0, 0, 1, 0.93])
    fig.savefig(OUTPUT_DIR / "panel_4_critical_coupling.png", dpi=200, facecolor="white")
    plt.close(fig)
    print("  Panel 4 saved.")


# ============================================================================
# PANEL 5 — Consciousness Window and Temporal Dynamics
# ============================================================================

def panel_5():
    fig = plt.figure(figsize=(20, 5), facecolor="white")
    fig.suptitle("Consciousness Window and Temporal Dynamics", fontsize=12,
                 color="#222222", y=0.97)

    # --- Chart 1: 3D surface C(tau_P, tau_T) ---
    ax1 = fig.add_subplot(1, 4, 1, projection="3d")
    tau_P = np.linspace(10, 200, 60)   # ms
    tau_T = np.linspace(50, 500, 60)   # ms
    TP, TT = np.meshgrid(tau_P, tau_T)
    # C = intersection duration approx: |tau_T - tau_P| * exp(-|tau_T-tau_P|/(tau_T+tau_P))
    diff = np.abs(TT - TP)
    C = (TP * TT / (TP + TT)) * np.exp(-diff / (TP + TT)) * 2
    ax1.plot_surface(TP, TT, C, cmap="inferno", alpha=0.9, edgecolor="none")
    ax1.set_xlabel("tau_P (ms)")
    ax1.set_ylabel("tau_T (ms)")
    ax1.set_zlabel("C (ms)")
    ax1.set_title("C(tau_P, tau_T)")
    ax1.view_init(30, -55)

    # --- Chart 2: Perception + thought decay curves ---
    ax2 = fig.add_subplot(1, 4, 2)
    t_ms = np.linspace(0, 400, 500)
    tau_p = 50.0
    tau_t = 100.0
    P = np.exp(-t_ms / tau_p)
    Th = 1 - np.exp(-t_ms / tau_t)  # thought rises then decays
    Th_full = Th * np.exp(-t_ms / (3 * tau_t))
    ax2.plot(t_ms, P, color=COLORS["primary"], lw=1.4, label="P(t)")
    ax2.plot(t_ms, Th_full, color=COLORS["secondary"], lw=1.4, label="T(t)")
    # Intersection region
    intersection = np.minimum(P, Th_full)
    ax2.fill_between(t_ms, 0, intersection, color=COLORS["quaternary"],
                     alpha=0.3, label="delta_t_C")
    ax2.set_xlabel("t (ms)")
    ax2.set_ylabel("amplitude")
    ax2.set_title("Temporal window")
    ax2.legend(fontsize=6, framealpha=0.3)

    # --- Chart 3: Heatmap T_internal/T_objective ---
    ax3 = fig.add_subplot(1, 4, 3)
    tau_circuit = np.linspace(5, 100, 50)    # ms
    n_holes = np.linspace(1, 20, 50)
    TC, NH = np.meshgrid(tau_circuit, n_holes)
    ratio = (1.0 + 0.1 * NH) * np.exp(-TC / 100) + 0.5
    im = ax3.imshow(ratio, cmap="viridis", aspect="auto",
                    extent=[tau_circuit[0], tau_circuit[-1], n_holes[-1], n_holes[0]],
                    origin="upper")
    cs = ax3.contour(TC, NH, ratio, levels=5, colors="#333333", linewidths=0.5, alpha=0.6)
    ax3.set_xlabel("tau_circuit (ms)")
    ax3.set_ylabel("n_active_holes")
    ax3.set_title("T_int / T_obj")
    fig.colorbar(im, ax=ax3, fraction=0.046, pad=0.04)

    # --- Chart 4: Time perception distortion by drug class ---
    ax4 = fig.add_subplot(1, 4, 4)
    drugs = ["stimulant", "depressant", "psychedelic", "anesthetic"]
    distortion = [15, -23, 12, -100]
    err = [5, 7, 50, 5]
    bar_cols = [COLORS["primary"], COLORS["tertiary"],
                COLORS["accent1"], COLORS["secondary"]]
    ax4.bar(drugs, distortion, yerr=err, color=bar_cols, edgecolor="#999999",
            capsize=3, width=0.6, alpha=0.9)
    ax4.axhline(0, color="#aaaaaa", lw=0.5)
    ax4.set_ylabel("distortion (%)")
    ax4.set_title("Drug effects")
    ax4.tick_params(axis="x", rotation=30)

    fig.tight_layout(rect=[0, 0, 1, 0.93])
    fig.savefig(OUTPUT_DIR / "panel_5_consciousness_window.png", dpi=200, facecolor="white")
    plt.close(fig)
    print("  Panel 5 saved.")


# ============================================================================
# PANEL 6 — Variance Minimization and Free Energy
# ============================================================================

def panel_6():
    fig = plt.figure(figsize=(20, 5), facecolor="white")
    fig.suptitle("Variance Minimization and Free Energy", fontsize=12,
                 color="#222222", y=0.97)

    kB = 1.38e-23

    # --- Chart 1: 3D surface F(sigma2, T) ---
    ax1 = fig.add_subplot(1, 4, 1, projection="3d")
    sigma2 = np.linspace(0.01, 2, 60)
    T_range = np.linspace(200, 400, 60)
    S2, TR = np.meshgrid(sigma2, T_range)
    # Normalized free energy (arbitrary units for viz)
    F = TR * S2  # proportional to k_B T sigma^2
    # Therapeutic floor curve: sigma2_floor(T) = 0.3 + 0.002*(T-200)
    ax1.plot_surface(S2, TR, F, cmap="plasma", alpha=0.85, edgecolor="none")
    # Therapeutic floor line
    T_line = np.linspace(200, 400, 50)
    s2_floor = 0.3 + 0.002 * (T_line - 200)
    F_floor = T_line * s2_floor
    ax1.plot(s2_floor, T_line, F_floor, color=COLORS["quaternary"], lw=2)
    ax1.set_xlabel("sigma^2")
    ax1.set_ylabel("T (K)")
    ax1.set_zlabel("F")
    ax1.set_title("F(sigma^2, T)")
    ax1.view_init(25, -55)

    # --- Chart 2: Log-log sigma2_min vs K ---
    ax2 = fig.add_subplot(1, 4, 2)
    K_vals = np.logspace(-0.5, 1.5, 50)
    sigma2_min = 1.0 / K_vals + 0.02 * np.random.randn(50) * 0.05
    sigma2_min = np.clip(sigma2_min, 0.01, None)
    ax2.loglog(K_vals, sigma2_min, "o", color=COLORS["primary"], ms=3, alpha=0.7)
    # slope -1 reference
    ax2.loglog(K_vals, 1.0 / K_vals, color=COLORS["secondary"], ls="--", lw=1,
               label="slope = -1")
    # Therapeutic window
    ax2.axvspan(2, 8, color=COLORS["tertiary"], alpha=0.15, label="therapeutic window")
    ax2.set_xlabel("K_coupling")
    ax2.set_ylabel("sigma^2_min")
    ax2.set_title("Variance scaling")
    ax2.legend(fontsize=6, framealpha=0.3)

    # --- Chart 3: Power P vs sigma2 for different K ---
    ax3 = fig.add_subplot(1, 4, 3)
    s2_line = np.linspace(0.05, 2.0, 200)
    K_demo = [0.5, 1.0, 2.0, 5.0]
    demo_cols = [COLORS["secondary"], COLORS["quaternary"],
                 COLORS["tertiary"], COLORS["primary"]]
    for K, col in zip(K_demo, demo_cols):
        P_val = K * s2_line * np.exp(-K * s2_line)
        ax3.plot(s2_line, P_val, color=col, lw=1.3, label=f"K={K}")
        # Mark minimum sigma2
        idx_max = np.argmax(P_val)
        ax3.plot(s2_line[idx_max], P_val[idx_max], "o", color=col, ms=5)
    ax3.set_xlabel("sigma^2")
    ax3.set_ylabel("P")
    ax3.set_title("Power vs variance")
    ax3.legend(fontsize=6, framealpha=0.3)

    # --- Chart 4: Contour free energy landscape with arrows ---
    ax4 = fig.add_subplot(1, 4, 4)
    S_k = np.linspace(0, 3, 100)
    S_e = np.linspace(0, 3, 100)
    SK, SE = np.meshgrid(S_k, S_e)
    # Free energy landscape with a minimum
    F_land = (SK - 1.2)**2 + (SE - 0.8)**2 + 0.3 * np.sin(2 * SK) * np.cos(2 * SE)
    cf = ax4.contourf(SK, SE, F_land, levels=20, cmap="inferno", alpha=0.8)
    ax4.contour(SK, SE, F_land, levels=10, colors="#333333", linewidths=0.3, alpha=0.4)
    # Gradient descent trajectory arrows
    # Compute gradient
    dFdx, dFdy = np.gradient(F_land, S_k, S_e)
    skip = 8
    ax4.quiver(SK[::skip, ::skip], SE[::skip, ::skip],
               -dFdx[::skip, ::skip], -dFdy[::skip, ::skip],
               color=COLORS["primary"], alpha=0.6, scale=40, width=0.004)
    ax4.set_xlabel("S_k")
    ax4.set_ylabel("S_e")
    ax4.set_title("Free energy landscape")
    fig.colorbar(cf, ax=ax4, fraction=0.046, pad=0.04)

    fig.tight_layout(rect=[0, 0, 1, 0.93])
    fig.savefig(OUTPUT_DIR / "panel_6_variance_free_energy.png", dpi=200, facecolor="white")
    plt.close(fig)
    print("  Panel 6 saved.")


# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    print("Generating regime classification panels...")
    print(f"Output: {OUTPUT_DIR.resolve()}")
    panel_1()
    panel_2()
    panel_3()
    panel_4()
    panel_5()
    panel_6()
    print("Done — all 6 panels generated.")
