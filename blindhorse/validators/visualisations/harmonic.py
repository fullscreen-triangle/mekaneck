import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx
from matplotlib.patches import Circle

plt.style.use('seaborn-v0_8-paper')
sns.set_palette("husl")
plt.rcParams['figure.figsize'] = (16, 12)
plt.rcParams['font.size'] = 10

def load_data(json_file):
    try:
        with open(json_file, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"Warning: JSON decode error at line {e.lineno}: {e.msg}")
        print("Loading partial data...")
        # Try to load what we can
        with open(json_file, 'r') as f:
            content = f.read()
            # Find the last valid closing brace
            last_brace = content.rfind('}')
            if last_brace > 0:
                # Try to parse up to the last valid brace
                valid_content = content[:last_brace+1]
                return json.loads(valid_content)
        raise

def plot_node_expansion(ax, data):
    """Panel A: Harmonic Expansion to 1950 Nodes"""
    params = data['parameters']
    expansion = data['harmonic_expansion']
    
    # Show progression from base to harmonics
    base_freq = params['num_base_frequencies']
    n_harmonics = params['n_max_harmonics']
    total_nodes = expansion['num_nodes']
    
    # Create bar chart showing expansion
    categories = ['Base\nFrequencies', 'Harmonics\n(up to 150th)', 'Total\nNodes']
    values = [base_freq, n_harmonics, total_nodes]
    colors = ['#3498db', '#e74c3c', '#2ecc71']
    
    bars = ax.bar(categories, values, color=colors, alpha=0.7, 
                  edgecolor='black', linewidth=2)
    
    # Add value labels
    for bar, val in zip(bars, values):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(val)}',
                ha='center', va='bottom', fontsize=14, fontweight='bold')
    
    ax.set_ylabel('Count', fontweight='bold', fontsize=12)
    ax.set_title('Harmonic Expansion: Base → 1950 Nodes\nf_n = n × f_base (n = 1, 2, ..., 150)',
                fontweight='bold', fontsize=14)
    ax.grid(axis='y', alpha=0.3)
    
    # Add expansion factor
    expansion_factor = total_nodes / base_freq
    ax.text(0.5, 0.95, f'Expansion Factor: {expansion_factor:.0f}×',
           transform=ax.transAxes, ha='center', va='top',
           bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.8),
           fontsize=12, fontweight='bold')
    
    # Add claim validation
    claim_val = expansion['claim_value']
    error = expansion['relative_error']
    validation_text = f"Claim: {claim_val} nodes\nError: {error:.1%}"
    validation_color = 'lightgreen' if error < 0.1 else 'lightyellow'
    ax.text(0.95, 0.05, validation_text,
           transform=ax.transAxes, ha='right', va='bottom',
           bbox=dict(boxstyle='round,pad=0.4', facecolor=validation_color, alpha=0.8),
           fontsize=10)

def plot_network_topology(ax, data):
    """Panel B: Network Topology Statistics"""
    topo = data['topology']
    
    # Create visualization of key statistics
    stats = {
        'Nodes': topo['num_nodes'],
        'Edges': topo['num_edges'],
        'Components': topo['num_components'],
        'Largest\nComponent': topo['largest_component_size']
    }
    
    x = np.arange(len(stats))
    values = list(stats.values())
    labels = list(stats.keys())
    
    # Normalize for visualization (log scale colors)
    colors = plt.cm.viridis(np.log10(values) / np.log10(max(values)))
    
    bars = ax.bar(x, values, color=colors, alpha=0.7, edgecolor='black', linewidth=2)
    
    # Add value labels
    for i, (bar, val) in enumerate(zip(bars, values)):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{val:,}',
                ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel('Count (log scale)', fontweight='bold', fontsize=12)
    ax.set_yscale('log')
    ax.set_title('Harmonic Network Topology',
                fontweight='bold', fontsize=14)
    ax.grid(axis='y', alpha=0.3)
    
    # Add degree statistics
    deg_stats = f"Avg Degree: {topo['average_degree']:.1f}\nDensity: {topo['density']:.1%}\nClustering: {topo['avg_clustering']:.1%}"
    ax.text(0.02, 0.98, deg_stats, transform=ax.transAxes,
           ha='left', va='top', fontsize=10,
           bbox=dict(boxstyle='round,pad=0.4', facecolor='lightblue', alpha=0.8))

def plot_degree_distribution(ax, data):
    """Panel C: Degree Distribution"""
    deg_dist = data['topology']['degree_distribution']
    topo = data['topology']
    
    # Create box plot representation
    stats = [deg_dist['min'], deg_dist['q25'], deg_dist['median'], 
             deg_dist['q75'], deg_dist['max']]
    positions = [1, 2, 3, 4, 5]
    labels = ['Min', 'Q25', 'Median', 'Q75', 'Max']
    
    # Plot bars
    colors = plt.cm.RdYlGn(np.linspace(0.2, 0.8, 5))
    bars = ax.bar(positions, stats, color=colors, alpha=0.7,
                  edgecolor='black', linewidth=2)
    
    # Add value labels
    for bar, val in zip(bars, stats):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{val:.0f}',
                ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    ax.set_xticks(positions)
    ax.set_xticklabels(labels)
    ax.set_ylabel('Degree (Connections)', fontweight='bold', fontsize=12)
    ax.set_title('Node Degree Distribution\n(Harmonic Coincidences)',
                fontweight='bold', fontsize=14)
    ax.set_yscale('log')
    ax.grid(axis='y', alpha=0.3)
    
    # Add average line
    avg_deg = topo['average_degree']
    ax.axhline(avg_deg, color='red', linestyle='--', linewidth=2.5,
              label=f'Mean: {avg_deg:.0f}', alpha=0.7)
    ax.legend(loc='upper left', frameon=True, shadow=True)
    
    # Add interpretation
    interp_text = f"High degree nodes:\nFrequency hubs\nStrong coincidence"
    ax.text(0.95, 0.95, interp_text, transform=ax.transAxes,
           ha='right', va='top', fontsize=10,
           bbox=dict(boxstyle='round,pad=0.4', facecolor='lightyellow', alpha=0.8))

