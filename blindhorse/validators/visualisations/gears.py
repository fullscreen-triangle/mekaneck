import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

plt.style.use('seaborn-v0_8-paper')
sns.set_palette("husl")
plt.rcParams['figure.figsize'] = (16, 12)
plt.rcParams['font.size'] = 10

def load_data(json_file):
    with open(json_file, 'r') as f:
        return json.load(f)

def plot_gear_ratio_distribution(ax, data):
    """Panel A: Gear Ratio Distribution"""
    test_cases = data['test_cases']

    drugs = [t['drug'] for t in test_cases]
    gear_ratios = np.array([t['gear_ratio'] for t in test_cases])

    # Create histogram
    n, bins, patches = ax.hist(gear_ratios, bins=15, alpha=0.7, color='#3498db',
                               edgecolor='white', linewidth=2, density=True)

    # Fit distribution
    mu, sigma = gear_ratios.mean(), gear_ratios.std()
    x = np.linspace(gear_ratios.min(), gear_ratios.max(), 100)
    y = stats.norm.pdf(x, mu, sigma)
    ax.plot(x, y, 'r-', linewidth=3, label=f'Normal fit\nμ={mu:.0f}, σ={sigma:.0f}')

    # Add mean line
    ax.axvline(mu, color='red', linestyle='--', linewidth=2, label=f'Mean: {mu:.0f}')

    ax.set_xlabel('Gear Ratio (G)', fontweight='bold')
    ax.set_ylabel('Probability Density', fontweight='bold')
    ax.set_title('Allosteric Gear Ratio Distribution\nω_therapeutic = G × ω_drug',
                fontweight='bold', fontsize=14)
    ax.legend(loc='upper right', frameon=True, shadow=True)
    ax.grid(True, alpha=0.3, axis='y')

    # Add statistics box
    stats_summary = data['statistics']['gear_ratios']
    stats_text = f"Mean: {stats_summary['mean']:.0f}\n"
    stats_text += f"Std: {stats_summary['std']:.0f}\n"
    stats_text += f"Range: [{min(gear_ratios):.0f}, {max(gear_ratios):.0f}]\n"
    stats_text += f"N: {len(gear_ratios)}"

    ax.text(0.02, 0.98, stats_text, transform=ax.transAxes,
           fontsize=10, verticalalignment='top',
           bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

def plot_pathway_gear_ratios(ax, data):
    """Panel B: Gear Ratios by Pathway"""
    test_cases = data['test_cases']

    # Group by pathway
    pathway_data = {}
    for t in test_cases:
        pathway = t['pathway']
        if pathway not in pathway_data:
            pathway_data[pathway] = []
        pathway_data[pathway].append(t['gear_ratio'])

    # Prepare data
    pathways = list(pathway_data.keys())
    gear_ratios_by_pathway = [pathway_data[p] for p in pathways]

    # Create violin plot
    parts = ax.violinplot(gear_ratios_by_pathway, positions=range(len(pathways)),
                          widths=0.7, showmeans=True, showmedians=True)

    # Color violins
    colors = plt.cm.Set2(np.linspace(0, 1, len(pathways)))
    for i, pc in enumerate(parts['bodies']):
        pc.set_facecolor(colors[i])
        pc.set_alpha(0.7)

    # Overlay box plots
    bp = ax.boxplot(gear_ratios_by_pathway, positions=range(len(pathways)),
                    widths=0.3, patch_artist=True, showfliers=False)

    for i, (box, color) in enumerate(zip(bp['boxes'], colors)):
        box.set_facecolor(color)
        box.set_alpha(0.5)

    # Add individual points
    for i, (pathway, ratios) in enumerate(zip(pathways, gear_ratios_by_pathway)):
        x = np.random.normal(i, 0.04, size=len(ratios))
        ax.scatter(x, ratios, alpha=0.6, s=80, color='black', edgecolors='white', linewidths=1)

    ax.set_xlabel('Therapeutic Pathway', fontweight='bold')
    ax.set_ylabel('Gear Ratio (G)', fontweight='bold')
    ax.set_title('Pathway-Specific Gear Ratio Distributions',
                fontweight='bold', fontsize=14)
    ax.set_xticks(range(len(pathways)))
    ax.set_xticklabels(pathways, rotation=45, ha='right')
    ax.grid(True, alpha=0.3, axis='y')

    # Add pathway statistics
    for i, (pathway, ratios) in enumerate(zip(pathways, gear_ratios_by_pathway)):
        mean_val = np.mean(ratios)
        ax.text(i, ax.get_ylim()[1]*0.95, f'{mean_val:.0f}',
               ha='center', fontsize=9, fontweight='bold',
               bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.5))

