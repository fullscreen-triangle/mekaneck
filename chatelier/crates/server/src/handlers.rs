//! Request handling, independent of transport.
//!
//! Every function here maps a [`ClientMessage`] to a [`ServerMessage`] with no
//! socket involved, so the protocol can be exercised without a network. The
//! WebSocket layer in [`crate::ws`] does nothing but framing and dispatch.

use std::collections::BTreeMap;

use mekaneck_algebra as alg;
use mekaneck_lang as lang;
use mekaneck_substrates::{cascade_for, Substrate, Tabular};

use crate::protocol::*;

/// Parse and type-check. Never evaluates.
pub fn check(request_id: String, source: &str, floors: &[FloorBinding]) -> ServerMessage {
    let fv: lang::FloorValues = floors
        .iter()
        .map(|f| (f.substrate.clone(), f.value))
        .collect();

    let diagnostics = lang::diagnose(source, &fv)
        .into_iter()
        .map(|d| {
            let (line, column) = d.span.line_col(source);
            Diagnostic {
                message: d.message,
                start: d.span.start,
                end: d.span.end,
                line,
                column,
                severity: match d.severity {
                    lang::Severity::Error => Severity::Error,
                    lang::Severity::Warning => Severity::Warning,
                },
            }
        })
        .collect();

    ServerMessage::Diagnostics {
        request_id,
        diagnostics,
    }
}

/// Evaluate the `seek` bindings of a program.
///
/// A *declination* is returned as a [`BindingResult`], not as
/// [`ServerMessage::Failed`]: contested evidence is one of the two normal
/// terminations, and reporting it as a failure would be the error the closure
/// criterion exists to prevent.
pub fn run(
    request_id: String,
    source: &str,
    floors: &[FloorBinding],
    cells: &[CellBinding],
) -> ServerMessage {
    let fv: lang::FloorValues = floors
        .iter()
        .map(|f| (f.substrate.clone(), f.value))
        .collect();

    let prog = match lang::parse(source) {
        Ok(p) => p,
        Err(e) => return failed(request_id, e.to_string()),
    };
    if let Err(e) = lang::typecheck(&prog, &fv) {
        return failed(request_id, e.to_string());
    }

    let mut substrate = lang::FixedSubstrate::new();
    for c in cells {
        substrate = substrate.with(&c.catalyst, &c.cell);
    }

    let mut bindings = Vec::new();
    for l in prog.lets() {
        match lang::eval_seek(&l.seek, &substrate) {
            Ok(ev) => bindings.push(BindingResult {
                name: l.name.clone(),
                outcome: match ev.outcome {
                    alg::Outcome::Resolved { cell } => Outcome::Resolved { cell },
                    alg::Outcome::Declined { cells } => Outcome::Declined { cells },
                },
                record: ev.record,
                trace: ev
                    .trace
                    .iter()
                    .map(|s| TraceStep {
                        catalyst: s.catalyst.clone(),
                        cell: s.cell.clone(),
                        record: s.record,
                    })
                    .collect(),
            }),
            Err(e) => return failed(request_id, e.to_string()),
        }
    }

    ServerMessage::RunResult {
        request_id,
        bindings,
    }
}

