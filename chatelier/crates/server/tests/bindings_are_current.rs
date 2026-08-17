//! Guard against protocol drift.
//!
//! The TypeScript client types are generated from `protocol.rs`. If someone
//! changes a message shape and does not re-export, the checked-in file goes
//! stale and the browser will fail at runtime over a socket — the failure mode
//! this design exists to prevent. This test turns that into a build failure.
//!
//! Regenerate with:
//!
//! ```text
//! cargo test -p mekaneck-server export_bindings
//! ```

use std::path::PathBuf;

fn bindings_path() -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .join("../../web/src/connection/protocol.ts")
}

#[test]
fn generated_typescript_exists_and_covers_every_message() {
    let path = bindings_path();
    let ts = std::fs::read_to_string(&path).unwrap_or_else(|e| {
        panic!(
            "{} is missing ({e}). Run: cargo test -p mekaneck-server export_bindings",
            path.display()
        )
    });

    // Every type the protocol exports must appear. A new variant that is not
    // re-exported fails here rather than in a browser.
    for ty in [
        "ClientMessage",
        "ServerMessage",
        "FloorBinding",
        "CellBinding",
        "Diagnostic",
        "Severity",
        "BindingResult",
        "Outcome",
        "TraceStep",
        "ReceiverFloor",
        "SeparationReport",
        "LawRow",
    ] {
        assert!(
            ts.contains(&format!("export type {ty} ")),
            "protocol.ts has no `{ty}`; regenerate the bindings"
        );
    }
}

/// The two properties a client must not lose in translation.
#[test]
fn the_wire_format_preserves_declination_and_evidential_status() {
    let ts = std::fs::read_to_string(bindings_path()).expect("bindings");

    // A declination carries a plurality of cells, so a client cannot render a
    // contested result as a single answer.
    assert!(
        ts.contains(r#""outcome": "declined", cells: Array<string>"#),
        "Outcome::Declined must carry a list of cells"
    );
    assert!(
        ts.contains(r#""outcome": "resolved", cell: string"#),
        "Outcome::Resolved must carry exactly one cell"
    );

    // The evidential flag must reach the client, or an algebraic identity
    // could be displayed as a finding.
    assert!(
        ts.contains("evidential: boolean"),
        "LawRow must carry `evidential`"
    );

    // And the doc comment explaining why should survive, since it is the only
    // warning a UI author will see at the point of use.
    assert!(
        ts.contains("instance-specific estimation"),
        "the evidential doc comment should be carried into the bindings"
    );
}

/// Every field name in the generated TypeScript must match what serde emits.
#[test]
fn field_names_match_the_serialised_form() {
    use mekaneck_server::protocol::*;

    let ts = std::fs::read_to_string(bindings_path()).expect("bindings");

    // Round-trip a representative message and check each key appears in the TS.
    let msg = ServerMessage::AnalysisResult {
        request_id: "r".into(),
        substrate: "s".into(),
        receivers: vec![ReceiverFloor {
            receiver: "rec".into(),
            floor: 10.0,
            estimator: "asymptotic".into(),
            falsifiable: true,
            supports_positive_floor: true,
        }],
        cascades: 1,
        separation: SeparationReport {
            eta: 0.9,
            between: 0.1,
            within: 0.01,
            n_types: 2,
            n_events: 4,
            informative: true,
        },
        laws: vec![],
    };
    let json = serde_json::to_value(&msg).unwrap();

    for key in json.as_object().unwrap().keys() {
        if key == "type" {
            continue; // the tag, rendered as `"type": "..."`
        }
        assert!(
            ts.contains(&format!("{key}:")),
            "serde emits {key:?} but protocol.ts has no such field"
        );
    }
}
