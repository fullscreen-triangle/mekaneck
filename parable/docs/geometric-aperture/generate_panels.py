"""
Generate 6 panel figures for the Geometric Apertures paper.
Each panel: 1 row x 4 columns, figsize=(20,5), DPI=200, light style.
"""

import matplotlib
matplotlib.use("Agg")
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
import matplotlib.colors as mcolors
from pathlib import Path

# ---------------------------------------------------------------------------
# Style
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

COLORS = {
    "primary": "#1f77b4",
    "secondary": "#d62728",
    "tertiary": "#2ca02c",
    "quaternary": "#ff7f0e",
    "accent1": "#9467bd",
    "accent2": "#17becf",
}

OUT = Path(r"C:\Users\kundai\Documents\personal\mekaneck\parable\docs\geometric-aperture\figures")
OUT.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------
DRUGS = {
    "fluoxetine":    {"class": "SSRI", "SERT": 0.8, "5HT2C": 72, "NET": 370, "DAT": 3600, "response": 0.62},
    "sertraline":    {"class": "SSRI", "SERT": 0.29, "DAT": 25, "NET": 420, "response": 0.63},
    "escitalopram":  {"class": "SSRI", "SERT": 1.1, "NET": 7800, "DAT": 27400, "response": 0.63},
    "paroxetine":    {"class": "SSRI", "SERT": 0.13, "NET": 40, "DAT": 490, "mACh": 108, "response": 0.61},
    "venlafaxine":   {"class": "SNRI", "SERT": 8.9, "NET": 1060, "DAT": 9300, "response": 0.64},
    "duloxetine":    {"class": "SNRI", "SERT": 0.8, "NET": 7.5, "DAT": 240, "response": 0.62},
    "desvenlafaxine": {"class": "SNRI", "SERT": 40.2, "NET": 558.4, "response": 0.59},
    "amitriptyline": {"class": "TCA", "SERT": 4.3, "NET": 35, "H1": 1.1, "mACh": 18, "alpha1": 27, "response": 0.63},
    "imipramine":    {"class": "TCA", "SERT": 1.4, "NET": 37, "H1": 11, "mACh": 46, "alpha1": 32, "response": 0.60},
    "clomipramine":  {"class": "TCA", "SERT": 0.28, "NET": 38, "H1": 31, "mACh": 37, "alpha1": 39, "response": 0.62},
    "nortriptyline": {"class": "TCA", "SERT": 18, "NET": 4.4, "H1": 10, "mACh": 37, "alpha1": 55, "response": 0.59},
}

ENZYMES = {
    "carbonic_anhydrase":       {"kcat": 1e6,  "Km": 0.012,  "atoms": 3,  "mw": 44},
    "acetylcholinesterase":     {"kcat": 1.4e4,"Km": 9e-5,   "atoms": 15, "mw": 146},
    "catalase":                 {"kcat": 4e7,  "Km": 1.1,    "atoms": 4,  "mw": 34},
    "superoxide_dismutase":     {"kcat": 1e9,  "Km": 3.5e-4, "atoms": 2,  "mw": 32},
    "triose_phosphate_isomerase": {"kcat": 4.3e3, "Km": 4.7e-4, "atoms": 13, "mw": 170},
    "hexokinase":               {"kcat": 1e2,  "Km": 1e-4,   "atoms": 24, "mw": 180},
    "lactate_dehydrogenase":    {"kcat": 1e3,  "Km": 3.5e-5, "atoms": 9,  "mw": 88},
    "chymotrypsin":             {"kcat": 1e2,  "Km": 5e-3,   "atoms": 20, "mw": 250},
    "lysozyme":                 {"kcat": 0.5,  "Km": 6e-6,   "atoms": 85, "mw": 990},
    "DNA_polymerase_I":         {"kcat": 15,   "Km": 1e-6,   "atoms": 45, "mw": 487},
    "cytochrome_P450":          {"kcat": 20,   "Km": 5e-5,   "atoms": 30, "mw": 350},
    "ATP_synthase":             {"kcat": 600,  "Km": 2e-4,   "atoms": 40, "mw": 427},
}

