"""
Shared plotting style for all manuscript panels.

Rules enforced here:
  - white background everywhere (figure, axes, 3d panes)
  - minimal text: short axis labels, no chart titles beyond a bold letter tag
  - no tables, no conceptual/box diagrams: every chart plots computed numbers
  - four charts per row, at least one 3d chart per panel
"""

from __future__ import annotations

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401  (registers 3d projection)

# ---- palette (colour-blind safe, print-legible) -----------------------
C_PRIMARY = "#1f4e79"   # deep blue
C_SECOND = "#c0392b"    # brick red
C_THIRD = "#2e8b57"     # sea green
C_FOURTH = "#e08214"    # amber
C_GREY = "#7f8c8d"
C_LIGHT = "#bdc3c7"

SERIES = [C_PRIMARY, C_SECOND, C_THIRD, C_FOURTH]

BASE_RC = {
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "savefig.facecolor": "white",
    "savefig.edgecolor": "white",
    "axes.edgecolor": "#333333",
    "axes.linewidth": 0.8,
    "axes.grid": True,
    "grid.color": "#dddddd",
    "grid.linewidth": 0.5,
    "grid.alpha": 0.9,
    "axes.axisbelow": True,
    "font.family": "DejaVu Sans",
    "font.size": 8.5,
    "axes.labelsize": 9,
    "xtick.labelsize": 8,
    "ytick.labelsize": 8,
    "legend.fontsize": 7.5,
    "legend.frameon": False,
    "lines.linewidth": 1.6,
    "figure.dpi": 200,
}

plt.rcParams.update(BASE_RC)


def new_panel(n=4, width=16.0, height=3.9, projections=None):
    """
    Build a 1-by-n panel. `projections` is a list like [None, None, '3d', None].
    Returns (fig, axes).
    """
    projections = projections or [None] * n
    fig = plt.figure(figsize=(width, height), facecolor="white")
    axes = []
    for i, proj in enumerate(projections):
        ax = fig.add_subplot(1, n, i + 1, projection=proj)
        if proj == "3d":
            style_3d(ax)
        axes.append(ax)
    return fig, axes


def style_3d(ax):
    """White panes, light gridlines, thin axis lines."""
    ax.set_facecolor("white")
    for pane in (ax.xaxis, ax.yaxis, ax.zaxis):
        pane.pane.fill = False
        pane.pane.set_edgecolor("#dddddd")
        pane._axinfo["grid"]["color"] = "#dddddd"
        pane._axinfo["grid"]["linewidth"] = 0.4
    ax.tick_params(labelsize=7)
    ax.xaxis.labelpad = 2
    ax.yaxis.labelpad = 2
    ax.zaxis.labelpad = 2


def tag(ax, letter, is3d=False):
    """Bold letter tag in the corner. This is the only text beyond axis labels."""
    if is3d:
        ax.text2D(-0.06, 1.03, letter, transform=ax.transAxes,
                  fontsize=12, fontweight="bold", va="top", ha="left")
    else:
        ax.text(-0.10, 1.04, letter, transform=ax.transAxes,
                fontsize=12, fontweight="bold", va="top", ha="left")


def finish(fig, path, tight=True):
    # subplots_adjust rather than tight_layout: 3d axes with colorbars make
    # tight_layout emit a warning and give up, leaving ragged spacing.
    if tight:
        fig.subplots_adjust(left=0.045, right=0.985, top=0.90, bottom=0.16,
                            wspace=0.34)
    fig.savefig(path, dpi=300, facecolor="white", bbox_inches="tight")
    plt.close(fig)
    print(f"  wrote {path}")
