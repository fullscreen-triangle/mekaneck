//! State Manager: Tracks state transitions and history.

use serde::{Deserialize, Serialize};
use vb_core::types::{MentalState, PartitionCoord, SCoord};

/// Result of a state transition.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TransitionResult {
    /// Whether transition succeeded
    pub success: bool,
    /// State before transition
    pub from_state: Option<SCoord>,
    /// State after transition
    pub to_state: SCoord,
    /// Distance traveled
    pub distance: f64,
    /// Additional metadata
    pub metadata: std::collections::HashMap<String, String>,
}

/// Manages state transitions and history.
#[derive(Debug, Clone)]
pub struct StateManager {
    /// Current mental state
    current_state: MentalState,
    /// History of states
    history: Vec<MentalState>,
    /// Maximum history size
    max_history: usize,
}

impl StateManager {
    /// Create new state manager.
    pub fn new(max_history: usize) -> Self {
        Self {
            current_state: MentalState::default(),
            history: Vec::new(),
            max_history,
        }
    }

    /// Initialize with a specific state.
    pub fn initialize(&mut self, s_coord: Option<SCoord>, partition: Option<PartitionCoord>) {
        self.current_state = MentalState::initial(s_coord, partition);
        self.history.clear();
        self.history.push(self.current_state.clone());
    }

    /// Get current state.
    pub fn current(&self) -> &MentalState {
        &self.current_state
    }

    /// Get state history.
    pub fn history(&self) -> &[MentalState] {
        &self.history
    }

    /// Transition to new S-coordinate.
    pub fn transition(
        &mut self,
        target_s_coord: SCoord,
        new_gamma: Option<f64>,
        new_gamma_f: Option<f64>,
    ) -> TransitionResult {
        let from_state = self.current_state.s_coord;
        let distance = from_state
            .map(|s| s.distance(&target_s_coord))
            .unwrap_or(0.0);

        // Create new state
        let mut new_state = self.current_state.transition_to(target_s_coord);

        if let Some(g) = new_gamma {
            new_state = new_state.with_gamma(g);
        }
        if let Some(gf) = new_gamma_f {
            new_state = new_state.with_gamma_f(gf);
        }

        // Update history
        self.history.push(new_state.clone());
        if self.history.len() > self.max_history {
            self.history.remove(0);
        }

        self.current_state = new_state;

        TransitionResult {
            success: true,
            from_state,
            to_state: target_s_coord,
            distance,
            metadata: std::collections::HashMap::new(),
        }
    }

    /// Validate current state.
    pub fn validate_state(&self) -> bool {
        let state = &self.current_state;

        // Check bounds
        if state.gamma < 0.0 || state.gamma > 1.0 {
            return false;
        }
        if state.gamma_f < 0.0 || state.gamma_f > 1.0 {
            return false;
        }
        if state.p_decay < 0.0 || state.p_decay > 1.0 {
            return false;
        }
        if state.t_decay < 0.0 || state.t_decay > 1.0 {
            return false;
        }

        // Check S-coordinate bounds if present
        if let Some(s) = &state.s_coord {
            if s.sk < 0.0 || s.sk > 1.0 {
                return false;
            }
            if s.st < 0.0 || s.st > 1.0 {
                return false;
            }
            if s.se < 0.0 || s.se > 1.0 {
                return false;
            }
        }

        true
    }

    /// Extract S-coordinate trajectory.
    pub fn get_trajectory(&self) -> Vec<SCoord> {
        self.history
            .iter()
            .filter_map(|s| s.s_coord)
            .collect()
    }

    /// Extract consciousness time series.
    pub fn get_consciousness_history(&self) -> Vec<f64> {
        self.history.iter().map(|s| s.consciousness()).collect()
    }

    /// Extract memory time series.
    pub fn get_memory_history(&self) -> Vec<f64> {
        self.history.iter().map(|s| s.m).collect()
    }

    /// Find state at specific time.
    pub fn find_state_at_time(&self, t: f64) -> Option<&MentalState> {
        self.history.iter().find(|s| (s.timestamp - t).abs() < 1e-6)
    }

