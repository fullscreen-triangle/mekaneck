//! # Virtual Brain Core
//!
//! Core types and constants for the Virtual Brain computing framework.
//!
//! ## Overview
//!
//! This crate provides the fundamental building blocks:
//!
//! - **Constants**: Physical constants (Boltzmann, Planck, timescales)
//! - **Types**: Core data structures for the framework
//!   - `PartitionCoord`: Quantum-style categorical coordinates with C(n) = 2n²
//!   - `SCoord`: S-entropy coordinates in [0,1]³ space
//!   - `TernaryAddr`: Ternary addressing with O(log₃ n) navigation
//!   - `MentalState`: Complete mental state representation
//!   - `CircuitState`: Circuit regime detection
//!
//! ## Example
//!
//! ```rust
//! use vb_core::types::{PartitionCoord, SCoord, Spin};
//!
//! // Create a partition coordinate
//! let coord = PartitionCoord::new(2, 1, 0, Spin::Up).unwrap();
//! assert_eq!(PartitionCoord::capacity(2).unwrap(), 8);
//!
//! // Create an S-entropy coordinate
//! let s = SCoord::new(0.5, 0.3, 0.7).unwrap();
//! assert!(s.entropy_magnitude() > 0.0);
//! ```

pub mod constants;
pub mod error;
pub mod types;

// Re-export commonly used items
pub use constants::*;
pub use error::*;
pub use types::*;
