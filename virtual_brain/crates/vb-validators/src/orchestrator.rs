//! Orchestrator: Runs all validators and produces comprehensive report.

use crate::base::{ValidationResult, Validator};
use crate::consciousness_validator::ConsciousnessValidator;
use crate::kuramoto_validator::KuramotoValidator;
use crate::partition_validator::PartitionValidator;
use anyhow::Result;
use std::collections::HashMap;
use std::path::{Path, PathBuf};
use std::time::Instant;

/// Validation suite that runs all validators.
pub struct ValidationSuite {
    output_dir: PathBuf,
    results: HashMap<String, ValidationResult>,
    start_time: Option<Instant>,
    end_time: Option<Instant>,
}

impl ValidationSuite {
    /// Create new validation suite.
    pub fn new(output_dir: impl AsRef<Path>) -> Self {
        Self {
            output_dir: output_dir.as_ref().to_path_buf(),
            results: HashMap::new(),
            start_time: None,
            end_time: None,
        }
    }

    /// Run complete validation.
    pub fn run_complete_validation(&mut self, skip_validators: &[&str]) -> Result<&HashMap<String, ValidationResult>> {
        println!("\n{}", "=".repeat(70));
        println!("{:^70}", "VIRTUAL BRAIN COMPUTING FRAMEWORK");
        println!("{:^70}", "VALIDATION SUITE (Rust)");
        println!("{}", "=".repeat(70));

        self.start_time = Some(Instant::now());

        // Define validators
        let validators: Vec<(&str, Box<dyn Validator>)> = vec![
            (
                "partition",
                Box::new(PartitionValidator::new(10, self.output_dir.join("partition"))),
            ),
            (
                "kuramoto",
                Box::new(KuramotoValidator::new(100, self.output_dir.join("kuramoto"))),
            ),
            (
                "consciousness",
                Box::new(ConsciousnessValidator::new(self.output_dir.join("consciousness"))),
            ),
        ];

        let total = validators.len();

        for (idx, (name, mut validator)) in validators.into_iter().enumerate() {
            if skip_validators.contains(&name) {
                println!("\n[SKIP] Validator {}/{}: {}", idx + 1, total, name);
                continue;
            }

            println!("\n{}", "=".repeat(70));
            println!("VALIDATOR {}/{}: {}", idx + 1, total, name.to_uppercase());
            println!("{}", "=".repeat(70));

            match validator.run_validation() {
                Ok(result) => {
                    self.results.insert(name.to_string(), result);
                }
                Err(e) => {
                    println!("ERROR in {}: {}", name, e);
                }
            }
        }

        self.end_time = Some(Instant::now());

        // Generate report
        self.generate_report();

        // Save complete results
        self.save_complete_results()?;

        Ok(&self.results)
    }

    fn generate_report(&self) {
        println!("\n{}", "=".repeat(70));
        println!("{:^70}", "VALIDATION REPORT");
        println!("{}", "=".repeat(70));

        let total_time = self
            .end_time
            .and_then(|e| self.start_time.map(|s| e.duration_since(s)))
            .map(|d| d.as_secs_f64())
            .unwrap_or(0.0);

        let total_validators = self.results.len();

        println!("\nExecution Summary:");
        println!("  Total validators: {}", total_validators);
        println!("  Total time: {:.2} seconds", total_time);

        // Count claims
        let mut total_claims = 0;
        let mut validated_claims = 0;

        for result in self.results.values() {
            total_claims += result.total_claims();
            validated_claims += result.validated_count();
        }

        let validation_rate = if total_claims > 0 {
            validated_claims as f64 / total_claims as f64
        } else {
            0.0
        };

        println!("\nValidation Summary:");
        println!("  Total claims: {}", total_claims);
        println!("  Validated: {}", validated_claims);
        println!("  Validation rate: {:.1}%", validation_rate * 100.0);

        let status = if validation_rate >= 0.9 {
            "[OK] EXCELLENT - Framework validated"
        } else if validation_rate >= 0.8 {
            "[OK] GOOD - Most claims validated"
        } else if validation_rate >= 0.7 {
            "[WARN] ACCEPTABLE - Needs review"
        } else {
            "[FAIL] NEEDS WORK - Significant issues"
        };

        println!("\nOverall Status: {}", status);
        println!("{}", "=".repeat(70));
    }

    fn save_complete_results(&self) -> Result<()> {
        std::fs::create_dir_all(&self.output_dir)?;

        let output_file = self.output_dir.join("complete_validation_results.json");

        let total_time = self
            .end_time
            .and_then(|e| self.start_time.map(|s| e.duration_since(s)))
            .map(|d| d.as_secs_f64())
            .unwrap_or(0.0);

        let results_with_metadata = serde_json::json!({
            "metadata": {
                "suite": "Virtual Brain Computing Framework Validation (Rust)",
                "version": "0.1.0",
                "timestamp": chrono::Local::now().format("%Y-%m-%d %H:%M:%S").to_string(),
                "total_time_seconds": total_time,
            },
            "results": self.results,
        });

        let json = serde_json::to_string_pretty(&results_with_metadata)?;
        std::fs::write(&output_file, json)?;

        println!("\n[OK] Complete results saved to: {}", output_file.display());

        Ok(())
    }
}
