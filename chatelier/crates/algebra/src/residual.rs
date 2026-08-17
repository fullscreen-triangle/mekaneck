//! The floor: derived rather than posited.
//!
//! Paper 1, §3. Under identification against a non-completable whole no
//! finite stage completes an identification, so every item carries a strictly
//! positive residual (Thm 3.1) and the floor `β = inf ρ(v) > 0` (Cor 3.2).
//!
//! The practical content is [`FloorEstimator`]. Two estimators are offered and
//! they differ in kind, not in accuracy:
//!
//! - [`FloorEstimator::SampleMinimum`] is bounded below by the sample and so
//!   returns a strictly positive value on *every* input. It therefore cannot
//!   produce evidence against `β > 0`, and it is biased upward, which by
//!   Prop 4.8 inflates the powers of exactly the events acting nearest the
//!   floor.
//! - [`FloorEstimator::Asymptotic`] extrapolates the stage minima to infinite
//!   sample and *can* return a non-positive value. It is the only one of the
//!   two capable of falsifying a positivity claim.
//!
//! A substrate is required to declare which it uses (Paper 3, obligation S4);
//! the type does that declaring.

use serde::{Deserialize, Serialize};

use crate::Error;

/// How a substrate discharges the floor obligation.
///
/// This is a declaration, not a hint: it is recorded alongside every estimate
/// so that a reader can tell whether a reported positive floor was capable of
/// coming out otherwise.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum FloorEstimator {
    /// Least observed uncertainty. Always positive on a positive sample;
    /// cannot falsify. Retained because it is what most pipelines do, and
    /// naming it is better than hiding it.
    SampleMinimum,
    /// Least-squares intercept of stage minima against `1/n`. Can return a
    /// value at or below zero when the generating process has no floor.
    Asymptotic,
}

impl FloorEstimator {
    /// Whether this estimator is capable of returning a non-positive value,
    /// i.e. of contradicting a positivity claim.
    pub fn is_falsifiable(self) -> bool {
        matches!(self, FloorEstimator::Asymptotic)
    }
}

/// A floor estimate together with the estimator that produced it.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct FloorEstimate {
    pub value: f64,
    pub estimator: FloorEstimator,
    /// Number of expansion stages the estimate was computed from.
    pub stages: usize,
    /// Total observations across all stages.
    pub observations: usize,
}

impl FloorEstimate {
    /// A floor is *usable* by the algebra only if strictly positive: the
    /// denominator `S - β` of Def 4.1 must not vanish.
    pub fn is_positive(&self) -> bool {
        self.value > 0.0
    }

    /// True when the estimate contradicts `β > 0`. Only reachable with a
    /// falsifiable estimator; a `SampleMinimum` estimate can never report this.
    pub fn falsifies_positivity(&self) -> bool {
        self.estimator.is_falsifiable() && self.value <= 0.0
    }

    /// Whether the estimate is indistinguishable from zero at the given
    /// tolerance, and so does not support a positive floor even when it
    /// happens to carry a positive sign.
    ///
    /// A strict `value <= 0` test is too brittle to report on alone: an
    /// asymptotic fit on a floorless process lands on either side of zero
    /// depending on sampling noise, and a value of `2e-6` is not evidence for
    /// `β > 0` merely because it is positive. Callers reporting a floor
    /// should consult this alongside [`Self::falsifies_positivity`].
    pub fn is_indistinguishable_from_zero(&self, tolerance: f64) -> bool {
        self.value.abs() <= tolerance
    }

    /// Whether this estimate supports a usable positive floor: falsifiable
    /// estimator, positive value, and not within `tolerance` of zero.
    pub fn supports_positive_floor(&self, tolerance: f64) -> bool {
        self.estimator.is_falsifiable()
            && self.value > 0.0
            && !self.is_indistinguishable_from_zero(tolerance)
    }
}

/// Default tolerance below which a floor estimate is treated as
/// indistinguishable from zero.
pub const ZERO_TOLERANCE: f64 = 1e-3;

