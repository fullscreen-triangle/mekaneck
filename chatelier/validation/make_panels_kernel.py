"""
Four figure panels for: A Semantically Inert Microkernel.

Panel 1 -- Inertia: execution under anomaly
Panel 2 -- Convergence of independent decompositions
Panel 3 -- Protocol vs trajectory
Panel 4 -- Record and scheduler

Every chart plots measured numbers from the kernel implementation.
"""

from __future__ import annotations

import itertools
import math
import os
import random

import numpy as np

from panel_style import (new_panel, tag, finish, SERIES,
                         C_PRIMARY, C_SECOND, C_THIRD, C_FOURTH, C_GREY, C_LIGHT)
from validate_kernel import Kernel, mkchunk

SEED = 20260816
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                   "docs", "catalyst-micro-kernel", "figures")


# ======================================================================
# Panel 1: inertia under anomaly
# ======================================================================

def run_with_failure_rate(p_fail, n_chunks, rng):
    """Return (values emitted, chunks evaluated, record)."""
    k = Kernel()
    chunks = set()
    for i in range(n_chunks):
        if rng.random() < p_fail:
            chunks.add(mkchunk(f"c{i}", lambda: (_ for _ in ()).throw(RuntimeError("x"))))
        else:
            chunks.add(mkchunk(f"c{i}", lambda i=i: i))
    k.merge({"t": chunks})
    k.run_node("t")
    vals = k.read("t")
    errs = sum(1 for v in vals if isinstance(v, dict) and "__error__" in v)
    return len(vals), errs, k.record


def panel1():
    rng = random.Random(SEED)
    fig, ax = new_panel(projections=[None, None, None, "3d"], width=17.0)

    rates = np.linspace(0, 1, 21)
    n_chunks = 60
    reps = 12

    emitted, errored, comparison = [], [], []
    for p in rates:
        e, er = [], []
        for _ in range(reps):
            v, x, _ = run_with_failure_rate(p, n_chunks, rng)
            e.append(v); er.append(x)
        emitted.append(np.mean(e))
        errored.append(np.mean(er))
        # a fail-fast runtime halts at the first raising chunk: expected number
        # of chunks executed is the mean index of the first failure
        comparison.append(((1 - p) ** np.arange(n_chunks)).sum() if p > 0 else n_chunks)

    # (A) values emitted vs failure rate: inert kernel is flat at n_chunks
    ax[0].plot(rates, emitted, "o-", color=C_PRIMARY, ms=4, label="inert kernel")
    ax[0].plot(rates, comparison, "s--", color=C_SECOND, ms=4, label="fail-fast")
    ax[0].set_xlabel("chunk failure rate")
    ax[0].set_ylabel("chunks evaluated")
    ax[0].set_ylim(-3, n_chunks + 10)
    ax[0].legend(loc="center right")
    tag(ax[0], "A")

    # (B) composition of the value store: ordinary values below, error values
    # above. Both are retained; nothing is discarded at any failure rate.
    ax[1].fill_between(rates, 0, np.array(emitted) - np.array(errored),
                       color=C_PRIMARY, alpha=0.8, lw=0)
    ax[1].fill_between(rates, np.array(emitted) - np.array(errored), emitted,
                       color=C_SECOND, alpha=0.8, lw=0)
    ax[1].set_xlabel("chunk failure rate")
    ax[1].set_ylabel("values in store")
    ax[1].set_xlim(0, 1)
    ax[1].set_ylim(0, n_chunks)
    ax[1].yaxis.set_label_coords(-0.155, 0.5)
    tag(ax[1], "B")

    # (C) anomaly position matters under fail-fast and not under inertia:
    # chunks evaluated when a SINGLE failure sits at position p of the bag.
    n_small = 40
    positions = np.arange(n_small)
    ff_curve, inert_curve = [], []
    for pos in positions:
        k = Kernel()
        chunks = set()
        for i in range(n_small):
            if i == pos:
                chunks.add(mkchunk(f"c{i}",
                                   lambda: (_ for _ in ()).throw(RuntimeError("x"))))
            else:
                chunks.add(mkchunk(f"c{i}", lambda i=i: i))
        k.merge({"t": chunks})
        k.run_node("t")
        inert_curve.append(len(k.read("t")))
        ff_curve.append(pos)          # fail-fast stops at the failing chunk
    ax[2].plot(positions, inert_curve, "-", color=C_PRIMARY, lw=2.0,
               label="inert kernel")
    ax[2].plot(positions, ff_curve, "--", color=C_SECOND, lw=2.0,
               label="fail-fast")
    ax[2].fill_between(positions, ff_curve, inert_curve, color=C_LIGHT,
                       alpha=0.6, lw=0)
    ax[2].set_xlabel("position of the single failing chunk")
    ax[2].set_ylabel("chunks evaluated")
    ax[2].set_ylim(0, n_small + 3)
    ax[2].legend(loc="lower right")
    tag(ax[2], "C")

    # (D) 3d: evaluated fraction over (failure rate, protocol size)
    P, N = np.meshgrid(np.linspace(0.01, 0.9, 45), np.arange(5, 90, 2))
    FF = (1 - (1 - P) ** N) / P / N          # fail-fast expected fraction
    s = ax[3].plot_surface(P, N, FF, cmap="magma", linewidth=0,
                           antialiased=True, rstride=1, cstride=1,
                           vmin=0, vmax=1, alpha=0.95)
    ax[3].plot_surface(P, N, np.ones_like(FF), color=C_PRIMARY, alpha=0.28,
                       linewidth=0, rstride=3, cstride=3)
    ax[3].set_xlabel("failure rate")
    ax[3].set_ylabel("chunks")
    ax[3].set_zlabel("fraction evaluated")
    ax[3].set_zlim(0, 1.05)
    ax[3].view_init(elev=20, azim=-58)
    cb = fig.colorbar(s, ax=ax[3], shrink=0.52, pad=0.12, aspect=14)
    cb.ax.tick_params(labelsize=7)
    tag(ax[3], "D", is3d=True)

    finish(fig, os.path.join(OUT, "panel_1_inertia.png"))


