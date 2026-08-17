//! The trajectory: what was computed, as against what could be (Paper 2, §5).
//!
//! The trajectory is the realised read-to-emit relation of a run (Def 5.2). It
//! is *not* a function of the protocol (Thm 5.1) and *not* recoverable from
//! the terminal value store (Thm 5.4), which together place it outside the
//! closure of the two data a reader normally holds — what was asked, and what
//! came back.
//!
//! That is why it must be recorded explicitly if it is wanted at all
//! (Rem 6.3), and why a reproducibility claim attaches to the protocol
//! fingerprint rather than to this (Cor 5.2).

use serde::{Deserialize, Serialize};

use crate::node::Tau;

/// One link: a module read at `from`, and on the strength of it emitted at
/// `to`.
///
/// The kernel cannot infer these — it does not know why a module emitted what
/// it did — so a module that wants its reasoning auditable records them.
#[derive(Debug, Clone, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub struct Link {
    pub from: Tau,
    pub to: Tau,
    /// The record value at which the emit was committed, so links inherit the
    /// monotone order of Thm 6.1.
    pub at: usize,
}

/// The realised read-to-emit relation of one run.
#[derive(Debug, Clone, Default, PartialEq, Serialize, Deserialize)]
pub struct Trajectory {
    links: Vec<Link>,
}

impl Trajectory {
    pub fn new() -> Self {
        Self::default()
    }

    pub fn record(&mut self, from: impl Into<Tau>, to: impl Into<Tau>, at: usize) {
        self.links.push(Link {
            from: from.into(),
            to: to.into(),
            at,
        });
    }

    pub fn links(&self) -> &[Link] {
        &self.links
    }

    pub fn len(&self) -> usize {
        self.links.len()
    }

    pub fn is_empty(&self) -> bool {
        self.links.is_empty()
    }

    /// A canonical digest of the route, for comparing two runs.
    ///
    /// Distinct from the protocol fingerprint on purpose: two runs of one
    /// protocol may differ here and agree there (Thm 5.1), and two runs
    /// reaching the same terminal store may differ here while no function of
    /// that store separates them (Thm 5.4).
    pub fn digest(&self) -> String {
        use sha2::{Digest, Sha256};
        let mut h = Sha256::new();
        for l in &self.links {
            h.update(l.from.as_bytes());
            h.update(b">");
            h.update(l.to.as_bytes());
            h.update(b"@");
            h.update(l.at.to_le_bytes());
            h.update(b"\x1e");
        }
        format!("{:x}", h.finalize())
    }

    /// Nodes this run actually passed through, in first-visit order.
    pub fn visited(&self) -> Vec<&Tau> {
        let mut seen = std::collections::BTreeSet::new();
        let mut out = Vec::new();
        for l in &self.links {
            for t in [&l.from, &l.to] {
                if seen.insert(t.clone()) {
                    out.push(t);
                }
            }
        }
        out
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn traj(pairs: &[(&str, &str)]) -> Trajectory {
        let mut t = Trajectory::new();
        for (i, (a, b)) in pairs.iter().enumerate() {
            t.record(*a, *b, i + 1);
        }
        t
    }

    #[test]
    fn distinct_routes_have_distinct_digests() {
        let a = traj(&[("n1", "n2"), ("n2", "n4")]);
        let b = traj(&[("n1", "n3"), ("n3", "n4")]);
        assert_ne!(a.digest(), b.digest());
    }

    #[test]
    fn the_same_route_digests_identically() {
        assert_eq!(
            traj(&[("a", "b"), ("b", "c")]).digest(),
            traj(&[("a", "b"), ("b", "c")]).digest()
        );
    }

    #[test]
    fn visited_reports_first_visit_order() {
        let t = traj(&[("n1", "n2"), ("n2", "n1"), ("n1", "n5")]);
        let v: Vec<&str> = t.visited().iter().map(|s| s.as_str()).collect();
        assert_eq!(v, vec!["n1", "n2", "n5"]);
    }

    #[test]
    fn links_carry_the_monotone_record() {
        let t = traj(&[("a", "b"), ("b", "c"), ("c", "d")]);
        let ats: Vec<usize> = t.links().iter().map(|l| l.at).collect();
        assert_eq!(ats, vec![1, 2, 3]);
        assert!(ats.windows(2).all(|w| w[0] < w[1]));
    }
}
