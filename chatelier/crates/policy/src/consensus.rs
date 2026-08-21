//! Classifying a node's value bag.
//!
//! When several chunks emit onto one node, a consumer wanting a single answer
//! must decide what agreement means. That decision is adjudication, so it
//! lives here rather than in the kernel: the kernel stores the bag and a
//! module chooses a criterion, visibly.
//!
//! The two outcomes are the ones an inquiry already has. A bag whose values
//! agree is a convergent closure; a bag whose values disagree is a contested
//! closure, and the honest report is the plurality rather than a selection
//! from it.

use std::collections::BTreeMap;

use mekaneck_algebra::Outcome;
use mekaneck_kernel::Value;

/// How a caller decides whether two values agree.
///
/// Explicit because there is no default that is right for every payload, and
/// a hidden default would be a judgement made on the caller's behalf.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Agreement {
    /// Byte-identical serialisations.
    Exact,
    /// Equal after the given number of decimal places, for numeric payloads.
    /// Non-numeric payloads fall back to [`Agreement::Exact`].
    Rounded(u32),
}

impl Agreement {
    /// The key under which a value counts as "the same answer".
    fn key(self, v: &Value) -> String {
        match self {
            Agreement::Exact => v.as_json().to_string(),
            Agreement::Rounded(dp) => match v.as_json().as_f64() {
                Some(x) => {
                    let f = 10f64.powi(dp as i32);
                    format!("{}", (x * f).round() / f)
                }
                None => v.as_json().to_string(),
            },
        }
    }
}

/// A classified bag.
#[derive(Debug, Clone, PartialEq)]
pub struct Consensus {
    pub outcome: Outcome,
    /// Distinct cells and how many values reached each.
    pub tally: BTreeMap<String, usize>,
    /// Values whose producing chunk raised. Counted, never silently dropped:
    /// a node consisting entirely of errors is contested, not empty.
    pub errors: usize,
    pub total: usize,
}

impl Consensus {
    pub fn is_resolved(&self) -> bool {
        self.outcome.is_resolved()
    }

    /// Share of non-error values holding the modal cell.
    ///
    /// Reported for display. It is deliberately *not* used to resolve a
    /// contested bag: a majority is not agreement, and treating it as such
    /// would silently discard the minority the plurality exists to report.
    pub fn modal_share(&self) -> f64 {
        let non_error = self.total.saturating_sub(self.errors);
        if non_error == 0 {
            return 0.0;
        }
        let modal = self.tally.values().copied().max().unwrap_or(0);
        modal as f64 / non_error as f64
    }
}

/// Classify a node's values.
///
/// Error values are counted separately and excluded from the tally: a chunk
/// that raised did not reach a cell. A bag of only errors is contested with
/// no cells, which is distinguishable from an empty node.
pub fn classify(values: &[Value], agreement: Agreement) -> Consensus {
    let mut tally: BTreeMap<String, usize> = BTreeMap::new();
    let mut errors = 0;

    for v in values {
        if v.is_error() {
            errors += 1;
            continue;
        }
        *tally.entry(agreement.key(v)).or_insert(0) += 1;
    }

    let outcome = if tally.len() == 1 {
        Outcome::Resolved {
            cell: tally.keys().next().cloned().expect("non-empty"),
        }
    } else {
        Outcome::Declined {
            cells: tally.keys().cloned().collect(),
        }
    };

    Consensus {
        outcome,
        tally,
        errors,
        total: values.len(),
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    fn ok(v: serde_json::Value) -> Value {
        Value::ok(v)
    }

    #[test]
    fn a_unanimous_bag_resolves() {
        let c = classify(&[ok(json!("x")), ok(json!("x")), ok(json!("x"))], Agreement::Exact);
        assert!(c.is_resolved());
        assert_eq!(c.tally["\"x\""], 3);
        assert!((c.modal_share() - 1.0).abs() < 1e-12);
    }

    #[test]
    fn a_split_bag_declines_with_every_cell() {
        let c = classify(
            &[ok(json!("a")), ok(json!("a")), ok(json!("b"))],
            Agreement::Exact,
        );
        match &c.outcome {
            Outcome::Declined { cells } => assert_eq!(cells.len(), 2),
            other => panic!("expected a declination, got {other:?}"),
        }
        // a majority is reported but does not resolve
        assert!((c.modal_share() - 2.0 / 3.0).abs() < 1e-12);
        assert!(!c.is_resolved());
    }

    #[test]
    fn the_agreement_criterion_is_the_callers_choice() {
        let vals = [ok(json!(1.0001)), ok(json!(1.0002))];
        assert!(!classify(&vals, Agreement::Exact).is_resolved());
        assert!(classify(&vals, Agreement::Rounded(2)).is_resolved());
    }

    #[test]
    fn errors_are_counted_not_dropped() {
        let c = classify(
            &[ok(json!("x")), Value::error("boom", "m"), ok(json!("x"))],
            Agreement::Exact,
        );
        assert_eq!(c.errors, 1);
        assert_eq!(c.total, 3);
        // the two agreeing values still resolve
        assert!(c.is_resolved());
        assert!((c.modal_share() - 1.0).abs() < 1e-12);
    }

    #[test]
    fn a_bag_of_only_errors_is_contested_with_no_cells() {
        let c = classify(&[Value::error("a", "m"), Value::error("b", "m")], Agreement::Exact);
        assert!(!c.is_resolved());
        assert!(c.tally.is_empty());
        assert_eq!(c.errors, 2);
        assert_eq!(c.modal_share(), 0.0);
    }

    #[test]
    fn an_empty_node_is_contested_rather_than_resolved() {
        // Nothing was produced, so nothing is agreed.
        let c = classify(&[], Agreement::Exact);
        assert!(!c.is_resolved());
        assert_eq!(c.total, 0);
    }

    #[test]
    fn rounding_falls_back_to_exact_on_non_numeric_payloads() {
        let c = classify(&[ok(json!("a")), ok(json!("b"))], Agreement::Rounded(3));
        assert!(!c.is_resolved());
        assert_eq!(c.tally.len(), 2);
    }
}