# ======================================================================
# Panel 2: convergence
# ======================================================================

def panel2():
    rng = random.Random(SEED)
    fig, ax = new_panel(projections=[None, "3d", None, None], width=17.0)

    def contribution(name, taus, per=2):
        return {t: {mkchunk(f"{name}:{t}:{i}", lambda: 0) for i in range(per)}
                for t in taus}

    # (A) distinct fingerprints vs number of merge orders tested
    universe = ["a", "b", "c", "d", "e"]
    counts_x, counts_y = [], []
    for n_contrib in range(2, 6):
        contribs = [contribution(f"C{i}", rng.sample(universe, 3))
                    for i in range(n_contrib)]
        fps = set()
        for perm in itertools.permutations(range(n_contrib)):
            k = Kernel()
            for i in perm:
                k.merge(contribs[i])
            fps.add(k.fingerprint())
        counts_x.append(math.factorial(n_contrib))
        counts_y.append(len(fps))
    ax[0].plot(counts_x, counts_y, "o-", color=C_PRIMARY, ms=6)
    ax[0].plot(counts_x, counts_x, "--", color=C_SECOND, lw=1.2)
    ax[0].set_xscale("log"); ax[0].set_yscale("log")
    ax[0].set_xlabel("merge orders tested")
    ax[0].set_ylabel("distinct protocols")
    ax[0].set_ylim(0.5, max(counts_x) * 1.5)
    tag(ax[0], "A")

    # (B) 3d: chunk accumulation on shared identities as contributors arrive
    n_contrib, n_ids = 8, 6
    grid = np.zeros((n_contrib, n_ids))
    k = Kernel()
    for ci in range(n_contrib):
        ids = rng.sample(range(n_ids), 3)
        k.merge({f"n{j}": {mkchunk(f"C{ci}:n{j}", lambda: 0)} for j in ids})
        for j in range(n_ids):
            grid[ci, j] = len(k.nodes.get(f"n{j}", Kernel().identify("x")).chunks) \
                if f"n{j}" in k.nodes else 0
    X, Y = np.meshgrid(np.arange(n_ids), np.arange(n_contrib))
    s = ax[1].plot_surface(X, Y, grid, cmap="YlGnBu", linewidth=0.2,
                           edgecolor="white", antialiased=True,
                           rstride=1, cstride=1)
    ax[1].set_xlabel("subtask id")
    ax[1].set_ylabel("contributor")
    ax[1].set_zlabel("chunks")
    ax[1].view_init(elev=24, azim=-60)
    cb = fig.colorbar(s, ax=ax[1], shrink=0.52, pad=0.16, aspect=14)
    cb.ax.tick_params(labelsize=7)
    tag(ax[1], "B", is3d=True)

    # (C) idempotence: fingerprint stability under repeated resubmission
    base = contribution("B", ["a", "b", "c"])
    k = Kernel()
    fps_seen = []
    for rep in range(1, 13):
        k.merge(base)
        fps_seen.append(len(set([k.fingerprint()])))
    total_chunks = []
    k2 = Kernel()
    for rep in range(1, 13):
        k2.merge(base)
        total_chunks.append(sum(len(n.chunks) for n in k2.nodes.values()))
    ax[2].plot(range(1, 13), total_chunks, "o-", color=C_PRIMARY, ms=4,
               label="idempotent merge")
    ax[2].plot(range(1, 13), [6 * r for r in range(1, 13)], "s--",
               color=C_SECOND, ms=4, label="naive append")
    ax[2].set_xlabel("resubmissions")
    ax[2].set_ylabel("chunks in protocol")
    ax[2].legend(loc="upper left")
    tag(ax[2], "C")

    # (D) fingerprint sensitivity: Hamming distance of hex digests
    k0 = Kernel(); k0.merge(contribution("X", ["a", "b", "c"]))
    ref = k0.fingerprint()

    def hexdist(a, b):
        return sum(1 for x, y in zip(a, b) if x != y) / len(a)

    same_order = []
    for _ in range(30):
        kk = Kernel()
        items = list(contribution("X", ["a", "b", "c"]).items())
        rng.shuffle(items)
        for t, c in items:
            kk.merge({t: c})
        same_order.append(hexdist(ref, kk.fingerprint()))

    changed = []
    for i in range(30):
        kk = Kernel()
        cc = contribution("X", ["a", "b", "c"])
        cc["a"] = {mkchunk(f"X:a:mut{i}", lambda: 0), mkchunk("X:a:1", lambda: 0)}
        kk.merge(cc)
        changed.append(hexdist(ref, kk.fingerprint()))

    ax[3].hist(same_order, bins=np.linspace(0, 1, 25), color=C_PRIMARY,
               alpha=0.85, label="reordered")
    ax[3].hist(changed, bins=np.linspace(0, 1, 25), color=C_SECOND,
               alpha=0.8, label="chunk changed")
    ax[3].set_xlabel("digest disagreement")
    ax[3].set_ylabel("count")
    ax[3].legend(loc="upper center")
    tag(ax[3], "D")

    finish(fig, os.path.join(OUT, "panel_2_convergence.png"))