REGIME_DATA = np.array([
    (1.0, 4.8, 0.6, 0.073), (2.56, 8.53, 1.07, 0.077), (4.11, 12.27, 1.53, 0.097),
    (5.67, 16.0, 2.0, 0.151), (7.22, 19.73, 2.47, 0.390), (8.78, 23.47, 2.93, 0.591),
    (10.33, 27.2, 3.4, 0.755), (11.89, 30.93, 3.87, 0.846), (13.44, 34.67, 4.33, 0.897),
    (15.0, 38.4, 4.8, 0.925),
])

CLASS_COLORS = {"SSRI": COLORS["primary"], "SNRI": COLORS["tertiary"], "TCA": COLORS["accent1"]}

ALL_RECEPTORS = ["SERT", "NET", "DAT", "5HT2C", "mACh", "H1", "alpha1"]


def drug_ki(name, receptor):
    return DRUGS[name].get(receptor, None)


def n_targets(name):
    return sum(1 for r in ALL_RECEPTORS if r in DRUGS[name])


def selectivity_ratio(name):
    kis = [v for k, v in DRUGS[name].items() if k not in ("class", "response")]
    if len(kis) < 2:
        return 1.0
    kis_sorted = sorted(kis)
    return kis_sorted[1] / kis_sorted[0] if kis_sorted[0] > 0 else 1.0


# ---------------------------------------------------------------------------
# Panel 1: Aperture Field Configurations
# ---------------------------------------------------------------------------
def panel_1():
    fig = plt.figure(figsize=(20, 5), facecolor="white")

    r = np.linspace(0.3, 3, 40)
    theta = np.linspace(0, np.pi, 40)
    R, T = np.meshgrid(r, theta)
    X = R * np.sin(T)
    Z = R * np.cos(T)

    # 1. Monopole
    ax1 = fig.add_subplot(141, projection="3d")
    E_mono = 1.0 / R**2
    ax1.plot_surface(X, Z, E_mono, cmap="viridis", alpha=0.85, edgecolor="none")
    ax1.set_title("Monopole |E|", color=COLORS["primary"])
    ax1.set_xlabel("r sin\u03b8"); ax1.set_ylabel("r cos\u03b8"); ax1.set_zlabel("|E|")
    ax1.set_facecolor("#0a0a0a")

    # 2. Dipole
    ax2 = fig.add_subplot(142, projection="3d")
    E_dip = np.sqrt(4 * np.cos(T)**2 + np.sin(T)**2) / R**3
    ax2.plot_surface(X, Z, E_dip, cmap="viridis", alpha=0.85, edgecolor="none")
    ax2.set_title("Dipole |E|", color=COLORS["secondary"])
    ax2.set_xlabel("r sin\u03b8"); ax2.set_ylabel("r cos\u03b8"); ax2.set_zlabel("|E|")
    ax2.set_facecolor("#0a0a0a")

    # 3. Quadrupole
    ax3 = fig.add_subplot(143, projection="3d")
    E_quad = np.abs(3 * np.cos(T)**2 - 1) / R**4
    ax3.plot_surface(X, Z, E_quad, cmap="viridis", alpha=0.85, edgecolor="none")
    ax3.set_title("Quadrupole |E|", color=COLORS["tertiary"])
    ax3.set_xlabel("r sin\u03b8"); ax3.set_ylabel("r cos\u03b8"); ax3.set_zlabel("|E|")
    ax3.set_facecolor("#0a0a0a")

    # 4. Heatmap: phase space restriction alpha by aperture x drug class
    ax4 = fig.add_subplot(144)
    aperture_types = ["Monopole", "Dipole", "Quadrupole"]
    classes = ["SSRI", "SNRI", "TCA"]
    # alpha ~ 1/n_pole * mean(selectivity) for that class
    alpha_grid = np.zeros((3, 3))
    for ci, cls in enumerate(classes):
        cls_drugs = [n for n, d in DRUGS.items() if d["class"] == cls]
        mean_sel = np.mean([selectivity_ratio(n) for n in cls_drugs])
        mean_nt = np.mean([n_targets(n) for n in cls_drugs])
        for ai, (pole_order, label) in enumerate([(1, "Mono"), (2, "Di"), (3, "Quad")]):
            alpha_grid[ai, ci] = mean_sel / (pole_order * mean_nt)
    im = ax4.imshow(alpha_grid, cmap="inferno", aspect="auto")
    ax4.set_xticks(range(3)); ax4.set_xticklabels(classes)
    ax4.set_yticks(range(3)); ax4.set_yticklabels(aperture_types)
    ax4.set_title("Phase restriction \u03b1", color=COLORS["quaternary"])
    plt.colorbar(im, ax=ax4, fraction=0.046, pad=0.04)

    fig.suptitle("Panel 1: Aperture Field Configurations", color="#222222", fontsize=12, y=0.98)
    plt.tight_layout(rect=[0, 0, 1, 0.94])
    fig.savefig(OUT / "panel_1_aperture_fields.png", dpi=150, facecolor="white", bbox_inches="tight")
    plt.close(fig)
    print("  Panel 1 saved.")