def plot_enhancement_factor(ax, data):
    """Panel D: Graph Enhancement Factor"""
    enhancement = data['enhancement']
    
    # Components of enhancement factor
    k_avg = enhancement['k_avg']
    rho = enhancement['rho']
    F_graph = enhancement['F_graph']
    F_claim = enhancement['claim_value']
    
    # Create schematic showing multiplication
    ax.axis('off')
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    
    # Title
    ax.text(5, 9.5, 'Graph Enhancement Factor Calculation',
           ha='center', fontsize=14, fontweight='bold')
    
    # Draw boxes for each component
    box1 = plt.Rectangle((1, 6.5), 2.5, 1.5, facecolor='#3498db', 
                         alpha=0.7, edgecolor='black', linewidth=2.5)
    ax.add_patch(box1)
    ax.text(2.25, 7.25, f'⟨k⟩\n{k_avg:.1f}', ha='center', va='center',
           fontsize=12, fontweight='bold', color='white')
    ax.text(2.25, 5.9, 'Average\nDegree', ha='center', fontsize=9)
    
    # Multiplication symbol
    ax.text(3.8, 7.25, '×', ha='center', va='center', fontsize=24, fontweight='bold')
    
    box2 = plt.Rectangle((4.5, 6.5), 2.5, 1.5, facecolor='#e74c3c',
                         alpha=0.7, edgecolor='black', linewidth=2.5)
    ax.add_patch(box2)
    ax.text(5.75, 7.25, f'ρ\n{rho:.2f}', ha='center', va='center',
           fontsize=12, fontweight='bold', color='white')
    ax.text(5.75, 5.9, 'Clustering\nCoefficient', ha='center', fontsize=9)
    
    # Equals
    ax.text(7.5, 7.25, '=', ha='center', va='center', fontsize=24, fontweight='bold')
    
    box3 = plt.Rectangle((8.5, 6.3), 1.3, 1.9, facecolor='#2ecc71',
                         alpha=0.7, edgecolor='black', linewidth=2.5)
    ax.add_patch(box3)
    ax.text(9.15, 7.25, f'F\n{F_graph:.0f}', ha='center', va='center',
           fontsize=12, fontweight='bold', color='white')
    ax.text(9.15, 5.7, 'Enhancement', ha='center', fontsize=9)
    
    # Add formula
    formula = "F_graph = ⟨k⟩ × ρ × N\n\nwhere N = # oscillators"
    ax.text(5, 4.5, formula, ha='center', fontsize=11, family='monospace',
           bbox=dict(boxstyle='round,pad=0.5', facecolor='lightyellow', alpha=0.8))
    
    # Add claim comparison
    error = enhancement['relative_error']
    comparison_text = f"Measured: {F_graph:.0f}\nClaim: {F_claim:,}\nError: {error:.1%}"
    comparison_color = 'lightgreen' if error < 0.5 else 'lightyellow'
    ax.text(5, 2.5, comparison_text, ha='center', fontsize=11, fontweight='bold',
           bbox=dict(boxstyle='round,pad=0.5', facecolor=comparison_color, 
                    alpha=0.8, edgecolor='black', linewidth=2))
    
    # Add interpretation
    interp = "Enhancement: Network amplifies\noscillator interactions\nthrough harmonic resonance"
    ax.text(5, 0.8, interp, ha='center', fontsize=9, style='italic')

def create_harmonic_network_figure(json_file, output_file='harmonic_network_figure.png'):
    """Main function to create 4-panel figure"""
    print(f"Loading data from {json_file}...")
    data = load_data(json_file)
    
    fig = plt.figure(figsize=(16, 12))
    fig.suptitle('Harmonic Coincidence Network Validation: 1950 Nodes, 182K Edges',
                fontsize=16, fontweight='bold', y=0.995)
    
    # Panel A: Top-left
    ax1 = plt.subplot(2, 2, 1)
    plot_node_expansion(ax1, data)
    ax1.text(-0.1, 1.05, 'A', transform=ax1.transAxes,
            fontsize=20, fontweight='bold', va='top')
    
    # Panel B: Top-right
    ax2 = plt.subplot(2, 2, 2)
    plot_network_topology(ax2, data)
    ax2.text(-0.1, 1.05, 'B', transform=ax2.transAxes,
            fontsize=20, fontweight='bold', va='top')
    
    # Panel C: Bottom-left
    ax3 = plt.subplot(2, 2, 3)
    plot_degree_distribution(ax3, data)
    ax3.text(-0.1, 1.05, 'C', transform=ax3.transAxes,
            fontsize=20, fontweight='bold', va='top')
    
    # Panel D: Bottom-right
    ax4 = plt.subplot(2, 2, 4)
    plot_enhancement_factor(ax4, data)
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
    json_file = 'public/harmonic_network_results.json'
    output_file = 'harmonic_network_figure.png'
    
    # Override with command line args if provided
    if len(sys.argv) > 1:
        json_file = sys.argv[1]
    if len(sys.argv) > 2:
        output_file = sys.argv[2]
    
    # Ensure output directory exists
    output_dir = os.path.dirname(output_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    create_harmonic_network_figure(json_file, output_file)

