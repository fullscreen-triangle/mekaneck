//! Catalytic power and the residual factor.
//!
//! Paper 1, §4. `κ(γ) = (S_before − S_after) / (S_before − β)` is the fraction
//! of the outstanding gap that an event closes; `1 − κ` is the fraction that
//! survives. The residual factor is the natural coordinate — every result in
//! [`crate::compose`] is a statement that residual factors multiply.

use serde::{Deserialize, Serialize};

use crate::Error;

/// A floor known to be strictly positive.
///
/// Constructing this is the only way to compute a power, so the precondition
/// of Def 4.1 — that `S − β` is a positive quantity — is discharged once, at
/// the boundary, rather than checked at every use.
#[derive(Debug, Clone, Copy, PartialEq, PartialOrd, Serialize, Deserialize)]
pub struct Floor(f64);

impl Floor {
    /// Fails on a non-positive floor. Cor 3.3: no state has `S = 0`, and a
    /// zero floor would make every power undefined at convergence.
    pub fn new(value: f64) -> Result<Self, Error> {
        if !value.is_finite() {
            return Err(Error::NonFinite("floor"));
        }
        if value <= 0.0 {
            return Err(Error::NonPositiveFloor(value));
        }
        Ok(Floor(value))
    }

    pub fn value(self) -> f64 {
        self.0
    }
}

/// The uncertainty of an observer in one state: the separation cost of the
/// target in its current graph (Def 2.4).
#[derive(Debug, Clone, Copy, PartialEq, PartialOrd, Serialize, Deserialize)]
pub struct State(f64);

impl State {
    pub fn new(value: f64) -> Result<Self, Error> {
        if !value.is_finite() {
            return Err(Error::NonFinite("state"));
        }
        Ok(State(value))
    }

    pub fn value(self) -> f64 {
        self.0
    }

    /// The outstanding gap to the floor.
    pub fn gap(self, floor: Floor) -> f64 {
        self.0 - floor.0
    }
}

/// The power of a single event, and its residual factor.
///
/// `κ` is deliberately unconstrained in sign. An event that increases the
/// outstanding commitment — one that introduces confusable alternatives — has
/// `κ < 0`, and Rem 4.4 is explicit that excluding such events would amount to
/// assuming every event is informative.
#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct Power {
    kappa: f64,
}

impl Power {
    /// Wrap a known power. Values above 1 are rejected: by Prop 4.3(i) a power
    /// of 1 attains the floor exactly, and above it the post-state would lie
    /// below the floor, which Cor 3.3 forbids.
    pub fn new(kappa: f64) -> Result<Self, Error> {
        if !kappa.is_finite() {
            return Err(Error::NonFinite("power"));
        }
        if kappa > 1.0 {
            return Err(Error::PowerAboveUnity(kappa));
        }
        Ok(Power { kappa })
    }

    /// Compute the power of an event from the states it connects (Def 4.1).
    ///
    /// The pre-state must lie strictly above the floor: an event acting on a
    /// state already at the floor has no outstanding gap to close, and the
    /// ratio is undefined rather than zero.
    pub fn measure(before: State, after: State, floor: Floor) -> Result<Self, Error> {
        let gap = before.gap(floor);
        if gap <= 0.0 {
            return Err(Error::PreStateAtFloor {
                state: before.value(),
                floor: floor.value(),
            });
        }
        Power::new((before.value() - after.value()) / gap)
    }

    pub fn kappa(self) -> f64 {
        self.kappa
    }

    /// `1 − κ`: the fraction of the gap that survives the event.
    pub fn residual_factor(self) -> f64 {
        1.0 - self.kappa
    }

    /// Whether the event moves the observer toward the floor.
    pub fn is_constructive(self) -> bool {
        self.kappa > 0.0
    }

    /// Apply the event to a state, returning the post-state.
    pub fn apply(self, before: State, floor: Floor) -> State {
        State(floor.value() + before.gap(floor) * self.residual_factor())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn f(x: f64) -> Floor {
        Floor::new(x).unwrap()
    }
    fn s(x: f64) -> State {
        State::new(x).unwrap()
    }

    #[test]
    fn floor_must_be_positive() {
        assert!(matches!(Floor::new(0.0), Err(Error::NonPositiveFloor(_))));
        assert!(matches!(Floor::new(-1.0), Err(Error::NonPositiveFloor(_))));
        assert!(Floor::new(1e-9).is_ok());
    }

    #[test]
    fn power_is_the_fraction_of_the_gap_closed() {
        // gap 90, closes 45 => exactly one half
        let p = Power::measure(s(100.0), s(55.0), f(10.0)).unwrap();
        assert!((p.kappa() - 0.5).abs() < 1e-12);
        assert!((p.residual_factor() - 0.5).abs() < 1e-12);
    }

    #[test]
    fn unit_power_attains_the_floor() {
        let p = Power::measure(s(100.0), s(10.0), f(10.0)).unwrap();
        assert!((p.kappa() - 1.0).abs() < 1e-12);
    }

    #[test]
    fn negative_power_is_admissible() {
        // an event that increases uncertainty (Rem 4.4)
        let p = Power::measure(s(50.0), s(70.0), f(10.0)).unwrap();
        assert!(p.kappa() < 0.0);
        assert!(!p.is_constructive());
        assert!(p.residual_factor() > 1.0);
    }

    #[test]
    fn post_state_below_floor_is_rejected() {
        assert!(matches!(
            Power::measure(s(100.0), s(5.0), f(10.0)),
            Err(Error::PowerAboveUnity(_))
        ));
    }

    #[test]
    fn pre_state_at_floor_is_rejected() {
        assert!(matches!(
            Power::measure(s(10.0), s(10.0), f(10.0)),
            Err(Error::PreStateAtFloor { .. })
        ));
    }

    #[test]
    fn apply_inverts_measure() {
        let floor = f(10.0);
        let before = s(100.0);
        let p = Power::new(0.3).unwrap();
        let after = p.apply(before, floor);
        let back = Power::measure(before, after, floor).unwrap();
        assert!((back.kappa() - 0.3).abs() < 1e-12);
    }

    #[test]
    fn power_is_scale_invariant() {
        // Prop 4.6: affine reparametrisation fixing the floor leaves κ alone.
        let k1 = Power::measure(s(100.0), s(55.0), f(10.0)).unwrap().kappa();
        // S -> 3(S - 10) + 10
        let map = |x: f64| 3.0 * (x - 10.0) + 10.0;
        let k2 = Power::measure(s(map(100.0)), s(map(55.0)), f(10.0))
            .unwrap()
            .kappa();
        assert!((k1 - k2).abs() < 1e-12);
    }
}
