//! Neural Operators: CONSCIOUSNESS, MEMORY, DREAM, WAKE.
//!
//! Implements neural-level operations for consciousness computation.

use ndarray::Array1;
use vb_core::constants::{TAU_PERCEPTION, TAU_THOUGHT};
use vb_core::types::MentalState;

/// CONSCIOUSNESS operator: Compute consciousness level.
///
/// C = P_decay * T_decay * gamma * gamma_f
pub fn consciousness(p_decay: f64, t_decay: f64, gamma: f64, gamma_f: f64) -> f64 {
    p_decay * t_decay * gamma * gamma_f
}

/// Consciousness frequency from component frequencies.
/// f_c = f_thought * f_perception / (f_thought + f_perception)
pub fn consciousness_frequency(omega_thought: f64, omega_perception: f64) -> f64 {
    if omega_thought + omega_perception < 1e-12 {
        return 0.0;
    }
    omega_thought * omega_perception / (omega_thought + omega_perception)
}

/// MEMORY operator: Accumulated emotional change.
///
/// M = ∫|dH/dt| dt
pub fn memory(h_field: &Array1<f64>, dt: f64) -> f64 {
    if h_field.len() < 2 {
        return 0.0;
    }

    let mut m = 0.0;
    for i in 1..h_field.len() {
        let dh_dt = (h_field[i] - h_field[i - 1]) / dt;
        m += dh_dt.abs() * dt;
    }
    m
}

/// Memory differential dM/dt.
pub fn memory_differential(h_current: f64, h_previous: f64, dt: f64) -> f64 {
    ((h_current - h_previous) / dt).abs()
}

/// DREAM operator: Enter dream state.
///
/// Sets P_decay = 0 (no perception input)
pub fn dream(state: &MentalState) -> MentalState {
    state.enter_dream()
}

/// WAKE operator: Wake from dream state.
///
/// Restores perception to specified level.
pub fn wake(state: &MentalState, perception_level: f64) -> MentalState {
    state.wake(perception_level)
}

/// Decay evolution: d(curve)/dt = -curve/tau + input_rate
pub fn decay_evolve(curve: f64, tau: f64, dt: f64, input_rate: f64) -> f64 {
    curve * (-dt / tau).exp() + input_rate * dt
}

/// Retrieve past emotional state from memory.
/// H(t_0) ≈ H(now) - (M(now) - M(t_0))
pub fn retrieve_memory(m_now: f64, m_t0: f64, h_now: f64) -> f64 {
    h_now - (m_now - m_t0)
}

/// Predict future emotional state.
/// H(t + Δt) ≈ H(t) + dM/dt * Δt
pub fn predict_emotion(h_now: f64, dm_dt: f64, delta_t: f64) -> f64 {
    h_now + dm_dt * delta_t
}

/// Evolve mental state by one time step.
pub fn evolve_mental_state(
    state: &MentalState,
    dt: f64,
    perception_input: f64,
    thought_input: f64,
    dh_dt: f64,
) -> MentalState {
    // Apply decays with input
    let new_p_decay = decay_evolve(state.p_decay, TAU_PERCEPTION, dt, perception_input);
    let new_t_decay = decay_evolve(state.t_decay, TAU_THOUGHT, dt, thought_input);

    // Update memory
    let new_m = state.m + dh_dt.abs() * dt;

    MentalState {
        gamma: state.gamma,
        gamma_f: state.gamma_f,
        m: new_m,
        s_coord: state.s_coord,
        partition: state.partition,
        timestamp: state.timestamp + dt,
        p_decay: new_p_decay.clamp(0.0, 1.0),
        t_decay: new_t_decay.clamp(0.0, 1.0),
        trajectory: state.trajectory.clone(),
    }
}

/// Generate consciousness time series.
pub fn consciousness_time_series(
    initial_state: &MentalState,
    duration: f64,
    dt: f64,
    perception_profile: &dyn Fn(f64) -> f64,
) -> (Array1<f64>, Array1<f64>) {
    let n_steps = (duration / dt) as usize;
    let mut times = Array1::zeros(n_steps);
    let mut consciousness_values = Array1::zeros(n_steps);

    let mut state = initial_state.clone();

    for i in 0..n_steps {
        let t = i as f64 * dt;
        times[i] = t;
        consciousness_values[i] = state.consciousness();

        let perception = perception_profile(t);
        state = evolve_mental_state(&state, dt, perception, 0.5, 0.0);
    }

    (times, consciousness_values)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_consciousness_formula() {
        let c = consciousness(1.0, 1.0, 0.8, 0.9);
        assert!((c - 0.72).abs() < 1e-10);
    }

    #[test]
    fn test_consciousness_bounds() {
        let c = consciousness(1.0, 1.0, 1.0, 1.0);
        assert!(c <= 1.0);
        let c = consciousness(0.0, 0.0, 0.0, 0.0);
        assert!(c >= 0.0);
    }

    #[test]
    fn test_memory() {
        let h_field = Array1::from_vec(vec![0.0, 1.0, 2.0, 3.0, 4.0]);
        let m = memory(&h_field, 1.0);
        assert!((m - 4.0).abs() < 1e-10); // |1| + |1| + |1| + |1| = 4
    }

    #[test]
    fn test_dream_wake() {
        let state = MentalState::default();
        let dreaming = dream(&state);
        assert_eq!(dreaming.p_decay, 0.0);

        let awake = wake(&dreaming, 0.8);
        assert!((awake.p_decay - 0.8).abs() < 1e-10);
    }

    #[test]
    fn test_decay_evolve() {
        let new_val = decay_evolve(1.0, 0.1, 0.01, 0.0);
        assert!(new_val < 1.0); // Should decay
    }
}
