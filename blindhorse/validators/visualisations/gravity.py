import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.patches import Circle, FancyArrowPatch, Wedge
from mpl_toolkits.mplot3d import Axes3D

plt.style.use('seaborn-v0_8-paper')
sns.set_palette("husl")
plt.rcParams['figure.figsize'] = (16, 12)
plt.rcParams['font.size'] = 10

def load_data(json_file):
    with open(json_file, 'r') as f:
        return json.load(f)

def plot_complexity_landscape(ax, data):
    """Panel A: Complexity Reduction Landscape"""
    results = data['complexity_reduction']['results']
    
    # Filter valid data
    sizes = []
    exhaustive_ops = []
    semantic_ops = []
    
    for r in results:
        sizes.append(r['problem_size'])
        ex = r['exhaustive_ops'] if r['exhaustive_ops'] is not None else np.nan
        exhaustive_ops.append(ex)
        semantic_ops.append(r['semantic_ops'])
    
    # Plot both complexities
    ax.semilogy(sizes, exhaustive_ops, 'o-', color='#e74c3c', linewidth=3, 
               markersize=10, markeredgecolor='white', markeredgewidth=2,
               label='Exhaustive O(n!)', zorder=3)
    ax.semilogy(sizes, semantic_ops, 's-', color='#2ecc71', linewidth=3,
               markersize=10, markeredgecolor='white', markeredgewidth=2,
               label='Semantic O(log n)', zorder=3)
    
    ax.set_xlabel('Problem Size (N)', fontweight='bold', fontsize=12)
    ax.set_ylabel('Operations Required (log scale)', fontweight='bold', fontsize=12)
    ax.set_title('Complexity Landscape: Exhaustive vs Semantic Navigation',
                fontweight='bold', fontsize=14)
    ax.legend(loc='upper left', frameon=True, shadow=True, fontsize=11)
    ax.grid(True, alpha=0.3, linestyle='--')
    
    # Add crossing region annotation
    ax.fill_between(sizes[:4], 1, 1e20, alpha=0.2, color='green',
                    label='Semantic Advantage')
    
    # Add complexity class labels
    ax.text(0.95, 0.95, 'O(n!) ≈ Exhaustive Search\nO(log n) ≈ Semantic Gravity',
           transform=ax.transAxes, ha='right', va='top', fontsize=10,
           bbox=dict(boxstyle='round,pad=0.5', facecolor='lightyellow', alpha=0.8))

def plot_speedup_growth(ax, data):
    """Panel B: Speedup Factor Growth"""
    results = data['complexity_reduction']['results']
    
    # Filter valid speedups
    sizes = []
    speedups = []
    for r in results:
        if r['speedup'] is not None:
            sizes.append(r['problem_size'])
            speedups.append(r['speedup'])
    
    if not sizes:
        ax.text(0.5, 0.5, 'No valid speedup data', ha='center', va='center',
               transform=ax.transAxes, fontsize=14)
        return
    
    # Create area plot
    ax.fill_between(sizes, 0, speedups, alpha=0.6, color='#3498db')
    ax.plot(sizes, speedups, 'o-', color='#2c3e50', linewidth=3,
           markersize=10, markeredgecolor='white', markeredgewidth=2)
    
    ax.set_xlabel('Problem Size (N)', fontweight='bold', fontsize=12)
    ax.set_ylabel('Speedup Factor', fontweight='bold', fontsize=12)
    ax.set_title('Semantic Gravity Speedup\nSpeedup = O(n!) / O(log n)',
                fontweight='bold', fontsize=14)
    ax.set_yscale('log')
    ax.grid(True, alpha=0.3)
    
    # Annotate maximum speedup
    max_speedup = max(speedups)
    max_size = sizes[speedups.index(max_speedup)]
    ax.annotate(f'Max: {max_speedup:.2e}×\nat N={max_size}',
               xy=(max_size, max_speedup), xytext=(max_size * 0.6, max_speedup * 0.3),
               fontsize=11, fontweight='bold',
               bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.8),
               arrowprops=dict(arrowstyle='->', lw=2.5, color='red'))

