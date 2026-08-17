//! Node execution and the committed record (Paper 2, §3 and §6).
//!
//! `Run(n)` evaluates every chunk in a node's bag and emits each result. It
//! does nothing else. There is no exit code, no status, and no return value
//! carrying a verdict — the [`Kernel`] type exposes none, which is the
//! Inertia Theorem (Thm 3.1) made structural: an exit code would have to be a
//! function of a stored expectation, the state space holds no expectation, and
//! the kernel's operations never inspect value content.
//!
//! Because nothing branches on emitted content, a raising chunk does not
//! truncate the run (Cor 3.2) and does not overwrite any other value
//! (Cor 3.3).

use serde::{Deserialize, Serialize};

use crate::graph::Graph;
use crate::node::Tau;

/// Provenance ordering without a clock (Def 6.1, Cor 6.2).
///
/// Monotone by construction: there is no decrement, because no kernel
/// operation removes a value. Two states with equal value stores and unequal
/// records are distinct, so a recurring configuration is not a return
/// (Thm 6.1).
#[derive(Debug, Clone, Copy, Default, PartialEq, Eq, PartialOrd, Ord, Serialize, Deserialize)]
pub struct Record(usize);

impl Record {
    pub fn get(self) -> usize {
        self.0
    }

    fn commit(&mut self) -> Record {
        self.0 += 1;
        *self
    }
}

/// One committed evaluation, for the trace.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct Commit {
    pub tau: Tau,
    pub chunk: String,
    pub origin: String,
    /// Whether the chunk raised. Reported, never acted on.
    pub errored: bool,
    pub record: usize,
}

/// The runtime.
///
/// Note what is absent: no `status()`, no `exit_code()`, no `failed()`. There
/// is nothing here that could mean "wrong", and that is the point.
#[derive(Debug, Default)]
pub struct Kernel {
    pub graph: Graph,
    record: Record,
    commits: Vec<Commit>,
}

impl Kernel {
    pub fn new() -> Self {
        Self::default()
    }

    pub fn record(&self) -> Record {
        self.record
    }

    pub fn commits(&self) -> &[Commit] {
        &self.commits
    }

    /// `Run(n)`: evaluate every pending chunk on this node and emit each
    /// result.
    ///
    /// Returns the number of chunks evaluated — a count of work done, not a
    /// verdict on it. The loop is not conditioned on any emitted value, so an
    /// early failure does not prevent a later chunk from running.
    pub fn run_node(&mut self, tau: &str) -> usize {
        let Some(node) = self.graph.node_mut(tau) else {
            return 0;
        };

        // Take the pending ids first: evaluation emits, which mutates the node.
        let pending: Vec<_> = node.pending().map(|c| c.id.clone()).collect();
        let mut n = 0;

        for id in pending {
            let Some(node) = self.graph.node_mut(tau) else {
                break;
            };
            let Some(chunk) = node.chunks.iter().find(|c| c.id == id) else {
                continue;
            };
            let origin = chunk.origin.clone();
            // The kernel does not look at what comes back. It emits it.
            let value = chunk.eval();
            let errored = value.is_error();

            node.emit(value);
            node.mark_executed(id.clone());

            let rec = self.record.commit();
            self.commits.push(Commit {
                tau: tau.to_string(),
                chunk: id.0[..16.min(id.0.len())].to_string(),
                origin,
                errored,
                record: rec.get(),
            });
            n += 1;
        }
        n
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::graph::Contribution;
    use crate::node::{Chunk, ChunkId};
    use serde_json::json;

    fn ok_chunk(name: &str) -> Chunk {
        let n = name.to_string();
        Chunk::new(ChunkId::of(name), "test", move || Ok(json!(n)))
    }

    fn bad_chunk(name: &str) -> Chunk {
        Chunk::new(ChunkId::of(name), "test", || Err("deliberate".into()))
    }

    #[test]
    fn every_chunk_runs_under_anomaly() {
        // Cor 3.2: two raising chunks do not prevent the other three.
        let mut k = Kernel::new();
        k.graph.merge(
            Contribution::new()
                .with("t", ok_chunk("c1"))
                .with("t", bad_chunk("c2"))
                .with("t", ok_chunk("c3"))
                .with("t", bad_chunk("c4"))
                .with("t", ok_chunk("c5")),
        );
        let n = k.run_node("t");

        assert_eq!(n, 5);
        let vals = k.graph.read("t");
        assert_eq!(vals.len(), 5);
        assert_eq!(vals.iter().filter(|v| v.is_error()).count(), 2);
        assert_eq!(vals.iter().filter(|v| !v.is_error()).count(), 3);
        assert_eq!(k.record().get(), 5);
    }

    #[test]
    fn a_failing_chunk_commits_like_any_other() {
        let mut k = Kernel::new();
        k.graph.merge(Contribution::new().with("t", bad_chunk("only")));
        k.run_node("t");
        assert_eq!(k.record().get(), 1);
        assert!(k.commits()[0].errored);
    }

    #[test]
    fn record_is_strictly_monotone_and_never_returns() {
        let mut k = Kernel::new();
        k.graph.merge(
            Contribution::new()
                .with("a", ok_chunk("x"))
                .with("b", ok_chunk("x2")),
        );
        let mut seen = vec![k.record().get()];
        k.run_node("a");
        seen.push(k.record().get());
        k.run_node("b");
        seen.push(k.record().get());

        assert_eq!(seen, vec![0, 1, 2]);
        // Thm 6.1: equal value configurations at different records are
        // distinct states.
        assert_eq!(k.graph.read("a").len(), k.graph.read("b").len());
        assert_ne!(seen[1], seen[2]);
    }

    #[test]
    fn an_unchanged_bag_is_not_re_executed() {
        // Thm 7.1(i)
        let mut k = Kernel::new();
        k.graph.merge(Contribution::new().with("t", ok_chunk("c")));
        assert_eq!(k.run_node("t"), 1);
        assert_eq!(k.run_node("t"), 0);
        assert_eq!(k.record().get(), 1);
        assert_eq!(k.graph.read("t").len(), 1);
    }

    #[test]
    fn a_new_chunk_makes_a_node_ready_again() {
        let mut k = Kernel::new();
        k.graph.merge(Contribution::new().with("t", ok_chunk("c1")));
        k.run_node("t");
        assert!(k.graph.ready().is_empty());

        k.graph.merge(Contribution::new().with("t", ok_chunk("late")));
        assert_eq!(k.graph.ready(), vec!["t".to_string()]);
        assert_eq!(k.run_node("t"), 1);
    }

    #[test]
    fn running_an_absent_node_is_a_no_op() {
        let mut k = Kernel::new();
        assert_eq!(k.run_node("nothing"), 0);
        assert_eq!(k.record().get(), 0);
    }
}