def plot_frequency_vs_response(ax, data):
    """Panel C: Drug Frequency vs Response Time"""
    test_cases = data['test_cases']

    freqs = np.array([t['drug_frequency_hz'] for t in test_cases]) / 1e12  # Convert to THz
    responses = np.array([t['measured_response_hr'] for t in test_cases])
    gear_ratios = np.array([t['gear_ratio'] for t in test_cases])
    drugs = [t['drug'] for t in test_cases]
    pathways = [t['pathway'] for t in test_cases]

    # Get unique pathways and colors
    unique_pathways = list(set(pathways))
    colors = plt.cm.tab10(np.linspace(0, 1, len(unique_pathways)))
    pathway_colors = {pathway: colors[i] for i, pathway in enumerate(unique_pathways)}

    # Scatter plot with bubble size = gear ratio
    for i, (f, r, g, drug, pathway) in enumerate(zip(freqs, responses, gear_ratios, drugs, pathways)):
        ax.scatter(f, r, s=g/5, alpha=0.6, color=pathway_colors[pathway],
                  edgecolors='white', linewidths=2)
        ax.annotate(drug, (f, r), xytext=(5, 5), textcoords='offset points',
                   fontsize=7, alpha=0.7)

    ax.set_xlabel('Drug Frequency (THz)', fontweight='bold')
    ax.set_ylabel('Response Time (hours)', fontweight='bold')
    ax.set_title('Drug Frequency vs Therapeutic Response Time\n(Bubble size ∝ gear ratio)',
                fontweight='bold', fontsize=14)
    ax.grid(True, alpha=0.3)

    # Add pathway legend
    handles = [plt.Line2D([0], [0], marker='o', color='w',
                         markerfacecolor=pathway_colors[p], markersize=10, label=p)
              for p in unique_pathways]
    ax.legend(handles=handles, title='Pathway', loc='upper right',
             frameon=True, shadow=True)

    # Add gear ratio size legend
    size_legend_ratios = [1000, 2000, 3000]
    for ratio in size_legend_ratios:
        ax.scatter([], [], s=ratio/5, c='gray', alpha=0.6,
                  label=f'G = {ratio}')
    ax.legend(loc='lower left', frameon=True, shadow=True, title='Gear Ratio')