    /// Compute memory differential from history.
    pub fn compute_memory_differential(&self) -> f64 {
        if self.history.len() < 2 {
            return 0.0;
        }

        let n = self.history.len();
        let dt = self.history[n - 1].timestamp - self.history[n - 2].timestamp;
        if dt.abs() < 1e-12 {
            return 0.0;
        }

        (self.history[n - 1].m - self.history[n - 2].m) / dt
    }

    /// Enter dream mode.
    pub fn enter_dream_mode(&mut self) -> TransitionResult {
        let from_state = self.current_state.s_coord;
        self.current_state = self.current_state.enter_dream();

        self.history.push(self.current_state.clone());
        if self.history.len() > self.max_history {
            self.history.remove(0);
        }

        TransitionResult {
            success: true,
            from_state,
            to_state: self.current_state.s_coord.unwrap_or(SCoord::origin()),
            distance: 0.0,
            metadata: {
                let mut m = std::collections::HashMap::new();
                m.insert("mode".to_string(), "dream".to_string());
                m
            },
        }
    }

    /// Wake up from dream.
    pub fn wake_up(&mut self, perception_level: f64) -> TransitionResult {
        let from_state = self.current_state.s_coord;
        self.current_state = self.current_state.wake(perception_level);

        self.history.push(self.current_state.clone());
        if self.history.len() > self.max_history {
            self.history.remove(0);
        }

        TransitionResult {
            success: true,
            from_state,
            to_state: self.current_state.s_coord.unwrap_or(SCoord::origin()),
            distance: 0.0,
            metadata: {
                let mut m = std::collections::HashMap::new();
                m.insert("mode".to_string(), "awake".to_string());
                m
            },
        }
    }

    /// Clear history.
    pub fn clear_history(&mut self) {
        self.history.clear();
        self.history.push(self.current_state.clone());
    }

    /// Get summary statistics.
    pub fn summary(&self) -> std::collections::HashMap<String, f64> {
        let mut summary = std::collections::HashMap::new();

        summary.insert("current_consciousness".to_string(), self.current_state.consciousness());
        summary.insert("current_gamma".to_string(), self.current_state.gamma);
        summary.insert("current_gamma_f".to_string(), self.current_state.gamma_f);
        summary.insert("current_memory".to_string(), self.current_state.m);
        summary.insert("history_length".to_string(), self.history.len() as f64);

        if !self.history.is_empty() {
            let c_history = self.get_consciousness_history();
            let mean_c: f64 = c_history.iter().sum::<f64>() / c_history.len() as f64;
            summary.insert("mean_consciousness".to_string(), mean_c);
        }

        summary
    }
}

impl Default for StateManager {
    fn default() -> Self {
        Self::new(1000)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_initialize() {
        let mut manager = StateManager::new(100);
        let s = SCoord::new(0.5, 0.5, 0.5).unwrap();
        manager.initialize(Some(s), None);

        assert!(manager.current().s_coord.is_some());
        assert_eq!(manager.history().len(), 1);
    }

    #[test]
    fn test_transition() {
        let mut manager = StateManager::new(100);
        manager.initialize(Some(SCoord::origin()), None);

        let target = SCoord::new(0.8, 0.8, 0.8).unwrap();
        let result = manager.transition(target, Some(0.9), None);

        assert!(result.success);
        assert!(result.distance > 0.0);
        assert_eq!(manager.current().gamma, 0.9);
    }

    #[test]
    fn test_dream_wake() {
        let mut manager = StateManager::new(100);
        manager.initialize(Some(SCoord::origin()), None);

        manager.enter_dream_mode();
        assert!(manager.current().is_dreaming() || manager.current().p_decay < 0.1);

        manager.wake_up(0.9);
        assert!(manager.current().p_decay > 0.5);
    }

    #[test]
    fn test_history_limit() {
        let mut manager = StateManager::new(5);
        manager.initialize(Some(SCoord::origin()), None);

        for i in 0..10 {
            let s = SCoord::new(i as f64 / 10.0, 0.5, 0.5).unwrap();
            manager.transition(s, None, None);
        }

        assert!(manager.history().len() <= 6); // 5 + initial
    }
}