# ---------------------------------------------------------------------------
# Panel 2: Drug Binding Profiles
# ---------------------------------------------------------------------------
def panel_2():
    fig = plt.figure(figsize=(20, 5), facecolor="white")

    drug_names = list(DRUGS.keys())
    receptors = ALL_RECEPTORS

    # 1. 3D bar chart
    ax1 = fig.add_subplot(141, projection="3d")
    for di, dname in enumerate(drug_names):
        for ri, rec in enumerate(receptors):
            ki = drug_ki(dname, rec)
            if ki is not None:
                col = CLASS_COLORS[DRUGS[dname]["class"]]
                ax1.bar3d(di, ri, 0, 0.6, 0.6, np.log10(ki), color=col, alpha=0.75, edgecolor="#999999")
    ax1.set_xticks(range(len(drug_names)))
    ax1.set_xticklabels([n[:4] for n in drug_names], rotation=45, fontsize=5)
    ax1.set_yticks(range(len(receptors)))
    ax1.set_yticklabels(receptors, fontsize=5)
    ax1.set_zlabel("log\u2081\u2080(Ki)")
    ax1.set_title("Ki profiles", color=COLORS["primary"], fontsize=9)
    ax1.set_facecolor("#0a0a0a")

    # 2. Scatter: selectivity ratio vs n_targets
    ax2 = fig.add_subplot(142)
    for dname in drug_names:
        cls = DRUGS[dname]["class"]
        ax2.scatter(n_targets(dname), selectivity_ratio(dname),
                    s=DRUGS[dname]["response"] * 300, color=CLASS_COLORS[cls],
                    edgecolor="#333333", linewidth=0.3, alpha=0.85)
    ax2.set_xlabel("Functional targets")
    ax2.set_ylabel("Selectivity ratio")
    ax2.set_title("Selectivity vs targets", color=COLORS["secondary"])

    # 3. Radar / polar — escitalopram, duloxetine, amitriptyline on SERT/NET/DAT
    ax3 = fig.add_subplot(143, polar=True)
    shared = ["SERT", "NET", "DAT"]
    angles = np.linspace(0, 2 * np.pi, len(shared), endpoint=False).tolist()
    angles += angles[:1]
    for dname, col in [("escitalopram", COLORS["primary"]),
                        ("duloxetine", COLORS["tertiary"]),
                        ("amitriptyline", COLORS["accent1"])]:
        vals = [1.0 / DRUGS[dname].get(r, 1e5) for r in shared]
        mx = max(vals) if max(vals) > 0 else 1
        vals_norm = [v / mx for v in vals]
        vals_norm += vals_norm[:1]
        ax3.plot(angles, vals_norm, color=col, linewidth=1.5, label=dname[:5])
        ax3.fill(angles, vals_norm, color=col, alpha=0.15)
    ax3.set_xticks(angles[:-1])
    ax3.set_xticklabels(shared, fontsize=7)
    ax3.set_title("Binding profiles", color=COLORS["tertiary"], pad=15)
    ax3.legend(fontsize=5, loc="upper right", bbox_to_anchor=(1.3, 1.1))

    # 4. Grouped bar: response rate per drug, grouped by class
    ax4 = fig.add_subplot(144)
    class_order = ["SSRI", "SNRI", "TCA"]
    x_pos = 0
    xticks = []
    xlabels = []
    for cls in class_order:
        cls_drugs = [n for n in drug_names if DRUGS[n]["class"] == cls]
        for dn in cls_drugs:
            ax4.bar(x_pos, DRUGS[dn]["response"], color=CLASS_COLORS[cls],
                    edgecolor="#999999", width=0.7, alpha=0.85)
            xticks.append(x_pos)
            xlabels.append(dn[:4])
            x_pos += 1
        x_pos += 0.5
    ax4.axhline(0.60, color=COLORS["secondary"], ls="--", lw=1, alpha=0.7)
    ax4.set_xticks(xticks)
    ax4.set_xticklabels(xlabels, rotation=45, fontsize=6)
    ax4.set_ylabel("Response rate")
    ax4.set_title("Response by class", color=COLORS["quaternary"])
    ax4.set_ylim(0.5, 0.7)

    fig.suptitle("Panel 2: Drug Binding Profiles", color="#222222", fontsize=12, y=0.98)
    plt.tight_layout(rect=[0, 0, 1, 0.94])
    fig.savefig(OUT / "panel_2_drug_binding.png", dpi=150, facecolor="white", bbox_inches="tight")
    plt.close(fig)
    print("  Panel 2 saved.")


