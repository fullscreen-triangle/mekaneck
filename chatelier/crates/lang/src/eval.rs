//! Small-step operational semantics (Paper 3, §6).
//!
//! Three reduction rules over a configuration `⟨e, Σ, ρ⟩`:
//!
//! - **E-Invoke** consumes one available catalyst, adds its cell to the
//!   reached set, and increments the record.
//! - **E-Close-Res** fires when no remaining catalyst adds a cell and exactly
//!   one was reached.
//! - **E-Close-Dec** fires under the same premise with two or more.
//!
//! Determinism modulo substrate (Thm 6.4) holds because the reached set is
//! built by union and the closure rules branch only on its cardinality.

use serde::{Deserialize, Serialize};

use crate::ast::SeekExpr;
use crate::Error;

pub use mekaneck_algebra::{Cell, Outcome};

/// What a catalyst yields when invoked against a substrate.
///
/// The language never inspects a cell's contents; it compares cells for
/// equality and nothing else, which is what keeps it substrate-neutral.
pub trait Substrate {
    /// The cell this catalyst reaches, or `None` if the catalyst is not bound
    /// in this substrate.
    fn invoke(&self, catalyst: &str) -> Option<Cell>;
}

/// A substrate backed by a fixed map, for tests and for replaying a recorded
/// run.
#[derive(Debug, Clone, Default)]
pub struct FixedSubstrate {
    map: std::collections::BTreeMap<String, Cell>,
}

impl FixedSubstrate {
    pub fn new() -> Self {
        Self::default()
    }

    pub fn with(mut self, catalyst: &str, cell: &str) -> Self {
        self.map.insert(catalyst.to_string(), cell.to_string());
        self
    }
}

impl Substrate for FixedSubstrate {
    fn invoke(&self, catalyst: &str) -> Option<Cell> {
        self.map.get(catalyst).cloned()
    }
}

/// One reduction step, recorded for the trace.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct Step {
    pub catalyst: String,
    pub cell: Cell,
    /// The committed record after this step. Strictly increasing (Thm 6.3).
    pub record: usize,
}

/// A completed evaluation.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct Evaluation {
    pub outcome: Outcome,
    pub record: usize,
    pub trace: Vec<Step>,
    /// Cells reached, in sorted order.
    pub reached: Vec<Cell>,
}

/// Evaluate a `seek` to an [`Outcome`].
///
/// Terminates in at most `via.len()` invocations (Thm 6.5) and produces a
/// value of type `Outcome` in every case (Thm 6.1, 6.2).
pub fn eval_seek(seek: &SeekExpr, substrate: &dyn Substrate) -> Result<Evaluation, Error> {
    eval_seek_ordered(seek, substrate, &seek.via)
}

