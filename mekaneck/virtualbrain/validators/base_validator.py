"""
BaseValidator: Abstract base class for all validators.

Follows blindhorse patterns for consistent validation interface.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, List
from pathlib import Path
import time

from ..utils import save_json


@dataclass
class ValidationResult:
    """Standard validation result structure."""

    validator_name: str
    timestamp: str
    parameters: Dict[str, Any]
    results: Dict[str, Any]
    claims_validated: Dict[str, bool]

    def overall_success(self) -> bool:
        """Check if all claims validated."""
        return all(self.claims_validated.values())

    def success_rate(self) -> float:
        """Compute validation success rate."""
        if not self.claims_validated:
            return 0.0
        return sum(self.claims_validated.values()) / len(self.claims_validated)


class BaseValidator(ABC):
    """
    Abstract base class for Virtual Brain validators.

    Follows blindhorse pattern with:
    - run_validation() -> Dict method
    - save_results() method
    - print_summary() method
    """

    def __init__(self, output_dir: Path = None):
        """
        Initialize validator.

        Args:
            output_dir: Output directory for results
        """
        self.validator_name = self.__class__.__name__
        self.output_dir = output_dir or Path(f"results/{self.validator_name.lower()}")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    @abstractmethod
    def run_validation(self) -> Dict[str, Any]:
        """
        Run validation tests.

        Must be implemented by subclasses.

        Returns:
            Dictionary with validation results including 'claims_validated' key
        """
        pass

    def save_results(self, results: Dict[str, Any]) -> Path:
        """
        Save validation results to JSON.

        Args:
            results: Results dictionary

        Returns:
            Path to saved file
        """
        output_file = self.output_dir / f"{self.validator_name.lower()}_results.json"
        save_json(results, output_file)
        print(f"\n[OK] Results saved to: {output_file}")
        return output_file

    def print_summary(self, results: Dict[str, Any]):
        """
        Print validation summary.

        Args:
            results: Results dictionary
        """
        print("\n" + "=" * 70)
        print("VALIDATION SUMMARY")
        print("=" * 70)

        if "claims_validated" in results:
            claims = results["claims_validated"]
            for claim, validated in claims.items():
                status = "[OK] VALIDATED" if validated else "[FAIL] FAILED"
                print(f"  {claim}: {status}")

            rate = sum(claims.values()) / len(claims) if claims else 0
            print(f"\nOverall: {sum(claims.values())}/{len(claims)} ({rate:.1%})")

        print("=" * 70)

    def _create_result_dict(
        self,
        parameters: Dict[str, Any],
        results: Dict[str, Any],
        claims_validated: Dict[str, bool],
    ) -> Dict[str, Any]:
        """
        Create standardized result dictionary.

        Args:
            parameters: Validation parameters
            results: Detailed results
            claims_validated: Claim validation status
        """
        return {
            "validator": self.validator_name,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "parameters": parameters,
            "results": results,
            "claims_validated": claims_validated,
        }
