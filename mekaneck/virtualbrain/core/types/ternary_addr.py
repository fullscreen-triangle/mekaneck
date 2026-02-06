"""
TernaryAddr: Ternary addressing with O(log3 n) navigation.

Implements ternary tree addressing for hierarchical state space navigation.
The ternary system provides 37% efficiency improvement over binary:
log_3(n) vs log_2(n) for the same state space.
"""

from dataclasses import dataclass
from typing import Tuple, Optional, Iterator, List
import numpy as np


@dataclass(frozen=True)
class TernaryAddr:
    """
    Ternary address for O(log3 n) categorical navigation.

    Uses base-3 digits for hierarchical addressing in S-entropy space.
    Each digit specifies which third of the remaining interval:
        0: Low third (low entropy region)
        1: Middle third (moderate entropy region)
        2: High third (high entropy region)

    The address IS the path - trajectory-position identity holds.

    Attributes:
        digits: Tuple of ternary digits (0, 1, or 2)

    Properties:
        depth: Number of trisection levels (precision)
        resolution: 3^(-depth) - size of addressed region
    """

    digits: Tuple[int, ...]

    def __post_init__(self) -> None:
        """Validate digits are ternary."""
        for d in self.digits:
            if d not in (0, 1, 2):
                raise ValueError(f"Digit must be 0, 1, or 2, got {d}")

    @property
    def depth(self) -> int:
        """Depth of this address in the ternary tree."""
        return len(self.digits)

    @property
    def resolution(self) -> float:
        """Resolution (region size) at this depth."""
        return 3.0 ** (-self.depth)

    @classmethod
    def encode(cls, value: int, depth: int) -> "TernaryAddr":
        """
        Encode integer to ternary address of given depth.

        Complexity: O(depth) = O(log3 n)

        Args:
            value: Non-negative integer to encode
            depth: Depth of ternary representation

        Returns:
            TernaryAddr with specified depth

        Raises:
            ValueError: If value exceeds capacity at given depth
        """
        if value < 0:
            raise ValueError(f"Value must be non-negative, got {value}")

        max_value = 3**depth - 1
        if value > max_value:
            raise ValueError(f"Value {value} exceeds max {max_value} for depth {depth}")

        digits = []
        remaining = value

        for _ in range(depth):
            digits.append(remaining % 3)
            remaining //= 3

        return cls(digits=tuple(reversed(digits)))

    @classmethod
    def from_float(cls, value: float, depth: int) -> "TernaryAddr":
        """
        Encode float in [0, 1] to ternary address.

        Repeatedly trisects the interval, recording which third
        contains the value at each level.

        Args:
            value: Float in [0, 1]
            depth: Precision depth

        Returns:
            TernaryAddr representing the value
        """
        if not (0.0 <= value <= 1.0):
            raise ValueError(f"Value must be in [0, 1], got {value}")

        digits = []
        low, high = 0.0, 1.0

        for _ in range(depth):
            third = (high - low) / 3
            if value < low + third:
                digits.append(0)
                high = low + third
            elif value < low + 2 * third:
                digits.append(1)
                low = low + third
                high = low + third
            else:
                digits.append(2)
                low = low + 2 * third

        return cls(digits=tuple(digits))

    def decode(self) -> int:
        """
        Decode ternary address to integer.

        Inverse of encode(). Complexity: O(depth)

        Returns:
            Integer value represented by this address
        """
        value = 0
        for d in self.digits:
            value = value * 3 + d
        return value

    def to_float(self) -> float:
        """
        Decode ternary address to float in [0, 1].

        Returns the center of the addressed interval.

        Returns:
            Float value in [0, 1]
        """
        low, high = 0.0, 1.0

        for d in self.digits:
            third = (high - low) / 3
            if d == 0:
                high = low + third
            elif d == 1:
                low = low + third
                high = low + third
            else:
                low = low + 2 * third

        return (low + high) / 2

    def interval(self) -> Tuple[float, float]:
        """
        Get the interval [low, high] addressed by this address.

        Returns:
            Tuple (low, high) in [0, 1]
        """
        low, high = 0.0, 1.0

        for d in self.digits:
            third = (high - low) / 3
            if d == 0:
                high = low + third
            elif d == 1:
                new_low = low + third
                high = new_low + third
                low = new_low
            else:
                low = low + 2 * third

        return (low, high)

    def trisect(self) -> Tuple["TernaryAddr", "TernaryAddr", "TernaryAddr"]:
        """
        Trisect this address into three child addresses.

        Returns:
            Tuple (left, middle, right) children
        """
        return (
            TernaryAddr(digits=self.digits + (0,)),
            TernaryAddr(digits=self.digits + (1,)),
            TernaryAddr(digits=self.digits + (2,)),
        )

    def parent(self) -> Optional["TernaryAddr"]:
        """
        Get parent address (one level up).

        Returns:
            Parent TernaryAddr, or None if at root
        """
        if self.depth == 0:
            return None
        return TernaryAddr(digits=self.digits[:-1])

    def navigate(self, direction: int) -> "TernaryAddr":
        """
        Navigate to child in given direction.

        Args:
            direction: 0 (low), 1 (middle), or 2 (high)

        Returns:
            Child TernaryAddr in specified direction
        """
        if direction not in (0, 1, 2):
            raise ValueError(f"Direction must be 0, 1, or 2, got {direction}")
        return TernaryAddr(digits=self.digits + (direction,))

    def common_ancestor(self, other: "TernaryAddr") -> "TernaryAddr":
        """
        Find lowest common ancestor with another address.

        Args:
            other: Another ternary address

        Returns:
            Common ancestor address
        """
        common = []
        for d1, d2 in zip(self.digits, other.digits):
            if d1 == d2:
                common.append(d1)
            else:
                break
        return TernaryAddr(digits=tuple(common))

    def navigation_distance(self, other: "TernaryAddr") -> int:
        """
        Compute navigation distance (number of tree edges).

        Distance = depth(self) + depth(other) - 2*depth(common_ancestor)

        Args:
            other: Target address

        Returns:
            Number of edges in path through tree
        """
        ancestor = self.common_ancestor(other)
        return self.depth + other.depth - 2 * ancestor.depth

    def path_to(self, other: "TernaryAddr") -> List["TernaryAddr"]:
        """
        Compute path from self to other through tree.

        Args:
            other: Target address

        Returns:
            List of addresses from self to other
        """
        ancestor = self.common_ancestor(other)
        path = []

        # Path from self up to ancestor
        current = self
        while current.depth > ancestor.depth:
            path.append(current)
            current = current.parent()

        # Path from ancestor down to other
        down_path = []
        current = other
        while current.depth > ancestor.depth:
            down_path.append(current)
            current = current.parent()

        path.append(ancestor)
        path.extend(reversed(down_path))

        return path

    def all_children(self, max_depth: int) -> Iterator["TernaryAddr"]:
        """
        Generate all descendants up to max_depth.

        Args:
            max_depth: Maximum depth to descend

        Yields:
            TernaryAddr for each descendant
        """
        if self.depth >= max_depth:
            return

        for child in self.trisect():
            yield child
            yield from child.all_children(max_depth)

    @classmethod
    def root(cls) -> "TernaryAddr":
        """Return root address (empty tuple)."""
        return cls(digits=())

    def to_string(self) -> str:
        """
        String representation of address.

        Format: T followed by digits, e.g., T012 for (0, 1, 2)
        """
        return "T" + "".join(str(d) for d in self.digits)

    @classmethod
    def from_string(cls, s: str) -> "TernaryAddr":
        """
        Parse address from string.

        Args:
            s: String starting with 'T' followed by digits

        Returns:
            TernaryAddr parsed from string
        """
        if not s.startswith("T"):
            raise ValueError(f"Ternary address must start with 'T', got {s}")
        if len(s) == 1:
            return cls(digits=())
        digits = tuple(int(c) for c in s[1:])
        return cls(digits=digits)

    def __repr__(self) -> str:
        """String representation."""
        return f"TernaryAddr({self.to_string()})"
