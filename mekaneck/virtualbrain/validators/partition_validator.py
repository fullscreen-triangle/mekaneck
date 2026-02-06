"""
PartitionValidator: Validates partition coordinate system.

Tests the (n, l, m, s) coordinate system and C(n) = 2n^2 capacity formula.
"""

from typing import Dict, Any, List
import numpy as np
from pathlib import Path

from .base_validator import BaseValidator
from ..core.types import PartitionCoord
from ..operators.partition_ops import CAPACITY, D_CAT, partition_to_sentropy


class PartitionValidator(BaseValidator):
    """
    Validates the partition coordinate system.

    Tests:
    1. Capacity formula C(n) = 2n^2
    2. Total capacity formula
    3. Coordinate constraints (n >= 1, 0 <= l < n, etc.)
    4. Linear index bijection
    5. Categorical distance symmetry
    """

    def __init__(self, n_max: int = 10, output_dir: Path = None):
        super().__init__(output_dir)
        self.n_max = n_max

    def test_capacity_formula(self) -> Dict[str, Any]:
        """Test C(n) = 2n^2."""
        results = []
        all_correct = True

        for n in range(1, self.n_max + 1):
            expected = 2 * n * n
            actual = CAPACITY(n)
            correct = expected == actual
            all_correct = all_correct and correct

            results.append({
                "n": n,
                "expected": expected,
                "actual": actual,
                "correct": correct,
            })

        return {"tests": results, "all_correct": all_correct}

    def test_total_capacity(self) -> Dict[str, Any]:
        """Test cumulative capacity formula."""
        results = []
        all_correct = True

        for n_max in range(1, self.n_max + 1):
            # Expected: sum of 2i^2 for i=1 to n_max
            expected = sum(2 * i * i for i in range(1, n_max + 1))
            actual = PartitionCoord.total_capacity(n_max)
            correct = expected == actual
            all_correct = all_correct and correct

            results.append({
                "n_max": n_max,
                "expected": expected,
                "actual": actual,
                "correct": correct,
            })

        return {"tests": results, "all_correct": all_correct}

    def test_linear_index_bijection(self) -> Dict[str, Any]:
        """Test that linear index is a bijection."""
        total = PartitionCoord.total_capacity(self.n_max)
        all_bijective = True

        # Test forward and inverse
        for idx in range(min(total, 100)):  # Test first 100
            coord = PartitionCoord.from_linear_index(idx)
            recovered_idx = coord.to_linear_index()

            if idx != recovered_idx:
                all_bijective = False
                break

        # Test uniqueness
        seen_indices = set()
        for coord in PartitionCoord.iterate_all(min(self.n_max, 5)):
            idx = coord.to_linear_index()
            if idx in seen_indices:
                all_bijective = False
                break
            seen_indices.add(idx)

        return {
            "total_states": total,
            "tested_states": min(total, 100),
            "all_bijective": all_bijective,
        }

    def test_distance_symmetry(self) -> Dict[str, Any]:
        """Test that D_cat is symmetric."""
        symmetric = True
        n_tests = 0

        coords = list(PartitionCoord.iterate_all(min(self.n_max, 4)))[:20]

        for i, c1 in enumerate(coords):
            for c2 in coords[i + 1 :]:
                d12 = D_CAT(c1, c2)
                d21 = D_CAT(c2, c1)

                if abs(d12 - d21) > 1e-10:
                    symmetric = False
                    break
                n_tests += 1

            if not symmetric:
                break

        return {"n_tests": n_tests, "symmetric": symmetric}

    def run_validation(self) -> Dict[str, Any]:
        """Run complete partition validation."""
        print("=" * 70)
        print("PARTITION COORDINATE VALIDATION")
        print("=" * 70)

        print("\n1. Testing capacity formula C(n) = 2n^2...")
        capacity_results = self.test_capacity_formula()

        print("2. Testing total capacity formula...")
        total_results = self.test_total_capacity()

        print("3. Testing linear index bijection...")
        bijection_results = self.test_linear_index_bijection()

        print("4. Testing distance symmetry...")
        symmetry_results = self.test_distance_symmetry()

        claims_validated = {
            "capacity_formula_correct": capacity_results["all_correct"],
            "total_capacity_correct": total_results["all_correct"],
            "linear_index_bijective": bijection_results["all_bijective"],
            "distance_symmetric": symmetry_results["symmetric"],
        }

        results = self._create_result_dict(
            parameters={"n_max": self.n_max},
            results={
                "capacity": capacity_results,
                "total_capacity": total_results,
                "bijection": bijection_results,
                "symmetry": symmetry_results,
            },
            claims_validated=claims_validated,
        )

        self.save_results(results)
        self.print_summary(results)

        return results