/// Analyse a serialised substrate: floors, separation, law comparison.
///
/// Both estimation regimes are reported. The instance-specific rows are
/// included precisely so a client can show that their perfect agreement is an
/// identity, and each row carries `evidential` to say so.
pub fn analyse(request_id: String, substrate: &serde_json::Value) -> ServerMessage {
    let sub: Tabular = match serde_json::from_value(substrate.clone()) {
        Ok(s) => s,
        Err(e) => return failed(request_id, format!("not a substrate: {e}")),
    };

    let mut receivers = Vec::new();
    let mut cascades = Vec::new();
    for r in sub.receivers() {
        match sub.floor(&r) {
            Ok(f) => receivers.push(ReceiverFloor {
                receiver: r.clone(),
                floor: f.value,
                estimator: format!("{:?}", f.estimator).to_lowercase(),
                falsifiable: f.estimator.is_falsifiable(),
                supports_positive_floor: f.supports_positive_floor(alg::ZERO_TOLERANCE),
            }),
            Err(e) => return failed(request_id, format!("receiver {r:?}: {e}")),
        }
        // A receiver that yields no cascade is skipped rather than fatal: the
        // others may still support an analysis.
        if let Ok(c) = cascade_for(&sub, &r) {
            cascades.push(c);
        }
    }

    if cascades.is_empty() {
        return failed(request_id, "no receiver produced a cascade".into());
    }

    let sep = match alg::separation(&cascades) {
        Ok(s) => s,
        Err(e) => return failed(request_id, e.to_string()),
    };
    let averages = match alg::TypeAverages::fit(&cascades) {
        Ok(a) => a,
        Err(e) => return failed(request_id, e.to_string()),
    };

    let mut laws = Vec::new();
    for law in alg::Law::ALL {
        for est in [
            alg::Estimation::InstanceSpecific,
            alg::Estimation::TypeAveraged,
        ] {
            let mut preds = Vec::new();
            let mut meas = Vec::new();
            let mut worst: f64 = 0.0;
            for c in &cascades {
                let avg = matches!(est, alg::Estimation::TypeAveraged).then_some(&averages);
                if let Ok(t) = alg::test_cascade(c, law, est, avg) {
                    worst = worst.max(t.discrepancy());
                    preds.push(t.predicted);
                    meas.push(t.measured);
                }
            }
            laws.push(LawRow {
                law: law.name().to_string(),
                estimation: match est {
                    alg::Estimation::InstanceSpecific => "instance_specific",
                    alg::Estimation::TypeAveraged => "type_averaged",
                }
                .to_string(),
                evidential: est.has_null_hypothesis(),
                max_discrepancy: worst,
                pearson_r: alg::pearson(&preds, &meas),
                rmse: alg::rmse(&preds, &meas),
            });
        }
    }

    ServerMessage::AnalysisResult {
        request_id,
        substrate: sub.name().to_string(),
        receivers,
        cascades: cascades.len(),
        separation: SeparationReport {
            eta: sep.eta,
            between: sep.between,
            within: sep.within,
            n_types: sep.n_types,
            n_events: sep.n_events,
            informative: sep.is_informative(),
        },
        laws,
    }
}

fn failed(request_id: String, message: String) -> ServerMessage {
    ServerMessage::Failed {
        request_id,
        message,
    }
}

/// Dispatch a message. `Hello` is handled by the transport layer, which owns
/// the handshake, so it is rejected here.
pub fn dispatch(msg: ClientMessage) -> ServerMessage {
    match msg {
        ClientMessage::Hello { .. } => ServerMessage::Failed {
            request_id: String::new(),
            message: "hello is only valid as the first frame".into(),
        },
        ClientMessage::Check {
            request_id,
            source,
            floors,
        } => check(request_id, &source, &floors),
        ClientMessage::Run {
            request_id,
            source,
            floors,
            cells,
        } => run(request_id, &source, &floors, &cells),
        ClientMessage::Analyse {
            request_id,
            substrate,
        } => analyse(request_id, &substrate),
        ClientMessage::Ping { request_id } => ServerMessage::Pong { request_id },
    }
}

/// Floors as a map, for callers that already hold one.
pub fn floors_from_map(m: &BTreeMap<String, f64>) -> Vec<FloorBinding> {
    m.iter()
        .map(|(k, v)| FloorBinding {
            substrate: k.clone(),
            value: *v,
        })
        .collect()
}

#[cfg(test)]
mod tests {
    use super::*;

    const GOOD: &str = r#"
substrate Osc { receivers : r(); observable : o(); events : e(); floor : asymptotic(); }
catalyst a : f() independent b, c;
catalyst b : g() independent a, c;
catalyst c : h() independent a, b;
let x = seek t() excluding rest() via (a, b, c) until closure;
report x;
"#;

    fn floors(v: f64) -> Vec<FloorBinding> {
        vec![FloorBinding {
            substrate: "Osc".into(),
            value: v,
        }]
    }

    #[test]
    fn check_reports_no_diagnostics_for_a_good_program() {
        match check("r1".into(), GOOD, &floors(12.5)) {
            ServerMessage::Diagnostics { diagnostics, .. } => assert!(diagnostics.is_empty()),
            other => panic!("unexpected {other:?}"),
        }
    }

    #[test]
    fn check_carries_line_and_column_for_the_editor() {
        let bad = GOOD.replace("excluding rest() ", "");
        match check("r1".into(), &bad, &floors(12.5)) {
            ServerMessage::Diagnostics { diagnostics, .. } => {
                assert_eq!(diagnostics.len(), 1);
                let d = &diagnostics[0];
                assert_eq!(d.severity, Severity::Error);
                assert!(d.line >= 1 && d.column >= 1);
                assert!(d.end >= d.start);
                assert!(d.message.contains("excluding"));
            }
            other => panic!("unexpected {other:?}"),
        }
    }

