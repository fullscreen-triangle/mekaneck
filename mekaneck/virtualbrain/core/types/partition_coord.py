"""
PartitionCoord: Quantum-style categorical coordinates (n, l, m, s).

Implements the partition coordinate system with capacity C(n) = 2n^2.
Maps categorical states to a hierarchical addressing scheme analogous
to atomic quantum numbers but for categorical neural states.
"""

from dataclasses import dataclass
from typing import List, Iterator
import numpy as np


@dataclass(frozen=True)
class PartitionCoord:
    """
    Partition coordinate representing categorical state location.

    Analogous to quantum numbers (n, l, m, s) but for categorical states.
    Provides a complete labeling system for neural partition states.

    Attributes:
        n: Principal quantum number (partition depth), n >= 1
        l: Orbital quantum number (complexity), 0 <= l < n
        m: Magnetic quantum number (orientation), -l <= m <= +l
        s: Spin quantum number (chirality), s in {-0.5, +0.5}

    The capacity at level n is C(n) = 2n^2, giving the sequence:
    C(1)=2, C(2)=8, C(3)=18, C(4)=32, C(5)=50, ...
    """

    n: int
    l: int
    m: int
    s: float

    def __post_init__(self) -> None:
        """Validate quantum number constraints."""
        if self.n < 1:
            raise ValueError(f"n must be >= 1, got {self.n}")
        if not (0 <= self.l < self.n):
            raise ValueError(f"l must be in [0, n), got l={self.l}, n={self.n}")
        if not (-self.l <= self.m <= self.l):
            raise ValueError(f"m must be in [-l, l], got m={self.m}, l={self.l}")
        if self.s not in (-0.5, 0.5):
            raise ValueError(f"s must be +/-0.5, got {self.s}")

    @staticmethod
    def capacity(n: int) -> int:
        """
        Compute capacity at level n.

        C(n) = 2n^2

        This is the total number of distinct categorical states
        at partition depth n.

        Args:
            n: Principal quantum number (partition depth)

        Returns:
            Total number of states at level n
        """
        if n < 1:
            raise ValueError(f"n must be >= 1, got {n}")
        return 2 * n * n

    @staticmethod
    def total_capacity(n_max: int) -> int:
        """
        Compute cumulative capacity up to level n_max.

        Sum_{i=1}^{n_max} C(i) = Sum_{i=1}^{n_max} 2i^2
                               = 2 * n_max(n_max+1)(2n_max+1)/6

        Args:
            n_max: Maximum principal quantum number

        Returns:
            Total number of states up to and including level n_max
        """
        if n_max < 1:
            return 0
        # Using the formula for sum of squares
        return n_max * (n_max + 1) * (2 * n_max + 1) // 3

    @staticmethod
    def density_of_states(n: int) -> int:
        """
        Compute density of states at level n.

        rho(n) = dC/dn = 4n

        Args:
            n: Principal quantum number

        Returns:
            Density of states
        """
        return 4 * n

    def to_linear_index(self) -> int:
        """
        Convert partition coordinate to linear index.

        Enables O(1) array-based lookups by mapping the 4D coordinate
        to a unique integer.

        Returns:
            Linear index for this coordinate
        """
        # States before this n level
        offset = self.total_capacity(self.n - 1)

        # States within this n level, ordered by (l, m, s)
        l_offset = 0
        for l_val in range(self.l):
            l_offset += 2 * (2 * l_val + 1)  # 2*(2l+1) states per l

        m_offset = self.m + self.l  # Map m from [-l, l] to [0, 2l]
        s_offset = 0 if self.s == -0.5 else 1

        return offset + l_offset + 2 * m_offset + s_offset

    @classmethod
    def from_linear_index(cls, index: int) -> "PartitionCoord":
        """
        Reconstruct PartitionCoord from linear index.

        Inverse of to_linear_index().

        Args:
            index: Linear index

        Returns:
            PartitionCoord corresponding to the index
        """
        if index < 0:
            raise ValueError(f"Index must be non-negative, got {index}")

        # Find n level by binary search or iteration
        n = 1
        while cls.total_capacity(n) <= index:
            n += 1

        # Remaining index within n level
        remaining = index - cls.total_capacity(n - 1)

        # Find l by iterating through l values
        l = 0
        while True:
            states_at_l = 2 * (2 * l + 1)
            if remaining < states_at_l:
                break
            remaining -= states_at_l
            l += 1

        # Find m and s from remaining
        m = remaining // 2 - l
        s = -0.5 if remaining % 2 == 0 else 0.5

        return cls(n=n, l=l, m=m, s=s)

    def categorical_distance(self, other: "PartitionCoord") -> float:
        """
        Compute categorical distance D_cat between coordinates.

        D_cat = sqrt((dn)^2 + (dl)^2 + (dm)^2 + (ds)^2)

        This distance is modality-independent - the same distance
        applies regardless of which sensory pathway led to the state.

        Args:
            other: Another partition coordinate

        Returns:
            Categorical distance (dimensionless)
        """
        dn = self.n - other.n
        dl = self.l - other.l
        dm = self.m - other.m
        ds = self.s - other.s

        return float(np.sqrt(dn**2 + dl**2 + dm**2 + ds**2))

    def is_adjacent(self, other: "PartitionCoord") -> bool:
        """
        Check if coordinates are adjacent (D_cat = 1).

        Adjacent states can transition directly without intermediate states.

        Args:
            other: Another partition coordinate

        Returns:
            True if coordinates are adjacent
        """
        return abs(self.categorical_distance(other) - 1.0) < 1e-10

    @classmethod
    def all_coords_at_level(cls, n: int) -> List["PartitionCoord"]:
        """
        Generate all coordinates at partition level n.

        Args:
            n: Principal quantum number

        Returns:
            List of all valid PartitionCoord at this level
        """
        coords = []
        for l in range(n):
            for m in range(-l, l + 1):
                for s in (-0.5, 0.5):
                    coords.append(cls(n=n, l=l, m=m, s=s))
        return coords

    @classmethod
    def iterate_all(cls, n_max: int) -> Iterator["PartitionCoord"]:
        """
        Iterate through all coordinates up to level n_max.

        Args:
            n_max: Maximum principal quantum number

        Yields:
            PartitionCoord in order of linear index
        """
        for n in range(1, n_max + 1):
            for coord in cls.all_coords_at_level(n):
                yield coord

    def energy_level(self, E_max: float = 1.0) -> float:
        """
        Compute energy level for this coordinate.

        E_n = E_max * (n / n_max)^2

        Args:
            E_max: Maximum energy at highest level

        Returns:
            Energy at this partition level
        """
        # Assume n_max = 10 for normalization
        n_max = 10
        return E_max * (self.n / n_max) ** 2

    def __repr__(self) -> str:
        """String representation."""
        s_str = "+1/2" if self.s == 0.5 else "-1/2"
        return f"PartitionCoord(n={self.n}, l={self.l}, m={self.m}, s={s_str})"
