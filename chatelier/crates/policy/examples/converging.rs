//! Several lines of work converging on one conclusion, under a budget.
//!
//! Run with: cargo run -p mekaneck-policy --example converging

use mekaneck_kernel::*;
use mekaneck_policy::{classify_values, Agreement};
use serde_json::json;

fn estimate(name: &str, value: f64) -> Chunk {
    Chunk::new(ChunkId::of(name), "estimator", move || Ok(json!(value)))
}

fn main() {
    let mut k = Kernel::new();

    // Three independent estimators, contributed separately.
    k.graph.merge(
        Contribution::new()
            .with("floor.spectral", estimate("s", 10.02))
            .with("floor.surrogate", estimate("u", 10.01))
            .with("floor.phase", estimate("p", 14.80)),
    );

    // One node reads all three and reports their spread.
    k.graph
        .try_merge(Contribution::new().with(
            "floor.consensus",
            Chunk::reading(
                ChunkId::of("spread"),
                "analysis",
                ["floor.spectral", "floor.surrogate", "floor.phase"],
                |view| {
                    let xs: Vec<f64> = view
                        .available()
                        .flat_map(|t| view.read(t))
                        .filter_map(|v| v.as_json().as_f64())
                        .collect();
                    let lo = xs.iter().cloned().fold(f64::INFINITY, f64::min);
                    let hi = xs.iter().cloned().fold(f64::NEG_INFINITY, f64::max);
                    Ok(json!({ "n": xs.len(), "spread": hi - lo }))
                },
            ),
        ))
        .expect("acyclic");

    println!("ready first:  {:?}", k.graph.ready());
    println!("blocked:      {}\n", k.graph.blocked().len());

    Scheduler::new(Selection::RoundRobin).run(&mut k);

    println!("consensus:    {}", k.graph.read("floor.consensus")[0].as_json());
    println!("record:       {}\n", k.record().get());

    // The three estimates are a bag. Whether they agree is the caller's call.
    let node = k.graph.read("floor.spectral");
    println!("one estimator alone: {:?}", classify_values(node, Agreement::Exact).outcome);

    // Pool them onto one identity and ask again, at two criteria.
    let mut pooled = Kernel::new();
    pooled.graph.merge(
        Contribution::new()
            .with("floor", estimate("s", 10.02))
            .with("floor", estimate("u", 10.01))
            .with("floor", estimate("p", 14.80)),
    );
    pooled.run_node("floor");
    let bag = pooled.graph.read("floor");

    for agreement in [Agreement::Exact, Agreement::Rounded(0)] {
        let c = classify_values(bag, agreement);
        println!(
            "{:?}: {:?}  modal share {:.2}",
            agreement, c.outcome, c.modal_share()
        );
    }
}