    #[test]
    fn a_missing_floor_is_a_warning_not_an_error() {
        match check("r1".into(), GOOD, &[]) {
            ServerMessage::Diagnostics { diagnostics, .. } => {
                assert_eq!(diagnostics.len(), 1);
                assert_eq!(diagnostics[0].severity, Severity::Warning);
            }
            other => panic!("unexpected {other:?}"),
        }
    }

    #[test]
    fn run_returns_a_resolution() {
        let cells = ["a", "b", "c"]
            .iter()
            .map(|c| CellBinding {
                catalyst: (*c).into(),
                cell: "X".into(),
            })
            .collect::<Vec<_>>();
        match run("r1".into(), GOOD, &floors(12.5), &cells) {
            ServerMessage::RunResult { bindings, .. } => {
                assert_eq!(bindings.len(), 1);
                assert!(matches!(bindings[0].outcome, Outcome::Resolved { .. }));
                assert_eq!(bindings[0].record, 1);
            }
            other => panic!("unexpected {other:?}"),
        }
    }

    #[test]
    fn a_declination_is_a_result_not_a_failure() {
        let cells = vec![
            CellBinding { catalyst: "a".into(), cell: "X".into() },
            CellBinding { catalyst: "b".into(), cell: "X".into() },
            CellBinding { catalyst: "c".into(), cell: "Y".into() },
        ];
        match run("r1".into(), GOOD, &floors(12.5), &cells) {
            ServerMessage::RunResult { bindings, .. } => match &bindings[0].outcome {
                Outcome::Declined { cells } => assert_eq!(cells.len(), 2),
                other => panic!("expected a declination, got {other:?}"),
            },
            // the important half: it must NOT arrive as Failed
            other => panic!("declination must not be a failure frame: {other:?}"),
        }
    }

    #[test]
    fn a_type_error_is_a_failure() {
        match run("r1".into(), GOOD, &floors(0.0), &[]) {
            ServerMessage::Failed { message, .. } => assert!(message.contains("positive")),
            other => panic!("unexpected {other:?}"),
        }
    }

    #[test]
    fn analyse_reports_both_regimes_with_their_status() {
        let sub = serde_json::json!({
            "name": "t",
            "records": {
                "r1": [
                    {"uncertainty": 100.0, "label": "A"},
                    {"uncertainty": 60.0,  "label": "B"},
                    {"uncertainty": 40.0,  "label": "C"}
                ],
                "r2": [
                    {"uncertainty": 90.0, "label": "A"},
                    {"uncertainty": 55.0, "label": "B"},
                    {"uncertainty": 38.0, "label": "C"}
                ]
            },
            "floor_stages": {
                "r1": [[12.0,40.0,90.0],[11.0,30.0,70.0,95.0],[10.4,25.0,61.0,88.0]],
                "r2": [[12.0,40.0,90.0],[11.0,30.0,70.0,95.0],[10.4,25.0,61.0,88.0]]
            },
            "estimator": "asymptotic",
            "catalysts": {}
        });

        match analyse("r1".into(), &sub) {
            ServerMessage::AnalysisResult { laws, cascades, .. } => {
                assert_eq!(cascades, 2);
                let inst: Vec<_> = laws.iter().filter(|l| !l.evidential).collect();
                let typed: Vec<_> = laws.iter().filter(|l| l.evidential).collect();
                assert_eq!(inst.len(), 4);
                assert_eq!(typed.len(), 4);

                // the multiplicative instance-specific row is the identity
                let m = inst.iter().find(|l| l.law == "multiplicative").unwrap();
                assert!(m.max_discrepancy < 1e-12, "{}", m.max_discrepancy);
                assert!(!m.evidential);
            }
            other => panic!("unexpected {other:?}"),
        }
    }

    #[test]
    fn hello_is_rejected_outside_the_handshake() {
        let m = dispatch(ClientMessage::Hello {
            token: "x".into(),
            protocol: PROTOCOL_VERSION,
        });
        assert!(matches!(m, ServerMessage::Failed { .. }));
    }

    #[test]
    fn ping_is_answered() {
        let m = dispatch(ClientMessage::Ping {
            request_id: "p".into(),
        });
        assert!(matches!(m, ServerMessage::Pong { .. }));
    }
}