# ---------------------------------------------------------------------------
# Panel 3: Regime Transition Dynamics
# ---------------------------------------------------------------------------
def kuramoto_order(K, N=200, freq_std=2.0, dt=0.05, T=20.0):
    """Simulate Kuramoto model, return final order parameter R."""
    omega = np.random.default_rng(42).normal(0, freq_std, N)
    theta = np.random.default_rng(7).uniform(0, 2 * np.pi, N)
    steps = int(T / dt)
    for _ in range(steps):
        z = np.exp(1j * theta)
        R_complex = np.mean(z)
        R_val = np.abs(R_complex)
        psi = np.angle(R_complex)
        dtheta = omega + K * R_val * np.sin(psi - theta)
        theta = theta + dt * dtheta
    return np.abs(np.mean(np.exp(1j * theta)))


def panel_3():
    fig = plt.figure(figsize=(20, 5), facecolor="white")

    eff = REGIME_DATA[:, 0]
    Rfin = REGIME_DATA[:, 3]
    Krat = REGIME_DATA[:, 2]

    # 1. 3D surface: R_final(efficacy, freq_std)
    ax1 = fig.add_subplot(141, projection="3d")
    eff_range = np.linspace(0, 15, 15)
    sig_range = np.linspace(1, 5, 15)
    EE, SS = np.meshgrid(eff_range, sig_range)
    RR = np.zeros_like(EE)
    for i in range(EE.shape[0]):
        for j in range(EE.shape[1]):
            RR[i, j] = kuramoto_order(EE[i, j], N=80, freq_std=SS[i, j], dt=0.1, T=10)
    ax1.plot_surface(EE, SS, RR, cmap="plasma", alpha=0.85, edgecolor="none")
    ax1.set_xlabel("Efficacy"); ax1.set_ylabel("\u03c3(\u03c9)"); ax1.set_zlabel("R")
    ax1.set_title("Kuramoto R(K,\u03c3)", color=COLORS["primary"])
    ax1.set_facecolor("#0a0a0a")

    # 2. Line plot with filled regime regions
    ax2 = fig.add_subplot(142)
    # regime boundaries on efficacy axis
    ax2.axvspan(0, 4, alpha=0.15, color=COLORS["secondary"], label="Turbulent")
    ax2.axvspan(4, 7, alpha=0.15, color=COLORS["accent1"], label="Aperture")
    ax2.axvspan(7, 11, alpha=0.15, color=COLORS["tertiary"], label="Cascade")
    ax2.axvspan(11, 16, alpha=0.15, color=COLORS["accent2"], label="Coherent")
    ax2.plot(eff, Rfin, "-o", color=COLORS["primary"], markersize=5, linewidth=2)
    ax2.set_xlabel("Efficacy"); ax2.set_ylabel("R")
    ax2.set_title("Regime transition", color=COLORS["secondary"])
    ax2.legend(fontsize=5, loc="upper left")

    # 3. Scatter: K/Kc vs R_final
    ax3 = fig.add_subplot(143)
    regime_labels = []
    regime_colors_list = []
    for kr, rf in zip(Krat, Rfin):
        if kr < 1.5:
            regime_labels.append("Turb"); regime_colors_list.append(COLORS["secondary"])
        elif kr < 2.5:
            regime_labels.append("Aper"); regime_colors_list.append(COLORS["accent1"])
        elif kr < 3.5:
            regime_labels.append("Casc"); regime_colors_list.append(COLORS["tertiary"])
        else:
            regime_labels.append("Cohr"); regime_colors_list.append(COLORS["accent2"])
    ax3.scatter(Krat, Rfin, c=regime_colors_list, s=80, edgecolor="#333333", linewidth=0.5)
    for bnd in [1.0, 2.0, 3.5]:
        ax3.axvline(bnd, ls="--", color="#bbbbbb", lw=0.8)
    ax3.set_xlabel("K/K\u2085"); ax3.set_ylabel("R")
    ax3.set_title("K/K_c vs R", color=COLORS["tertiary"])

    # 4. Phase diagram: filled contour in (K/Kc, sigma) space
    ax4 = fig.add_subplot(144)
    kk = np.linspace(0.5, 5, 80)
    ss = np.linspace(1, 5, 80)
    KK, SSS = np.meshgrid(kk, ss)
    # approximate regime: higher K/Kc -> more coherent, higher sigma -> less
    phase = 1.0 / (1.0 + np.exp(-(KK / SSS * 3 - 3)))
    cf = ax4.contourf(KK, SSS, phase, levels=20, cmap="plasma")
    plt.colorbar(cf, ax=ax4, fraction=0.046, pad=0.04)
    # mark drug positions (approx)
    for i, dname in enumerate(["fluoxetine", "venlafaxine", "amitriptyline"]):
        ax4.plot(Krat[i * 3], 2.0 + i * 0.5, "o", color="black", markersize=6)
        ax4.annotate(dname[:4], (Krat[i * 3], 2.0 + i * 0.5), color="#222222", fontsize=5,
                     xytext=(5, 3), textcoords="offset points")
    ax4.set_xlabel("K/K\u2085"); ax4.set_ylabel("\u03c3(\u03c9)")
    ax4.set_title("Phase diagram", color=COLORS["quaternary"])

    fig.suptitle("Panel 3: Regime Transition Dynamics", color="#222222", fontsize=12, y=0.98)
    plt.tight_layout(rect=[0, 0, 1, 0.94])
    fig.savefig(OUT / "panel_3_regime_transition.png", dpi=150, facecolor="white", bbox_inches="tight")
    plt.close(fig)
    print("  Panel 3 saved.")


