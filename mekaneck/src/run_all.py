"""
Run all validation experiments.

Usage:
    python run_all.py              # run all experiments
    python run_all.py sleep        # run only sleep experiment
    python run_all.py pharma       # run only pharmacology experiment
    python run_all.py enzyme       # run only enzyme experiment
    python run_all.py npl          # run only NPL experiment
"""

import sys
import time

EXPERIMENTS = {
    "sleep": ("sleep.run_sleep_validation", "Sleep Stage - Regime Classification"),
    "pharma": ("pharmacology.run_pharmacology_validation", "Drug Action as Structural Factor"),
    "enzyme": ("enzyme.run_enzyme_validation", "Catalytic Efficiency vs Partition Depth"),
    "npl": ("npl.run_npl_validation", "pNPL Type System Validation"),
}


def run_experiment(module_path: str, name: str) -> bool:
    try:
        print(f"\n{'#' * 70}")
        print(f"# {name}")
        print(f"{'#' * 70}\n")

        module = __import__(module_path, fromlist=["main"])
        start = time.time()
        module.main()
        elapsed = time.time() - start
        print(f"\n  Completed in {elapsed:.1f}s")
        return True
    except Exception as e:
        print(f"\n  [ERROR] {name} failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    selected = sys.argv[1:] if len(sys.argv) > 1 else list(EXPERIMENTS.keys())

    print("=" * 70)
    print("PARTITION MECHANICS VALIDATION SUITE")
    print("=" * 70)

    results = {}
    for key in selected:
        if key not in EXPERIMENTS:
            print(f"Unknown experiment: {key}")
            print(f"Available: {', '.join(EXPERIMENTS.keys())}")
            continue
        module_path, name = EXPERIMENTS[key]
        results[key] = run_experiment(module_path, name)

    print("\n" + "=" * 70)
    print("SUITE SUMMARY")
    print("=" * 70)
    for key, success in results.items():
        status = "[OK]  " if success else "[FAIL]"
        print(f"  {status} {EXPERIMENTS[key][1]}")
    print("=" * 70)


if __name__ == "__main__":
    main()
