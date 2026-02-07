//! Partition Validator: Validates partition coordinate system.

use crate::base::{create_result, ValidationResult, Validator};
use anyhow::Result;
use serde_json::json;
use std::collections::HashMap;
use std::path::{Path, PathBuf};
use vb_core::types::PartitionCoord;
use vb_operators::partition_ops::{capacity, d_cat};

/// Validates partition coordinate system properties.
pub struct PartitionValidator {
    n_max: i32,
    output_dir: PathBuf,
}

impl PartitionValidator {
    /// Create new partition validator.
    pub fn new(n_max: i32, output_dir: impl AsRef<Path>) -> Self {
        Self {
            n_max,
            output_dir: output_dir.as_ref().to_path_buf(),
        }
    }

    fn test_capacity_formula(&self) -> (HashMap<String, serde_json::Value>, bool) {
        let mut tests = Vec::new();
        let mut all_correct = true;

        for n in 1..=self.n_max {
            let expected = 2 * n * n;
            let actual = capacity(n).unwrap();
            let correct = expected == actual;
            all_correct = all_correct && correct;

            tests.push(json!({
                "n": n,
                "expected": expected,
                "actual": actual,
                "correct": correct
            }));
        }

        let mut results = HashMap::new();
        results.insert("tests".to_string(), json!(tests));
        results.insert("all_correct".to_string(), json!(all_correct));
        (results, all_correct)
    }

    fn test_total_capacity(&self) -> (HashMap<String, serde_json::Value>, bool) {
        let mut tests = Vec::new();
        let mut all_correct = true;

        for n_max in 1..=self.n_max {
            let expected: i64 = (1..=n_max).map(|i| 2 * i as i64 * i as i64).sum();
            let actual = PartitionCoord::total_capacity(n_max);
            let correct = expected == actual;
            all_correct = all_correct && correct;

            tests.push(json!({
                "n_max": n_max,
                "expected": expected,
                "actual": actual,
                "correct": correct
            }));
        }

        let mut results = HashMap::new();
        results.insert("tests".to_string(), json!(tests));
        results.insert("all_correct".to_string(), json!(all_correct));
        (results, all_correct)
    }

    fn test_linear_index_bijection(&self) -> (HashMap<String, serde_json::Value>, bool) {
        let total = PartitionCoord::total_capacity(self.n_max);
        let mut all_bijective = true;
        let test_count = total.min(100);

        for idx in 0..test_count {
            if let Ok(coord) = PartitionCoord::from_linear_index(idx) {
                if coord.to_linear_index() != idx {
                    all_bijective = false;
                    break;
                }
            } else {
                all_bijective = false;
                break;
            }
        }

        let mut results = HashMap::new();
        results.insert("total_states".to_string(), json!(total));
        results.insert("tested_states".to_string(), json!(test_count));
        results.insert("all_bijective".to_string(), json!(all_bijective));
        (results, all_bijective)
    }

    fn test_distance_symmetry(&self) -> (HashMap<String, serde_json::Value>, bool) {
        let coords: Vec<_> = PartitionCoord::iter_all(self.n_max.min(4)).take(20).collect();
        let mut symmetric = true;
        let mut n_tests = 0;

        'outer: for (i, c1) in coords.iter().enumerate() {
            for c2 in coords.iter().skip(i + 1) {
                let d12 = d_cat(c1, c2);
                let d21 = d_cat(c2, c1);

                if (d12 - d21).abs() > 1e-10 {
                    symmetric = false;
                    break 'outer;
                }
                n_tests += 1;
            }
        }

        let mut results = HashMap::new();
        results.insert("n_tests".to_string(), json!(n_tests));
        results.insert("symmetric".to_string(), json!(symmetric));
        (results, symmetric)
    }
}

impl Validator for PartitionValidator {
    fn name(&self) -> &str {
        "Partition Validator"
    }

    fn output_dir(&self) -> &Path {
        &self.output_dir
    }

    fn run_validation(&mut self) -> Result<ValidationResult> {
        println!("{}", "=".repeat(70));
        println!("PARTITION COORDINATE VALIDATION");
        println!("{}", "=".repeat(70));

        println!("\n1. Testing capacity formula C(n) = 2n^2...");
        let (capacity_results, capacity_valid) = self.test_capacity_formula();
        println!("   Result: {}", if capacity_valid { "PASS" } else { "FAIL" });

        println!("2. Testing total capacity formula...");
        let (total_results, total_valid) = self.test_total_capacity();
        println!("   Result: {}", if total_valid { "PASS" } else { "FAIL" });

        println!("3. Testing linear index bijection...");
        let (bijection_results, bijection_valid) = self.test_linear_index_bijection();
        println!("   Result: {}", if bijection_valid { "PASS" } else { "FAIL" });

        println!("4. Testing distance symmetry...");
        let (symmetry_results, symmetry_valid) = self.test_distance_symmetry();
        println!("   Result: {}", if symmetry_valid { "PASS" } else { "FAIL" });

        let mut claims = HashMap::new();
        claims.insert("capacity_formula_correct".to_string(), capacity_valid);
        claims.insert("total_capacity_correct".to_string(), total_valid);
        claims.insert("linear_index_bijective".to_string(), bijection_valid);
        claims.insert("distance_symmetric".to_string(), symmetry_valid);

        let mut all_results = HashMap::new();
        all_results.insert("capacity".to_string(), json!(capacity_results));
        all_results.insert("total_capacity".to_string(), json!(total_results));
        all_results.insert("bijection".to_string(), json!(bijection_results));
        all_results.insert("symmetry".to_string(), json!(symmetry_results));

        let mut params = HashMap::new();
        params.insert("n_max".to_string(), json!(self.n_max));

        let result = create_result(self.name(), params, all_results, claims);
        self.save_results(&result)?;
        self.print_summary(&result);

        Ok(result)
    }
}
