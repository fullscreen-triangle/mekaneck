//! Physical constants for the Virtual Brain computing framework.
//!
//! These constants define the fundamental scales and parameters
//! used throughout the framework.

/// Boltzmann constant (J/K)
pub const BOLTZMANN_CONSTANT: f64 = 1.381e-23;

/// Planck constant (J*s)
pub const PLANCK_CONSTANT: f64 = 6.626e-34;

/// Reduced Planck constant (J*s)
pub const HBAR: f64 = 1.055e-34;

/// H+ flux frequency (Hz) - emotional substrate
pub const H_PLUS_FREQUENCY: f64 = 4.06e13;

/// Thought frequency (Hz) - alpha-theta range
pub const THOUGHT_FREQUENCY: f64 = 10.0;

/// Consciousness frequency (Hz)
pub const CONSCIOUSNESS_FREQUENCY: f64 = 2.5;

/// O2 molecular quantum states
pub const O2_QUANTUM_STATES: usize = 25110;

/// Thermal energy at room temperature 298K (J)
pub const KT_ROOM_TEMP: f64 = 4.11e-21;

/// Perception timescale (s)
pub const TAU_PERCEPTION: f64 = 0.050;

/// Thought timescale (s)
pub const TAU_THOUGHT: f64 = 0.100;

/// Consciousness timescale (s)
pub const TAU_CONSCIOUSNESS: f64 = 0.400;

/// Partition capacity coefficient: C(n) = 2n^2
pub const PARTITION_CAPACITY_COEFF: i32 = 2;

/// Ternary efficiency: log_2(3) ≈ 1.585
pub const TERNARY_EFFICIENCY: f64 = 1.585;

/// Reference temperature (K)
pub const T_0_REFERENCE: f64 = 300.0;

/// Reference S-entropy for temperature mapping
pub const SE_REFERENCE: f64 = 0.5;

/// Default Kuramoto coupling strength
pub const DEFAULT_COUPLING_STRENGTH: f64 = 0.5;

/// Default number of oscillators
pub const DEFAULT_N_OSCILLATORS: usize = 100;

/// Biological gear ratios (8-level cascade)
pub const BIOLOGICAL_GEAR_RATIOS: [f64; 8] = [
    1e-3, 1e-3, 1e-3, 1e-3, 0.1, 1e-6, 0.1, 1.0
];

/// Reynolds number threshold for laminar flow
pub const RE_LAMINAR_MAX: f64 = 2300.0;

/// Reynolds number threshold for turbulent flow
pub const RE_TURBULENT_MIN: f64 = 4000.0;
