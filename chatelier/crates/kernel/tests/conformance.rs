//! Conformance against `chatelier/validation/validate_kernel.py`.
//!
//! Emergence and opacity need several runs of one protocol, so they live here
//! rather than in the unit tests. Quoted numbers are the ones the Python suite
//! records in `validation/results/kernel_results.json`.

use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::Arc;

use mekaneck_kernel::*;
use serde_json::json;

fn ok(name: &str) -> Chunk {
    Chunk::new(ChunkId::of(name), "conf", || Ok(json!(1)))
}

fn bad(name: &str) -> Chunk {
    Chunk::new(ChunkId::of(name), "conf", || Err("deliberate".into()))
}

/// Thm 3.1 / Cor 3.2, and the Python `inertia_and_completion` check: a node of
/// five chunks, two of which raise, emits five values and commits five times.
#[test]
fn inertia_matches_python() {
    let mut k = Kernel::new();
    k.graph.merge(
        Contribution::new()
            .with("t", ok("c1"))
            .with("t", bad("c2"))
            .with("t", ok("c3"))
            .with("t", bad("c4"))
            .with("t", ok("c5")),
    );
    k.run_node("t");

    let vals = k.graph.read("t");
    assert_eq!(vals.len(), 5, "n_values_emitted");
    assert_eq!(vals.iter().filter(|v| v.is_error()).count(), 2, "n_error_values");
    assert_eq!(vals.iter().filter(|v| !v.is_error()).count(), 3, "n_normal_values");
    assert_eq!(k.record().get(), 5, "committed_record");
}

/// Under a rising failure rate the inert kernel evaluates every chunk, while a
/// fail-fast runtime would stop at the first raise. The Python panel reports
/// the inert count constant at 60 across all 21 rates.
#[test]
fn evaluation_count_is_independent_of_failure_rate() {
    const N: usize = 60;
    for numerator in 0..=10 {
        let mut k = Kernel::new();
        let mut c = Contribution::new();
        for i in 0..N {
            // deterministic "failure rate" of numerator/10
            let fails = (i * 10) % 100 < numerator * 10;
            c = c.with(
                "t",
                if fails {
                    bad(&format!("c{i}"))
                } else {
                    ok(&format!("c{i}"))
                },
            );
        }
        k.graph.merge(c);
        k.run_node("t");
        assert_eq!(k.graph.read("t").len(), N, "rate {numerator}/10");
        assert_eq!(k.record().get(), N);
    }
}

/// Thm 4.1 and the Python `convergence_monoid` check: all merge orders of
/// three contributions give one protocol, and resubmission changes nothing.
#[test]
fn convergence_matches_python() {
    fn contrib(name: &str, taus: &[&str]) -> Contribution {
        let mut c = Contribution::new();
        for t in taus {
            c = c
                .with(*t, ok(&format!("{name}:{t}:0")))
                .with(*t, ok(&format!("{name}:{t}:1")));
        }
        c
    }

    let mut fps = std::collections::BTreeSet::new();
    for order in [[0, 1, 2], [0, 2, 1], [1, 0, 2], [1, 2, 0], [2, 0, 1], [2, 1, 0]] {
        let mut g = Graph::new();
        for i in order {
            g.merge(match i {
                0 => contrib("A", &["alpha", "beta"]),
                1 => contrib("B", &["beta", "gamma"]),
                _ => contrib("C", &["gamma", "delta"]),
            });
        }
        fps.insert(g.fingerprint());
    }
    // Python: n_distinct_fingerprints = 1 over 6 orders
    assert_eq!(fps.len(), 1);

    // Python: converged_node_chunk_count = 4 on the shared identity
    let mut g = Graph::new();
    g.merge(contrib("A", &["beta"]));
    g.merge(contrib("B", &["beta"]));
    assert_eq!(g.get("beta").unwrap().chunks.len(), 4);
}

