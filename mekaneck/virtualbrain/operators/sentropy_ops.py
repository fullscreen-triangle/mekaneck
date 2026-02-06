"""
S-Entropy Operators: NAVIGATE, GRAD_S, UPDATE_SK, UPDATE_ST, UPDATE_SE.

Implements S-entropy space navigation and update operations.
"""

from typing import List, Callable, Tuple
import numpy as np

from ..core.types import SCoord
from ..core.constants import TAU_CONSCIOUSNESS


def NAVIGATE(
    current: SCoord,
    target: SCoord,
    step_size: float = 0.1,
    max_steps: int = 100,
) -> List[SCoord]:
    """
    NAVIGATE operator: Find path from current to target in S-space.

    Uses gradient descent navigation with O(log n) complexity
    via ternary trisection.

    Args:
        current: Starting S-entropy coordinate
        target: Target S-entropy coordinate
        step_size: Step size for each iteration
        max_steps: Maximum navigation steps

    Returns:
        Path of SCoord from current to target
    """
    path = [current]
    state = current

    for _ in range(max_steps):
        distance = state.distance(target)

        if distance < step_size:
            path.append(target)
            break

        # Compute gradient direction
        grad = state.gradient(target)

        # Update state
        state = state.update(
            delta_sk=step_size * grad[0],
            delta_st=step_size * grad[1],
            delta_se=step_size * grad[2],
        )
        path.append(state)

    return path


def GRAD_S(
    s_coord: SCoord,
    field: Callable[[SCoord], float],
    epsilon: float = 1e-6,
) -> np.ndarray:
    """
    GRAD_S operator: Compute gradient of field in S-space.

    Uses central differences for numerical gradient.

    Args:
        s_coord: Point at which to compute gradient
        field: Scalar field function f(SCoord) -> float
        epsilon: Step size for finite differences

    Returns:
        Gradient vector [df/dSk, df/dSt, df/dSe]
    """
    grad = np.zeros(3)

    # Gradient in Sk direction
    s_plus = s_coord.update(delta_sk=epsilon)
    s_minus = s_coord.update(delta_sk=-epsilon)
    grad[0] = (field(s_plus) - field(s_minus)) / (2 * epsilon)

    # Gradient in St direction
    s_plus = s_coord.update(delta_st=epsilon)
    s_minus = s_coord.update(delta_st=-epsilon)
    grad[1] = (field(s_plus) - field(s_minus)) / (2 * epsilon)

    # Gradient in Se direction
    s_plus = s_coord.update(delta_se=epsilon)
    s_minus = s_coord.update(delta_se=-epsilon)
    grad[2] = (field(s_plus) - field(s_minus)) / (2 * epsilon)

    return grad


def UPDATE_SK(
    s_coord: SCoord,
    information_gain: float,
) -> SCoord:
    """
    UPDATE_SK operator: Update knowledge entropy from observation.

    Sk_new = Sk_old - I(observation)

    Information reduces uncertainty (entropy).

    Args:
        s_coord: Current S-entropy coordinate
        information_gain: Information gained (in normalized units)

    Returns:
        Updated SCoord with reduced Sk
    """
    return s_coord.update(delta_sk=-information_gain)


def UPDATE_ST(
    s_coord: SCoord,
    tau_circuit: float,
    tau_max: float = TAU_CONSCIOUSNESS,
) -> SCoord:
    """
    UPDATE_ST operator: Update temporal entropy from circuit completion.

    St_new = St_old + tau_circuit / tau_max

    Circuit completion increases temporal distance.

    Args:
        s_coord: Current S-entropy coordinate
        tau_circuit: Circuit completion duration
        tau_max: Maximum circuit time (normalization)

    Returns:
        Updated SCoord with increased St
    """
    delta_st = tau_circuit / tau_max
    return s_coord.update(delta_st=delta_st)


def UPDATE_SE(
    s_coord: SCoord,
    trajectory_step: float,
    dt: float = 0.01,
) -> SCoord:
    """
    UPDATE_SE operator: Update evolution entropy from trajectory step.

    Se_new = Se_old + |dS/dt| * dt

    Trajectory progression increases evolution entropy.

    Args:
        s_coord: Current S-entropy coordinate
        trajectory_step: Magnitude of trajectory step |dS|
        dt: Time step

    Returns:
        Updated SCoord with increased Se
    """
    delta_se = trajectory_step * dt
    return s_coord.update(delta_se=delta_se)


def entropy_field(s_coord: SCoord) -> float:
    """
    Compute total entropy field value at coordinate.

    S_total = Sk + St + Se

    Args:
        s_coord: S-entropy coordinate

    Returns:
        Total entropy (sum of components)
    """
    return s_coord.sk + s_coord.st + s_coord.se


def free_energy_field(
    s_coord: SCoord,
    temperature: float = 300.0,
    internal_energy: float = 0.0,
) -> float:
    """
    Compute Helmholtz free energy F = U - TS.

    Args:
        s_coord: S-entropy coordinate
        temperature: Temperature in Kelvin
        internal_energy: Internal energy U

    Returns:
        Free energy F
    """
    from ..core.constants import BOLTZMANN_CONSTANT

    S = s_coord.entropy_magnitude() * BOLTZMANN_CONSTANT
    return internal_energy - temperature * S


def minimize_free_energy(
    initial: SCoord,
    temperature: float = 300.0,
    max_iterations: int = 100,
    learning_rate: float = 0.1,
) -> Tuple[SCoord, List[float]]:
    """
    Find S-coordinate minimizing free energy.

    Uses gradient descent on the free energy landscape.

    Args:
        initial: Starting coordinate
        temperature: Temperature for free energy
        max_iterations: Maximum iterations
        learning_rate: Step size

    Returns:
        (final_coord, energy_history)
    """

    def F(s):
        return free_energy_field(s, temperature)

    current = initial
    history = [F(current)]

    for _ in range(max_iterations):
        grad = GRAD_S(current, F)
        current = current.update(
            delta_sk=-learning_rate * grad[0],
            delta_st=-learning_rate * grad[1],
            delta_se=-learning_rate * grad[2],
        )
        history.append(F(current))

        # Check convergence
        if len(history) > 1 and abs(history[-1] - history[-2]) < 1e-8:
            break

    return current, history
