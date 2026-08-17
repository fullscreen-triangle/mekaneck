//! The four obligations (Paper 3, Def 3.1).
//!
//! A substrate binds an experimental domain to the language by discharging
//! exactly four obligations and nothing else. The language depends on no other
//! property, which is what [`Prop 9.1`] means by substrate neutrality: a
//! program is well typed and reduces identically over any binding that
//! satisfies these.
//!
//! S1–S3 are bookkeeping — what the units are, what is measured, what counts
//! as a step. **S4 is the obligation with empirical content.** A binding that
//! discharges it by returning the least observed uncertainty has discharged it
//! trivially: that value is positive whenever the sample is, so it cannot come
//! out otherwise and confirms nothing. [`Substrate::floor_estimator`] therefore
//! requires a binding to *declare* which estimator it uses, so a reader can
//! see whether a reported positive floor was capable of failing.

use mekaneck_algebra::{Cell, Error as AlgError, ExpandingFamily, FloorEstimate, FloorEstimator};
use serde::{Deserialize, Serialize};

/// One observation in a receiver's record: an uncertainty with a label.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct Observation {
    /// The uncertainty `S` of this state — the separation cost of the target
    /// in the observer's current graph.
    pub uncertainty: f64,
    /// The state label, from a finite set. Event types are formed from ordered
    /// pairs of these.
    pub label: String,
}

/// A discriminating event: an ordered pair of observations, with its type.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct Discriminating {
    pub from: usize,
    pub to: usize,
    pub event_type: String,
}

/// The four obligations.
pub trait Substrate {
    /// **S1.** The bounded systems to which a floor attaches.
    fn receivers(&self) -> Vec<String>;

    /// **S2.** The observable: an ordered sequence of labelled states for one
    /// receiver.
    fn observations(&self, receiver: &str) -> Result<Vec<Observation>, Error>;

    /// **S3.** Which ordered pairs of states constitute discriminating events,
    /// and the type of each.
    ///
    /// The default types an event by the ordered pair of its labels and
    /// treats every adjacent pair with differing labels as discriminating,
    /// which is the usual reading; a binding whose events are not adjacent
    /// transitions overrides it.
    fn events(&self, obs: &[Observation]) -> Vec<Discriminating> {
        obs.windows(2)
            .enumerate()
            .filter(|(_, w)| w[0].label != w[1].label)
            .map(|(i, w)| Discriminating {
                from: i,
                to: i + 1,
                event_type: format!("{}->{}", w[0].label, w[1].label),
            })
            .collect()
    }

    /// **S4a.** Which estimator discharges the floor obligation.
    ///
    /// This is a declaration a reader can check, not an implementation
    /// detail. A binding returning [`FloorEstimator::SampleMinimum`] is saying
    /// that its floor claim cannot be contradicted by data.
    fn floor_estimator(&self) -> FloorEstimator;

    /// **S4b.** The expanding family from which the floor is estimated.
    ///
    /// Estimation is *across* stages, as the medium is progressively brought
    /// to bear — a single sample cannot exhibit the asymptote the claim is
    /// about (Rem 3.5 of Paper 1).
    fn floor_family(&self, receiver: &str) -> Result<ExpandingFamily, Error>;

    /// The floor for one receiver, under the declared estimator.
    fn floor(&self, receiver: &str) -> Result<FloorEstimate, Error> {
        Ok(self.floor_family(receiver)?.estimate(self.floor_estimator())?)
    }

    /// The cell a catalyst reaches, or `None` if unbound here.
    ///
    /// Cells, not points: the return type is an equivalence class because a
    /// point-valued answer would assert a zero residual (Rem 3.4).
    fn invoke(&self, catalyst: &str) -> Option<Cell>;

    /// A short name for display.
    fn name(&self) -> &str;
}

#[derive(Debug, Clone, PartialEq, thiserror::Error)]
pub enum Error {
    #[error("no receiver named {0:?}")]
    NoSuchReceiver(String),

    #[error("receiver {receiver:?} has {got} observations, need at least {need}")]
    TooFewObservations {
        receiver: String,
        got: usize,
        need: usize,
    },

    #[error("substrate data is malformed: {0}")]
    Malformed(String),

    #[error(transparent)]
    Algebra(#[from] AlgError),
}

#[cfg(test)]
mod tests {
    use super::*;

    struct Stub;

    impl Substrate for Stub {
        fn receivers(&self) -> Vec<String> {
            vec!["r1".into()]
        }
        fn observations(&self, _: &str) -> Result<Vec<Observation>, Error> {
            Ok(vec![
                Observation { uncertainty: 100.0, label: "W".into() },
                Observation { uncertainty: 60.0, label: "N1".into() },
                Observation { uncertainty: 55.0, label: "N1".into() },
                Observation { uncertainty: 30.0, label: "N2".into() },
            ])
        }
        fn floor_estimator(&self) -> FloorEstimator {
            FloorEstimator::Asymptotic
        }
        fn floor_family(&self, _: &str) -> Result<ExpandingFamily, Error> {
            let mut f = ExpandingFamily::new();
            f.push_stage(vec![12.0, 40.0, 90.0])?;
            f.push_stage(vec![11.0, 30.0, 70.0, 95.0])?;
            Ok(f)
        }
        fn invoke(&self, c: &str) -> Option<Cell> {
            match c {
                "a" | "b" => Some("cellX".into()),
                "c" => Some("cellY".into()),
                _ => None,
            }
        }
        fn name(&self) -> &str {
            "stub"
        }
    }

    #[test]
    fn default_events_skip_repeated_labels() {
        let s = Stub;
        let obs = s.observations("r1").unwrap();
        let ev = s.events(&obs);
        // W->N1 and N1->N2; the N1->N1 pair is not discriminating
        assert_eq!(ev.len(), 2);
        assert_eq!(ev[0].event_type, "W->N1");
        assert_eq!(ev[1].event_type, "N1->N2");
    }

    #[test]
    fn floor_uses_the_declared_estimator() {
        let s = Stub;
        let f = s.floor("r1").unwrap();
        assert_eq!(f.estimator, FloorEstimator::Asymptotic);
        assert!(f.estimator.is_falsifiable());
    }

    #[test]
    fn unbound_catalyst_yields_none() {
        assert!(Stub.invoke("nope").is_none());
    }
}
