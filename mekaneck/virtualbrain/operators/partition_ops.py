"""
Partition Operators: PARTITION, D_CAT, CAPACITY, COORDS.

Implements categorical partition operations for state space management.
"""

from typing import List
import numpy as np

from ..core.types import PartitionCoord, SCoord


def PARTITION(state_id: int, n_max: int = 10) -> PartitionCoord:
    """
    PARTITION operator: Map state ID to partition coordinate.

    Maps linear state identifier to (n, l, m, s) coordinates.

    Args:
        state_id: Linear state identifier
        n_max: Maximum principal quantum number

    Returns:
        PartitionCoord for the state

    Raises:
        ValueError: If state_id exceeds capacity
    """
    total = PartitionCoord.total_capacity(n_max)
    if state_id >= total:
        raise ValueError(f"state_id {state_id} exceeds capacity {total}")

    return PartitionCoord.from_linear_index(state_id)


def D_CAT(coord1: PartitionCoord, coord2: PartitionCoord) -> float:
    """
    D_CAT operator: Compute categorical distance.

    D_cat = sqrt((dn)^2 + (dl)^2 + (dm)^2 + (ds)^2)

    This distance is modality-independent - the same regardless
    of which sensory pathway led to the states.

    Args:
        coord1: First partition coordinate
        coord2: Second partition coordinate

    Returns:
        Categorical distance (dimensionless)
    """
    return coord1.categorical_distance(coord2)


def CAPACITY(n: int) -> int:
    """
    CAPACITY operator: Compute capacity at level n.

    C(n) = 2n^2

    Args:
        n: Principal quantum number

    Returns:
        Number of states at level n
    """
    return PartitionCoord.capacity(n)


def COORDS(n_level: int) -> List[PartitionCoord]:
    """
    COORDS operator: Generate all coordinates at level n.

    Args:
        n_level: Principal quantum number

    Returns:
        List of all valid PartitionCoord at this level
    """
    return PartitionCoord.all_coords_at_level(n_level)


def partition_to_sentropy(
    coord: PartitionCoord,
    n_max: int = 10,
) -> SCoord:
    """
    Map partition coordinate to S-entropy coordinate.

    Establishes correspondence between partition and S-entropy spaces.

    Args:
        coord: Partition coordinate
        n_max: Maximum n for normalization

    Returns:
        SCoord in [0,1]^3
    """
    # Knowledge entropy scales with principal number
    sk = coord.n / n_max

    # Temporal entropy inversely with orbital complexity
    st = 1.0 - coord.l / max(coord.n - 1, 1) if coord.n > 1 else 0.5

    # Evolution entropy from magnetic quantum number
    if coord.l > 0:
        se = (coord.m + coord.l) / (2 * coord.l)
    else:
        se = 0.5

    return SCoord(
        sk=min(1.0, max(0.0, sk)),
        st=min(1.0, max(0.0, st)),
        se=min(1.0, max(0.0, se)),
    )


def sentropy_to_partition(
    s_coord: SCoord,
    n_max: int = 10,
) -> PartitionCoord:
    """
    Map S-entropy coordinate to partition coordinate.

    Inverse of partition_to_sentropy (approximate).

    Args:
        s_coord: S-entropy coordinate
        n_max: Maximum n for mapping

    Returns:
        Nearest PartitionCoord
    """
    # Estimate n from sk
    n = max(1, min(n_max, int(np.round(s_coord.sk * n_max))))

    # Estimate l from st
    if n > 1:
        l = max(0, min(n - 1, int(np.round((1.0 - s_coord.st) * (n - 1)))))
    else:
        l = 0

    # Estimate m from se
    if l > 0:
        m = int(np.round(s_coord.se * 2 * l - l))
        m = max(-l, min(l, m))
    else:
        m = 0

    # Default spin
    s = 0.5

    return PartitionCoord(n=n, l=l, m=m, s=s)


def adjacent_coords(coord: PartitionCoord) -> List[PartitionCoord]:
    """
    Find all coordinates adjacent to the given coordinate.

    Adjacent means D_cat = 1.

    Args:
        coord: Center coordinate

    Returns:
        List of adjacent PartitionCoord
    """
    adjacent = []

    # Changes in n (if valid)
    if coord.n > 1:
        # Try n-1, keeping l, m valid
        new_l = min(coord.l, coord.n - 2)
        new_m = max(-new_l, min(new_l, coord.m))
        adjacent.append(PartitionCoord(n=coord.n - 1, l=new_l, m=new_m, s=coord.s))

    # n+1
    adjacent.append(PartitionCoord(n=coord.n + 1, l=coord.l, m=coord.m, s=coord.s))

    # Changes in l (if valid)
    if coord.l > 0:
        new_m = max(-(coord.l - 1), min(coord.l - 1, coord.m))
        adjacent.append(PartitionCoord(n=coord.n, l=coord.l - 1, m=new_m, s=coord.s))

    if coord.l < coord.n - 1:
        adjacent.append(PartitionCoord(n=coord.n, l=coord.l + 1, m=coord.m, s=coord.s))

    # Changes in m
    if coord.m > -coord.l:
        adjacent.append(PartitionCoord(n=coord.n, l=coord.l, m=coord.m - 1, s=coord.s))

    if coord.m < coord.l:
        adjacent.append(PartitionCoord(n=coord.n, l=coord.l, m=coord.m + 1, s=coord.s))

    # Change in s
    new_s = -0.5 if coord.s == 0.5 else 0.5
    adjacent.append(PartitionCoord(n=coord.n, l=coord.l, m=coord.m, s=new_s))

    return adjacent
