//! Charge Operators: CONSERVE, REDISTRIBUTE.
//!
//! Operators for charge transport and conservation.

use ndarray::Array1;
use vb_core::constants::BOLTZMANN_CONSTANT;

/// CONSERVE operator: Verify total charge conservation.
pub fn conserve(rho: &Array1<f64>) -> f64 {
    rho.sum()
}

/// REDISTRIBUTE operator: Move charge toward target distribution.
pub fn redistribute(rho: &Array1<f64>, target: &Array1<f64>, rate: f64) -> Array1<f64> {
    let diff = target - rho;
    rho + &(diff * rate)
}

/// Compute charge variance.
pub fn charge_variance(rho: &Array1<f64>) -> f64 {
    let mean = rho.mean().unwrap_or(0.0);
    rho.mapv(|x| (x - mean).powi(2)).mean().unwrap_or(0.0)
}

/// Minimize variance through redistribution.
pub fn minimize_variance(
    rho: &Array1<f64>,
    max_iterations: usize,
    tolerance: f64,
) -> Array1<f64> {
    let n = rho.len();
    let total = conserve(rho);
    let uniform = Array1::from_elem(n, total / n as f64);

    let mut current = rho.clone();

    for _ in 0..max_iterations {
        let var = charge_variance(&current);
        if var < tolerance {
            break;
        }
        current = redistribute(&current, &uniform, 0.1);
    }

    current
}

/// Charge continuity: drho/dt + div(J) = 0
pub fn charge_continuity(rho: &Array1<f64>, j: &Array1<f64>, dt: f64, dx: f64) -> Array1<f64> {
    let n = rho.len();
    let mut new_rho = rho.clone();

    for i in 1..n - 1 {
        let div_j = (j[i + 1] - j[i - 1]) / (2.0 * dx);
        new_rho[i] = rho[i] - div_j * dt;
    }

    // Boundary conditions (zero flux)
    new_rho[0] = new_rho[1];
    new_rho[n - 1] = new_rho[n - 2];

    new_rho
}

/// Couple charge to consciousness.
pub fn couple_charge_consciousness(
    rho: &Array1<f64>,
    consciousness: f64,
    coupling: f64,
) -> Array1<f64> {
    // Higher consciousness leads to more organized charge distribution
    let mean = rho.mean().unwrap_or(0.0);
    let factor = 1.0 - coupling * consciousness;

    rho.mapv(|x| mean + factor * (x - mean))
}

/// Boltzmann equilibrium distribution.
pub fn charge_equilibrium(rho: &Array1<f64>, temperature: f64) -> Array1<f64> {
    let n = rho.len();
    if n == 0 {
        return rho.clone();
    }

    // Simple harmonic potential centered at middle
    let center = n as f64 / 2.0;
    let potential: Array1<f64> = Array1::from_iter(
        (0..n).map(|i| 0.5 * (i as f64 - center).powi(2))
    );

    // Boltzmann factor
    let kt = BOLTZMANN_CONSTANT * temperature;
    let boltzmann: Array1<f64> = potential.mapv(|v| (-v / kt).exp());
    let z = boltzmann.sum();

    let total_charge = conserve(rho);
    boltzmann.mapv(|b| total_charge * b / z)
}

/// Surface coupling between electric and chemical.
pub fn surface_coupling(
    rho_electric: &Array1<f64>,
    c_chemical: &Array1<f64>,
    coupling_constant: f64,
) -> (Array1<f64>, Array1<f64>) {
    // Bidirectional coupling
    let interaction = rho_electric * c_chemical;

    let new_rho = rho_electric - &(&interaction * coupling_constant);
    let new_c = c_chemical + &(&interaction * coupling_constant);

    (new_rho, new_c)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_conserve() {
        let rho = Array1::from_vec(vec![1.0, 2.0, 3.0, 4.0]);
        assert!((conserve(&rho) - 10.0).abs() < 1e-10);
    }

    #[test]
    fn test_redistribute_conservation() {
        let rho = Array1::from_vec(vec![1.0, 2.0, 3.0, 4.0]);
        let target = Array1::from_vec(vec![2.5, 2.5, 2.5, 2.5]);

        let new_rho = redistribute(&rho, &target, 0.5);

        // Total charge should be conserved
        assert!((conserve(&new_rho) - conserve(&rho)).abs() < 1e-10);
    }

    #[test]
    fn test_minimize_variance() {
        let rho = Array1::from_vec(vec![1.0, 5.0, 2.0, 8.0]);
        let minimized = minimize_variance(&rho, 1000, 1e-6);

        // Variance should be reduced
        assert!(charge_variance(&minimized) < charge_variance(&rho));

        // Total charge conserved
        assert!((conserve(&minimized) - conserve(&rho)).abs() < 1e-10);
    }

    #[test]
    fn test_charge_variance() {
        let uniform = Array1::from_vec(vec![1.0, 1.0, 1.0, 1.0]);
        assert!(charge_variance(&uniform) < 1e-10);

        let varied = Array1::from_vec(vec![0.0, 2.0, 0.0, 2.0]);
        assert!(charge_variance(&varied) > 0.5);
    }
}
