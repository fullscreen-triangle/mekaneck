//! Many contributions converging on one node.
//!
//! A node's value may now depend on what other nodes produced, which is what
//! lets several lines of work compose into one conclusion rather than each
//! standing alone. Three properties are checked here because each is a place
//! the design could quietly go wrong:
//!
//! - a chunk sees only what it declared reading, so the recorded trajectory
//!   matches the reads actually permitted;
//! - a contribution closing a read cycle is refused, naming the cycle, and
//!   leaves the graph unchanged;
//! - a node holding several values hands the reader the bag, never a verdict.

use mekaneck_kernel::*;
use serde_json::json;

fn emits(name: &str, payload: serde_json::Value) -> Chunk {
    Chunk::new(ChunkId::of(name), "test", move || Ok(payload.clone()))
}

#[test]
fn a_node_can_be_a_function_of_other_nodes() {
    let mut k = Kernel::new();

    // two independent lines of work...
    k.graph.merge(
        Contribution::new()
            .with("evidence.a", emits("a", json!(3)))
            .with("evidence.b", emits("b", json!(4))),
    );

    // ...converging on one conclusion
    k.graph
        .try_merge(Contribution::new().with(
            "conclusion",
            Chunk::reading(
                ChunkId::of("combine"),
                "test",
                ["evidence.a", "evidence.b"],
                |view| {
                    let sum: i64 = ["evidence.a", "evidence.b"]
                        .iter()
                        .flat_map(|t| view.read(t))
                        .filter_map(|v| v.as_json().as_i64())
                        .sum();
                    Ok(json!(sum))
                },
            ),
        ))
        .expect("acyclic");

    // The conclusion is not ready until its inputs have run.
    assert_eq!(k.graph.ready(), vec!["evidence.a", "evidence.b"]);
    assert_eq!(k.graph.blocked().len(), 1);

    let mut sched = Scheduler::new(Selection::RoundRobin);
    sched.run(&mut k);

    assert_eq!(k.graph.read("conclusion")[0].as_json(), &json!(7));
}

#[test]
fn a_chunk_sees_only_what_it_declared() {
    let mut k = Kernel::new();
    k.graph.merge(
        Contribution::new()
            .with("declared", emits("d", json!("visible")))
            .with("undeclared", emits("u", json!("hidden"))),
    );
    k.run_node("declared");
    k.run_node("undeclared");

    k.graph
        .try_merge(Contribution::new().with(
            "probe",
            Chunk::reading(ChunkId::of("p"), "test", ["declared"], |view| {
                Ok(json!({
                    "saw_declared": !view.read("declared").is_empty(),
                    // reachable in the graph, but not declared: empty
                    "saw_undeclared": !view.read("undeclared").is_empty(),
                }))
            }),
        ))
        .unwrap();
    k.run_node("probe");

    let v = k.graph.read("probe")[0].as_json().clone();
    assert_eq!(v["saw_declared"], json!(true));
    assert_eq!(v["saw_undeclared"], json!(false));
}

#[test]
fn a_read_cycle_is_refused_and_named() {
    let mut k = Kernel::new();
    k.graph
        .try_merge(Contribution::new().with(
            "a",
            Chunk::reading(ChunkId::of("a"), "test", ["b"], |_| Ok(json!(1))),
        ))
        .expect("no cycle yet");

    let before = k.graph.fingerprint();

    // b reads a, closing the loop
    let err = k
        .graph
        .try_merge(Contribution::new().with(
            "b",
            Chunk::reading(ChunkId::of("b"), "test", ["a"], |_| Ok(json!(2))),
        ))
        .expect_err("should be refused");

    // the cycle is named, not merely detected
    assert!(err.cycle.len() >= 2, "cycle {:?}", err.cycle);
    assert!(err.to_string().contains("->"));

    // and the refusal left the graph untouched, so a caller may retry
    assert_eq!(k.graph.fingerprint(), before);
}

#[test]
fn a_self_read_is_refused() {
    let mut k = Kernel::new();
    let err = k
        .graph
        .try_merge(Contribution::new().with(
            "solipsist",
            Chunk::reading(ChunkId::of("s"), "test", ["solipsist"], |_| Ok(json!(1))),
        ))
        .expect_err("a node reading itself is a cycle of length one");
    assert!(err.cycle.contains(&"solipsist".to_string()));
}

#[test]
fn a_long_chain_is_permitted() {
    // Acyclicity forbids loops, not depth.
    let mut k = Kernel::new();
    k.graph.merge(Contribution::new().with("n0", emits("n0", json!(0))));

    for i in 1..12 {
        let prev = format!("n{}", i - 1);
        k.graph
            .try_merge(Contribution::new().with(
                format!("n{i}"),
                Chunk::reading(ChunkId::of(&format!("n{i}")), "test", [prev.clone()], move |view| {
                    let v = view
                        .read(&prev)
                        .first()
                        .and_then(|v| v.as_json().as_i64())
                        .unwrap_or(-1);
                    Ok(json!(v + 1))
                }),
            ))
            .expect("a chain is acyclic");
    }

    Scheduler::new(Selection::RoundRobin).run(&mut k);
    assert_eq!(k.graph.read("n11")[0].as_json(), &json!(11));
}

#[test]
fn an_unreachable_read_is_reported_not_silently_stalled() {
    let mut k = Kernel::new();
    k.graph
        .try_merge(Contribution::new().with(
            "waiter",
            Chunk::reading(ChunkId::of("w"), "test", ["never-contributed"], |_| Ok(json!(1))),
        ))
        .unwrap();

    // Nothing is ready, and the reason is available.
    assert!(k.graph.ready().is_empty());
    let blocked = k.graph.blocked();
    assert_eq!(blocked.len(), 1);
    assert_eq!(blocked[0].tau, "waiter");
    assert!(blocked[0].unreachable, "the awaited identity was never contributed");

    // The sweep terminates rather than spinning.
    let sweep = Scheduler::new(Selection::RoundRobin).run(&mut k);
    assert_eq!(sweep.executions, 0);
}

#[test]
fn a_reader_receives_the_whole_bag_not_a_verdict() {
    // Three chunks emit onto one node. A reader gets all three: reducing them
    // to one answer is a judgement, and the kernel makes none.
    let mut k = Kernel::new();
    k.graph.merge(
        Contribution::new()
            .with("panel", emits("x", json!("agree")))
            .with("panel", emits("y", json!("agree")))
            .with("panel", emits("z", json!("dissent"))),
    );
    k.run_node("panel");

    k.graph
        .try_merge(Contribution::new().with(
            "observer",
            Chunk::reading(ChunkId::of("o"), "test", ["panel"], |view| {
                Ok(json!(view.read("panel").len()))
            }),
        ))
        .unwrap();
    k.run_node("observer");

    assert_eq!(k.graph.read("observer")[0].as_json(), &json!(3));
}

#[test]
fn reads_are_recoverable_from_the_protocol() {
    // The read graph is declared, so the dependency structure is part of the
    // protocol rather than something a module must log by hand.
    let mut k = Kernel::new();
    k.graph.merge(Contribution::new().with("src", emits("s", json!(1))));
    k.graph
        .try_merge(Contribution::new().with(
            "dst",
            Chunk::reading(ChunkId::of("d"), "test", ["src"], |_| Ok(json!(2))),
        ))
        .unwrap();

    let edges = k.graph.read_edges();
    assert_eq!(edges, vec![("dst".to_string(), "src".to_string())]);
}
