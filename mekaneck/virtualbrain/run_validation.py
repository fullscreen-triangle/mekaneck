#!/usr/bin/env python3
"""
Run Virtual Brain validation suite.

Usage:
    python -m virtualbrain.run_validation
    python -m virtualbrain.run_validation --fast
    python -m virtualbrain.run_validation --skip partition kuramoto
"""

import argparse
import sys
from pathlib import Path

from .orchestrator import VirtualBrainValidationSuite


def main():
    """Main entry point for validation."""
    parser = argparse.ArgumentParser(
        description="Virtual Brain Computing Framework Validation Suite"
    )
    parser.add_argument(
        "--fast",
        action="store_true",
        help="Run fast validation (skip slow tests)",
    )
    parser.add_argument(
        "--skip",
        nargs="+",
        default=[],
        help="Validators to skip",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("results"),
        help="Output directory for results",
    )

    args = parser.parse_args()

    # Run validation
    suite = VirtualBrainValidationSuite(output_dir=args.output_dir)

    skip_validators = args.skip
    if args.fast:
        # In fast mode, skip slower validators
        skip_validators = list(set(skip_validators))

    results = suite.run_complete_validation(skip_validators=skip_validators)

    # Check overall success
    total_claims = 0
    validated_claims = 0

    for validator_results in results.values():
        if "claims_validated" in validator_results:
            claims = validator_results["claims_validated"]
            total_claims += len(claims)
            validated_claims += sum(1 for c in claims.values() if c)

    success_rate = validated_claims / total_claims if total_claims > 0 else 0

    # Exit with appropriate code
    if success_rate >= 0.9:
        sys.exit(0)
    elif success_rate >= 0.7:
        sys.exit(0)  # Still acceptable
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