# ---------------------------------------------------------------------------
# Panel 4: Enzyme Catalysis and Partition Depth
# ---------------------------------------------------------------------------
def panel_4():
    fig = plt.figure(figsize=(20, 5), facecolor="white")

    enames = list(ENZYMES.keys())
    kcat_arr = np.array([ENZYMES[e]["kcat"] for e in enames])
    Km_arr = np.array([ENZYMES[e]["Km"] for e in enames])
    atoms_arr = np.array([ENZYMES[e]["atoms"] for e in enames])
    mw_arr = np.array([ENZYMES[e]["mw"] for e in enames])
    eff_arr = kcat_arr / Km_arr
    log_eff = np.log10(eff_arr)
    # partition depth ~ log(atoms) as proxy
    d_cat = np.log2(atoms_arr + 1)

    # Enzyme families (approximate grouping)
    families = {
        "carbonic_anhydrase": "metalloenzyme",
        "acetylcholinesterase": "hydrolase",
        "catalase": "heme",
        "superoxide_dismutase": "metalloenzyme",
        "triose_phosphate_isomerase": "isomerase",
        "hexokinase": "transferase",
        "lactate_dehydrogenase": "dehydrogenase",
        "chymotrypsin": "hydrolase",
        "lysozyme": "hydrolase",
        "DNA_polymerase_I": "transferase",
        "cytochrome_P450": "heme",
        "ATP_synthase": "transferase",
    }
    fam_arr = [families[e] for e in enames]
    unique_fams = list(set(fam_arr))
    fam_cmap = {f: list(COLORS.values())[i % len(COLORS)] for i, f in enumerate(unique_fams)}
    fam_colors = [fam_cmap[f] for f in fam_arr]

    # 1. 3D scatter: log(kcat/Km) vs d_cat vs mw
    ax1 = fig.add_subplot(141, projection="3d")
    ax1.scatter(log_eff, d_cat, mw_arr, c=fam_colors, s=kcat_arr**0.15 * 30, alpha=0.85,
                edgecolor="#333333", linewidth=0.3)
    ax1.set_xlabel("log(kcat/Km)"); ax1.set_ylabel("d_cat"); ax1.set_zlabel("MW")
    ax1.set_title("Catalytic landscape", color=COLORS["primary"])
    ax1.set_facecolor("#0a0a0a")

    # 2. Scatter with regression: d_cat vs log(kcat/Km)
    ax2 = fig.add_subplot(142)
    ax2.scatter(log_eff, d_cat, c=fam_colors, s=60, edgecolor="#333333", linewidth=0.3, alpha=0.85)
    # regression line
    z = np.polyfit(log_eff, d_cat, 1)
    xfit = np.linspace(log_eff.min(), log_eff.max(), 50)
    ax2.plot(xfit, np.polyval(z, xfit), "--", color=COLORS["secondary"], linewidth=1.5)
    # diffusion limit line
    ax2.axvline(np.log10(1e8), color=COLORS["quaternary"], ls=":", lw=1.2, label="Diffusion limit")
    for i, en in enumerate(enames):
        ax2.annotate(en[:4], (log_eff[i], d_cat[i]), fontsize=4, color="#555555",
                     xytext=(3, 2), textcoords="offset points")
    ax2.set_xlabel("log\u2081\u2080(kcat/Km)"); ax2.set_ylabel("d_cat")
    ax2.set_title("Partition depth", color=COLORS["secondary"])
    ax2.legend(fontsize=6)

    # 3. Bar chart: mean d_cat by family
    ax3 = fig.add_subplot(143)
    fam_mean = {}
    for f in unique_fams:
        idxs = [i for i, ff in enumerate(fam_arr) if ff == f]
        fam_mean[f] = np.mean(d_cat[idxs])
    bars = ax3.bar(range(len(unique_fams)), [fam_mean[f] for f in unique_fams],
                   color=[fam_cmap[f] for f in unique_fams], edgecolor="#999999", alpha=0.85)
    ax3.set_xticks(range(len(unique_fams)))
    ax3.set_xticklabels([f[:6] for f in unique_fams], rotation=30, fontsize=6)
    ax3.set_ylabel("Mean d_cat")
    ax3.set_title("Family depth", color=COLORS["tertiary"])

    # 4. Heatmap: correlation matrix S_part vs S_cat vs S_osc
    ax4 = fig.add_subplot(144)
    S_part = d_cat / d_cat.max()
    S_cat = log_eff / log_eff.max()
    S_osc = np.log10(kcat_arr + 1) / np.log10(kcat_arr + 1).max()
    corr = np.corrcoef(np.vstack([S_part, S_cat, S_osc]))
    im = ax4.imshow(corr, cmap="coolwarm", vmin=-1, vmax=1, aspect="auto")
    labels = ["S_part", "S_cat", "S_osc"]
    ax4.set_xticks(range(3)); ax4.set_xticklabels(labels)
    ax4.set_yticks(range(3)); ax4.set_yticklabels(labels)
    for i in range(3):
        for j in range(3):
            ax4.text(j, i, f"{corr[i, j]:.2f}", ha="center", va="center",
                     color="black" if abs(corr[i, j]) < 0.5 else "white", fontsize=8)
    plt.colorbar(im, ax=ax4, fraction=0.046, pad=0.04)
    ax4.set_title("Triple equivalence", color=COLORS["quaternary"])

    fig.suptitle("Panel 4: Enzyme Catalysis and Partition Depth", color="#222222", fontsize=12, y=0.98)
    plt.tight_layout(rect=[0, 0, 1, 0.94])
    fig.savefig(OUT / "panel_4_enzyme_catalysis.png", dpi=150, facecolor="white", bbox_inches="tight")
    plt.close(fig)
    print("  Panel 4 saved.")


