//! # Virtual Brain Engine
//!
//! Core simulation engine for the Virtual Brain computing framework.
//!
//! ## Components
//!
//! - `PoincareComputer`: Main simulation engine for consciousness computation
//! - `StateManager`: State transition and history management

pub mod poincare_computer;
pub mod state_manager;

pub use poincare_computer::{ComputeResult, PoincareComputer};
pub use state_manager::{StateManager, TransitionResult};
