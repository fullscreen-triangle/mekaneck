//! Error types for the Virtual Brain framework.

use thiserror::Error;

/// Errors for PartitionCoord operations
#[derive(Error, Debug, Clone)]
pub enum PartitionCoordError {
    #[error("n must be >= 1, got {0}")]
    InvalidN(i32),

    #[error("l must be in [0, n), got l={0}, n={1}")]
    InvalidL(i32, i32),

    #[error("m must be in [-l, l], got m={0}, l={1}")]
    InvalidM(i32, i32),

    #[error("s must be +/-0.5, got {0}")]
    InvalidSpin(f64),

    #[error("Index must be non-negative, got {0}")]
    InvalidIndex(i64),
}

/// Errors for SCoord operations
#[derive(Error, Debug, Clone)]
pub enum SCoordError {
    #[error("{0} must be in [0, 1], got {1}")]
    OutOfBounds(String, f64),

    #[error("Array must have length 3, got {0}")]
    InvalidShape(usize),

    #[error("Interpolation parameter t must be in [0, 1], got {0}")]
    InvalidInterpolation(f64),
}

/// Errors for TernaryAddr operations
#[derive(Error, Debug, Clone)]
pub enum TernaryAddrError {
    #[error("Digit must be 0, 1, or 2, got {0}")]
    InvalidDigit(u8),

    #[error("Value {0} exceeds max {1} for depth {2}")]
    ValueExceedsCapacity(u64, u64, usize),

    #[error("Value must be in [0, 1], got {0}")]
    ValueOutOfBounds(f64),

    #[error("Direction must be 0, 1, or 2, got {0}")]
    InvalidDirection(u8),

    #[error("Ternary address must start with 'T', got {0}")]
    InvalidPrefix(String),
}

/// Errors for MentalState operations
#[derive(Error, Debug, Clone)]
pub enum MentalStateError {
    #[error("{0} must be in [0, 1], got {1}")]
    OutOfBounds(String, f64),
}

/// General Virtual Brain errors
#[derive(Error, Debug)]
pub enum VBError {
    #[error("Partition coordinate error: {0}")]
    PartitionCoord(#[from] PartitionCoordError),

    #[error("S-coordinate error: {0}")]
    SCoord(#[from] SCoordError),

    #[error("Ternary address error: {0}")]
    TernaryAddr(#[from] TernaryAddrError),

    #[error("Mental state error: {0}")]
    MentalState(#[from] MentalStateError),

    #[error("Computation error: {0}")]
    Computation(String),

    #[error("Validation error: {0}")]
    Validation(String),
}
