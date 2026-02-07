//! Partition Operators: CAPACITY, D_CAT, partition_to_sentropy.
//!
//! Operators for working with partition coordinates.

use vb_core::error::PartitionCoordError;
use vb_core::types::{PartitionCoord, SCoord, Spin};

/// CAPACITY operator: Compute capacity at level n.
/// C(n) = 2n²
pub fn capacity(n: i32) -> Result<i32, PartitionCoordError> {
    PartitionCoord::capacity(n)
}

/// Total capacity up to level n_max.
pub fn total_capacity(n_max: i32) -> i64 {
    PartitionCoord::total_capacity(n_max)
}

/// D_CAT operator: Categorical distance between coordinates.
pub fn d_cat(c1: &PartitionCoord, c2: &PartitionCoord) -> f64 {
    c1.categorical_distance(c2)
}

/// PARTITION operator: Map state ID to partition coordinate.
pub fn partition(state_id: i64, n_max: i32) -> Result<PartitionCoord, PartitionCoordError> {
    let total = total_capacity(n_max);
    if state_id < 0 || state_id >= total {
        return Err(PartitionCoordError::InvalidIndex(state_id));
    }
    PartitionCoord::from_linear_index(state_id)
}

/// COORDS operator: Generate all coordinates at level n.
pub fn coords(n: i32) -> Result<Vec<PartitionCoord>, PartitionCoordError> {
    PartitionCoord::all_coords_at_level(n)
}

/// Map partition coordinate to S-entropy coordinate.
pub fn partition_to_sentropy(coord: &PartitionCoord, n_max: i32) -> SCoord {
    // Sk: based on n level (deeper = more knowledge)
    let sk = coord.n() as f64 / n_max as f64;

    // St: based on l complexity
    let st = if coord.n() > 1 {
        coord.l() as f64 / (coord.n() - 1) as f64
    } else {
        0.0
    };

    // Se: based on m orientation and spin
    let m_normalized = if coord.l() > 0 {
        (coord.m() as f64 + coord.l() as f64) / (2.0 * coord.l() as f64)
    } else {
        0.5
    };
    let spin_contrib = if coord.s() == Spin::Up { 0.5 } else { 0.0 };
    let se = (m_normalized + spin_contrib) / 1.5;

    SCoord::new_unchecked(sk.clamp(0.0, 1.0), st.clamp(0.0, 1.0), se.clamp(0.0, 1.0))
}

/// Map S-entropy coordinate to nearest partition coordinate.
pub fn sentropy_to_partition(s_coord: &SCoord, n_max: i32) -> Result<PartitionCoord, PartitionCoordError> {
    // Inverse mapping (approximate)
    let n = ((s_coord.sk * n_max as f64).round() as i32).max(1);
    let l = if n > 1 {
        ((s_coord.st * (n - 1) as f64).round() as i32).clamp(0, n - 1)
    } else {
        0
    };
    let m = if l > 0 {
        let m_frac = s_coord.se * 1.5 - 0.25;
        ((m_frac * 2.0 * l as f64 - l as f64).round() as i32).clamp(-l, l)
    } else {
        0
    };
    let s = if s_coord.se > 0.5 { Spin::Up } else { Spin::Down };

    PartitionCoord::new(n, l, m, s)
}

/// Find adjacent coordinates (D_cat = 1).
pub fn adjacent_coords(coord: &PartitionCoord) -> Vec<PartitionCoord> {
    let mut adjacent = Vec::new();
    let n = coord.n();
    let l = coord.l();
    let m = coord.m();
    let s = coord.s();

    // n ± 1
    if n > 1 {
        if let Ok(c) = PartitionCoord::new(n - 1, l.min(n - 2), m.clamp(-(l.min(n - 2)), l.min(n - 2)), s) {
            if coord.is_adjacent(&c) {
                adjacent.push(c);
            }
        }
    }
    if let Ok(c) = PartitionCoord::new(n + 1, l, m, s) {
        if coord.is_adjacent(&c) {
            adjacent.push(c);
        }
    }

    // l ± 1
    if l > 0 {
        if let Ok(c) = PartitionCoord::new(n, l - 1, m.clamp(-(l - 1), l - 1), s) {
            if coord.is_adjacent(&c) {
                adjacent.push(c);
            }
        }
    }
    if l + 1 < n {
        if let Ok(c) = PartitionCoord::new(n, l + 1, m, s) {
            if coord.is_adjacent(&c) {
                adjacent.push(c);
            }
        }
    }

    // m ± 1
    if m > -l {
        if let Ok(c) = PartitionCoord::new(n, l, m - 1, s) {
            if coord.is_adjacent(&c) {
                adjacent.push(c);
            }
        }
    }
    if m < l {
        if let Ok(c) = PartitionCoord::new(n, l, m + 1, s) {
            if coord.is_adjacent(&c) {
                adjacent.push(c);
            }
        }
    }

    // Spin flip (ds = 1)
    let other_spin = match s {
        Spin::Up => Spin::Down,
        Spin::Down => Spin::Up,
    };
    if let Ok(c) = PartitionCoord::new(n, l, m, other_spin) {
        if coord.is_adjacent(&c) {
            adjacent.push(c);
        }
    }

    adjacent
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_capacity() {
        assert_eq!(capacity(1).unwrap(), 2);
        assert_eq!(capacity(2).unwrap(), 8);
        assert_eq!(capacity(3).unwrap(), 18);
    }

    #[test]
    fn test_partition_mapping() {
        for idx in 0..28 {
            let coord = partition(idx, 3).unwrap();
            assert_eq!(coord.to_linear_index(), idx);
        }
    }

    #[test]
    fn test_partition_to_sentropy() {
        let coord = PartitionCoord::new(2, 1, 0, Spin::Up).unwrap();
        let s = partition_to_sentropy(&coord, 4);
        assert!(s.sk > 0.0 && s.sk <= 1.0);
        assert!(s.st >= 0.0 && s.st <= 1.0);
        assert!(s.se >= 0.0 && s.se <= 1.0);
    }

    #[test]
    fn test_adjacent_coords() {
        let coord = PartitionCoord::new(2, 1, 0, Spin::Up).unwrap();
        let adj = adjacent_coords(&coord);
        for a in &adj {
            assert!(coord.is_adjacent(a));
        }
    }
}
