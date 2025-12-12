"""
Oxygen Phase Lock & Categorical Exclusion Visualization
3D volumetric charts showing oxygen movement and categorical field dynamics
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.patches import Circle, FancyArrowPatch
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

plt.style.use('seaborn-v0_8-paper')
sns.set_palette("husl")
plt.rcParams['figure.figsize'] = (18, 14)
plt.rcParams['font.size'] = 10

def plot_oxygen_phase_states(ax):
    """Panel A: 25,110 Oxygen Quantum States (Polar Phase Diagram)"""
    # Represent discrete oxygen quantum states in polar coordinates
    n_states_show = 100  # Show subset for visualization
    n_total = 25110
    
    # Divide states into shells (like electron shells)
    shells = [10, 20, 30, 40]  # Number of states per shell
    
    for shell_idx, n_states in enumerate(shells):
        angles = np.linspace(0, 2*np.pi, n_states, endpoint=False)
        r = (shell_idx + 1) * 0.3
        
        # Color by energy/state
        colors = plt.cm.viridis(np.linspace(0, 1, n_states))
        
        for angle, color in zip(angles, colors):
            ax.plot([angle], [r], 'o', color=color, markersize=4, alpha=0.7)
    
    # Add labels for shells
    for shell_idx in range(len(shells)):
        r = (shell_idx + 1) * 0.3
        ax.text(0, r + 0.05, f'Shell {shell_idx+1}', fontsize=8, ha='center')
    
    ax.set_ylim(0, 1.5)
    ax.set_title(f'O₂ Quantum States (Total: {n_total:,})\n4:1 Resonance with H+ at 40 THz',
                fontweight='bold', fontsize=13, pad=15)
    ax.grid(True, alpha=0.3)
    ax.set_theta_zero_location('N')
    
    # Add state info
    ax.text(0.02, 0.98, 
           f'Total States: {n_total:,}\nParametric States: O₂(3Σg⁻)\nResonance: 4:1 with H+',
           transform=ax.transAxes, ha='left', va='top', fontsize=9,
           bbox=dict(boxstyle='round,pad=0.4', facecolor='lightblue', alpha=0.8))

def plot_3d_oxygen_volume(ax):
    """Panel B: 3D Volumetric Oxygen Distribution in Cytoplasm"""
    # Create 3D volume showing oxygen concentration
    x = np.linspace(-2, 2, 20)
    y = np.linspace(-2, 2, 20)
    z = np.linspace(-2, 2, 20)
    X, Y, Z = np.meshgrid(x, y, z)
    
    # Simulate oxygen concentration with gradients and hot spots
    # Multiple gaussian-like distributions representing O2 regions
    O2_concentration = (
        np.exp(-((X-0.5)**2 + (Y-0.5)**2 + (Z-0.5)**2) / 0.5) +
        np.exp(-((X+0.5)**2 + (Y+0.5)**2 + (Z+0.5)**2) / 0.7) +
        np.exp(-((X-0.7)**2 + (Y+0.3)**2 + (Z-0.8)**2) / 0.4)
    )
    
    # Flatten for scatter plot
    points = np.array([X.flatten(), Y.flatten(), Z.flatten()]).T
    colors = O2_concentration.flatten()
    
    # Only plot points above threshold
    threshold = 0.3
    mask = colors > threshold
    
    scatter = ax.scatter(points[mask, 0], points[mask, 1], points[mask, 2],
                        c=colors[mask], cmap='Reds', alpha=0.6, s=30,
                        vmin=0, vmax=colors.max())
    
    # Add mitochondria-like structures (O2 sinks)
    mito_positions = [(-1, -1, -1), (1, 1, 1), (0, 1.5, -1)]
    for mx, my, mz in mito_positions:
        ax.scatter([mx], [my], [mz], c='blue', s=200, marker='s',
                  edgecolors='black', linewidths=2, alpha=0.8, label='Mitochondria')
    
    ax.set_xlabel('X (μm)', fontweight='bold', fontsize=10)
    ax.set_ylabel('Y (μm)', fontweight='bold', fontsize=10)
    ax.set_zlabel('Z (μm)', fontweight='bold', fontsize=10)
    ax.set_title('3D Cytoplasmic O₂ Distribution\nVolumetric Concentration Map',
                fontweight='bold', fontsize=13)
    
    # Colorbar
    cbar = plt.colorbar(scatter, ax=ax, fraction=0.03, pad=0.1)
    cbar.set_label('[O₂] (a.u.)', rotation=270, labelpad=15, fontsize=9)
    
    # Remove duplicate legend entries
    handles, labels = ax.get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    ax.legend(by_label.values(), by_label.keys(), loc='upper left', fontsize=8)

def plot_categorical_exclusion(ax):
    """Panel C: Categorical Exclusion Cascade"""
    # Show the 5-level categorical exclusion hierarchy
    levels = [
        'Glucose\nTransport',
        'Glycolysis',
        'TCA Cycle',
        'ETC\n(O₂ → H₂O)',
        'Gene\nExpression'
    ]
    
    # Exclusion strength at each level
    exclusion_strength = [0.85, 0.92, 0.95, 0.98, 0.99]
    entropy_decrease = [0.15, 0.25, 0.35, 0.45, 0.60]
    
    y_pos = np.arange(len(levels))
    
    # Create horizontal bars for exclusion strength
    bars1 = ax.barh(y_pos, exclusion_strength, height=0.35, 
                    label='Categorical Exclusion', color='#e74c3c', 
                    alpha=0.7, edgecolor='black', linewidth=2)
    
    # Create bars for entropy decrease (offset)
    bars2 = ax.barh(y_pos + 0.35, entropy_decrease, height=0.35,
                    label='Information Compression', color='#3498db',
                    alpha=0.7, edgecolor='black', linewidth=2)
    
    # Add value labels
    for i, (bar1, bar2, strength, entropy) in enumerate(zip(bars1, bars2, exclusion_strength, entropy_decrease)):
        ax.text(strength + 0.02, i, f'{strength:.0%}', 
               va='center', fontsize=9, fontweight='bold')
        ax.text(entropy + 0.02, i + 0.35, f'{entropy:.0%}',
               va='center', fontsize=9, fontweight='bold')
    
    ax.set_yticks(y_pos + 0.175)
    ax.set_yticklabels(levels)
    ax.set_xlabel('Fraction', fontweight='bold', fontsize=11)
    ax.set_title('Categorical Exclusion Cascade\n5-Level Metabolic Hierarchy',
                fontweight='bold', fontsize=13)
    ax.set_xlim(0, 1.1)
    ax.legend(loc='lower right', frameon=True, shadow=True, fontsize=10)
    ax.grid(axis='x', alpha=0.3)
    
    # Add O2 role annotation
    ax.text(0.5, -0.5, 'O₂ enables categorical selection at ETC level\n→ Information flows downhill',
           ha='center', fontsize=10, style='italic',
           bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.7))

def plot_phase_lock_field(ax):
    """Panel D: O₂-H+ Phase-Lock Field (3D)"""
    # Create 3D phase-lock field showing coupling
    theta = np.linspace(0, 2*np.pi, 30)
    z = np.linspace(-2, 2, 30)
    Theta, Z = np.meshgrid(theta, z)
    
    # Radial coordinate (field strength)
    R = 1 + 0.3 * np.sin(4*Z) * np.cos(4*Theta)
    
    # Convert to Cartesian
    X = R * np.cos(Theta)
    Y = R * np.sin(Theta)
    
    # Color by phase coherence
    coherence = 0.5 + 0.5 * np.cos(2*Theta) * np.cos(Z)
    
    # Plot surface
    surf = ax.plot_surface(X, Y, Z, facecolors=plt.cm.RdYlGn(coherence),
                          alpha=0.8, shade=True, antialiased=True)
    
    # Add arrows showing O2 movement
    n_arrows = 8
    for i in range(n_arrows):
        z_pos = -2 + 4*i/n_arrows
        theta_pos = 2*np.pi * i / n_arrows
        r_start = 1.5
        r_end = 1.8
        
        x_start = r_start * np.cos(theta_pos)
        y_start = r_start * np.sin(theta_pos)
        x_end = r_end * np.cos(theta_pos)
        y_end = r_end * np.sin(theta_pos)
        
        ax.quiver(x_start, y_start, z_pos, 
                 x_end - x_start, y_end - y_start, 0,
                 arrow_length_ratio=0.3, color='blue', linewidth=2, alpha=0.7)
    
    ax.set_xlabel('X', fontweight='bold', fontsize=10)
    ax.set_ylabel('Y', fontweight='bold', fontsize=10)
    ax.set_zlabel('Z (time)', fontweight='bold', fontsize=10)
    ax.set_title('O₂-H+ Phase-Lock Field\n4:1 Frequency Coupling',
                fontweight='bold', fontsize=13)
    
    # Add text annotation
    ax.text2D(0.02, 0.98, 
             'O₂ paramagnetic coupling\nwith H+ EM field\nf_O2 : f_H+ = 1 : 4',
             transform=ax.transAxes, ha='left', va='top', fontsize=9,
             bbox=dict(boxstyle='round,pad=0.4', facecolor='lightgreen', alpha=0.8))

def create_oxygen_categorical_figure(output_file='oxygen_categorical_figure.png'):
    """Main function to create 4-panel figure"""
    print(f"Creating Oxygen Phase Lock & Categorical Exclusion visualization...")
    
    fig = plt.figure(figsize=(18, 14))
    fig.suptitle('Oxygen Phase Lock & Categorical Exclusion: Volumetric Field Dynamics',
                fontsize=17, fontweight='bold', y=0.995)
    
    # Panel A: Top-left (Polar)
    ax1 = plt.subplot(2, 2, 1, projection='polar')
    plot_oxygen_phase_states(ax1)
    ax1.text(-0.15, 1.05, 'A', transform=ax1.transAxes,
            fontsize=22, fontweight='bold', va='top')
    
    # Panel B: Top-right (3D)
    ax2 = plt.subplot(2, 2, 2, projection='3d')
    plot_3d_oxygen_volume(ax2)
    ax2.text2D(-0.1, 1.05, 'B', transform=ax2.transAxes,
              fontsize=22, fontweight='bold', va='top')
    
    # Panel C: Bottom-left
    ax3 = plt.subplot(2, 2, 3)
    plot_categorical_exclusion(ax3)
    ax3.text(-0.1, 1.05, 'C', transform=ax3.transAxes,
            fontsize=22, fontweight='bold', va='top')
    
    # Panel D: Bottom-right (3D)
    ax4 = plt.subplot(2, 2, 4, projection='3d')
    plot_phase_lock_field(ax4)
    ax4.text2D(-0.1, 1.05, 'D', transform=ax4.transAxes,
              fontsize=22, fontweight='bold', va='top')
    
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
    output_file = 'oxygen_categorical_figure.png'
    
    # Override with command line args if provided
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    
    # Ensure output directory exists
    output_dir = os.path.dirname(output_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    create_oxygen_categorical_figure(output_file)


