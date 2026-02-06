"""Validators module for the Virtual Brain framework."""

from .base_validator import BaseValidator, ValidationResult
from .partition_validator import PartitionValidator
from .triple_equivalence_validator import TripleEquivalenceValidator
from .kuramoto_validator import KuramotoValidator
from .consciousness_validator import ConsciousnessValidator

__all__ = [
    "BaseValidator",
    "ValidationResult",
    "PartitionValidator",
    "TripleEquivalenceValidator",
    "KuramotoValidator",
    "ConsciousnessValidator",
]
