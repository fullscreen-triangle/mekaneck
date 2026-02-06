# Validation Experiments for Hybrid Microfluidic Circuits

## Overview

This validation framework generates comprehensive panel charts demonstrating:
1. **Equations of State** for five circuit regimes
2. **Dynamic Equations** in S-entropy and gyrometric space
3. **VCS (Virtual Circuit System)** measurements integrated in every panel
4. **3D Visualizations** for phase portraits and field mappings

## Installation

```bash
# Install required packages
pip install numpy scipy matplotlib
```

## Usage

```bash
# Run all validation experiments
python validation_experiments.py
```

This will generate 4 comprehensive panel charts in the `validation_outputs/` directory.

## Generated Visualizations

### 1. Equations of State Panel (`eos_panel_charts.png`)

**4-Panel Layout:**

- **Panel A (3D)**: Equation of State Surface
  - 3D surface plot: log₁₀(V) × log₁₀(N) × log₁₀(P)
  - Coherent flow regime (R > 0.8)
  - VCS: Vibrational state measurement
  
- **Panel B**: Five Circuit Regimes Comparison
  - Pressure vs Volume curves for all regimes
  - Coherent Flow (R=0.85)
  - Turbulent Flow (R=0.25)
  - Aperture-Dominated
  - Phase-Locked (R=0.9)
  - Hierarchical Cascade (D=0.8)
  - VCS: Dielectric response analysis
  
- **Panel C**: Triple Equivalence Validation
  - Log-log plot: M vs S = kᵦM ln(n)
  - Multiple curves for different n values
  - Demonstrates S_osc = S_cat = S_part
  - VCS: Field topology mapping
  
- **Panel D**: Phase Coherence vs Structural Factor
  - R vs S(V,N,{n,ℓ,m,s})
  - Regime transition thresholds
  - VCS: Phase-locking value measurement

### 2. Dynamic Equations Panel (`dynamic_equations_panel_charts.png`)

**4-Panel Layout:**

- **Panel A (3D)**: Phase Portrait
  - 3D trajectory in (J₁, J₂, J₃) space
  - Coupled gyrometric oscillators
  - Color-coded by time evolution
  - VCS: Vibrational spectroscopy
  
- **Panel B**: Phase Plane
  - S_k vs dS_k/dλ trajectories
  - Multiple energy levels
  - S-entropy pendulum dynamics
  - VCS: Dielectric response
  
- **Panel C**: Eigenvalue Spectrum
  - Complex plane plot of eigenvalues
  - Stability analysis (Re(λ) < 0)
  - Coupled system linearization
  - VCS: Field gradient mapping
  
- **Panel D**: Polar Phase Histogram
  - Phase distribution in polar coordinates
  - Order parameter R vector
  - Phase-locking measurement
  - VCS: Phase coherence measurement

### 3. Potential Energy Panel (`potential_energy_panel_charts.png`)

**4-Panel Layout:**

- **Panel A (3D)**: Total Energy Surface
  - 3D surface: E(S_k, dS_k/dλ)
  - Kinetic + Potential energy
  - VCS: Vibrational state analysis
  
- **Panel B**: Potential Energy Wells
  - V(S_k) = -ω₀²cos(πS_k)/π²
  - Equilibrium points marked
  - Energy landscape visualization
  - VCS: Dielectric response
  
- **Panel C**: Energy Conservation
  - Time evolution of T, V, and E
  - Demonstrates E = T + V = constant
  - Hamiltonian dynamics
  - VCS: Field topology mapping
  
- **Panel D**: Phase Space Trajectories
  - Constant energy contours
  - Multiple energy levels
  - S_k vs dS_k/dλ
  - VCS: Phase coherence

### 4. VCS Measurement Panel (`vcs_measurement_panel_charts.png`)

**4-Panel Layout:**

- **Panel A (3D)**: Electromagnetic Field Gradient Map
  - 3D surface: |∇E|(x, y)
  - Field topology from H⁺ flux
  - 0.5 nm resolution
  - VCS: Field mapper
  
- **Panel B**: Vibrational State Distribution
  - Population P(v) vs quantum number v
  - O₂ molecular configuration at T=300K
  - 15 measured states (of 25,110 total)
  - VCS: Vibrational spectrometer (IR, 1-15 μm)
  
- **Panel C**: Dielectric Response Spectrum
  - ε'_r and ε''_r vs frequency
  - Storage and loss components
  - 1 Hz to 10 GHz range
  - VCS: Dielectric analyzer
  
