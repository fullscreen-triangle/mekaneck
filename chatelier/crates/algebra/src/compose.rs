//! Composition, and the estimation regime that decides whether a test of it
//! means anything.
//!
//! Paper 1, §4–§6. Residual factors multiply (Thm 4.1), which makes
//! composition a commutative monoid on `(−∞, 1]` (Cor 4.2).
//!
//! The important part of this module is not the law but [`Estimation`]. Under
//! [`Estimation::InstanceSpecific`] the multiplicative prediction and the
//! measured net power are *the same algebraic expression* (Thm 5.2), so the
//! comparison is an identity: it reports perfect agreement on data from any
//! process whatsoever and has no null (Cor 5.3). The API therefore refuses to
//! call that comparison a test — see [`CompositionTest::is_evidential`].

use std::collections::BTreeMap;

use serde::{Deserialize, Serialize};

use crate::{Error, Floor, Power, State};

/// The four composition rules compared in Prop 6.3. They are distinct
/// functions of the constituent powers and are ordered
/// `max ≤ multiplicative ≤ min(Σκ, 1)` off the degenerate cases.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, PartialOrd, Ord, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum Law {
    /// `1 − Π(1 − κᵢ)`. The law implied by the definitions (Thm 4.1).
    Multiplicative,
    /// `min(Σκᵢ, 1)`. The natural but incorrect alternative.
    Additive,
    /// `1 − (Π(1 − κᵢ))^{1/n}`.
    GeometricMean,
    /// `max κᵢ`.
    Maximum,
}

impl Law {
    pub const ALL: [Law; 4] = [
        Law::Multiplicative,
        Law::Additive,
        Law::GeometricMean,
        Law::Maximum,
    ];

    pub fn name(self) -> &'static str {
        match self {
            Law::Multiplicative => "multiplicative",
            Law::Additive => "additive",
            Law::GeometricMean => "geometric_mean",
            Law::Maximum => "maximum",
        }
    }

    /// Combine per-event powers under this law.
    pub fn combine(self, powers: &[Power]) -> Result<f64, Error> {
        if powers.is_empty() {
            return Err(Error::EmptyCascade);
        }
        let residual: f64 = powers.iter().map(|p| p.residual_factor()).product();
        Ok(match self {
            Law::Multiplicative => 1.0 - residual,
            Law::Additive => powers.iter().map(|p| p.kappa()).sum::<f64>().min(1.0),
            Law::GeometricMean => {
                if residual < 0.0 {
                    // a fractional power of a negative residual is not real;
                    // report rather than silently produce NaN
                    return Err(Error::NonRealGeometricMean(residual));
                }
                1.0 - residual.powf(1.0 / powers.len() as f64)
            }
            Law::Maximum => powers
                .iter()
                .map(|p| p.kappa())
                .fold(f64::NEG_INFINITY, f64::max),
        })
    }
}

/// Composition of powers under the multiplicative law (Thm 4.1).
pub fn compose(powers: &[Power]) -> Result<Power, Error> {
    Power::new(Law::Multiplicative.combine(powers)?)
}

/// How the per-event powers used in a prediction were estimated.
///
/// This is the distinction Thm 5.2 turns on, and it is carried in the type so
/// that a caller cannot report an instance-specific agreement as evidence
/// without the value saying otherwise.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum Estimation {
    /// Powers computed from the same state sequence that determines the
    /// cascade's own measured net power. Degenerate: the prediction *is* the
    /// measurement (Thm 5.2), and no data can make it fail (Cor 5.3).
    InstanceSpecific,
    /// Powers computed as means over all instances of each event type,
    /// independently of the cascade being predicted. Non-degenerate
    /// (Thm 5.5).
    TypeAveraged,
}

impl Estimation {
    /// Whether a comparison built on this regime can fail, and so whether its
    /// agreement carries evidential weight.
    pub fn has_null_hypothesis(self) -> bool {
        matches!(self, Estimation::TypeAveraged)
    }
}

/// One event in an observed cascade: the states it connects and its type.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct Event {
    pub before: State,
    pub after: State,
    /// Type label, e.g. the ordered pair of state labels (Def 5.4).
    pub event_type: String,
}

/// An observed cascade over a fixed floor.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct Cascade {
    pub events: Vec<Event>,
    pub floor: Floor,
}

impl Cascade {
    /// Build from a labelled state sequence: `n+1` states give `n` events,
    /// typed by the ordered pair of adjacent labels.
    pub fn from_states(states: &[(f64, String)], floor: Floor) -> Result<Self, Error> {
        if states.len() < 2 {
            return Err(Error::EmptyCascade);
        }
        let mut events = Vec::with_capacity(states.len() - 1);
        for w in states.windows(2) {
            events.push(Event {
                before: State::new(w[0].0)?,
                after: State::new(w[1].0)?,
                event_type: format!("{}->{}", w[0].1, w[1].1),
            });
        }
        Ok(Cascade { events, floor })
    }

