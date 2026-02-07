//! # Virtual Brain Validators
//!
//! Validation suite for the Virtual Brain computing framework.
//!
//! ## Components
//!
//! - `Validator` trait: Abstract base for all validators
//! - `ValidationResult`: Standard result structure
//! - `PartitionValidator`: Validates partition coordinate system
//! - `KuramotoValidator`: Validates Kuramoto dynamics
//! - `ConsciousnessValidator`: Validates consciousness equations
//! - `ValidationSuite`: Orchestrates all validators

pub mod base;
pub mod consciousness_validator;
pub mod kuramoto_validator;
pub mod orchestrator;
pub mod partition_validator;

pub use base::{ValidationResult, Validator};
pub use consciousness_validator::ConsciousnessValidator;
pub use kuramoto_validator::KuramotoValidator;
pub use orchestrator::ValidationSuite;
pub use partition_validator::PartitionValidator;
