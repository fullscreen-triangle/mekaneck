//! The `mekaneck` command-line tool.
//!
//! Runs entirely on the user's machine. Nothing here contacts the network:
//! the web IDE connects *to* this binary over loopback, not the other way
//! round, so analysis data never leaves the host.

use std::collections::BTreeMap;
use std::path::{Path, PathBuf};
use std::process::ExitCode;

use anyhow::{Context, Result};
use clap::{Parser, Subcommand};
use mekaneck_algebra as alg;
use mekaneck_lang as lang;

#[derive(Parser, Debug)]
#[command(
    name = "mekaneck",
    version,
    about = "Individuation-structured inquiry: check and run .mck programs",
    long_about = None
)]
struct Cli {
    #[command(subcommand)]
    command: Command,
}

#[derive(Subcommand, Debug)]
enum Command {
    /// Parse and type-check a program without running it.
    Check {
        file: PathBuf,
        /// Substrate floor, as `NAME=VALUE`. Without it T-Seek-Pos is
        /// reported as unchecked rather than silently assumed.
        #[arg(long = "floor", value_name = "NAME=VALUE")]
        floors: Vec<String>,
        #[arg(long)]
        json: bool,
    },
    /// Run a program against a substrate given as `CATALYST=CELL` pairs.
    Run {
        file: PathBuf,
        #[arg(long = "floor", value_name = "NAME=VALUE")]
        floors: Vec<String>,
        /// Catalyst outcome, as `CATALYST=CELL`.
        #[arg(long = "cell", value_name = "CATALYST=CELL")]
        cells: Vec<String>,
        #[arg(long)]
        json: bool,
    },
    /// Estimate a floor from an expanding family of observations.
    Floor {
        /// JSON file: `{"stages": [[...], [...]]}`.
        file: PathBuf,
        /// Which estimator discharges the obligation. `sample-minimum`
        /// cannot return a non-positive value and so cannot falsify.
        #[arg(long, default_value = "asymptotic")]
        estimator: String,
        #[arg(long)]
        json: bool,
    },
    /// Print the tokens a source file lexes to (for editor development).
    Tokens { file: PathBuf },
    /// Serve the local IDE on loopback and print a pairing token.
    Serve {
        /// Port on 127.0.0.1. 0 asks the OS for a free one.
        #[arg(long, default_value_t = 8731)]
        port: u16,
    },
    /// Analyse a substrate: estimate its floor, extract cascades, and compare
    /// composition laws under both estimation regimes.
    Analyse {
        /// A serialised `Tabular` substrate (JSON).
        file: PathBuf,
        #[arg(long)]
        json: bool,
    },
}

fn parse_pairs(items: &[String], what: &str) -> Result<Vec<(String, String)>> {
    items
        .iter()
        .map(|s| {
            s.split_once('=')
                .map(|(k, v)| (k.trim().to_string(), v.trim().to_string()))
                .with_context(|| format!("{what} must be NAME=VALUE, got {s:?}"))
        })
        .collect()
}

fn floor_values(items: &[String]) -> Result<lang::FloorValues> {
    let mut m = BTreeMap::new();
    for (k, v) in parse_pairs(items, "--floor")? {
        let parsed: f64 = v
            .parse()
            .with_context(|| format!("floor for {k:?} is not a number: {v:?}"))?;
        m.insert(k, parsed);
    }
    Ok(m)
}

/// Render a diagnostic as `file:line:col: severity: message`.
fn render(path: &Path, src: &str, d: &lang::Diagnostic) -> String {
    let (line, col) = d.span.line_col(src);
    let sev = match d.severity {
        lang::Severity::Error => "error",
        lang::Severity::Warning => "warning",
    };
    format!("{}:{}:{}: {}: {}", path.display(), line, col, sev, d.message)
}

fn cmd_check(file: PathBuf, floors: Vec<String>, json: bool) -> Result<ExitCode> {
    let src = std::fs::read_to_string(&file)
        .with_context(|| format!("reading {}", file.display()))?;
    let fv = floor_values(&floors)?;
    let diags = lang::diagnose(&src, &fv);

    let n_err = diags
        .iter()
        .filter(|d| d.severity == lang::Severity::Error)
        .count();

    if json {
        println!("{}", serde_json::to_string_pretty(&diags)?);
    } else if diags.is_empty() {
        println!("{}: ok", file.display());
    } else {
        for d in &diags {
            println!("{}", render(&file, &src, d));
        }
    }
    Ok(if n_err > 0 {
        ExitCode::FAILURE
    } else {
        ExitCode::SUCCESS
    })
}

