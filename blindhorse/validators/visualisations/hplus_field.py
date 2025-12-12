"""
H+ Field Changes Visualization
Polar phase charts showing the 40 THz proton electromagnetic field dynamics
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.patches import Circle, Wedge
from mpl_toolkits.mplot3d import Axes3D

plt.style.use('seaborn-v0_8-paper')
sns.set_palette("husl")
plt.rcParams['figure.figsize'] = (16, 12)
plt.rcParams['font.size'] = 10

def plot_hplus_phase_oscillation(ax):
    """Panel A: H+ Field Phase Oscillation (Polar)"""
    # Simulate 40 THz H+ oscillation phases
    n_cycles = 5
    theta = np.linspace(0, n_cycles * 2 * np.pi, 1000)
    
    # Amplitude modulation showing field strength
    r = 1 + 0.3 * np.sin(8 * theta)  # Field strength modulation
    
    # Plot spiral showing time evolution
    colors = plt.cm.viridis(np.linspace(0, 1, len(theta)))
    for i in range(len(theta)-1):
        ax.plot(theta[i:i+2], r[i:i+2], color=colors[i], linewidth=2, alpha=0.7)
    
    # Mark key phases
    key_phases = [0, np.pi/2, np.pi, 3*np.pi/2, 2*np.pi]
    key_labels = ['0°\n(Peak +)', '90°\n(Zero ↑)', '180°\n(Peak -)', '270°\n(Zero ↓)', '360°\n(Peak +)']
    
    for phase, label in zip(key_phases, key_labels):
        r_val = 1 + 0.3 * np.sin(8 * phase)
        ax.plot([phase], [r_val], 'ro', markersize=12, markeredgecolor='white', markeredgewidth=2, zorder=10)
        ax.text(phase, r_val + 0.15, label, ha='center', fontsize=9, fontweight='bold')
    
    ax.set_theta_zero_location('N')
    ax.set_theta_direction(-1)
    ax.set_ylim(0, 1.6)
    ax.set_title('H+ Field Phase Oscillation\nf = 40 THz | T = 25 fs',
                fontweight='bold', fontsize=14, pad=20)
    ax.grid(True, alpha=0.3)
    
    # Add field strength indicator
    ax.text(0.02, 0.98, 'Field Strength:\n|E| ∝ r\nPhase: θ',
           transform=ax.transAxes, ha='left', va='top', fontsize=9,
           bbox=dict(boxstyle='round,pad=0.4', facecolor='lightyellow', alpha=0.8))

def plot_field_topology(ax):
    """Panel B: H+ Field Topology (2D Field Map)"""
    # Create 2D field map
    x = np.linspace(-3, 3, 50)
    y = np.linspace(-3, 3, 50)
    X, Y = np.meshgrid(x, y)
    
    # Simulate H+ field with multiple oscillating centers (protons)
    n_protons = 5
    proton_positions = [
        (0, 0), (-1.5, 1.5), (1.5, 1.5), (-1.5, -1.5), (1.5, -1.5)
    ]
    
    # Field is sum of contributions from each proton
    Field = np.zeros_like(X)
    for px, py in proton_positions:
        r = np.sqrt((X - px)**2 + (Y - py)**2)
        Field += np.exp(-r/0.8) * np.cos(2*np.pi * 2 * r)  # Oscillatory field
    
    # Plot field as contour
    levels = 20
    contour = ax.contourf(X, Y, Field, levels=levels, cmap='RdBu_r', alpha=0.8)
    contour_lines = ax.contour(X, Y, Field, levels=levels, colors='black', alpha=0.2, linewidths=0.5)
    
    # Mark proton positions
    for px, py in proton_positions:
        ax.plot(px, py, 'o', color='yellow', markersize=15, 
               markeredgecolor='black', markeredgewidth=2, zorder=10)
        ax.text(px, py, 'H+', ha='center', va='center', 
               fontsize=10, fontweight='bold', color='red', zorder=11)
    
    # Add colorbar
    cbar = plt.colorbar(contour, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label('Field Amplitude (a.u.)', rotation=270, labelpad=20, fontsize=10)
    
    ax.set_xlabel('x (nm)', fontweight='bold', fontsize=11)
    ax.set_ylabel('y (nm)', fontweight='bold', fontsize=11)
    ax.set_title('H+ Field Topology: Cytoplasmic Proton Distribution',
                fontweight='bold', fontsize=14)
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)
    
    # Add info box
    ax.text(0.02, 0.98, f'N_protons: {n_protons}\nFrequency: 40 THz\nWavelength: 7.5 μm',
           transform=ax.transAxes, ha='left', va='top', fontsize=9,
           bbox=dict(boxstyle='round,pad=0.4', facecolor='lightblue', alpha=0.8))

def plot_phase_drug_interaction(ax):
    """Panel C: Drug-Modified Field Phase"""
    # Show three states: baseline, drug-bound, therapeutic
    states = ['Baseline\n(No Drug)', 'Drug Binding\n(Transient)', 'Therapeutic\n(Phase-Locked)']
    
    n_states = len(states)
    angles_per_state = np.linspace(0, 2*np.pi, 100)
    
    # Create subplots in polar for each state
    for i, state in enumerate(states):
        # Calculate position
        theta_offset = i * 2 * np.pi / n_states
        
        # Base amplitude
        if i == 0:  # Baseline
            r = 1.0 * np.ones_like(angles_per_state)
            color = '#95a5a6'
            coherence = 0.3
        elif i == 1:  # Drug binding
            r = 1.0 + 0.2 * np.sin(5 * angles_per_state)  # Modulated
            color = '#e67e22'
            coherence = 0.6
        else:  # Therapeutic
            r = 1.2 * np.ones_like(angles_per_state)  # Enhanced & stable
            color = '#2ecc71'
            coherence = 0.9
        
        # Plot each state as a sector
        start_angle = theta_offset - np.pi/3
        end_angle = theta_offset + np.pi/3
        sector_angles = np.linspace(start_angle, end_angle, len(angles_per_state))
        
        ax.plot(sector_angles, r, color=color, linewidth=3, alpha=0.8)
        ax.fill_between(sector_angles, 0, r, alpha=0.3, color=color)
        
        # Add label
        label_angle = theta_offset
        label_r = 1.6
        ax.text(label_angle, label_r, state, ha='center', va='center',
               fontsize=11, fontweight='bold',
               bbox=dict(boxstyle='round,pad=0.5', facecolor=color, alpha=0.6, edgecolor='black', linewidth=2))
        
        # Add coherence indicator
        ax.text(label_angle, label_r - 0.3, f'R = {coherence:.1f}',
               ha='center', fontsize=9, fontweight='bold')
    
    ax.set_ylim(0, 1.8)
    ax.set_title('Drug-Modified H+ Field Phase\n(Polar Phase Diagram)',
                fontweight='bold', fontsize=14, pad=20)
    ax.grid(True, alpha=0.3)
    ax.set_theta_zero_location('N')
    
    # Add legend
    ax.text(0.5, -0.15, 'Drug binding increases field coherence and amplitude',
           transform=ax.transAxes, ha='center', fontsize=10, style='italic')

def plot_temporal_evolution(ax):
    """Panel D: Temporal Field Evolution"""
    time = np.linspace(0, 100, 1000)  # Time in femtoseconds
    
    # Baseline H+ field
    baseline = np.sin(2 * np.pi * 0.04 * time) * np.exp(-time/200)
    
    # Drug interaction event at t=30
    drug_onset = 30
    drug_effect = 1 / (1 + np.exp(-(time - drug_onset)/5))  # Sigmoid
    
    # Modified field
    enhanced_amplitude = 1 + 0.5 * drug_effect
    phase_lock = 1 - 0.3 * drug_effect * np.sin(2 * np.pi * 0.1 * time)
    
    field_with_drug = baseline * enhanced_amplitude * phase_lock
    
    # Plot
    ax.plot(time, baseline, label='Baseline H+ Field', color='#95a5a6', 
           linewidth=2, alpha=0.7, linestyle='--')
    ax.plot(time, field_with_drug, label='Drug-Modified Field', 
           color='#2ecc71', linewidth=3)
    
    # Mark drug binding event
    ax.axvline(drug_onset, color='red', linestyle='--', linewidth=2, alpha=0.7)
    ax.text(drug_onset, ax.get_ylim()[1] * 0.9, 'Drug Binding ↓',
           ha='center', fontsize=10, fontweight='bold', color='red',
           bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7))
    
    # Fill enhancement region
    ax.fill_between(time, baseline, field_with_drug, 
                    where=(field_with_drug >= baseline), 
                    alpha=0.3, color='green', label='Enhancement')
    
    ax.set_xlabel('Time (femtoseconds)', fontweight='bold', fontsize=12)
    ax.set_ylabel('Field Amplitude (a.u.)', fontweight='bold', fontsize=12)
    ax.set_title('Temporal Evolution: H+ Field Modulation by Drug',
                fontweight='bold', fontsize=14)
    ax.legend(loc='upper right', frameon=True, shadow=True, fontsize=10)
    ax.grid(True, alpha=0.3)
    
    # Add info
    ax.text(0.02, 0.05, 
           'H+ oscillation: 40 THz\nDrug binding time: 30 fs\nAmplitude enhancement: +50%',
           transform=ax.transAxes, ha='left', va='bottom', fontsize=9,
           bbox=dict(boxstyle='round,pad=0.4', facecolor='lightgreen', alpha=0.8))

def create_hplus_field_figure(output_file='hplus_field_figure.png'):
    """Main function to create 4-panel figure"""
    print(f"Creating H+ Field visualization...")
    
    fig = plt.figure(figsize=(16, 12))
    fig.suptitle('H+ Electromagnetic Field Dynamics: 40 THz Proton Oscillations',
                fontsize=16, fontweight='bold', y=0.995)
    
    # Panel A: Top-left (Polar)
    ax1 = plt.subplot(2, 2, 1, projection='polar')
    plot_hplus_phase_oscillation(ax1)
    ax1.text(-0.15, 1.05, 'A', transform=ax1.transAxes,
            fontsize=20, fontweight='bold', va='top')
    
    # Panel B: Top-right
    ax2 = plt.subplot(2, 2, 2)
    plot_field_topology(ax2)
    ax2.text(-0.1, 1.05, 'B', transform=ax2.transAxes,
            fontsize=20, fontweight='bold', va='top')
    
    # Panel C: Bottom-left (Polar)
    ax3 = plt.subplot(2, 2, 3, projection='polar')
    plot_phase_drug_interaction(ax3)
    ax3.text(-0.15, 1.05, 'C', transform=ax3.transAxes,
            fontsize=20, fontweight='bold', va='top')
    
    # Panel D: Bottom-right
    ax4 = plt.subplot(2, 2, 4)
    plot_temporal_evolution(ax4)
    ax4.text(-0.1, 1.05, 'D', transform=ax4.transAxes,
            fontsize=20, fontweight='bold', va='top')
    
    plt.tight_layout(rect=[0, 0, 1, 0.99])
    plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"[OK] Figure saved to {output_file}")
    plt.close()
    
    return fig

# Run
if __name__ == "__main__":
    import sys
    import os
    
    # Default path
    output_file = 'hplus_field_figure.png'
    
    # Override with command line args if provided
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    
    # Ensure output directory exists
    output_dir = os.path.dirname(output_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    create_hplus_field_figure(output_file)


