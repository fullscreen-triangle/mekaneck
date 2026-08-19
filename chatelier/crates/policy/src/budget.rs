//! Selection under a bounded budget (Paper 2, §8).
//!
//! This lives **above** the kernel rather than inside it, and the placement is
//! the point. Selection needs a per-candidate gain; gain is an interpretive
//! quantity; and by the Inertia Theorem the kernel computes no such thing. A
//! module supplies gains and decides what to contribute — the kernel still
//! executes whatever it is given and judges none of it.

use serde::{Deserialize, Serialize};

use crate::Error;

/// A candidate execution, with the two quantities selection needs.
///
/// `gain` is supplied by the submitting module and is not checked against
/// anything: there is no notion here of a gain being *correct*.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct Candidate {
    pub id: String,
    /// Cost of committing. Bounded below by the floor (Def 8.1).
    pub cost: f64,
    /// Value of committing, in whatever units the module uses. May be
    /// negative: a module is entitled to describe a candidate as harmful.
    pub gain: f64,
}

impl Candidate {
    pub fn new(id: impl Into<String>, cost: f64, gain: f64) -> Result<Self, Error> {
        if !cost.is_finite() || !gain.is_finite() {
            return Err(Error::NonFinite);
        }
        if cost <= 0.0 {
            return Err(Error::NonPositiveCost(cost));
        }
        Ok(Candidate {
            id: id.into(),
            cost,
            gain,
        })
    }

    /// Gain per unit cost. The quantity selection orders by.
    pub fn density(&self) -> f64 {
        self.gain / self.cost
    }
}

/// A bounded budget.
#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct Budget {
    total: f64,
    /// Lower bound on any candidate's cost. Used to bound how many
    /// candidates can be committed regardless of their gains (Cor 8.4).
    floor: f64,
}

impl Budget {
    pub fn new(total: f64, floor: f64) -> Result<Self, Error> {
        if !total.is_finite() || !floor.is_finite() {
            return Err(Error::NonFinite);
        }
        if total <= 0.0 {
            return Err(Error::NonPositiveBudget(total));
        }
        if floor <= 0.0 {
            return Err(Error::NonPositiveFloor(floor));
        }
        Ok(Budget { total, floor })
    }

    pub fn total(self) -> f64 {
        self.total
    }

    /// Most candidates committable per interval, whatever their gains.
    ///
    /// This is the structural half of Cor 8.4: declining is forced by
    /// boundedness, not by any judgement about the declined candidates.
    pub fn max_commitments(self) -> usize {
        (self.total / self.floor).floor() as usize
    }
}

/// The result of applying the selection rule.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct Selection {
    /// Committed, in the order taken.
    pub committed: Vec<String>,
    /// Not committed. Distinguished from a failure: these were declined
    /// because the budget could not pay for them.
    pub declined: Vec<String>,
    pub spent: f64,
    pub total_gain: f64,
    /// The binding price: density of the highest-density candidate excluded.
    /// `None` when everything fit.
    pub shadow_price: Option<f64>,
}

impl Selection {
    /// Whether anything was declined. Under a bounded budget this is
    /// ordinary, and a caller should not treat it as an error.
    pub fn declined_any(&self) -> bool {
        !self.declined.is_empty()
    }
}

/// Select by threshold on gain density (Thm 8.2).
///
/// Optimal for the continuous relaxation and within one candidate of the
/// integer optimum; exactly optimal when the repertoire is divisible
/// (see [`is_divisible`]).
///
/// Candidates with non-positive density are never committed: spending budget
/// on them cannot increase total gain, and committing a negative-gain
/// candidate would be a choice the rule has no reason to make.
pub fn select(candidates: &[Candidate], budget: Budget) -> Selection {
    let mut order: Vec<&Candidate> = candidates.iter().collect();
    // Descending density. Ties broken by id so the result is deterministic —
    // two runs of the same protocol must select the same set.
    order.sort_by(|a, b| {
        b.density()
            .partial_cmp(&a.density())
            .unwrap_or(std::cmp::Ordering::Equal)
            .then_with(|| a.id.cmp(&b.id))
    });

    let mut committed = Vec::new();
    let mut declined = Vec::new();
    let mut spent = 0.0;
    let mut total_gain = 0.0;
    let mut shadow_price: Option<f64> = None;

    for c in order {
        let affordable = spent + c.cost <= budget.total + 1e-12;
        if affordable && c.density() > 0.0 {
            committed.push(c.id.clone());
            spent += c.cost;
            total_gain += c.gain;
        } else {
            // The first candidate the budget excludes sets the price
            // (Rem 8.5): not the last one admitted, which is not monotone.
            if shadow_price.is_none() && !affordable {
                shadow_price = Some(c.density());
            }
            declined.push(c.id.clone());
        }
    }

    Selection {
        committed,
        declined,
        spent,
        total_gain,
        shadow_price,
    }
}

