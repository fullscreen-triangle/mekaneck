//! S-Entropy Operators: NAVIGATE, GRAD_S, UPDATE_*.
//!
//! Operators for navigating S-entropy space.

use vb_core::types::SCoord;

const EPSILON: f64 = 1e-10;

/// NAVIGATE operator: Gradient descent path from current to target.
pub fn navigate(
    current: &SCoord,
    target: &SCoord,
    step_size: f64,
    max_steps: usize,
) -> Vec<SCoord> {
    let mut path = vec![*current];
    let mut pos = *current;

    for _ in 0..max_steps {
        let dist = pos.distance(target);
        if dist < EPSILON {
            break;
        }

        let (gsk, gst, gse) = pos.gradient(target);
        let step = step_size.min(dist);

        pos = pos.update(gsk * step, gst * step, gse * step);
        path.push(pos);
    }

    path
}

/// GRAD_S operator: Numerical gradient of a field.
pub fn grad_s<F>(s: &SCoord, field: F, epsilon: f64) -> [f64; 3]
where
    F: Fn(&SCoord) -> f64,
{
    let f0 = field(s);

    // Partial derivatives
    let dsk = if s.sk + epsilon <= 1.0 {
        let s_plus = SCoord::new_unchecked(s.sk + epsilon, s.st, s.se);
        (field(&s_plus) - f0) / epsilon
    } else if s.sk - epsilon >= 0.0 {
        let s_minus = SCoord::new_unchecked(s.sk - epsilon, s.st, s.se);
        (f0 - field(&s_minus)) / epsilon
    } else {
        0.0
    };

    let dst = if s.st + epsilon <= 1.0 {
        let s_plus = SCoord::new_unchecked(s.sk, s.st + epsilon, s.se);
        (field(&s_plus) - f0) / epsilon
    } else if s.st - epsilon >= 0.0 {
        let s_minus = SCoord::new_unchecked(s.sk, s.st - epsilon, s.se);
        (f0 - field(&s_minus)) / epsilon
    } else {
        0.0
    };

    let dse = if s.se + epsilon <= 1.0 {
        let s_plus = SCoord::new_unchecked(s.sk, s.st, s.se + epsilon);
        (field(&s_plus) - f0) / epsilon
    } else if s.se - epsilon >= 0.0 {
        let s_minus = SCoord::new_unchecked(s.sk, s.st, s.se - epsilon);
        (f0 - field(&s_minus)) / epsilon
    } else {
        0.0
    };

    [dsk, dst, dse]
}

/// UPDATE_SK operator: Update knowledge entropy based on information gain.
pub fn update_sk(s: &SCoord, information_gain: f64) -> SCoord {
    // More information reduces knowledge entropy
    let delta_sk = -information_gain * s.sk;
    s.update(delta_sk, 0.0, 0.0)
}

/// UPDATE_ST operator: Update temporal entropy based on circuit timescale.
pub fn update_st(s: &SCoord, tau_circuit: f64, tau_max: f64) -> SCoord {
    // Longer timescale increases temporal entropy
    let delta_st = (tau_circuit / tau_max) * (1.0 - s.st);
    s.update(0.0, delta_st, 0.0)
}

/// UPDATE_SE operator: Update evolution entropy based on trajectory step.
pub fn update_se(s: &SCoord, trajectory_step: f64, dt: f64) -> SCoord {
    // Larger trajectory steps increase evolution entropy
    let delta_se = trajectory_step * dt * (1.0 - s.se);
    s.update(0.0, 0.0, delta_se)
}

/// Entropy field: Total entropy magnitude.
pub fn entropy_field(s: &SCoord) -> f64 {
    s.entropy_magnitude()
}

/// Free energy field: F = U - T*S
pub fn free_energy_field(s: &SCoord, temperature: f64, internal_energy: f64) -> f64 {
    internal_energy - temperature * s.entropy_magnitude()
}

/// Minimize free energy using gradient descent.
pub fn minimize_free_energy(
    initial: &SCoord,
    temperature: f64,
    max_iterations: usize,
    learning_rate: f64,
) -> SCoord {
    let mut s = *initial;

    for _ in 0..max_iterations {
        let grad = grad_s(&s, |coord| free_energy_field(coord, temperature, 1.0), 1e-6);

        // Gradient descent step
        let new_s = s.update(
            -learning_rate * grad[0],
            -learning_rate * grad[1],
            -learning_rate * grad[2],
        );

        // Check convergence
        if s.distance(&new_s) < EPSILON {
            break;
        }
        s = new_s;
    }

    s
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_navigate() {
        let start = SCoord::origin();
        let target = SCoord::new(0.5, 0.5, 0.5).unwrap();
        let path = navigate(&start, &target, 0.1, 100);

        assert!(path.len() > 1);
        assert!(path.last().unwrap().distance(&target) < 0.15);
    }

    #[test]
    fn test_grad_s() {
        let s = SCoord::new(0.5, 0.5, 0.5).unwrap();
        let grad = grad_s(&s, entropy_field, 1e-6);

        // Gradient should point toward increasing entropy
        assert!(grad[0] > 0.0);
        assert!(grad[1] > 0.0);
        assert!(grad[2] > 0.0);
    }

    #[test]
    fn test_update_sk() {
        let s = SCoord::new(0.8, 0.5, 0.5).unwrap();
        let updated = update_sk(&s, 0.5);
        assert!(updated.sk < s.sk);
    }

    #[test]
    fn test_update_st() {
        let s = SCoord::new(0.5, 0.3, 0.5).unwrap();
        let updated = update_st(&s, 0.5, 1.0);
        assert!(updated.st > s.st);
    }
}