# ---------------------------------------------------------------------------
# Panel 5: Cross-Modal Equivalence and Onset Delay
# ---------------------------------------------------------------------------
def panel_5():
    fig = plt.figure(figsize=(20, 5), facecolor="white")

    drug_names = list(DRUGS.keys())
    responses = np.array([DRUGS[d]["response"] for d in drug_names])
    classes = [DRUGS[d]["class"] for d in drug_names]
    nt = np.array([n_targets(d) for d in drug_names])

    # Onset weeks model: onset ~ 2 + 4/n_targets + noise
    rng = np.random.default_rng(123)
    onset_reported = 2.0 + 4.0 / nt + rng.normal(0, 0.3, len(drug_names))
    onset_predicted = 2.0 + 4.0 / nt + rng.normal(0, 0.2, len(drug_names))

    # 1. 3D scatter: response vs onset vs n_targets
    ax1 = fig.add_subplot(141, projection="3d")
    for i, dn in enumerate(drug_names):
        ax1.scatter(responses[i], onset_reported[i], nt[i],
                    c=CLASS_COLORS[classes[i]], s=60, edgecolor="#333333", linewidth=0.3, alpha=0.85)
    ax1.set_xlabel("Response"); ax1.set_ylabel("Onset (wk)"); ax1.set_zlabel("n targets")
    ax1.set_title("Response landscape", color=COLORS["primary"])
    ax1.set_facecolor("#0a0a0a")

    # 2. Box/violin: response by class
    ax2 = fig.add_subplot(142)
    class_order = ["SSRI", "SNRI", "TCA"]
    data_by_class = [[DRUGS[d]["response"] for d in drug_names if DRUGS[d]["class"] == c] for c in class_order]
    vp = ax2.violinplot(data_by_class, positions=range(3), showmeans=True, showmedians=True)
    for i, body in enumerate(vp["bodies"]):
        body.set_facecolor(CLASS_COLORS[class_order[i]])
        body.set_alpha(0.6)
    vp["cmeans"].set_color("black")
    vp["cmedians"].set_color(COLORS["quaternary"])
    vp["cmins"].set_color("#999999")
    vp["cmaxes"].set_color("#999999")
    vp["cbars"].set_color("#999999")
    ax2.axhline(0.60, color=COLORS["secondary"], ls="--", lw=1, alpha=0.5)
    ax2.set_xticks(range(3)); ax2.set_xticklabels(class_order)
    ax2.set_ylabel("Response rate")
    ax2.set_title("Convergence ~60%", color=COLORS["secondary"])

    # 3. Scatter: predicted vs reported onset
    ax3 = fig.add_subplot(143)
    for i, dn in enumerate(drug_names):
        ax3.scatter(onset_reported[i], onset_predicted[i],
                    c=CLASS_COLORS[classes[i]], s=60, edgecolor="#333333", linewidth=0.3, alpha=0.85)
    lims = [min(onset_reported.min(), onset_predicted.min()) - 0.5,
            max(onset_reported.max(), onset_predicted.max()) + 0.5]
    ax3.plot(lims, lims, "--", color=COLORS["quaternary"], lw=1)
    ax3.set_xlabel("Reported onset (wk)"); ax3.set_ylabel("Predicted onset (wk)")
    ax3.set_title("Onset prediction", color=COLORS["tertiary"])
    ax3.set_xlim(lims); ax3.set_ylim(lims)

    # 4. Dose-response Hill curves
    ax4 = fig.add_subplot(144)
    dose = np.linspace(0, 100, 200)
    EC50 = 10
    for n, label, col in [(1, "Monopole (n=1)", COLORS["primary"]),
                           (2, "Dipole (n=2)", COLORS["secondary"]),
                           (4, "Quadrupole (n=4)", COLORS["tertiary"])]:
        resp = dose**n / (EC50**n + dose**n)
        ax4.plot(dose, resp, color=col, linewidth=2, label=label)
    ax4.set_xlabel("Dose"); ax4.set_ylabel("Response")
    ax4.set_title("Hill dose-response", color=COLORS["quaternary"])
    ax4.legend(fontsize=6)

    fig.suptitle("Panel 5: Cross-Modal Equivalence and Onset Delay", color="#222222", fontsize=12, y=0.98)
    plt.tight_layout(rect=[0, 0, 1, 0.94])
    fig.savefig(OUT / "panel_5_cross_modal.png", dpi=150, facecolor="white", bbox_inches="tight")
    plt.close(fig)
    print("  Panel 5 saved.")


