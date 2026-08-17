//! Reference bindings (Paper 3, §8).
//!
//! Three substrates of quite different character — an oscillatory-coherence
//! record, a discrete transition record, and a latency record — each
//! discharging only the four obligations. They share one storage shape,
//! which is the point: the differences between them are in how a domain maps
//! onto `(receiver, labelled uncertainty, event, floor)` and nowhere else.

use std::collections::BTreeMap;

use mekaneck_algebra::{Cell, ExpandingFamily, FloorEstimator};
use serde::{Deserialize, Serialize};

use crate::traits::{Error, Observation, Substrate};

/// A substrate backed by tabular data, with an explicit floor declaration.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Tabular {
    pub name: String,
    /// Receiver → ordered observations.
    pub records: BTreeMap<String, Vec<Observation>>,
    /// Receiver → expansion stages for the floor estimate.
    pub floor_stages: BTreeMap<String, Vec<Vec<f64>>>,
    /// Which estimator discharges S4. Serialised, so a stored substrate
    /// carries its own evidential status.
    pub estimator: FloorEstimator,
    /// Catalyst → cell.
    pub catalysts: BTreeMap<String, Cell>,
}

impl Tabular {
    pub fn new(name: impl Into<String>, estimator: FloorEstimator) -> Self {
        Tabular {
            name: name.into(),
            records: BTreeMap::new(),
            floor_stages: BTreeMap::new(),
            estimator,
            catalysts: BTreeMap::new(),
        }
    }

    pub fn with_record(mut self, receiver: &str, obs: Vec<Observation>) -> Self {
        self.records.insert(receiver.to_string(), obs);
        self
    }

    pub fn with_floor_stages(mut self, receiver: &str, stages: Vec<Vec<f64>>) -> Self {
        self.floor_stages.insert(receiver.to_string(), stages);
        self
    }

    pub fn with_catalyst(mut self, name: &str, cell: &str) -> Self {
        self.catalysts.insert(name.to_string(), cell.to_string());
        self
    }

    /// Build a record from `(uncertainty, label)` pairs.
    pub fn record_from(pairs: &[(f64, &str)]) -> Vec<Observation> {
        pairs
            .iter()
            .map(|(u, l)| Observation {
                uncertainty: *u,
                label: (*l).to_string(),
            })
            .collect()
    }
}

impl Substrate for Tabular {
    fn receivers(&self) -> Vec<String> {
        self.records.keys().cloned().collect()
    }

    fn observations(&self, receiver: &str) -> Result<Vec<Observation>, Error> {
        let obs = self
            .records
            .get(receiver)
            .ok_or_else(|| Error::NoSuchReceiver(receiver.to_string()))?;
        if obs.len() < 2 {
            return Err(Error::TooFewObservations {
                receiver: receiver.to_string(),
                got: obs.len(),
                need: 2,
            });
        }
        Ok(obs.clone())
    }

    fn floor_estimator(&self) -> FloorEstimator {
        self.estimator
    }

    fn floor_family(&self, receiver: &str) -> Result<ExpandingFamily, Error> {
        let stages = self
            .floor_stages
            .get(receiver)
            .ok_or_else(|| Error::NoSuchReceiver(receiver.to_string()))?;
        let mut f = ExpandingFamily::new();
        for s in stages {
            f.push_stage(s.clone())?;
        }
        Ok(f)
    }

    fn invoke(&self, catalyst: &str) -> Option<Cell> {
        self.catalysts.get(catalyst).cloned()
    }

    fn name(&self) -> &str {
        &self.name
    }
}

/// **Oscillatory coherence.** Receivers are recordings; the observable is a
/// coherence index in `[0,1]` mapped to uncertainty by an order-reversing
/// affine map, so higher coherence is lower uncertainty; events are label
/// changes between adjacent segments.
pub fn oscillatory(coherence_by_segment: &[(f64, &str)], scale: f64) -> Vec<Observation> {
    coherence_by_segment
        .iter()
        .map(|(r, label)| Observation {
            uncertainty: scale * (1.0 - r),
            label: (*label).to_string(),
        })
        .collect()
}

