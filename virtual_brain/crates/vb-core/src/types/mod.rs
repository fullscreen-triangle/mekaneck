//! Core types for the Virtual Brain framework.
//!
//! This module contains the fundamental data structures:
//! - `PartitionCoord`: Quantum-style categorical coordinates (n, l, m, s)
//! - `SCoord`: S-entropy coordinates in [0,1]^3
//! - `TernaryAddr`: Ternary addressing for O(log3 n) navigation
//! - `MentalState`: Complete mental state (gamma, gamma_f, M)
//! - `CircuitState`: Circuit regime detection

pub mod circuit_state;
pub mod mental_state;
pub mod partition_coord;
pub mod s_coord;
pub mod ternary_addr;

// Re-exports
pub use circuit_state::{CircuitRegime, CircuitState};
pub use mental_state::MentalState;
pub use partition_coord::{PartitionCoord, Spin};
pub use s_coord::SCoord;
pub use ternary_addr::TernaryAddr;