/// Whether a repertoire is *divisible*: every candidate is an independently
/// selectable unit of the same cost.
///
/// This is the hypothesis clause (ii) of Thm 8.2 needs, and it is stronger
/// than "costs are multiples of the floor". Bundling floor-sized units into
/// an indivisible candidate restores a 0/1 knapsack, where the threshold rule
/// is only within one candidate of the optimum — see the witness in
/// `tests/conformance.rs`.
pub fn is_divisible(candidates: &[Candidate]) -> bool {
    let mut it = candidates.iter();
    let Some(first) = it.next() else {
        return true;
    };
    it.all(|c| (c.cost - first.cost).abs() < 1e-12)
}

#[cfg(test)]
mod tests {
    use super::*;

    fn c(id: &str, cost: f64, gain: f64) -> Candidate {
        Candidate::new(id, cost, gain).unwrap()
    }

    #[test]
    fn commits_in_density_order_until_the_budget_is_spent() {
        let cands = vec![c("lo", 1.0, 0.2), c("hi", 1.0, 0.9), c("mid", 1.0, 0.5)];
        let s = select(&cands, Budget::new(2.0, 0.5).unwrap());
        assert_eq!(s.committed, vec!["hi", "mid"]);
        assert_eq!(s.declined, vec!["lo"]);
        assert!((s.total_gain - 1.4).abs() < 1e-12);
    }

    #[test]
    fn declining_is_forced_by_the_budget() {
        // Cor 8.4: at most floor(A / beta) commitments, whatever the gains.
        let b = Budget::new(2.0, 0.5).unwrap();
        assert_eq!(b.max_commitments(), 4);

        let cands: Vec<_> = (0..10).map(|i| c(&format!("c{i}"), 0.5, 1.0)).collect();
        let s = select(&cands, b);
        assert_eq!(s.committed.len(), 4);
        assert!(s.declined_any());
    }

    #[test]
    fn the_price_is_the_first_excluded_not_the_last_admitted() {
        // Rem 8.5. Densities: a=1.0, b=0.9, c=0.8.
        let cands = vec![c("a", 1.0, 1.0), c("b", 1.0, 0.9), c("c", 1.0, 0.8)];
        let s = select(&cands, Budget::new(2.0, 0.5).unwrap());
        assert_eq!(s.committed, vec!["a", "b"]);
        // the excluded candidate's density, not the admitted one's
        assert!((s.shadow_price.unwrap() - 0.8).abs() < 1e-12);
    }

    #[test]
    fn no_price_when_everything_fits() {
        let cands = vec![c("a", 1.0, 1.0)];
        let s = select(&cands, Budget::new(10.0, 0.5).unwrap());
        assert!(s.shadow_price.is_none());
        assert!(!s.declined_any());
    }

    #[test]
    fn a_non_positive_gain_is_never_committed() {
        // Spending budget on it cannot raise total gain.
        let cands = vec![c("harmful", 1.0, -0.5), c("inert", 1.0, 0.0)];
        let s = select(&cands, Budget::new(10.0, 0.5).unwrap());
        assert!(s.committed.is_empty());
        assert_eq!(s.declined.len(), 2);
    }

    #[test]
    fn selection_is_deterministic_under_ties() {
        // Two runs of one protocol must select the same set.
        let cands = vec![c("b", 1.0, 0.5), c("a", 1.0, 0.5), c("c", 1.0, 0.5)];
        let b = Budget::new(2.0, 0.5).unwrap();
        let first = select(&cands, b);
        for _ in 0..20 {
            assert_eq!(select(&cands, b).committed, first.committed);
        }
        assert_eq!(first.committed, vec!["a", "b"]);
    }

    #[test]
    fn divisibility_is_stricter_than_multiples_of_the_floor() {
        // costs 0.25 and 0.5 are both multiples of a 0.25 floor, but the
        // repertoire is not divisible.
        assert!(is_divisible(&[c("a", 0.25, 0.1), c("b", 0.25, 0.2)]));
        assert!(!is_divisible(&[c("a", 0.25, 0.1), c("b", 0.5, 0.4)]));
    }

    #[test]
    fn rejects_degenerate_inputs() {
        assert!(matches!(Candidate::new("x", 0.0, 1.0), Err(Error::NonPositiveCost(_))));
        assert!(matches!(Candidate::new("x", f64::NAN, 1.0), Err(Error::NonFinite)));
        assert!(matches!(Budget::new(0.0, 0.5), Err(Error::NonPositiveBudget(_))));
        assert!(matches!(Budget::new(1.0, 0.0), Err(Error::NonPositiveFloor(_))));
    }
}
