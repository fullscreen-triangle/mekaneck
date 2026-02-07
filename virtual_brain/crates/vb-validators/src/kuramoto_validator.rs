//! Kuramoto Validator: Validates Kuramoto dynamics.

use crate::base::{create_result, ValidationResult, Validator};
use anyhow::Result;
use serde_json::json;
use std::collections::HashMap;
use std::path::{Path, PathBuf};
use vb_operators::{
    critical_coupling, kuramoto, phase_lock, simulate_kuramoto, variance, KuramotoState,
};

/// Validates Kuramoto oscillator dynamics.
pub struct KuramotoValidator {
    n_oscillators: usize,
    output_dir: PathBuf,
}

impl KuramotoValidator {
    /// Create new Kuramoto validator.
    pub fn new(n_oscillators: usize, output_dir: impl AsRef<Path>) -> Self {
        Self {
            n_oscillators,
            output_dir: output_dir.as_ref().to_path_buf(),
        }
    }

    fn test_phase_coherence_bounds(&self) -> (HashMap<String, serde_json::Value>, bool) {
        let mut all_valid = true;
        let n_tests = 100;

        for _ in 0..n_tests {
            let state = KuramotoState::random(self.n_oscillators, 10.0, 1.0, 0.5);
            let (r, _) = phase_lock(&state.phases);

            if r < 0.0 || r > 1.0 {
                all_valid = false;
                break;
            }
        }

        let mut results = HashMap::new();
        results.insert("n_tests".to_string(), json!(n_tests));
        results.insert("all_in_bounds".to_string(), json!(all_valid));
        (results, all_valid)
    }

    fn test_synchronization_onset(&self) -> (HashMap<String, serde_json::Value>, bool) {
        let frequency_std = 1.0;
        let k_c = critical_coupling(frequency_std, self.n_oscillators);

        // Below critical coupling
        let state_below = KuramotoState::random(self.n_oscillators, 10.0, frequency_std, k_c * 0.5);
        let (_, r_below, _) = simulate_kuramoto(&state_below, 10.0, 0.01);
        let final_r_below = r_below[r_below.len() - 1];

        // Above critical coupling
        let state_above = KuramotoState::random(self.n_oscillators, 10.0, frequency_std, k_c * 2.0);
        let (_, r_above, _) = simulate_kuramoto(&state_above, 10.0, 0.01);
        let final_r_above = r_above[r_above.len() - 1];

        let sync_below = final_r_below < 0.5;
        let sync_above = final_r_above > 0.5;

        let mut results = HashMap::new();
        results.insert("critical_coupling".to_string(), json!(k_c));
        results.insert("r_below_critical".to_string(), json!(final_r_below));
        results.insert("r_above_critical".to_string(), json!(final_r_above));
        results.insert("desync_below_critical".to_string(), json!(sync_below));
        results.insert("sync_above_critical".to_string(), json!(sync_above));

        (results, sync_below && sync_above)
    }

    fn test_order_parameter_convergence(&self) -> (HashMap<String, serde_json::Value>, bool) {
        let state = KuramotoState::random(self.n_oscillators, 10.0, 0.5, 2.0);
        let (_, r_values, _) = simulate_kuramoto(&state, 20.0, 0.01);

        // Check if variance decreases over time
        let n = r_values.len();
        let first_half = r_values.slice(ndarray::s![..n / 2]).to_owned();
        let second_half = r_values.slice(ndarray::s![n / 2..]).to_owned();

        let var_first = variance(&first_half);
        let var_second = variance(&second_half);

        let converges = var_second < var_first || var_second < 0.01;

        let mut results = HashMap::new();
        results.insert("variance_first_half".to_string(), json!(var_first));
        results.insert("variance_second_half".to_string(), json!(var_second));
        results.insert("converges".to_string(), json!(converges));

        (results, converges)
    }
}

impl Validator for KuramotoValidator {
    fn name(&self) -> &str {
        "Kuramoto Validator"
    }

    fn output_dir(&self) -> &Path {
        &self.output_dir
    }

    fn run_validation(&mut self) -> Result<ValidationResult> {
        println!("{}", "=".repeat(70));
        println!("KURAMOTO DYNAMICS VALIDATION");
        println!("{}", "=".repeat(70));

        println!("\n1. Testing phase coherence bounds R in [0, 1]...");
        let (bounds_results, bounds_valid) = self.test_phase_coherence_bounds();
        println!("   Result: {}", if bounds_valid { "PASS" } else { "FAIL" });

        println!("2. Testing synchronization onset at critical coupling...");
        let (sync_results, sync_valid) = self.test_synchronization_onset();
        println!("   Result: {}", if sync_valid { "PASS" } else { "FAIL" });

        println!("3. Testing order parameter convergence...");
        let (conv_results, conv_valid) = self.test_order_parameter_convergence();
        println!("   Result: {}", if conv_valid { "PASS" } else { "FAIL" });

        let mut claims = HashMap::new();
        claims.insert("phase_coherence_bounded".to_string(), bounds_valid);
        claims.insert("sync_above_critical".to_string(), sync_valid);
        claims.insert("order_param_converges".to_string(), conv_valid);

        let mut all_results = HashMap::new();
        all_results.insert("bounds".to_string(), json!(bounds_results));
        all_results.insert("synchronization".to_string(), json!(sync_results));
        all_results.insert("convergence".to_string(), json!(conv_results));

        let mut params = HashMap::new();
        params.insert("n_oscillators".to_string(), json!(self.n_oscillators));

        let result = create_result(self.name(), params, all_results, claims);
        self.save_results(&result)?;
        self.print_summary(&result);

        Ok(result)
    }
}