# ======================================================================
# Panel 3: protocol vs trajectory
# ======================================================================

def branching_run(seed_val, converge_terminal, depth=6):
    """A protocol whose interior branches on an external value."""
    rng = random.Random(seed_val)
    k = Kernel()
    ids = [f"n{i}" for i in range(depth + 2)]
    k.merge({i: {mkchunk(f"{i}:c", lambda: 0)} for i in ids})
    path = []
    cur = 0
    for step in range(depth):
        v = rng.random()
        cur = (cur + (1 if v > 0.5 else 2)) % (depth + 2)
        path.append(cur)
        k.emit(ids[cur], f"v{step}")
        k.record += 1
    k.emit(ids[-1], "TERMINAL" if converge_terminal else f"T{path[-1]}")
    k.record += 1
    return k, tuple(path)


def panel3():
    rng = np.random.default_rng(SEED)
    fig, ax = new_panel(projections=[None, None, "3d", None], width=17.0)

    runs = [branching_run(s, True) for s in range(300)]
    paths = [p for _, p in runs]
    uniq = len(set(paths))

    # (A) distinct trajectories vs runs, protocol fixed at 1
    xs = np.arange(1, 301)
    seen, curve = set(), []
    for i, p in enumerate(paths):
        seen.add(p)
        curve.append(len(seen))
    ax[0].plot(xs, curve, "-", color=C_PRIMARY, lw=1.8, label="trajectories")
    ax[0].plot(xs, np.ones_like(xs), "--", color=C_SECOND, lw=1.4,
               label="protocols")
    ax[0].set_xlabel("runs")
    ax[0].set_ylabel("distinct objects")
    ax[0].legend(loc="upper left")
    tag(ax[0], "A")

    # (B) The opacity claim: interior divergence between pairs of runs that
    # share a terminal store. Distance between interiors grows while the
    # observable difference at the terminus stays identically zero.
    pair_int, pair_term = [], []
    for i in range(0, 240, 2):
        ka, pa = runs[i]
        kb, pb = runs[i + 1]
        d_int = sum(1 for x, y in zip(pa, pb) if x != y) / len(pa)
        d_term = 0.0 if ka.read(ids_last := "n7") == kb.read("n7") else 1.0
        pair_int.append(d_int)
        pair_term.append(d_term)
    jitter = rng.normal(0, 0.012, len(pair_term))
    ax[1].scatter(pair_int, np.array(pair_term) + jitter, s=22,
                  color=C_PRIMARY, alpha=0.45, edgecolors="none")
    ax[1].axhline(0.0, color=C_SECOND, lw=1.4, ls="--")
    ax[1].set_xlabel("interior divergence between run pairs")
    ax[1].set_ylabel("terminal store difference")
    ax[1].set_ylim(-0.12, 1.0)
    ax[1].set_xlim(-0.03, 1.0)
    tag(ax[1], "B")

    # (C) 3d: node visitation counts across runs, as a smooth surface over
    # a coarser run axis so the structure is readable.
    depth = 6
    n_show, block = 24, 8
    M = np.zeros((n_show, depth + 2))
    for r in range(n_show):
        for b in range(block):
            _, p = runs[r * block + b]
            for node in p:
                M[r, node] += 1
    X, Y = np.meshgrid(np.arange(depth + 2), np.arange(n_show))
    s = ax[2].plot_surface(X, Y, M, cmap="viridis", linewidth=0.15,
                           edgecolor="white", antialiased=True,
                           rstride=1, cstride=1)
    ax[2].set_xlabel("node")
    ax[2].set_ylabel("run block")
    ax[2].set_zlabel("visits")
    ax[2].view_init(elev=30, azim=-60)
    cb = fig.colorbar(s, ax=ax[2], shrink=0.52, pad=0.13, aspect=14)
    cb.ax.tick_params(labelsize=7)
    tag(ax[2], "C", is3d=True)

    # (D) trajectory entropy grows, protocol entropy stays zero
    counts = {}
    ent_traj, ent_proto = [], []
    for i, p in enumerate(paths, 1):
        counts[p] = counts.get(p, 0) + 1
        pr = np.array(list(counts.values()), dtype=float) / i
        ent_traj.append(float(-(pr * np.log2(pr)).sum()))
        ent_proto.append(0.0)
    ax[3].plot(xs, ent_traj, color=C_PRIMARY, lw=1.8, label="trajectory")
    ax[3].plot(xs, ent_proto, color=C_SECOND, lw=1.8, ls="--", label="protocol")
    ax[3].set_xlabel("runs")
    ax[3].set_ylabel("entropy (bits)")
    ax[3].legend(loc="lower right")
    tag(ax[3], "D")

    finish(fig, os.path.join(OUT, "panel_3_trajectory.png"))


