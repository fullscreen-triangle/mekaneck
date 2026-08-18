//! Generate the shared diagnostic fixtures.
//!
//! The TypeScript mirror in `web/src/languages/mekaneck/` reimplements
//! lex/parse/typecheck so the editor can mark errors without a round trip.
//! Two front halves drift, and a diagnostic that differs between the editor
//! and the binary is worse than no editor diagnostic at all — so both
//! implementations are checked against one file of cases produced here.
//!
//! Regenerate with:
//!
//! ```text
//! cargo test -p mekaneck-lang --test fixtures -- --ignored
//! ```

use std::collections::BTreeMap;
use std::path::PathBuf;

use mekaneck_lang as lang;
use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize)]
struct Case {
    /// Short identifier, used in test output on both sides.
    name: String,
    /// Why this case exists — kept in the fixture so a failure explains
    /// itself without cross-referencing the papers.
    rationale: String,
    source: String,
    floors: BTreeMap<String, f64>,
    expected: Vec<ExpectedDiagnostic>,
}

#[derive(Debug, Serialize, Deserialize)]
struct ExpectedDiagnostic {
    severity: String,
    line: usize,
    column: usize,
    /// A substring the message must contain. Full messages are wording, and
    /// wording should be free to improve; the *substance* is pinned.
    message_contains: String,
}

fn fixtures_path() -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("../../web/src/languages/mekaneck/fixtures.json")
}

const SUBSTRATE: &str =
    "substrate Osc { receivers : r(); observable : o(); events : e(); floor : asymptotic(); }";

fn triad() -> String {
    [
        "catalyst a : f() independent b, c;",
        "catalyst b : g() independent a, c;",
        "catalyst c : h() independent a, b;",
    ]
    .join("\n")
}

fn cases() -> Vec<(&'static str, &'static str, String, f64)> {
    let ok = format!(
        "{SUBSTRATE}\n{}\nlet x = seek t() excluding rest() via (a, b, c) until closure;\nreport x;",
        triad()
    );
    vec![
        (
            "well_formed",
            "A conforming program produces no diagnostics at all.",
            ok.clone(),
            12.5,
        ),
        (
            "missing_exclusion",
            "Thm 4.3: a positive description alone does not determine a target, \
             so a seek without `excluding` is a form the language does not contain. \
             Rejected at parse time, before typing.",
            ok.replace("excluding rest() ", ""),
            12.5,
        ),
        (
            "zero_floor",
            "T-Seek-Pos: a program may not assert an attainable zero residual.",
            ok.clone(),
            0.0,
        ),
        (
            "negative_floor",
            "T-Seek-Pos again, with a floor below zero rather than at it.",
            ok.clone(),
            -3.0,
        ),
        (
            "two_catalysts",
            "T-Seek-Coh: no support structure shorter than three survives the \
             loss of a member (a 1-cycle is vacuous, a 2-cycle collapses).",
            ok.replace("via (a, b, c)", "via (a, b)"),
            12.5,
        ),
        (
            "not_mutually_independent",
            "T-Seek-Coh checks the independence relation, not merely the count: \
             three catalysts that are not pairwise declared independent fail.",
            format!(
                "{SUBSTRATE}\ncatalyst a : f() independent b, c;\ncatalyst b : g() independent a, c;\ncatalyst c : h();\nlet x = seek t() excluding rest() via (a, b, c) until closure;\nreport x;"
            ),
            12.5,
        ),
        (
            "unknown_catalyst_in_via",
            "A via clause naming a catalyst that was never declared.",
            ok.replace("via (a, b, c)", "via (a, b, zz)"),
            12.5,
        ),
        (
            "duplicate_catalyst_in_via",
            "Naming one catalyst twice does not make a triad.",
            ok.replace("via (a, b, c)", "via (a, a, b)"),
            12.5,
        ),
        (
            "independence_names_unknown",
            "An independence declaration referring to a catalyst that does not \
             exist is unverifiable in a way the checker can detect.",
            ok.replace(
                "catalyst a : f() independent b, c;",
                "catalyst a : f() independent b, ghost;",
            ),
            12.5,
        ),
        (
            "report_unbound",
            "Reporting a name that was never bound.",
            ok.replace("report x;", "report nope;"),
            12.5,
        ),
        (
            "no_substrate",
            "Without a substrate there is no floor obligation for a seek to satisfy.",
            format!(
                "{}\nlet x = seek t() excluding rest() via (a, b, c) until closure;\nreport x;",
                triad()
            ),
            12.5,
        ),
        (
            "missing_substrate_field",
            "The four obligations are positional; a missing one is named.",
            format!(
                "substrate Osc {{ receivers : r(); observable : o(); floor : f(); }}\n{}\nlet x = seek t() excluding rest() via (a, b, c) until closure;\nreport x;",
                triad()
            ),
            12.5,
        ),
        (
            "unterminated_string",
            "Lexical: a string literal running to end of line.",
            format!(
                "{}\nlet x = seek t(\"open) excluding rest() until closure;\nreport x;",
                SUBSTRATE
            ),
            12.5,
        ),
        (
            "unexpected_character",
            "Lexical: a character no token may begin with.",
            format!("{SUBSTRATE}\nlet x @ y;"),
            12.5,
        ),
        (
            "no_via_clause_is_legal",
            "T-Seek-Coh applies only to an explicit chain, so omitting `via` is \
             well typed — the rule constrains what is named, not that anything is.",
            format!(
                "{SUBSTRATE}\nlet x = seek t() excluding rest() until closure;\nreport x;"
            ),
            12.5,
        ),
    ]
}

