"""
Download Sleep-EDF Expanded dataset from PhysioNet.

Downloads a subset of SC (Sleep Cassette) subjects for validation.
Files are saved to results/sleep/data/

Usage:
    python download_sleep_edf.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from common import download_file

SLEEP_EDF_BASE = "https://physionet.org/files/sleep-edfx/1.0.0/sleep-cassette"
DATA_DIR = Path(__file__).resolve().parent.parent.parent / "results" / "sleep" / "data"

# Subset: 4 recordings (2 subjects × 2 nights)
FILES = [
    "SC4001E0-PSG.edf",
    "SC4001EC-Hypnogram.edf",
    "SC4002E0-PSG.edf",
    "SC4002EC-Hypnogram.edf",
    "SC4011E0-PSG.edf",
    "SC4011EC-Hypnogram.edf",
    "SC4012E0-PSG.edf",
    "SC4012EC-Hypnogram.edf",
]


def main():
    print("Downloading Sleep-EDF Expanded subset...")
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    for fname in FILES:
        url = f"{SLEEP_EDF_BASE}/{fname}"
        dest = DATA_DIR / fname
        try:
            download_file(url, dest)
        except Exception as e:
            print(f"  [error] Failed to download {fname}: {e}")
            print("  You may need to accept the PhysioNet data use agreement.")
            print(f"  Manual download: {url}")

    print("\nDone. Files saved to:", DATA_DIR)


if __name__ == "__main__":
    main()
