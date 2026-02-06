"""
Physical constants for the Virtual Brain framework.

These constants define the fundamental scales at which the
Virtual Brain operates, from quantum to neural timescales.
"""

# Fundamental constants
BOLTZMANN_CONSTANT: float = 1.381e-23  # J/K
PLANCK_CONSTANT: float = 6.626e-34  # J*s
HBAR: float = 1.055e-34  # J*s (reduced Planck constant)

# Virtual Brain characteristic frequencies
H_PLUS_FREQUENCY: float = 4.06e13  # Hz - H+ flux (emotional substrate)
THOUGHT_FREQUENCY: float = 10.0  # Hz - O2 molecular dynamics (alpha-theta)
CONSCIOUSNESS_FREQUENCY: float = 2.5  # Hz - Decay curve intersection

# O2 molecular states (25,110 = 3 * 23 * 364 + 18)
O2_QUANTUM_STATES: int = 25110

# Thermal energy at room temperature (298K)
KT_ROOM_TEMP: float = 4.11e-21  # J

# Timescale hierarchy
TAU_PERCEPTION: float = 0.050  # 50 ms - perceptual integration
TAU_THOUGHT: float = 0.100  # 100 ms - thought decay constant
TAU_CONSCIOUSNESS: float = 0.400  # 400 ms - consciousness integration

# Partition capacity formula coefficient
# C(n) = 2n^2
PARTITION_CAPACITY_COEFF: int = 2

# Ternary advantage over binary
# log_3(n) / log_2(n) = log_2(3) = 1.585
TERNARY_EFFICIENCY: float = 1.585

# Categorical distance normalization
# Maximum partition level for normalization
MAX_PARTITION_LEVEL: int = 10

# Temperature factorization reference
# T = T_0 * exp(Se - Se_ref)
T_0_REFERENCE: float = 300.0  # K
SE_REFERENCE: float = 0.5  # dimensionless

# Kuramoto default parameters
DEFAULT_COUPLING_STRENGTH: float = 0.5
DEFAULT_N_OSCILLATORS: int = 100

# Biological gear ratios (8-level cascade)
BIOLOGICAL_GEAR_RATIOS: tuple = (
    1e-3,   # Level 1: Quantum coherence -> Protein conformational
    1e-3,   # Level 2: Protein -> Ion channel
    1e-3,   # Level 3: Ion channel -> Enzyme catalysis
    1e-3,   # Level 4: Enzyme -> Synaptic
    0.1,    # Level 5: Synaptic -> Action potential
    1e-6,   # Level 6: Action potential -> Circadian
    0.1,    # Level 7: Circadian -> Environmental
    1.0,    # Level 8: Environmental coupling
)

# Regime transition thresholds
RE_LAMINAR_MAX: float = 2300.0
RE_TURBULENT_MIN: float = 4000.0
