"""
CircuitState: Circuit regime detection and state management.

Implements circuit state with regime detection for fluidic/electronic
hybrid computing systems. Maps physical circuit dynamics to the
categorical partition framework.
"""

from dataclasses import dataclass
from typing import Optional, List, Tuple
from enum import Enum, auto
import numpy as np

from ..constants import RE_LAMINAR_MAX, RE_TURBULENT_MIN


class CircuitRegime(Enum):
    """
    Circuit operating regimes.

    These regimes characterize the dynamical behavior of the
    hybrid microfluidic-electronic circuit.
    """

    LAMINAR = auto()  # Low Re, linear flow, predictable
    TRANSITIONAL = auto()  # Intermediate Re, mixed behavior
    TURBULENT = auto()  # High Re, chaotic, unpredictable
    OSCILLATORY = auto()  # Periodic behavior, limit cycles
    BISTABLE = auto()  # Two stable states, switching
    CHAOTIC = auto()  # Deterministic chaos, strange attractors
    PHASE_LOCKED = auto()  # Synchronized oscillators
    HIERARCHICAL = auto()  # Multi-scale cascade active


@dataclass
class CircuitState:
    """
    Circuit state with regime detection.

    Represents the instantaneous state of the hybrid circuit,
    including electrical, fluidic, and phase variables.

    Attributes:
        voltage: Voltage level (V)
        current: Current flow (A)
        reynolds_number: Flow regime indicator (dimensionless)
        phase: Oscillation phase (radians)
        frequency: Oscillation frequency (Hz)
        coherence: Phase coherence R in [0, 1]
        depth: Hierarchical depth D in [0, 1]
        variance: State variance sigma^2
    """

    voltage: float
    current: float
    reynolds_number: float
    phase: float = 0.0
    frequency: float = 0.0
    coherence: float = 0.0  # Kuramoto order parameter R
    depth: float = 0.0  # Hierarchical depth D
    variance: float = 0.0  # State variance

    _regime_override: Optional[CircuitRegime] = None

    @property
    def regime(self) -> CircuitRegime:
        """
        Detect current operating regime from state variables.

        Uses Reynolds number, coherence, and depth to determine
        the dynamical regime.

        Returns:
            CircuitRegime enum value
        """
        if self._regime_override is not None:
            return self._regime_override

        # Hierarchical takes precedence if depth is high
        if self.depth >= 0.6:
            return CircuitRegime.HIERARCHICAL

        # Phase-locked if coherence is very high
        if self.coherence > 0.8:
            return CircuitRegime.PHASE_LOCKED

        # Reynolds number based regimes
        Re = self.reynolds_number

        if Re < RE_LAMINAR_MAX:
            if self.coherence > 0.5:
                return CircuitRegime.OSCILLATORY
            return CircuitRegime.LAMINAR
        elif Re > RE_TURBULENT_MIN:
            if self.variance > 1.0:
                return CircuitRegime.CHAOTIC
            return CircuitRegime.TURBULENT
        else:
            # Transitional regime
            if abs(self.coherence - 0.5) < 0.1:
                return CircuitRegime.BISTABLE
            return CircuitRegime.TRANSITIONAL

    @property
    def power(self) -> float:
        """
        Compute power dissipation P = V * I.

        Returns:
            Power in Watts
        """
        return self.voltage * self.current

    @property
    def impedance(self) -> complex:
        """
        Compute complex impedance.

        Z = V/I * exp(i*phase)

        Returns:
            Complex impedance
        """
        if abs(self.current) < 1e-12:
            return complex(float("inf"), 0)

        magnitude = self.voltage / self.current
        return magnitude * np.exp(1j * self.phase)

    @property
    def resistance(self) -> float:
        """
        Compute DC resistance R = V/I.

        Returns:
            Resistance in Ohms
        """
        if abs(self.current) < 1e-12:
            return float("inf")
        return self.voltage / self.current

    @property
    def reactance(self) -> float:
        """
        Compute reactance (imaginary part of impedance).

        Returns:
            Reactance in Ohms
        """
        return float(self.impedance.imag)

    def is_stable(self, threshold: float = 0.1) -> bool:
        """
        Check if state is stable (low variance regime).

        Args:
            threshold: Variance threshold for stability

        Returns:
            True if state is stable
        """
        stable_regimes = {
            CircuitRegime.LAMINAR,
            CircuitRegime.BISTABLE,
            CircuitRegime.PHASE_LOCKED,
        }
        return self.regime in stable_regimes and self.variance < threshold

    def is_oscillating(self) -> bool:
        """
        Check if circuit is in oscillatory regime.

        Returns:
            True if oscillating
        """
        return self.regime in {CircuitRegime.OSCILLATORY, CircuitRegime.PHASE_LOCKED}

    def detect_oscillation(
        self, voltage_history: List[float], dt: float
    ) -> Tuple[bool, float]:
        """
        Detect oscillatory behavior from voltage history.

        Uses zero-crossing analysis to estimate frequency.

        Args:
            voltage_history: List of recent voltage values
            dt: Time step between samples

        Returns:
            (is_oscillating, frequency_hz)
        """
        if len(voltage_history) < 10:
            return False, 0.0

        v = np.array(voltage_history)
        v_centered = v - np.mean(v)

        # Count zero crossings
        crossings = np.sum(np.diff(np.sign(v_centered)) != 0)

        if crossings < 2:
            return False, 0.0

        # Frequency = crossings / (2 * total_time)
        total_time = len(voltage_history) * dt
        frequency = crossings / (2 * total_time)

        return True, float(frequency)

    def step(
        self,
        dV_dt: float,
        dI_dt: float,
        dt: float,
        dR_dt: float = 0.0,
    ) -> "CircuitState":
        """
        Evolve circuit state by one time step.

        Uses Euler integration for simplicity.

        Args:
            dV_dt: Voltage time derivative
            dI_dt: Current time derivative
            dt: Time step
            dR_dt: Coherence time derivative (optional)

        Returns:
            New CircuitState after time step
        """
        new_voltage = self.voltage + dV_dt * dt
        new_current = self.current + dI_dt * dt
        new_phase = (self.phase + 2 * np.pi * self.frequency * dt) % (2 * np.pi)
        new_coherence = max(0.0, min(1.0, self.coherence + dR_dt * dt))

        return CircuitState(
            voltage=new_voltage,
            current=new_current,
            reynolds_number=self.reynolds_number,
            phase=new_phase,
            frequency=self.frequency,
            coherence=new_coherence,
            depth=self.depth,
            variance=self.variance,
        )

    def update_reynolds(self, velocity: float, length: float, viscosity: float) -> "CircuitState":
        """
        Update Reynolds number from flow parameters.

        Re = (rho * v * L) / mu = v * L / nu

        Args:
            velocity: Flow velocity (m/s)
            length: Characteristic length (m)
            viscosity: Kinematic viscosity (m^2/s)

        Returns:
            New CircuitState with updated Reynolds number
        """
        new_Re = velocity * length / viscosity

        return CircuitState(
            voltage=self.voltage,
            current=self.current,
            reynolds_number=new_Re,
            phase=self.phase,
            frequency=self.frequency,
            coherence=self.coherence,
            depth=self.depth,
            variance=self.variance,
        )

    def compute_variance(self, values: np.ndarray) -> "CircuitState":
        """
        Update variance from array of values.

        sigma^2 = <(x - <x>)^2>

        Args:
            values: Array of values to compute variance from

        Returns:
            New CircuitState with updated variance
        """
        new_variance = float(np.var(values))

        return CircuitState(
            voltage=self.voltage,
            current=self.current,
            reynolds_number=self.reynolds_number,
            phase=self.phase,
            frequency=self.frequency,
            coherence=self.coherence,
            depth=self.depth,
            variance=new_variance,
        )

    def phase_lock(self, target_phase: float, strength: float, dt: float) -> "CircuitState":
        """
        Apply phase-locking dynamics.

        d(phase)/dt = -strength * sin(phase - target)

        Args:
            target_phase: Target phase to lock to
            strength: Coupling strength
            dt: Time step

        Returns:
            New CircuitState with updated phase
        """
        d_phase = -strength * np.sin(self.phase - target_phase) * dt
        new_phase = (self.phase + d_phase) % (2 * np.pi)

        # Update coherence based on phase distance
        phase_diff = abs(new_phase - target_phase)
        new_coherence = 1.0 - min(phase_diff, 2 * np.pi - phase_diff) / np.pi

        return CircuitState(
            voltage=self.voltage,
            current=self.current,
            reynolds_number=self.reynolds_number,
            phase=new_phase,
            frequency=self.frequency,
            coherence=new_coherence,
            depth=self.depth,
            variance=self.variance,
        )

    @classmethod
    def initial(
        cls,
        voltage: float = 0.0,
        current: float = 0.0,
        reynolds: float = 1000.0,
    ) -> "CircuitState":
        """
        Create initial circuit state.

        Args:
            voltage: Initial voltage
            current: Initial current
            reynolds: Initial Reynolds number

        Returns:
            Initial CircuitState
        """
        return cls(
            voltage=voltage,
            current=current,
            reynolds_number=reynolds,
            phase=0.0,
            frequency=0.0,
            coherence=0.0,
            depth=0.0,
            variance=0.0,
        )

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"CircuitState(V={self.voltage:.3f}, I={self.current:.6f}, "
            f"Re={self.reynolds_number:.0f}, regime={self.regime.name})"
        )
