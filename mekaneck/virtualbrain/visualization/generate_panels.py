#!/usr/bin/env python3
"""
Generate 6 panel figures for the Virtual Brain Computing Framework.

Each panel contains 4 charts with minimal text and at least one 3D visualization.

Panels:
1. Kuramoto Dynamics
2. Computational Methods
3. Consciousness Equations of State
4. Thought Geometry
5. Phase Coherence
6. Memory
"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
from matplotlib.colors import Normalize
from pathlib import Path
import warnings

warnings.filterwarnings("ignore")

# Set style
plt.style.use("dark_background")
plt.rcParams["font.family"] = "monospace"
plt.rcParams["font.size"] = 8
plt.rcParams["axes.labelsize"] = 9
plt.rcParams["axes.titlesize"] = 10
plt.rcParams["figure.facecolor"] = "#0a0a0a"
plt.rcParams["axes.facecolor"] = "#0a0a0a"
plt.rcParams["axes.edgecolor"] = "#333333"
plt.rcParams["axes.grid"] = True
plt.rcParams["grid.alpha"] = 0.3
plt.rcParams["grid.color"] = "#333333"

# Color palette
COLORS = {
    "primary": "#00d4ff",
    "secondary": "#ff6b6b",
    "tertiary": "#4ecdc4",
    "quaternary": "#ffe66d",
    "accent1": "#c792ea",
    "accent2": "#82aaff",
    "gradient_start": "#667eea",
    "gradient_end": "#764ba2",
}


def create_output_dir():
    """Create output directory for figures."""
    output_dir = Path("results/visualizations")
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


# ============================================================================
# PANEL 1: KURAMOTO DYNAMICS
# ============================================================================

def generate_kuramoto_panel(output_dir: Path):
    """Generate Kuramoto dynamics panel with 4 charts."""
    fig = plt.figure(figsize=(16, 12))
    fig.suptitle("KURAMOTO DYNAMICS", fontsize=14, color=COLORS["primary"], y=0.98)

    # Simulate Kuramoto dynamics
    N = 50  # Number of oscillators
    K_values = [0.5, 1.0, 2.0, 4.0]
    dt = 0.01
    T = 20
    t = np.arange(0, T, dt)

    # Natural frequencies (Lorentzian distribution)
    np.random.seed(42)
    omega = np.random.standard_cauchy(N) * 0.5 + 10

    def simulate_kuramoto(K, phases_init):
        phases = phases_init.copy()
        R_history = []
        phase_history = []

        for _ in t:
            # Compute order parameter
            z = np.mean(np.exp(1j * phases))
            R = np.abs(z)
            Psi = np.angle(z)
            R_history.append(R)
            phase_history.append(phases.copy())

            # Kuramoto update
            coupling = (K / N) * np.sum(np.sin(phases[:, np.newaxis] - phases), axis=0)
            phases = np.mod(phases + (omega - coupling) * dt, 2 * np.pi)

        return np.array(R_history), np.array(phase_history)

    phases_init = np.random.uniform(0, 2 * np.pi, N)

    # Chart 1: 3D Phase Evolution Surface
    ax1 = fig.add_subplot(2, 2, 1, projection="3d")
    R_hist, phase_hist = simulate_kuramoto(2.0, phases_init)

    # Sample oscillators and time for surface
    osc_idx = np.linspace(0, N - 1, 20).astype(int)
    t_idx = np.linspace(0, len(t) - 1, 100).astype(int)

    T_mesh, O_mesh = np.meshgrid(t[t_idx], osc_idx)
    Z = phase_hist[t_idx, :][:, osc_idx].T

    surf = ax1.plot_surface(T_mesh, O_mesh, Z, cmap="twilight", alpha=0.8,
                            linewidth=0, antialiased=True)
    ax1.set_xlabel("Time", labelpad=5)
    ax1.set_ylabel("Oscillator", labelpad=5)
    ax1.set_zlabel("Phase", labelpad=5)
    ax1.view_init(elev=25, azim=45)
    ax1.set_box_aspect([2, 1, 1])

    # Chart 2: Order Parameter vs Coupling Strength
    ax2 = fig.add_subplot(2, 2, 2)
    K_range = np.linspace(0.1, 5, 30)
    final_R = []

    for K in K_range:
        R_hist, _ = simulate_kuramoto(K, phases_init)
        final_R.append(np.mean(R_hist[-200:]))

    ax2.fill_between(K_range, 0, final_R, alpha=0.3, color=COLORS["primary"])
    ax2.plot(K_range, final_R, color=COLORS["primary"], linewidth=2)
    ax2.axhline(y=0.5, color=COLORS["secondary"], linestyle="--", alpha=0.5)
    ax2.axvline(x=2.0, color=COLORS["tertiary"], linestyle=":", alpha=0.5)
    ax2.set_xlabel("Coupling Strength K")
    ax2.set_ylabel("Order Parameter R")
    ax2.set_xlim(0, 5)
    ax2.set_ylim(0, 1)

    # Chart 3: Phase Space Trajectories
    ax3 = fig.add_subplot(2, 2, 3, projection="polar")
    R_hist, phase_hist = simulate_kuramoto(2.5, phases_init)

    for i in range(0, N, 5):
        phases_i = phase_hist[::50, i]
        r_vals = np.linspace(0.5, 1.0, len(phases_i))
        ax3.scatter(phases_i, r_vals, c=np.arange(len(phases_i)),
                   cmap="plasma", s=2, alpha=0.6)

    # Mean phase trajectory
    mean_phases = np.angle(np.mean(np.exp(1j * phase_hist), axis=1))
    ax3.plot(mean_phases[::10], R_hist[::10], color=COLORS["quaternary"],
             linewidth=2, alpha=0.8)
    ax3.set_ylim(0, 1)

    # Chart 4: Synchronization Time Series
    ax4 = fig.add_subplot(2, 2, 4)
    colors = [COLORS["primary"], COLORS["secondary"], COLORS["tertiary"], COLORS["quaternary"]]

    for i, K in enumerate([0.5, 1.5, 2.5, 4.0]):
        R_hist, _ = simulate_kuramoto(K, phases_init)
        ax4.plot(t[::10], R_hist[::10], color=colors[i], linewidth=1.5,
                alpha=0.8, label=f"K={K}")

    ax4.set_xlabel("Time")
    ax4.set_ylabel("R(t)")
    ax4.set_xlim(0, T)
    ax4.set_ylim(0, 1)
    ax4.legend(loc="lower right", fontsize=7, framealpha=0.3)

    plt.tight_layout()
    fig.savefig(output_dir / "panel_1_kuramoto_dynamics.png", dpi=300,
                facecolor=fig.get_facecolor(), edgecolor="none", bbox_inches="tight")
    plt.close(fig)
    print("[OK] Panel 1: Kuramoto Dynamics")


# ============================================================================
# PANEL 2: COMPUTATIONAL METHODS
# ============================================================================

def generate_computational_panel(output_dir: Path):
    """Generate computational methods panel with 4 charts."""
    fig = plt.figure(figsize=(16, 12))
    fig.suptitle("COMPUTATIONAL METHODS", fontsize=14, color=COLORS["secondary"], y=0.98)

    # Chart 1: 3D Ternary Trisection Tree
    ax1 = fig.add_subplot(2, 2, 1, projection="3d")

    def plot_ternary_tree(ax, x, y, z, depth, max_depth):
        if depth >= max_depth:
            return

        # Three children
        dx = 0.5 ** depth
        dz = 1.0 / max_depth

        for i, offset in enumerate([-dx, 0, dx]):
            new_x = x + offset * 0.5
            new_y = y + depth * 0.1
            new_z = z - dz

            # Draw connection
            ax.plot([x, new_x], [y, new_y], [z, new_z],
                   color=cm.viridis(depth / max_depth), linewidth=2 - depth * 0.3, alpha=0.7)

            # Draw node
            ax.scatter([new_x], [new_y], [new_z], s=50 - depth * 8,
                      c=[cm.viridis(depth / max_depth)], alpha=0.8)

            plot_ternary_tree(ax, new_x, new_y, new_z, depth + 1, max_depth)

    ax1.scatter([0], [0], [1], s=100, c=[COLORS["primary"]], alpha=1)
    plot_ternary_tree(ax1, 0, 0, 1, 0, 4)
    ax1.set_xlabel("X")
    ax1.set_ylabel("Depth")
    ax1.set_zlabel("Level")
    ax1.view_init(elev=20, azim=45)
    ax1.set_box_aspect([1, 1, 1])

    # Chart 2: O(log₃ n) vs O(log₂ n) Complexity
    ax2 = fig.add_subplot(2, 2, 2)
    n = np.logspace(1, 8, 100)
    log2_n = np.log2(n)
    log3_n = np.log(n) / np.log(3)

    ax2.fill_between(n, log3_n, log2_n, alpha=0.3, color=COLORS["tertiary"],
                     label="Ternary Advantage")
    ax2.loglog(n, log2_n, color=COLORS["secondary"], linewidth=2, label="Binary O(log₂n)")
    ax2.loglog(n, log3_n, color=COLORS["primary"], linewidth=2, label="Ternary O(log₃n)")
    ax2.set_xlabel("State Space Size n")
    ax2.set_ylabel("Operations")
    ax2.legend(loc="upper left", fontsize=7, framealpha=0.3)

    # Chart 3: Poincaré Recurrence Basin
    ax3 = fig.add_subplot(2, 2, 3)
    theta = np.linspace(0, 2 * np.pi, 100)

    for r in np.linspace(0.2, 1.0, 5):
        x = r * np.cos(theta)
        y = r * np.sin(theta)
        ax3.plot(x, y, color=cm.plasma(r), linewidth=1, alpha=0.6)

    # Trajectory spiraling to attractor
    t_traj = np.linspace(0, 10 * np.pi, 500)
    r_traj = 1.0 * np.exp(-t_traj / 20)
    x_traj = r_traj * np.cos(t_traj)
    y_traj = r_traj * np.sin(t_traj)
    ax3.scatter(x_traj, y_traj, c=np.arange(len(t_traj)), cmap="viridis", s=2, alpha=0.8)
    ax3.scatter([0], [0], s=100, c=[COLORS["quaternary"]], marker="*", zorder=5)
    ax3.set_xlim(-1.2, 1.2)
    ax3.set_ylim(-1.2, 1.2)
    ax3.set_aspect("equal")
    ax3.set_xlabel("x")
    ax3.set_ylabel("y")

    # Chart 4: Constraint Satisfaction Convergence
    ax4 = fig.add_subplot(2, 2, 4)
    iterations = np.arange(0, 100)
    constraints = [
        np.exp(-iterations / 20) * np.sin(iterations / 5) * 0.5 + np.exp(-iterations / 15),
        np.exp(-iterations / 15) * 0.8,
        np.exp(-iterations / 25) * np.cos(iterations / 8) * 0.3 + np.exp(-iterations / 20),
    ]

    colors = [COLORS["primary"], COLORS["secondary"], COLORS["tertiary"]]
    labels = ["C₁", "C₂", "C₃"]
    for i, (c, col, lab) in enumerate(zip(constraints, colors, labels)):
        ax4.plot(iterations, c, color=col, linewidth=2, alpha=0.8, label=lab)

    ax4.axhline(y=0.01, color=COLORS["quaternary"], linestyle="--", alpha=0.5)
    ax4.fill_between(iterations, 0, 0.01, alpha=0.2, color=COLORS["quaternary"])
    ax4.set_xlabel("Iteration")
    ax4.set_ylabel("Constraint Violation")
    ax4.set_yscale("log")
    ax4.set_ylim(1e-3, 2)
    ax4.legend(loc="upper right", fontsize=7, framealpha=0.3)

    plt.tight_layout()
    fig.savefig(output_dir / "panel_2_computational_methods.png", dpi=300,
                facecolor=fig.get_facecolor(), edgecolor="none", bbox_inches="tight")
    plt.close(fig)
    print("[OK] Panel 2: Computational Methods")


# ============================================================================
# PANEL 3: CONSCIOUSNESS EQUATIONS OF STATE
# ============================================================================

def generate_consciousness_panel(output_dir: Path):
    """Generate consciousness equations panel with 4 charts."""
    fig = plt.figure(figsize=(16, 12))
    fig.suptitle("CONSCIOUSNESS EQUATIONS OF STATE", fontsize=14, color=COLORS["tertiary"], y=0.98)

    # Chart 1: 3D Consciousness Surface C = P × T × γ × γ_f
    ax1 = fig.add_subplot(2, 2, 1, projection="3d")

    P = np.linspace(0, 1, 50)
    T = np.linspace(0, 1, 50)
    P_mesh, T_mesh = np.meshgrid(P, T)

    # C = P_decay × T_decay (with fixed gamma = 0.8)
    gamma = 0.8
    gamma_f = 0.9
    C = P_mesh * T_mesh * gamma * gamma_f

    surf = ax1.plot_surface(P_mesh, T_mesh, C, cmap="plasma", alpha=0.85,
                            linewidth=0, antialiased=True)
    ax1.set_xlabel("P_decay", labelpad=5)
    ax1.set_ylabel("T_decay", labelpad=5)
    ax1.set_zlabel("C", labelpad=5)
    ax1.view_init(elev=25, azim=135)

    # Chart 2: Decay Curve Intersection
    ax2 = fig.add_subplot(2, 2, 2)
    t = np.linspace(0, 5, 200)
    tau_p = 0.5
    tau_t = 1.0

    P_decay = np.exp(-t / tau_p)
    T_decay = 0.3 + 0.7 * np.exp(-t / tau_t)
    C_intersection = P_decay * T_decay

    ax2.fill_between(t, 0, np.minimum(P_decay, T_decay), alpha=0.3, color=COLORS["quaternary"])
    ax2.plot(t, P_decay, color=COLORS["primary"], linewidth=2, label="P_decay")
    ax2.plot(t, T_decay, color=COLORS["secondary"], linewidth=2, label="T_decay")
    ax2.plot(t, C_intersection, color=COLORS["quaternary"], linewidth=2.5,
             linestyle="--", label="C = P ∩ T")
    ax2.set_xlabel("Time")
    ax2.set_ylabel("Level")
    ax2.set_xlim(0, 5)
    ax2.set_ylim(0, 1.1)
    ax2.legend(loc="upper right", fontsize=7, framealpha=0.3)

    # Chart 3: Frequency Hierarchy
    ax3 = fig.add_subplot(2, 2, 3)
    frequencies = [4.06e13, 1e10, 10, 2.5]
    labels = ["H⁺ (Reality)", "Molecular", "Thought", "Consciousness"]
    colors = [COLORS["secondary"], COLORS["tertiary"], COLORS["primary"], COLORS["quaternary"]]

    y_pos = np.arange(len(frequencies))
    bars = ax3.barh(y_pos, np.log10(frequencies), color=colors, alpha=0.8, height=0.6)

    ax3.set_yticks(y_pos)
    ax3.set_yticklabels(labels)
    ax3.set_xlabel("log₁₀(Frequency / Hz)")
    ax3.set_xlim(0, 15)

    # Add frequency annotations
    for i, (bar, freq) in enumerate(zip(bars, frequencies)):
        ax3.text(bar.get_width() + 0.2, bar.get_y() + bar.get_height() / 2,
                f"{freq:.0e}" if freq > 100 else f"{freq:.1f}",
                va="center", fontsize=7, color=colors[i])

    # Chart 4: Wake/Dream State Diagram
    ax4 = fig.add_subplot(2, 2, 4)

    # Simulate wake-sleep-wake cycle
    t = np.linspace(0, 24, 500)
    # P_decay oscillates (awake during day)
    P = 0.5 + 0.5 * np.cos(2 * np.pi * (t - 6) / 24)
    P = np.clip(P, 0, 1)

    # T_decay also varies
    T = 0.6 + 0.3 * np.sin(2 * np.pi * t / 8) + 0.1 * np.random.randn(len(t))
    T = np.clip(T, 0.3, 1)

    C = P * T * 0.8

    # Color by state
    wake_mask = P > 0.5
    dream_mask = (P < 0.3) & (T > 0.5)

    ax4.fill_between(t, 0, C, where=wake_mask, alpha=0.4, color=COLORS["primary"], label="Awake")
    ax4.fill_between(t, 0, C, where=dream_mask, alpha=0.4, color=COLORS["accent1"], label="Dream")
    ax4.fill_between(t, 0, C, where=~(wake_mask | dream_mask), alpha=0.2, color="gray")
    ax4.plot(t, C, color="white", linewidth=1, alpha=0.8)
    ax4.plot(t, P, color=COLORS["primary"], linewidth=1, linestyle=":", alpha=0.5)

    ax4.set_xlabel("Time (hours)")
    ax4.set_ylabel("C")
    ax4.set_xlim(0, 24)
    ax4.set_ylim(0, 1)
    ax4.legend(loc="upper right", fontsize=7, framealpha=0.3)

    plt.tight_layout()
    fig.savefig(output_dir / "panel_3_consciousness_equations.png", dpi=300,
                facecolor=fig.get_facecolor(), edgecolor="none", bbox_inches="tight")
    plt.close(fig)
    print("[OK] Panel 3: Consciousness Equations of State")


# ============================================================================
# PANEL 4: THOUGHT GEOMETRY
# ============================================================================

def generate_thought_geometry_panel(output_dir: Path):
    """Generate thought geometry panel with 4 charts."""
    fig = plt.figure(figsize=(16, 12))
    fig.suptitle("THOUGHT GEOMETRY", fontsize=14, color=COLORS["quaternary"], y=0.98)

    # Chart 1: 3D O₂ Molecular Configuration Space
    ax1 = fig.add_subplot(2, 2, 1, projection="3d")

    # Generate O2 molecular positions around oscillatory hole
    np.random.seed(42)
    n_molecules = 50
    theta = np.random.uniform(0, 2 * np.pi, n_molecules)
    phi = np.random.uniform(0, np.pi, n_molecules)
    r = 0.374 + 0.081 * np.random.randn(n_molecules)  # Mean O2-hole distance

    x = r * np.sin(phi) * np.cos(theta)
    y = r * np.sin(phi) * np.sin(theta)
    z = r * np.cos(phi)

    # O2 molecules
    ax1.scatter(x, y, z, c=r, cmap="coolwarm", s=40, alpha=0.7)

    # Central hole
    ax1.scatter([0], [0], [0], s=200, c=[COLORS["quaternary"]], marker="o", alpha=0.9)

    # Electron position
    e_pos = np.array([0.147, 0.05, 0.02])
    ax1.scatter([e_pos[0]], [e_pos[1]], [e_pos[2]], s=100, c=[COLORS["primary"]],
               marker="^", alpha=0.9)

    # Draw connection
    ax1.plot([0, e_pos[0]], [0, e_pos[1]], [0, e_pos[2]], color=COLORS["primary"],
            linewidth=2, alpha=0.5)

    ax1.set_xlabel("x (Å)")
    ax1.set_ylabel("y (Å)")
    ax1.set_zlabel("z (Å)")
    ax1.set_box_aspect([1, 1, 1])

    # Chart 2: Partition Capacity C(n) = 2n²
    ax2 = fig.add_subplot(2, 2, 2)
    n_vals = np.arange(1, 11)
    capacity = 2 * n_vals ** 2
    cumulative = np.cumsum(capacity)

    ax2.bar(n_vals - 0.2, capacity, width=0.4, color=COLORS["primary"], alpha=0.8, label="C(n)")
    ax2.bar(n_vals + 0.2, cumulative, width=0.4, color=COLORS["tertiary"], alpha=0.8, label="Σ C(n)")

    ax2.set_xlabel("n (partition level)")
    ax2.set_ylabel("States")
    ax2.set_xticks(n_vals)
    ax2.legend(loc="upper left", fontsize=7, framealpha=0.3)

    # Chart 3: S-Entropy Space [0,1]³
    ax3 = fig.add_subplot(2, 2, 3, projection="3d")

    # Draw unit cube edges
    edges = [
        ([0, 1], [0, 0], [0, 0]), ([0, 1], [1, 1], [0, 0]),
        ([0, 1], [0, 0], [1, 1]), ([0, 1], [1, 1], [1, 1]),
        ([0, 0], [0, 1], [0, 0]), ([1, 1], [0, 1], [0, 0]),
        ([0, 0], [0, 1], [1, 1]), ([1, 1], [0, 1], [1, 1]),
        ([0, 0], [0, 0], [0, 1]), ([1, 1], [0, 0], [0, 1]),
        ([0, 0], [1, 1], [0, 1]), ([1, 1], [1, 1], [0, 1]),
    ]
    for e in edges:
        ax3.plot(e[0], e[1], e[2], color="gray", linewidth=0.5, alpha=0.5)

    # Sample points in S-space (trajectory)
    t_traj = np.linspace(0, 1, 100)
    sk = 0.3 + 0.5 * t_traj + 0.1 * np.sin(10 * t_traj)
    st = 0.2 + 0.6 * t_traj ** 0.5
    se = 0.5 + 0.3 * np.sin(5 * t_traj)

    sk = np.clip(sk, 0, 1)
    st = np.clip(st, 0, 1)
    se = np.clip(se, 0, 1)

    ax3.scatter(sk, st, se, c=t_traj, cmap="viridis", s=15, alpha=0.8)
    ax3.plot(sk, st, se, color=COLORS["primary"], linewidth=1, alpha=0.5)

    # Start and end points
    ax3.scatter([sk[0]], [st[0]], [se[0]], s=100, c=[COLORS["tertiary"]], marker="o")
    ax3.scatter([sk[-1]], [st[-1]], [se[-1]], s=100, c=[COLORS["secondary"]], marker="*")

    ax3.set_xlabel("Sₖ")
    ax3.set_ylabel("Sₜ")
    ax3.set_zlabel("Sₑ")
    ax3.set_xlim(0, 1)
    ax3.set_ylim(0, 1)
    ax3.set_zlim(0, 1)

    # Chart 4: Oscillatory Signature (30D projected to 2D)
    ax4 = fig.add_subplot(2, 2, 4)

    # Generate 30D signature and project via PCA-like method
    np.random.seed(123)
    n_signatures = 5
    dim = 30
    t_sig = np.linspace(0, 2 * np.pi, 100)

    for i in range(n_signatures):
        # Random 30D signature
        signature = np.zeros((100, dim))
        for d in range(dim):
            freq = 1 + d * 0.3 + np.random.randn() * 0.1
            phase = np.random.uniform(0, 2 * np.pi)
            amplitude = np.exp(-d / 15) * (0.5 + 0.5 * np.random.rand())
            signature[:, d] = amplitude * np.sin(freq * t_sig + phase)

        # Project to 2D (first two "principal components")
        proj_x = np.sum(signature[:, :15], axis=1)
        proj_y = np.sum(signature[:, 15:], axis=1)

        color = cm.viridis(i / n_signatures)
        ax4.plot(proj_x, proj_y, color=color, linewidth=1.5, alpha=0.7)
        ax4.scatter(proj_x[0], proj_y[0], s=50, c=[color], marker="o")

    ax4.set_xlabel("Component 1")
    ax4.set_ylabel("Component 2")
    ax4.set_aspect("equal")

    plt.tight_layout()
    fig.savefig(output_dir / "panel_4_thought_geometry.png", dpi=300,
                facecolor=fig.get_facecolor(), edgecolor="none", bbox_inches="tight")
    plt.close(fig)
    print("[OK] Panel 4: Thought Geometry")


# ============================================================================
# PANEL 5: PHASE COHERENCE
# ============================================================================

def generate_phase_coherence_panel(output_dir: Path):
    """Generate phase coherence panel with 4 charts."""
    fig = plt.figure(figsize=(16, 12))
    fig.suptitle("PHASE COHERENCE", fontsize=14, color=COLORS["accent1"], y=0.98)

    # Chart 1: 3D Phase Evolution Manifold
    ax1 = fig.add_subplot(2, 2, 1, projection="3d")

    N = 20
    T = 100
    phases = np.zeros((T, N))
    phases[0] = np.random.uniform(0, 2 * np.pi, N)

    K = 2.0
    omega = np.random.normal(10, 1, N)

    for t in range(1, T):
        coupling = (K / N) * np.sum(np.sin(phases[t - 1][:, np.newaxis] - phases[t - 1]), axis=0)
        phases[t] = np.mod(phases[t - 1] + (omega - coupling) * 0.1, 2 * np.pi)

    # Plot as 3D surface
    t_mesh, n_mesh = np.meshgrid(np.arange(T), np.arange(N))
    ax1.plot_surface(t_mesh, n_mesh, phases.T, cmap="twilight_shifted",
                    alpha=0.85, linewidth=0)
    ax1.set_xlabel("Time")
    ax1.set_ylabel("Oscillator")
    ax1.set_zlabel("Phase")
    ax1.view_init(elev=30, azim=60)

    # Chart 2: Order Parameter Circle
    ax2 = fig.add_subplot(2, 2, 2, projection="polar")

    # Multiple snapshots
    snapshots = [0, 25, 50, 75, 99]
    colors_snap = cm.plasma(np.linspace(0.2, 0.8, len(snapshots)))

    for idx, (t_idx, color) in enumerate(zip(snapshots, colors_snap)):
        phase_t = phases[t_idx]
        z = np.mean(np.exp(1j * phase_t))
        R = np.abs(z)
        Psi = np.angle(z)

        # Individual oscillators
        ax2.scatter(phase_t, np.ones(N) * (0.5 + idx * 0.1), s=20, c=[color], alpha=0.6)

        # Mean phase
        ax2.scatter([Psi], [R], s=100, c=[color], marker="*", zorder=5)

    ax2.set_ylim(0, 1.2)

    # Chart 3: Phase Velocity Distribution
    ax3 = fig.add_subplot(2, 2, 3)

    # Compute phase velocities
    d_phases = np.diff(phases, axis=0)
    d_phases = np.mod(d_phases + np.pi, 2 * np.pi) - np.pi  # Wrap

    # Histogram at different times
    times_hist = [10, 30, 50, 80]
    colors_hist = [COLORS["primary"], COLORS["secondary"], COLORS["tertiary"], COLORS["quaternary"]]

    for t_idx, color in zip(times_hist, colors_hist):
        velocities = d_phases[t_idx] / 0.1
        ax3.hist(velocities, bins=20, alpha=0.5, color=color, density=True)

    ax3.set_xlabel("dφ/dt")
    ax3.set_ylabel("Density")

    # Chart 4: Critical Coupling Transition
    ax4 = fig.add_subplot(2, 2, 4)

    K_range = np.linspace(0, 4, 50)
    R_equilibrium = []

    np.random.seed(42)
    omega_fixed = np.random.normal(10, 1, 50)
    phases_init = np.random.uniform(0, 2 * np.pi, 50)

    for K in K_range:
        phases_k = phases_init.copy()
        for _ in range(200):
            coupling = (K / 50) * np.sum(np.sin(phases_k[:, np.newaxis] - phases_k), axis=0)
            phases_k = np.mod(phases_k + (omega_fixed - coupling) * 0.1, 2 * np.pi)

        z = np.mean(np.exp(1j * phases_k))
        R_equilibrium.append(np.abs(z))

    R_equilibrium = np.array(R_equilibrium)

    # Theoretical curve
    K_c = 2 * 1 / np.pi  # Critical coupling for std=1
    R_theory = np.where(K_range > K_c, np.sqrt(1 - K_c / K_range), 0)

    ax4.fill_between(K_range, 0, R_equilibrium, alpha=0.3, color=COLORS["primary"])
    ax4.plot(K_range, R_equilibrium, color=COLORS["primary"], linewidth=2, label="Simulation")
    ax4.plot(K_range, R_theory, color=COLORS["secondary"], linewidth=2,
             linestyle="--", label="Theory", alpha=0.7)
    ax4.axvline(x=K_c, color=COLORS["quaternary"], linestyle=":", alpha=0.7)
    ax4.text(K_c + 0.1, 0.9, "Kc", color=COLORS["quaternary"], fontsize=9)
    ax4.set_xlabel("Coupling K")
    ax4.set_ylabel("R∞")
    ax4.set_xlim(0, 4)
    ax4.set_ylim(0, 1)
    ax4.legend(loc="lower right", fontsize=7, framealpha=0.3)

    plt.tight_layout()
    fig.savefig(output_dir / "panel_5_phase_coherence.png", dpi=300,
                facecolor=fig.get_facecolor(), edgecolor="none", bbox_inches="tight")
    plt.close(fig)
    print("[OK] Panel 5: Phase Coherence")


# ============================================================================
# PANEL 6: MEMORY
# ============================================================================

def generate_memory_panel(output_dir: Path):
    """Generate memory panel with 4 charts."""
    fig = plt.figure(figsize=(16, 12))
    fig.suptitle("MEMORY: M = ∫(dH⁺/dt)dt", fontsize=14, color=COLORS["accent2"], y=0.98)

    # Chart 1: 3D Memory Accumulation Surface
    ax1 = fig.add_subplot(2, 2, 1, projection="3d")

    # Time and emotional field evolution
    t = np.linspace(0, 10, 100)
    H_plus = np.zeros((5, len(t)))

    # Different emotional trajectories
    for i in range(5):
        freq = 0.5 + i * 0.2
        phase = i * np.pi / 3
        H_plus[i] = np.sin(freq * t + phase) * np.exp(-t / 15) + 0.5 * (1 - np.exp(-t / 3))

    # Compute memory (cumulative integral of dH/dt)
    M = np.zeros_like(H_plus)
    dt = t[1] - t[0]
    for i in range(5):
        dH_dt = np.gradient(H_plus[i], dt)
        M[i] = np.cumsum(dH_dt) * dt

    t_mesh, traj_mesh = np.meshgrid(t, np.arange(5))
    ax1.plot_surface(t_mesh, traj_mesh, M, cmap="viridis", alpha=0.85, linewidth=0)
    ax1.set_xlabel("Time")
    ax1.set_ylabel("Trajectory")
    ax1.set_zlabel("M(t)")
    ax1.view_init(elev=25, azim=45)

    # Chart 2: Emotional Field and Memory
    ax2 = fig.add_subplot(2, 2, 2)

    t = np.linspace(0, 20, 400)
    H = np.sin(0.5 * t) * np.exp(-t / 30) + 0.5 * (1 - np.exp(-t / 5))
    H += 0.1 * np.sin(3 * t) * np.exp(-t / 10)  # High frequency component

    dt = t[1] - t[0]
    dH_dt = np.gradient(H, dt)
    M = np.cumsum(dH_dt) * dt

    ax2_twin = ax2.twinx()

    ax2.plot(t, H, color=COLORS["secondary"], linewidth=2, label="H⁺(t)")
    ax2_twin.plot(t, M, color=COLORS["primary"], linewidth=2, label="M(t)")

    ax2.set_xlabel("Time")
    ax2.set_ylabel("H⁺", color=COLORS["secondary"])
    ax2_twin.set_ylabel("M", color=COLORS["primary"])
    ax2.tick_params(axis="y", labelcolor=COLORS["secondary"])
    ax2_twin.tick_params(axis="y", labelcolor=COLORS["primary"])

    # Chart 3: Memory Retrieval
    ax3 = fig.add_subplot(2, 2, 3)

    # Current state
    t_now = 15
    H_now = H[np.argmin(np.abs(t - t_now))]
    M_now = M[np.argmin(np.abs(t - t_now))]

    # Retrieve past states
    t_past = np.array([2, 5, 8, 12])
    M_past = M[np.searchsorted(t, t_past)]
    H_retrieved = H_now - (M_now - M_past)
    H_actual = H[np.searchsorted(t, t_past)]

    ax3.scatter(t_past, H_actual, s=100, c=[COLORS["tertiary"]], marker="o", label="Actual H⁺")
    ax3.scatter(t_past, H_retrieved, s=100, c=[COLORS["quaternary"]], marker="x", label="Retrieved")

    # Connect with lines
    for tp, ha, hr in zip(t_past, H_actual, H_retrieved):
        ax3.plot([tp, tp], [ha, hr], color="white", linewidth=1, alpha=0.5)

    ax3.plot(t[:np.argmin(np.abs(t - t_now))], H[:np.argmin(np.abs(t - t_now))],
             color=COLORS["secondary"], linewidth=1, alpha=0.5)
    ax3.axvline(x=t_now, color=COLORS["primary"], linestyle="--", alpha=0.5)
    ax3.set_xlabel("Time")
    ax3.set_ylabel("H⁺")
    ax3.legend(loc="upper left", fontsize=7, framealpha=0.3)

    # Chart 4: Forgetting Dynamics
    ax4 = fig.add_subplot(2, 2, 4)

    # Memory resolution decay
    t_forget = np.linspace(0, 50, 200)
    tau_forget = 10

    # Different emotional intensities
    intensities = [0.2, 0.5, 1.0, 2.0]
    colors_int = [COLORS["primary"], COLORS["secondary"], COLORS["tertiary"], COLORS["quaternary"]]

    for intensity, color in zip(intensities, colors_int):
        # Resolution = exp(-t/tau) + |dH/dt|
        resolution = np.exp(-t_forget / tau_forget) + intensity * np.exp(-t_forget / 30)
        resolution = np.clip(resolution, 0, 1)
        ax4.plot(t_forget, resolution, color=color, linewidth=2, alpha=0.8)

    ax4.axhline(y=0.1, color="white", linestyle=":", alpha=0.3)
    ax4.fill_between(t_forget, 0, 0.1, alpha=0.2, color="white")
    ax4.set_xlabel("Time Since Event")
    ax4.set_ylabel("Memory Resolution")
    ax4.set_xlim(0, 50)
    ax4.set_ylim(0, 1.1)

    # Add legend manually
    from matplotlib.lines import Line2D
    legend_elements = [Line2D([0], [0], color=c, linewidth=2, label=f"|dH/dt|={i}")
                      for i, c in zip(intensities, colors_int)]
    ax4.legend(handles=legend_elements, loc="upper right", fontsize=7, framealpha=0.3)

    plt.tight_layout()
    fig.savefig(output_dir / "panel_6_memory.png", dpi=300,
                facecolor=fig.get_facecolor(), edgecolor="none", bbox_inches="tight")
    plt.close(fig)
    print("[OK] Panel 6: Memory")


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Generate all panel figures."""
    print("=" * 70)
    print("GENERATING VIRTUAL BRAIN PANEL FIGURES")
    print("=" * 70)

    output_dir = create_output_dir()
    print(f"Output directory: {output_dir}\n")

    generate_kuramoto_panel(output_dir)
    generate_computational_panel(output_dir)
    generate_consciousness_panel(output_dir)
    generate_thought_geometry_panel(output_dir)
    generate_phase_coherence_panel(output_dir)
    generate_memory_panel(output_dir)

    print("\n" + "=" * 70)
    print(f"All panels saved to: {output_dir}")
    print("=" * 70)


if __name__ == "__main__":
    main()
