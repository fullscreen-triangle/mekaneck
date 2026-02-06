"""
Poincare Operators: COMPLETE, TARGET, SATISFY, EQUILIBRIUM.

Implements the Poincare computing paradigm - work backward from
completion conditions to determine trajectories.
"""

from typing import Callable, Optional, Tuple, List
from dataclasses import dataclass
import numpy as np

from ..core.types import SCoord, MentalState


@dataclass
class CompletionResult:
    """Result of a completion operation."""

    success: bool
    final_state: SCoord
    iterations: int
    trajectory: List[SCoord]
    constraint_violations: List[float]


def COMPLETE(
    partial_state: SCoord,
    constraints: List[Callable[[SCoord], float]],
    max_iterations: int = 1000,
    tolerance: float = 1e-6,
    learning_rate: float = 0.1,
) -> CompletionResult:
    """
    COMPLETE operator: Complete partial state to satisfy constraints.

    Implements Poincare completion - finding a state that satisfies
    all given constraints through gradient descent in S-entropy space.

    This is the core of backward determination: specifying the
    completion condition determines what the trajectory MUST have been.

    Args:
        partial_state: Starting state
        constraints: List of constraint functions (return 0 when satisfied)
        max_iterations: Maximum iterations
        tolerance: Convergence tolerance
        learning_rate: Initial learning rate

    Returns:
        CompletionResult with final state and trajectory
    """
    current = partial_state
    trajectory = [current]
    violations = []
    lr = learning_rate

    for iteration in range(max_iterations):
        # Compute total constraint violation
        total_violation = sum(abs(c(current)) for c in constraints)
        violations.append(total_violation)

        if total_violation < tolerance:
            return CompletionResult(
                success=True,
                final_state=current,
                iterations=iteration,
                trajectory=trajectory,
                constraint_violations=violations,
            )

        # Gradient descent step
        grad = _compute_constraint_gradient(current, constraints)

        current = current.update(
            delta_sk=-lr * grad[0],
            delta_st=-lr * grad[1],
            delta_se=-lr * grad[2],
        )
        trajectory.append(current)

        # Adaptive learning rate decay
        lr *= 0.999

    return CompletionResult(
        success=False,
        final_state=current,
        iterations=max_iterations,
        trajectory=trajectory,
        constraint_violations=violations,
    )


def TARGET(
    current: SCoord,
    target: SCoord,
    step_size: float = 0.1,
) -> SCoord:
    """
    TARGET operator: Move one step toward target state.

    Single step of gradient-based navigation toward target.

    Args:
        current: Current S-entropy coordinate
        target: Target S-entropy coordinate
        step_size: Step size for navigation

    Returns:
        Updated SCoord closer to target
    """
    grad = current.gradient(target)

    return current.update(
        delta_sk=step_size * grad[0],
        delta_st=step_size * grad[1],
        delta_se=step_size * grad[2],
    )


def SATISFY(
    state: SCoord,
    constraint: Callable[[SCoord], float],
    tolerance: float = 1e-6,
) -> bool:
    """
    SATISFY operator: Check if state satisfies constraint.

    Args:
        state: State to check
        constraint: Constraint function (returns 0 when satisfied)
        tolerance: Satisfaction tolerance

    Returns:
        True if constraint satisfied within tolerance
    """
    return abs(constraint(state)) < tolerance


def EQUILIBRIUM(
    initial_state: MentalState,
    dynamics: Callable[[MentalState, float], MentalState],
    dt: float = 0.01,
    max_time: float = 100.0,
    tolerance: float = 1e-4,
) -> Tuple[MentalState, bool, List[float]]:
    """
    EQUILIBRIUM operator: Find equilibrium state.

    Evolves system until equilibrium is reached (consciousness stabilizes)
    or max_time exceeded.

    Args:
        initial_state: Starting mental state
        dynamics: Dynamics function f(state, dt) -> new_state
        dt: Time step
        max_time: Maximum simulation time
        tolerance: Equilibrium tolerance

    Returns:
        (final_state, converged, consciousness_history)
    """
    current = initial_state
    prev_consciousness = current.consciousness
    consciousness_history = [prev_consciousness]

    t = 0.0
    while t < max_time:
        current = dynamics(current, dt)
        t += dt

        consciousness_history.append(current.consciousness)

        # Check for equilibrium
        delta_C = abs(current.consciousness - prev_consciousness)
        if delta_C < tolerance:
            return current, True, consciousness_history

        prev_consciousness = current.consciousness

    return current, False, consciousness_history


def _compute_constraint_gradient(
    state: SCoord,
    constraints: List[Callable[[SCoord], float]],
    epsilon: float = 1e-6,
) -> np.ndarray:
    """
    Compute numerical gradient of constraint violations.

    Args:
        state: Current state
        constraints: List of constraint functions
        epsilon: Finite difference step

    Returns:
        Gradient vector [d/dSk, d/dSt, d/dSe]
    """
    grad = np.zeros(3)

    for i, (delta_name, delta_val) in enumerate(
        [("delta_sk", epsilon), ("delta_st", epsilon), ("delta_se", epsilon)]
    ):
        # Perturb in positive direction
        kwargs_plus = {delta_name.replace("delta_", "delta_"): epsilon}
        if i == 0:
            state_plus = state.update(delta_sk=epsilon)
            state_minus = state.update(delta_sk=-epsilon)
        elif i == 1:
            state_plus = state.update(delta_st=epsilon)
            state_minus = state.update(delta_st=-epsilon)
        else:
            state_plus = state.update(delta_se=epsilon)
            state_minus = state.update(delta_se=-epsilon)

        # Compute gradient for each constraint
        for constraint in constraints:
            grad[i] += (constraint(state_plus) - constraint(state_minus)) / (2 * epsilon)

    return grad


def recurrence_constraint(
    initial: SCoord,
    epsilon: float = 0.1,
) -> Callable[[SCoord], float]:
    """
    Create Poincare recurrence constraint.

    The constraint is satisfied when ||state - initial|| < epsilon.

    Args:
        initial: Initial state to return to
        epsilon: Recurrence tolerance

    Returns:
        Constraint function
    """

    def constraint(state: SCoord) -> float:
        return max(0, state.distance(initial) - epsilon)

    return constraint


def equilibrium_constraint(
    target_consciousness: float,
    tolerance: float = 0.1,
) -> Callable[[MentalState], float]:
    """
    Create equilibrium constraint for consciousness level.

    Args:
        target_consciousness: Target consciousness level
        tolerance: Tolerance around target

    Returns:
        Constraint function
    """

    def constraint(state: MentalState) -> float:
        return max(0, abs(state.consciousness - target_consciousness) - tolerance)

    return constraint
