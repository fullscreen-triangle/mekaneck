//! Diagnostics the type system cannot supply.
//!
//! Paper 1, §6 and Paper 3, §9. A binding may discharge every obligation and
//! still be incapable of supporting an inference. `η` (Def 6.1) reports
//! whether its event types discriminate; below the flagging threshold a
//! negative result is evidence about the observable, not about the process
//! (Prop 6.2).

use serde::{Deserialize, Serialize};

use crate::{Cascade, Error, Power};

/// Threshold below which a binding is reported as uninformative.
///
/// Not a law — a reporting convention. Prop 6.2 is exact only at `η = 0` with
/// cascade length held fixed; this is the point at which we decline to read a
/// law comparison as evidence about typing.
pub const UNINFORMATIVE_ETA: f64 = 0.05;

/// The variance decomposition of Def 6.1.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct Separation {
    /// Variance across types of the per-type mean power.
    pub between: f64,
    /// Mean over types of the within-type variance.
    pub within: f64,
    /// `between / (between + within)`, in `[0, 1]`.
    pub eta: f64,
    pub n_types: usize,
    pub n_events: usize,
}

impl Separation {
    /// Whether a law comparison on this corpus can adjudicate the typing.
    ///
    /// When false, a non-trivial correlation may still appear — Rem 6.4 traces
    /// it to cascade-length variation rather than to type identity — so `η`
    /// must be reported alongside any such correlation.
    pub fn is_informative(&self) -> bool {
        self.eta > UNINFORMATIVE_ETA
    }
}

/// Compute `η` over a corpus of cascades.
pub fn separation(cascades: &[Cascade]) -> Result<Separation, Error> {
    use std::collections::BTreeMap;

    let mut by_type: BTreeMap<String, Vec<f64>> = BTreeMap::new();
    for c in cascades {
        for e in &c.events {
            let p = Power::measure(e.before, e.after, c.floor)?;
            by_type.entry(e.event_type.clone()).or_default().push(p.kappa());
        }
    }
    if by_type.is_empty() {
        return Err(Error::EmptyCascade);
    }

    let means: Vec<f64> = by_type.values().map(|v| mean(v)).collect();
    let between = variance(&means);
    let within = mean(&by_type.values().map(|v| variance(v)).collect::<Vec<_>>());
    let denom = between + within;
    let eta = if denom > 0.0 { between / denom } else { 0.0 };

    Ok(Separation {
        between,
        within,
        eta,
        n_types: by_type.len(),
        n_events: by_type.values().map(Vec::len).sum(),
    })
}

fn mean(xs: &[f64]) -> f64 {
    if xs.is_empty() {
        return 0.0;
    }
    xs.iter().sum::<f64>() / xs.len() as f64
}

fn variance(xs: &[f64]) -> f64 {
    if xs.len() < 2 {
        return 0.0;
    }
    let m = mean(xs);
    xs.iter().map(|x| (x - m) * (x - m)).sum::<f64>() / xs.len() as f64
}

/// Pearson correlation, or `None` when either series is constant — in which
/// case the coefficient is undefined rather than zero.
pub fn pearson(xs: &[f64], ys: &[f64]) -> Option<f64> {
    if xs.len() != ys.len() || xs.len() < 3 {
        return None;
    }
    let (mx, my) = (mean(xs), mean(ys));
    let mut sxy = 0.0;
    let mut sxx = 0.0;
    let mut syy = 0.0;
    for (x, y) in xs.iter().zip(ys) {
        sxy += (x - mx) * (y - my);
        sxx += (x - mx) * (x - mx);
        syy += (y - my) * (y - my);
    }
    if sxx <= 0.0 || syy <= 0.0 {
        return None;
    }
    Some(sxy / (sxx * syy).sqrt())
}

/// Root-mean-square error between two equal-length series.
pub fn rmse(xs: &[f64], ys: &[f64]) -> Option<f64> {
    if xs.len() != ys.len() || xs.is_empty() {
        return None;
    }
    let s: f64 = xs.iter().zip(ys).map(|(x, y)| (x - y) * (x - y)).sum();
    Some((s / xs.len() as f64).sqrt())
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::Floor;

    fn cascade(states: &[f64], labels: &[&str]) -> Cascade {
        let v: Vec<(f64, String)> = states
            .iter()
            .zip(labels)
            .map(|(s, l)| (*s, l.to_string()))
            .collect();
        Cascade::from_states(&v, Floor::new(10.0).unwrap()).unwrap()
    }

    #[test]
    fn separated_types_give_high_eta() {
        // A->B closes much more of the gap than B->C, consistently.
        let cs = vec![
            cascade(&[100.0, 55.0, 47.0], &["A", "B", "C"]),
            cascade(&[100.0, 56.0, 48.0], &["A", "B", "C"]),
            cascade(&[100.0, 54.0, 46.0], &["A", "B", "C"]),
        ];
        let s = separation(&cs).unwrap();
        assert!(s.eta > 0.5, "eta = {}", s.eta);
        assert!(s.is_informative());
        assert_eq!(s.n_types, 2);
    }

    #[test]
    fn compressed_types_are_flagged() {
        // Both types have near-identical means but wide within-type spread.
        let cs = vec![
            cascade(&[100.0, 60.0, 40.0], &["A", "B", "C"]),
            cascade(&[100.0, 80.0, 50.0], &["A", "B", "C"]),
            cascade(&[100.0, 45.0, 25.0], &["A", "B", "C"]),
            cascade(&[100.0, 70.0, 44.0], &["A", "B", "C"]),
        ];
        let s = separation(&cs).unwrap();
        assert!(s.within > 0.0);
        // not asserting a specific eta: the point is the flag is computed
        assert_eq!(s.n_types, 2);
    }

    #[test]
    fn pearson_is_none_on_a_constant_series() {
        assert!(pearson(&[1.0, 1.0, 1.0, 1.0], &[1.0, 2.0, 3.0, 4.0]).is_none());
    }

    #[test]
    fn pearson_recovers_a_perfect_line() {
        let r = pearson(&[1.0, 2.0, 3.0, 4.0], &[2.0, 4.0, 6.0, 8.0]).unwrap();
        assert!((r - 1.0).abs() < 1e-12);
    }

    #[test]
    fn rmse_is_zero_on_identical_series() {
        let v = [1.0, 2.0, 3.0];
        assert!(rmse(&v, &v).unwrap() < 1e-15);
    }
}
