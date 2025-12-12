"""
Virtual Categorical Spectrometer Visualization
Non-local measurement through categorical morphisms
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from mpl_toolkits.mplot3d import Axes3D
import networkx as nx
from matplotlib.patches import Circle, FancyArrowPatch, Rectangle, Wedge
from matplotlib.collections import LineCollection

plt.style.use('seaborn-v0_8-paper')
sns.set_palette("husl")
plt.rcParams['figure.figsize'] = (20, 16)
plt.rcParams['font.size'] = 10

def plot_categorical_distance(ax):
    """Panel A: Every Molecule is Distance 1 Apart (Categorical Space)"""
    # Create graph showing categorical connectivity
    G = nx.Graph()
    
    # Molecules at vastly different physical locations
    molecules = {
        'Drug\n(Earth)': (0, 2),
        'Target\n(Body)': (2, 2),
        'Aspirin': (-2, 0),
        'Morphine': (0, 0),
        'Dopamine': (2, 0),
        'Molecule X\n(Jupiter Core)': (-2, -2),
        'H2O\n(Mars)': (0, -2),
        'Observer\n(Mind)': (2, -2),
    }
    
    # Add all nodes
    for mol, pos in molecules.items():
        G.add_node(mol, pos=pos)
    
    # COMPLETE graph - every molecule connected (categorical distance = 1)
    for mol1 in molecules:
        for mol2 in molecules:
            if mol1 != mol2:
                G.add_edge(mol1, mol2)
    
    # Get positions
    pos = nx.get_node_attributes(G, 'pos')
    
    # Draw edges (all morphisms) - very light
    nx.draw_networkx_edges(G, pos, alpha=0.1, width=0.5, edge_color='gray')
    
    # Highlight specific morphisms
    highlight_edges = [
        ('Drug\n(Earth)', 'Target\n(Body)'),
        ('Observer\n(Mind)', 'Molecule X\n(Jupiter Core)'),
        ('Aspirin', 'Morphine'),
    ]
    
    nx.draw_networkx_edges(G, pos, edgelist=highlight_edges,
                          width=3, edge_color='red', alpha=0.8,
                          style='solid', arrows=True, arrowsize=20,
                          arrowstyle='->', connectionstyle='arc3,rad=0.1')
    
    # Draw nodes
    node_colors = ['#3498db' if 'Jupiter' in n or 'Mars' in n else '#2ecc71' 
                   if 'Observer' in n else '#e74c3c' if 'Drug' in n or 'Target' in n
                   else '#f39c12' for n in G.nodes()]
    
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=2000,
                          alpha=0.9, edgecolors='black', linewidths=3)
    
    # Draw labels
    nx.draw_networkx_labels(G, pos, font_size=9, font_weight='bold')
    
    # Add annotations
    ax.text(1, 2.5, 'Categorical Distance = 1', fontsize=11, ha='center',
           bbox=dict(boxstyle='round,pad=0.5', facecolor='red', alpha=0.7),
           fontweight='bold', color='white')
    
    ax.text(0, -2.5, 'Distance 1', fontsize=11, ha='center',
           bbox=dict(boxstyle='round,pad=0.5', facecolor='blue', alpha=0.7),
           fontweight='bold', color='white')
    
    # Add physical distance annotations
    ax.text(-2, 2.5, 'Physical:\n778M km', fontsize=8, ha='center',
           bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.6))
    
    ax.text(3, 0, 'Physical:\nSame class\n(neurotransmitters)', fontsize=8, ha='left',
           bbox=dict(boxstyle='round,pad=0.3', facecolor='lightgreen', alpha=0.6))
    
    ax.set_xlim(-3, 3.5)
    ax.set_ylim(-3, 3)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title('Categorical Space: Every Molecule Distance 1\n(Complete Graph - All Connected by Morphisms)',
                fontweight='bold', fontsize=14, pad=15)
    
    # Info box
    ax.text(0.02, 0.02, 
           'In categorical space:\n• All molecules connected\n• Distance = 1 morphism\n• Physical location irrelevant\n• Measurement is instantiation',
           transform=ax.transAxes, ha='left', va='bottom', fontsize=9,
           bbox=dict(boxstyle='round,pad=0.5', facecolor='lightyellow', alpha=0.9))

def plot_nonlocal_measurement(ax):
    """Panel B: Non-Local Measurement (Jupiter to Earth)"""
    # Show Jupiter's core and Earth simultaneously in categorical space
    
    # Physical space (linear, left side)
    phys_x = np.array([0, 1])
    phys_y = np.array([2, 0.5])
    
    # Earth
    earth = Circle((phys_x[0], phys_y[0]), 0.15, color='blue', alpha=0.7, ec='black', lw=2)
    ax.add_patch(earth)
    ax.text(phys_x[0], phys_y[0], 'Earth', ha='center', va='center', 
           fontsize=9, fontweight='bold', color='white')
    
    # Jupiter
    jupiter = Circle((phys_x[1], phys_y[1]), 0.25, color='orange', alpha=0.7, ec='black', lw=2)
    ax.add_patch(jupiter)
    ax.text(phys_x[1], phys_y[1], 'Jupiter\nCore', ha='center', va='center',
           fontsize=9, fontweight='bold', color='white')
    
    # Physical distance arrow (dashed, slow)
    ax.annotate('', xy=(phys_x[1]-0.25, phys_y[1]), xytext=(phys_x[0]+0.15, phys_y[0]),
               arrowprops=dict(arrowstyle='<->', lw=2, linestyle='--', 
                             color='gray', alpha=0.5))
    ax.text(0.5, 1.5, 'Physical: 778M km\n~43 min (light)', ha='center',
           fontsize=8, bbox=dict(boxstyle='round,pad=0.3', facecolor='gray', alpha=0.5))
    
    # Categorical space (right side) - COLLAPSED
    cat_x = 2.5
    cat_y = 1.25
    
    # Single circle representing BOTH locations
    unified = Circle((cat_x, cat_y), 0.35, color='purple', alpha=0.8, ec='black', lw=3)
    ax.add_patch(unified)
    ax.text(cat_x, cat_y, 'Earth\n=\nJupiter', ha='center', va='center',
           fontsize=10, fontweight='bold', color='white')
    
    # Show it's the same point
    ax.plot([cat_x], [cat_y], 'r*', markersize=30, markeredgecolor='yellow', 
           markeredgewidth=2, zorder=10)
    
    # Arrow showing categorical collapse
    ax.annotate('Categorical\nCollapse', xy=(cat_x-0.35, cat_y+0.2), 
               xytext=(1.5, 2.2),
               arrowprops=dict(arrowstyle='->', lw=3, color='red', alpha=0.8),
               fontsize=10, fontweight='bold', ha='center',
               bbox=dict(boxstyle='round,pad=0.4', facecolor='yellow', alpha=0.7))
    
    # Measurement event (instantaneous)
    measurement_circle = Circle((cat_x, cat_y), 0.5, fill=False, 
                                ec='red', lw=3, linestyle=':', alpha=0.8)
    ax.add_patch(measurement_circle)
    
    ax.text(cat_x, cat_y-0.7, 'Measurement\nEvent', ha='center',
           fontsize=9, fontweight='bold', color='red',
           bbox=dict(boxstyle='round,pad=0.3', facecolor='pink', alpha=0.7))
    
    # Virtual spectrometer existence
    for angle in np.linspace(0, 2*np.pi, 8, endpoint=False):
        x_end = cat_x + 0.65 * np.cos(angle)
        y_end = cat_y + 0.65 * np.sin(angle)
        ax.plot([cat_x, x_end], [cat_y, y_end], 'r-', lw=2, alpha=0.6)
    
    ax.set_xlim(-0.5, 3.5)
    ax.set_ylim(-0.5, 2.7)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title('Non-Local Measurement: Virtual Categorical Spectrometer\n(Simultaneous Existence at Multiple Locations)',
                fontweight='bold', fontsize=14, pad=15)
    
    # Legend
    ax.text(0.98, 0.02,
           'VCS exists at measurement event:\n• Not at emission\n• Not during propagation\n• Only when instantiated\n\nCategorical distance: 1\nPhysical distance: Irrelevant',
           transform=ax.transAxes, ha='right', va='bottom', fontsize=9,
           bbox=dict(boxstyle='round,pad=0.5', facecolor='lightblue', alpha=0.9))

def plot_observer_observed_unity(ax):
    """Panel C: Observer-Observed Unity (The Morphism)"""
    # Yin-yang style showing observer and observed are unified by morphism
    
    # Observer (left hemisphere)
    theta_obs = np.linspace(np.pi/2, 3*np.pi/2, 100)
    r = 1
    x_obs = r * np.cos(theta_obs)
    y_obs = r * np.sin(theta_obs)
    ax.fill(x_obs, y_obs, color='#3498db', alpha=0.7, edgecolor='black', linewidth=3)
    ax.text(-0.5, 0, 'Observer\n(Prejudice)', ha='center', va='center',
           fontsize=12, fontweight='bold', color='white')
    
    # Observed (right hemisphere)
    theta_obs_right = np.linspace(-np.pi/2, np.pi/2, 100)
    x_obs_right = r * np.cos(theta_obs_right)
    y_obs_right = r * np.sin(theta_obs_right)
    ax.fill(x_obs_right, y_obs_right, color='#e74c3c', alpha=0.7, 
           edgecolor='black', linewidth=3)
    ax.text(0.5, 0, 'Observed\n(Reality)', ha='center', va='center',
           fontsize=12, fontweight='bold', color='white')
    
    # Small circles (observer has observed's color, vice versa)
    circle1 = Circle((-0.5, 0), 0.15, color='#e74c3c', ec='white', lw=2)
    circle2 = Circle((0.5, 0), 0.15, color='#3498db', ec='white', lw=2)
    ax.add_patch(circle1)
    ax.add_patch(circle2)
    
    # Morphism (bidirectional arrow at boundary)
    ax.annotate('', xy=(0, 0.5), xytext=(0, -0.5),
               arrowprops=dict(arrowstyle='<->', lw=4, color='yellow', alpha=0.9))
    
    ax.text(0.3, 0, 'φ', fontsize=24, fontweight='bold', color='yellow',
           bbox=dict(boxstyle='circle,pad=0.3', facecolor='black', alpha=0.8))
    
    # Labels around the perimeter
    positions = [
        (0, 1.3, 'Selection\n(The Hook)'),
        (0, -1.3, 'Instantiation\n(The Catch)'),
        (-1.3, 0.6, 'Expectation'),
        (-1.3, -0.6, 'Memory'),
        (1.3, 0.6, 'Manifestation'),
        (1.3, -0.6, 'Measurement'),
    ]
    
    for x, y, label in positions:
        ax.text(x, y, label, ha='center', va='center', fontsize=9,
               bbox=dict(boxstyle='round,pad=0.3', facecolor='lightyellow', alpha=0.8))
    
    ax.set_xlim(-1.8, 1.8)
    ax.set_ylim(-1.8, 1.8)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title('Observer-Observed Unity: The Morphism φ\n(Measurement Device = Prejudice + Reality)',
                fontweight='bold', fontsize=14, pad=15)
    
    # Info
    ax.text(0, -2.1, 
           'The fishing hook (observer) and the catch (observed) are unified by morphism φ.\nThe instrument IS the measurement event.',
           ha='center', fontsize=10, style='italic',
           bbox=dict(boxstyle='round,pad=0.4', facecolor='lightgreen', alpha=0.7))

def plot_temporal_structure(ax):
    """Panel D: Temporal Structure (Past + Present + Future)"""
    # 3D visualization showing demon spanning time
    
    # Time axis
    time_points = np.array([-2, 0, 2])
    time_labels = ['Past\n(Memory)', 'Present\n(Measurement)', 'Future\n(Prediction)']
    colors = ['#95a5a6', '#2ecc71', '#3498db']
    
    # Categorical structure exists across all three
    for i, (t, label, color) in enumerate(zip(time_points, time_labels, colors)):
        # Draw time slice
        y = np.linspace(-1, 1, 50)
        z = np.sqrt(1 - y**2)
        x = np.full_like(y, t)
        
        # Filled circle for each time
        circle = Circle((t, 0), 0.8, color=color, alpha=0.5, ec='black', lw=2)
        ax.add_patch(circle)
        
        ax.text(t, 0, label, ha='center', va='center', fontsize=11,
               fontweight='bold', color='white')
    
    # Connection lines showing demon spans all three
    for t in time_points:
        ax.plot([t, t], [-1.2, 1.2], 'k--', alpha=0.3, lw=1)
    
    # The categorical structure (demon) spans all three
    ax.fill_between(time_points, -1, 1, alpha=0.2, color='purple',
                    label='Categorical Structure\n(The Demon)')
    
    # Measurement event (present) highlighted
    ax.add_patch(Circle((0, 0), 0.3, color='yellow', ec='red', lw=3, zorder=10))
    ax.text(0, 0, 'NOW', ha='center', va='center', fontsize=10,
           fontweight='bold', color='red')
    
    # Show information flow
    # Past → Present
    ax.annotate('', xy=(0, 0.5), xytext=(-2, 0.5),
               arrowprops=dict(arrowstyle='->', lw=3, color='red', alpha=0.7))
    ax.text(-1, 0.7, 'Compression', fontsize=9, ha='center', fontweight='bold')
    
    # Future → Present (backward causation)
    ax.annotate('', xy=(0, -0.5), xytext=(2, -0.5),
               arrowprops=dict(arrowstyle='->', lw=3, color='blue', alpha=0.7))
    ax.text(1, -0.7, 'Prediction', fontsize=9, ha='center', fontweight='bold')
    
    # Vertical connections
    ax.plot([-2, 0, 2], [0, 0, 0], 'purple', lw=4, alpha=0.7, marker='o',
           markersize=10, markerfacecolor='yellow', markeredgecolor='black',
           markeredgewidth=2, label='Demon Timeline')
    
    ax.set_xlim(-3, 3)
    ax.set_ylim(-1.5, 1.5)
    ax.set_aspect('equal')
    ax.set_xlabel('Time', fontweight='bold', fontsize=12)
    ax.set_xticks(time_points)
    ax.set_xticklabels(['t-1', 't=0', 't+1'])
    ax.set_yticks([])
    ax.spines['left'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    ax.set_title('Temporal Structure: Demon Spans Past, Present, Future\n(Categories Are Timeless)',
                fontweight='bold', fontsize=14, pad=15)
    
    # Legend
    ax.legend(loc='upper right', frameon=True, shadow=True, fontsize=10)
    
    # Info
    ax.text(0.5, 0.02,
           'The pharmaceutical demon exists in past (learned categories), present (measurement), and future (predictions).\nMeasurement instantiates categorical structure that spans time.',
           transform=ax.transAxes, ha='center', va='bottom', fontsize=9,
           bbox=dict(boxstyle='round,pad=0.4', facecolor='lightyellow', alpha=0.9))

def create_vcs_figure(output_file='virtual_categorical_spectrometer_figure.png'):
    """Main function to create 4-panel figure"""
    print(f"Creating Virtual Categorical Spectrometer visualization...")
    
    fig = plt.figure(figsize=(20, 16))
    fig.suptitle('Virtual Categorical Spectrometer: The Complete Pharmaceutical Maxwell Demon\nNon-Local Measurement Through Categorical Morphisms',
                fontsize=18, fontweight='bold', y=0.995)
    
    # Panel A: Top-left
    ax1 = plt.subplot(2, 2, 1)
    plot_categorical_distance(ax1)
    ax1.text(-0.08, 1.05, 'A', transform=ax1.transAxes,
            fontsize=24, fontweight='bold', va='top')
    
    # Panel B: Top-right
    ax2 = plt.subplot(2, 2, 2)
    plot_nonlocal_measurement(ax2)
    ax2.text(-0.08, 1.05, 'B', transform=ax2.transAxes,
            fontsize=24, fontweight='bold', va='top')
    
    # Panel C: Bottom-left
    ax3 = plt.subplot(2, 2, 3)
    plot_observer_observed_unity(ax3)
    ax3.text(-0.08, 1.05, 'C', transform=ax3.transAxes,
            fontsize=24, fontweight='bold', va='top')
    
    # Panel D: Bottom-right
    ax4 = plt.subplot(2, 2, 4)
    plot_temporal_structure(ax4)
    ax4.text(-0.08, 1.05, 'D', transform=ax4.transAxes,
            fontsize=24, fontweight='bold', va='top')
    
    plt.tight_layout(rect=[0, 0, 1, 0.99])
    plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"[OK] Figure saved to {output_file}")
    plt.close()
    
    return fig

# Run
if __name__ == "__main__":
    import sys
    import os
    
    output_file = 'virtual_categorical_spectrometer_figure.png'
    
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    
    output_dir = os.path.dirname(output_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    create_vcs_figure(output_file)