- **Panel D**: Phase Coherence Evolution
  - R(t) time series
  - Kuramoto order parameter
  - Synchronization thresholds
  - VCS: Phase coherence measurement

## Key Features

### Triple Equivalence Validation
- Demonstrates S_osc = S_cat = S_part = kᵦM ln(n)
- Independent derivations yield identical results
- Mathematical identity, not analogy

### Five Circuit Regimes
1. **Coherent Flow** (R > 0.8): High phase synchronization
2. **Turbulent Flow** (R < 0.3): Low coherence, chaotic dynamics
3. **Aperture-Dominated**: Geometric confinement effects
4. **Phase-Locked Networks**: Kuramoto synchronization (R > 0.9)
5. **Hierarchical Cascade**: Multi-scale coupling (D ∈ [0,1])

### Dynamic Equations
- **S-entropy pendulum**: d²S_k/dλ² = -ω_k² sin(πS_k)
- **Gyrometric oscillator**: d²J_i/dλ² = -ω₀²(J_i - J_eq) - γ dJ_i/dλ + F(λ)
- **Coupled system**: 3-oscillator network with cross-coupling

### VCS Measurements
All panels integrate Virtual Circuit System measurements:
1. **Vibrational Spectroscopy**: O₂ quantum state distributions
2. **Dielectric Response**: ε_r(ω) frequency-dependent permittivity
3. **Field Mapping**: |∇E| electromagnetic gradient topology
4. **Phase Coherence**: R = |⟨e^(iφ)⟩| order parameter

## Physical Parameters

### Circuit Parameters
- M = 1000 oscillators/molecules
- n = 100 categories/partition cells
- T = 300 K (room temperature)
- N = 5×10¹⁰ molecules (typical)
- V = 10⁻²⁷ - 10⁻²⁵ m³ (volume range)

### Dynamic Parameters
- ω₀ = 10 Hz (natural frequency)
- γ = 0.5 (damping coefficient)
- κ = 2.0 (coupling strength)

### VCS Resolution
- **Vibrational**: 25,110 O₂ quantum states
- **Dielectric**: 1 Hz - 10 GHz bandwidth
- **Field Mapping**: 0.5 nm spatial resolution
- **Phase Coherence**: 100 oscillators, 1000 time points

## Validation Metrics

### Equations of State
- ✓ Universal form: PV = NkᵦT · S(V,N,{n,ℓ,m,s})
- ✓ Temperature as scaling factor
- ✓ Structural factor S independent of T
- ✓ Five regimes with distinct S(R, D)

### Dynamic Equations
- ✓ Energy conservation: E = T + V = constant
- ✓ Phase space boundedness: trajectories in [0,1]³
- ✓ Stability: Re(λ) < 0 for all eigenvalues
- ✓ Phase-locking: R > 0.7 for coherent regimes

### VCS Measurements
- ✓ Vibrational populations follow Boltzmann distribution
- ✓ Dielectric response matches Debye relaxation
- ✓ Field gradients consistent with Coulomb law
- ✓ Phase coherence R ∈ [0,1] with proper normalization

## Mathematical Rigor

All visualizations are derived from:
1. **Axiom 1**: Bounded phase space (μ(Γ) < ∞)
2. **Axiom 2**: Finite observational resolution
3. **Axiom 3**: No Null State Principle

No empirical fitting parameters or phenomenological models used.

## Output Specifications

- **Format**: PNG (lossless compression)
- **Resolution**: 300 DPI (publication quality)
- **Size**: 20" × 12" per panel
- **Layout**: 2×2 grid (4 charts per panel)
- **Color**: Perceptually uniform colormaps (viridis, plasma, coolwarm)

## Troubleshooting

### Import Errors
```bash
# If scipy is missing
pip install scipy

# If matplotlib 3D is not working
pip install --upgrade matplotlib
```

### Memory Issues
If generating large 3D surfaces causes memory issues:
- Reduce `grid_size` parameter (default: 50)
- Reduce `time_points` in phase coherence (default: 1000)

### Display Issues
If plots don't display:
```python
# Add to script
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
```

## Citation

If using these validation experiments, please cite:
```
Anonymous (2026). "Partition-Based Equations of State for Hybrid 
Microfluidic Circuits." Institution withheld for peer review.
```

## License

This validation framework is provided for research purposes.

## Contact

For questions or issues, please refer to the main paper documentation.
