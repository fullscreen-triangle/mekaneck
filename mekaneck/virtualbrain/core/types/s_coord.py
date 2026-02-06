"""
SCoord: S-Entropy coordinate system (Sk, St, Se) in [0,1]^3.

Implements the three-dimensional entropy coordinate space for
categorical state navigation. The triple equivalence holds:
S_osc = S_cat = S_part = k_B * M * ln(n)
"""

from dataclasses import dataclass
from typing import Tuple, Optional
import numpy as np

from ..constants import (
    BOLTZMANN_CONSTANT,
    HBAR,
    KT_ROOM_TEMP,
    O2_QUANTUM_STATES,
    T_0_REFERENCE,
    SE_REFERENCE,
)


@dataclass
class SCoord:
    """
    S-Entropy coordinate in normalized [0,1]^3 space.

    The S-entropy space provides a unified representation where
    oscillatory, categorical, and partition entropy are equivalent.

    Attributes:
        sk: Knowledge entropy (information deficit) in [0, 1]
            - 0 = complete knowledge (minimum uncertainty)
            - 1 = no knowledge (maximum uncertainty)
        st: Temporal entropy (temporal distance) in [0, 1]
            - 0 = events simultaneous
            - 1 = maximum temporal separation
        se: Evolution entropy (trajectory uncertainty) in [0, 1]
            - 0 = deterministic trajectory
            - 1 = maximum trajectory uncertainty

    The triple equivalence holds:
        S_osc = S_cat = S_part = k_B * M * ln(n)
    """

    sk: float  # Knowledge entropy
    st: float  # Temporal entropy
    se: float  # Evolution entropy

    _EPSILON: float = 1e-10

    def __post_init__(self) -> None:
        """Validate coordinates are in [0, 1]."""
        for name, val in [("sk", self.sk), ("st", self.st), ("se", self.se)]:
            if not (0.0 <= val <= 1.0):
                raise ValueError(f"{name} must be in [0, 1], got {val}")

    @classmethod
    def from_frequency(
        cls,
        frequency_hz: float,
        n_states: int = O2_QUANTUM_STATES,
    ) -> "SCoord":
        """
        Map frequency to S-entropy coordinates.

        Uses thermodynamic relations to convert frequency-space
        information to the normalized S-entropy representation.

        Args:
            frequency_hz: Input frequency in Hz
            n_states: Number of categorical states (default: O2 = 25,110)

        Returns:
            SCoord in normalized [0,1]^3 space
        """
        omega = 2 * np.pi * frequency_hz

        # Energy at this frequency
        E = HBAR * omega

        # S_knowledge: fraction of accessible states via Boltzmann factor
        if E > 0:
            p_accessible = 1 / (1 + np.exp(E / KT_ROOM_TEMP))
        else:
            p_accessible = 0.5

        n_accessible = max(1, p_accessible * n_states)
        sk = min(1.0, np.log2(n_accessible) / np.log2(n_states))

        # S_time: temporal distance (log scale, normalized)
        tau = 1 / max(frequency_hz, cls._EPSILON)
        # Normalize: tau from 10^-15 to 10^5 seconds maps to [0, 1]
        st = min(1.0, max(0.0, (np.log10(tau) + 15) / 20))

        # S_entropy: phase distribution entropy from frequency
        phase_variance = min(1.0, frequency_hz / 1e12)
        se = min(1.0, -np.log(1 - phase_variance + cls._EPSILON) / 10)

        return cls(sk=sk, st=st, se=se)

    @classmethod
    def from_array(cls, arr: np.ndarray) -> "SCoord":
        """
        Construct SCoord from numpy array.

        Args:
            arr: Array of shape (3,) with [sk, st, se]

        Returns:
            SCoord instance
        """
        if arr.shape != (3,):
            raise ValueError(f"Expected shape (3,), got {arr.shape}")
        return cls(sk=float(arr[0]), st=float(arr[1]), se=float(arr[2]))

    @classmethod
    def origin(cls) -> "SCoord":
        """Return origin of S-entropy space (0, 0, 0)."""
        return cls(sk=0.0, st=0.0, se=0.0)

    @classmethod
    def equilibrium(cls) -> "SCoord":
        """Return equilibrium state (1, 1, 1) - maximum entropy."""
        return cls(sk=1.0, st=1.0, se=1.0)

    def to_array(self) -> np.ndarray:
        """
        Convert to numpy array [sk, st, se].

        Returns:
            Array of shape (3,)
        """
        return np.array([self.sk, self.st, self.se])

    def distance(self, other: "SCoord") -> float:
        """
        Compute Euclidean distance in S-entropy space.

        d_cat = ||S1 - S2|| = sqrt((dSk)^2 + (dSt)^2 + (dSe)^2)

        This is the categorical distance independent of sensory modality.

        Args:
            other: Another S-entropy coordinate

        Returns:
            Euclidean distance in [0, sqrt(3)]
        """
        dsk = self.sk - other.sk
        dst = self.st - other.st
        dse = self.se - other.se

        return float(np.sqrt(dsk**2 + dst**2 + dse**2))

    def gradient(self, other: "SCoord") -> "SCoord":
        """
        Compute gradient direction from self to other.

        Returns normalized direction vector as SCoord.

        Args:
            other: Target S-entropy coordinate

        Returns:
            Normalized direction as SCoord (may have values outside [0,1])
        """
        dsk = other.sk - self.sk
        dst = other.st - self.st
        dse = other.se - self.se

        norm = np.sqrt(dsk**2 + dst**2 + dse**2) + self._EPSILON

        # Return as tuple since gradient can be negative
        return (dsk / norm, dst / norm, dse / norm)

    def update(
        self,
        delta_sk: float = 0.0,
        delta_st: float = 0.0,
        delta_se: float = 0.0,
    ) -> "SCoord":
        """
        Create updated coordinate with deltas, clamped to [0, 1].

        Args:
            delta_sk: Change in knowledge entropy
            delta_st: Change in temporal entropy
            delta_se: Change in evolution entropy

        Returns:
            New SCoord with clamped values
        """
        return SCoord(
            sk=max(0.0, min(1.0, self.sk + delta_sk)),
            st=max(0.0, min(1.0, self.st + delta_st)),
            se=max(0.0, min(1.0, self.se + delta_se)),
        )

    def to_temperature(
        self,
        se_ref: float = SE_REFERENCE,
        T_0: float = T_0_REFERENCE,
    ) -> float:
        """
        Compute temperature from S-entropy coordinate.

        T = T_0 * exp(Se_current - Se_ref)

        This implements the categorical temperature formula where
        temperature is a universal scaling factor.

        Args:
            se_ref: Reference evolution entropy (default: 0.5)
            T_0: Reference temperature in K (default: 300K)

        Returns:
            Temperature in Kelvin
        """
        return T_0 * np.exp(self.se - se_ref)

    def entropy_magnitude(self) -> float:
        """
        Compute total entropy magnitude.

        |S| = sqrt(Sk^2 + St^2 + Se^2)

        Returns:
            Total entropy in [0, sqrt(3)]
        """
        return float(np.sqrt(self.sk**2 + self.st**2 + self.se**2))

    def categorical_entropy(self, n_categories: int = O2_QUANTUM_STATES) -> float:
        """
        Compute categorical entropy S_cat.

        S_cat = k_B * ln(n_accessible)

        Uses the S-coordinates to determine accessible states.

        Args:
            n_categories: Total number of categories

        Returns:
            Entropy in J/K
        """
        # Use sk as proxy for accessible fraction
        n_accessible = max(1, int(self.sk * n_categories))
        return BOLTZMANN_CONSTANT * np.log(n_accessible)

    def interpolate(self, other: "SCoord", t: float) -> "SCoord":
        """
        Linear interpolation between self and other.

        Args:
            other: Target coordinate
            t: Interpolation parameter in [0, 1]

        Returns:
            Interpolated SCoord
        """
        if not (0.0 <= t <= 1.0):
            raise ValueError(f"t must be in [0, 1], got {t}")

        return SCoord(
            sk=self.sk + t * (other.sk - self.sk),
            st=self.st + t * (other.st - self.st),
            se=self.se + t * (other.se - self.se),
        )

    def __repr__(self) -> str:
        """String representation."""
        return f"SCoord(sk={self.sk:.4f}, st={self.st:.4f}, se={self.se:.4f})"
