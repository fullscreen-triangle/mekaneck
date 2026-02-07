//! PartitionCoord: Quantum-style categorical coordinates (n, l, m, s).
//!
//! Implements the partition coordinate system with capacity C(n) = 2n^2.
//! Maps categorical states to a hierarchical addressing scheme analogous
//! to atomic quantum numbers but for categorical neural states.
//!
//! ```text
//! Capacity formula: C(n) = 2n^2
//!   n=1: C=2,  n=2: C=8,  n=3: C=18,  n=4: C=32, ...
//!
//! Constraints:
//!   n >= 1         (principal quantum number)
//!   0 <= l < n     (orbital quantum number)
//!   -l <= m <= +l  (magnetic quantum number)
//!   s in {-0.5, +0.5}  (spin quantum number)
//! ```

use crate::error::PartitionCoordError;
use serde::{Deserialize, Serialize};

/// Spin values representing chirality
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub enum Spin {
    /// Spin down (-0.5)
    Down,
    /// Spin up (+0.5)
    Up,
}

impl Spin {
    /// Get the numerical value of the spin
    pub fn value(&self) -> f64 {
        match self {
            Spin::Down => -0.5,
            Spin::Up => 0.5,
        }
    }

    /// Create Spin from numerical value
    pub fn from_value(v: f64) -> Result<Self, PartitionCoordError> {
        if (v - (-0.5)).abs() < 1e-10 {
            Ok(Spin::Down)
        } else if (v - 0.5).abs() < 1e-10 {
            Ok(Spin::Up)
        } else {
            Err(PartitionCoordError::InvalidSpin(v))
        }
    }
}

/// Partition coordinate representing categorical state location.
///
/// Analogous to quantum numbers (n, l, m, s) but for categorical states.
/// This type is immutable and hashable, suitable for use as map keys.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub struct PartitionCoord {
    /// Principal quantum number (partition depth), n >= 1
    n: i32,
    /// Orbital quantum number (complexity), 0 <= l < n
    l: i32,
    /// Magnetic quantum number (orientation), -l <= m <= +l
    m: i32,
    /// Spin quantum number (chirality)
    s: Spin,
}

impl PartitionCoord {
    /// Create a new PartitionCoord with validation.
    pub fn new(n: i32, l: i32, m: i32, s: Spin) -> Result<Self, PartitionCoordError> {
        if n < 1 {
            return Err(PartitionCoordError::InvalidN(n));
        }
        if l < 0 || l >= n {
            return Err(PartitionCoordError::InvalidL(l, n));
        }
        if m < -l || m > l {
            return Err(PartitionCoordError::InvalidM(m, l));
        }
        Ok(Self { n, l, m, s })
    }

    /// Create from f64 spin value (for Python interop).
    pub fn from_components(n: i32, l: i32, m: i32, s_val: f64) -> Result<Self, PartitionCoordError> {
        let s = Spin::from_value(s_val)?;
        Self::new(n, l, m, s)
    }

    // Accessor methods
    pub fn n(&self) -> i32 {
        self.n
    }
    pub fn l(&self) -> i32 {
        self.l
    }
    pub fn m(&self) -> i32 {
        self.m
    }
    pub fn s(&self) -> Spin {
        self.s
    }
    pub fn s_value(&self) -> f64 {
        self.s.value()
    }

    /// Compute capacity at level n: C(n) = 2n^2
    pub fn capacity(n: i32) -> Result<i32, PartitionCoordError> {
        if n < 1 {
            return Err(PartitionCoordError::InvalidN(n));
        }
        Ok(2 * n * n)
    }

    /// Compute cumulative capacity up to level n_max.
    /// Sum_{i=1}^{n_max} 2i^2 = n_max(n_max+1)(2n_max+1)/3
    pub fn total_capacity(n_max: i32) -> i64 {
        if n_max < 1 {
            return 0;
        }
        let n = n_max as i64;
        n * (n + 1) * (2 * n + 1) / 3
    }

    /// Compute density of states: rho(n) = dC/dn = 4n
    pub fn density_of_states(n: i32) -> i32 {
        4 * n
    }

    /// Convert to linear index for O(1) array lookups.
    pub fn to_linear_index(&self) -> i64 {
        let offset = Self::total_capacity(self.n - 1);

        // States within this n level, ordered by (l, m, s)
        let mut l_offset: i64 = 0;
        for l_val in 0..self.l {
            l_offset += 2 * (2 * l_val as i64 + 1); // 2*(2l+1) states per l
        }

        let m_offset = (self.m + self.l) as i64; // Map m from [-l, l] to [0, 2l]
        let s_offset = match self.s {
            Spin::Down => 0,
            Spin::Up => 1,
        };

        offset + l_offset + 2 * m_offset + s_offset
    }