/// An expanding family of observations: successive stages, each a sample of
/// the uncertainty `S` over a progressively larger portion of the medium.
///
/// The floor is estimated *across* stages, not within one, because the claim
/// under test is about what happens as the medium is more fully brought to
/// bear (Rem 3.5).
#[derive(Debug, Clone, Default)]
pub struct ExpandingFamily {
    stages: Vec<Vec<f64>>,
}

impl ExpandingFamily {
    pub fn new() -> Self {
        Self::default()
    }

    /// Add one stage. Empty stages are rejected: a stage with no observation
    /// contributes no minimum and would silently distort the fit.
    pub fn push_stage(&mut self, observations: Vec<f64>) -> Result<(), Error> {
        if observations.is_empty() {
            return Err(Error::EmptyStage);
        }
        if observations.iter().any(|x| !x.is_finite()) {
            return Err(Error::NonFinite("stage observation"));
        }
        self.stages.push(observations);
        Ok(())
    }

    pub fn len(&self) -> usize {
        self.stages.len()
    }

    pub fn is_empty(&self) -> bool {
        self.stages.is_empty()
    }

    pub fn total_observations(&self) -> usize {
        self.stages.iter().map(Vec::len).sum()
    }

    /// Per-stage `(n, min S)` pairs — the data the asymptotic fit consumes.
    fn stage_minima(&self) -> Vec<(f64, f64)> {
        self.stages
            .iter()
            .map(|s| {
                let m = s.iter().copied().fold(f64::INFINITY, f64::min);
                (s.len() as f64, m)
            })
            .collect()
    }

    /// Estimate the floor under the declared estimator.
    ///
    /// The asymptotic estimator needs at least two stages of differing size to
    /// determine a slope; with fewer it would be reporting the sample minimum
    /// under another name, so it errors instead of silently degrading.
    pub fn estimate(&self, estimator: FloorEstimator) -> Result<FloorEstimate, Error> {
        if self.stages.is_empty() {
            return Err(Error::EmptyFamily);
        }
        let value = match estimator {
            FloorEstimator::SampleMinimum => self
                .stages
                .iter()
                .flat_map(|s| s.iter().copied())
                .fold(f64::INFINITY, f64::min),
            FloorEstimator::Asymptotic => {
                let pts = self.stage_minima();
                if pts.len() < 2 {
                    return Err(Error::InsufficientStages {
                        got: pts.len(),
                        need: 2,
                    });
                }
                let xs: Vec<f64> = pts.iter().map(|(n, _)| 1.0 / n).collect();
                if xs.windows(2).all(|w| (w[0] - w[1]).abs() < f64::EPSILON) {
                    // All stages the same size: the design has no leverage on
                    // the intercept. Report that rather than a fitted value.
                    return Err(Error::DegenerateDesign);
                }
                let ys: Vec<f64> = pts.iter().map(|(_, m)| *m).collect();
                least_squares_intercept(&xs, &ys)?
            }
        };
        Ok(FloorEstimate {
            value,
            estimator,
            stages: self.stages.len(),
            observations: self.total_observations(),
        })
    }
}

/// Ordinary least squares, returning only the intercept: the fitted value at
/// `1/n = 0`, i.e. the extrapolated infinite-sample minimum.
fn least_squares_intercept(xs: &[f64], ys: &[f64]) -> Result<f64, Error> {
    let n = xs.len() as f64;
    let sx: f64 = xs.iter().sum();
    let sy: f64 = ys.iter().sum();
    let sxx: f64 = xs.iter().map(|x| x * x).sum();
    let sxy: f64 = xs.iter().zip(ys).map(|(x, y)| x * y).sum();
    let denom = n * sxx - sx * sx;
    if denom.abs() < 1e-300 {
        return Err(Error::DegenerateDesign);
    }
    let slope = (n * sxy - sx * sy) / denom;
    Ok((sy - slope * sx) / n)
}

#[cfg(test)]
mod tests {
    use super::*;

