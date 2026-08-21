//! The graph, convergence, and the protocol fingerprint (Paper 2, §4–§5).
//!
//! Merge is associative, commutative and idempotent (Thm 4.1), so the protocol
//! is a function of the *set* of contributions and of nothing about the order
//! in which they arrived.
//!
//! The fingerprint (Thm 5.3) hashes node identities and sorted chunk ids. It
//! is stable under merge order and under resubmission, and changes when any
//! identity or chunk changes — which is what makes a reproducibility claim
//! about the protocol checkable, and a claim about the trajectory not
//! (Cor 5.2).

use std::collections::BTreeMap;

use crate::node::{Chunk, ChunkId, Node, ReadView, Tau, Value};

/// A submitted decomposition: chunks assigned to subtask identities.
#[derive(Debug, Default)]
pub struct Contribution {
    pub chunks: BTreeMap<Tau, Vec<Chunk>>,
}

impl Contribution {
    pub fn new() -> Self {
        Self::default()
    }

    pub fn with(mut self, tau: impl Into<Tau>, chunk: Chunk) -> Self {
        self.chunks.entry(tau.into()).or_default().push(chunk);
        self
    }
}

/// The kernel's state: nodes keyed by subtask identity.
#[derive(Debug, Default)]
pub struct Graph {
    nodes: BTreeMap<Tau, Node>,
}

impl Graph {
    pub fn new() -> Self {
        Self::default()
    }

    /// `identify(τ)`: obtain the node bearing this identity, creating it empty
    /// if absent (Def 2.3).
    pub fn identify(&mut self, tau: impl Into<Tau>) -> &mut Node {
        let tau = tau.into();
        self.nodes.entry(tau.clone()).or_insert_with(|| Node::new(tau))
    }

    pub fn get(&self, tau: &str) -> Option<&Node> {
        self.nodes.get(tau)
    }

    /// `read(n)`: the current value collection, or empty for an absent node.
    pub fn read(&self, tau: &str) -> &[Value] {
        self.nodes.get(tau).map(Node::values).unwrap_or(&[])
    }

    /// `emit(n, x)`: adjoin a value.
    pub fn emit(&mut self, tau: impl Into<Tau>, value: Value) {
        self.identify(tau).emit(value);
    }

    /// Merge a contribution.
    ///
    /// Two contributors that reach the same subtask identity converge onto one
    /// node rather than producing parallel nodes (Def 4.2). Chunks are keyed by
    /// content id, so resubmitting an identical contribution changes nothing
    /// — this is the idempotence half of Thm 4.1.
    ///
    /// The kernel cannot verify that two contributors who reach *the same
    /// subtask* produce the same `τ`. That obligation sits above the kernel
    /// (Rem 4.3); if identities are assigned arbitrarily, convergence simply
    /// never occurs and the graph is a disjoint union of private
    /// decompositions.
    pub fn merge(&mut self, contribution: Contribution) {
        // Infallible form, retained for contributions that read nothing.
        // A nullary contribution cannot close a cycle.
        self.try_merge(contribution)
            .expect("a contribution of nullary chunks cannot close a cycle");
    }

    /// Merge, refusing a contribution that would close a read cycle.
    ///
    /// Rejection is structural, not a judgement about content: the kernel
    /// inspects declared read sets and never values. A cycle is refused
    /// because no execution order exists for it, and because admitting one
    /// would make termination depend on a budget rather than on the protocol
    /// — which would break the separation between what can be computed and
    /// what was.
    ///
    /// The refusal names the cycle, since "some contribution closed a loop"
    /// is not actionable. A refused contribution leaves the graph unchanged,
    /// so a caller may correct and retry.
    pub fn try_merge(&mut self, contribution: Contribution) -> Result<(), CycleError> {
        let mut edges: Vec<(Tau, Tau)> = self.read_edges();
        for (tau, chunks) in &contribution.chunks {
            for c in chunks {
                for r in c.reads() {
                    edges.push((tau.clone(), r.clone()));
                }
            }
        }
        if let Some(cycle) = find_cycle(&edges) {
            return Err(CycleError { cycle });
        }

        for (tau, chunks) in contribution.chunks {
            let node = self.identify(tau);
            for c in chunks {
                if !node.chunks.iter().any(|existing| existing.id == c.id) {
                    node.chunks.push(c);
                }
            }
        }
        Ok(())
    }

    /// Edges of the read graph: `(reader, read)` for every declared read.
    pub fn read_edges(&self) -> Vec<(Tau, Tau)> {
        let mut out = Vec::new();
        for (tau, node) in &self.nodes {
            for c in &node.chunks {
                for r in c.reads() {
                    out.push((tau.clone(), r.clone()));
                }
            }
        }
        out
    }

