//! # Policy
//!
//! Selection under a bounded budget, phase exclusion, and relay provenance.
//!
//! Everything here sits **above** the kernel. That placement is load-bearing:
//! selection needs a per-candidate gain, gain is an interpretive quantity, and
//! by the Inertia Theorem the kernel computes no such thing. A module uses
//! this crate to decide what to contribute; the kernel still executes whatever
//! it is given and judges none of it.
//!
//! Three results are carried by the types rather than by discipline:
//!
//! - [`Budget::max_commitments`] bounds commitments by `floor(A/β)` whatever
//!   the gains, so declining is visibly forced by boundedness rather than by
//!   a judgement about what was declined.
//! - [`Selection::shadow_price`] is the density of the first *excluded*
//!   candidate, not the last admitted one — the latter is not monotone in the
//!   budget, and using it would give a price that rises as attention widens.
//! - [`Relayed`] carries depth and fidelity but exposes no predicate for a
//!   relayed account being false. Accumulated drift is computable; falsity
//!   would be a comparison against a value no observer holds.
//!
//! ```
//! use mekaneck_policy::*;
//!
//! let candidates = vec![
//!     Candidate::new("cheap-and-good", 1.0, 0.9)?,
//!     Candidate::new("costly",         3.0, 1.0)?,
//! ];
//! let selection = select(&candidates, Budget::new(2.0, 0.5)?);
//!
//! assert_eq!(selection.committed, vec!["cheap-and-good"]);
//! assert!(selection.declined_any());          // forced, not a failure
//! # Ok::<(), Error>(())
//! ```

#![forbid(unsafe_code)]
#![warn(missing_debug_implementations)]

pub mod budget;
pub mod phase;
pub mod relay;

pub use budget::{is_divisible, select, Budget, Candidate, Selection};
pub use phase::{classify, Phase, PhaseLog, Quiescence};
pub use relay::{fidelity_bound, relays_until, Relayed};

/// Errors from the policy layer.
#[derive(Debug, Clone, PartialEq, thiserror::Error)]
pub enum Error {
    #[error("cost must be strictly positive, got {0}")]
    NonPositiveCost(f64),

    #[error("budget must be strictly positive, got {0}")]
    NonPositiveBudget(f64),

    #[error("floor must be strictly positive, got {0}")]
    NonPositiveFloor(f64),

    #[error("costs and gains must be finite")]
    NonFinite,

    #[error(transparent)]
    Algebra(#[from] mekaneck_algebra::Error),
}