/// **Discrete transitions.** Receivers are experimental conditions; states are
/// members of a small class set with an occupancy, from which uncertainty is
/// derived. Appropriate when the record is a transition matrix rather than a
/// time series.
pub fn discrete(occupancy_by_class: &[(f64, &str)], scale: f64) -> Vec<Observation> {
    occupancy_by_class
        .iter()
        .map(|(occ, label)| Observation {
            // higher occupancy => better individuated => lower uncertainty
            uncertainty: scale * (1.0 - occ.clamp(0.0, 1.0)),
            label: (*label).to_string(),
        })
        .collect()
}

/// **Latency.** Receivers are participants; states are trials labelled by
/// condition, with uncertainty an affine function of response latency. Yields
/// a zero-free-parameter prediction: the power of a compound condition should
/// equal the composition of its constituents'.
pub fn latency(trials: &[(f64, &str)], reference_ms: f64) -> Vec<Observation> {
    trials
        .iter()
        .map(|(ms, label)| Observation {
            uncertainty: ms / reference_ms * 50.0,
            label: (*label).to_string(),
        })
        .collect()
}

#[cfg(test)]
mod tests {
    use super::*;

    fn stages() -> Vec<Vec<f64>> {
        vec![
            vec![12.0, 40.0, 90.0, 60.0],
            vec![11.0, 30.0, 70.0, 95.0, 44.0],
            vec![10.4, 25.0, 61.0, 88.0, 39.0, 51.0],
        ]
    }

    #[test]
    fn one_engine_serves_three_domains() {
        // Prop 9.1: nothing below refers to any property beyond the four
        // obligations, so the same code path serves all three.
        let osc = Tabular::new("osc", FloorEstimator::Asymptotic)
            .with_record("rec1", oscillatory(&[(0.9, "hi"), (0.4, "lo"), (0.85, "hi")], 100.0))
            .with_floor_stages("rec1", stages());

        let dis = Tabular::new("dis", FloorEstimator::Asymptotic)
            .with_record("cond1", discrete(&[(0.7, "A"), (0.2, "B"), (0.6, "C")], 100.0))
            .with_floor_stages("cond1", stages());

        let lat = Tabular::new("lat", FloorEstimator::Asymptotic)
            .with_record("subj1", latency(&[(420.0, "V"), (380.0, "VA"), (500.0, "A")], 400.0))
            .with_floor_stages("subj1", stages());

        for (s, r) in [
            (&osc as &dyn Substrate, "rec1"),
            (&dis as &dyn Substrate, "cond1"),
            (&lat as &dyn Substrate, "subj1"),
        ] {
            let obs = s.observations(r).unwrap();
            assert_eq!(obs.len(), 3);
            assert_eq!(s.events(&obs).len(), 2);
            assert!(s.floor(r).unwrap().value.is_finite());
        }
    }

    #[test]
    fn oscillatory_reverses_coherence() {
        // higher coherence must give lower uncertainty
        let o = oscillatory(&[(0.9, "hi"), (0.1, "lo")], 100.0);
        assert!(o[0].uncertainty < o[1].uncertainty);
    }

    #[test]
    fn missing_receiver_is_named() {
        let t = Tabular::new("t", FloorEstimator::Asymptotic);
        assert!(matches!(
            t.observations("absent"),
            Err(Error::NoSuchReceiver(r)) if r == "absent"
        ));
    }

    #[test]
    fn a_single_observation_is_too_few() {
        let t = Tabular::new("t", FloorEstimator::Asymptotic)
            .with_record("r", Tabular::record_from(&[(50.0, "A")]));
        assert!(matches!(
            t.observations("r"),
            Err(Error::TooFewObservations { got: 1, need: 2, .. })
        ));
    }

    #[test]
    fn the_declared_estimator_is_carried_not_inferred() {
        let trivial = Tabular::new("t", FloorEstimator::SampleMinimum)
            .with_floor_stages("r", stages());
        let f = trivial.floor("r").unwrap();
        assert!(!f.estimator.is_falsifiable());
        // and it round-trips, so a stored substrate keeps its status
        let json = serde_json::to_string(&trivial).unwrap();
        let back: Tabular = serde_json::from_str(&json).unwrap();
        assert_eq!(back.floor_estimator(), FloorEstimator::SampleMinimum);
    }
}
