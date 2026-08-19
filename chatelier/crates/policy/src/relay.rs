//! Relay drift (Paper 1, §4.x).
//!
//! An account passed along a chain acquires each relay's individuation as a
//! composed factor, so its fidelity is `prod(1 - k_i)` — the residual factor
//! of the composition law. Drift accumulates **without any relay altering the
//! account on purpose**.
//!
//! What this module deliberately does not provide: any predicate saying a
//! relayed account is false, corrupt, or wrong. No account resolves to a
//! point in any observer's graph, so there is no value to compare against.
//! Accumulated drift is computable; falsity is not, and a type asserting it
//! would import a claim the algebra does not make.

use mekaneck_algebra::{Error as AlgError, Power};
use serde::{Deserialize, Serialize};

/// A value carrying how far it has been relayed.
///
/// Depth alone bounds the accumulated drift when a lower bound on relay
/// powers is known, and does so without inspecting the content.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct Relayed<T> {
    pub value: T,
    /// Number of relays this value has passed through.
    pub depth: usize,
    /// Surviving fidelity: the product of residual factors so far.
    fidelity: f64,
}

impl<T> Relayed<T> {
    /// A value at the source: depth zero, fidelity one.
    pub fn origin(value: T) -> Self {
        Relayed {
            value,
            depth: 0,
            fidelity: 1.0,
        }
    }

    /// Pass through one relay applying the given power.
    pub fn relay(self, power: Power) -> Self {
        Relayed {
            value: self.value,
            depth: self.depth + 1,
            fidelity: self.fidelity * power.residual_factor(),
        }
    }

    /// Fraction of the original account surviving the chain.
    pub fn fidelity(&self) -> f64 {
        self.fidelity
    }

    /// Accumulated drift: `1 - fidelity`. This is the composition of the
    /// relay powers, by Cor 4.x.
    pub fn drift(&self) -> f64 {
        1.0 - self.fidelity
    }

    /// Map the payload, preserving provenance.
    pub fn map<U>(self, f: impl FnOnce(T) -> U) -> Relayed<U> {
        Relayed {
            value: f(self.value),
            depth: self.depth,
            fidelity: self.fidelity,
        }
    }
}

/// Worst-case fidelity after `depth` relays, given a lower bound `c` on relay
/// powers.
///
/// The only statement about a relayed account the algebra supports from depth
/// alone, without inspecting content.
pub fn fidelity_bound(depth: usize, min_power: f64) -> Result<f64, AlgError> {
    let p = Power::new(min_power)?;
    Ok(p.residual_factor().powi(depth as i32))
}

/// Relays a value may pass before its fidelity falls below `threshold`.
///
/// Returns `None` when relays are non-attenuating, in which case no depth
/// forces the bound.
pub fn relays_until(threshold: f64, min_power: f64) -> Option<usize> {
    if !(0.0..1.0).contains(&threshold) || min_power <= 0.0 || min_power >= 1.0 {
        return None;
    }
    let r = 1.0 - min_power;
    // (1-c)^n < threshold  =>  n > ln(threshold)/ln(1-c)
    Some((threshold.ln() / r.ln()).ceil() as usize)
}

#[cfg(test)]
mod tests {
    use super::*;

    fn p(k: f64) -> Power {
        Power::new(k).unwrap()
    }

    #[test]
    fn a_source_value_is_undrifted() {
        let v = Relayed::origin("account");
        assert_eq!(v.depth, 0);
        assert!((v.fidelity() - 1.0).abs() < 1e-12);
        assert!(v.drift().abs() < 1e-12);
    }

    #[test]
    fn fidelity_is_the_product_of_residual_factors() {
        let v = Relayed::origin(())
            .relay(p(0.2))
            .relay(p(0.3))
            .relay(p(0.5));
        assert_eq!(v.depth, 3);
        let expected = 0.8 * 0.7 * 0.5;
        assert!((v.fidelity() - expected).abs() < 1e-12);
        assert!((v.drift() - (1.0 - expected)).abs() < 1e-12);
    }

    #[test]
    fn drift_matches_the_composition_law() {
        // Cor: relay drift IS composition, not an analogy.
        let ks = [0.2, 0.35, 0.1, 0.4];
        let mut v = Relayed::origin(());
        for k in ks {
            v = v.relay(p(k));
        }
        let composed = mekaneck_algebra::compose(
            &ks.iter().map(|k| p(*k)).collect::<Vec<_>>(),
        )
        .unwrap();
        assert!((v.drift() - composed.kappa()).abs() < 1e-12);
    }

    #[test]
    fn a_faithful_relay_still_drifts_the_chain() {
        // No relay alters the account on purpose; drift is nonetheless large.
        let mut v = Relayed::origin(());
        for _ in 0..10 {
            v = v.relay(p(0.2));
        }
        assert!(v.fidelity() < 0.11, "fidelity {}", v.fidelity());
        assert!(v.drift() > 0.89);
    }

    #[test]
    fn a_negative_power_relay_can_restore_fidelity() {
        // A relay that increases the outstanding gap has residual > 1. The
        // algebra admits this and so must the provenance.
        let v = Relayed::origin(()).relay(p(0.5)).relay(p(-1.0));
        assert!((v.fidelity() - 1.0).abs() < 1e-12);
    }

    #[test]
    fn depth_alone_bounds_fidelity() {
        let b = fidelity_bound(10, 0.2).unwrap();
        assert!((b - 0.8_f64.powi(10)).abs() < 1e-12);
        // and it is a bound: an actual chain of stronger relays is worse
        let mut v = Relayed::origin(());
        for _ in 0..10 {
            v = v.relay(p(0.3));
        }
        assert!(v.fidelity() < b);
    }

    #[test]
    fn relays_until_threshold() {
        // 0.8^n < 0.5  =>  n >= 4
        assert_eq!(relays_until(0.5, 0.2), Some(4));
        assert!(0.8_f64.powi(4) < 0.5);
        assert!(0.8_f64.powi(3) > 0.5);

        // non-attenuating relays never force the bound
        assert_eq!(relays_until(0.5, 0.0), None);
    }

    #[test]
    fn mapping_preserves_provenance() {
        let v = Relayed::origin(2i32).relay(p(0.5)).map(|x| x * 10);
        assert_eq!(v.value, 20);
        assert_eq!(v.depth, 1);
        assert!((v.fidelity() - 0.5).abs() < 1e-12);
    }
}