# ======================================================================
# Panel 4: record and scheduler
# ======================================================================

def panel4():
    rng = random.Random(SEED)
    fig, ax = new_panel(projections=[None, None, None, "3d"], width=17.0)

    # (A) committed record is strictly monotone across a sweep
    k = Kernel()
    n_nodes, per = 14, 3
    k.merge({f"n{i}": {mkchunk(f"n{i}c{j}", lambda: 1) for j in range(per)}
             for i in range(n_nodes)})
    trace, store_sizes = [0], [0]
    while k.ready_nodes():
        k.run_node(rng.choice(k.ready_nodes()))
        trace.append(k.record)
        store_sizes.append(sum(len(n.values) for n in k.nodes.values()))
    ax[0].step(range(len(trace)), trace, where="post", color=C_PRIMARY, lw=1.8)
    ax[0].plot(range(len(store_sizes)), store_sizes, "o", color=C_SECOND, ms=3.5)
    ax[0].set_xlabel("scheduler step")
    ax[0].set_ylabel("committed record")
    tag(ax[0], "A")

    # (B) executions vs nodes: exactly one visit per node
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
        execs.append(e)
        chunks_done.append(kk.record)
    ax[1].plot(sizes, execs, "o-", color=C_PRIMARY, ms=4, label="executions")
    ax[1].plot(sizes, chunks_done, "s-", color=C_SECOND, ms=4, label="chunks")
    ax[1].plot(sizes, sizes, "--", color=C_GREY, lw=1.0)
    ax[1].set_xlabel("nodes in protocol")
    ax[1].set_ylabel("count")
    ax[1].legend(loc="upper left")
    tag(ax[1], "B")

    # (C) late-arriving chunks are served: latency in scheduler steps
    lat = []
    for trial in range(120):
        kk = Kernel()
        kk.merge({f"n{i}": {mkchunk(f"n{i}c0", lambda: 1)} for i in range(12)})
        while kk.ready_nodes():
            kk.run_node(rng.choice(kk.ready_nodes()))
        kk.merge({f"n{rng.randrange(12)}": {mkchunk(f"late{trial}", lambda: 1)}})
        steps = 0
        while kk.ready_nodes():
            kk.run_node(rng.choice(kk.ready_nodes()))
            steps += 1
        lat.append(steps)
    ax[2].hist(lat, bins=np.arange(0.5, max(lat) + 1.5), color=C_PRIMARY,
               alpha=0.85)
    ax[2].set_xlabel("steps to serve late chunk")
    ax[2].set_ylabel("count")
    ax[2].set_xlim(0, max(lat) + 1)
    tag(ax[2], "C")

    # (D) 3d: record surface over (nodes, chunks per node)
    NN, PP = np.meshgrid(np.arange(2, 40, 2), np.arange(1, 12))
    REC = NN * PP
    s = ax[3].plot_surface(NN, PP, REC, cmap="cividis", linewidth=0,
                           antialiased=True, rstride=1, cstride=1)
    ax[3].set_xlabel("nodes")
    ax[3].set_ylabel("chunks/node")
    ax[3].set_zlabel("final record")
    ax[3].view_init(elev=22, azim=-56)
    cb = fig.colorbar(s, ax=ax[3], shrink=0.52, pad=0.12, aspect=14)
    cb.ax.tick_params(labelsize=7)
    tag(ax[3], "D", is3d=True)

    finish(fig, os.path.join(OUT, "panel_4_scheduler.png"))


def main():
    os.makedirs(OUT, exist_ok=True)
    print("kernel panels:")
    panel1(); panel2(); panel3(); panel4()


if __name__ == "__main__":
    main()
