//! Nodes, chunks and values (Paper 2, §2).
//!
//! A node is `(τ, K(n), V(n))`: a subtask identity, a bag of executable
//! chunks, and a growing collection of values.
//!
//! The kernel's inertia is structural here rather than conventional. [`Value`]
//! exposes no comparison, no ordering, and no accessor that yields anything
//! the kernel could branch on — only [`Value::as_json`], which exists for
//! *modules* and for serialisation to a client. Nothing in this crate calls
//! it. An error value is an ordinary value (Cor 3.2), so a raising chunk
//! commits exactly as a returning one does.

use std::collections::{BTreeMap, BTreeSet};

use serde::{Deserialize, Serialize};

/// A subtask identity.
///
/// Convergence (Def 4.2) depends on two contributors who reach *the same*
/// subtask producing the same identity, so this should be derived from a
/// canonical description of the subtask rather than assigned. The kernel
/// cannot check that and does not pretend to — see `Rem 4.3` and the note on
/// [`crate::graph::Graph::merge`].
pub type Tau = String;

/// A content hash identifying a chunk.
///
/// Merge is idempotent only if two submissions of the same work carry the same
/// id (Thm 4.1), so this is derived from chunk content, not from a counter.
#[derive(Debug, Clone, PartialEq, Eq, PartialOrd, Ord, Hash, Serialize, Deserialize)]
pub struct ChunkId(pub String);

impl ChunkId {
    /// Hash the chunk's source text or canonical description.
    pub fn of(content: &str) -> Self {
        use sha2::{Digest, Sha256};
        let mut h = Sha256::new();
        h.update(content.as_bytes());
        ChunkId(format!("{:x}", h.finalize()))
    }

    pub fn short(&self) -> &str {
        &self.0[..16.min(self.0.len())]
    }
}

/// A value emitted onto a node.
///
/// Deliberately opaque. The kernel stores and transports values and never
/// inspects them: there is no `PartialEq`, no `PartialOrd`, and no predicate
/// over contents, so no kernel-computable quantity can depend on what a value
/// *says*. This is what makes [`crate::exec`] unable to compute an exit code
/// (Thm 3.1) rather than merely choosing not to.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Value {
    payload: serde_json::Value,
    /// Set when the producing chunk raised. Recorded so that a *module* can
    /// see it; the kernel itself never reads this field.
    is_error: bool,
}

impl Value {
    pub fn ok(payload: serde_json::Value) -> Self {
        Value {
            payload,
            is_error: false,
        }
    }

    /// An exception, wrapped as an ordinary value (Cor 3.2). This is not a
    /// control-flow signal: it is emitted, stored and read like any other.
    pub fn error(kind: &str, message: &str) -> Self {
        Value {
            payload: serde_json::json!({ "__error__": kind, "message": message }),
            is_error: true,
        }
    }

    /// For modules and for serialisation to a client. Not called anywhere in
    /// this crate; the kernel has no use for it.
    pub fn as_json(&self) -> &serde_json::Value {
        &self.payload
    }

    /// Whether the producing chunk raised.
    ///
    /// This is reporting, not adjudication: nothing in the kernel branches on
    /// it, and a module that does is making a judgement of its own, visibly.
    pub fn is_error(&self) -> bool {
        self.is_error
    }
}

/// What a chunk body is: a function of its declared reads, returning either a
/// value or a message that becomes an error value.
type ChunkBody = dyn Fn(&ReadView) -> Result<serde_json::Value, String> + Send + Sync;

/// An executable chunk: a closure plus the id that identifies it.
///
/// The kernel knows only that a chunk can be evaluated and that evaluating it
/// yields a value. It does not know what DSL produced it.
pub struct Chunk {
    pub id: ChunkId,
    /// The DSL or module that contributed this chunk, for display only.
    pub origin: String,
    /// Subtask identities this chunk reads before it can be evaluated.
    ///
    /// Declared rather than discovered. The kernel needs the read set *before*
    /// running anything — to order execution, to reject a contribution that
    /// would close a cycle, and to record the trajectory — and it cannot learn
    /// it by inspecting the closure.
    reads: Vec<Tau>,
    run: Box<ChunkBody>,
}

impl Chunk {
    /// A chunk that reads nothing.
    ///
    /// Retained unchanged: a nullary chunk is the common case and should not
    /// have to mention an empty read set.
    pub fn new<F>(id: ChunkId, origin: impl Into<String>, run: F) -> Self
    where
        F: Fn() -> Result<serde_json::Value, String> + Send + Sync + 'static,
    {
        Chunk {
            id,
            origin: origin.into(),
            reads: Vec::new(),
            run: Box::new(move |_| run()),
        }
    }

    /// A chunk whose value depends on other nodes.
    ///
    /// This is what lets many contributions converge into one: a node's value
    /// can be a function of what other nodes produced, rather than every
    /// contribution standing alone.
    ///
    /// The read set is declared up front. A chunk that reads a node absent
    /// from this list receives nothing from it — the view is restricted to
    /// what was declared, so the trajectory recorded matches the reads
    /// actually permitted.
    pub fn reading<F>(
        id: ChunkId,
        origin: impl Into<String>,
        reads: impl IntoIterator<Item = impl Into<Tau>>,
        run: F,
    ) -> Self
    where
        F: Fn(&ReadView) -> Result<serde_json::Value, String> + Send + Sync + 'static,
    {
        Chunk {
            id,
            origin: origin.into(),
            reads: reads.into_iter().map(Into::into).collect(),
            run: Box::new(run),
        }
    }

