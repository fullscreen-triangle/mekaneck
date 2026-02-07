//! Virtual Brain CLI
//!
//! Command-line interface for the Virtual Brain computing framework.

use anyhow::Result;
use clap::{Parser, Subcommand};
use std::path::PathBuf;
use vb_validators::ValidationSuite;

#[derive(Parser)]
#[command(name = "vb")]
#[command(about = "Virtual Brain Computing Framework CLI", long_about = None)]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    /// Run validation suite
    Validate {
        /// Output directory for results
        #[arg(short, long, default_value = "results")]
        output: PathBuf,

        /// Validators to skip
        #[arg(short, long)]
        skip: Vec<String>,
    },

    /// Run a simulation
    Simulate {
        /// Simulation duration in seconds
        #[arg(short, long, default_value = "10.0")]
        duration: f64,

        /// Time step in seconds
        #[arg(short = 't', long, default_value = "0.01")]
        dt: f64,

        /// Number of oscillators
        #[arg(short, long, default_value = "100")]
        n_oscillators: usize,

        /// Coupling strength
        #[arg(short, long, default_value = "1.0")]
        coupling: f64,
    },

    /// Display framework information
    Info,
}

fn main() -> Result<()> {
    env_logger::init();

    let cli = Cli::parse();

    match cli.command {
        Commands::Validate { output, skip } => {
            run_validation(&output, &skip)?;
        }
        Commands::Simulate {
            duration,
            dt,
            n_oscillators,
            coupling,
        } => {
            run_simulation(duration, dt, n_oscillators, coupling)?;
        }
        Commands::Info => {
            print_info();
        }
    }

    Ok(())
}

fn run_validation(output_dir: &PathBuf, skip: &[String]) -> Result<()> {
    let skip_refs: Vec<&str> = skip.iter().map(|s| s.as_str()).collect();

    let mut suite = ValidationSuite::new(output_dir);
    let results = suite.run_complete_validation(&skip_refs)?;

    // Calculate overall success
    let mut total = 0;
    let mut passed = 0;
    for result in results.values() {
        total += result.total_claims();
        passed += result.validated_count();
    }

    let rate = if total > 0 {
        passed as f64 / total as f64
    } else {
        0.0
    };

    if rate >= 0.7 {
        std::process::exit(0);
    } else {
        std::process::exit(1);
    }
}

fn run_simulation(duration: f64, dt: f64, n_oscillators: usize, coupling: f64) -> Result<()> {
    use vb_core::types::MentalState;
    use vb_engine::PoincareComputer;

    println!("Running Virtual Brain Simulation");
    println!("================================");
    println!("Duration: {} s", duration);
    println!("Time step: {} s", dt);
    println!("Oscillators: {}", n_oscillators);
    println!("Coupling: {}", coupling);
    println!();

    let mut computer = PoincareComputer::new(n_oscillators, coupling, 5);
    let initial = MentalState::default();

    let states = computer.run_simulation(&initial, duration, dt);

    // Print statistics
    let final_state = states.last().unwrap();
    println!("Simulation Complete");
    println!("==================");
    println!("Final consciousness: {:.4}", final_state.consciousness());
    println!("Final gamma (coherence): {:.4}", final_state.gamma);
    println!("Final gamma_f: {:.4}", final_state.gamma_f);
    println!("Total states recorded: {}", states.len());

    // Compute average consciousness
    let avg_c: f64 = states.iter().map(|s| s.consciousness()).sum::<f64>() / states.len() as f64;
    println!("Average consciousness: {:.4}", avg_c);

    Ok(())
}

fn print_info() {
    println!("Virtual Brain Computing Framework");
    println!("==================================");
    println!("Version: 0.1.0");
    println!("Language: Rust");
    println!();
    println!("Components:");
    println!("  - vb-core: Core types and constants");
    println!("  - vb-operators: Mathematical operators");
    println!("  - vb-engine: Simulation engine");
    println!("  - vb-validators: Validation suite");
    println!();
    println!("Key Features:");
    println!("  - Partition coordinates with C(n) = 2n^2 capacity");
    println!("  - S-entropy space navigation in [0,1]^3");
    println!("  - Ternary addressing with O(log3 n) efficiency");
    println!("  - Kuramoto oscillator dynamics");
    println!("  - Poincare computing paradigm");
    println!();
    println!("Run 'vb validate' to verify the framework.");
    println!("Run 'vb simulate' to run a consciousness simulation.");
}
