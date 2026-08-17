//! Closure: termination by exhaustion of reachable outcomes.
//!
//! Paper 1, §7. A cascade is closed when no remaining catalyst can carry the
//! observer into an equivalence class it has not already reached (Def 7.2).
//! This is strictly stronger than any fixed threshold on attained uncertainty
//! (Thm 7.3), terminates over a finite registry (Thm 7.4), and resolves into
//! exactly two outcomes (Thm 7.5) — the second of which is an explicit
//! declination rather than a selected representative.

use std::collections::BTreeSet;

use serde::{Deserialize, Serialize};

use crate::Error;

/// An equivalence class of terminal states under a substrate-supplied
/// indistinguishability relation (Def 3.3 of Paper 3). Cells, not points, are
/// what an inquiry returns.
pub type Cell = String;

/// A named means of advancing an inquiry. Opaque here: the algebra knows only
/// its name and the cell it reaches.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct Catalyst {
    pub name: String,
    pub reaches: Cell,
}

/// The two ways an inquiry ends (Thm 7.5). There is no third.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
#[serde(tag = "outcome", rename_all = "snake_case")]
pub enum Outcome {
    /// Every admissible catalyst terminates in one class.
    Resolved { cell: Cell },
    /// Two or more incompatible classes were reached. The honest report is the
    /// plurality together with the catalysts leading to each — not a choice
    /// among them, which the evidence does not license.
    Declined { cells: Vec<Cell> },
}

impl Outcome {
    pub fn is_resolved(&self) -> bool {
        matches!(self, Outcome::Resolved { .. })
    }
}

/// A completed run of the closure procedure.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct ClosureRun {
    pub outcome: Outcome,
    /// Committed record: catalysts actually invoked (Def 8.1). Monotone.
    pub record: usize,
    /// Order in which catalysts were invoked, with the cell each reached.
    pub trace: Vec<(String, Cell)>,
}

/// Run to closure over a finite registry.
///
/// Invokes catalysts only while one of them can add a new cell; stops as soon
/// as the reachable set is stable. Terminates in at most `registry.len()`
/// invocations (Thm 7.4), and the outcome does not depend on the order in
/// which catalysts are consumed, since the reached set is built by union.
pub fn run_to_closure(registry: &[Catalyst]) -> Result<ClosureRun, Error> {
    if registry.is_empty() {
        return Err(Error::EmptyRegistry);
    }
    let mut reached: BTreeSet<Cell> = BTreeSet::new();
    let mut trace = Vec::new();
    let mut remaining: Vec<&Catalyst> = registry.iter().collect();

    loop {
        // Closure test: does any uninvoked catalyst add a class?
        let next = remaining
            .iter()
            .position(|c| !reached.contains(&c.reaches));
        match next {
            Some(i) => {
                let c = remaining.remove(i);
                reached.insert(c.reaches.clone());
                trace.push((c.name.clone(), c.reaches.clone()));
            }
            None => break,
        }
    }

    let outcome = if reached.len() == 1 {
        Outcome::Resolved {
            cell: reached.iter().next().expect("non-empty").clone(),
        }
    } else {
        Outcome::Declined {
            cells: reached.into_iter().collect(),
        }
    };
    Ok(ClosureRun {
        record: trace.len(),
        trace,
        outcome,
    })
}

/// Terminate as soon as an invoked catalyst reaches a cell whose attained
/// uncertainty falls below `theta`.
///
/// Provided for comparison only. Thm 7.3 shows this halts on a single
/// internally consistent line of evidence without consulting the sources that
/// would have disagreed; the validation reports that on the tested substrate
/// family it errs on *exactly* the contested runs.
pub fn run_to_threshold(
    registry: &[Catalyst],
    uncertainty: &dyn Fn(&str) -> f64,
    theta: f64,
) -> Result<ClosureRun, Error> {
    if registry.is_empty() {
        return Err(Error::EmptyRegistry);
    }
    let mut reached: BTreeSet<Cell> = BTreeSet::new();
    let mut trace = Vec::new();
    for c in registry {
        reached.insert(c.reaches.clone());
        trace.push((c.name.clone(), c.reaches.clone()));
        if uncertainty(&c.reaches) < theta {
            return Ok(ClosureRun {
                record: trace.len(),
                trace,
                outcome: Outcome::Resolved {
                    cell: c.reaches.clone(),
                },
            });
        }
    }
    let outcome = if reached.len() == 1 {
        Outcome::Resolved {
            cell: reached.iter().next().expect("non-empty").clone(),
        }
    } else {
        Outcome::Declined {
            cells: reached.into_iter().collect(),
        }
    };
    Ok(ClosureRun {
        record: trace.len(),
        trace,
        outcome,
    })
}

#[cfg(test)]
mod tests {
    use super::*;

    fn cat(name: &str, cell: &str) -> Catalyst {
        Catalyst {
            name: name.into(),
            reaches: cell.into(),
        }
    }

    #[test]
    fn unanimous_registry_resolves() {
        let r = run_to_closure(&[cat("a", "X"), cat("b", "X"), cat("c", "X")]).unwrap();
        assert!(r.outcome.is_resolved());
        // stops as soon as the reachable set is stable: one invocation
        assert_eq!(r.record, 1);
    }

    #[test]
    fn split_registry_declines() {
        let r = run_to_closure(&[cat("a", "X"), cat("b", "X"), cat("c", "Y")]).unwrap();
        assert_eq!(
            r.outcome,
            Outcome::Declined {
                cells: vec!["X".into(), "Y".into()]
            }
        );
        assert_eq!(r.record, 2);
    }

    #[test]
    fn closure_is_strictly_stronger_than_a_threshold() {
        // Thm 7.3, instantiated: cellX is "confident", cellY is not.
        let reg = [cat("a", "X"), cat("b", "X"), cat("c", "Y")];
        let unc = |c: &str| if c == "X" { 5.0 } else { 40.0 };

        let thr = run_to_threshold(&reg, &unc, 10.0).unwrap();
        let clo = run_to_closure(&reg).unwrap();

        // the threshold rule stops on the first confident cell...
        assert!(thr.outcome.is_resolved());
        assert_eq!(thr.record, 1);
        // ...and never consults the catalyst that disagrees
        assert!(!clo.outcome.is_resolved());
        assert!(clo.record > thr.record);
    }

    #[test]
    fn outcome_is_order_independent() {
        // Reached set is built by union, so permuting the registry cannot
        // change the verdict (only the trace).
        let base = [cat("a", "X"), cat("b", "Y"), cat("c", "X")];
        let perms = [
            [0usize, 1, 2],
            [2, 1, 0],
            [1, 0, 2],
            [1, 2, 0],
            [2, 0, 1],
            [0, 2, 1],
        ];
        let mut outcomes = BTreeSet::new();
        for p in perms {
            let reg: Vec<Catalyst> = p.iter().map(|i| base[*i].clone()).collect();
            let r = run_to_closure(&reg).unwrap();
            outcomes.insert(format!("{:?}", r.outcome));
        }
        assert_eq!(outcomes.len(), 1, "outcome varied with order: {outcomes:?}");
    }

    #[test]
    fn terminates_within_the_registry_bound() {
        let reg: Vec<Catalyst> = (0..8).map(|i| cat(&format!("c{i}"), &format!("cell{i}"))).collect();
        let r = run_to_closure(&reg).unwrap();
        assert!(r.record <= reg.len());
        assert_eq!(r.record, 8); // every catalyst adds a new cell here
    }

    #[test]
    fn empty_registry_is_an_error() {
        assert!(matches!(run_to_closure(&[]), Err(Error::EmptyRegistry)));
    }
}