    /// Subtask identities this chunk declares it reads.
    pub fn reads(&self) -> &[Tau] {
        &self.reads
    }

    /// Evaluate against a view of what it declared it reads.
    ///
    /// A returned `Err` becomes an error *value*, not a failure of the kernel:
    /// `Run(n)` proceeds to the next chunk regardless (Cor 3.2).
    pub(crate) fn eval(&self, view: &ReadView) -> Value {
        match (self.run)(view) {
            Ok(v) => Value::ok(v),
            Err(e) => Value::error("chunk_error", &e),
        }
    }
}

/// What a chunk may read while evaluating.
///
/// Restricted to the identities the chunk declared, so a chunk cannot reach
/// values it did not announce a dependency on — the read set is a contract,
/// not a hint.
///
/// A read returns the node's whole value collection, deliberately. Several
/// chunks may have emitted onto one node, and reducing that bag to a single
/// answer is adjudication: whether the values agree is a question for a
/// consuming module, which must choose a criterion visibly rather than
/// inherit one from the kernel.
#[derive(Debug, Default)]
pub struct ReadView<'a> {
    entries: BTreeMap<Tau, &'a [Value]>,
}

impl<'a> ReadView<'a> {
    pub(crate) fn new(entries: BTreeMap<Tau, &'a [Value]>) -> Self {
        ReadView { entries }
    }

    /// Values a node holds, or empty when the identity was not declared or
    /// the node emitted nothing.
    pub fn read(&self, tau: &str) -> &[Value] {
        self.entries.get(tau).copied().unwrap_or(&[])
    }

    /// Identities available in this view.
    pub fn available(&self) -> impl Iterator<Item = &Tau> {
        self.entries.keys()
    }

    /// Whether every declared read produced at least one value.
    ///
    /// Reported, not enforced: a chunk is free to run on partial input, and
    /// deciding that partial input is unacceptable is the chunk's judgement
    /// to make, not the kernel's.
    pub fn complete(&self) -> bool {
        self.entries.values().all(|v| !v.is_empty())
    }
}

impl std::fmt::Debug for Chunk {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.debug_struct("Chunk")
            .field("id", &self.id.short())
            .field("origin", &self.origin)
            .finish_non_exhaustive()
    }
}

/// A node: subtask identity, chunk bag, value collection.
#[derive(Debug, Default)]
pub struct Node {
    pub tau: Tau,
    pub chunks: Vec<Chunk>,
    /// Append-only. `emit` adjoins and never replaces, so no emission
    /// destroys a prior one (Cor 3.3).
    values: Vec<Value>,
    /// Chunk ids already evaluated in this run, so a node whose bag has not
    /// changed is not re-executed (Thm 7.1(i)).
    executed: BTreeSet<ChunkId>,
}

impl Node {
    pub fn new(tau: impl Into<Tau>) -> Self {
        Node {
            tau: tau.into(),
            ..Default::default()
        }
    }

    /// Adjoin a value. There is no `set`, no `remove`, and no `clear`.
    pub fn emit(&mut self, value: Value) {
        self.values.push(value);
    }

    /// Read the value collection. Returns a slice, not ownership: a reader
    /// cannot remove what it has read.
    pub fn values(&self) -> &[Value] {
        &self.values
    }

    /// Chunks contributed but not yet evaluated in this run.
    pub fn pending(&self) -> impl Iterator<Item = &Chunk> {
        self.chunks.iter().filter(|c| !self.executed.contains(&c.id))
    }

    pub fn has_pending(&self) -> bool {
        self.pending().next().is_some()
    }

    pub(crate) fn mark_executed(&mut self, id: ChunkId) {
        self.executed.insert(id);
    }

    /// Sorted chunk ids, for the protocol fingerprint (Thm 5.3).
    pub fn chunk_ids(&self) -> Vec<&ChunkId> {
        let mut v: Vec<&ChunkId> = self.chunks.iter().map(|c| &c.id).collect();
        v.sort();
        v
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn chunk_ids_are_content_derived() {
        assert_eq!(ChunkId::of("same"), ChunkId::of("same"));
        assert_ne!(ChunkId::of("a"), ChunkId::of("b"));
    }

    #[test]
    fn emit_adjoins_and_never_replaces() {
        let mut n = Node::new("t");
        n.emit(Value::ok(serde_json::json!(1)));
        n.emit(Value::ok(serde_json::json!(2)));
        n.emit(Value::error("boom", "x"));
        assert_eq!(n.values().len(), 3);
        // the error sits alongside the others, not in place of them
        assert!(n.values()[2].is_error());
        assert!(!n.values()[0].is_error());
    }

    #[test]
    fn a_raising_chunk_yields_an_error_value() {
        let c = Chunk::new(ChunkId::of("bad"), "test", || Err("deliberate".into()));
        let v = c.eval(&ReadView::default());
        assert!(v.is_error());
        assert_eq!(v.as_json()["__error__"], "chunk_error");
    }

    #[test]
    fn pending_excludes_executed() {
        let mut n = Node::new("t");
        let id = ChunkId::of("c1");
        n.chunks
            .push(Chunk::new(id.clone(), "test", || Ok(serde_json::json!(1))));
        assert!(n.has_pending());
        n.mark_executed(id);
        assert!(!n.has_pending());
    }
}
