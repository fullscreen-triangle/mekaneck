//! Poincare Operators: COMPLETE, TARGET, SATISFY, EQUILIBRIUM.
//!
//! Implements backward constraint satisfaction for Poincare computing.

use serde::{Deserialize, Serialize};
use vb_core::types::{MentalState, SCoord};

const EPSILON: f64 = 1e-10;

/// Result of a completion operation.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CompletionResult {
    /// Whether completion succeeded
    pub success: bool,
    /// Final state after completion
    pub final_state: SCoord,
    /// Number of iterations
    pub iterations: usize,
    /// Trajectory during completion
    pub trajectory: Vec<SCoord>,
    /// Constraint violations over time
    pub constraint_violations: Vec<f64>,
}

/// COMPLETE operator: Satisfy constraints through gradient descent.
pub fn complete<F>(
    partial_state: &SCoord,
    constraints: &[F],
    max_iterations: usize,
    tolerance: f64,
    learning_rate: f64,
) -> CompletionResult
where
    F: Fn(&SCoord) -> f64,
{
    let mut state = *partial_state;
    let mut trajectory = vec![state];
    let mut violations = Vec::new();

    for iter in 0..max_iterations {
        // Compute total constraint violation
        let total_violation: f64 = constraints.iter().map(|c| c(&state).abs()).sum();
        violations.push(total_violation);

        if total_violation < tolerance {
            return CompletionResult {
                success: true,
                final_state: state,
                iterations: iter,
                trajectory,
                constraint_violations: violations,
            };
        }

        // Compute gradient of constraint violation
        let grad = compute_constraint_gradient(&state, constraints, 1e-6);

        // Update state
        state = state.update(
            -learning_rate * grad[0],
            -learning_rate * grad[1],
            -learning_rate * grad[2],
        );

        trajectory.push(state);
    }

    let final_violation: f64 = constraints.iter().map(|c| c(&state).abs()).sum();
    violations.push(final_violation);

    CompletionResult {
        success: final_violation < tolerance,
        final_state: state,
        iterations: max_iterations,
        trajectory,
        constraint_violations: violations,
    }
}

/// Compute gradient of constraint violation.
fn compute_constraint_gradient<F>(state: &SCoord, constraints: &[F], epsilon: f64) -> [f64; 3]
where
    F: Fn(&SCoord) -> f64,
{
    let violation = |s: &SCoord| -> f64 { constraints.iter().map(|c| c(s).powi(2)).sum() };

    let v0 = violation(state);

    let dsk = if state.sk + epsilon <= 1.0 {
        let s_plus = SCoord::new_unchecked(state.sk + epsilon, state.st, state.se);
        (violation(&s_plus) - v0) / epsilon
    } else {
        0.0
    };

    let dst = if state.st + epsilon <= 1.0 {
        let s_plus = SCoord::new_unchecked(state.sk, state.st + epsilon, state.se);
        (violation(&s_plus) - v0) / epsilon
    } else {
        0.0
    };

    let dse = if state.se + epsilon <= 1.0 {
        let s_plus = SCoord::new_unchecked(state.sk, state.st, state.se + epsilon);
        (violation(&s_plus) - v0) / epsilon
    } else {
        0.0
    };

    [dsk, dst, dse]
}

/// TARGET operator: Move one step toward target.
pub fn target(current: &SCoord, target: &SCoord, step_size: f64) -> SCoord {
    let dist = current.distance(target);
    if dist < EPSILON {
        return *target;
    }

    let (gsk, gst, gse) = current.gradient(target);
    let step = step_size.min(dist);

    current.update(gsk * step, gst * step, gse * step)
}

/// SATISFY operator: Check if constraint is satisfied.
pub fn satisfy<F>(state: &SCoord, constraint: F, tolerance: f64) -> bool
where
    F: Fn(&SCoord) -> f64,
{
    constraint(state).abs() < tolerance
}

/// EQUILIBRIUM operator: Find equilibrium of mental state dynamics.
pub fn equilibrium<F>(
    initial_state: &MentalState,
    dynamics: F,
    dt: f64,
    max_time: f64,
    tolerance: f64,
) -> (MentalState, bool)
where
    F: Fn(&MentalState, f64) -> MentalState,
{
    let mut state = initial_state.clone();
    let mut time = 0.0;
    let mut prev_consciousness = state.consciousness();

    while time < max_time {
        state = dynamics(&state, dt);
        time += dt;

        let new_consciousness = state.consciousness();
        if (new_consciousness - prev_consciousness).abs() < tolerance {
            return (state, true);
        }
        prev_consciousness = new_consciousness;
    }

    (state, false)
}

/// Poincare recurrence constraint.
pub fn recurrence_constraint(initial: &SCoord, epsilon: f64) -> impl Fn(&SCoord) -> f64 + '_ {
    move |s: &SCoord| s.distance(initial) - epsilon
}

/// Consciousness target constraint.
pub fn consciousness_constraint(target_c: f64, tolerance: f64) -> impl Fn(f64) -> f64 {
    move |c: f64| {
        if (c - target_c).abs() < tolerance {
            0.0
        } else {
            c - target_c
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_target() {
        let current = SCoord::origin();
        let target_s = SCoord::new(1.0, 1.0, 1.0).unwrap();

        let stepped = target(&current, &target_s, 0.1);
        assert!(stepped.distance(&current) > 0.0);
        assert!(stepped.distance(&target_s) < current.distance(&target_s));
    }

    #[test]
    fn test_satisfy() {
        let state = SCoord::new(0.5, 0.5, 0.5).unwrap();

        // Constraint: sum should be 1.5
        let constraint = |s: &SCoord| s.sk + s.st + s.se - 1.5;
        assert!(satisfy(&state, constraint, 0.01));

        // Constraint: sum should be 2.0
        let constraint2 = |s: &SCoord| s.sk + s.st + s.se - 2.0;
        assert!(!satisfy(&state, constraint2, 0.01));
    }

    #[test]
    fn test_complete() {
        let initial = SCoord::new(0.1, 0.1, 0.1).unwrap();

        // Constraint: move toward (0.5, 0.5, 0.5)
        let constraints: Vec<Box<dyn Fn(&SCoord) -> f64>> = vec![
            Box::new(|s: &SCoord| s.sk - 0.5),
            Box::new(|s: &SCoord| s.st - 0.5),
            Box::new(|s: &SCoord| s.se - 0.5),
        ];

        let result = complete(
            &initial,
            &constraints.iter().map(|c| c.as_ref()).collect::<Vec<_>>(),
            1000,
            0.01,
            0.1,
        );

        assert!(result.success);
        assert!((result.final_state.sk - 0.5).abs() < 0.05);
    }

    fn complete_with_refs<F>(
        partial_state: &SCoord,
        constraints: &[&F],
        max_iterations: usize,
        tolerance: f64,
        learning_rate: f64,
    ) -> CompletionResult
    where
        F: Fn(&SCoord) -> f64 + ?Sized,
    {
        let boxed: Vec<Box<dyn Fn(&SCoord) -> f64>> = constraints
            .iter()
            .map(|&c| {
                let c_clone = c as *const F;
                Box::new(move |s: &SCoord| unsafe { (*c_clone)(s) }) as Box<dyn Fn(&SCoord) -> f64>
            })
            .collect();

        complete(
            partial_state,
            &boxed.iter().map(|b| b.as_ref()).collect::<Vec<_>>(),
            max_iterations,
            tolerance,
            learning_rate,
        )
    }
}
