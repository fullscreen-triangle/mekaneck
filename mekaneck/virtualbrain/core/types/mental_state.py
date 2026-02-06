"""
MentalState: Complete mental state representation (gamma, Gamma_f, M).

Encapsulates the mental state triple including trajectory (gamma),
terminus state (Gamma_f), and memory (M). This is the fundamental
unit of the Virtual Brain.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
import numpy as np

from .s_coord import SCoord
from .partition_coord import PartitionCoord


@dataclass
class MentalState:
    """
    Complete mental state representation.

    A mental state is a trajectory-terminus-memory triple:
        M = (gamma, Gamma_f, M)

    Where:
        - gamma: Phase coherence / trajectory through S-space
        - Gamma_f: Terminus state (what the thought IS)
        - M: Memory (accumulated emotional change, how we got here)

    The same thought content in different contexts constitutes
    different mental states because the trajectory differs.

    Attributes:
        gamma: Phase coherence (Kuramoto order parameter R) in [0, 1]
        gamma_f: Frequency coherence (global frequency locking) in [0, 1]
        M: Memory integral (accumulated entropy changes)
        s_coord: Current S-entropy coordinate
        partition: Current partition coordinate
        timestamp: Time of this state
        p_decay: Perception decay level in [0, 1]
        t_decay: Thought decay level in [0, 1]
    """

    gamma: float  # Phase coherence in [0, 1]
    gamma_f: float  # Frequency coherence in [0, 1]
    M: float  # Memory integral

    s_coord: Optional[SCoord] = None
    partition: Optional[PartitionCoord] = None
    timestamp: float = 0.0

    p_decay: float = 1.0  # Perception decay (1 = full perception)
    t_decay: float = 1.0  # Thought decay (1 = full thought)

    # Trajectory history (for complete state tracking)
    trajectory: List[SCoord] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validate state parameters."""
        if not 0.0 <= self.gamma <= 1.0:
            raise ValueError(f"gamma must be in [0, 1], got {self.gamma}")
        if not 0.0 <= self.gamma_f <= 1.0:
            raise ValueError(f"gamma_f must be in [0, 1], got {self.gamma_f}")
        if not 0.0 <= self.p_decay <= 1.0:
            raise ValueError(f"p_decay must be in [0, 1], got {self.p_decay}")
        if not 0.0 <= self.t_decay <= 1.0:
            raise ValueError(f"t_decay must be in [0, 1], got {self.t_decay}")

    @property
    def consciousness(self) -> float:
        """
        Compute consciousness level.

        C = P_decay intersect T_decay

        Consciousness emerges from the intersection of perception
        and thought decay dynamics. Implemented as the product
        (geometric intersection in probability space).

        Returns:
            Consciousness level in [0, 1]
        """
        return self.p_decay * self.t_decay * self.gamma * self.gamma_f

    @property
    def is_conscious(self) -> bool:
        """
        Check if consciousness threshold is met.

        Returns:
            True if consciousness > 0.5
        """
        return self.consciousness > 0.5

    @property
    def is_dreaming(self) -> bool:
        """
        Check if in dream state.

        Dreaming occurs when:
            - P_decay = 0 (no perceptual constraint)
            - T_decay > 0 (thought dynamics persist)
            - High gamma_f (internal coherence)

        Returns:
            True if in dream state
        """
        return self.p_decay < 0.1 and self.t_decay > 0.5 and self.gamma_f > 0.5

    @property
    def is_awake(self) -> bool:
        """
        Check if in awake state.

        Awake state requires:
            - High P_decay (active perception)
            - Moderate T_decay (thought dynamics)
            - High gamma (external synchronization)

        Returns:
            True if in awake state
        """
        return self.p_decay > 0.7 and self.gamma > 0.5

    def update_memory(self, dH_dt: float, dt: float) -> "MentalState":
        """
        Update memory by integrating entropy change.

        M(t) = integral(dH/dt) dt

        Memory is the accumulated change in the emotional field -
        "how the field got here".

        Args:
            dH_dt: Rate of emotional field change (dH+/dt)
            dt: Time step

        Returns:
            New MentalState with updated memory
        """
        new_M = self.M + dH_dt * dt
        new_trajectory = self.trajectory.copy()
        if self.s_coord:
            new_trajectory.append(self.s_coord)

        return MentalState(
            gamma=self.gamma,
            gamma_f=self.gamma_f,
            M=new_M,
            s_coord=self.s_coord,
            partition=self.partition,
            timestamp=self.timestamp + dt,
            p_decay=self.p_decay,
            t_decay=self.t_decay,
            trajectory=new_trajectory,
        )

    def decay_perception(self, tau_p: float, dt: float) -> "MentalState":
        """
        Apply perception decay.

        P_decay(t+dt) = P_decay(t) * exp(-dt/tau_p)

        Args:
            tau_p: Perception decay time constant
            dt: Time step

        Returns:
            New MentalState with decayed perception
        """
        new_p_decay = self.p_decay * np.exp(-dt / tau_p)

        return MentalState(
            gamma=self.gamma,
            gamma_f=self.gamma_f,
            M=self.M,
            s_coord=self.s_coord,
            partition=self.partition,
            timestamp=self.timestamp + dt,
            p_decay=new_p_decay,
            t_decay=self.t_decay,
            trajectory=self.trajectory,
        )

    def decay_thought(self, tau_t: float, dt: float) -> "MentalState":
        """
        Apply thought decay.

        T_decay(t+dt) = T_decay(t) * exp(-dt/tau_t)

        Args:
            tau_t: Thought decay time constant
            dt: Time step

        Returns:
            New MentalState with decayed thought
        """
        new_t_decay = self.t_decay * np.exp(-dt / tau_t)

        return MentalState(
            gamma=self.gamma,
            gamma_f=self.gamma_f,
            M=self.M,
            s_coord=self.s_coord,
            partition=self.partition,
            timestamp=self.timestamp + dt,
            p_decay=self.p_decay,
            t_decay=new_t_decay,
            trajectory=self.trajectory,
        )

    def transition_to(
        self,
        new_gamma: Optional[float] = None,
        new_gamma_f: Optional[float] = None,
        new_s_coord: Optional[SCoord] = None,
        new_partition: Optional[PartitionCoord] = None,
        new_p_decay: Optional[float] = None,
        new_t_decay: Optional[float] = None,
    ) -> "MentalState":
        """
        Create new state with transitioned parameters.

        Preserves memory and trajectory history.

        Args:
            new_gamma: New phase coherence (or keep current)
            new_gamma_f: New frequency coherence (or keep current)
            new_s_coord: New S-entropy coordinate (or keep current)
            new_partition: New partition coordinate (or keep current)
            new_p_decay: New perception decay (or keep current)
            new_t_decay: New thought decay (or keep current)

        Returns:
            New MentalState with updated parameters
        """
        new_trajectory = self.trajectory.copy()
        if self.s_coord:
            new_trajectory.append(self.s_coord)

        return MentalState(
            gamma=new_gamma if new_gamma is not None else self.gamma,
            gamma_f=new_gamma_f if new_gamma_f is not None else self.gamma_f,
            M=self.M,
            s_coord=new_s_coord if new_s_coord is not None else self.s_coord,
            partition=new_partition if new_partition is not None else self.partition,
            timestamp=self.timestamp,
            p_decay=new_p_decay if new_p_decay is not None else self.p_decay,
            t_decay=new_t_decay if new_t_decay is not None else self.t_decay,
            trajectory=new_trajectory,
        )

    def enter_dream(self) -> "MentalState":
        """
        Transition to dream state.

        Sets P_decay = 0, allowing unbounded thought trajectories.

        Returns:
            New MentalState in dream mode
        """
        return self.transition_to(new_p_decay=0.0)

    def wake(self, perception_level: float = 1.0) -> "MentalState":
        """
        Transition to awake state.

        Restores perception decay to specified level.

        Args:
            perception_level: Initial perception level (default: 1.0)

        Returns:
            New MentalState in awake mode
        """
        return self.transition_to(new_p_decay=perception_level)

    def retrieve_memory(self, t_0: float, H_now: float) -> float:
        """
        Retrieve past emotional state by inverting memory.

        H(t_0) = H_now - (M(now) - M(t_0))

        Args:
            t_0: Time to retrieve
            H_now: Current emotional field value

        Returns:
            Estimated emotional field at t_0
        """
        # Estimate M(t_0) from trajectory length
        # This is a simplified model; full implementation would
        # track M values along trajectory
        trajectory_fraction = t_0 / max(self.timestamp, 1e-10)
        M_t0 = self.M * trajectory_fraction

        return H_now - (self.M - M_t0)

    def predict_emotion(self, delta_t: float, dM_dt: float) -> float:
        """
        Predict future emotional state from memory trajectory.

        H(t + dt) ≈ H(t) + (dM/dt) * dt

        Args:
            delta_t: Time into future
            dM_dt: Current rate of memory change

        Returns:
            Predicted emotional field change
        """
        return dM_dt * delta_t

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize to dictionary.

        Returns:
            Dictionary representation of mental state
        """
        return {
            "gamma": self.gamma,
            "gamma_f": self.gamma_f,
            "M": self.M,
            "consciousness": self.consciousness,
            "is_conscious": self.is_conscious,
            "is_dreaming": self.is_dreaming,
            "is_awake": self.is_awake,
            "timestamp": self.timestamp,
            "p_decay": self.p_decay,
            "t_decay": self.t_decay,
            "s_coord": {
                "sk": self.s_coord.sk,
                "st": self.s_coord.st,
                "se": self.s_coord.se,
            }
            if self.s_coord
            else None,
            "partition": {
                "n": self.partition.n,
                "l": self.partition.l,
                "m": self.partition.m,
                "s": self.partition.s,
            }
            if self.partition
            else None,
            "trajectory_length": len(self.trajectory),
        }

    @classmethod
    def initial(
        cls,
        s_coord: Optional[SCoord] = None,
        partition: Optional[PartitionCoord] = None,
    ) -> "MentalState":
        """
        Create initial mental state (awake, zero memory).

        Args:
            s_coord: Initial S-entropy coordinate
            partition: Initial partition coordinate

        Returns:
            Initial MentalState
        """
        return cls(
            gamma=0.5,
            gamma_f=0.5,
            M=0.0,
            s_coord=s_coord,
            partition=partition,
            timestamp=0.0,
            p_decay=1.0,
            t_decay=1.0,
            trajectory=[],
        )

    def __repr__(self) -> str:
        """String representation."""
        state = "dreaming" if self.is_dreaming else ("awake" if self.is_awake else "transitional")
        return (
            f"MentalState(gamma={self.gamma:.3f}, gamma_f={self.gamma_f:.3f}, "
            f"M={self.M:.3f}, C={self.consciousness:.3f}, state={state})"
        )