/// Evaluate under an explicit catalyst order.
///
/// Exposed so that determinism can be exercised directly: the outcome must not
/// depend on `order`, only the trace may.
pub fn eval_seek_ordered(
    seek: &SeekExpr,
    substrate: &dyn Substrate,
    order: &[String],
) -> Result<Evaluation, Error> {
    if seek.via.is_empty() {
        return Err(Error::NoCatalysts { span: seek.span });
    }
    let mut available: Vec<String> = order.to_vec();
    let mut reached: std::collections::BTreeSet<Cell> = Default::default();
    let mut trace: Vec<Step> = Vec::new();

    loop {
        // Closure premise: can any remaining catalyst add a cell?
        let mut pick = None;
        for (i, name) in available.iter().enumerate() {
            let cell = substrate
                .invoke(name)
                .ok_or_else(|| Error::UnboundCatalystAtRuntime {
                    name: name.clone(),
                    span: seek.span,
                })?;
            if !reached.contains(&cell) {
                pick = Some((i, cell));
                break;
            }
        }

        match pick {
            // E-Invoke
            Some((i, cell)) => {
                let name = available.remove(i);
                reached.insert(cell.clone());
                trace.push(Step {
                    catalyst: name,
                    cell,
                    record: trace.len() + 1,
                });
            }
            // E-Close-Res / E-Close-Dec
            None => break,
        }
    }

    let cells: Vec<Cell> = reached.into_iter().collect();
    let outcome = if cells.len() == 1 {
        Outcome::Resolved {
            cell: cells[0].clone(),
        }
    } else {
        Outcome::Declined {
            cells: cells.clone(),
        }
    };

    Ok(Evaluation {
        record: trace.len(),
        trace,
        reached: cells,
        outcome,
    })
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::parse::parse;

    fn seek_of(src: &str) -> SeekExpr {
        parse(src).unwrap().lets().next().unwrap().seek.clone()
    }

    const P: &str = r#"
substrate S { receivers : r(); observable : o(); events : e(); floor : f(); }
catalyst a : f() independent b, c;
catalyst b : g() independent a, c;
catalyst c : h() independent a, b;
let x = seek t() excluding rest() via (a, b, c) until closure;
report x;
"#;

    #[test]
    fn unanimous_substrate_resolves() {
        let s = FixedSubstrate::new()
            .with("a", "X")
            .with("b", "X")
            .with("c", "X");
        let e = eval_seek(&seek_of(P), &s).unwrap();
        assert_eq!(e.outcome, Outcome::Resolved { cell: "X".into() });
        assert_eq!(e.record, 1);
    }

    #[test]
    fn split_substrate_declines() {
        let s = FixedSubstrate::new()
            .with("a", "X")
            .with("b", "X")
            .with("c", "Y");
        let e = eval_seek(&seek_of(P), &s).unwrap();
        assert_eq!(
            e.outcome,
            Outcome::Declined {
                cells: vec!["X".into(), "Y".into()]
            }
        );
    }

    #[test]
    fn outcome_is_deterministic_across_orderings() {
        // Thm 6.4: only the trace may vary.
        let s = FixedSubstrate::new()
            .with("a", "X")
            .with("b", "Y")
            .with("c", "X");
        let seek = seek_of(P);
        let names = ["a".to_string(), "b".to_string(), "c".to_string()];
        let perms = [
            [0, 1, 2],
            [0, 2, 1],
            [1, 0, 2],
            [1, 2, 0],
            [2, 0, 1],
            [2, 1, 0],
        ];
        let mut outcomes = std::collections::BTreeSet::new();
        for p in perms {
            let order: Vec<String> = p.iter().map(|i| names[*i].clone()).collect();
            let e = eval_seek_ordered(&seek, &s, &order).unwrap();
            outcomes.insert(format!("{:?}", e.outcome));
            assert!(e.record <= 3, "termination bound");
        }
        assert_eq!(outcomes.len(), 1, "outcome varied: {outcomes:?}");
    }

    #[test]
    fn record_is_strictly_monotone() {
        let s = FixedSubstrate::new()
            .with("a", "X")
            .with("b", "Y")
            .with("c", "Z");
        let e = eval_seek(&seek_of(P), &s).unwrap();
        for (i, step) in e.trace.iter().enumerate() {
            assert_eq!(step.record, i + 1);
        }
        assert_eq!(e.record, 3);
    }

    #[test]
    fn invocations_equal_distinct_cells() {
        for (cells, expect) in [
            (["X", "X", "X"], 1usize),
            (["X", "X", "Y"], 2),
            (["X", "Y", "Z"], 3),
        ] {
            let s = FixedSubstrate::new()
                .with("a", cells[0])
                .with("b", cells[1])
                .with("c", cells[2]);
            let e = eval_seek(&seek_of(P), &s).unwrap();
            assert_eq!(e.record, expect, "for {cells:?}");
        }
    }

    #[test]
    fn unbound_catalyst_at_runtime_is_an_error() {
        let s = FixedSubstrate::new().with("a", "X"); // b, c missing
        assert!(matches!(
            eval_seek(&seek_of(P), &s),
            Err(Error::UnboundCatalystAtRuntime { .. })
        ));
    }
}
