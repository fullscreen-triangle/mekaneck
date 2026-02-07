//! Dynamics Operators: KURAMOTO, PHASE_LOCK, CASCADE, VARIANCE.
//!
//! Implements Kuramoto model for oscillator synchronization:
//! dφᵢ/dt = ωᵢ + (K/N) Σⱼ sin(φⱼ - φᵢ)

use ndarray::Array1;
use num_complex::Complex64;
use rand::Rng;
use rand_distr::{Distribution, Normal};
use serde::{Deserialize, Serialize};
use std::f64::consts::PI;
use vb_core::constants::BIOLOGICAL_GEAR_RATIOS;

/// State of Kuramoto oscillator network.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct KuramotoState {
    /// Oscillator phases in [0, 2*pi)
    pub phases: Array1<f64>,
    /// Natural frequencies (rad/s)
    pub natural_frequencies: Array1<f64>,
    /// Global coupling strength K
    pub coupling_strength: f64,
}

impl KuramotoState {
    /// Create new Kuramoto state.
    pub fn new(phases: Array1<f64>, natural_frequencies: Array1<f64>, coupling_strength: f64) -> Self {
        Self {
            phases,
            natural_frequencies,
            coupling_strength,
        }
    }

    /// Create random Kuramoto state.
    pub fn random(
        n_oscillators: usize,
        mean_frequency: f64,
        frequency_std: f64,
        coupling: f64,
    ) -> Self {
        let mut rng = rand::thread_rng();

        let phases =
            Array1::from_iter((0..n_oscillators).map(|_| rng.gen::<f64>() * 2.0 * PI));

        let normal = Normal::new(mean_frequency * 2.0 * PI, frequency_std * 2.0 * PI)
            .unwrap_or_else(|_| Normal::new(mean_frequency * 2.0 * PI, 1.0).unwrap());
        let frequencies =
            Array1::from_iter((0..n_oscillators).map(|_| normal.sample(&mut rng)));

        Self {
            phases,
            natural_frequencies: frequencies,
            coupling_strength: coupling,
        }
    }

    /// Number of oscillators.
    pub fn n_oscillators(&self) -> usize {
        self.phases.len()
    }
}

/// KURAMOTO operator: Evolve Kuramoto oscillator network.
///
/// Implements: dφᵢ/dt = ωᵢ + (K/N) Σⱼ sin(φⱼ - φᵢ)
pub fn kuramoto(state: &KuramotoState, dt: f64) -> KuramotoState {
    let n = state.n_oscillators();
    let k = state.coupling_strength;

    // Compute coupling term (vectorized)
    let mut d_phases = state.natural_frequencies.clone();

    for i in 0..n {
        let mut coupling_sum = 0.0;
        for j in 0..n {
            coupling_sum += (state.phases[j] - state.phases[i]).sin();
        }
        d_phases[i] += (k / n as f64) * coupling_sum;
    }

    // Update phases
    let new_phases = (&state.phases + &(&d_phases * dt)).mapv(|x| x.rem_euclid(2.0 * PI));

    KuramotoState {
        phases: new_phases,
        natural_frequencies: state.natural_frequencies.clone(),
        coupling_strength: k,
    }
}

/// KURAMOTO with drug perturbation.
pub fn kuramoto_with_drug(
    state: &KuramotoState,
    drug_concentration: f64,
    k_agg: f64,
    dt: f64,
) -> KuramotoState {
    // Drug modifies coupling strength
    let effective_k = state.coupling_strength * (1.0 - k_agg * drug_concentration);
    let modified_state = KuramotoState {
        phases: state.phases.clone(),
        natural_frequencies: state.natural_frequencies.clone(),
        coupling_strength: effective_k.max(0.0),
    };
    kuramoto(&modified_state, dt)
}

