"""
NPL Operators module.

Implements the Neural Partition Language operators for the Virtual Brain framework.
"""

from .partition_ops import PARTITION, D_CAT, CAPACITY, COORDS, partition_to_sentropy
from .sentropy_ops import NAVIGATE, GRAD_S, UPDATE_SK, UPDATE_ST, UPDATE_SE
from .ternary_ops import ENCODE, DECODE, TRISECT, NAVIGATE_TERNARY
from .poincare_ops import COMPLETE, TARGET, SATISFY, EQUILIBRIUM
from .neural_ops import CONSCIOUSNESS, MEMORY, DREAM, WAKE
from .dynamics_ops import KURAMOTO, PHASE_LOCK, CASCADE, VARIANCE, KuramotoState
from .charge_ops import CONSERVE, REDISTRIBUTE

__all__ = [
    # Partition
    "PARTITION",
    "D_CAT",
    "CAPACITY",
    "COORDS",
    "partition_to_sentropy",
    # S-Entropy
    "NAVIGATE",
    "GRAD_S",
    "UPDATE_SK",
    "UPDATE_ST",
    "UPDATE_SE",
    # Ternary
    "ENCODE",
    "DECODE",
    "TRISECT",
    "NAVIGATE_TERNARY",
    # Poincare
    "COMPLETE",
    "TARGET",
    "SATISFY",
    "EQUILIBRIUM",
    # Neural
    "CONSCIOUSNESS",
    "MEMORY",
    "DREAM",
    "WAKE",
    # Dynamics
    "KURAMOTO",
    "PHASE_LOCK",
    "CASCADE",
    "VARIANCE",
    "KuramotoState",
    # Charge
    "CONSERVE",
    "REDISTRIBUTE",
]
