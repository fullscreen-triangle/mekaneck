//! # Mekaneck (`.mck`)
//!
//! A Rust port of the language specified in *Mekaneck: A Substrate-Neutral
//! Language for Individuation-Structured Inquiry* and validated in
//! `chatelier/validation/validate_mekaneck.py`.
//!
//! One primitive, `seek`, with a mandatory exclusion clause and termination by
//! closure rather than by threshold. Two commitments are enforced by the
//! implementation rather than by convention:
//!
//! - a `seek` without `excluding` is rejected at parse time, because a
//!   positive description alone does not determine a target (Thm 4.3);
//! - a `via` clause naming fewer than three mutually independent catalysts is
//!   rejected by the type checker, because no shorter support structure
//!   survives the loss of a member (Thm 6.2).
//!
//! ```
//! use mekaneck_lang::{parse, typecheck, eval_seek, FixedSubstrate, Outcome};
//! use std::collections::BTreeMap;
//!
//! let src = r#"
//! substrate S { receivers : r(); observable : o(); events : e(); floor : asymptotic(); }
//! catalyst a : f() independent b, c;
//! catalyst b : g() independent a, c;
//! catalyst c : h() independent a, b;
//! let x = seek t() excluding rest() via (a, b, c) until closure;
//! report x;
//! "#;
//!
//! let prog = parse(src)?;
//! let mut floors = BTreeMap::new();
//! floors.insert("S".to_string(), 12.5);
//! typecheck(&prog, &floors)?;
//!
//! // two catalysts agree, one does not: the honest report is a declination
//! let sub = FixedSubstrate::new().with("a", "X").with("b", "X").with("c", "Y");
//! let ev = eval_seek(&prog.lets().next().unwrap().seek, &sub)?;
//! assert!(matches!(ev.outcome, Outcome::Declined { .. }));
//! # Ok::<(), mekaneck_lang::Error>(())
//! ```

#![forbid(unsafe_code)]
#![warn(missing_debug_implementations)]

pub mod ast;
pub mod eval;
pub mod lex;
pub mod parse;
pub mod types;

pub use ast::{
    CatalystDecl, Decl, Expr, LetDecl, Program, ReportDecl, SeekExpr, SubstrateDecl,
};
pub use eval::{eval_seek, eval_seek_ordered, Evaluation, FixedSubstrate, Step, Substrate};
pub use lex::{lex, Span, Token, TokenKind, KEYWORDS};
pub use mekaneck_algebra::{Cell, Outcome};
pub use parse::parse;
pub use types::{
    diagnose, typecheck, Diagnostic, FloorValues, Severity, Ty, TypeEnv, MIN_COHERENCE,
};

/// Errors from any stage. Each carries the span it applies to where one
/// exists, so the editor can mark source rather than print prose.
#[derive(Debug, Clone, PartialEq, thiserror::Error)]
pub enum Error {
    // ---- lexical ----
    #[error("unexpected character {ch:?}")]
    UnexpectedChar { ch: char, span: Span },

    #[error("unterminated string literal")]
    UnterminatedString(Span),

    #[error("malformed number {text:?}")]
    MalformedNumber { text: String, span: Span },

    // ---- syntactic ----
    #[error("expected {what}, found {found:?}")]
    Expected {
        what: String,
        found: String,
        span: Span,
    },

    #[error(
        "seek requires an 'excluding' clause: a target is not determined by a positive \
         description alone, so a seek without one has no unique denotation"
    )]
    MissingExclusion { span: Span },

    // ---- type ----
    #[error("no substrate declared: a seek has no floor obligation to satisfy")]
    NoSubstrate,

    #[error("{name:?} is declared more than once")]
    Duplicate { name: String, span: Span },

    #[error(
        "substrate {substrate:?} declares floor {value}, which is not strictly positive: \
         a program may not assert an attainable zero residual"
    )]
    NonPositiveFloor {
        substrate: String,
        value: f64,
        span: Span,
    },

    #[error("unknown catalyst {name:?}")]
    UnknownCatalyst { name: String, span: Span },

    #[error("catalyst {name:?} is declared independent of itself")]
    SelfIndependence { name: String, span: Span },

    #[error("catalyst {name:?} appears more than once in the via clause")]
    DuplicateCatalyst { name: String, span: Span },

    #[error(
        "via names {got} catalyst(s); a support structure robust to the loss of any one \
         member needs at least {need} (a 1-cycle is vacuous, a 2-cycle collapses)"
    )]
    InsufficientCoherence {
        got: usize,
        need: usize,
        span: Span,
    },

    #[error("catalysts {a:?} and {b:?} are not mutually declared independent")]
    NotMutuallyIndependent { a: String, b: String, span: Span },

    #[error("{name:?} is not bound")]
    Unbound { name: String, span: Span },

    // ---- evaluation ----
    #[error("seek has no catalysts to invoke")]
    NoCatalysts { span: Span },

    #[error("catalyst {name:?} is not bound in this substrate")]
    UnboundCatalystAtRuntime { name: String, span: Span },
}

impl Error {
    /// The source span this error applies to, when it has one.
    pub fn span(&self) -> Option<Span> {
        use Error::*;
        match self {
            UnexpectedChar { span, .. }
            | UnterminatedString(span)
            | MalformedNumber { span, .. }
            | Expected { span, .. }
            | MissingExclusion { span }
            | Duplicate { span, .. }
            | NonPositiveFloor { span, .. }
            | UnknownCatalyst { span, .. }
            | SelfIndependence { span, .. }
            | DuplicateCatalyst { span, .. }
            | InsufficientCoherence { span, .. }
            | NotMutuallyIndependent { span, .. }
            | Unbound { span, .. }
            | NoCatalysts { span }
            | UnboundCatalystAtRuntime { span, .. } => Some(*span),
            NoSubstrate => None,
        }
    }
}
