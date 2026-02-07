//! Poincare Computer: Main simulation engine.
//!
//! Implements the Poincare computing paradigm for consciousness simulation.

use serde::{Deserialize, Serialize};
use vb_core::constants::{DEFAULT_COUPLING_STRENGTH, DEFAULT_N_OSCILLATORS};
use vb_core::types::{MentalState, SCoord};
use vb_operators::{
    coherence, kuramoto, kuramoto_with_drug, navigate, KuramotoState,
};

/// Result of a computation.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ComputeResult {
    /// Whether computation succeeded
    pub success: bool,
    /// Final mental state
    pub final_state: MentalState,
    /// Number of iterations
    pub iterations: usize,
    /// Convergence history (consciousness over time)
    pub convergence_history: Vec<f64>,
    /// S-coordinate trajectory
    pub trajectory: Vec<SCoord>,
    /// Additional metadata
    pub metadata: std::collections::HashMap<String, String>,
}

/// Main Poincare computing engine.
#[derive(Debug, Clone)]
pub struct PoincareComputer {
    /// Kuramoto oscillator state
    kuramoto_state: KuramotoState,
    /// History of mental states
    state_history: Vec<MentalState>,
    /// Number of partition levels
    n_partition_levels: i32,
    /// Mean oscillator frequency
    mean_frequency: f64,
    /// Frequency standard deviation
    frequency_std: f64,
}

impl PoincareComputer {
    /// Create new Poincare computer.
    pub fn new(
        n_oscillators: usize,
        coupling_strength: f64,
        n_partition_levels: i32,
    ) -> Self {
        let mean_frequency = 10.0; // Hz
        let frequency_std = 1.0;

        Self {
            kuramoto_state: KuramotoState::random(
                n_oscillators,
                mean_frequency,
                frequency_std,
                coupling_strength,
            ),
            state_history: Vec::new(),
            n_partition_levels,
            mean_frequency,
            frequency_std,
        }
    }

    /// Get current Kuramoto coherence.
    pub fn current_coherence(&self) -> f64 {
        coherence(&self.kuramoto_state.phases)
    }

    /// Compute consciousness to target level.
    pub fn compute_consciousness(
        &mut self,
        initial_state: &MentalState,
        target_consciousness: f64,
        max_iterations: usize,
        dt: f64,
    ) -> ComputeResult {
        let mut state = initial_state.clone();
        let mut trajectory = Vec::new();
        let mut convergence = Vec::new();

        if let Some(s) = state.s_coord {
            trajectory.push(s);
        }

        for iter in 0..max_iterations {
            // Evolve Kuramoto
            self.kuramoto_state = kuramoto(&self.kuramoto_state, dt);
            let r = self.current_coherence();

            // Update mental state
            state = state.with_gamma(r);
            state = state.decay_perception(0.05, dt);
            state = state.decay_thought(0.1, dt);

            let c = state.consciousness();
            convergence.push(c);

            // Check convergence
            if (c - target_consciousness).abs() < 0.01 {
                return ComputeResult {
                    success: true,
                    final_state: state,
                    iterations: iter + 1,
                    convergence_history: convergence,
                    trajectory,
                    metadata: std::collections::HashMap::new(),
                };
            }

            // Adjust coupling to steer toward target
            if c < target_consciousness {
                self.kuramoto_state.coupling_strength *= 1.01;
            } else {
                self.kuramoto_state.coupling_strength *= 0.99;
            }
        }

        ComputeResult {
            success: false,
            final_state: state,
            iterations: max_iterations,
            convergence_history: convergence,
            trajectory,
            metadata: {
                let mut m = std::collections::HashMap::new();
                m.insert("reason".to_string(), "max_iterations".to_string());
                m
            },
        }
    }

    /// Navigate categorical space from start to target.
    pub fn navigate_categorical_space(
        &mut self,
        start: &SCoord,
        target: &SCoord,
        step_size: f64,
        max_steps: usize,
    ) -> Vec<SCoord> {
        navigate(start, target, step_size, max_steps)
    }

