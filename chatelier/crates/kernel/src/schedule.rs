//! A fair readiness-based scheduler (Paper 2, §7).
//!
//! Dependencies are not declared — by Thm 5.1 the trajectory is not a function
//! of the protocol, so no schedule can be computed in advance. The scheduler
//! therefore proceeds by *readiness*: repeatedly pick a node with a pending
//! chunk, run it, stop when none remains.
//!
//! Thm 7.1 gives three guarantees: no node whose bag is unchanged is
//! re-executed, no pending chunk is starved, and the sweep terminates once
//! contributions cease.

use crate::exec::Kernel;
use crate::node::Tau;

/// How the scheduler picks among ready nodes.
///
/// Any rule that eventually selects every continuously ready node is fair in
/// the sense Thm 7.1(ii) needs. `RoundRobin` is the default because it is
/// deterministic and so makes a run reproducible at the protocol level;
/// `Rotating` is the least favourable fair rule and is used in tests to show
/// the guarantees are not artefacts of a helpful order.
#[derive(Debug, Clone, Copy, Default, PartialEq, Eq)]
pub enum Selection {
    #[default]
    RoundRobin,
    /// Advance a cursor through the ready set, wrapping. Fair, but visits in
    /// a different order each sweep.
    Rotating,
}

#[derive(Debug, Default)]
pub struct Scheduler {
    selection: Selection,
    cursor: usize,
    /// Guard against a contribution loop wedging the process. Not part of the
    /// theorem: Thm 7.1(iii) terminates once contributions cease, and this
    /// only bounds a caller that never stops contributing.
    max_steps: Option<usize>,
}

/// What a sweep did. A count of work, not a verdict.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Sweep {
    /// Node executions performed.
    pub executions: usize,
    /// Chunks evaluated across those executions.
    pub chunks: usize,
    /// Nodes visited, in order.
    pub visited: Vec<Tau>,
    /// True if `max_steps` cut the sweep short rather than readiness.
    pub truncated: bool,
}

impl Scheduler {
    pub fn new(selection: Selection) -> Self {
        Scheduler {
            selection,
            cursor: 0,
            max_steps: None,
        }
    }

    pub fn with_max_steps(mut self, n: usize) -> Self {
        self.max_steps = Some(n);
        self
    }

    /// Run until no node is ready.
    ///
    /// Each execution evaluates *all* of a node's pending chunks, so the
    /// number of executions equals the number of nodes when every node is
    /// contributed before the sweep starts.
    pub fn run(&mut self, kernel: &mut Kernel) -> Sweep {
        let mut sweep = Sweep {
            executions: 0,
            chunks: 0,
            visited: Vec::new(),
            truncated: false,
        };

        loop {
            let ready = kernel.graph.ready();
            if ready.is_empty() {
                break;
            }
            if let Some(max) = self.max_steps {
                if sweep.executions >= max {
                    sweep.truncated = true;
                    break;
                }
            }

            let idx = match self.selection {
                Selection::RoundRobin => 0,
                Selection::Rotating => {
                    self.cursor = self.cursor.wrapping_add(1);
                    self.cursor % ready.len()
                }
            };
            let tau = ready[idx].clone();

            sweep.chunks += kernel.run_node(&tau);
            sweep.executions += 1;
            sweep.visited.push(tau);
        }
        sweep
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::graph::Contribution;
    use crate::node::{Chunk, ChunkId};
    use serde_json::json;

    fn chunk(name: &str) -> Chunk {
        Chunk::new(ChunkId::of(name), "test", || Ok(json!(1)))
    }

    fn protocol(nodes: usize, per: usize) -> Contribution {
        let mut c = Contribution::new();
        for i in 0..nodes {
            for j in 0..per {
                c = c.with(format!("n{i}"), chunk(&format!("n{i}c{j}")));
            }
        }
        c
    }

    #[test]
    fn one_execution_per_node_and_all_chunks_evaluated() {
        // Thm 7.1(i) and (iii)
        for selection in [Selection::RoundRobin, Selection::Rotating] {
            let mut k = Kernel::new();
            k.graph.merge(protocol(12, 3));
            let sweep = Scheduler::new(selection).run(&mut k);

            assert_eq!(sweep.executions, 12, "{selection:?}");
            assert_eq!(sweep.chunks, 36, "{selection:?}");
            assert_eq!(k.record().get(), 36);
            assert!(k.graph.ready().is_empty());
            // no node visited twice
            let mut v = sweep.visited.clone();
            v.sort();
            v.dedup();
            assert_eq!(v.len(), 12);
        }
    }

    #[test]
    fn a_late_chunk_is_not_starved() {
        // Thm 7.1(ii): contributed after the sweep went quiescent.
        let mut k = Kernel::new();
        k.graph.merge(protocol(8, 1));
        let mut s = Scheduler::new(Selection::Rotating);
        s.run(&mut k);
        assert!(k.graph.ready().is_empty());

        k.graph
            .merge(Contribution::new().with("n3", chunk("late-arrival")));
        let second = s.run(&mut k);

        assert_eq!(second.executions, 1);
        assert_eq!(second.chunks, 1);
        assert_eq!(second.visited, vec!["n3".to_string()]);
    }

    #[test]
    fn terminates_when_contributions_cease() {
        let mut k = Kernel::new();
        k.graph.merge(protocol(30, 2));
        let sweep = Scheduler::new(Selection::RoundRobin)
            .with_max_steps(1000)
            .run(&mut k);
        assert!(!sweep.truncated);
        assert_eq!(sweep.chunks, 60);
    }

    #[test]
    fn an_empty_graph_sweeps_to_nothing() {
        let mut k = Kernel::new();
        let sweep = Scheduler::new(Selection::RoundRobin).run(&mut k);
        assert_eq!(sweep.executions, 0);
        assert!(!sweep.truncated);
    }

    #[test]
    fn raising_chunks_do_not_stop_the_sweep() {
        let mut k = Kernel::new();
        let mut c = Contribution::new();
        for i in 0..10 {
            c = c.with(
                format!("n{i}"),
                Chunk::new(ChunkId::of(&format!("bad{i}")), "test", || {
                    Err("deliberate".into())
                }),
            );
        }
        k.graph.merge(c);
        let sweep = Scheduler::new(Selection::RoundRobin).run(&mut k);
        assert_eq!(sweep.executions, 10);
        assert_eq!(k.record().get(), 10);
    }
}
