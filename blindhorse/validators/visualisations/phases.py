import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.patches import Circle, FancyArrowPatch, Wedge

plt.style.use('seaborn-v0_8-paper')
sns.set_palette("husl")
plt.rcParams['figure.figsize'] = (16, 12)
plt.rcParams['font.size'] = 10

def load_data(json_file):
    with open(json_file, 'r') as f:
        return json.load(f)

def plot_drug_coupling_modification(ax, data):
    """Panel A: Drug-Modified Coupling Strength"""
    results = data['drug_modified_coupling']['results']

    drugs = [r['drug'] for r in results]
    K_baseline = [r['K_baseline'] for r in results]
    K_modified = [r['K_modified'] for r in results]
    K_expected = [r['K_expected'] for r in results]

    x = np.arange(len(drugs))
    width = 0.25

    # Create grouped bar chart
    bars1 = ax.bar(x - width, K_baseline, width, label='Baseline',
                   color='#95a5a6', alpha=0.8, edgecolor='black', linewidth=1.5)
    bars2 = ax.bar(x, K_modified, width, label='Drug-Modified',
                   color='#3498db', alpha=0.8, edgecolor='black', linewidth=1.5)
    bars3 = ax.bar(x + width, K_expected, width, label='Expected',
                   color='#2ecc71', alpha=0.8, edgecolor='black', linewidth=1.5)

    ax.set_xlabel('Drug', fontweight='bold', fontsize=12)
    ax.set_ylabel('Coupling Strength (K)', fontweight='bold', fontsize=12)
    ax.set_title('Drug-Modified Coupling Strength\nΔK = K_drug - K_baseline',
                fontweight='bold', fontsize=14)
    ax.set_xticks(x)
    ax.set_xticklabels(drugs, rotation=0)
    ax.legend(loc='upper right', frameon=True, shadow=True)
    ax.grid(axis='y', alpha=0.3)

    # Add delta K annotations
    for i, drug in enumerate(drugs):
        delta_K = K_modified[i] - K_baseline[i]
        color = 'green' if delta_K > 0 else 'red'
        ax.text(i, max(K_modified[i], K_expected[i]) + 0.2,
                f'ΔK={delta_K:+.1f}',
                ha='center', fontsize=9, color=color, fontweight='bold')

def plot_coherence_evolution(ax, data):
    """Panel B: Phase Coherence Evolution"""
    results = data['drug_modified_coupling']['results']

    drugs = [r['drug'] for r in results]
    R_baseline = [r['R_baseline'] for r in results]
    R_drug = [r['R_drug'] for r in results]
    coherence_change = [r['coherence_change'] for r in results]

    # Create scatter plot with arrows
    x_base = np.arange(len(drugs))

    for i, drug in enumerate(drugs):
        # Plot baseline
        ax.scatter(x_base[i], R_baseline[i], s=200, color='#95a5a6',
                  alpha=0.7, edgecolors='black', linewidths=2, zorder=3, marker='o')
        # Plot drug-modified
        ax.scatter(x_base[i], R_drug[i], s=200, color='#e74c3c' if coherence_change[i] < 0 else '#2ecc71',
                  alpha=0.7, edgecolors='black', linewidths=2, zorder=3, marker='s')

        # Draw arrow showing change
        ax.annotate('', xy=(x_base[i], R_drug[i]), xytext=(x_base[i], R_baseline[i]),
                   arrowprops=dict(arrowstyle='->', lw=2.5,
                                 color='red' if coherence_change[i] < 0 else 'green'))

        # Label with change
        mid_y = (R_baseline[i] + R_drug[i]) / 2
        ax.text(x_base[i] + 0.15, mid_y,
                f'{coherence_change[i]:+.3f}',
                fontsize=9, fontweight='bold')

    # Add therapeutic threshold
    ax.axhline(0.7, color='blue', linestyle='--', linewidth=2.5,
              label='Therapeutic Threshold (R=0.7)', alpha=0.7)

    ax.set_xlabel('Drug', fontweight='bold', fontsize=12)
    ax.set_ylabel('Phase Coherence (R)', fontweight='bold', fontsize=12)
    ax.set_title('Phase Coherence: Baseline → Drug-Modified',
                fontweight='bold', fontsize=14)
    ax.set_xticks(x_base)
    ax.set_xticklabels(drugs)
    ax.set_ylim(0, 1)
    ax.legend(loc='upper right', frameon=True, shadow=True)
    ax.grid(axis='y', alpha=0.3)

    # Custom legend
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], marker='o', color='w', markerfacecolor='#95a5a6',
               markersize=10, label='Baseline', markeredgecolor='black', markeredgewidth=1.5),
        Line2D([0], [0], marker='s', color='w', markerfacecolor='#2ecc71',
               markersize=10, label='Drug (Improved)', markeredgecolor='black', markeredgewidth=1.5),
        Line2D([0], [0], color='blue', linestyle='--', linewidth=2, label='Therapeutic R=0.7')
    ]
    ax.legend(handles=legend_elements, loc='lower right', frameon=True, shadow=True)

