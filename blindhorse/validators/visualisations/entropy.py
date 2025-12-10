import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.patches import FancyBboxPatch

plt.style.use('seaborn-v0_8-paper')
sns.set_palette("husl")
plt.rcParams['figure.figsize'] = (16, 12)
plt.rcParams['font.size'] = 10

def load_data(json_file):
    with open(json_file, 'r') as f:
        return json.load(f)

def plot_3d_sentropy_space(ax, data):
    """Panel A: 3D S-entropy Space"""
    coords = data['coordinates']
    
    # Extract coordinates (lowercase keys!)
    sk = np.array([c['s_knowledge'] for c in coords])
    st = np.array([c['s_time'] for c in coords])
    se = np.array([c['s_entropy'] for c in coords])
    labels = [c['label'] for c in coords]
    
    # Create scatter plot
    scatter = ax.scatter(sk, st, se, c=se, cmap='viridis', s=100, alpha=0.7, edgecolors='black', linewidth=1.5)
    
    # Add labels for key points
    for i, label in enumerate(labels):
        if 'CPU' in label or 'Screen' in label or 'WiFi' in label:
            ax.text(sk[i], st[i], se[i], '  '+label.replace('_', '\n'), fontsize=7, alpha=0.8)
    
    ax.set_xlabel('S_knowledge', fontweight='bold', fontsize=11)
    ax.set_ylabel('S_time', fontweight='bold', fontsize=11)
    ax.set_zlabel('S_entropy', fontweight='bold', fontsize=11)
    ax.set_title('S-Entropy Coordinate Space',
                fontweight='bold', fontsize=14)
    
    # Add colorbar
    plt.colorbar(scatter, ax=ax, label='S_entropy', shrink=0.5, pad=0.1)
    
    # Add grid
    ax.grid(True, alpha=0.3)

def plot_metric_space_properties(ax, data):
    """Panel B: Metric Space Triangle Inequality Tests"""
    metric_data = data['space_properties']['metric_space']
    
    # Data
    tests = metric_data['triangle_inequality_tests']
    satisfied = metric_data['triangle_inequality_satisfied']
    failed = tests - satisfied
    
    # Create pie chart
    sizes = [satisfied, failed]
    colors = ['#2ecc71', '#e74c3c']
    labels = [f'Satisfied: {satisfied}', f'Failed: {failed}']
    explode = (0.1, 0 if failed > 0 else 0)
    
    wedges, texts, autotexts = ax.pie(sizes, explode=explode, labels=labels, colors=colors,
                                       autopct='%1.1f%%', shadow=True, startangle=90,
                                       textprops={'fontsize': 11, 'fontweight': 'bold'})
    
    ax.set_title('Triangle Inequality Validation\n(Metric Space Property)',
                fontweight='bold', fontsize=14)
    
    # Add validation note
    is_metric = metric_data['is_metric_space']
    note = "✓ Valid Metric Space" if is_metric else "✗ Not a Metric Space"
    ax.text(0, -1.3, note, ha='center', fontsize=12,
            bbox=dict(boxstyle='round,pad=0.5', 
                     facecolor='lightgreen' if is_metric else 'lightcoral', alpha=0.7))

def plot_dimensional_analysis(ax, data):
    """Panel C: Dimensional Analysis (PCA Variance)"""
    dim_data = data['space_properties']['dimensionality']
    
    # Explained variance
    variances = [
        dim_data['explained_variance_pc1'],
        dim_data['explained_variance_pc2'],
        dim_data['explained_variance_pc3']
    ]
    components = ['PC1\n(S_knowledge)', 'PC2\n(S_time)', 'PC3\n(S_entropy)']
    
    # Create bar plot
    colors = ['#3498db', '#e74c3c', '#2ecc71']
    bars = ax.bar(components, variances, color=colors, alpha=0.7, edgecolor='black', linewidth=2)
    
    # Add value labels
    for bar, var in zip(bars, variances):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{var:.1%}',
                ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    ax.set_ylabel('Explained Variance', fontweight='bold', fontsize=12)
    ax.set_title('PCA: Effective Dimensionality',
                fontweight='bold', fontsize=14)
    ax.grid(axis='y', alpha=0.3)
    ax.set_ylim(0, 1.0)
    
    # Add cumulative variance line
    cumulative = np.cumsum(variances)
    ax2 = ax.twinx()
    ax2.plot(components, cumulative, 'ro-', linewidth=2, markersize=10, label='Cumulative')
    ax2.set_ylabel('Cumulative Variance', fontweight='bold', fontsize=12, color='red')
    ax2.tick_params(axis='y', labelcolor='red')
    ax2.set_ylim(0, 1.0)
    ax2.legend(loc='center right', fontsize=10)
    
    # Add effective dimensions note
    eff_dims = dim_data['effective_dimensions']
    note = f"Effective Dimensions: {eff_dims}"
    ax.text(0.5, 0.95, note, transform=ax.transAxes, ha='center', va='top',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.7),
            fontsize=11, fontweight='bold')