    pub fn nodes(&self) -> impl Iterator<Item = (&Tau, &Node)> {
        self.nodes.iter()
    }

    pub fn len(&self) -> usize {
        self.nodes.len()
    }

    pub fn is_empty(&self) -> bool {
        self.nodes.is_empty()
    }

    /// Node identities with at least one *runnable* pending chunk (Def 7.1).
    ///
    /// A chunk is runnable when every identity it declared reading has
    /// produced values. Readiness is therefore data-dependent once chunks
    /// read: a node whose inputs have not been produced is not ready, and
    /// becomes ready when they are.
    ///
    /// A node whose reads can never be satisfied is reported by
    /// [`Self::blocked`] rather than silently never running.
    pub fn ready(&self) -> Vec<Tau> {
        self.nodes
            .iter()
            .filter(|(_, n)| n.pending().any(|c| self.reads_satisfied(c)))
            .map(|(t, _)| t.clone())
            .collect()
    }

    /// Nodes with pending chunks whose reads are not yet satisfied.
    ///
    /// Distinguishes "waiting on a node that exists but has not run" from
    /// "waiting on an identity nobody contributed". The second cannot resolve
    /// without a further contribution and is worth surfacing; neither is an
    /// error the kernel adjudicates.
    pub fn blocked(&self) -> Vec<Blocked> {
        let mut out = Vec::new();
        for (tau, node) in &self.nodes {
            for c in node.pending() {
                if self.reads_satisfied(c) {
                    continue;
                }
                let missing: Vec<Tau> = c
                    .reads()
                    .iter()
                    .filter(|r| !self.has_run(r))
                    .cloned()
                    .collect();
                let unreachable = missing.iter().any(|m| !self.nodes.contains_key(m));
                out.push(Blocked {
                    tau: tau.clone(),
                    chunk: c.id.clone(),
                    waiting_on: missing,
                    unreachable,
                });
            }
        }
        out
    }

    /// Whether every identity this chunk reads has produced values.
    fn reads_satisfied(&self, chunk: &Chunk) -> bool {
        chunk.reads().iter().all(|r| self.has_run(r))
    }

    fn has_run(&self, tau: &str) -> bool {
        self.nodes
            .get(tau)
            .map(|n| !n.values().is_empty())
            .unwrap_or(false)
    }

    /// A view over what a chunk declared it reads.
    pub(crate) fn view_for<'a>(&'a self, chunk: &Chunk) -> ReadView<'a> {
        let mut entries = BTreeMap::new();
        for r in chunk.reads() {
            if let Some(node) = self.nodes.get(r) {
                entries.insert(r.clone(), node.values());
            }
        }
        ReadView::new(entries)
    }

    /// The protocol fingerprint (Thm 5.3): a hash of node identities and their
    /// sorted chunk ids.
    ///
    /// Invariant under merge order and resubmission; sensitive to any change of
    /// identity or chunk. Values are deliberately *not* hashed — the protocol
    /// is what can be computed, not what was.
    pub fn fingerprint(&self) -> String {
        use sha2::{Digest, Sha256};
        let mut h = Sha256::new();
        for (tau, node) in &self.nodes {
            h.update(tau.as_bytes());
            h.update(b"\x1f");
            for id in node.chunk_ids() {
                h.update(id.0.as_bytes());
                h.update(b"\x1e");
            }
            h.update(b"\x1d");
        }
        format!("{:x}", h.finalize())
    }

    pub(crate) fn node_mut(&mut self, tau: &str) -> Option<&mut Node> {
        self.nodes.get_mut(tau)
    }

    /// Total chunks across all nodes.
    pub fn chunk_count(&self) -> usize {
        self.nodes.values().map(|n| n.chunks.len()).sum()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::node::ChunkId;
    use serde_json::json;

    fn chunk(name: &str) -> Chunk {
        Chunk::new(ChunkId::of(name), "test", || Ok(json!(1)))
    }

    fn contribution(name: &str, taus: &[&str]) -> Contribution {
        let mut c = Contribution::new();
        for t in taus {
            c = c
                .with(*t, chunk(&format!("{name}:{t}:0")))
                .with(*t, chunk(&format!("{name}:{t}:1")));
        }
        c
    }

    #[test]
    fn merge_is_order_independent() {
        // Thm 4.1: the protocol is a function of the set of contributions.
        let mut fps = std::collections::BTreeSet::new();
        for order in [[0, 1, 2], [2, 1, 0], [1, 2, 0], [0, 2, 1], [1, 0, 2], [2, 0, 1]] {
            let mut g = Graph::new();
            for i in order {
                g.merge(match i {
                    0 => contribution("A", &["alpha", "beta"]),
                    1 => contribution("B", &["beta", "gamma"]),
                    _ => contribution("C", &["gamma", "delta"]),
                });
            }
            fps.insert(g.fingerprint());
        }
        assert_eq!(fps.len(), 1, "protocol varied with merge order");
    }

    #[test]
    fn merge_is_idempotent() {
        let mut a = Graph::new();
        a.merge(contribution("X", &["p", "q"]));
        let once = (a.fingerprint(), a.chunk_count());

        a.merge(contribution("X", &["p", "q"]));
        a.merge(contribution("X", &["p", "q"]));
        assert_eq!((a.fingerprint(), a.chunk_count()), once);
    }

    #[test]
    fn independent_contributors_converge_on_a_shared_identity() {
        let mut g = Graph::new();
        g.merge(contribution("A", &["shared"]));
        g.merge(contribution("B", &["shared"]));
        // one node, four chunks: convergence, not parallel nodes
        assert_eq!(g.len(), 1);
        assert_eq!(g.get("shared").unwrap().chunks.len(), 4);
    }

    #[test]
    fn fingerprint_detects_chunk_and_identity_changes() {
        let mut base = Graph::new();
        base.merge(contribution("X", &["p"]));
        let f0 = base.fingerprint();

        let mut altered_chunk = Graph::new();
        altered_chunk.merge(Contribution::new().with("p", chunk("X:p:0")).with("p", chunk("MUTATED")));
        assert_ne!(f0, altered_chunk.fingerprint());

        let mut altered_id = Graph::new();
        altered_id.merge(contribution("X", &["different"]));
        assert_ne!(f0, altered_id.fingerprint());
    }

    #[test]
    fn fingerprint_ignores_values() {
        // The protocol is what can be computed, not what was (Cor 5.2).
        let mut g = Graph::new();
        g.merge(contribution("X", &["p"]));
        let before = g.fingerprint();
        g.emit("p", Value::ok(json!("anything")));
        g.emit("p", Value::error("boom", "x"));
        assert_eq!(before, g.fingerprint());
    }

    #[test]
    fn reading_an_absent_node_is_empty_not_an_error() {
        let g = Graph::new();
        assert!(g.read("nothing-here").is_empty());
    }
}