    /// Deterministic stand-in for a cubic-density draw: values concentrate
    /// near the floor, which is the regime in which the two estimators are
    /// hardest to distinguish.
    fn stage(n: usize, floor: f64, seed: u64) -> Vec<f64> {
        let mut s = seed;
        (0..n)
            .map(|_| {
                s = s.wrapping_mul(6364136223846793005).wrapping_add(1442695040888963407);
                let u = ((s >> 11) as f64) / ((1u64 << 53) as f64);
                floor + 40.0 * u.powi(3)
            })
            .collect()
    }

    fn family(floor: f64) -> ExpandingFamily {
        let mut f = ExpandingFamily::new();
        for (i, n) in [50usize, 120, 400, 1000, 2500, 4000].iter().enumerate() {
            f.push_stage(stage(*n, floor, 42 + i as u64)).unwrap();
        }
        f
    }

    #[test]
    fn sample_minimum_is_positive_on_a_floorless_process() {
        // The load-bearing property: this estimator cannot falsify.
        let e = family(0.0).estimate(FloorEstimator::SampleMinimum).unwrap();
        assert!(e.value > 0.0, "sample minimum returned {}", e.value);
        assert!(!e.falsifies_positivity());
        assert!(!e.estimator.is_falsifiable());
    }

    #[test]
    fn asymptotic_can_falsify_on_a_floorless_process() {
        let e = family(0.0).estimate(FloorEstimator::Asymptotic).unwrap();
        assert!(e.estimator.is_falsifiable());
        assert!(e.value < 0.5, "asymptotic returned {}", e.value);
    }

    #[test]
    fn asymptotic_recovers_a_true_floor() {
        let e = family(10.0).estimate(FloorEstimator::Asymptotic).unwrap();
        assert!((e.value - 10.0).abs() < 0.5, "recovered {}", e.value);
        assert!(e.is_positive());
    }

    #[test]
    fn near_zero_estimate_does_not_support_a_positive_floor() {
        // An asymptotic fit on a floorless process lands on either side of
        // zero; a positive sign at 1e-6 is not evidence for a floor.
        let e = family(0.0).estimate(FloorEstimator::Asymptotic).unwrap();
        assert!(e.is_indistinguishable_from_zero(ZERO_TOLERANCE));
        assert!(!e.supports_positive_floor(ZERO_TOLERANCE));

        let good = family(10.0).estimate(FloorEstimator::Asymptotic).unwrap();
        assert!(good.supports_positive_floor(ZERO_TOLERANCE));

        // and the sample minimum never supports it, however large
        let sm = family(10.0).estimate(FloorEstimator::SampleMinimum).unwrap();
        assert!(!sm.supports_positive_floor(ZERO_TOLERANCE));
    }

    #[test]
    fn sample_minimum_is_biased_upward() {
        // A sample minimum is an upper bound on the infimum (Prop 4.8).
        let e = family(10.0).estimate(FloorEstimator::SampleMinimum).unwrap();
        assert!(e.value >= 10.0);
    }

    #[test]
    fn asymptotic_needs_leverage() {
        let mut f = ExpandingFamily::new();
        f.push_stage(vec![1.0, 2.0]).unwrap();
        assert!(matches!(
            f.estimate(FloorEstimator::Asymptotic),
            Err(Error::InsufficientStages { .. })
        ));

        let mut g = ExpandingFamily::new();
        g.push_stage(vec![1.0, 2.0]).unwrap();
        g.push_stage(vec![3.0, 4.0]).unwrap();
        assert!(matches!(
            g.estimate(FloorEstimator::Asymptotic),
            Err(Error::DegenerateDesign)
        ));
    }

    #[test]
    fn rejects_empty_and_non_finite() {
        let mut f = ExpandingFamily::new();
        assert!(matches!(f.push_stage(vec![]), Err(Error::EmptyStage)));
        assert!(matches!(
            f.push_stage(vec![1.0, f64::NAN]),
            Err(Error::NonFinite(_))
        ));
    }
}