def plot_categorical_richness(ax, data):
    """Panel D: Oxygen State Utilization"""
    richness = data['space_properties']['categorical_richness']
    
    # Data
    utilized = richness['oxygen_states_utilized']
    total = richness['claim_oxygen_states']
    unused = total - utilized
    
    # Create stacked bar
    categories = ['O₂ Quantum States']
    utilized_pct = (utilized / total) * 100
    unused_pct = (unused / total) * 100
    
    ax.barh(categories, utilized_pct, color='#2ecc71', alpha=0.7, edgecolor='black', linewidth=2,
            label=f'Utilized: {utilized}')
    ax.barh(categories, unused_pct, left=utilized_pct, color='#ecf0f1', alpha=0.7,
            edgecolor='black', linewidth=2, label=f'Unused: {unused}')
    
    # Add percentage labels
    ax.text(utilized_pct/2, 0, f'{utilized_pct:.1f}%\n({utilized})',
            ha='center', va='center', fontsize=11, fontweight='bold')
    ax.text(utilized_pct + unused_pct/2, 0, f'{unused_pct:.1f}%\n({unused})',
            ha='center', va='center', fontsize=11, fontweight='bold')
    
    ax.set_xlabel('Utilization (%)', fontweight='bold', fontsize=12)
    ax.set_title('Categorical Richness: O₂ States (25,110 total)',
                fontweight='bold', fontsize=14)
    ax.set_xlim(0, 100)
    ax.legend(loc='upper right', fontsize=10)
    ax.grid(axis='x', alpha=0.3)
    
    # Add richness ratio
    ratio = richness['richness_ratio']
    note = f"Richness Ratio: {ratio:.1%}\nS_knowledge Range: {richness['s_knowledge_range']:.2f}"
    ax.text(0.5, -0.3, note, transform=ax.transAxes, ha='center', va='top',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='lightyellow', alpha=0.7),
            fontsize=10)

def create_sentropy_figure(json_file, output_file='sentropy_figure.png'):
    """Main function to create 4-panel figure"""
    print(f"Loading data from {json_file}...")
    data = load_data(json_file)
    
    fig = plt.figure(figsize=(16, 12))
    fig.suptitle('S-Entropy Coordinate System Validation',
                fontsize=16, fontweight='bold', y=0.995)
    
    # Panel A: Top-left (3D plot)
    ax1 = fig.add_subplot(2, 2, 1, projection='3d')
    plot_3d_sentropy_space(ax1, data)
    ax1.text2D(-0.1, 1.05, 'A', transform=ax1.transAxes,
              fontsize=20, fontweight='bold', va='top')
    
    # Panel B: Top-right
    ax2 = plt.subplot(2, 2, 2)
    plot_metric_space_properties(ax2, data)
    ax2.text(-0.1, 1.05, 'B', transform=ax2.transAxes,
            fontsize=20, fontweight='bold', va='top')
    
    # Panel C: Bottom-left
    ax3 = plt.subplot(2, 2, 3)
    plot_dimensional_analysis(ax3, data)
    ax3.text(-0.1, 1.05, 'C', transform=ax3.transAxes,
            fontsize=20, fontweight='bold', va='top')
    
    # Panel D: Bottom-right
    ax4 = plt.subplot(2, 2, 4)
    plot_categorical_richness(ax4, data)
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
    json_file = 'public/sentropy_results.json'
    output_file = 'sentropy_figure.png'
    
    # Override with command line args if provided
    if len(sys.argv) > 1:
        json_file = sys.argv[1]
    if len(sys.argv) > 2:
        output_file = sys.argv[2]
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_file) if os.path.dirname(output_file) else '.', exist_ok=True)
    
    create_sentropy_figure(json_file, output_file)
