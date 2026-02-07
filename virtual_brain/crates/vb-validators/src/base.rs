//! Base Validator: Abstract trait for all validators.

use anyhow::Result;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::path::{Path, PathBuf};

/// Standard validation result structure.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ValidationResult {
    /// Name of the validator
    pub validator_name: String,
    /// Timestamp of validation
    pub timestamp: String,
    /// Parameters used for validation
    pub parameters: HashMap<String, serde_json::Value>,
    /// Detailed results
    pub results: HashMap<String, serde_json::Value>,
    /// Claims that were validated
    pub claims_validated: HashMap<String, bool>,
}

impl ValidationResult {
    /// Check if all claims were validated.
    pub fn overall_success(&self) -> bool {
        self.claims_validated.values().all(|&v| v)
    }

    /// Compute validation success rate.
    pub fn success_rate(&self) -> f64 {
        if self.claims_validated.is_empty() {
            return 0.0;
        }
        let passed = self.claims_validated.values().filter(|&&v| v).count();
        passed as f64 / self.claims_validated.len() as f64
    }

    /// Count of validated claims.
    pub fn validated_count(&self) -> usize {
        self.claims_validated.values().filter(|&&v| v).count()
    }

    /// Total claim count.
    pub fn total_claims(&self) -> usize {
        self.claims_validated.len()
    }
}

/// Abstract trait for Virtual Brain validators.
pub trait Validator: Send + Sync {
    /// Validator name.
    fn name(&self) -> &str;

    /// Output directory for results.
    fn output_dir(&self) -> &Path;

    /// Run validation tests.
    fn run_validation(&mut self) -> Result<ValidationResult>;

    /// Save results to JSON.
    fn save_results(&self, results: &ValidationResult) -> Result<PathBuf> {
        let output_file = self.output_dir().join(format!(
            "{}_results.json",
            self.name().to_lowercase().replace(' ', "_")
        ));

        std::fs::create_dir_all(self.output_dir())?;
        let json = serde_json::to_string_pretty(results)?;
        std::fs::write(&output_file, json)?;

        println!("\n[OK] Results saved to: {}", output_file.display());
        Ok(output_file)
    }

    /// Print validation summary.
    fn print_summary(&self, results: &ValidationResult) {
        println!("\n{}", "=".repeat(70));
        println!("VALIDATION SUMMARY: {}", results.validator_name);
        println!("{}", "=".repeat(70));

        for (claim, validated) in &results.claims_validated {
            let status = if *validated {
                "[OK] VALIDATED"
            } else {
                "[FAIL] FAILED"
            };
            println!("  {}: {}", claim, status);
        }

        let rate = results.success_rate();
        let passed = results.validated_count();
        let total = results.total_claims();
        println!("\nOverall: {}/{} ({:.1}%)", passed, total, rate * 100.0);
        println!("{}", "=".repeat(70));
    }
}

/// Helper to create validation result.
pub fn create_result(
    validator_name: &str,
    parameters: HashMap<String, serde_json::Value>,
    results: HashMap<String, serde_json::Value>,
    claims_validated: HashMap<String, bool>,
) -> ValidationResult {
    ValidationResult {
        validator_name: validator_name.to_string(),
        timestamp: chrono::Local::now().format("%Y-%m-%d %H:%M:%S").to_string(),
        parameters,
        results,
        claims_validated,
    }
}
