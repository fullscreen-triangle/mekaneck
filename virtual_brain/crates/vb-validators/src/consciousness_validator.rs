//! Consciousness Validator: Validates consciousness equations.

use crate::base::{create_result, ValidationResult, Validator};
use anyhow::Result;
use serde_json::json;
use std::collections::HashMap;
use std::path::{Path, PathBuf};
use vb_core::types::MentalState;
use vb_operators::{consciousness, dream, wake};

/// Validates consciousness equations and dynamics.
pub struct ConsciousnessValidator {
    output_dir: PathBuf,
}

impl ConsciousnessValidator {
    /// Create new consciousness validator.
    pub fn new(output_dir: impl AsRef<Path>) -> Self {
        Self {
            output_dir: output_dir.as_ref().to_path_buf(),
        }
    }

    fn test_consciousness_formula(&self) -> (HashMap<String, serde_json::Value>, bool) {
        let test_cases = vec![
            (1.0, 1.0, 1.0, 1.0, 1.0),
            (0.5, 0.5, 0.5, 0.5, 0.0625),
            (1.0, 1.0, 0.8, 0.9, 0.72),
            (0.0, 1.0, 1.0, 1.0, 0.0),
            (1.0, 0.0, 1.0, 1.0, 0.0),
        ];

        let mut all_correct = true;
        let mut tests = Vec::new();

        for (p, t, g, gf, expected) in &test_cases {
            let c = consciousness(*p, *t, *g, *gf);
            let correct = (c - expected).abs() < 1e-10;
            all_correct = all_correct && correct;

            tests.push(json!({
                "p_decay": p,
                "t_decay": t,
                "gamma": g,
                "gamma_f": gf,
                "expected": expected,
                "actual": c,
                "correct": correct
            }));
        }

        let mut results = HashMap::new();
        results.insert("tests".to_string(), json!(tests));
        results.insert("all_correct".to_string(), json!(all_correct));
        (results, all_correct)
    }

    fn test_consciousness_bounds(&self) -> (HashMap<String, serde_json::Value>, bool) {
        let mut all_in_bounds = true;
        let n_tests = 100;

        for _ in 0..n_tests {
            let p = rand::random::<f64>();
            let t = rand::random::<f64>();
            let g = rand::random::<f64>();
            let gf = rand::random::<f64>();

            let c = consciousness(p, t, g, gf);

            if c < 0.0 || c > 1.0 {
                all_in_bounds = false;
                break;
            }
        }

        let mut results = HashMap::new();
        results.insert("n_tests".to_string(), json!(n_tests));
        results.insert("all_in_bounds".to_string(), json!(all_in_bounds));
        (results, all_in_bounds)
    }

    fn test_dream_state(&self) -> (HashMap<String, serde_json::Value>, bool) {
        let state = MentalState::new(0.8, 0.8, 0.0).unwrap();
        let dreaming = dream(&state);

        let c_before = state.consciousness();
        let c_after = dreaming.consciousness();

        let dream_reduces = c_after < 0.01;

        let mut results = HashMap::new();
        results.insert("consciousness_before".to_string(), json!(c_before));
        results.insert("consciousness_after".to_string(), json!(c_after));
        results.insert("dream_reduces_consciousness".to_string(), json!(dream_reduces));
        (results, dream_reduces)
    }

    fn test_awake_state(&self) -> (HashMap<String, serde_json::Value>, bool) {
        let state = MentalState::new(0.8, 0.8, 0.0).unwrap();
        let dreaming = dream(&state);
        let awake = wake(&dreaming, 0.9);

        let c_dream = dreaming.consciousness();
        let c_awake = awake.consciousness();

        let wake_increases = c_awake > c_dream;

        let mut results = HashMap::new();
        results.insert("consciousness_dream".to_string(), json!(c_dream));
        results.insert("consciousness_awake".to_string(), json!(c_awake));
        results.insert("wake_increases_consciousness".to_string(), json!(wake_increases));
        (results, wake_increases)
    }
}

impl Validator for ConsciousnessValidator {
    fn name(&self) -> &str {
        "Consciousness Validator"
    }

    fn output_dir(&self) -> &Path {
        &self.output_dir
    }

    fn run_validation(&mut self) -> Result<ValidationResult> {
        println!("{}", "=".repeat(70));
        println!("CONSCIOUSNESS EQUATIONS VALIDATION");
        println!("{}", "=".repeat(70));

        println!("\n1. Testing consciousness formula C = P * T * gamma * gamma_f...");
        let (formula_results, formula_valid) = self.test_consciousness_formula();
        println!("   Result: {}", if formula_valid { "PASS" } else { "FAIL" });

        println!("2. Testing consciousness bounds [0, 1]...");
        let (bounds_results, bounds_valid) = self.test_consciousness_bounds();
        println!("   Result: {}", if bounds_valid { "PASS" } else { "FAIL" });

        println!("3. Testing dream state (P_decay = 0)...");
        let (dream_results, dream_valid) = self.test_dream_state();
        println!("   Result: {}", if dream_valid { "PASS" } else { "FAIL" });

        println!("4. Testing awake state...");
        let (awake_results, awake_valid) = self.test_awake_state();
        println!("   Result: {}", if awake_valid { "PASS" } else { "FAIL" });

        let mut claims = HashMap::new();
        claims.insert("formula_correct".to_string(), formula_valid);
        claims.insert("bounds_correct".to_string(), bounds_valid);
        claims.insert("dream_works".to_string(), dream_valid);
        claims.insert("awake_works".to_string(), awake_valid);

        let mut all_results = HashMap::new();
        all_results.insert("formula".to_string(), json!(formula_results));
        all_results.insert("bounds".to_string(), json!(bounds_results));
        all_results.insert("dream".to_string(), json!(dream_results));
        all_results.insert("awake".to_string(), json!(awake_results));

        let params = HashMap::new();

        let result = create_result(self.name(), params, all_results, claims);
        self.save_results(&result)?;
        self.print_summary(&result);

        Ok(result)
    }
}
