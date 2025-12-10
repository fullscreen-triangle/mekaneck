import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.patches import Rectangle, FancyBboxPatch

plt.style.use('seaborn-v0_8-paper')
sns.set_palette("husl")
plt.rcParams['figure.figsize'] = (16, 12)
plt.rcParams['font.size'] = 10

def load_data(json_file):
    with open(json_file, 'r') as f:
        return json.load(f)

def plot_frequency_spectrum(ax, data):
    """Panel A: Hardware Frequency Spectrum (Log Scale)"""
    freqs_data = data['frequencies']

    sources = [f['source'] for f in freqs_data]
    freqs = np.array([f['frequency_hz'] for f in freqs_data])
    uncertainties = np.array([f['uncertainty_hz'] for f in freqs_data])

    # Sort by frequency
    sort_idx = np.argsort(freqs)
    sources = [sources[i] for i in sort_idx]
    freqs = freqs[sort_idx]
    uncertainties = uncertainties[sort_idx]

    # Create bar chart
    x = np.arange(len(sources))
    colors = plt.cm.viridis(np.linspace(0, 1, len(sources)))

    bars = ax.bar(x, freqs, color=colors, alpha=0.7,
                  edgecolor='white', linewidth=2,
                  yerr=uncertainties, capsize=5, error_kw={'linewidth': 2})

    ax.set_yscale('log')
    ax.set_ylabel('Frequency (Hz, log scale)', fontweight='bold')
    ax.set_xlabel('Hardware Source', fontweight='bold')
    ax.set_title('Hardware Oscillation Spectrum: 11+ Orders of Magnitude',
                fontweight='bold', fontsize=14)
    ax.set_xticks(x)
    ax.set_xticklabels(sources, rotation=45, ha='right')
    ax.grid(True, alpha=0.3, axis='y')

    # Add frequency labels on bars
    for i, (bar, freq) in enumerate(zip(bars, freqs)):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
               f'{freq:.2e} Hz',
               ha='center', va='bottom', fontsize=8, rotation=0)

    # Add coverage annotation
    coverage = np.log10(freqs.max()) - np.log10(freqs.min())
    ax.text(0.02, 0.98, f'Frequency Coverage:\n{coverage:.1f} orders of magnitude',
           transform=ax.transAxes, fontsize=11, fontweight='bold',
           verticalalignment='top',
           bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7))

def plot_biological_mapping(ax, data):
    """Panel B: Hardware-to-Biology Frequency Mapping"""
    freqs_data = data['frequencies']

    # Extract data
    sources = [f['source'] for f in freqs_data]
    freqs = np.array([f['frequency_hz'] for f in freqs_data])
    bio_scales = [f['biological_scale'] for f in freqs_data]

    # Define biological hierarchy
    bio_hierarchy = {
        'Cellular_Signaling_1_Hz': (1, 1),
        'Enzymatic_Catalysis_10^3_Hz': (1e3, 2),
        'Conformational_Changes_10^9_Hz': (1e9, 3),
        'Protein_Conformational_10^12_Hz': (1e12, 4),
        'Vibrational_Modes_10^13_Hz': (1e13, 5),
        'Electronic_Transitions_10^14_Hz': (1e14, 6),
        'Quantum_Coherence_10^15_Hz': (1e15, 7)
    }

    # Clear axis and set limits
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 8)
    ax.axis('off')

    # Draw biological hierarchy levels
    for bio_scale, (freq, level) in bio_hierarchy.items():
        # Draw level box
        rect = FancyBboxPatch((0.5, level-0.3), 4, 0.6,
                             boxstyle="round,pad=0.05",
                             facecolor=plt.cm.Blues(level/7),
                             edgecolor='white', linewidth=2, alpha=0.6)
        ax.add_patch(rect)

        # Add label
        label = bio_scale.replace('_', ' ')
        ax.text(2.5, level, label, ha='center', va='center',
               fontsize=9, fontweight='bold', color='white')

    # Draw hardware sources and connections
    colors = plt.cm.viridis(np.linspace(0, 1, len(sources)))

    for i, (source, freq, bio_scale, color) in enumerate(zip(sources, freqs, bio_scales, colors)):
        # Find biological level
        if bio_scale in bio_hierarchy:
            bio_freq, bio_level = bio_hierarchy[bio_scale]

            # Draw hardware box
            hw_y = 0.5 + i * 7.0 / len(sources)
            hw_rect = FancyBboxPatch((5.5, hw_y-0.2), 3.5, 0.4,
                                    boxstyle="round,pad=0.05",
                                    facecolor=color, edgecolor='white',
                                    linewidth=2, alpha=0.7)
            ax.add_patch(hw_rect)

            # Add hardware label
            ax.text(7.25, hw_y, source, ha='center', va='center',
                   fontsize=8, fontweight='bold', color='white')

            # Draw connection arrow
            ax.annotate('', xy=(4.5, bio_level), xytext=(5.5, hw_y),
                       arrowprops=dict(arrowstyle='->', lw=2,
                                     color=color, alpha=0.5))

    # Add title
    ax.text(5, 7.5, 'Hardware → Biology Frequency Mapping',
           ha='center', fontsize=14, fontweight='bold')

    # Add legend
    ax.text(0.5, 0.3, 'Biological\nHierarchy', ha='left', va='center',
           fontsize=10, fontweight='bold',
           bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.5))
    ax.text(7.25, 0.3, 'Hardware\nOscillators', ha='center', va='center',
           fontsize=10, fontweight='bold',
           bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.5))