    /// Apply drug perturbation to dynamics.
    pub fn apply_drug_perturbation(
        &mut self,
        state: &MentalState,
        concentration: f64,
        k_agg: f64,
        dt: f64,
    ) -> MentalState {
        self.kuramoto_state = kuramoto_with_drug(&self.kuramoto_state, concentration, k_agg, dt);
        let r = self.current_coherence();
        state.with_gamma(r)
    }

    /// Run simulation for given duration.
    pub fn run_simulation(
        &mut self,
        initial_state: &MentalState,
        duration: f64,
        dt: f64,
    ) -> Vec<MentalState> {
        let n_steps = (duration / dt) as usize;
        let mut states = Vec::with_capacity(n_steps);
        let mut state = initial_state.clone();

        for _ in 0..n_steps {
            self.kuramoto_state = kuramoto(&self.kuramoto_state, dt);
            let r = self.current_coherence();

            state = state.with_gamma(r);
            state = state.decay_perception(0.05, dt);
            state = state.decay_thought(0.1, dt);
            state.timestamp += dt;

            states.push(state.clone());
        }

        self.state_history = states.clone();
        states
    }

    /// Find equilibrium state.
    pub fn find_equilibrium(
        &mut self,
        initial_state: &MentalState,
        max_time: f64,
        dt: f64,
        tolerance: f64,
    ) -> (MentalState, bool) {
        let mut state = initial_state.clone();
        let mut time = 0.0;
        let mut prev_c = state.consciousness();

        while time < max_time {
            self.kuramoto_state = kuramoto(&self.kuramoto_state, dt);
            let r = self.current_coherence();

            state = state.with_gamma(r);
            state = state.decay_perception(0.05, dt);
            state = state.decay_thought(0.1, dt);

            let c = state.consciousness();

            if (c - prev_c).abs() < tolerance {
                return (state, true);
            }

            prev_c = c;
            time += dt;
        }

        (state, false)
    }

    /// Simulate dream state.
    pub fn dream_simulation(
        &mut self,
        initial_state: &MentalState,
        duration: f64,
        dt: f64,
    ) -> Vec<MentalState> {
        let dream_state = initial_state.enter_dream();
        self.run_simulation(&dream_state, duration, dt)
    }

    /// Get state history.
    pub fn state_history(&self) -> &[MentalState] {
        &self.state_history
    }

    /// Reset Kuramoto state.
    pub fn reset_kuramoto(&mut self) {
        self.kuramoto_state = KuramotoState::random(
            self.kuramoto_state.n_oscillators(),
            self.mean_frequency,
            self.frequency_std,
            self.kuramoto_state.coupling_strength,
        );
    }
}

impl Default for PoincareComputer {
    fn default() -> Self {
        Self::new(DEFAULT_N_OSCILLATORS, DEFAULT_COUPLING_STRENGTH, 5)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_new() {
        let computer = PoincareComputer::new(50, 0.5, 5);
        assert!(computer.current_coherence() >= 0.0);
        assert!(computer.current_coherence() <= 1.0);
    }

    #[test]
    fn test_run_simulation() {
        let mut computer = PoincareComputer::new(50, 2.0, 5);
        let initial = MentalState::default();

        let states = computer.run_simulation(&initial, 1.0, 0.01);
        assert_eq!(states.len(), 100);
    }

    #[test]
    fn test_navigate() {
        let mut computer = PoincareComputer::default();
        let start = SCoord::origin();
        let target = SCoord::new(0.8, 0.8, 0.8).unwrap();

        let path = computer.navigate_categorical_space(&start, &target, 0.1, 100);
        assert!(path.len() > 1);
    }

    #[test]
    fn test_dream_simulation() {
        let mut computer = PoincareComputer::default();
        let initial = MentalState::default();

        let states = computer.dream_simulation(&initial, 0.5, 0.01);
        assert!(!states.is_empty());

        // In dream state, p_decay should be 0
        for state in &states {
            assert!(state.p_decay < 0.01);
        }
    }
}
