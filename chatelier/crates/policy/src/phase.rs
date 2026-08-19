//! Phase exclusion (Paper 2, §9).
//!
//! A module does not construct and commit in the same instant. The
//! consequence is a throughput ceiling **independent of the budget**: an
//! interval spent forming new subtasks is not available for executing them,
//! and no amount of resource relaxes that.
//!
//! This is a second, separate reason a sweep quiesces. A kernel observing low
//! throughput cannot tell the two apart from the record alone, which is why
//! the phase is tracked explicitly here rather than inferred.

use serde::{Deserialize, Serialize};

/// What a module is doing in one instant.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum Phase {
    /// Forming new subtask identities and chunks to contribute.
    Constructing,
    /// Executing chunks already contributed.
    Committing,
}

/// A module's alternation between the two phases.
///
/// The type makes the exclusion structural: there is no state in which both
/// are active, because `Phase` has no such variant.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct PhaseLog {
    phases: Vec<Phase>,
}

impl Default for PhaseLog {
    fn default() -> Self {
        Self::new()
    }
}

impl PhaseLog {
    pub fn new() -> Self {
        PhaseLog { phases: Vec::new() }
    }

    pub fn record(&mut self, phase: Phase) {
        self.phases.push(phase);
    }

    pub fn len(&self) -> usize {
        self.phases.len()
    }

    pub fn is_empty(&self) -> bool {
        self.phases.is_empty()
    }

    pub fn constructing(&self) -> usize {
        self.phases.iter().filter(|p| **p == Phase::Constructing).count()
    }

    pub fn committing(&self) -> usize {
        self.phases.iter().filter(|p| **p == Phase::Committing).count()
    }

    /// Fraction of instants spent constructing.
    pub fn construction_fraction(&self) -> f64 {
        if self.phases.is_empty() {
            return 0.0;
        }
        self.constructing() as f64 / self.phases.len() as f64
    }

    /// The ceiling of Prop 9.2: the committed record grows at most at rate
    /// `1 - phi` per instant, whatever the budget.
    pub fn commitment_ceiling(&self) -> f64 {
        1.0 - self.construction_fraction()
    }

    /// Commitments the ceiling permits over `instants`.
    pub fn permitted_commitments(&self, instants: usize) -> usize {
        (self.commitment_ceiling() * instants as f64).floor() as usize
    }

    /// Whether a module ever constructs.
    ///
    /// A module that never constructs never acquires new nodes to commit to
    /// (Prop 9.2, final clause) — it can only exhaust what it already has.
    pub fn ever_constructs(&self) -> bool {
        self.constructing() > 0
    }
}

/// Why a sweep produced fewer commitments than its ready set held.
///
/// The two causes are independent (Rem 9.3) and a report conflating them is
/// wrong in a way that matters: one is relieved by more resource, the other
/// is not.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum Quiescence {
    /// Everything ready was committed.
    Exhausted,
    /// The budget could not pay for the remaining candidates. More resource
    /// would admit more.
    BudgetBound,
    /// Instants were spent constructing. More resource would not help.
    PhaseBound,
    /// Both ceilings were active.
    Both,
}

/// Classify why a sweep stopped short.
pub fn classify(declined: usize, log: &PhaseLog) -> Quiescence {
    let budget_bound = declined > 0;
    let phase_bound = log.constructing() > 0;
    match (budget_bound, phase_bound) {
        (false, false) => Quiescence::Exhausted,
        (true, false) => Quiescence::BudgetBound,
        (false, true) => Quiescence::PhaseBound,
        (true, true) => Quiescence::Both,
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn log(pattern: &[Phase]) -> PhaseLog {
        let mut l = PhaseLog::new();
        for p in pattern {
            l.record(*p);
        }
        l
    }

    #[test]
    fn the_ceiling_tracks_the_construction_fraction() {
        use Phase::*;
        let l = log(&[Constructing, Committing, Committing, Committing]);
        assert!((l.construction_fraction() - 0.25).abs() < 1e-12);
        assert!((l.commitment_ceiling() - 0.75).abs() < 1e-12);
        assert_eq!(l.permitted_commitments(100), 75);
    }

    #[test]
    fn a_module_that_never_constructs_acquires_nothing() {
        use Phase::*;
        let l = log(&[Committing, Committing]);
        assert!(!l.ever_constructs());
        // ceiling is 1.0: every instant available, but nothing new arrives
        assert!((l.commitment_ceiling() - 1.0).abs() < 1e-12);
    }

    #[test]
    fn a_module_that_only_constructs_commits_nothing() {
        use Phase::*;
        let l = log(&[Constructing, Constructing, Constructing]);
        assert!((l.commitment_ceiling() - 0.0).abs() < 1e-12);
        assert_eq!(l.permitted_commitments(1000), 0);
    }

    #[test]
    fn the_two_ceilings_are_distinguished() {
        use Phase::*;
        let none = log(&[Committing, Committing]);
        let some = log(&[Constructing, Committing]);

        assert_eq!(classify(0, &none), Quiescence::Exhausted);
        assert_eq!(classify(3, &none), Quiescence::BudgetBound);
        assert_eq!(classify(0, &some), Quiescence::PhaseBound);
        assert_eq!(classify(3, &some), Quiescence::Both);
    }

    #[test]
    fn an_empty_log_has_no_construction() {
        let l = PhaseLog::new();
        assert_eq!(l.construction_fraction(), 0.0);
        assert!(!l.ever_constructs());
    }
}