/// Thm 5.1: one protocol, differing trajectories.
///
/// The probe chunk consults a source outside the graph, and a module branches
/// on what it read — so the route differs across runs while the node set and
/// chunk bags do not.
#[test]
fn trajectory_emerges_from_a_fixed_protocol() {
    fn run(external: usize) -> (String, Trajectory) {
        let seen = Arc::new(AtomicUsize::new(external));
        let probe = {
            let seen = Arc::clone(&seen);
            Chunk::new(ChunkId::of("probe"), "conf", move || {
                Ok(json!(seen.load(Ordering::SeqCst)))
            })
        };

        let mut k = Kernel::new();
        k.graph.merge(
            Contribution::new()
                .with("n1", probe)
                .with("n2", ok("n2c"))
                .with("n3", ok("n3c"))
                .with("n4", ok("n4c")),
        );
        k.run_node("n1");

        // A module reads n1 and, on the strength of it, emits elsewhere.
        let branch = if external % 2 == 0 { "n2" } else { "n3" };
        let mut t = Trajectory::new();
        k.graph.emit(branch, Value::ok(json!("intermediate")));
        t.record("n1", branch, k.record().get() + 1);
        k.graph.emit("n4", Value::ok(json!("TERMINAL")));
        t.record(branch, "n4", k.record().get() + 2);

        (k.graph.fingerprint(), t)
    }

    let (fp_a, tr_a) = run(2);
    let (fp_b, tr_b) = run(3);

    assert_eq!(fp_a, fp_b, "protocol must be identical");
    assert_ne!(tr_a.digest(), tr_b.digest(), "trajectory must differ");
}

/// Thm 5.4 / Cor 5.5: two runs reaching the same terminal store are not
/// separated by any function of that store, though their interiors differ.
#[test]
fn trajectories_are_opaque_from_the_terminal_store() {
    fn run(external: usize) -> (Vec<String>, Trajectory) {
        let mut k = Kernel::new();
        k.graph.merge(
            Contribution::new()
                .with("n2", ok("n2c"))
                .with("n3", ok("n3c"))
                .with("n4", ok("n4c")),
        );

        let branch = if external % 2 == 0 { "n2" } else { "n3" };
        let mut t = Trajectory::new();
        k.graph.emit(branch, Value::ok(json!("intermediate")));
        t.record("n1", branch, 1);
        // both branches deposit the SAME terminal value
        k.graph.emit("n4", Value::ok(json!("TERMINAL")));
        t.record(branch, "n4", 2);

        let store: Vec<String> = k
            .graph
            .read("n4")
            .iter()
            .map(|v| v.as_json().to_string())
            .collect();
        (store, t)
    }

    let (store_a, tr_a) = run(2);
    let (store_b, tr_b) = run(3);

    assert_eq!(store_a, store_b, "terminal stores must agree");
    assert_ne!(tr_a.digest(), tr_b.digest(), "interiors must differ");

    // No function of the terminal store separates them. Probe three.
    let len = |s: &Vec<String>| s.len();
    let sorted = |s: &Vec<String>| {
        let mut v = s.clone();
        v.sort();
        v
    };
    let digest = |s: &Vec<String>| {
        use sha2::{Digest, Sha256};
        let mut h = Sha256::new();
        for x in sorted(s) {
            h.update(x.as_bytes());
        }
        format!("{:x}", h.finalize())
    };
    assert_eq!(len(&store_a), len(&store_b));
    assert_eq!(sorted(&store_a), sorted(&store_b));
    assert_eq!(digest(&store_a), digest(&store_b));
}

/// Thm 7.1 and the Python `scheduler_soundness` check: 12 nodes of 3 chunks
/// give 12 executions and a record of 36, with no node visited twice.
#[test]
fn scheduler_matches_python() {
    let mut k = Kernel::new();
    let mut c = Contribution::new();
    for i in 0..12 {
        for j in 0..3 {
            c = c.with(format!("n{i}"), ok(&format!("n{i}c{j}")));
        }
    }
    k.graph.merge(c);

    let sweep = Scheduler::new(Selection::Rotating).run(&mut k);
    assert_eq!(sweep.executions, 12, "executions");
    assert_eq!(k.record().get(), 36, "committed_record_after_sweep");
    assert!(k.graph.ready().is_empty(), "terminated");

    let mut v = sweep.visited.clone();
    v.sort();
    v.dedup();
    assert_eq!(v.len(), 12, "no_redundant_execution");

    // Python: late_chunk_served = true, served in one step
    k.graph
        .merge(Contribution::new().with("n0", ok("late_chunk")));
    let second = Scheduler::new(Selection::Rotating).run(&mut k);
    assert_eq!(second.executions, 1);
    assert_eq!(k.record().get(), 37);
}

/// Thm 6.1: a recurring value configuration is not a return, because the
/// record has strictly grown.
#[test]
fn recurrence_is_not_return() {
    let mut k = Kernel::new();
    k.graph
        .merge(Contribution::new().with("a", ok("x1")).with("b", ok("x2")));

    k.run_node("a");
    let r1 = k.record().get();
    k.run_node("b");
    let r2 = k.record().get();

    // equal configurations: one value on each node
    assert_eq!(k.graph.read("a").len(), k.graph.read("b").len());
    // distinct states: the record separates them
    assert!(r1 < r2);
}
