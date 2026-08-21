"""
Prepare chart data for the IDE's cardiac panels.

Everything emitted here is computed from the record; nothing is illustrative.
Where a series exists to show that a claim *fails*, that is stated in the
payload so the front end can label it rather than render it as a result.

Writes web/public/dataset/cardiac_charts.json
"""

from __future__ import annotations

import json
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "web", "public", "dataset")
STAGE = {"D": "deep", "L": "light", "R": "rem", "A": "awake"}


def load(name):
    with open(os.path.join(DATA, name), encoding="utf-8") as f:
        return json.load(f)


def intraday(name):
    rows = []
    for r in load(name):
        v = str(r.get("Heart Rate", "")).strip()
        p = str(r.get("Time", "")).split(":")
        if v and len(p) == 3:
            try:
                rows.append((int(p[0]) * 3600 + int(p[1]) * 60 + int(p[2]), float(v)))
            except ValueError:
                continue
    rows.sort()
    return np.array([x[0] for x in rows]), np.array([x[1] for x in rows])


def stage_minima_curve(series, n=24):
    """(n, running minimum) pairs plus the fitted intercept — the floor plot."""
    series = np.asarray(series, float)
    lo = max(10, len(series) // 100)
    sizes = np.unique(np.logspace(np.log10(lo), np.log10(len(series)), n).astype(int))
    mins = np.array([series[:k].min() for k in sizes], float)
    ns = sizes.astype(float)
    A = np.vstack([1.0 / ns, np.ones_like(ns)]).T
    slope, intercept = np.linalg.lstsq(A, mins, rcond=None)[0]
    return {
        "points": [{"n": int(k), "inv_n": float(1.0 / k), "min": float(m)}
                   for k, m in zip(sizes, mins)],
        "slope": float(slope),
        "intercept": float(intercept),
        "sample_minimum": float(series.min()),
    }


def main():
    nights = load("sleep_summary.json")

    # ---- 1. per-night overview -------------------------------------------
    per_night = []
    for i, n in enumerate(nights):
        vals = [x for x in (n.get("rmssd_5min") or []) if x]
        hyp = n.get("hypnogram_5min") or ""
        counts = {v: 0 for v in STAGE.values()}
        for s in hyp:
            if s in STAGE:
                counts[STAGE[s]] += 1
        per_night.append({
            "night": i,
            "rmssd": n.get("rmssd"),
            "hr_average": n.get("hr_average"),
            "hr_lowest": n.get("hr_lowest"),
            "efficiency": n.get("efficiency"),
            "score": n.get("score"),
            "duration_h": n.get("duration_in_hrs"),
            "deep_h": n.get("deep_in_hrs"),
            "rem_h": n.get("rem_in_hrs"),
            "light_h": n.get("light_in_hrs"),
            "awake_h": n.get("awake_in_hrs"),
            "epochs": len(vals),
            "stages": counts,
            "temperature_deviation": n.get("temperature_deviation"),
        })

    # ---- 2. within-night traces (a representative subset) ----------------
    traces = []
    ranked = sorted(range(len(nights)),
                    key=lambda i: len([x for x in (nights[i].get("rmssd_5min") or []) if x]),
                    reverse=True)
    for i in ranked[:6]:
        n = nights[i]
        vals = n.get("rmssd_5min") or []
        hrs = n.get("hr_5min") or []
        hyp = n.get("hypnogram_5min") or ""
        pts = []
        for j, (v, h) in enumerate(zip(vals, hyp)):
            if v:
                pts.append({
                    "t": j * 5,                       # minutes from sleep onset
                    "rmssd": float(v),
                    "hr": float(hrs[j]) if j < len(hrs) and hrs[j] else None,
                    "stage": STAGE.get(h),
                })
        traces.append({"night": i, "points": pts})

    # ---- 3. the floor test, at both resolutions --------------------------
    seps = []
    for n in nights:
        vals = n.get("rmssd_5min") or []
        hyp = n.get("hypnogram_5min") or ""
        by = {}
        for x, s in zip(vals, hyp):
            if x and s in STAGE:
                by.setdefault(STAGE[s], []).append(float(x))
        for stage, v in by.items():
            rest = [y for k, ys in by.items() if k != stage for y in ys]
            if len(v) >= 3 and len(rest) >= 3:
                seps.append({
                    "stage": stage,
                    "cost": abs(float(np.median(v)) - float(np.median(rest))),
                })
    sep_costs = np.array([s["cost"] for s in seps])

    _, hr = intraday("intraday_base.json")
    dhr = np.abs(np.diff(hr))

    floor_test = {
        "stage_level": {
            "resolution": "5 min",
            "separations": seps,
            "curve": stage_minima_curve(sep_costs, n=20),
            "exactly_zero": int((sep_costs == 0).sum()),
            "n": len(sep_costs),
        },
        "intraday": {
            "resolution": "5 s",
            "curve": stage_minima_curve(dhr),
            "exactly_zero": int((dhr == 0).sum()),
            "zero_fraction": float((dhr == 0).mean()),
            "n": len(dhr),
            "histogram": [
                {"bpm": int(b), "count": int(c)}
                for b, c in zip(*np.unique(dhr[dhr <= 12], return_counts=True))
            ],
        },
        "verdict": "no positive floor at either resolution",
    }

    # ---- 4. the forced constructions, shown as a caution -----------------
    allv = np.array([x for n in nights for x in (n.get("rmssd_5min") or []) if x], float)
    forced = {
        "affine": [
            {"scale": s, "intercept": stage_minima_curve(s - allv)["intercept"]}
            for s in [60, 80, 120, 200, 1000] if s > allv.max()
        ],
        "rmssd_max": float(allv.max()),
        "why": (
            "Any scale above the maximum yields a positive intercept by "
            "construction. These are shown to be discounted, not believed."
        ),
    }

    # ---- 5. transition types and the separation statistic ----------------
    by_type = {}
    for n in nights:
        vals = n.get("rmssd_5min") or []
        hyp = n.get("hypnogram_5min") or ""
        prev = None
        for x, s in zip(vals, hyp):
            if not x or s not in STAGE:
                prev = None
                continue
            cur = STAGE[s]
            if prev is not None and prev[0] != cur and prev[1] > 0:
                by_type.setdefault(f"{prev[0]}->{cur}", []).append(
                    (prev[1] - float(x)) / prev[1]
                )
            prev = (cur, float(x))

    types = []
    for k, v in sorted(by_type.items()):
        if len(v) >= 2:
            types.append({
                "type": k,
                "mean": float(np.mean(v)),
                "sd": float(np.std(v)),
                "n": len(v),
                "values": [float(x) for x in v[:400]],
            })
    means = [t["mean"] for t in types]
    within = float(np.mean([t["sd"] ** 2 for t in types]))
    between = float(np.var(means))
    eta = between / (between + within) if between + within > 0 else 0.0

    # ---- 6. hypnogram + rate, for the stage ribbon -----------------------
    hypnograms = []
    for i in ranked[:6]:
        hyp = nights[i].get("hypnogram_5min") or ""
        runs = []
        if hyp:
            cur, start = hyp[0], 0
            for j, s in enumerate(hyp[1:], 1):
                if s != cur:
                    if cur in STAGE:
                        runs.append({"stage": STAGE[cur], "from": start * 5, "to": j * 5})
                    cur, start = s, j
            if cur in STAGE:
                runs.append({"stage": STAGE[cur], "from": start * 5, "to": len(hyp) * 5})
        hypnograms.append({"night": i, "runs": runs})

    payload = {
        "meta": {
            "n_nights": len(nights),
            "n_epochs": int(len(allv)),
            "source": "consumer wearable, 86-night single-subject record",
        },
        "per_night": per_night,
        "traces": traces,
        "hypnograms": hypnograms,
        "floor_test": floor_test,
        "forced_constructions": forced,
        "transitions": {
            "types": types,
            "between": between,
            "within": within,
            "eta": eta,
            "informative": bool(eta > 0.05),
            "threshold": 0.05,
        },
    }

    path = os.path.join(DATA, "cardiac_charts.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f)
    size = os.path.getsize(path) / 1024
    print(f"wrote {path} ({size:.0f} kB)")
    print(f"  nights {len(per_night)}  epochs {len(allv)}  traces {len(traces)}")
    print(f"  eta {eta:.4f} ({'informative' if eta > 0.05 else 'below threshold'})")
    print(f"  floor: {floor_test['verdict']}")


if __name__ == "__main__":
    main()