    /// Reconstruct PartitionCoord from linear index.
    pub fn from_linear_index(index: i64) -> Result<Self, PartitionCoordError> {
        if index < 0 {
            return Err(PartitionCoordError::InvalidIndex(index));
        }

        // Find n level
        let mut n = 1;
        while Self::total_capacity(n) <= index {
            n += 1;
        }

        // Remaining index within n level
        let mut remaining = index - Self::total_capacity(n - 1);

        // Find l
        let mut l = 0;
        loop {
            let states_at_l = 2 * (2 * l as i64 + 1);
            if remaining < states_at_l {
                break;
            }
            remaining -= states_at_l;
            l += 1;
        }

        // Find m and s
        let m = (remaining / 2) as i32 - l;
        let s = if remaining % 2 == 0 {
            Spin::Down
        } else {
            Spin::Up
        };

        Self::new(n, l, m, s)
    }

    /// Compute categorical distance D_cat between coordinates.
    /// D_cat = sqrt((dn)^2 + (dl)^2 + (dm)^2 + (ds)^2)
    pub fn categorical_distance(&self, other: &PartitionCoord) -> f64 {
        let dn = (self.n - other.n) as f64;
        let dl = (self.l - other.l) as f64;
        let dm = (self.m - other.m) as f64;
        let ds = self.s.value() - other.s.value();

        (dn * dn + dl * dl + dm * dm + ds * ds).sqrt()
    }

    /// Check if coordinates are adjacent (D_cat = 1).
    pub fn is_adjacent(&self, other: &PartitionCoord) -> bool {
        (self.categorical_distance(other) - 1.0).abs() < 1e-10
    }

    /// Generate all coordinates at partition level n.
    pub fn all_coords_at_level(n: i32) -> Result<Vec<PartitionCoord>, PartitionCoordError> {
        if n < 1 {
            return Err(PartitionCoordError::InvalidN(n));
        }

        let mut coords = Vec::with_capacity(Self::capacity(n)? as usize);
        for l in 0..n {
            for m in -l..=l {
                coords.push(PartitionCoord::new(n, l, m, Spin::Down)?);
                coords.push(PartitionCoord::new(n, l, m, Spin::Up)?);
            }
        }
        Ok(coords)
    }

    /// Iterator over all coordinates up to level n_max.
    pub fn iter_all(n_max: i32) -> impl Iterator<Item = PartitionCoord> {
        (1..=n_max).flat_map(|n| Self::all_coords_at_level(n).unwrap_or_default())
    }

    /// Compute energy level: E_n = E_max * (n / n_max)^2
    pub fn energy_level(&self, e_max: f64, n_max: i32) -> f64 {
        e_max * (self.n as f64 / n_max as f64).powi(2)
    }
}

impl Default for PartitionCoord {
    fn default() -> Self {
        Self::new(1, 0, 0, Spin::Down).unwrap()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_capacity_formula() {
        assert_eq!(PartitionCoord::capacity(1).unwrap(), 2);
        assert_eq!(PartitionCoord::capacity(2).unwrap(), 8);
        assert_eq!(PartitionCoord::capacity(3).unwrap(), 18);
        assert_eq!(PartitionCoord::capacity(4).unwrap(), 32);
        assert_eq!(PartitionCoord::capacity(5).unwrap(), 50);
    }

    #[test]
    fn test_total_capacity() {
        assert_eq!(PartitionCoord::total_capacity(1), 2);
        assert_eq!(PartitionCoord::total_capacity(2), 10); // 2 + 8
        assert_eq!(PartitionCoord::total_capacity(3), 28); // 2 + 8 + 18
    }

    #[test]
    fn test_linear_index_bijection() {
        for idx in 0..100 {
            let coord = PartitionCoord::from_linear_index(idx).unwrap();
            assert_eq!(coord.to_linear_index(), idx);
        }
    }

    #[test]
    fn test_distance_symmetry() {
        let c1 = PartitionCoord::new(2, 1, 0, Spin::Up).unwrap();
        let c2 = PartitionCoord::new(3, 1, 1, Spin::Down).unwrap();
        assert!((c1.categorical_distance(&c2) - c2.categorical_distance(&c1)).abs() < 1e-10);
    }

    #[test]
    fn test_validation() {
        assert!(PartitionCoord::new(0, 0, 0, Spin::Up).is_err());
        assert!(PartitionCoord::new(1, 1, 0, Spin::Up).is_err()); // l >= n
        assert!(PartitionCoord::new(2, 1, 2, Spin::Up).is_err()); // m > l
    }
}