def plot_semantic_attractor(ax, data):
    """Panel C: Semantic Attractor Basin"""
    ax.axis('off')
    ax.set_xlim(-1.5, 1.5)
    ax.set_ylim(-1.5, 1.5)
    ax.set_aspect('equal')
    
    # Draw attractor basin (circular potential well)
    theta = np.linspace(0, 2*np.pi, 100)
    
    # Multiple concentric circles showing potential levels
    for i, r in enumerate(np.linspace(1.3, 0.3, 8)):
        color_intensity = 1 - (i / 8)
        circle = Circle((0, 0), r, fill=False, edgecolor=plt.cm.Blues(color_intensity),
                       linewidth=2, alpha=0.7)
        ax.add_patch(circle)
    
    # Fill center (attractor)
    center_circle = Circle((0, 0), 0.25, color='#2ecc71', alpha=0.8,
                          edgecolor='black', linewidth=2.5)
    ax.add_patch(center_circle)
    ax.text(0, 0, 'Healthy\nState', ha='center', va='center',
           fontsize=10, fontweight='bold', color='white')
    
    # Draw example trajectories (pathological → healthy)
    n_trajectories = 6
    for i in range(n_trajectories):
        angle = i * 2 * np.pi / n_trajectories
        start_x = 1.3 * np.cos(angle)
        start_y = 1.3 * np.sin(angle)
        
        # Spiral trajectory towards center
        t = np.linspace(0, 1, 50)
        traj_r = 1.3 * (1 - t) + 0.25 * t
        traj_angle = angle + t * np.pi * 2  # Spiral
        traj_x = traj_r * np.cos(traj_angle)
        traj_y = traj_r * np.sin(traj_angle)
        
        ax.plot(traj_x, traj_y, color='#e74c3c', linewidth=2, alpha=0.6)
        
        # Start marker (pathological state)
        ax.scatter(start_x, start_y, s=100, color='#e74c3c', 
                  edgecolors='black', linewidths=2, zorder=5, marker='x')
        
        # Arrow at end
        ax.annotate('', xy=(0.25*np.cos(traj_angle[-1]), 0.25*np.sin(traj_angle[-1])),
                   xytext=(traj_x[-2], traj_y[-2]),
                   arrowprops=dict(arrowstyle='->', lw=2, color='#e74c3c'))
    
    # Title
    ax.text(0, 1.45, 'Semantic Gravity Field',
           ha='center', fontsize=14, fontweight='bold')
    
    # Add labels
    ax.text(0, -1.55, 'Trajectories: Pathological → Healthy',
           ha='center', fontsize=10, style='italic')
    
    # Add navigation stats
    nav_data = data.get('therapeutic_navigation', {})
    success_rate = nav_data.get('success_rate', 0) * 100
    ax.text(-1.3, 1.3, f'Success Rate:\n{success_rate:.0f}%',
           ha='center', fontsize=10, fontweight='bold',
           bbox=dict(boxstyle='round,pad=0.4', facecolor='lightblue', alpha=0.8))

def plot_information_gradient(ax, data):
    """Panel D: Information Gradient Field"""
    results = data['complexity_reduction']['results']
    
    # Create a field showing information gradient
    x = np.linspace(-3, 3, 20)
    y = np.linspace(-3, 3, 20)
    X, Y = np.meshgrid(x, y)
    
    # Gradient points towards center (semantic attractor)
    U = -X / (X**2 + Y**2 + 0.5)  # Gradient field
    V = -Y / (X**2 + Y**2 + 0.5)
    
    # Normalize
    magnitude = np.sqrt(U**2 + V**2)
    U = U / magnitude
    V = V / magnitude
    
    # Plot vector field
    ax.quiver(X, Y, U, V, magnitude, cmap='viridis', alpha=0.6, scale=25)
    
    # Add contours showing "potential"
    potential = np.log(X**2 + Y**2 + 1)
    contours = ax.contour(X, Y, potential, levels=10, colors='gray', 
                          alpha=0.3, linewidths=1)
    
    # Highlight center
    center = Circle((0, 0), 0.3, color='red', alpha=0.8,
                   edgecolor='black', linewidth=2.5, zorder=5)
    ax.add_patch(center)
    ax.text(0, 0, 'Target', ha='center', va='center',
           fontsize=10, fontweight='bold', color='white', zorder=6)
    
    ax.set_xlabel('Semantic Dimension 1', fontweight='bold', fontsize=12)
    ax.set_ylabel('Semantic Dimension 2', fontweight='bold', fontsize=12)
    ax.set_title('Information Gradient: ∇S(x) Points to Attractor',
                fontweight='bold', fontsize=14)
    ax.set_xlim(-3, 3)
    ax.set_ylim(-3, 3)
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)
    
    # Add equation
    eq_text = "∇S = -dS/dr · r̂\nSemantics flows downhill"
    ax.text(0.98, 0.98, eq_text, transform=ax.transAxes,
           ha='right', va='top', fontsize=10, family='monospace',
           bbox=dict(boxstyle='round,pad=0.5', facecolor='lightyellow', alpha=0.8))

def create_semantic_gravity_figure(json_file, output_file='semantic_gravity_figure.png'):
    """Main function to create 4-panel figure"""
    print(f"Loading data from {json_file}...")
    data = load_data(json_file)
    
    fig = plt.figure(figsize=(16, 12))
    fig.suptitle('Semantic Gravity Validation: O(log n) Navigation in Therapeutic Space',
                fontsize=16, fontweight='bold', y=0.995)
    
    # Panel A: Top-left
    ax1 = plt.subplot(2, 2, 1)
    plot_complexity_landscape(ax1, data)
    ax1.text(-0.1, 1.05, 'A', transform=ax1.transAxes,
            fontsize=20, fontweight='bold', va='top')
    
    # Panel B: Top-right
    ax2 = plt.subplot(2, 2, 2)
    plot_speedup_growth(ax2, data)
    ax2.text(-0.1, 1.05, 'B', transform=ax2.transAxes,
            fontsize=20, fontweight='bold', va='top')
    
    # Panel C: Bottom-left
    ax3 = plt.subplot(2, 2, 3)
    plot_semantic_attractor(ax3, data)
    ax3.text(-0.1, 1.05, 'C', transform=ax3.transAxes,
            fontsize=20, fontweight='bold', va='top')
    
    # Panel D: Bottom-right
    ax4 = plt.subplot(2, 2, 4)
    plot_information_gradient(ax4, data)
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
    
    # Default paths
    json_file = 'public/semantic_gravity_results.json'
    output_file = 'semantic_gravity_figure.png'
    
    # Override with command line args if provided
    if len(sys.argv) > 1:
        json_file = sys.argv[1]
    if len(sys.argv) > 2:
        output_file = sys.argv[2]
    
    # Ensure output directory exists
    output_dir = os.path.dirname(output_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    create_semantic_gravity_figure(json_file, output_file)
