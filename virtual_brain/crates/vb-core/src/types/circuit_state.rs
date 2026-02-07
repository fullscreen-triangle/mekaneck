//! CircuitState: Circuit regime detection and state management.
//!
//! Models hybrid microfluidic-electronic circuit states with
//! automatic regime detection based on Reynolds number and coherence.

use crate::constants::{RE_LAMINAR_MAX, RE_TURBULENT_MIN};
use num_complex::Complex64;
use serde::{Deserialize, Serialize};
use std::f64::consts::PI;

/// Circuit operating regimes.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum CircuitRegime {
    /// Laminar flow (Re < 2300)
    Laminar,
    /// Transitional flow (2300 <= Re < 4000)
    Transitional,
    /// Turbulent flow (Re >= 4000)
    Turbulent,
    /// Oscillatory behavior with coherence
    Oscillatory,
    /// Bistable regime near transition
    Bistable,
    /// Chaotic regime with high variance
    Chaotic,
    /// Phase-locked oscillations
    PhaseLocked,
    /// Hierarchical multi-scale dynamics
    Hierarchical,
}

/// Circuit state with regime detection.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CircuitState {
    /// Voltage (V)
    pub voltage: f64,
    /// Current (A)
    pub current: f64,
    /// Reynolds number (dimensionless)
    pub reynolds_number: f64,
    /// Phase angle (rad)
    pub phase: f64,
    /// Oscillation frequency (Hz)
    pub frequency: f64,
    /// Phase coherence [0, 1]
    pub coherence: f64,
    /// Hierarchical depth [0, 1]
    pub depth: f64,
    /// State variance
    pub variance: f64,
    /// Manual regime override
    regime_override: Option<CircuitRegime>,
}

impl CircuitState {
    /// Create new circuit state.
    pub fn new(voltage: f64, current: f64, reynolds_number: f64) -> Self {
        Self {
            voltage,
            current,
            reynolds_number,
            phase: 0.0,
            frequency: 0.0,
            coherence: 0.0,
            depth: 0.0,
            variance: 0.0,
            regime_override: None,
        }
    }

    /// Detect current operating regime.
    pub fn regime(&self) -> CircuitRegime {
        if let Some(r) = self.regime_override {
            return r;
        }

        if self.depth >= 0.6 {
            return CircuitRegime::Hierarchical;
        }

        if self.coherence > 0.8 {
            return CircuitRegime::PhaseLocked;
        }

        let re = self.reynolds_number;

        if re < RE_LAMINAR_MAX {
            if self.coherence > 0.5 {
                CircuitRegime::Oscillatory
            } else {
                CircuitRegime::Laminar
            }
        } else if re > RE_TURBULENT_MIN {
            if self.variance > 1.0 {
                CircuitRegime::Chaotic
            } else {
                CircuitRegime::Turbulent
            }
        } else {
            // Transitional region
            if (self.coherence - 0.5).abs() < 0.1 {
                CircuitRegime::Bistable
            } else {
                CircuitRegime::Transitional
            }
        }
    }

    /// Set regime override.
    pub fn set_regime_override(&mut self, regime: Option<CircuitRegime>) {
        self.regime_override = regime;
    }

    /// Power dissipation P = V * I.
    pub fn power(&self) -> f64 {
        self.voltage * self.current
    }

    /// Resistance R = V / I.
    pub fn resistance(&self) -> f64 {
        if self.current.abs() < 1e-12 {
            f64::INFINITY
        } else {
            self.voltage / self.current
        }
    }

    /// Complex impedance Z = |V/I| * exp(i*phase).
    pub fn impedance(&self) -> Complex64 {
        if self.current.abs() < 1e-12 {
            return Complex64::new(f64::INFINITY, 0.0);
        }
        let magnitude = self.voltage / self.current;
        magnitude * Complex64::from_polar(1.0, self.phase)
    }

    /// Reactance (imaginary part of impedance).
    pub fn reactance(&self) -> f64 {
        self.impedance().im
    }

    /// Check if state is stable.
    pub fn is_stable(&self) -> bool {
        matches!(
            self.regime(),
            CircuitRegime::Laminar | CircuitRegime::Bistable | CircuitRegime::PhaseLocked
        ) && self.variance < 0.1
    }

    /// Check if oscillating.
    pub fn is_oscillating(&self) -> bool {
        self.coherence > 0.3 && self.frequency > 0.0
    }

    /// Evolve by one time step using Euler integration.
    pub fn step(&self, dv_dt: f64, di_dt: f64, dt: f64, dr_dt: f64) -> Self {
        Self {
            voltage: self.voltage + dv_dt * dt,
            current: self.current + di_dt * dt,
            reynolds_number: self.reynolds_number,
            phase: (self.phase + 2.0 * PI * self.frequency * dt) % (2.0 * PI),
            frequency: self.frequency,
            coherence: (self.coherence + dr_dt * dt).clamp(0.0, 1.0),
            depth: self.depth,
            variance: self.variance,
            regime_override: None,
        }
    }

    /// Update Reynolds number based on flow parameters.
    pub fn update_reynolds(&self, velocity: f64, length: f64, viscosity: f64) -> Self {
        let mut new_state = self.clone();
        new_state.reynolds_number = velocity * length / viscosity;
        new_state
    }

    /// Update variance from a set of measurements.
    pub fn with_variance(&self, variance: f64) -> Self {
        let mut new_state = self.clone();
        new_state.variance = variance;
        new_state
    }

    /// Update coherence.
    pub fn with_coherence(&self, coherence: f64) -> Self {
        let mut new_state = self.clone();
        new_state.coherence = coherence.clamp(0.0, 1.0);
        new_state
    }

    /// Update frequency.
    pub fn with_frequency(&self, frequency: f64) -> Self {
        let mut new_state = self.clone();
        new_state.frequency = frequency;
        new_state
    }

    /// Initial circuit state.
    pub fn initial(voltage: f64, current: f64, reynolds: f64) -> Self {
        Self::new(voltage, current, reynolds)
    }
}

impl Default for CircuitState {
    fn default() -> Self {
        Self::initial(0.0, 0.0, 1000.0)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_regime_detection() {
        let laminar = CircuitState::new(1.0, 1.0, 1000.0);
        assert_eq!(laminar.regime(), CircuitRegime::Laminar);

        let turbulent = CircuitState::new(1.0, 1.0, 5000.0);
        assert_eq!(turbulent.regime(), CircuitRegime::Turbulent);

        let transitional = CircuitState::new(1.0, 1.0, 3000.0);
        assert_eq!(transitional.regime(), CircuitRegime::Transitional);
    }

    #[test]
    fn test_power() {
        let state = CircuitState::new(10.0, 2.0, 1000.0);
        assert!((state.power() - 20.0).abs() < 1e-10);
    }

    #[test]
    fn test_phase_locked_regime() {
        let mut state = CircuitState::new(1.0, 1.0, 1000.0);
        state.coherence = 0.9;
        assert_eq!(state.regime(), CircuitRegime::PhaseLocked);
    }

    #[test]
    fn test_step() {
        let state = CircuitState::new(1.0, 0.5, 1000.0);
        let stepped = state.step(0.1, 0.05, 0.01, 0.0);
        assert!((stepped.voltage - 1.001).abs() < 1e-10);
        assert!((stepped.current - 0.5005).abs() < 1e-10);
    }
}