def plot_information_transfer_rate(ax, data):
    """Panel C: Information Transfer Rate"""
    info_data = data['information_transfer']

    R_values = [item['R'] for item in info_data]
    bit_rates = [item['information_rate_bits_per_sec'] for item in info_data]

    # Create line plot
    ax.plot(R_values, bit_rates, 'o-', color='#3498db', linewidth=3,
           markersize=10, markeredgecolor='white', markeredgewidth=2, label='Bit Rate')

    # Fill area under curve
    ax.fill_between(R_values, 0, bit_rates, alpha=0.3, color='#3498db')

    # Add therapeutic threshold
    threshold_idx = np.where(np.array(R_values) >= 0.7)[0]
    if len(threshold_idx) > 0:
        ax.axvline(0.7, color='red', linestyle='--', linewidth=2.5,
                  label='Therapeutic Threshold', alpha=0.7)
        # Highlight therapeutic region
        therapeutic_R = [r for r in R_values if r >= 0.7]
        therapeutic_rates = [bit_rates[i] for i, r in enumerate(R_values) if r >= 0.7]
        if therapeutic_R:
            ax.fill_between(therapeutic_R, 0, therapeutic_rates,
                           alpha=0.5, color='green', label='Therapeutic Region')

    ax.set_xlabel('Phase Coherence (R)', fontweight='bold', fontsize=12)
    ax.set_ylabel('Bit Rate (bits/s)', fontweight='bold', fontsize=12)
    ax.set_title('Information Transfer Rate\nI = B × log₂(1 + SNR × R²)',
                fontweight='bold', fontsize=14)
    ax.legend(loc='upper left', frameon=True, shadow=True)
    ax.grid(True, alpha=0.3)

    # Add max rate annotation
    max_rate = max(bit_rates)
    max_R = R_values[bit_rates.index(max_rate)]
    ax.annotate(f'Max: {max_rate:.0f} bits/s\nat R={max_R:.3f}',
               xy=(max_R, max_rate), xytext=(max_R - 0.1, max_rate * 0.7),
               fontsize=10, fontweight='bold',
               bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.7),
               arrowprops=dict(arrowstyle='->', lw=2))

