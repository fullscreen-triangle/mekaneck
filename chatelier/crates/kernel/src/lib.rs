//! # A semantically inert kernel
//!
//! A Rust port of the runtime specified in *A Semantically Inert Microkernel*
//! and validated in `chatelier/validation/validate_kernel.py`.
//!
//! The kernel executes and does not judge. That commitment is structural here
//! rather than conventional, in three places:
//!
//! - [`Kernel`] exposes no `status`, no `exit_code`, and no `failed`. There is
//!   no quantity it computes that could mean "wrong" (Thm 3.1).
//! - [`Value`] has no `PartialEq`, no `PartialOrd`, and no predicate over
//!   contents that the kernel calls. Nothing in this crate branches on what a
//!   value says, so a raising chunk cannot truncate a run (Cor 3.2).
//! - [`Node::emit`] adjoins; there is no `set`, `remove` or `clear`, so no
//!   emission destroys a prior one (Cor 3.3) and the record cannot decrease
//!   (Thm 6.1).
//!
//! Adjudication is thereby relocated into the modules that read values, where
//! it is visible and revisable, rather than residing in the substrate.
//!
//! ```
//! use mekaneck_kernel::*;
//! use serde_json::json;
//!
//! let mut k = Kernel::new();
//! k.graph.merge(
//!     Contribution::new()
//!         .with("analysis", Chunk::new(ChunkId::of("a"), "demo", || Ok(json!(1))))
//!         .with("analysis", Chunk::new(ChunkId::of("b"), "demo", || Err("boom".into())))
//!         .with("analysis", Chunk::new(ChunkId::of("c"), "demo", || Ok(json!(3)))),
//! );
//!
//! // every chunk runs; the failure is a value, not a control transfer
//! assert_eq!(k.run_node("analysis"), 3);
//! assert_eq!(k.graph.read("analysis").len(), 3);
//! assert_eq!(k.record().get(), 3);
//! ```

#![forbid(unsafe_code)]
#![warn(missing_debug_implementations)]

pub mod exec;
pub mod graph;
pub mod node;
pub mod schedule;
pub mod trajectory;

pub use exec::{Commit, Kernel, Record};
pub use graph::{Contribution, Graph};
pub use node::{Chunk, ChunkId, Node, Tau, Value};
pub use schedule::{Scheduler, Selection, Sweep};
pub use trajectory::{Link, Trajectory};

/// Errors the kernel can report.
///
/// Deliberately few. Most conditions a conventional runtime treats as errors
/// — a chunk raising, an unexpected value, a node yielding nothing — are here
/// ordinary outcomes recorded in the value store.
#[derive(Debug, Clone, PartialEq, Eq, thiserror::Error)]
pub enum Error {
    #[error("no node bears the identity {0:?}")]
    NoSuchNode(String),
}
