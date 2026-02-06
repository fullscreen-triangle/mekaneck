"""Core type definitions for the Virtual Brain framework."""

from .partition_coord import PartitionCoord
from .s_coord import SCoord
from .ternary_addr import TernaryAddr
from .mental_state import MentalState
from .circuit_state import CircuitState, CircuitRegime

__all__ = [
    "PartitionCoord",
    "SCoord",
    "TernaryAddr",
    "MentalState",
    "CircuitState",
    "CircuitRegime",
]