def plot_uncertainty_analysis(ax, data):
    """Panel C: Measurement Uncertainty Analysis"""
    freqs_data = data['frequencies']

    sources = [f['source'] for f in freqs_data]
    freqs = np.array([f['frequency_hz'] for f in freqs_data])
    uncertainties = np.array([f['uncertainty_hz'] for f in freqs_data])

    # Calculate relative uncertainty (%)
    rel_uncertainties = (uncertainties / freqs) * 100

    # Sort by frequency
    sort_idx = np.argsort(freqs)
    sources = [sources[i] for i in sort_idx]
    freqs = freqs[sort_idx]
    rel_uncertainties = rel_uncertainties[sort_idx]

    # Create horizontal bar chart
    y = np.arange(len(sources))
    colors = plt.cm.RdYlGn_r(rel_uncertainties / rel_uncertainties.max())

    bars = ax.barh(y, rel_uncertainties, color=colors, alpha=0.7,
                   edgecolor='white', linewidth=2)

    ax.set_xlabel('Relative Uncertainty (%)', fontweight='bold')
    ax.set_ylabel('Hardware Source', fontweight='bold')
    ax.set_title('Measurement Uncertainty by Source',
                fontweight='bold', fontsize=14)
    ax.set_yticks(y)
    ax.set_yticklabels(sources)
    ax.grid(True, alpha=0.3, axis='x')

    # Add value labels
    for i, (bar, val) in enumerate(zip(bars, rel_uncertainties)):
        width = bar.get_width()
        ax.text(width + 0.1, bar.get_y() + bar.get_height()/2.,
               f'{val:.2f}%',
               ha='left', va='center', fontsize=9, fontweight='bold')

    # Add statistics
    mean_unc = np.mean(rel_uncertainties)
    max_unc = np.max(rel_uncertainties)
    min_unc = np.min(rel_uncertainties)

    stats_text = f'Mean: {mean_unc:.2f}%\nMax: {max_unc:.2f}%\nMin: {min_unc:.2f}%'
    ax.text(0.98, 0.98, stats_text, transform=ax.transAxes,
           fontsize=10, verticalalignment='top', horizontalalignment='right',
           bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

    # Add quality threshold line
    ax.axvline(1.0, color='green', linestyle='--', linewidth=2,
              label='1% Threshold', alpha=0.7)
    ax.legend(loc='lower right', frameon=True, shadow=True)

def plot_measurement_methods(ax, data):
    """Panel D: Measurement Methods Distribution"""
    freqs_data = data['frequencies']

    # Count measurement methods
    methods = {}
    for f in freqs_data:
        method = f['measurement_method']
        if method not in methods:
            methods[method] = {'count': 0, 'sources': [], 'freqs': []}
        methods[method]['count'] += 1
        methods[method]['sources'].append(f['source'])
        methods[method]['freqs'].append(f['frequency_hz'])

    # Prepare data
    method_names = list(methods.keys())
    counts = [methods[m]['count'] for m in method_names]

    # Create pie chart with nested information
    colors = plt.cm.Set3(np.linspace(0, 1, len(method_names)))

    wedges, texts, autotexts = ax.pie(counts, labels=method_names, autopct='%1.1f%%',
                                       colors=colors, startangle=90,
                                       textprops={'fontsize': 10, 'fontweight': 'bold'},
                                       wedgeprops={'edgecolor': 'white', 'linewidth': 2})

    # Make percentage text white and bold
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontsize(11)
        autotext.set_fontweight('bold')

    ax.set_title('Hardware Measurement Methods Distribution',
                fontweight='bold', fontsize=14)

    # Add legend with details
    legend_labels = []
    for method, data_dict in methods.items():
        freq_range = f"{min(data_dict['freqs']):.1e} - {max(data_dict['freqs']):.1e} Hz"
        legend_labels.append(f"{method}\n({data_dict['count']} sources)\n{freq_range}")

    ax.legend(legend_labels, loc='center left', bbox_to_anchor=(1, 0, 0.5, 1),
             frameon=True, shadow=True, fontsize=8)

def create_hardware_oscillation_figure(json_file, output_file='hardware_oscillation_figure.png'):
    """Main function to create 4-panel figure"""
    data = load_data(json_file)

    fig = plt.figure(figsize=(16, 12))
    fig.suptitle('Hardware Oscillation Harvesting: Zero-Cost Frequency Spectrum Validation',
                fontsize=16, fontweight='bold', y=0.995)

    # Panel A: Top-left
    ax1 = plt.subplot(2, 2, 1)
    plot_frequency_spectrum(ax1, data)
    ax1.text(-0.1, 1.05, 'A', transform=ax1.transAxes,
            fontsize=20, fontweight='bold', va='top')

    # Panel B: Top-right
    ax2 = plt.subplot(2, 2, 2)
    plot_biological_mapping(ax2, data)
    ax2.text(-0.1, 1.05, 'B', transform=ax2.transAxes,
            fontsize=20, fontweight='bold', va='top')

    # Panel C: Bottom-left
    ax3 = plt.subplot(2, 2, 3)
    plot_uncertainty_analysis(ax3, data)
    ax3.text(-0.1, 1.05, 'C', transform=ax3.transAxes,
            fontsize=20, fontweight='bold', va='top')

    # Panel D: Bottom-right
    ax4 = plt.subplot(2, 2, 4)
    plot_measurement_methods(ax4, data)
    ax4.text(-0.1, 1.05, 'D', transform=ax4.transAxes,
            fontsize=20, fontweight='bold', va='top')

    plt.tight_layout(rect=[0, 0, 1, 0.99])
    plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"✓ Figure saved to {output_file}")
    plt.close()

    return fig

# Run
if __name__ == "__main__":
    create_hardware_oscillation_figure('hardware_oscillation_results.json')
