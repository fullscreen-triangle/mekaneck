//! SCoord: S-Entropy coordinate system (Sk, St, Se) in [0,1]^3.
//!
//! The triple equivalence holds: S_osc = S_cat = S_part = k_B * M * ln(n)

use crate::constants::{BOLTZMANN_CONSTANT, HBAR, KT_ROOM_TEMP, SE_REFERENCE, T_0_REFERENCE};
use crate::error::SCoordError;
use ndarray::Array1;
use serde::{Deserialize, Serialize};
use std::f64::consts::PI;

const EPSILON: f64 = 1e-10;

/// S-Entropy coordinate in normalized [0,1]^3 space.
#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct SCoord {
    /// Knowledge entropy (information deficit) in [0, 1]
    pub sk: f64,
    /// Temporal entropy (temporal distance) in [0, 1]
    pub st: f64,
    /// Evolution entropy (trajectory uncertainty) in [0, 1]
    pub se: f64,
}

impl SCoord {
    /// Create new SCoord with validation.
    pub fn new(sk: f64, st: f64, se: f64) -> Result<Self, SCoordError> {
        Self::validate_range("sk", sk)?;
        Self::validate_range("st", st)?;
        Self::validate_range("se", se)?;
        Ok(Self { sk, st, se })
    }

    /// Create without validation (fast but unsafe).
    pub fn new_unchecked(sk: f64, st: f64, se: f64) -> Self {
        Self { sk, st, se }
    }

    fn validate_range(name: &str, val: f64) -> Result<(), SCoordError> {
        if !(0.0..=1.0).contains(&val) {
            return Err(SCoordError::OutOfBounds(name.to_string(), val));
        }
        Ok(())
    }

    /// Map frequency to S-entropy coordinates.
    pub fn from_frequency(frequency_hz: f64, n_states: usize) -> Self {
        let omega = 2.0 * PI * frequency_hz;
        let e = HBAR * omega;

        // S_knowledge: fraction of accessible states
        let p_accessible = if e > 0.0 {
            1.0 / (1.0 + (e / KT_ROOM_TEMP).exp())
        } else {
            0.5
        };

        let n_accessible = (p_accessible * n_states as f64).max(1.0);
        let sk = (n_accessible.log2() / (n_states as f64).log2()).clamp(0.0, 1.0);

        // S_time: temporal distance (log scale)
        let tau = 1.0 / frequency_hz.max(EPSILON);
        let st = ((tau.log10() + 15.0) / 20.0).clamp(0.0, 1.0);

        // S_entropy: phase distribution entropy
        let phase_variance = (frequency_hz / 1e12).min(1.0);
        let se = (-(1.0 - phase_variance + EPSILON).ln() / 10.0).clamp(0.0, 1.0);

        Self { sk, st, se }
    }

    /// Create from ndarray.
    pub fn from_array(arr: &Array1<f64>) -> Result<Self, SCoordError> {
        if arr.len() != 3 {
            return Err(SCoordError::InvalidShape(arr.len()));
        }
        Self::new(arr[0], arr[1], arr[2])
    }

    /// Origin of S-entropy space.
    pub fn origin() -> Self {
        Self {
            sk: 0.0,
            st: 0.0,
            se: 0.0,
        }
    }

    /// Equilibrium state (maximum entropy).
    pub fn equilibrium() -> Self {
        Self {
            sk: 1.0,
            st: 1.0,
            se: 1.0,
        }
    }

    /// Convert to ndarray.
    pub fn to_array(&self) -> Array1<f64> {
        Array1::from_vec(vec![self.sk, self.st, self.se])
    }

    /// Euclidean distance in S-entropy space.
    pub fn distance(&self, other: &SCoord) -> f64 {
        let dsk = self.sk - other.sk;
        let dst = self.st - other.st;
        let dse = self.se - other.se;
        (dsk * dsk + dst * dst + dse * dse).sqrt()
    }

    /// Compute gradient direction from self to other.
    pub fn gradient(&self, other: &SCoord) -> (f64, f64, f64) {
        let dsk = other.sk - self.sk;
        let dst = other.st - self.st;
        let dse = other.se - self.se;
        let norm = (dsk * dsk + dst * dst + dse * dse).sqrt() + EPSILON;
        (dsk / norm, dst / norm, dse / norm)
    }

    /// Create updated coordinate with deltas, clamped to [0, 1].
    pub fn update(&self, delta_sk: f64, delta_st: f64, delta_se: f64) -> Self {
        Self {
            sk: (self.sk + delta_sk).clamp(0.0, 1.0),
            st: (self.st + delta_st).clamp(0.0, 1.0),
            se: (self.se + delta_se).clamp(0.0, 1.0),
        }
    }

    /// Compute temperature from S-entropy coordinate.
    pub fn to_temperature(&self) -> f64 {
        self.to_temperature_with_ref(SE_REFERENCE, T_0_REFERENCE)
    }

    /// Compute temperature with custom reference.
    pub fn to_temperature_with_ref(&self, se_ref: f64, t_0: f64) -> f64 {
        t_0 * (self.se - se_ref).exp()
    }

    /// Total entropy magnitude |S| = sqrt(Sk^2 + St^2 + Se^2).
    pub fn entropy_magnitude(&self) -> f64 {
        (self.sk * self.sk + self.st * self.st + self.se * self.se).sqrt()
    }

    /// Categorical entropy S_cat = k_B * ln(n_accessible).
    pub fn categorical_entropy(&self, n_categories: usize) -> f64 {
        let n_accessible = (self.sk * n_categories as f64).max(1.0) as usize;
        BOLTZMANN_CONSTANT * (n_accessible as f64).ln()
    }

    /// Linear interpolation between self and other.
    pub fn interpolate(&self, other: &SCoord, t: f64) -> Result<Self, SCoordError> {
        if !(0.0..=1.0).contains(&t) {
            return Err(SCoordError::InvalidInterpolation(t));
        }
        Ok(Self {
            sk: self.sk + t * (other.sk - self.sk),
            st: self.st + t * (other.st - self.st),
            se: self.se + t * (other.se - self.se),
        })
    }
}

impl Default for SCoord {
    fn default() -> Self {
        Self::origin()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_origin_and_equilibrium() {
        let origin = SCoord::origin();
        assert_eq!(origin.sk, 0.0);
        assert_eq!(origin.st, 0.0);
        assert_eq!(origin.se, 0.0);

        let eq = SCoord::equilibrium();
        assert_eq!(eq.sk, 1.0);
        assert_eq!(eq.st, 1.0);
        assert_eq!(eq.se, 1.0);
    }

    #[test]
    fn test_distance() {
        let a = SCoord::origin();
        let b = SCoord::equilibrium();
        let d = a.distance(&b);
        assert!((d - 3.0_f64.sqrt()).abs() < 1e-10);
    }

    #[test]
    fn test_interpolation() {
        let a = SCoord::origin();
        let b = SCoord::equilibrium();
        let mid = a.interpolate(&b, 0.5).unwrap();
        assert!((mid.sk - 0.5).abs() < 1e-10);
        assert!((mid.st - 0.5).abs() < 1e-10);
        assert!((mid.se - 0.5).abs() < 1e-10);
    }

    #[test]
    fn test_validation() {
        assert!(SCoord::new(-0.1, 0.5, 0.5).is_err());
        assert!(SCoord::new(0.5, 1.1, 0.5).is_err());
        assert!(SCoord::new(0.5, 0.5, 0.5).is_ok());
    }
}
