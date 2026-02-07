//! MentalState: Complete mental state representation (gamma, Gamma_f, M).
//!
//! A mental state is a trajectory-terminus-memory triple that captures
//! the complete state of consciousness.

use crate::error::MentalStateError;
use crate::types::{PartitionCoord, SCoord};
use serde::{Deserialize, Serialize};

/// Complete mental state representation.
///
/// A mental state M = (gamma, Gamma_f, M) captures:
/// - gamma: Phase coherence (Kuramoto order parameter R)
/// - gamma_f: Frequency coherence (global frequency locking)
/// - m: Memory integral (accumulated entropy changes)
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MentalState {
    /// Phase coherence (Kuramoto order parameter R) in [0, 1]
    pub gamma: f64,
    /// Frequency coherence (global frequency locking) in [0, 1]
    pub gamma_f: f64,
    /// Memory integral (accumulated entropy changes)
    pub m: f64,

    /// Current S-entropy coordinate
    pub s_coord: Option<SCoord>,
    /// Current partition coordinate
    pub partition: Option<PartitionCoord>,
    /// Time of this state
    pub timestamp: f64,

    /// Perception decay level in [0, 1]
    pub p_decay: f64,
    /// Thought decay level in [0, 1]
    pub t_decay: f64,

    /// Trajectory history
    pub trajectory: Vec<SCoord>,
}

impl MentalState {
    /// Create new MentalState with validation.
    pub fn new(gamma: f64, gamma_f: f64, m: f64) -> Result<Self, MentalStateError> {
        Self::validate_range("gamma", gamma)?;
        Self::validate_range("gamma_f", gamma_f)?;

        Ok(Self {
            gamma,
            gamma_f,
            m,
            s_coord: None,
            partition: None,
            timestamp: 0.0,
            p_decay: 1.0,
            t_decay: 1.0,
            trajectory: Vec::new(),
        })
    }

    fn validate_range(name: &str, val: f64) -> Result<(), MentalStateError> {
        if !(0.0..=1.0).contains(&val) {
            return Err(MentalStateError::OutOfBounds(name.to_string(), val));
        }
        Ok(())
    }

    /// Consciousness level: C = P_decay * T_decay * gamma * gamma_f
    pub fn consciousness(&self) -> f64 {
        self.p_decay * self.t_decay * self.gamma * self.gamma_f
    }

    /// Check if consciousness threshold is met.
    pub fn is_conscious(&self) -> bool {
        self.consciousness() > 0.5
    }

    /// Check if in dream state.
    pub fn is_dreaming(&self) -> bool {
        self.p_decay < 0.1 && self.t_decay > 0.5 && self.gamma_f > 0.5
    }

    /// Check if in awake state.
    pub fn is_awake(&self) -> bool {
        self.p_decay > 0.7 && self.gamma > 0.5
    }

    /// Enter dream state (P_decay = 0).
    pub fn enter_dream(&self) -> Self {
        let mut new_state = self.clone();
        new_state.p_decay = 0.0;
        new_state
    }

    /// Wake from dream state.
    pub fn wake(&self, perception_level: f64) -> Self {
        let mut new_state = self.clone();
        new_state.p_decay = perception_level.clamp(0.0, 1.0);
        new_state
    }

    /// Create initial mental state.
    pub fn initial(s_coord: Option<SCoord>, partition: Option<PartitionCoord>) -> Self {
        Self {
            gamma: 0.5,
            gamma_f: 0.5,
            m: 0.0,
            s_coord,
            partition,
            timestamp: 0.0,
            p_decay: 1.0,
            t_decay: 1.0,
            trajectory: Vec::new(),
        }
    }

    /// Update with new gamma value.
    pub fn with_gamma(&self, gamma: f64) -> Self {
        let mut new_state = self.clone();
        new_state.gamma = gamma.clamp(0.0, 1.0);
        new_state
    }

    /// Update with new gamma_f value.
    pub fn with_gamma_f(&self, gamma_f: f64) -> Self {
        let mut new_state = self.clone();
        new_state.gamma_f = gamma_f.clamp(0.0, 1.0);
        new_state
    }

    /// Update memory.
    pub fn with_memory(&self, m: f64) -> Self {
        let mut new_state = self.clone();
        new_state.m = m;
        new_state
    }

    /// Apply perception decay.
    pub fn decay_perception(&self, tau_p: f64, dt: f64) -> Self {
        let mut new_state = self.clone();
        new_state.p_decay *= (-dt / tau_p).exp();
        new_state.timestamp += dt;
        new_state
    }

    /// Apply thought decay.
    pub fn decay_thought(&self, tau_t: f64, dt: f64) -> Self {
        let mut new_state = self.clone();
        new_state.t_decay *= (-dt / tau_t).exp();
        new_state.timestamp += dt;
        new_state
    }

    /// Update memory integral: M += (dH/dt) * dt
    pub fn update_memory(&self, dh_dt: f64, dt: f64) -> Self {
        let mut new_state = self.clone();
        new_state.m += dh_dt.abs() * dt;
        new_state
    }

    /// Add position to trajectory.
    pub fn add_to_trajectory(&mut self, s: SCoord) {
        self.trajectory.push(s);
    }

    /// Set s_coord and add to trajectory.
    pub fn transition_to(&self, s: SCoord) -> Self {
        let mut new_state = self.clone();
        if let Some(current) = &new_state.s_coord {
            new_state.trajectory.push(*current);
        }
        new_state.s_coord = Some(s);
        new_state
    }
}

impl Default for MentalState {
    fn default() -> Self {
        Self::initial(None, None)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_consciousness_formula() {
        let state = MentalState {
            gamma: 0.8,
            gamma_f: 0.9,
            p_decay: 1.0,
            t_decay: 1.0,
            ..Default::default()
        };
        let c = state.consciousness();
        assert!((c - 0.72).abs() < 1e-10); // 0.8 * 0.9 * 1.0 * 1.0
    }

    #[test]
    fn test_dream_state() {
        let state = MentalState::default();
        let dreaming = state.enter_dream();
        assert_eq!(dreaming.p_decay, 0.0);
        assert!(dreaming.consciousness() < 0.01);
    }

    #[test]
    fn test_decay() {
        let state = MentalState::default();
        let decayed = state.decay_perception(0.05, 0.01);
        assert!(decayed.p_decay < 1.0);
        assert!(decayed.timestamp > 0.0);
    }

    #[test]
    fn test_validation() {
        assert!(MentalState::new(1.5, 0.5, 0.0).is_err());
        assert!(MentalState::new(0.5, -0.1, 0.0).is_err());
        assert!(MentalState::new(0.5, 0.5, 0.0).is_ok());
    }
}
