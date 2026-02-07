//! TernaryAddr: Ternary addressing with O(log3 n) navigation.
//!
//! The ternary system provides 37% efficiency improvement over binary
//! (log_2(3) ≈ 1.585 bits per trit vs 1 bit per bit).

use crate::error::TernaryAddrError;
use serde::{Deserialize, Serialize};

/// Ternary address for O(log3 n) categorical navigation.
#[derive(Debug, Clone, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub struct TernaryAddr {
    digits: Vec<u8>,
}

impl TernaryAddr {
    /// Create from digit vector with validation.
    pub fn new(digits: Vec<u8>) -> Result<Self, TernaryAddrError> {
        for &d in &digits {
            if d > 2 {
                return Err(TernaryAddrError::InvalidDigit(d));
            }
        }
        Ok(Self { digits })
    }

    /// Create without validation.
    pub fn new_unchecked(digits: Vec<u8>) -> Self {
        Self { digits }
    }

    /// Get the digits.
    pub fn digits(&self) -> &[u8] {
        &self.digits
    }

    /// Depth of this address in the ternary tree.
    pub fn depth(&self) -> usize {
        self.digits.len()
    }

    /// Resolution (region size) at this depth.
    pub fn resolution(&self) -> f64 {
        3.0_f64.powi(-(self.depth() as i32))
    }

    /// Encode integer to ternary address of given depth.
    pub fn encode(value: u64, depth: usize) -> Result<Self, TernaryAddrError> {
        let max_value = 3u64.pow(depth as u32) - 1;
        if value > max_value {
            return Err(TernaryAddrError::ValueExceedsCapacity(
                value, max_value, depth,
            ));
        }

        let mut digits = Vec::with_capacity(depth);
        let mut remaining = value;

        for _ in 0..depth {
            digits.push((remaining % 3) as u8);
            remaining /= 3;
        }

        digits.reverse();
        Ok(Self { digits })
    }

    /// Encode float in [0, 1] to ternary address.
    pub fn from_float(value: f64, depth: usize) -> Result<Self, TernaryAddrError> {
        if !(0.0..=1.0).contains(&value) {
            return Err(TernaryAddrError::ValueOutOfBounds(value));
        }

        let mut digits = Vec::with_capacity(depth);
        let (mut low, mut high) = (0.0, 1.0);

        for _ in 0..depth {
            let third = (high - low) / 3.0;
            if value < low + third {
                digits.push(0);
                high = low + third;
            } else if value < low + 2.0 * third {
                digits.push(1);
                let new_low = low + third;
                high = new_low + third;
                low = new_low;
            } else {
                digits.push(2);
                low += 2.0 * third;
            }
        }

        Ok(Self { digits })
    }

    /// Decode to integer.
    pub fn decode(&self) -> u64 {
        self.digits.iter().fold(0u64, |acc, &d| acc * 3 + d as u64)
    }

    /// Decode to float (center of addressed interval).
    pub fn to_float(&self) -> f64 {
        let (low, high) = self.interval();
        (low + high) / 2.0
    }

    /// Get the interval [low, high] addressed by this address.
    pub fn interval(&self) -> (f64, f64) {
        let (mut low, mut high) = (0.0, 1.0);

        for &d in &self.digits {
            let third = (high - low) / 3.0;
            match d {
                0 => high = low + third,
                1 => {
                    let new_low = low + third;
                    high = new_low + third;
                    low = new_low;
                }
                2 => low += 2.0 * third,
                _ => unreachable!(),
            }
        }

        (low, high)
    }

    /// Trisect into three child addresses.
    pub fn trisect(&self) -> (Self, Self, Self) {
        let mut left = self.digits.clone();
        let mut middle = self.digits.clone();
        let mut right = self.digits.clone();
        left.push(0);
        middle.push(1);
        right.push(2);
        (
            Self { digits: left },
            Self { digits: middle },
            Self { digits: right },
        )
    }

    /// Get parent address (one level up).
    pub fn parent(&self) -> Option<Self> {
        if self.digits.is_empty() {
            None
        } else {
            Some(Self {
                digits: self.digits[..self.digits.len() - 1].to_vec(),
            })
        }
    }

