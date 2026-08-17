//! # Residual algebra
//!
//! A Rust port of the algebra specified in *A Residual Algebra for Catalytic
//! Composition* and validated in `chatelier/validation/validate_algebra.py`.
//!
//! The crate has one quantity and one law. The quantity is the residual, whose
//! positivity is derived rather than posited ([`residual`]); the law is that
//! residual factors multiply ([`compose`]).
//!
//! Three of the paper's results are enforced by the types rather than left to
//! the caller's discipline:
//!
//! 1. [`Floor`] cannot hold a non-positive value, so the denominator of
//!    Def 4.1 is never zero.
//! 2. [`Estimation`] travels with every prediction, and
//!    [`CompositionTest::is_evidential`] is false under instance-specific
//!    estimation however good the agreement looks — this is the telescoping
//!    obstruction (Thm 5.2), which reports `r = 1.000` on data from any
//!    process whatsoever.
//! 3. [`FloorEstimator`] records whether an estimate *could* have come out
//!    non-positive, so a reported positive floor carries its own evidential
//!    status.
//!
//! ```
//! use mekaneck_algebra::*;
//!
//! let floor = Floor::new(10.0)?;
//! let before = State::new(100.0)?;
//! let after = State::new(55.0)?;
//!
//! // half the outstanding gap
//! let p = Power::measure(before, after, floor)?;
//! assert!((p.kappa() - 0.5).abs() < 1e-12);
//!
//! // residual factors multiply
//! let net = compose(&[p, p])?;
//! assert!((net.kappa() - 0.75).abs() < 1e-12);
//! # Ok::<(), Error>(())
//! ```

#![forbid(unsafe_code)]
#![warn(missing_debug_implementations)]

pub mod cascade;
pub mod compose;
pub mod diagnose;
pub mod power;
pub mod residual;

pub use cascade::{run_to_closure, run_to_threshold, Catalyst, Cell, ClosureRun, Outcome};
pub use compose::{
    compose, test_cascade, Cascade, CompositionTest, Estimation, Event, Law, TypeAverages,
};
pub use diagnose::{pearson, rmse, separation, Separation, UNINFORMATIVE_ETA};
pub use power::{Floor, Power, State};
pub use residual::{ExpandingFamily, FloorEstimate, FloorEstimator, ZERO_TOLERANCE};

/// Errors the algebra can report.
///
/// Every variant marks a precondition of a numbered result. None is a
/// recoverable-by-default condition: each means the caller has asked for a
/// quantity that is undefined rather than merely awkward.
#[derive(Debug, Clone, PartialEq, thiserror::Error)]
pub enum Error {
    #[error("floor must be strictly positive, got {0} (Cor 3.2)")]
    NonPositiveFloor(f64),

    #[error("{0} must be finite")]
    NonFinite(&'static str),

    #[error("power {0} exceeds 1: the post-state would lie below the floor (Cor 3.3)")]
    PowerAboveUnity(f64),

    #[error("pre-state {state} is at or below the floor {floor}: no outstanding gap (Def 4.1)")]
    PreStateAtFloor { state: f64, floor: f64 },

    #[error("a cascade needs at least one event")]
    EmptyCascade,

    #[error("type-averaged estimation requires fitted type averages (Def 5.4)")]
    MissingTypeAverages,

    #[error("event type {0:?} was not seen when the type averages were fitted")]
    UnknownEventType(String),

    #[error("geometric-mean law is not real-valued for residual product {0}")]
    NonRealGeometricMean(f64),

    #[error("an expanding family needs at least one stage")]
    EmptyFamily,

    #[error("a stage needs at least one observation")]
    EmptyStage,

    #[error("asymptotic estimation needs {need} stages, got {got}")]
    InsufficientStages { got: usize, need: usize },

    #[error("all stages are the same size: the fit has no leverage on the intercept")]
    DegenerateDesign,

    #[error("a catalyst registry must be non-empty")]
    EmptyRegistry,
}
