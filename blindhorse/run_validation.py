#!/usr/bin/env python3
"""
Quick run script for Pharmaceutical Maxwell Demon validation suite.

Usage:
    python run_validation.py              # Run all validations
    python run_validation.py --fast       # Skip slow validators
    python run_validation.py --no-viz     # Skip visualizations
"""

import sys
import argparse
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from blindhorse.orchestrator import PharmBMDValidationSuite


def main():
    parser = argparse.ArgumentParser(
        description="Run Pharmaceutical Maxwell Demon validation suite"
    )
    parser.add_argument(
        "--fast",
        action="store_true",
        help="Skip slow validators (harmonic network, Maxwell demon)"
    )
    parser.add_argument(
        "--no-viz",
        action="store_true",
        help="Skip visualization generation"
    )
    parser.add_argument(
        "--skip",
        nargs="+",
        help="List of validators to skip (e.g., --skip harmonic maxwell)"
    )
    
    args = parser.parse_args()
    
    # Determine skip list
    skip_validators = args.skip or []
    if args.fast:
        skip_validators.extend(["harmonic", "maxwell"])
    
    # Create suite
    print("\n" + "="*70)
    print(" "*10 + "PHARMACEUTICAL MAXWELL DEMON")
    print(" "*15 + "VALIDATION SUITE")
    print("="*70)
    print("\nInitializing validation suite...")
    
    suite = PharmBMDValidationSuite()
    
    # Run validation
    print(f"\nConfiguration:")
    print(f"  Skip visualizations: {args.no_viz}")
    print(f"  Skip validators: {skip_validators if skip_validators else 'None'}")
    print("\nStarting validation...\n")
    
    results = suite.run_complete_validation(
        skip_visualizations=args.no_viz,
        skip_validators=skip_validators
    )
    
    print("\n" + "="*70)
    print(" "*15 + "VALIDATION COMPLETE")
    print("="*70)
    print("\n✓ Results saved in ./results/ directory")
    print("✓ See README.md for details on interpreting results")
    print("\n")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