fn cmd_run(
    file: PathBuf,
    floors: Vec<String>,
    cells: Vec<String>,
    json: bool,
) -> Result<ExitCode> {
    let src = std::fs::read_to_string(&file)
        .with_context(|| format!("reading {}", file.display()))?;
    let fv = floor_values(&floors)?;

    let prog = match lang::parse(&src) {
        Ok(p) => p,
        Err(e) => {
            eprintln!("{}", render(&file, &src, &to_diag(&e)));
            return Ok(ExitCode::FAILURE);
        }
    };
    if let Err(e) = lang::typecheck(&prog, &fv) {
        eprintln!("{}", render(&file, &src, &to_diag(&e)));
        return Ok(ExitCode::FAILURE);
    }

    let mut sub = lang::FixedSubstrate::new();
    for (c, cell) in parse_pairs(&cells, "--cell")? {
        sub = sub.with(&c, &cell);
    }

    let mut out = Vec::new();
    for l in prog.lets() {
        match lang::eval_seek(&l.seek, &sub) {
            Ok(ev) => out.push((l.name.clone(), ev)),
            Err(e) => {
                eprintln!("{}", render(&file, &src, &to_diag(&e)));
                return Ok(ExitCode::FAILURE);
            }
        }
    }

    if json {
        let payload: Vec<_> = out
            .iter()
            .map(|(n, e)| serde_json::json!({ "binding": n, "evaluation": e }))
            .collect();
        println!("{}", serde_json::to_string_pretty(&payload)?);
    } else {
        for (name, ev) in &out {
            match &ev.outcome {
                alg::Outcome::Resolved { cell } => {
                    println!("{name}: resolved {cell}  (record {})", ev.record);
                }
                alg::Outcome::Declined { cells } => {
                    // A declination is a normal termination, not an error:
                    // it is one of the two outcomes of Thm 6.7.
                    println!(
                        "{name}: declined, {} incompatible cells  (record {})",
                        cells.len(),
                        ev.record
                    );
                    for c in cells {
                        let by: Vec<&str> = ev
                            .trace
                            .iter()
                            .filter(|s| &s.cell == c)
                            .map(|s| s.catalyst.as_str())
                            .collect();
                        println!("    {c}  via {}", by.join(", "));
                    }
                }
            }
        }
    }
    Ok(ExitCode::SUCCESS)
}

fn to_diag(e: &lang::Error) -> lang::Diagnostic {
    lang::Diagnostic {
        message: e.to_string(),
        span: e.span().unwrap_or(lang::Span::new(0, 0)),
        severity: lang::Severity::Error,
    }
}

#[derive(serde::Deserialize)]
struct Stages {
    stages: Vec<Vec<f64>>,
}

fn cmd_floor(file: PathBuf, estimator: String, json: bool) -> Result<ExitCode> {
    let text = std::fs::read_to_string(&file)
        .with_context(|| format!("reading {}", file.display()))?;
    let stages: Stages = serde_json::from_str(&text)
        .with_context(|| format!("{} must be {{\"stages\": [[..]]}}", file.display()))?;

    let est = match estimator.as_str() {
        "asymptotic" => alg::FloorEstimator::Asymptotic,
        "sample-minimum" | "sample_minimum" => alg::FloorEstimator::SampleMinimum,
        other => anyhow::bail!("unknown estimator {other:?}; expected asymptotic or sample-minimum"),
    };

    let mut fam = alg::ExpandingFamily::new();
    for s in stages.stages {
        fam.push_stage(s)?;
    }
    let est = fam.estimate(est)?;

    if json {
        println!("{}", serde_json::to_string_pretty(&est)?);
    } else {
        println!("floor: {:.6}", est.value);
        println!("estimator: {:?}", est.estimator);
        println!("stages: {}  observations: {}", est.stages, est.observations);
        if !est.estimator.is_falsifiable() {
            // Say so unprompted: a positive value from this estimator is not
            // evidence, because it could not have come out otherwise.
            println!(
                "note: this estimator is bounded below by the sample and cannot return a \
                 non-positive value, so its positivity is not evidence for a positive floor"
            );
        } else if est.falsifies_positivity() {
            println!("note: this estimate contradicts a positive floor");
        } else if est.is_indistinguishable_from_zero(alg::ZERO_TOLERANCE) {
            // A positive sign is not on its own evidence for a positive
            // floor when the magnitude is within noise of zero.
            println!(
                "note: this estimate is within {:e} of zero and does not support a positive floor, despite its sign",
                alg::ZERO_TOLERANCE
            );
        }
    }
    Ok(ExitCode::SUCCESS)
}

fn cmd_tokens(file: PathBuf) -> Result<ExitCode> {
    let src = std::fs::read_to_string(&file)
        .with_context(|| format!("reading {}", file.display()))?;
    match lang::lex(&src) {
        Ok(toks) => {
            println!("{}", serde_json::to_string_pretty(&toks)?);
            Ok(ExitCode::SUCCESS)
        }
        Err(e) => {
            eprintln!("{}", render(&file, &src, &to_diag(&e)));
            Ok(ExitCode::FAILURE)
        }
    }
}

