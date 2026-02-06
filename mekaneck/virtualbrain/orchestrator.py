"""
VirtualBrainValidationSuite: Orchestrates complete validation.

Follows blindhorse pattern for validation orchestration.
"""

import time
from pathlib import Path
from typing import Dict, List, Optional

from .validators import (
    PartitionValidator,
    TripleEquivalenceValidator,
    KuramotoValidator,
    ConsciousnessValidator,
)
from .utils import save_json


class VirtualBrainValidationSuite:
    """
    Orchestrates complete Virtual Brain validation.

    Runs all validators in sequence, collects results,
    and produces comprehensive report.
    """

    def __init__(self, output_dir: Path = Path("results")):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.results: Dict = {}
        self.start_time = None
        self.end_time = None

    def run_complete_validation(
        self,
        skip_validators: Optional[List[str]] = None,
    ) -> Dict:
        """
        Run complete validation suite.

        Args:
            skip_validators: List of validator names to skip

        Returns:
            Complete results dictionary
        """
        skip_validators = skip_validators or []

        print("\n" + "=" * 70)
        print(" " * 15 + "VIRTUAL BRAIN COMPUTING FRAMEWORK")
        print(" " * 20 + "VALIDATION SUITE")
        print("=" * 70)

        self.start_time = time.time()

        # Define validators in order
        validators = [
            ("partition", PartitionValidator, "Partition Coordinates"),
            ("triple_equivalence", TripleEquivalenceValidator, "Triple Equivalence"),
            ("kuramoto", KuramotoValidator, "Kuramoto Dynamics"),
            ("consciousness", ConsciousnessValidator, "Consciousness Equations"),
        ]

        # Run each validator
        for idx, (name, ValidatorClass, description) in enumerate(validators, 1):
            if name in skip_validators:
                print(f"\n[SKIP] Validator {idx}/{len(validators)}: {description}")
                continue

            try:
                print(f"\n" + "=" * 70)
                print(f"VALIDATOR {idx}/{len(validators)}: {description}")
                print("=" * 70)

                validator = ValidatorClass(output_dir=self.output_dir / name)
                self.results[name] = validator.run_validation()

            except Exception as e:
                print(f"ERROR in {description}: {e}")
                self.results[name] = {"error": str(e)}

        self.end_time = time.time()

        # Generate report
        self._generate_report()

        # Save complete results
        self._save_complete_results()

        return self.results

    def _generate_report(self):
        """Generate comprehensive validation report."""
        print("\n" + "=" * 70)
        print(" " * 20 + "VALIDATION REPORT")
        print("=" * 70)

        total_time = self.end_time - self.start_time

        total_validators = len(self.results)
        successful = sum(1 for r in self.results.values() if "error" not in r)

        print(f"\nExecution Summary:")
        print(f"  Total validators: {total_validators}")
        print(f"  Successful: {successful}")
        print(f"  Failed: {total_validators - successful}")
        print(f"  Total time: {total_time:.2f} seconds")

        # Count claims
        total_claims = 0
        validated_claims = 0

        for validator_name, results in self.results.items():
            if "claims_validated" in results:
                claims = results["claims_validated"]
                total_claims += len(claims)
                validated_claims += sum(1 for c in claims.values() if c)

        validation_rate = validated_claims / total_claims if total_claims > 0 else 0

        print(f"\nValidation Summary:")
        print(f"  Total claims: {total_claims}")
        print(f"  Validated: {validated_claims}")
        print(f"  Validation rate: {validation_rate:.1%}")

        if validation_rate >= 0.9:
            status = "[OK] EXCELLENT - Framework validated"
        elif validation_rate >= 0.8:
            status = "[OK] GOOD - Most claims validated"
        elif validation_rate >= 0.7:
            status = "[WARN] ACCEPTABLE - Needs review"
        else:
            status = "[FAIL] NEEDS WORK - Significant issues"

        print(f"\nOverall Status: {status}")
        print("=" * 70)

    def _save_complete_results(self):
        """Save complete results to JSON."""
        output_file = self.output_dir / "complete_validation_results.json"

        results_with_metadata = {
            "metadata": {
                "suite": "Virtual Brain Computing Framework Validation",
                "version": "0.1.0",
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "total_time_seconds": float(self.end_time - self.start_time),
            },
            "results": self.results,
        }

        save_json(results_with_metadata, output_file)
        print(f"\n[OK] Complete results saved to: {output_file}")