    /// Navigate to child in given direction.
    pub fn navigate(&self, direction: u8) -> Result<Self, TernaryAddrError> {
        if direction > 2 {
            return Err(TernaryAddrError::InvalidDirection(direction));
        }
        let mut digits = self.digits.clone();
        digits.push(direction);
        Ok(Self { digits })
    }

    /// Find lowest common ancestor.
    pub fn common_ancestor(&self, other: &TernaryAddr) -> Self {
        let common: Vec<u8> = self
            .digits
            .iter()
            .zip(other.digits.iter())
            .take_while(|(a, b)| a == b)
            .map(|(&a, _)| a)
            .collect();
        Self { digits: common }
    }

    /// Navigation distance through tree.
    pub fn navigation_distance(&self, other: &TernaryAddr) -> usize {
        let ancestor = self.common_ancestor(other);
        self.depth() + other.depth() - 2 * ancestor.depth()
    }

    /// Path from self to other through tree.
    pub fn path_to(&self, other: &TernaryAddr) -> Vec<TernaryAddr> {
        let ancestor = self.common_ancestor(other);
        let mut path = Vec::new();

        // Path up to ancestor
        let mut current = self.clone();
        while current.depth() > ancestor.depth() {
            path.push(current.clone());
            current = current.parent().unwrap();
        }

        // Path down from ancestor
        let mut down_path = Vec::new();
        let mut current = other.clone();
        while current.depth() > ancestor.depth() {
            down_path.push(current.clone());
            current = current.parent().unwrap();
        }

        path.push(ancestor);
        path.extend(down_path.into_iter().rev());
        path
    }

    /// Root address (empty).
    pub fn root() -> Self {
        Self { digits: vec![] }
    }

    /// String representation.
    pub fn to_string_repr(&self) -> String {
        format!(
            "T{}",
            self.digits.iter().map(|d| d.to_string()).collect::<String>()
        )
    }

    /// Parse from string.
    pub fn from_string(s: &str) -> Result<Self, TernaryAddrError> {
        if !s.starts_with('T') {
            return Err(TernaryAddrError::InvalidPrefix(s.to_string()));
        }
        if s.len() == 1 {
            return Ok(Self::root());
        }
        let digits: Result<Vec<u8>, _> = s[1..]
            .chars()
            .map(|c| {
                c.to_digit(10)
                    .map(|d| d as u8)
                    .ok_or(TernaryAddrError::InvalidDigit(255))
            })
            .collect();
        Self::new(digits?)
    }
}

impl Default for TernaryAddr {
    fn default() -> Self {
        Self::root()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_encode_decode() {
        for depth in 1..=5 {
            let max_val = 3u64.pow(depth as u32) - 1;
            for val in 0..=max_val.min(100) {
                let addr = TernaryAddr::encode(val, depth).unwrap();
                assert_eq!(addr.decode(), val);
            }
        }
    }

    #[test]
    fn test_float_encoding() {
        let addr = TernaryAddr::from_float(0.5, 5).unwrap();
        let decoded = addr.to_float();
        assert!((decoded - 0.5).abs() < 0.1);
    }

    #[test]
    fn test_trisect() {
        let root = TernaryAddr::root();
        let (left, mid, right) = root.trisect();
        assert_eq!(left.digits(), &[0]);
        assert_eq!(mid.digits(), &[1]);
        assert_eq!(right.digits(), &[2]);
    }

    #[test]
    fn test_navigation_distance() {
        let a = TernaryAddr::new(vec![0, 1]).unwrap();
        let b = TernaryAddr::new(vec![0, 2]).unwrap();
        assert_eq!(a.navigation_distance(&b), 2); // Up to [0], down to [0,2]
    }

    #[test]
    fn test_string_roundtrip() {
        let addr = TernaryAddr::new(vec![0, 1, 2]).unwrap();
        let s = addr.to_string_repr();
        assert_eq!(s, "T012");
        let parsed = TernaryAddr::from_string(&s).unwrap();
        assert_eq!(addr, parsed);
    }
}