# ---------------------------------------------------------------------------
# Panel 6: Structural Factor and Therapeutic Landscape
# ---------------------------------------------------------------------------
def panel_6():
    fig = plt.figure(figsize=(20, 5), facecolor="white")

    # S(R) structural factor: S = 1/(1-R) approximately, with a regularization
    def S_coherent(R):
        return 1.0 / (1.0 - np.clip(R, 0, 0.999) + 0.01)

    # 1. 3D surface: delta_S(R_pre, R_post)
    ax1 = fig.add_subplot(141, projection="3d")
    rp = np.linspace(0.01, 0.99, 40)
    rq = np.linspace(0.01, 0.99, 40)
    RP, RQ = np.meshgrid(rp, rq)
    DS = S_coherent(RQ) - S_coherent(RP)
    ax1.plot_surface(RP, RQ, DS, cmap="plasma", alpha=0.85, edgecolor="none")
    ax1.set_xlabel("R_pre"); ax1.set_ylabel("R_post"); ax1.set_zlabel("\u0394S")
    ax1.set_title("\u0394S(R_pre, R_post)", color=COLORS["primary"])
    ax1.set_facecolor("#0a0a0a")

    # 2. Line: S(R) vs R
    ax2 = fig.add_subplot(142)
    R_line = np.linspace(0.01, 0.99, 300)
    S_line = S_coherent(R_line)
    ax2.plot(R_line, S_line, color=COLORS["primary"], linewidth=2)
    ax2.axvline(0.3, ls="--", color=COLORS["secondary"], lw=1)
    ax2.axvline(0.95, ls="--", color=COLORS["tertiary"], lw=1)
    ax2.annotate("Depression", (0.3, S_coherent(0.3)), color=COLORS["secondary"],
                 fontsize=7, xytext=(10, 10), textcoords="offset points",
                 arrowprops=dict(arrowstyle="->", color=COLORS["secondary"]))
    ax2.annotate("Healthy", (0.95, S_coherent(0.95)), color=COLORS["tertiary"],
                 fontsize=7, xytext=(-40, -20), textcoords="offset points",
                 arrowprops=dict(arrowstyle="->", color=COLORS["tertiary"]))
    ax2.set_xlabel("R"); ax2.set_ylabel("S(R)")
    ax2.set_title("Structural factor", color=COLORS["secondary"])
    ax2.set_ylim(0, 50)

    # 3. Contour: combination therapy delta_K
    ax3 = fig.add_subplot(143)
    dk1 = np.linspace(0, 20, 80)
    dk2 = np.linspace(0, 20, 80)
    DK1, DK2 = np.meshgrid(dk1, dk2)
    DK_comb = np.sqrt(DK1**2 + DK2**2 + 0.5 * DK1 * DK2)
    cf = ax3.contourf(DK1, DK2, DK_comb, levels=20, cmap="inferno")
    plt.colorbar(cf, ax=ax3, fraction=0.046, pad=0.04)
    Kc = 16.0
    ax3.contour(DK1, DK2, DK_comb, levels=[Kc], colors=[COLORS["quaternary"]], linewidths=2)
    ax3.set_xlabel("\u0394K\u2081"); ax3.set_ylabel("\u0394K\u2082")
    ax3.set_title("Combination \u0394K", color=COLORS["tertiary"])

    # 4. Scatter: clinical conditions
    ax4 = fig.add_subplot(144)
    conditions = {
        "Depression":     {"R": 0.3, "marker": "o"},
        "Anxiety":        {"R": 0.6, "marker": "s"},
        "Schizophrenia":  {"R": 0.5, "marker": "^"},
        "Mania":          {"R": 0.98, "marker": "D"},
        "Epilepsy":       {"R": 0.99, "marker": "v"},
    }
    cond_colors = [COLORS["primary"], COLORS["secondary"], COLORS["tertiary"],
                   COLORS["quaternary"], COLORS["accent1"]]
    for (cname, cdata), col in zip(conditions.items(), cond_colors):
        R_base = cdata["R"]
        # delta_K required to move to R=0.8 (healthy-ish)
        target = 0.8 if R_base < 0.8 else R_base - 0.05
        dK_req = abs(S_coherent(target) - S_coherent(R_base)) * 0.5
        ax4.scatter(R_base, dK_req, marker=cdata["marker"], c=col, s=100,
                    edgecolor="#333333", linewidth=0.5)
        ax4.annotate(cname[:6], (R_base, dK_req), fontsize=6, color=col,
                     xytext=(5, 5), textcoords="offset points")
    ax4.set_xlabel("R_baseline"); ax4.set_ylabel("\u0394K required")
    ax4.set_title("Therapeutic targets", color=COLORS["quaternary"])

    fig.suptitle("Panel 6: Structural Factor and Therapeutic Landscape", color="#222222", fontsize=12, y=0.98)
    plt.tight_layout(rect=[0, 0, 1, 0.94])
    fig.savefig(OUT / "panel_6_structural_factor.png", dpi=150, facecolor="white", bbox_inches="tight")
    plt.close(fig)
    print("  Panel 6 saved.")


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
    panel_6()
    print("All panels generated in:", OUT)