/// A pending chunk whose declared reads are not yet satisfied.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Blocked {
    pub tau: Tau,
    pub chunk: ChunkId,
    /// Identities it is waiting on.
    pub waiting_on: Vec<Tau>,
    /// True when at least one awaited identity was never contributed, so the
    /// wait cannot resolve without a further contribution.
    pub unreachable: bool,
}

/// A contribution refused because it would close a read cycle.
#[derive(Debug, Clone, PartialEq, Eq, thiserror::Error)]
#[error("contribution would close a read cycle: {}", .cycle.join(" -> "))]
pub struct CycleError {
    /// The cycle, as a sequence of identities returning to its start.
    pub cycle: Vec<Tau>,
}

/// Find a cycle in a directed edge list, returning it if one exists.
///
/// Iterative depth-first search, so the cycle can be reported rather than
/// merely detected, and so a deep graph cannot overflow the stack.
fn find_cycle(edges: &[(Tau, Tau)]) -> Option<Vec<Tau>> {
    use std::collections::BTreeMap as Map;

    let mut adj: Map<&str, Vec<&str>> = Map::new();
    for (from, to) in edges {
        adj.entry(from.as_str()).or_default().push(to.as_str());
        adj.entry(to.as_str()).or_default();
    }

    #[derive(Clone, Copy, PartialEq)]
    enum Mark {
        Open,
        Done,
    }

    let mut mark: Map<&str, Mark> = Map::new();
    let keys: Vec<&str> = adj.keys().copied().collect();

    for root in keys {
        if mark.contains_key(root) {
            continue;
        }
        // (node, index of next child to visit)
        let mut stack: Vec<(&str, usize)> = vec![(root, 0)];
        mark.insert(root, Mark::Open);

        while let Some(&mut (node, ref mut idx)) = stack.last_mut() {
            let children = adj.get(node).map(Vec::as_slice).unwrap_or(&[]);
            if *idx < children.len() {
                let next = children[*idx];
                *idx += 1;
                match mark.get(next) {
                    Some(Mark::Done) => {}
                    Some(Mark::Open) => {
                        let at = stack.iter().position(|(n, _)| *n == next).unwrap_or(0);
                        let mut cyc: Vec<Tau> =
                            stack[at..].iter().map(|(n, _)| n.to_string()).collect();
                        cyc.push(next.to_string());
                        return Some(cyc);
                    }
                    None => {
                        mark.insert(next, Mark::Open);
                        stack.push((next, 0));
                    }
                }
            } else {
                mark.insert(node, Mark::Done);
                stack.pop();
            }
        }
    }
    None
}
