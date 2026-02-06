"""
PoincareComputer: Main Poincare computing engine.

Implements the Poincare computing paradigm for Virtual Brain simulation.
Programs specify completion conditions, and the engine navigates
backward through S-entropy space to satisfy constraints.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import numpy as np

from ..core.types import SCoord, MentalState, PartitionCoord
from ..core.constants import DEFAULT_COUPLING_STRENGTH, DEFAULT_N_OSCILLATORS
from ..operators.poincare_ops import COMPLETE, TARGET, EQUILIBRIUM
from ..operators.dynamics_ops import KURAMOTO, PHASE_LOCK, CASCADE, KuramotoState
from ..operators.neural_ops import evolve_mental_state, CONSCIOUSNESS


@dataclass
class ComputeResult:
    """Result of Poincare computation."""

    success: bool
    final_state: MentalState
    iterations: int
    convergence_history: List[float]
    trajectory: List[SCoord] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class PoincareComputer:
    """
    Main Poincare computing engine for Virtual Brain.

    Implements constraint satisfaction computing through
    equilibrium finding in categorical state space.

    The key insight is backward determination: specifying the
    completion state determines what the trajectory MUST have been.
    """

    def __init__(
        self,
        n_oscillators: int = DEFAULT_N_OSCILLATORS,
        coupling_strength: float = DEFAULT_COUPLING_STRENGTH,
        n_partition_levels: int = 10,
    ):
        """
        Initialize Poincare Computer.

        Args:
            n_oscillators: Number of Kuramoto oscillators
            coupling_strength: Default coupling strength K
            n_partition_levels: Max partition level n
        """
        self.n_oscillators = n_oscillators
        self.coupling_strength = coupling_strength
        self.n_partition_levels = n_partition_levels

        # Initialize Kuramoto network
        self.kuramoto_state = self._init_kuramoto()

        # State history for memory
        self.state_history: List[MentalState] = []

    def _init_kuramoto(self) -> KuramotoState:
        """Initialize Kuramoto oscillator network."""
        return KuramotoState.random(
            n_oscillators=self.n_oscillators,
            mean_frequency=10.0,
            frequency_std=2.0,
            coupling=self.coupling_strength,
        )

    def compute_consciousness(
        self,
        initial_state: MentalState,
        target_consciousness: float = 0.8,
        max_iterations: int = 1000,
        dt: float = 0.01,
    ) -> ComputeResult:
        """
        Compute state achieving target consciousness level.

        Uses Poincare completion to find state satisfying
        C = gamma * gamma_f = target.

        Args:
            initial_state: Starting mental state
            target_consciousness: Target consciousness level
            max_iterations: Maximum iterations
            dt: Time step

        Returns:
            ComputeResult with final state
        """
        convergence_history = []
        trajectory = []
        current = initial_state

        if current.s_coord:
            trajectory.append(current.s_coord)

        for iteration in range(max_iterations):
            # Evolve Kuramoto network
            self.kuramoto_state = KURAMOTO(self.kuramoto_state, dt)

            # Compute order parameter
            R, Psi = PHASE_LOCK(self.kuramoto_state.phases)

            # Update mental state with new coherence
            current = current.transition_to(new_gamma=R)

            # Evolve decay dynamics
            current = evolve_mental_state(current, dt)

            # Track convergence
            C = current.consciousness
            convergence_history.append(C)

            if current.s_coord:
                trajectory.append(current.s_coord)

            # Check convergence
            if abs(C - target_consciousness) < 0.01:
                return ComputeResult(
                    success=True,
                    final_state=current,
                    iterations=iteration,
                    convergence_history=convergence_history,
                    trajectory=trajectory,
                    metadata={"target": target_consciousness, "achieved": C},
                )

            # Adaptive coupling adjustment to reach target
            if C < target_consciousness:
                self.kuramoto_state = KuramotoState(
                    phases=self.kuramoto_state.phases,
                    natural_frequencies=self.kuramoto_state.natural_frequencies,
                    coupling_strength=self.kuramoto_state.coupling_strength * 1.01,
                )
            else:
                self.kuramoto_state = KuramotoState(
                    phases=self.kuramoto_state.phases,
                    natural_frequencies=self.kuramoto_state.natural_frequencies,
                    coupling_strength=self.kuramoto_state.coupling_strength * 0.99,
                )

        return ComputeResult(
            success=False,
            final_state=current,
            iterations=max_iterations,
            convergence_history=convergence_history,
            trajectory=trajectory,
            metadata={"target": target_consciousness, "achieved": current.consciousness},
        )

    def navigate_categorical_space(
        self,
        start: SCoord,
        target: SCoord,
        step_size: float = 0.1,
        max_steps: int = 100,
    ) -> List[SCoord]:
        """
        Navigate from start to target in S-entropy space.

        Implements O(log n) navigation via TARGET operator.

        Args:
            start: Starting S-entropy coordinate
            target: Target S-entropy coordinate
            step_size: Step size per iteration
            max_steps: Maximum navigation steps

        Returns:
            Path of SCoord from start to target
        """
        path = [start]
        current = start

        for _ in range(max_steps):
            if current.distance(target) < step_size:
                path.append(target)
                break

            current = TARGET(current, target, step_size)
            path.append(current)

        return path

    def apply_drug_perturbation(
        self,
        state: MentalState,
        drug_concentration: float,
        K_agg: float = 1e4,
        equilibration_steps: int = 100,
        dt: float = 0.01,
    ) -> MentalState:
        """
        Apply drug perturbation to mental state.

        Modifies coupling strength and evolves system to new equilibrium.

        Args:
            state: Current mental state
            drug_concentration: Drug concentration in M
            K_agg: Aggregation constant M^-1
            equilibration_steps: Steps to equilibrate
            dt: Time step

        Returns:
            Perturbed mental state after equilibration
        """
        # Modify coupling strength based on drug
        K_modified = self.coupling_strength * (1 + drug_concentration * K_agg)

        # Create modified Kuramoto state
        modified_kuramoto = KuramotoState(
            phases=self.kuramoto_state.phases,
            natural_frequencies=self.kuramoto_state.natural_frequencies,
            coupling_strength=K_modified,
        )

        # Evolve to new equilibrium
        for _ in range(equilibration_steps):
            modified_kuramoto = KURAMOTO(modified_kuramoto, dt)

        # Compute new coherence
        R, _ = PHASE_LOCK(modified_kuramoto.phases)

        # Update internal state
        self.kuramoto_state = modified_kuramoto

        return state.transition_to(new_gamma=R)

    def run_simulation(
        self,
        initial_state: MentalState,
        duration: float,
        dt: float = 0.01,
    ) -> List[MentalState]:
        """
        Run full simulation for given duration.

        Args:
            initial_state: Starting state
            duration: Simulation duration
            dt: Time step

        Returns:
            List of mental states over time
        """
        states = [initial_state]
        current = initial_state
        t = 0.0

        while t < duration:
            # Evolve Kuramoto
            self.kuramoto_state = KURAMOTO(self.kuramoto_state, dt)

            # Compute order parameter
            R, _ = PHASE_LOCK(self.kuramoto_state.phases)

            # Update state
            current = current.transition_to(new_gamma=R)
            current = evolve_mental_state(current, dt)

            states.append(current)
            self.state_history.append(current)
            t += dt

        return states

    def find_equilibrium(
        self,
        initial_state: MentalState,
        max_time: float = 100.0,
        dt: float = 0.01,
        tolerance: float = 1e-4,
    ) -> ComputeResult:
        """
        Find equilibrium state from initial conditions.

        Args:
            initial_state: Starting state
            max_time: Maximum simulation time
            dt: Time step
            tolerance: Convergence tolerance

        Returns:
            ComputeResult with equilibrium state
        """

        def dynamics(state, dt):
            self.kuramoto_state = KURAMOTO(self.kuramoto_state, dt)
            R, _ = PHASE_LOCK(self.kuramoto_state.phases)
            new_state = state.transition_to(new_gamma=R)
            return evolve_mental_state(new_state, dt)

        final_state, converged, history = EQUILIBRIUM(
            initial_state, dynamics, dt, max_time, tolerance
        )

        return ComputeResult(
            success=converged,
            final_state=final_state,
            iterations=len(history),
            convergence_history=history,
        )

    def dream_simulation(
        self,
        initial_state: MentalState,
        duration: float,
        dt: float = 0.01,
    ) -> List[MentalState]:
        """
        Simulate dream state (P_decay = 0).

        Thought trajectories are unbounded, navigating full S-space.

        Args:
            initial_state: Starting state
            duration: Dream duration
            dt: Time step

        Returns:
            List of mental states during dream
        """
        # Enter dream state
        dream_state = initial_state.enter_dream()

        return self.run_simulation(dream_state, duration, dt)

    def wake_transition(
        self,
        dream_state: MentalState,
        wake_duration: float = 1.0,
        dt: float = 0.01,
    ) -> List[MentalState]:
        """
        Simulate transition from dream to wake.

        Args:
            dream_state: State at end of dream
            wake_duration: Duration of wake transition
            dt: Time step

        Returns:
            List of mental states during transition
        """
        # Wake up
        wake_state = dream_state.wake(perception_level=0.1)

        states = [wake_state]
        current = wake_state
        t = 0.0

        while t < wake_duration:
            # Gradually increase perception
            new_p_decay = min(1.0, current.p_decay + dt)
            current = current.transition_to(new_p_decay=new_p_decay)

            # Evolve dynamics
            self.kuramoto_state = KURAMOTO(self.kuramoto_state, dt)
            R, _ = PHASE_LOCK(self.kuramoto_state.phases)
            current = current.transition_to(new_gamma=R)

            states.append(current)
            t += dt

        return states

    def reset(self):
        """Reset computer to initial state."""
        self.kuramoto_state = self._init_kuramoto()
        self.state_history = []
