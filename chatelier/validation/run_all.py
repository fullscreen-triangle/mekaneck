"""
Run all three validation suites and write a combined summary.

Usage:  python run_all.py
Writes: results/{algebra,kernel,mekaneck}_results.json and results/summary.json
"""

from __future__ import annotations

import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(HERE, "results")

SUITES = [
    ("algebra", "validate_algebra.py", "algebra_results.json",
     "A Residual Algebra for Catalytic Composition"),
    ("kernel", "validate_kernel.py", "kernel_results.json",
     "A Semantically Inert Microkernel"),
    ("mekaneck", "validate_mekaneck.py", "mekaneck_results.json",
     "Mekaneck: Substrate-Neutral Language for Individuation-Structured Inquiry"),
    ("policy", "validate_policy.py", "policy_results.json",
     "Policy: bounded-budget selection, phase exclusion, relay drift"),
    ("cardiac", "validate_cardiac.py", "cardiac_results.json",
     "Cardiac substrate: the floor obligation on an 86-night record"),
]


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    summary = {"suites": {}, "totals": {}}

    for key, script, out_json, paper in SUITES:
        print(f"\n{'=' * 70}\n  {paper}\n{'=' * 70}")
        proc = subprocess.run([sys.executable, os.path.join(HERE, script)],
                              capture_output=True, text=True, cwd=HERE)
        sys.stdout.write(proc.stdout)
        if proc.returncode != 0:
            sys.stderr.write(proc.stderr)

        path = os.path.join(OUT_DIR, out_json)
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            summary["suites"][key] = {
                "paper": paper,
                "results_file": out_json,
                **data["summary"],
            }

    tot = sum(s.get("n_checks", 0) for s in summary["suites"].values())
    passed = sum(s.get("n_passed", 0) for s in summary["suites"].values())
    failed = sum(s.get("n_failed", 0) for s in summary["suites"].values())
    summary["totals"] = {
        "n_checks": tot,
        "n_passed": passed,
        "n_failed": failed,
        "all_passed": failed == 0,
    }

    with open(os.path.join(OUT_DIR, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print(f"\n{'=' * 70}\n  COMBINED\n{'=' * 70}")
    print(json.dumps(summary["totals"], indent=2))
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
