"""Core module containing types, entities, and constants."""

from .constants import (
    BOLTZMANN_CONSTANT,
    PLANCK_CONSTANT,
    HBAR,
    H_PLUS_FREQUENCY,
    O2_QUANTUM_STATES,
    THOUGHT_FREQUENCY,
    CONSCIOUSNESS_FREQUENCY,
    KT_ROOM_TEMP,
)
from .types import (
    PartitionCoord,
    SCoord,
    TernaryAddr,
    MentalState,
    CircuitState,
    CircuitRegime,
)

__all__ = [
    # Constants
    "BOLTZMANN_CONSTANT",
    "PLANCK_CONSTANT",
    "HBAR",
    "H_PLUS_FREQUENCY",
    "O2_QUANTUM_STATES",
    "THOUGHT_FREQUENCY",
    "CONSCIOUSNESS_FREQUENCY",
    "KT_ROOM_TEMP",
    # Types
    "PartitionCoord",
    "SCoord",
    "TernaryAddr",
    "MentalState",
    "CircuitState",
    "CircuitRegime",
]
