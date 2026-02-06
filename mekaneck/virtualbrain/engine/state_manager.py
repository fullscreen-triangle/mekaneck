"""
StateManager: State transitions and validation.

Manages mental state transitions, validates states, and maintains
state history for the Virtual Brain.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
import numpy as np

from ..core.types import MentalState, SCoord, PartitionCoord
from ..operators.partition_ops import partition_to_sentropy, D_CAT


@dataclass
class TransitionResult:
    """Result of a state transition."""

    success: bool
    from_state: MentalState
    to_state: MentalState
    distance: float
    metadata: Dict[str, Any] = field(default_factory=dict)


class StateManager:
    """
    Manages mental state transitions and validation.

    Ensures state consistency, tracks history, and provides
    utilities for state manipulation.
    """

    def __init__(self, max_history: int = 1000):
        """
        Initialize state manager.

        Args:
            max_history: Maximum states to keep in history
        """
        self.max_history = max_history
        self.history: List[MentalState] = []
        self.current_state: Optional[MentalState] = None

    def initialize(
        self,
        s_coord: Optional[SCoord] = None,
        partition: Optional[PartitionCoord] = None,
    ) -> MentalState:
        """
        Initialize with a new state.

        Args:
            s_coord: Initial S-entropy coordinate
            partition: Initial partition coordinate

        Returns:
            Initial MentalState
        """
        if s_coord is None:
            s_coord = SCoord(sk=0.5, st=0.5, se=0.5)

        state = MentalState.initial(s_coord=s_coord, partition=partition)
        self.current_state = state
        self.history = [state]

        return state

    def transition(
        self,
        target_s_coord: Optional[SCoord] = None,
        target_partition: Optional[PartitionCoord] = None,
        new_gamma: Optional[float] = None,
        new_gamma_f: Optional[float] = None,
    ) -> TransitionResult:
        """
        Transition to new state.

        Args:
            target_s_coord: Target S-entropy coordinate
            target_partition: Target partition coordinate
            new_gamma: New phase coherence
            new_gamma_f: New frequency coherence

        Returns:
            TransitionResult with transition details
        """
        if self.current_state is None:
            raise RuntimeError("State manager not initialized")

        old_state = self.current_state

        # Compute transition distance
        distance = 0.0
        if target_s_coord and old_state.s_coord:
            distance = old_state.s_coord.distance(target_s_coord)
        elif target_partition and old_state.partition:
            distance = D_CAT(old_state.partition, target_partition)

        # Create new state
        new_state = old_state.transition_to(
            new_s_coord=target_s_coord,
            new_partition=target_partition,
            new_gamma=new_gamma,
            new_gamma_f=new_gamma_f,
        )

        # Update current and history
        self.current_state = new_state
        self._add_to_history(new_state)

        return TransitionResult(
            success=True,
            from_state=old_state,
            to_state=new_state,
            distance=distance,
        )

    def validate_state(self, state: MentalState) -> bool:
        """
        Validate that state is consistent.

        Checks:
        - gamma in [0, 1]
        - gamma_f in [0, 1]
        - p_decay in [0, 1]
        - t_decay in [0, 1]
        - S-coordinates in [0, 1]^3

        Args:
            state: State to validate

        Returns:
            True if state is valid
        """
        # Check coherence values
        if not (0 <= state.gamma <= 1):
            return False
        if not (0 <= state.gamma_f <= 1):
            return False
        if not (0 <= state.p_decay <= 1):
            return False
        if not (0 <= state.t_decay <= 1):
            return False

        # Check S-coordinates
        if state.s_coord:
            if not (0 <= state.s_coord.sk <= 1):
                return False
            if not (0 <= state.s_coord.st <= 1):
                return False
            if not (0 <= state.s_coord.se <= 1):
                return False

        return True

    def get_trajectory(self) -> List[SCoord]:
        """
        Get S-entropy trajectory from history.

        Returns:
            List of S-coordinates from history
        """
        return [s.s_coord for s in self.history if s.s_coord is not None]

    def get_consciousness_history(self) -> np.ndarray:
        """
        Get consciousness values from history.

        Returns:
            Array of consciousness values
        """
        return np.array([s.consciousness for s in self.history])

    def get_memory_history(self) -> np.ndarray:
        """
        Get memory values from history.

        Returns:
            Array of memory values
        """
        return np.array([s.M for s in self.history])

    def find_state_at_time(self, t: float) -> Optional[MentalState]:
        """
        Find state closest to given time.

        Args:
            t: Target time

        Returns:
            MentalState closest to time t, or None
        """
        if not self.history:
            return None

        closest = min(self.history, key=lambda s: abs(s.timestamp - t))
        return closest

    def compute_memory_differential(self) -> float:
        """
        Compute current rate of memory change.

        Returns:
            dM/dt at current state
        """
        if len(self.history) < 2:
            return 0.0

        recent = self.history[-1]
        previous = self.history[-2]

        dt = recent.timestamp - previous.timestamp
        if dt == 0:
            return 0.0

        return (recent.M - previous.M) / dt

    def enter_dream_mode(self) -> MentalState:
        """
        Transition current state to dream mode.

        Returns:
            Dream state
        """
        if self.current_state is None:
            raise RuntimeError("State manager not initialized")

        dream_state = self.current_state.enter_dream()
        self.current_state = dream_state
        self._add_to_history(dream_state)

        return dream_state

    def wake_up(self, perception_level: float = 1.0) -> MentalState:
        """
        Transition from dream to awake.

        Args:
            perception_level: Initial perception level

        Returns:
            Awake state
        """
        if self.current_state is None:
            raise RuntimeError("State manager not initialized")

        wake_state = self.current_state.wake(perception_level)
        self.current_state = wake_state
        self._add_to_history(wake_state)

        return wake_state

    def _add_to_history(self, state: MentalState):
        """Add state to history, maintaining max size."""
        self.history.append(state)
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history :]

    def clear_history(self):
        """Clear state history."""
        if self.current_state:
            self.history = [self.current_state]
        else:
            self.history = []

    def summary(self) -> Dict[str, Any]:
        """
        Get summary of current state and history.

        Returns:
            Dictionary with state summary
        """
        if self.current_state is None:
            return {"initialized": False}

        return {
            "initialized": True,
            "current_consciousness": self.current_state.consciousness,
            "current_memory": self.current_state.M,
            "is_dreaming": self.current_state.is_dreaming,
            "is_awake": self.current_state.is_awake,
            "history_length": len(self.history),
            "total_time": self.current_state.timestamp,
        }
