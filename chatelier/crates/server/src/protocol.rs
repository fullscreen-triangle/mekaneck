//! Wire protocol between the local binary and the browser IDE.
//!
//! This module is the **single source of truth** for the message shapes. The
//! TypeScript in `web/src/connection/protocol.ts` is generated from these
//! types by `cargo test -p mekaneck-server export_bindings`, not written by
//! hand: a mismatched message shape would otherwise fail at runtime over a
//! socket, which is a worse failure than a compile error.
//!
//! Two properties of the papers survive into the wire format and are worth
//! stating, because a client that ignored them would misreport results:
//!
//! - an [`Outcome`] is `Resolved` **or** `Declined`, and a declination is a
//!   normal termination carrying a plurality of cells — not an error frame;
//! - a [`LawRow`] carries `evidential`, which is false under instance-specific
//!   estimation however good the fit, so a client cannot render an algebraic
//!   identity as a finding without discarding the flag on purpose.

use serde::{Deserialize, Serialize};
use ts_rs::TS;

/// Protocol version. The client sends the version it was built against and the
/// server refuses a mismatch rather than negotiating: a stale browser tab
/// talking to a new binary is exactly the drift this design exists to prevent.
pub const PROTOCOL_VERSION: u32 = 1;

// ---------------------------------------------------------------------------
// Client -> server
// ---------------------------------------------------------------------------

#[derive(Debug, Clone, Serialize, Deserialize, TS)]
#[ts(export, export_to = "../../../web/src/connection/protocol.ts")]
#[serde(tag = "type", rename_all = "snake_case")]
pub enum ClientMessage {
    /// First frame on every socket. The token is the one the binary printed on
    /// startup; without it the connection is closed.
    Hello { token: String, protocol: u32 },

    /// Parse and type-check a source buffer. Sent on every keystroke pause, so
    /// it must be cheap and must never evaluate anything.
    Check {
        request_id: String,
        source: String,
        /// Substrate floors, as name → value. Absent floors leave T-Seek-Pos
        /// unchecked and produce a warning rather than an error.
        floors: Vec<FloorBinding>,
    },

    /// Evaluate the `seek` bindings in a program against a substrate.
    Run {
        request_id: String,
        source: String,
        floors: Vec<FloorBinding>,
        cells: Vec<CellBinding>,
    },

    /// Analyse a serialised substrate: floor, separation, law comparison.
    Analyse {
        request_id: String,
        /// A serialised `Tabular` substrate. Opaque to the protocol: the
        /// substrate schema belongs to `mekaneck-substrates`, and duplicating
        /// it here would be a second source of truth.
        #[ts(type = "unknown")]
        substrate: serde_json::Value,
    },

    /// Keepalive. The server replies with [`ServerMessage::Pong`].
    Ping { request_id: String },
}

#[derive(Debug, Clone, Serialize, Deserialize, TS)]
#[ts(export, export_to = "../../../web/src/connection/protocol.ts")]
pub struct FloorBinding {
    pub substrate: String,
    pub value: f64,
}

#[derive(Debug, Clone, Serialize, Deserialize, TS)]
#[ts(export, export_to = "../../../web/src/connection/protocol.ts")]
pub struct CellBinding {
    pub catalyst: String,
    pub cell: String,
}

// ---------------------------------------------------------------------------
// Server -> client
// ---------------------------------------------------------------------------

#[derive(Debug, Clone, Serialize, Deserialize, TS)]
#[ts(export, export_to = "../../../web/src/connection/protocol.ts")]
#[serde(tag = "type", rename_all = "snake_case")]
pub enum ServerMessage {
    /// Accepted handshake. Carries what the client needs to display the
    /// connection honestly: which binary, on which host.
    Welcome {
        protocol: u32,
        server_version: String,
        /// Always loopback. Sent so the UI can state where data is going.
        bound_to: String,
    },

    /// Rejected handshake. The socket closes immediately after.
    Denied { reason: String },

    /// Diagnostics for a `Check`. An empty list means the program is well
    /// formed; warnings are not errors and do not block a run.
    Diagnostics {
        request_id: String,
        diagnostics: Vec<Diagnostic>,
    },

    /// The result of a `Run`: one entry per `let` binding.
    RunResult {
        request_id: String,
        bindings: Vec<BindingResult>,
    },

    /// The result of an `Analyse`.
    AnalysisResult {
        request_id: String,
        substrate: String,
        receivers: Vec<ReceiverFloor>,
        cascades: usize,
        separation: SeparationReport,
        laws: Vec<LawRow>,
    },

    /// A request could not be served. Distinct from a *declination*, which is
    /// a normal result and arrives as a [`BindingResult`].
    Failed { request_id: String, message: String },

