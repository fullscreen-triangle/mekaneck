"""
Ternary Operators: ENCODE, DECODE, TRISECT, NAVIGATE_TERNARY.

Implements ternary addressing operations with O(log3 n) complexity.
The ternary system provides 37% efficiency improvement over binary.
"""

from typing import Tuple, List
import numpy as np

from ..core.types import TernaryAddr, SCoord


def ENCODE(value: int, depth: int) -> TernaryAddr:
    """
    ENCODE operator: Encode integer to ternary address.

    Complexity: O(depth) = O(log3 n)

    Args:
        value: Non-negative integer to encode
        depth: Depth of ternary representation

    Returns:
        TernaryAddr of specified depth
    """
    return TernaryAddr.encode(value, depth)


def ENCODE_FLOAT(value: float, depth: int) -> TernaryAddr:
    """
    ENCODE_FLOAT operator: Encode float in [0,1] to ternary address.

    Args:
        value: Float in [0, 1]
        depth: Precision depth

    Returns:
        TernaryAddr representing the value
    """
    return TernaryAddr.from_float(value, depth)


def DECODE(addr: TernaryAddr) -> int:
    """
    DECODE operator: Decode ternary address to integer.

    Inverse of ENCODE. Complexity: O(depth)

    Args:
        addr: Ternary address

    Returns:
        Integer value
    """
    return addr.decode()


def DECODE_FLOAT(addr: TernaryAddr) -> float:
    """
    DECODE_FLOAT operator: Decode ternary address to float.

    Args:
        addr: Ternary address

    Returns:
        Float in [0, 1]
    """
    return addr.to_float()


def TRISECT(addr: TernaryAddr) -> Tuple[TernaryAddr, TernaryAddr, TernaryAddr]:
    """
    TRISECT operator: Divide address into three children.

    Generates left (0), middle (1), and right (2) children.

    Args:
        addr: Parent address

    Returns:
        Tuple (left, middle, right) children
    """
    return addr.trisect()


def NAVIGATE_TERNARY(
    addr_from: TernaryAddr,
    addr_to: TernaryAddr,
) -> List[TernaryAddr]:
    """
    NAVIGATE_TERNARY operator: Find path through ternary tree.

    Navigates from source to destination through common ancestor.
    Complexity: O(depth_from + depth_to) = O(log3 n)

    Args:
        addr_from: Starting address
        addr_to: Destination address

    Returns:
        List of addresses forming the path
    """
    return addr_from.path_to(addr_to)


def TERNARY_DISTANCE(addr1: TernaryAddr, addr2: TernaryAddr) -> int:
    """
    Compute navigation distance between addresses.

    Distance = number of edges in path through tree.

    Args:
        addr1: First address
        addr2: Second address

    Returns:
        Navigation distance
    """
    return addr1.navigation_distance(addr2)


def encode_scoord(s_coord: SCoord, depth: int) -> Tuple[TernaryAddr, TernaryAddr, TernaryAddr]:
    """
    Encode S-entropy coordinate as three ternary addresses.

    One address per dimension (Sk, St, Se).

    Args:
        s_coord: S-entropy coordinate
        depth: Precision depth

    Returns:
        Tuple of three TernaryAddr (sk_addr, st_addr, se_addr)
    """
    sk_addr = TernaryAddr.from_float(s_coord.sk, depth)
    st_addr = TernaryAddr.from_float(s_coord.st, depth)
    se_addr = TernaryAddr.from_float(s_coord.se, depth)

    return sk_addr, st_addr, se_addr


def decode_scoord(
    sk_addr: TernaryAddr,
    st_addr: TernaryAddr,
    se_addr: TernaryAddr,
) -> SCoord:
    """
    Decode three ternary addresses to S-entropy coordinate.

    Args:
        sk_addr: Address for Sk
        st_addr: Address for St
        se_addr: Address for Se

    Returns:
        SCoord from decoded addresses
    """
    return SCoord(
        sk=sk_addr.to_float(),
        st=st_addr.to_float(),
        se=se_addr.to_float(),
    )


def ternary_search(
    target: float,
    evaluate: callable,
    depth: int = 20,
) -> Tuple[TernaryAddr, float]:
    """
    Ternary search for value in [0, 1].

    Uses trisection to find address where evaluate(x) is closest to target.

    Args:
        target: Target value
        evaluate: Function f(x) -> float for x in [0, 1]
        depth: Maximum search depth

    Returns:
        (best_address, best_value)
    """
    addr = TernaryAddr.root()
    best_addr = addr
    best_diff = float("inf")

    for _ in range(depth):
        left, middle, right = addr.trisect()

        # Evaluate at each child
        left_val = evaluate(left.to_float())
        middle_val = evaluate(middle.to_float())
        right_val = evaluate(right.to_float())

        # Find closest to target
        diffs = [
            (abs(left_val - target), left, left_val),
            (abs(middle_val - target), middle, middle_val),
            (abs(right_val - target), right, right_val),
        ]
        diffs.sort(key=lambda x: x[0])

        if diffs[0][0] < best_diff:
            best_diff = diffs[0][0]
            best_addr = diffs[0][1]

        # Descend into best child
        addr = diffs[0][1]

    return best_addr, evaluate(best_addr.to_float())


def ternary_efficiency() -> float:
    """
    Compute ternary efficiency over binary.

    Efficiency = log_2(3) ≈ 1.585

    This means ternary requires 37% fewer iterations than binary
    for the same precision.

    Returns:
        Efficiency ratio
    """
    return np.log(3) / np.log(2)
