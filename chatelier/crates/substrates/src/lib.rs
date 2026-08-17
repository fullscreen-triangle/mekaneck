//! # Substrate bindings
//!
//! The four obligations of *Mekaneck* §3 as a trait, plus reference bindings.
//!
//! A substrate is how an experimental domain enters the language, and the
//! language depends on nothing about it beyond these four. Three of them are
//! bookkeeping. The fourth — the floor — is a claim with empirical content,
//! and [`Substrate::floor_estimator`] requires a binding to declare which
//! estimator discharges it, because a binding that returns a sample minimum
//! has made a claim no data could refute.
//!
//! ```
//! use mekaneck_substrates::*;
//! use mekaneck_algebra::FloorEstimator;
//!
//! let sub = Tabular::new("osc", FloorEstimator::Asymptotic)
//!     .with_record("rec1", oscillatory(&[(0.9, "hi"), (0.4, "lo")], 100.0))
//!     .with_floor_stages("rec1", vec![
//!         vec![12.0, 40.0, 90.0],
//!         vec![11.0, 30.0, 70.0, 95.0],
//!     ])
//!     .with_catalyst("spectral", "cellA");
//!
//! let floor = sub.floor("rec1")?;
//! assert!(floor.estimator.is_falsifiable());
//! # Ok::<(), mekaneck_substrates::Error>(())
//! ```

#![forbid(unsafe_code)]
#![warn(missing_debug_implementations)]

pub mod tabular;
pub mod traits;

pub use tabular::{discrete, latency, oscillatory, Tabular};
pub use traits::{Discriminating, Error, Observation, Substrate};

/// Build the cascades of the residual algebra from a substrate's record.
///
/// This is the bridge between a binding and the algebra: it applies S2 and S3
/// to produce the labelled state sequence a [`mekaneck_algebra::Cascade`]
/// needs, using the floor the binding declares.
pub fn cascade_for(
    substrate: &dyn Substrate,
    receiver: &str,
) -> Result<mekaneck_algebra::Cascade, Error> {
    let obs = substrate.observations(receiver)?;
    let floor = substrate.floor(receiver)?;
    let f = mekaneck_algebra::Floor::new(floor.value)?;

    let states: Vec<(f64, String)> = obs
        .iter()
        .map(|o| (o.uncertainty, o.label.clone()))
        .collect();
    Ok(mekaneck_algebra::Cascade::from_states(&states, f)?)
}

#[cfg(test)]
mod tests {
    use super::*;
    use mekaneck_algebra::FloorEstimator;

    #[test]
    fn a_binding_feeds_the_algebra() {
        let sub = Tabular::new("osc", FloorEstimator::Asymptotic)
            .with_record(
                "r",
                Tabular::record_from(&[(100.0, "W"), (60.0, "N1"), (40.0, "N2")]),
            )
            .with_floor_stages(
                "r",
                vec![
                    vec![12.0, 40.0, 90.0],
                    vec![11.0, 30.0, 70.0, 95.0],
                    vec![10.5, 26.0, 62.0, 88.0],
                ],
            );

        let c = cascade_for(&sub, "r").unwrap();
        assert_eq!(c.len(), 2);
        assert_eq!(c.events[0].event_type, "W->N1");
        // powers are computable, so the floor came through positive
        assert_eq!(c.instance_powers().unwrap().len(), 2);
    }

    #[test]
    fn a_non_positive_floor_stops_the_bridge() {
        // A binding whose stages extrapolate to zero cannot feed the algebra:
        // Floor::new rejects it rather than the algebra dividing by zero.
        let sub = Tabular::new("flat", FloorEstimator::Asymptotic)
            .with_record("r", Tabular::record_from(&[(100.0, "A"), (50.0, "B")]))
            .with_floor_stages(
                "r",
                vec![vec![0.0, 10.0, 20.0], vec![0.0, 8.0, 16.0, 30.0]],
            );
        assert!(matches!(
            cascade_for(&sub, "r"),
            Err(Error::Algebra(mekaneck_algebra::Error::NonPositiveFloor(_)))
        ));
    }
}