/// Analyse a substrate end to end.
///
/// Reports the floor with its evidential status, the type separation η, and
/// the law comparison under *both* estimation regimes — the instance-specific
/// one is shown precisely so that its perfect agreement can be seen for what
/// it is rather than mistaken for a result.
fn cmd_analyse(file: PathBuf, json: bool) -> Result<ExitCode> {
    use mekaneck_substrates::{cascade_for, Substrate, Tabular};

    let text = std::fs::read_to_string(&file)
        .with_context(|| format!("reading {}", file.display()))?;
    let sub: Tabular = serde_json::from_str(&text)
        .with_context(|| format!("{} is not a serialised substrate", file.display()))?;

    let mut cascades = Vec::new();
    let mut floors = Vec::new();
    for r in sub.receivers() {
        let f = sub.floor(&r)?;
        floors.push((r.clone(), f));
        match cascade_for(&sub, &r) {
            Ok(c) => cascades.push(c),
            Err(e) => eprintln!("warning: receiver {r:?} yielded no cascade: {e}"),
        }
    }
    if cascades.is_empty() {
        anyhow::bail!("no receiver produced a cascade");
    }

    let sep = alg::separation(&cascades)?;
    let averages = alg::TypeAverages::fit(&cascades)?;

    // Both regimes, so the contrast is visible.
    let mut rows = Vec::new();
    for law in alg::Law::ALL {
        for est in [alg::Estimation::InstanceSpecific, alg::Estimation::TypeAveraged] {
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
            rows.push(serde_json::json!({
                "law": law.name(),
                "estimation": if matches!(est, alg::Estimation::TypeAveraged)
                    { "type_averaged" } else { "instance_specific" },
                "evidential": est.has_null_hypothesis(),
                "max_discrepancy": worst,
                "pearson_r": alg::pearson(&preds, &meas),
                "rmse": alg::rmse(&preds, &meas),
            }));
        }
    }

    if json {
        println!(
            "{}",
            serde_json::to_string_pretty(&serde_json::json!({
                "substrate": sub.name(),
                "receivers": floors.iter().map(|(r, f)| serde_json::json!({
                    "receiver": r,
                    "floor": f.value,
                    "estimator": f.estimator,
                    "falsifiable": f.estimator.is_falsifiable(),
                    "supports_positive_floor": f.supports_positive_floor(alg::ZERO_TOLERANCE),
                })).collect::<Vec<_>>(),
                "cascades": cascades.len(),
                "separation": sep,
                "laws": rows,
            }))?
        );
        return Ok(ExitCode::SUCCESS);
    }

    println!("substrate: {}", sub.name());
    for (r, f) in &floors {
        print!("  {r}: floor {:.6} [{:?}]", f.value, f.estimator);
        if !f.estimator.is_falsifiable() {
            print!("  (cannot falsify: positivity is not evidence)");
        } else if !f.supports_positive_floor(alg::ZERO_TOLERANCE) {
            print!("  (does not support a positive floor)");
        }
        println!();
    }
    println!(
        "\ncascades: {}   types: {}   eta: {:.4}{}",
        cascades.len(),
        sep.n_types,
        sep.eta,
        if sep.is_informative() {
            ""
        } else {
            "  <- below threshold: a law comparison here cannot adjudicate the typing"
        }
    );

    println!("\n{:<16} {:<18} {:>10} {:>10} {:>8}", "law", "estimation", "r", "rmse", "evid");
    for row in &rows {
        println!(
            "{:<16} {:<18} {:>10} {:>10} {:>8}",
            row["law"].as_str().unwrap_or("?"),
            row["estimation"].as_str().unwrap_or("?"),
            row["pearson_r"].as_f64().map(|v| format!("{v:.4}")).unwrap_or_else(|| "-".into()),
            row["rmse"].as_f64().map(|v| format!("{v:.4}")).unwrap_or_else(|| "-".into()),
            if row["evidential"].as_bool().unwrap_or(false) { "yes" } else { "NO" },
        );
    }
    println!(
        "\nRows marked evid=NO are algebraic identities: under instance-specific\n\
         estimation the prediction and the measurement are the same expression,\n\
         so their agreement is not evidence about the process."
    );
    Ok(ExitCode::SUCCESS)
}

/// Start the loopback server.
///
/// The token is printed once, here, and never written to disk. Restarting the
/// binary invalidates it, which is the behaviour we want from a pairing secret
/// rather than a credential.
fn cmd_serve(port: u16) -> Result<ExitCode> {
    use mekaneck_server::{serve_local, Token};

    let token = Token::generate()?;
    println!("mekaneck is listening on http://127.0.0.1:{port}");
    println!();
    println!("  token: {}", token.expose());
    println!();
    println!("Paste that token into the IDE to pair this browser with this binary.");
    println!("Nothing leaves this machine: the browser connects to you, not the other way round.");
    println!("The token is not stored; restarting invalidates it.");
    println!();
    println!("Press Ctrl-C to stop.");

    let rt = tokio::runtime::Runtime::new()?;
    rt.block_on(serve_local(token, port))?;
    Ok(ExitCode::SUCCESS)
}

fn main() -> Result<ExitCode> {
    match Cli::parse().command {
        Command::Check { file, floors, json } => cmd_check(file, floors, json),
        Command::Run {
            file,
            floors,
            cells,
            json,
        } => cmd_run(file, floors, cells, json),
        Command::Floor {
            file,
            estimator,
            json,
        } => cmd_floor(file, estimator, json),
        Command::Tokens { file } => cmd_tokens(file),
        Command::Analyse { file, json } => cmd_analyse(file, json),
        Command::Serve { port } => cmd_serve(port),
    }
}
