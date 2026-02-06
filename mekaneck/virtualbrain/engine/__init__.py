"""Engine module containing the Poincare computer and state manager."""

from .poincare_computer import PoincareComputer, ComputeResult
from .state_manager import StateManager

__all__ = [
    "PoincareComputer",
    "ComputeResult",
    "StateManager",
]