/// Write the fixture file. Ignored by default so a normal `cargo test` does
/// not rewrite a checked-in artefact.
#[test]
#[ignore = "regenerates a checked-in file; run explicitly"]
fn regenerate_fixtures() {
    let mut out = Vec::new();

    for (name, rationale, source, floor) in cases() {
        let mut floors = BTreeMap::new();
        floors.insert("Osc".to_string(), floor);

        let expected = lang::diagnose(&source, &floors)
            .into_iter()
            .map(|d| {
                let (line, column) = d.span.line_col(&source);
                // Pin a distinctive fragment rather than the whole message.
                let msg = d.message.to_lowercase();
                let key = ["excluding", "positive", "catalyst", "independent", "bound",
                           "substrate", "string", "character", "events", "unchecked"]
                    .iter()
                    .find(|k| msg.contains(**k))
                    .map(|k| k.to_string())
                    .unwrap_or_else(|| {
                        msg.split_whitespace().take(3).collect::<Vec<_>>().join(" ")
                    });
                ExpectedDiagnostic {
                    severity: match d.severity {
                        lang::Severity::Error => "error",
                        lang::Severity::Warning => "warning",
                    }
                    .to_string(),
                    line,
                    column,
                    message_contains: key,
                }
            })
            .collect();

        out.push(Case {
            name: name.to_string(),
            rationale: rationale.to_string(),
            source,
            floors,
            expected,
        });
    }

    let path = fixtures_path();
    std::fs::create_dir_all(path.parent().expect("parent")).expect("mkdir");
    std::fs::write(&path, serde_json::to_string_pretty(&out).expect("serialise"))
        .expect("write fixtures");
    eprintln!("wrote {} cases to {}", out.len(), path.display());
}

/// The Rust side of the shared suite: every fixture must still reproduce.
///
/// This runs on every `cargo test`, so a change to the checker that alters a
/// diagnostic fails here — and the same file fails in the TypeScript suite,
/// which is the point.
#[test]
fn rust_reproduces_the_fixtures() {
    let path = fixtures_path();
    let text = std::fs::read_to_string(&path).unwrap_or_else(|e| {
        panic!(
            "{} missing ({e}). Run: cargo test -p mekaneck-lang --test fixtures -- --ignored",
            path.display()
        )
    });
    let cases: Vec<Case> = serde_json::from_str(&text).expect("parse fixtures");
    assert!(!cases.is_empty(), "fixture file is empty");

    for case in &cases {
        let got = lang::diagnose(&case.source, &case.floors);
        assert_eq!(
            got.len(),
            case.expected.len(),
            "case {:?}: expected {} diagnostics, got {} ({:?})\nrationale: {}",
            case.name,
            case.expected.len(),
            got.len(),
            got.iter().map(|d| &d.message).collect::<Vec<_>>(),
            case.rationale,
        );

        for (g, e) in got.iter().zip(&case.expected) {
            let (line, column) = g.span.line_col(&case.source);
            let sev = match g.severity {
                lang::Severity::Error => "error",
                lang::Severity::Warning => "warning",
            };
            assert_eq!(sev, e.severity, "case {:?}: severity", case.name);
            assert_eq!(line, e.line, "case {:?}: line", case.name);
            assert_eq!(column, e.column, "case {:?}: column", case.name);
            assert!(
                g.message.to_lowercase().contains(&e.message_contains),
                "case {:?}: message {:?} does not contain {:?}",
                case.name,
                g.message,
                e.message_contains
            );
        }
    }
}
