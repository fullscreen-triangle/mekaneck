"""
Dynamics Operators: KURAMOTO, PHASE_LOCK, CASCADE, VARIANCE.

Implements dynamical system operators for oscillatory computing,
including Kuramoto synchronization and multi-scale cascade dynamics.
"""

from dataclasses import dataclass
from typing import List, Tuple, Optional
import numpy as np

from ..core.constants import BIOLOGICAL_GEAR_RATIOS, DEFAULT_COUPLING_STRENGTH


@dataclass
class KuramotoState:
    """
    State of Kuramoto oscillator network.

    The Kuramoto model describes synchronization of coupled oscillators:
    d(phi_i)/dt = omega_i + (K/N) * sum_j sin(phi_j - phi_i)

    Attributes:
        phases: Array of oscillator phases in [0, 2*pi)
        natural_frequencies: Array of natural frequencies (rad/s)
        coupling_strength: Global coupling strength K
    """

    phases: np.ndarray
    natural_frequencies: np.ndarray
    coupling_strength: float

    @classmethod
    def random(
        cls,
        n_oscillators: int,
        mean_frequency: float = 10.0,
        frequency_std: float = 2.0,
        coupling: float = DEFAULT_COUPLING_STRENGTH,
    ) -> "KuramotoState":
        """
        Create random Kuramoto state.

        Args:
            n_oscillators: Number of oscillators
            mean_frequency: Mean natural frequency (Hz)
            frequency_std: Standard deviation of frequencies
            coupling: Coupling strength

        Returns:
            Random KuramotoState
        """
        phases = np.random.uniform(0, 2 * np.pi, n_oscillators)
        # Convert to rad/s
        frequencies = np.random.normal(mean_frequency, frequency_std, n_oscillators) * 2 * np.pi

        return cls(
            phases=phases,
            natural_frequencies=frequencies,
            coupling_strength=coupling,
        )

    @property
    def n_oscillators(self) -> int:
        """Number of oscillators."""
        return len(self.phases)


def KURAMOTO(state: KuramotoState, dt: float) -> KuramotoState:
    """
    KURAMOTO operator: Evolve Kuramoto oscillator network.

    d(phi_i)/dt = omega_i + (K/N) * sum_j sin(phi_j - phi_i)

    This implements the mean-field Kuramoto model for phase synchronization.

    Args:
        state: Current Kuramoto state
        dt: Time step

    Returns:
        Updated KuramotoState
    """
    N = state.n_oscillators
    K = state.coupling_strength
    omega = state.natural_frequencies
    phases = state.phases

    # Compute coupling term for all oscillators (vectorized)
    # For each oscillator i: sum_j sin(phi_j - phi_i)
    phase_diff = phases[np.newaxis, :] - phases[:, np.newaxis]  # N x N matrix
    coupling = (K / N) * np.sum(np.sin(phase_diff), axis=1)

    # Update phases using Euler integration
    d_phases = omega + coupling
    new_phases = np.mod(phases + d_phases * dt, 2 * np.pi)

    return KuramotoState(
        phases=new_phases,
        natural_frequencies=omega,
        coupling_strength=K,
    )


def PHASE_LOCK(phases: np.ndarray) -> Tuple[float, float]:
    """
    PHASE_LOCK operator: Compute Kuramoto order parameter.

    R = (1/N) * |sum_j exp(i * phi_j)|
    Psi = arg(sum_j exp(i * phi_j))

    R measures synchronization:
    - R = 0: Incoherent (random phases)
    - R = 1: Perfect synchronization

    Args:
        phases: Array of oscillator phases

    Returns:
        (R, Psi) - order parameter magnitude and mean phase
    """
    z = np.mean(np.exp(1j * phases))
    R = float(np.abs(z))
    Psi = float(np.angle(z))

    return R, Psi


def CASCADE(
    input_frequency: float,
    gear_ratios: Optional[List[float]] = None,
) -> List[float]:
    """
    CASCADE operator: Multi-scale frequency cascade.

    omega_out[i] = G[i] * omega_out[i-1]

    Implements 8-level biological frequency hierarchy from
    quantum coherence to environmental coupling.

    Args:
        input_frequency: Input frequency in Hz
        gear_ratios: List of gear ratios (default: biological)

    Returns:
        List of frequencies at each cascade level
    """
    if gear_ratios is None:
        gear_ratios = list(BIOLOGICAL_GEAR_RATIOS)

    frequencies = [input_frequency]

    for G in gear_ratios:
        next_freq = frequencies[-1] * G
        frequencies.append(next_freq)

    return frequencies


def VARIANCE(values: np.ndarray) -> float:
    """
    VARIANCE operator: Compute variance of values.

    sigma^2 = <(x - <x>)^2>

    Used for phase coherence analysis and regime detection.

    Args:
        values: Array of values

    Returns:
        Variance
    """
    return float(np.var(values))


def COHERENCE(phases: np.ndarray) -> float:
    """
    COHERENCE operator: Compute phase coherence.

    Alias for the R component of PHASE_LOCK.

    Args:
        phases: Array of phases

    Returns:
        Coherence R in [0, 1]
    """
    R, _ = PHASE_LOCK(phases)
    return R


def kuramoto_with_drug(
    state: KuramotoState,
    drug_concentration: float,
    K_agg: float,
    dt: float,
) -> KuramotoState:
    """
    Drug-modified Kuramoto dynamics.

    K_modified = K_0 * (1 + [Drug] * K_agg)

    The drug concentration modulates the effective coupling strength.

    Args:
        state: Current Kuramoto state
        drug_concentration: Drug concentration in M
        K_agg: Aggregation constant in M^-1
        dt: Time step

    Returns:
        Updated KuramotoState
    """
    K_modified = state.coupling_strength * (1 + drug_concentration * K_agg)

    modified_state = KuramotoState(
        phases=state.phases,
        natural_frequencies=state.natural_frequencies,
        coupling_strength=K_modified,
    )

    return KURAMOTO(modified_state, dt)


def simulate_kuramoto(
    initial_state: KuramotoState,
    duration: float,
    dt: float = 0.001,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Simulate Kuramoto dynamics over time.

    Args:
        initial_state: Initial Kuramoto state
        duration: Simulation duration
        dt: Time step

    Returns:
        (times, order_parameters, mean_phases)
    """
    n_steps = int(duration / dt)
    times = np.linspace(0, duration, n_steps)
    order_params = np.zeros(n_steps)
    mean_phases = np.zeros(n_steps)

    state = initial_state

    for i in range(n_steps):
        R, Psi = PHASE_LOCK(state.phases)
        order_params[i] = R
        mean_phases[i] = Psi

        state = KURAMOTO(state, dt)

    return times, order_params, mean_phases


def critical_coupling(
    frequency_std: float,
    n_oscillators: int,
) -> float:
    """
    Estimate critical coupling for synchronization onset.

    K_c ≈ 2 * sigma_omega / pi (for Lorentzian distribution)

    Args:
        frequency_std: Standard deviation of natural frequencies
        n_oscillators: Number of oscillators

    Returns:
        Critical coupling strength
    """
    return 2 * frequency_std / np.pi


def phase_velocity(
    coupling_strength: float,
    diffusion_coeff: float,
) -> float:
    """
    Compute phase propagation velocity.

    V_phase = sqrt(K * D)

    Args:
        coupling_strength: Kuramoto coupling K
        diffusion_coeff: Diffusion coefficient D

    Returns:
        Phase velocity
    """
    return np.sqrt(coupling_strength * diffusion_coeff)
