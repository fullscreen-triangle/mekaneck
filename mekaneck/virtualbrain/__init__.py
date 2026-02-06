"""
Virtual Brain Computing Framework.

A trajectory-based computational architecture for neuropharmacology
where experiment = observation = computation.

Based on the Neural Partition Language (NPL) specification.
"""

__version__ = "0.1.0"
__author__ = "Kundai Farai Sachikonye"

from .core.types import (
    PartitionCoord,
    SCoord,
    TernaryAddr,
    MentalState,
    CircuitState,
    CircuitRegime,
)
from .core.constants import (
    BOLTZMANN_CONSTANT,
    PLANCK_CONSTANT,
    HBAR,
    H_PLUS_FREQUENCY,
    O2_QUANTUM_STATES,
)

__all__ = [
    # Types
    "PartitionCoord",
    "SCoord",
    "TernaryAddr",
    "MentalState",
    "CircuitState",
    "CircuitRegime",
    # Constants
    "BOLTZMANN_CONSTANT",
    "PLANCK_CONSTANT",
    "HBAR",
    "H_PLUS_FREQUENCY",
    "O2_QUANTUM_STATES",
]