    pub fn len(&self) -> usize {
        self.events.len()
    }

    pub fn is_empty(&self) -> bool {
        self.events.is_empty()
    }

    /// Powers of the constituent events, each computed from its own states.
    pub fn instance_powers(&self) -> Result<Vec<Power>, Error> {
        self.events
            .iter()
            .map(|e| Power::measure(e.before, e.after, self.floor))
            .collect()
    }

    /// The net power of the cascade regarded as a single event (Def 4.7):
    /// `(S₁ − S_{n+1}) / (S₁ − β)`.
    pub fn measured_net(&self) -> Result<Power, Error> {
        let first = self.events.first().ok_or(Error::EmptyCascade)?.before;
        let last = self.events.last().ok_or(Error::EmptyCascade)?.after;
        Power::measure(first, last, self.floor)
    }
}

/// Mean power per event type, pooled over a corpus (Def 5.4).
///
/// This is the population-level quantity whose composition is a genuine
/// prediction about an instance-level outcome.
#[derive(Debug, Clone, Default, Serialize, Deserialize)]
pub struct TypeAverages {
    means: BTreeMap<String, f64>,
    counts: BTreeMap<String, usize>,
}

impl TypeAverages {
    /// Pool the powers of every event in every cascade, by type.
    pub fn fit(cascades: &[Cascade]) -> Result<Self, Error> {
        let mut sums: BTreeMap<String, f64> = BTreeMap::new();
        let mut counts: BTreeMap<String, usize> = BTreeMap::new();
        for c in cascades {
            for e in &c.events {
                let p = Power::measure(e.before, e.after, c.floor)?;
                *sums.entry(e.event_type.clone()).or_insert(0.0) += p.kappa();
                *counts.entry(e.event_type.clone()).or_insert(0) += 1;
            }
        }
        if counts.is_empty() {
            return Err(Error::EmptyCascade);
        }
        let means = sums
            .iter()
            .map(|(k, s)| (k.clone(), s / counts[k] as f64))
            .collect();
        Ok(TypeAverages { means, counts })
    }

    pub fn get(&self, event_type: &str) -> Option<f64> {
        self.means.get(event_type).copied()
    }

    pub fn types(&self) -> impl Iterator<Item = (&String, &f64)> {
        self.means.iter()
    }

    pub fn count(&self, event_type: &str) -> usize {
        self.counts.get(event_type).copied().unwrap_or(0)
    }

    /// Powers for a cascade's events, taken from the type means rather than
    /// from the cascade itself. An unseen type is an error, not a zero.
    pub fn powers_for(&self, cascade: &Cascade) -> Result<Vec<Power>, Error> {
        cascade
            .events
            .iter()
            .map(|e| {
                self.get(&e.event_type)
                    .ok_or_else(|| Error::UnknownEventType(e.event_type.clone()))
                    .and_then(Power::new)
            })
            .collect()
    }
}

/// A prediction of a cascade's net power, carrying the regime it was formed
/// under so that its evidential status travels with it.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct CompositionTest {
    pub law: Law,
    pub estimation: Estimation,
    pub predicted: f64,
    pub measured: f64,
}

impl CompositionTest {
    pub fn discrepancy(&self) -> f64 {
        (self.predicted - self.measured).abs()
    }

    /// Whether agreement here is evidence about the process.
    ///
    /// False under [`Estimation::InstanceSpecific`] regardless of how close
    /// the agreement is: by Cor 5.3 that comparison cannot fail, and a test
    /// that cannot fail cannot discriminate.
    pub fn is_evidential(&self) -> bool {
        self.estimation.has_null_hypothesis()
    }
}

/// Predict a cascade's net power under a law and an estimation regime.
pub fn test_cascade(
    cascade: &Cascade,
    law: Law,
    estimation: Estimation,
    averages: Option<&TypeAverages>,
) -> Result<CompositionTest, Error> {
    let powers = match estimation {
        Estimation::InstanceSpecific => cascade.instance_powers()?,
        Estimation::TypeAveraged => {
            let a = averages.ok_or(Error::MissingTypeAverages)?;
            a.powers_for(cascade)?
        }
    };
    Ok(CompositionTest {
        law,
        estimation,
        predicted: law.combine(&powers)?,
        measured: cascade.measured_net()?.kappa(),
    })
}

#[cfg(test)]
mod tests {
    use super::*;

    fn floor() -> Floor {
        Floor::new(10.0).unwrap()
    }

