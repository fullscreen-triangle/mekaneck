//! # Virtual Brain Operators
//!
//! Mathematical operators for the Virtual Brain computing framework.
//!
//! ## Modules
//!
//! - `partition_ops`: Partition coordinate operators (CAPACITY, D_CAT)
//! - `sentropy_ops`: S-entropy navigation operators (NAVIGATE, GRAD_S)
//! - `ternary_ops`: Ternary tree operators (ENCODE, DECODE, TRISECT)
//! - `neural_ops`: Neural operators (CONSCIOUSNESS, MEMORY, DREAM, WAKE)
//! - `dynamics_ops`: Kuramoto dynamics (KURAMOTO, PHASE_LOCK, CASCADE)
//! - `poincare_ops`: Poincare computing (COMPLETE, TARGET, EQUILIBRIUM)
//! - `charge_ops`: Charge transport (CONSERVE, REDISTRIBUTE)

pub mod charge_ops;
pub mod dynamics_ops;
pub mod neural_ops;
pub mod partition_ops;
pub mod poincare_ops;
pub mod sentropy_ops;
pub mod ternary_ops;

// Re-export commonly used items
pub use dynamics_ops::{
    cascade, coherence, critical_coupling, kuramoto, kuramoto_with_drug, phase_lock,
    simulate_kuramoto, variance, KuramotoState,
};
pub use neural_ops::{consciousness, dream, evolve_mental_state, memory, wake};
pub use partition_ops::{adjacent_coords, capacity, coords, d_cat, partition, partition_to_sentropy};
pub use poincare_ops::{complete, equilibrium, satisfy, target, CompletionResult};
pub use sentropy_ops::{grad_s, minimize_free_energy, navigate, update_se, update_sk, update_st};
pub use ternary_ops::{decode, decode_float, encode, encode_float, ternary_search, trisect};