/// PHASE_LOCK operator: Compute Kuramoto order parameter.
///
/// Returns (R, Psi) - magnitude and mean phase.
/// R = (1/N) |Σⱼ exp(iφⱼ)|
pub fn phase_lock(phases: &Array1<f64>) -> (f64, f64) {
    let n = phases.len() as f64;
    let z: Complex64 = phases
        .iter()
        .map(|&phi| Complex64::from_polar(1.0, phi))
        .sum::<Complex64>()
        / n;

    (z.norm(), z.arg())
}

/// COHERENCE operator (alias for R from PHASE_LOCK).
pub fn coherence(phases: &Array1<f64>) -> f64 {
    phase_lock(phases).0
}

/// CASCADE operator: Multi-scale frequency cascade.
pub fn cascade(input_frequency: f64, gear_ratios: Option<&[f64]>) -> Vec<f64> {
    let ratios = gear_ratios.unwrap_or(&BIOLOGICAL_GEAR_RATIOS);

    let mut frequencies = vec![input_frequency];
    for &g in ratios {
        frequencies.push(frequencies.last().unwrap() * g);
    }
    frequencies
}

/// VARIANCE operator.
pub fn variance(values: &Array1<f64>) -> f64 {
    let mean = values.mean().unwrap_or(0.0);
    values.mapv(|x| (x - mean).powi(2)).mean().unwrap_or(0.0)
}

/// Simulate Kuramoto dynamics over time.
pub fn simulate_kuramoto(
    initial_state: &KuramotoState,
    duration: f64,
    dt: f64,
) -> (Array1<f64>, Array1<f64>, Array1<f64>) {
    let n_steps = (duration / dt) as usize;
    let mut times = Array1::zeros(n_steps);
    let mut order_params = Array1::zeros(n_steps);
    let mut mean_phases = Array1::zeros(n_steps);

    let mut state = initial_state.clone();

    for i in 0..n_steps {
        times[i] = i as f64 * dt;
        let (r, psi) = phase_lock(&state.phases);
        order_params[i] = r;
        mean_phases[i] = psi;
        state = kuramoto(&state, dt);
    }

    (times, order_params, mean_phases)
}

/// Critical coupling for synchronization onset.
/// K_c ≈ 2σ/π for Lorentzian frequency distribution
pub fn critical_coupling(frequency_std: f64, _n_oscillators: usize) -> f64 {
    2.0 * frequency_std / PI
}

/// Phase velocity for traveling waves.
pub fn phase_velocity(coupling_strength: f64, diffusion_coeff: f64) -> f64 {
    (coupling_strength * diffusion_coeff).sqrt()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_phase_lock_bounds() {
        let state = KuramotoState::random(100, 10.0, 1.0, 0.5);
        let (r, _) = phase_lock(&state.phases);
        assert!(r >= 0.0 && r <= 1.0);
    }

    #[test]
    fn test_synchronized_phases() {
        // All phases equal should give R = 1
        let phases = Array1::from_elem(100, 0.5);
        let (r, _) = phase_lock(&phases);
        assert!((r - 1.0).abs() < 1e-10);
    }

    #[test]
    fn test_uniform_phases() {
        // Uniformly distributed phases should give R ≈ 0
        let n = 1000;
        let phases = Array1::from_iter((0..n).map(|i| 2.0 * PI * i as f64 / n as f64));
        let (r, _) = phase_lock(&phases);
        assert!(r < 0.1);
    }

    #[test]
    fn test_cascade() {
        let freqs = cascade(1e12, None);
        assert_eq!(freqs.len(), 9); // input + 8 gear ratios
        assert!((freqs[0] - 1e12).abs() < 1e-10);
    }

    #[test]
    fn test_variance() {
        let values = Array1::from_vec(vec![1.0, 2.0, 3.0, 4.0, 5.0]);
        let v = variance(&values);
        assert!((v - 2.0).abs() < 1e-10); // Variance of [1,2,3,4,5] is 2.0
    }

    #[test]
    fn test_kuramoto_evolution() {
        let state = KuramotoState::random(10, 1.0, 0.1, 2.0);
        let evolved = kuramoto(&state, 0.01);
        assert_eq!(evolved.n_oscillators(), state.n_oscillators());
    }
}