    Pong { request_id: String },
}

#[derive(Debug, Clone, Serialize, Deserialize, TS)]
#[ts(export, export_to = "../../../web/src/connection/protocol.ts")]
pub struct Diagnostic {
    pub message: String,
    pub start: usize,
    pub end: usize,
    pub line: usize,
    pub column: usize,
    pub severity: Severity,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize, TS)]
#[ts(export, export_to = "../../../web/src/connection/protocol.ts")]
#[serde(rename_all = "snake_case")]
pub enum Severity {
    Error,
    Warning,
}

#[derive(Debug, Clone, Serialize, Deserialize, TS)]
#[ts(export, export_to = "../../../web/src/connection/protocol.ts")]
pub struct BindingResult {
    pub name: String,
    pub outcome: Outcome,
    /// Committed record: catalysts actually invoked. Monotone.
    pub record: usize,
    pub trace: Vec<TraceStep>,
}

/// The two ways an inquiry ends. There is no third, and neither is an error.
#[derive(Debug, Clone, Serialize, Deserialize, TS)]
#[ts(export, export_to = "../../../web/src/connection/protocol.ts")]
#[serde(tag = "outcome", rename_all = "snake_case")]
pub enum Outcome {
    Resolved { cell: String },
    /// Contested closure: the evidence supports no single cell. The client
    /// must render the plurality rather than picking one.
    Declined { cells: Vec<String> },
}

#[derive(Debug, Clone, Serialize, Deserialize, TS)]
#[ts(export, export_to = "../../../web/src/connection/protocol.ts")]
pub struct TraceStep {
    pub catalyst: String,
    pub cell: String,
    pub record: usize,
}

#[derive(Debug, Clone, Serialize, Deserialize, TS)]
#[ts(export, export_to = "../../../web/src/connection/protocol.ts")]
pub struct ReceiverFloor {
    pub receiver: String,
    pub floor: f64,
    pub estimator: String,
    /// Whether this estimator *could* have returned a non-positive value. A
    /// positive floor from a non-falsifiable estimator is not evidence.
    pub falsifiable: bool,
    pub supports_positive_floor: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize, TS)]
#[ts(export, export_to = "../../../web/src/connection/protocol.ts")]
pub struct SeparationReport {
    pub eta: f64,
    pub between: f64,
    pub within: f64,
    pub n_types: usize,
    pub n_events: usize,
    /// False when a law comparison on this corpus cannot adjudicate the
    /// typing, whatever correlation it reports.
    pub informative: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize, TS)]
#[ts(export, export_to = "../../../web/src/connection/protocol.ts")]
pub struct LawRow {
    pub law: String,
    pub estimation: String,
    /// False under instance-specific estimation. A client that renders such a
    /// row as a finding is discarding this flag deliberately.
    pub evidential: bool,
    pub max_discrepancy: f64,
    pub pearson_r: Option<f64>,
    pub rmse: Option<f64>,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn outcomes_round_trip_with_their_tag() {
        let d = Outcome::Declined {
            cells: vec!["a".into(), "b".into()],
        };
        let j = serde_json::to_value(&d).unwrap();
        assert_eq!(j["outcome"], "declined");
        assert_eq!(j["cells"].as_array().unwrap().len(), 2);

        let back: Outcome = serde_json::from_value(j).unwrap();
        assert!(matches!(back, Outcome::Declined { .. }));
    }

    #[test]
    fn client_messages_are_externally_tagged_by_type() {
        let m = ClientMessage::Ping {
            request_id: "r1".into(),
        };
        let j = serde_json::to_value(&m).unwrap();
        assert_eq!(j["type"], "ping");
    }

    #[test]
    fn a_law_row_carries_its_evidential_status() {
        let row = LawRow {
            law: "multiplicative".into(),
            estimation: "instance_specific".into(),
            evidential: false,
            max_discrepancy: 0.0,
            pearson_r: Some(1.0),
            rmse: Some(0.0),
        };
        let j = serde_json::to_value(&row).unwrap();
        // a perfect fit that is explicitly not evidence
        assert_eq!(j["pearson_r"], 1.0);
        assert_eq!(j["evidential"], false);
    }

    /// Generates the TypeScript client types. Run via
    /// `cargo test -p mekaneck-server export_bindings`.
    ///
    /// This is a test rather than a build script so that generation is
    /// explicit: a protocol change that is not re-exported shows up as a diff
    /// in the generated file, which is exactly the signal we want.
    #[test]
    fn export_bindings() {
        let cfg = ts_rs::Config::default();
        ClientMessage::export_all(&cfg).expect("export ClientMessage");
        ServerMessage::export_all(&cfg).expect("export ServerMessage");
    }
}
