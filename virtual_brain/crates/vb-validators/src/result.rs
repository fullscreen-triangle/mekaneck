//! Validation result types.

use serde::{Deserialize, Serialize};
use std::collections::HashMap;

/// Standard validation result structure.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ValidationResult {
    /// Name of the validator
    pub validator_name: String,
    /// Timestamp of validation
    pub timestamp: String,
    /// Parameters used
    pub parameters: HashMap<String, serde_json::Value>,
    /// Test results
    pub results: HashMap<String, serde_json::Value>,
    /// Claims validated (claim_name -> passed)
    pub claims_validated: HashMap<String, bool>,
}

impl ValidationResult {
    /// Create new validation result.
    pub fn new(validator_name: &str) -> Self {
        Self {
            validator_name: validator_name.to_string(),
            timestamp: chrono::Local::now().format("%Y-%m-%d %H:%M:%S").to_string(),
            parameters: HashMap::new(),
            results: HashMap::new(),
            claims_validated: HashMap::new(),
        }
    }

    /// Check if all claims validated.
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

    /// Add a parameter.
    pub fn add_parameter(&mut self, key: &str, value: impl Serialize) {
        self.parameters
            .insert(key.to_string(), serde_json::to_value(value).unwrap());
    }

    /// Add a result.
    pub fn add_result(&mut self, key: &str, value: impl Serialize) {
        self.results
            .insert(key.to_string(), serde_json::to_value(value).unwrap());
    }

    /// Add a claim validation.
    pub fn add_claim(&mut self, claim: &str, passed: bool) {
        self.claims_validated.insert(claim.to_string(), passed);
    }

    /// Get summary string.
    pub fn summary(&self) -> String {
        let passed = self.claims_validated.values().filter(|&&v| v).count();
        let total = self.claims_validated.len();
        format!(
            "{}: {}/{} claims ({:.1}%)",
            self.validator_name,
            passed,
            total,
            self.success_rate() * 100.0
        )
    }
}

impl Default for ValidationResult {
    fn default() -> Self {
        Self::new("unnamed")
    }
}