def plot_gear_mechanism(ax, data):
    """Panel D: Gear Mechanism Schematic"""
    # Clear axis
    ax.axis('off')
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)

    # Title
    ax.text(5, 9.5, 'Allosteric Gear Network Mechanism',
           ha='center', fontsize=14, fontweight='bold')

    # Draw drug frequency input
    drug_circle = plt.Circle((2, 7), 0.8, color='#e74c3c', alpha=0.7,
                            edgecolor='white', linewidth=3)
    ax.add_patch(drug_circle)
    ax.text(2, 7, 'ω_drug', ha='center', va='center',
           fontsize=12, fontweight='bold', color='white')
    ax.text(2, 5.5, 'Drug\nFrequency', ha='center', va='top',
           fontsize=9, fontweight='bold')

    # Draw gear box
    gear_rect = plt.Rectangle((4, 6), 2, 2, facecolor='#f39c12', alpha=0.7,
                             edgecolor='white', linewidth=3)
    ax.add_patch(gear_rect)
    ax.text(5, 7, 'G', ha='center', va='center',
           fontsize=16, fontweight='bold', color='white')
    ax.text(5, 5.5, 'Allosteric\nGear Network', ha='center', va='top',
           fontsize=9, fontweight='bold')

    # Draw therapeutic frequency output
    therapeutic_circle = plt.Circle((8, 7), 0.8, color='#2ecc71', alpha=0.7,
                                   edgecolor='white', linewidth=3)
    ax.add_patch(therapeutic_circle)
    ax.text(8, 7, 'ω_ther', ha='center', va='center',
           fontsize=11, fontweight='bold', color='white')
    ax.text(8, 5.5, 'Therapeutic\nFrequency', ha='center', va='top',
           fontsize=9, fontweight='bold')

    # Draw arrows
    ax.annotate('', xy=(4, 7), xytext=(2.8, 7),
               arrowprops=dict(arrowstyle='->', lw=3, color='black'))
    ax.annotate('', xy=(7.2, 7), xytext=(6, 7),
               arrowprops=dict(arrowstyle='->', lw=3, color='black'))

    # Add equation
    ax.text(5, 4, 'ω_therapeutic = G × ω_drug',
           ha='center', fontsize=14, fontweight='bold',
           bbox=dict(boxstyle='round,pad=0.8', facecolor='yellow', alpha=0.7))

    # Add example calculation
    stats = data['statistics']
    stats_gr = data['statistics']['gear_ratios']
    example_text = f"Example:\nG_mean = {stats_gr['mean']:.0f}\n"
    example_text += f"ω_drug = 40 THz\n"
    example_text += f"ω_ther = {stats_gr['mean']:.0f} × 40 THz\n"
    example_text += f"       = {stats_gr['mean']*40:.1e} Hz"

    ax.text(5, 2, example_text, ha='center', va='center',
           fontsize=10, family='monospace',
           bbox=dict(boxstyle='round,pad=0.5', facecolor='lightblue', alpha=0.7))

    # Add mechanism notes
    notes = "Mechanism:\n1. Drug binds at allosteric site\n2. Conformational change propagates\n3. Frequency transformed by gear ratio\n4. Therapeutic effect at target site"
    ax.text(0.5, 3, notes, ha='left', va='center', fontsize=8,
           bbox=dict(boxstyle='round,pad=0.5', facecolor='wheat', alpha=0.7))

def create_gear_ratio_figure(json_file, output_file='gear_ratio_figure.png'):
    """Main function to create 4-panel figure"""
    data = load_data(json_file)

    fig = plt.figure(figsize=(16, 12))
    fig.suptitle('Allosteric Gear Ratio Validation: Frequency Transformation Mechanism',
                fontsize=16, fontweight='bold', y=0.995)

    # Panel A: Top-left
    ax1 = plt.subplot(2, 2, 1)
    plot_gear_ratio_distribution(ax1, data)
    ax1.text(-0.1, 1.05, 'A', transform=ax1.transAxes,
            fontsize=20, fontweight='bold', va='top')

    # Panel B: Top-right
    ax2 = plt.subplot(2, 2, 2)
    plot_pathway_gear_ratios(ax2, data)
    ax2.text(-0.1, 1.05, 'B', transform=ax2.transAxes,
            fontsize=20, fontweight='bold', va='top')

    # Panel C: Bottom-left
    ax3 = plt.subplot(2, 2, 3)
    plot_frequency_vs_response(ax3, data)
    ax3.text(-0.1, 1.05, 'C', transform=ax3.transAxes,
            fontsize=20, fontweight='bold', va='top')

    # Panel D: Bottom-right
    ax4 = plt.subplot(2, 2, 4)
    plot_gear_mechanism(ax4, data)
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
    json_file = 'public/gear_ratio_results.json'
    output_file = 'gear_ratio_figure.png'
    
    # Override with command line args if provided
    if len(sys.argv) > 1:
        json_file = sys.argv[1]
    if len(sys.argv) > 2:
        output_file = sys.argv[2]
    
    # Ensure output directory exists
    output_dir = os.path.dirname(output_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    create_gear_ratio_figure(json_file, output_file)
