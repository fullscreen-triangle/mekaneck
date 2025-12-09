"""
Blindhorse: Pharmaceutical Maxwell Demon Validation Framework

A comprehensive validation package for pharmaceutical BMD theoretical predictions,
including hardware oscillation harvesting, harmonic coincidence networks, S-entropy
navigation, gear ratio predictions, phase-lock dynamics, and trans-Planckian 
temporal measurements.

Validates ALL claims from the pharmaceutical Maxwell demon framework through:
- Zero-simulation categorical state navigation
- Hardware-based oscillation harvesting
- O(1) therapeutic prediction
- Trans-Planckian temporal precision
- Categorical irreversibility
"""

__version__ = "0.1.0"
__author__ = "Kundai Farai Sachikonye"

from .validators import (
    HardwareOscillationValidator,
    HarmonicNetworkValidator,
    SEntropyValidator,
    MaxwellDemonValidator,
    GearRatioValidator,
    PhaseLockValidator,
    SemanticGravityValidator,
    TransPlanckianValidator,
    CategoricalStateValidator,
    TherapeuticPredictionValidator,
)

from .orchestrator import PharmBMDValidationSuite

__all__ = [
    "HardwareOscillationValidator",
    "HarmonicNetworkValidator",
    "SEntropyValidator",
    "MaxwellDemonValidator",
    "GearRatioValidator",
    "PhaseLockValidator",
    "SemanticGravityValidator",
    "TransPlanckianValidator",
    "CategoricalStateValidator",
    "TherapeuticPredictionValidator",
    "PharmBMDValidationSuite",
]