def plot_kuramoto_model_schematic(ax, data):
    """Panel D: Kuramoto Phase-Lock Model"""
    ax.axis('off')
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)

    # Title
    ax.text(5, 9.5, 'Kuramoto Phase-Lock Model',
           ha='center', fontsize=14, fontweight='bold')

    # Draw oscillators in a network
    n_oscillators = 5
    radius = 2.5
    center = (5, 5.5)

    angles = np.linspace(0, 2*np.pi, n_oscillators, endpoint=False)

    # Draw all coupling connections first (background)
    for i in range(n_oscillators):
        x_i = center[0] + radius * np.cos(angles[i])
        y_i = center[1] + radius * np.sin(angles[i])
        for j in range(i+1, n_oscillators):
            x_j = center[0] + radius * np.cos(angles[j])
            y_j = center[1] + radius * np.sin(angles[j])
            ax.plot([x_i, x_j], [y_i, y_j], 'gray', alpha=0.3, linewidth=1.5, zorder=1)

    # Draw oscillators
    for i, angle in enumerate(angles):
        x = center[0] + radius * np.cos(angle)
        y = center[1] + radius * np.sin(angle)

        # Oscillator circle
        circle = Circle((x, y), 0.4, color=plt.cm.viridis(i/n_oscillators),
                       alpha=0.8, edgecolor='black', linewidth=2.5, zorder=3)
        ax.add_patch(circle)
        ax.text(x, y, f'θ_{i+1}', ha='center', va='center',
               fontsize=11, fontweight='bold', color='white', zorder=4)

    # Add governing equation
    eq_text = "dθᵢ/dt = ωᵢ + (K/N) Σⱼ sin(θⱼ - θᵢ)"
    ax.text(5, 2, eq_text, ha='center', fontsize=12, fontweight='bold',
           family='monospace',
           bbox=dict(boxstyle='round,pad=0.5', facecolor='lightyellow',
                    alpha=0.8, edgecolor='black', linewidth=2))

    # Add order parameter box
    order_text = "Order Parameter R:\nR = |⟨exp(iθ)⟩|\n\nR → 1: Synchronized\nR → 0: Incoherent"
    ax.text(8.8, 5.5, order_text, ha='center', va='center', fontsize=9,
           bbox=dict(boxstyle='round,pad=0.5', facecolor='lightblue',
                    alpha=0.8, edgecolor='black', linewidth=2))

    # Add drug effect box
    drug_text = "Drug Action:\nK_baseline → K_drug\n\nΔK > 0: Enhanced\nR > 0.7: Therapeutic"
    ax.text(1.2, 5.5, drug_text, ha='center', va='center', fontsize=9,
           bbox=dict(boxstyle='round,pad=0.5', facecolor='lightgreen',
                    alpha=0.8, edgecolor='black', linewidth=2))

    # Add legend
    legend_text = "K: Coupling | ωᵢ: Natural Frequency | θᵢ: Phase | N: Oscillators"
    ax.text(5, 0.7, legend_text, ha='center', fontsize=8, style='italic')

def create_phase_lock_figure(json_file, output_file='phase_lock_figure.png'):
    """Main function to create 4-panel figure"""
    print(f"Loading data from {json_file}...")
    data = load_data(json_file)

    fig = plt.figure(figsize=(16, 12))
    fig.suptitle('Phase-Lock Dynamics Validation: Kuramoto Model Drug Action',
                fontsize=16, fontweight='bold', y=0.995)

    # Panel A: Top-left
    ax1 = plt.subplot(2, 2, 1)
    plot_drug_coupling_modification(ax1, data)
    ax1.text(-0.1, 1.05, 'A', transform=ax1.transAxes,
            fontsize=20, fontweight='bold', va='top')

    # Panel B: Top-right
    ax2 = plt.subplot(2, 2, 2)
    plot_coherence_evolution(ax2, data)
    ax2.text(-0.1, 1.05, 'B', transform=ax2.transAxes,
            fontsize=20, fontweight='bold', va='top')

    # Panel C: Bottom-left
    ax3 = plt.subplot(2, 2, 3)
    plot_information_transfer_rate(ax3, data)
    ax3.text(-0.1, 1.05, 'C', transform=ax3.transAxes,
            fontsize=20, fontweight='bold', va='top')

    # Panel D: Bottom-right
    ax4 = plt.subplot(2, 2, 4)
    plot_kuramoto_model_schematic(ax4, data)
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
    json_file = 'public/phase_lock_results.json'
    output_file = 'phase_lock_figure.png'

    # Override with command line args if provided
    if len(sys.argv) > 1:
        json_file = sys.argv[1]
    if len(sys.argv) > 2:
        output_file = sys.argv[2]

    # Ensure output directory exists
    output_dir = os.path.dirname(output_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    create_phase_lock_figure(json_file, output_file)
