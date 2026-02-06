"""
Neural Operators: CONSCIOUSNESS, MEMORY, DREAM, WAKE.

Implements neural-specific operations for the Virtual Brain framework.
These operators model consciousness, memory, and sleep/wake transitions.
"""

from typing import Tuple, List, Optional
import numpy as np

from ..core.types import MentalState, SCoord
from ..core.constants import TAU_PERCEPTION, TAU_THOUGHT, H_PLUS_FREQUENCY


def CONSCIOUSNESS(
    p_decay: float,
    t_decay: float,
    gamma: float = 1.0,
    gamma_f: float = 1.0,
) -> float:
    """
    CONSCIOUSNESS operator: Compute consciousness level.

    C = P_decay ∩ T_decay = P_decay * T_decay * gamma * gamma_f

    Consciousness emerges from the intersection of perception
    and thought decay dynamics, modulated by phase coherence.

    Args:
        p_decay: Perception decay level in [0, 1]
        t_decay: Thought decay level in [0, 1]
        gamma: Phase coherence (Kuramoto R) in [0, 1]
        gamma_f: Frequency coherence in [0, 1]

    Returns:
        Consciousness level in [0, 1]
    """
    return p_decay * t_decay * gamma * gamma_f


def CONSCIOUSNESS_FREQUENCY(
    omega_t: float = 2 * np.pi * 10,  # 10 Hz thought
    omega_p: float = 2 * np.pi * 20,  # 20 Hz perception
) -> float:
    """
    Compute consciousness frequency from thought and perception frequencies.

    omega_c = (omega_T * omega_P) / (omega_T + omega_P)

    This is the intersection frequency, approximately 2.5 Hz.

    Args:
        omega_t: Thought angular frequency (rad/s)
        omega_p: Perception angular frequency (rad/s)

    Returns:
        Consciousness angular frequency (rad/s)
    """
    return (omega_t * omega_p) / (omega_t + omega_p)


def MEMORY(
    H_field: np.ndarray,
    dt: float,
) -> float:
    """
    MEMORY operator: Compute accumulated emotional change.

    M = integral(dH/dt) dt

    Memory is the accumulated change in the emotional field -
    "how the field got here". This enables temporal differentiation
    of thoughts within the same emotional context.

    Args:
        H_field: Array of H+ field values over time
        dt: Time step between samples

    Returns:
        Total memory (accumulated change)
    """
    if len(H_field) < 2:
        return 0.0

    # Compute derivative dH/dt
    dH_dt = np.diff(H_field) / dt

    # Integrate
    M = np.sum(dH_dt) * dt

    return float(M)


def MEMORY_DIFFERENTIAL(
    H_current: float,
    H_previous: float,
    dt: float,
) -> float:
    """
    Compute instantaneous memory differential.

    dM/dt = dH/dt

    Args:
        H_current: Current H+ field value
        H_previous: Previous H+ field value
        dt: Time step

    Returns:
        Rate of memory change
    """
    return (H_current - H_previous) / dt


def DREAM(state: MentalState) -> MentalState:
    """
    DREAM operator: Transition to dream state.

    Sets P_decay = 0, removing perceptual constraint.
    Thought trajectories become unbounded, navigating
    full S-space without categorical completion requirements.

    Args:
        state: Current mental state

    Returns:
        New MentalState in dream mode
    """
    return state.enter_dream()


def WAKE(
    state: MentalState,
    perception_level: float = 1.0,
) -> MentalState:
    """
    WAKE operator: Transition to awake state.

    Restores perception decay, constraining thought trajectories
    to perceptible regions of S-space.

    Args:
        state: Current mental state
        perception_level: Initial perception level (default: 1.0)

    Returns:
        New MentalState in awake mode
    """
    return state.wake(perception_level)


def DECAY_EVOLVE(
    curve: float,
    tau: float,
    dt: float,
    input_rate: float = 0.0,
) -> float:
    """
    Evolve decay curve by one time step.

    d(curve)/dt = -curve/tau + input

    Args:
        curve: Current decay level
        tau: Time constant
        dt: Time step
        input_rate: Input rate (refreshes decay)

    Returns:
        Updated decay level
    """
    d_curve = (-curve / tau + input_rate) * dt
    return max(0.0, min(1.0, curve + d_curve))


def RETRIEVE_MEMORY(
    M_now: float,
    M_t0: float,
    H_now: float,
) -> float:
    """
    Retrieve past emotional state from memory.

    H(t_0) = H_now - (M(now) - M(t_0))

    Args:
        M_now: Current memory value
        M_t0: Memory value at time t_0
        H_now: Current emotional field

    Returns:
        Estimated emotional field at t_0
    """
    return H_now - (M_now - M_t0)


def PREDICT_EMOTION(
    H_now: float,
    dM_dt: float,
    delta_t: float,
) -> float:
    """
    Predict future emotional state from memory trajectory.

    H(t + dt) ≈ H(t) + (dM/dt) * dt

    The memory trajectory encodes the predictive signal for
    where emotions are going.

    Args:
        H_now: Current emotional field
        dM_dt: Current rate of memory change
        delta_t: Time into future

    Returns:
        Predicted emotional field
    """
    return H_now + dM_dt * delta_t


def evolve_mental_state(
    state: MentalState,
    dt: float,
    tau_p: float = TAU_PERCEPTION,
    tau_t: float = TAU_THOUGHT,
    perception_input: float = 0.0,
    thought_input: float = 0.0,
    dH_dt: float = 0.0,
) -> MentalState:
    """
    Evolve mental state by one time step.

    Applies decay dynamics to perception and thought,
    and accumulates memory.

    Args:
        state: Current mental state
        dt: Time step
        tau_p: Perception decay constant
        tau_t: Thought decay constant
        perception_input: Perception input rate
        thought_input: Thought input rate
        dH_dt: Rate of emotional field change

    Returns:
        Evolved MentalState
    """
    # Evolve decay curves
    new_p_decay = DECAY_EVOLVE(state.p_decay, tau_p, dt, perception_input)
    new_t_decay = DECAY_EVOLVE(state.t_decay, tau_t, dt, thought_input)

    # Update memory
    new_M = state.M + dH_dt * dt

    return MentalState(
        gamma=state.gamma,
        gamma_f=state.gamma_f,
        M=new_M,
        s_coord=state.s_coord,
        partition=state.partition,
        timestamp=state.timestamp + dt,
        p_decay=new_p_decay,
        t_decay=new_t_decay,
        trajectory=state.trajectory,
    )


def consciousness_time_series(
    initial_state: MentalState,
    duration: float,
    dt: float = 0.01,
    perception_profile: Optional[np.ndarray] = None,
) -> Tuple[np.ndarray, np.ndarray, List[MentalState]]:
    """
    Generate consciousness time series.

    Args:
        initial_state: Starting mental state
        duration: Total duration
        dt: Time step
        perception_profile: Optional perception input over time

    Returns:
        (times, consciousness_values, states)
    """
    n_steps = int(duration / dt)
    times = np.linspace(0, duration, n_steps)
    consciousness = np.zeros(n_steps)
    states = []

    state = initial_state

    for i in range(n_steps):
        states.append(state)
        consciousness[i] = state.consciousness

        # Get perception input
        if perception_profile is not None and i < len(perception_profile):
            p_input = perception_profile[i]
        else:
            p_input = 0.1  # Default small input

        state = evolve_mental_state(state, dt, perception_input=p_input)

    return times, consciousness, states