    fn cascade(states: &[f64], labels: &[&str]) -> Cascade {
        let v: Vec<(f64, String)> = states
            .iter()
            .zip(labels)
            .map(|(s, l)| (*s, l.to_string()))
            .collect();
        Cascade::from_states(&v, floor()).unwrap()
    }

    #[test]
    fn residual_factors_multiply() {
        let a = Power::new(0.5).unwrap();
        let b = Power::new(0.5).unwrap();
        // 1 - (0.5 * 0.5)
        assert!((compose(&[a, b]).unwrap().kappa() - 0.75).abs() < 1e-12);
    }

    #[test]
    fn composition_is_a_commutative_monoid() {
        let a = Power::new(0.4).unwrap();
        let b = Power::new(-0.2).unwrap();
        let c = Power::new(0.7).unwrap();
        let id = Power::new(0.0).unwrap();

        let ab_c = compose(&[compose(&[a, b]).unwrap(), c]).unwrap();
        let a_bc = compose(&[a, compose(&[b, c]).unwrap()]).unwrap();
        assert!((ab_c.kappa() - a_bc.kappa()).abs() < 1e-12);

        assert!((compose(&[a, b]).unwrap().kappa() - compose(&[b, a]).unwrap().kappa()).abs() < 1e-12);
        assert!((compose(&[a, id]).unwrap().kappa() - a.kappa()).abs() < 1e-12);
        let absorbing = Power::new(1.0).unwrap();
        assert!((compose(&[a, absorbing]).unwrap().kappa() - 1.0).abs() < 1e-12);
    }

    #[test]
    fn telescoping_identity_holds_exactly() {
        // Thm 5.2: under instance-specific estimation the prediction and the
        // measurement are the same expression, so the deviation is 0 to
        // machine precision on every input.
        for states in [
            vec![100.0, 60.0, 35.0, 22.0],
            vec![80.0, 79.0, 41.0, 12.0, 11.0],
            vec![50.0, 70.0, 30.0], // includes a negative-power event
        ] {
            let labels: Vec<&str> = ["A", "B", "C", "D", "E"][..states.len()].to_vec();
            let c = cascade(&states, &labels);
            let t = test_cascade(&c, Law::Multiplicative, Estimation::InstanceSpecific, None)
                .unwrap();
            assert!(
                t.discrepancy() < 1e-12,
                "deviation {} for {:?}",
                t.discrepancy(),
                states
            );
            // and the API refuses to call it evidence
            assert!(!t.is_evidential());
        }
    }

    #[test]
    fn type_averaged_test_is_not_an_identity() {
        // Thm 5.5: with two instances of a type differing in power, the
        // type-averaged prediction must differ from the measurement.
        let c1 = cascade(&[100.0, 60.0], &["A", "B"]);
        let c2 = cascade(&[100.0, 80.0], &["A", "B"]);
        let avg = TypeAverages::fit(&[c1.clone(), c2.clone()]).unwrap();
        let t = test_cascade(&c1, Law::Multiplicative, Estimation::TypeAveraged, Some(&avg))
            .unwrap();
        assert!(t.discrepancy() > 1e-6, "discrepancy {}", t.discrepancy());
        assert!(t.is_evidential());
    }

    #[test]
    fn laws_are_ordered() {
        // Prop 6.3: max <= multiplicative <= min(sum, 1)
        let ps: Vec<Power> = [0.3, 0.4, 0.2]
            .iter()
            .map(|k| Power::new(*k).unwrap())
            .collect();
        let mx = Law::Maximum.combine(&ps).unwrap();
        let ml = Law::Multiplicative.combine(&ps).unwrap();
        let ad = Law::Additive.combine(&ps).unwrap();
        assert!(mx < ml, "{mx} !< {ml}");
        assert!(ml < ad, "{ml} !< {ad}");
        let gm = Law::GeometricMean.combine(&ps).unwrap();
        assert!(gm < ml, "geometric mean should sit below multiplicative");
    }

    #[test]
    fn unknown_event_type_is_an_error() {
        let known = cascade(&[100.0, 60.0], &["A", "B"]);
        let avg = TypeAverages::fit(&[known]).unwrap();
        let other = cascade(&[100.0, 60.0], &["X", "Y"]);
        assert!(matches!(
            avg.powers_for(&other),
            Err(Error::UnknownEventType(_))
        ));
    }

    #[test]
    fn type_averaged_requires_averages() {
        let c = cascade(&[100.0, 60.0], &["A", "B"]);
        assert!(matches!(
            test_cascade(&c, Law::Multiplicative, Estimation::TypeAveraged, None),
            Err(Error::MissingTypeAverages)
        ));
    }
}
