import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.patches import Rectangle, FancyBboxPatch, FancyArrowPatch

plt.style.use('seaborn-v0_8-paper')
sns.set_palette("husl")
plt.rcParams['figure.figsize'] = (16, 12)
plt.rcParams['font.size'] = 10

def load_data(json_file):
    with open(json_file, 'r') as f:
        return json.load(f)

def plot_enhancement_cascade(ax, data):
    """Panel A: Enhancement Factor Cascade"""
    cascade = data['enhancement_cascade']
    factors = cascade['enhancement_factors']
    
    # Enhancement factors
    names = ['F_graph\n(Network)', 'F_BMD\n(Maxwell)', 'F_cascade\n(Levels)', 'F_total\n(Combined)']
    values = [factors['F_graph'], factors['F_BMD'], factors['F_cascade'], factors['F_total']]
    colors = ['#3498db', '#e74c3c', '#f39c12', '#2ecc71']
    
    # Create bars
    y_pos = np.arange(len(names))
    bars = ax.barh(y_pos, np.log10(values), color=colors, alpha=0.7,
                   edgecolor='black', linewidth=2)
    
    # Add value labels
    for i, (bar, val) in enumerate(zip(bars, values)):
        width = bar.get_width()
        ax.text(width + 0.5, bar.get_y() + bar.get_height()/2.,
                f'{val:.2e}',
                ha='left', va='center', fontsize=11, fontweight='bold')
    
    ax.set_yticks(y_pos)
    ax.set_yticklabels(names)
    ax.set_xlabel('Enhancement Factor (log₁₀)', fontweight='bold', fontsize=12)
    ax.set_title('Enhancement Cascade: Network × BMD × Hierarchy',
                fontweight='bold', fontsize=14)
    ax.grid(axis='x', alpha=0.3)
    
    # Add multiplication schematic
    mult_text = "F_total = F_graph × F_BMD × F_cascade"
    ax.text(0.5, 0.95, mult_text, transform=ax.transAxes,
           ha='center', va='top', fontsize=11, family='monospace',
           bbox=dict(boxstyle='round,pad=0.5', facecolor='lightyellow', alpha=0.8))

def plot_temporal_precision(ax, data):
    """Panel B: Temporal Precision vs Planck Time"""
    cascade = data['enhancement_cascade']
    temporal = cascade['temporal_precision']
    constants = data['physical_constants']
    
    # Key timescales
    t_planck = constants['t_planck_s']
    delta_t = temporal['delta_t_seconds']
    claim_delta_t = temporal['claim_delta_t']
    
    timescales = {
        'Planck\nTime': t_planck,
        'Achieved\nPrecision': delta_t,
        'Claimed\nPrecision': claim_delta_t
    }
    
    labels = list(timescales.keys())
    values = list(timescales.values())
    
    # Plot on log scale
    x_pos = np.arange(len(labels))
    log_values = [np.log10(v) for v in values]
    colors = ['#95a5a6', '#3498db', '#2ecc71']
    
    bars = ax.bar(x_pos, [-log_val for log_val in log_values], 
                  color=colors, alpha=0.7, edgecolor='black', linewidth=2)
    
    # Add value labels
    for i, (bar, val) in enumerate(zip(bars, values)):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{val:.2e} s',
                ha='center', va='bottom', fontsize=10, fontweight='bold', rotation=0)
    
    ax.set_xticks(x_pos)
    ax.set_xticklabels(labels)
    ax.set_ylabel('-log₁₀(Time / seconds)', fontweight='bold', fontsize=12)
    ax.set_title('Temporal Precision: Trans-Planckian Target\nδt < t_Planck',
                fontweight='bold', fontsize=14)
    ax.grid(axis='y', alpha=0.3)
    
    # Add ratio annotation
    ratio = temporal['delta_t_over_t_planck']
    orders = temporal['orders_below_planck']
    status = 'Trans-Planckian' if orders > 0 else 'Sub-Planckian'
    status_color = 'lightgreen' if orders > 0 else 'lightyellow'
    
    ratio_text = f"δt / t_Planck = {ratio:.2e}\nOrders below: {abs(orders):.1f}\nStatus: {status}"
    ax.text(0.02, 0.98, ratio_text, transform=ax.transAxes,
           ha='left', va='top', fontsize=10, fontweight='bold',
           bbox=dict(boxstyle='round,pad=0.5', facecolor=status_color, alpha=0.8))

def plot_heisenberg_bypass(ax, data):
    """Panel C: Heisenberg Uncertainty Bypass"""
    bypass = data['heisenberg_bypass']
    
    # Create schematic comparison
    ax.axis('off')
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    
    # Title
    ax.text(5, 9.5, 'Heisenberg Uncertainty Bypass',
           ha='center', fontsize=14, fontweight='bold')
    
    # Standard quantum measurement (left side)
    box1 = FancyBboxPatch((0.5, 5), 4, 3.5, boxstyle="round,pad=0.1",
                          facecolor='#e74c3c', alpha=0.3, edgecolor='black', linewidth=2.5)
    ax.add_patch(box1)
    ax.text(2.5, 7.8, 'Standard Quantum', ha='center', fontsize=12, fontweight='bold')
    
    std_text = "ΔE · Δt ≥ ħ/2\n\nMeasurement\nbackaction\n\nPhase space\nconstraints"
    ax.text(2.5, 6.5, std_text, ha='center', fontsize=10,
           bbox=dict(boxstyle='round,pad=0.4', facecolor='white', alpha=0.8))
    
    std_limit = bypass['standard_heisenberg_limit_seconds']
    ax.text(2.5, 4.7, f'Δt ≥ {std_limit:.0e} s', ha='center', fontsize=10,
           fontweight='bold', color='red')
    
    # Arrow
    arrow = FancyArrowPatch((4.5, 6.5), (5.5, 6.5),
                           arrowstyle='->', mutation_scale=30, linewidth=3,
                           color='green')
    ax.add_patch(arrow)
    ax.text(5, 7, 'Bypass', ha='center', fontsize=11, fontweight='bold', color='green')
    
    # Categorical measurement (right side)
    box2 = FancyBboxPatch((5.5, 5), 4, 3.5, boxstyle="round,pad=0.1",
                          facecolor='#2ecc71', alpha=0.3, edgecolor='black', linewidth=2.5)
    ax.add_patch(box2)
    ax.text(7.5, 7.8, 'Categorical Access', ha='center', fontsize=12, fontweight='bold')
    
    cat_checks = [
        f"[{'X' if bypass['categorical_access_commutes'] else ' '}] Operators commute",
        f"[{'X' if bypass['zero_backaction'] else ' '}] Zero backaction",
        f"[{'X' if bypass['operates_in_information_space'] else ' '}] Information space",
        f"[{'X' if bypass['orthogonal_to_phase_space'] else ' '}] Orthogonal to phase"
    ]
    cat_text = '\n'.join(cat_checks)
    ax.text(7.5, 6.5, cat_text, ha='center', fontsize=9,
           bbox=dict(boxstyle='round,pad=0.4', facecolor='white', alpha=0.8),
           family='monospace')
    
    ax.text(7.5, 4.7, 'No Δt constraint!', ha='center', fontsize=11,
           fontweight='bold', color='green')
    
    # Add validation status
    validated = bypass['claim_validated']
    status_text = f"Bypass: {'✓ VALIDATED' if validated else '✗ FAILED'}"
    status_color = 'lightgreen' if validated else 'lightcoral'
    ax.text(5, 3.5, status_text, ha='center', fontsize=12, fontweight='bold',
           bbox=dict(boxstyle='round,pad=0.5', facecolor=status_color, 
                    alpha=0.8, edgecolor='black', linewidth=2.5))
    
    # Add key insight
    insight = "Key: Categorical space is orthogonal to phase space\n∴ Heisenberg relation doesn't apply"
    ax.text(5, 1.5, insight, ha='center', fontsize=9, style='italic')

def plot_frequency_amplification(ax, data):
    """Panel D: Frequency Amplification Chain"""
    cascade = data['enhancement_cascade']
    f_base = cascade['f_base_hz']
    f_effective = cascade['f_effective_hz']
    F_total = cascade['enhancement_factors']['F_total']
    
    # Create amplification chain
    ax.axis('off')
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    
    # Title
    ax.text(5, 9.5, 'Frequency Amplification Chain',
           ha='center', fontsize=14, fontweight='bold')
    
    # Base frequency
    box1 = Rectangle((1, 7), 2, 1.2, facecolor='#3498db', alpha=0.7,
                     edgecolor='black', linewidth=2.5)
    ax.add_patch(box1)
    ax.text(2, 7.6, f'f_base\n{f_base/1e9:.1f} GHz', ha='center', va='center',
           fontsize=11, fontweight='bold', color='white')
    
    # Enhancement
    ax.text(3.3, 7.6, '×', ha='center', va='center', fontsize=20, fontweight='bold')
    
    box2 = Rectangle((3.8, 7), 2.4, 1.2, facecolor='#f39c12', alpha=0.7,
                     edgecolor='black', linewidth=2.5)
    ax.add_patch(box2)
    ax.text(5, 7.6, f'F_total\n{F_total:.2e}', ha='center', va='center',
           fontsize=11, fontweight='bold', color='white')
    
    # Result
    ax.text(6.5, 7.6, '=', ha='center', va='center', fontsize=20, fontweight='bold')
    
    box3 = Rectangle((7, 6.8), 2.5, 1.6, facecolor='#2ecc71', alpha=0.7,
                     edgecolor='black', linewidth=2.5)
    ax.add_patch(box3)
    ax.text(8.25, 7.6, f'f_eff\n{f_effective:.2e} Hz', ha='center', va='center',
           fontsize=11, fontweight='bold', color='white')
    
    # Show temporal resolution
    delta_t = 1 / f_effective
    ax.text(5, 5.5, f'Temporal Resolution:\nδt = 1/f_eff = {delta_t:.2e} s',
           ha='center', fontsize=11,
           bbox=dict(boxstyle='round,pad=0.5', facecolor='lightyellow', alpha=0.8))
    
    # Breakdown of enhancement
    factors = cascade['enhancement_factors']
    breakdown = f"Enhancement Breakdown:\n"
    breakdown += f"• Network (F_graph): {factors['F_graph']:,}\n"
    breakdown += f"• Maxwell (F_BMD): {factors['F_BMD']:,}\n"
    breakdown += f"• Cascade (F_cascade): {factors['F_cascade']}\n"
    breakdown += f"━━━━━━━━━━━━━━━\n"
    breakdown += f"• Total: {F_total:.2e}"
    
    ax.text(5, 3, breakdown, ha='center', fontsize=9, family='monospace',
           bbox=dict(boxstyle='round,pad=0.5', facecolor='lightblue', alpha=0.8))
    
    # Add physical interpretation
    interp = "Physical Meaning: Hardware oscillations\namplified through resonant networks\nto achieve ultra-fast temporal sampling"
    ax.text(5, 0.8, interp, ha='center', fontsize=8, style='italic')

def create_trans_planckian_figure(json_file, output_file='trans_planckian_figure.png'):
    """Main function to create 4-panel figure"""
    print(f"Loading data from {json_file}...")
    data = load_data(json_file)
    
    fig = plt.figure(figsize=(16, 12))
    fig.suptitle('Trans-Planckian Temporal Precision: Heisenberg Bypass via Categorical Space',
                fontsize=16, fontweight='bold', y=0.995)
    
    # Panel A: Top-left
    ax1 = plt.subplot(2, 2, 1)
    plot_enhancement_cascade(ax1, data)
    ax1.text(-0.1, 1.05, 'A', transform=ax1.transAxes,
            fontsize=20, fontweight='bold', va='top')
    
    # Panel B: Top-right
    ax2 = plt.subplot(2, 2, 2)
    plot_temporal_precision(ax2, data)
    ax2.text(-0.1, 1.05, 'B', transform=ax2.transAxes,
            fontsize=20, fontweight='bold', va='top')
    
    # Panel C: Bottom-left
    ax3 = plt.subplot(2, 2, 3)
    plot_heisenberg_bypass(ax3, data)
    ax3.text(-0.1, 1.05, 'C', transform=ax3.transAxes,
            fontsize=20, fontweight='bold', va='top')
    
    # Panel D: Bottom-right
    ax4 = plt.subplot(2, 2, 4)
    plot_frequency_amplification(ax4, data)
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
    json_file = 'public/trans_planckian_results.json'
    output_file = 'trans_planckian_figure.png'
    
    # Override with command line args if provided
    if len(sys.argv) > 1:
        json_file = sys.argv[1]
    if len(sys.argv) > 2:
        output_file = sys.argv[2]
    
    # Ensure output directory exists
    output_dir = os.path.dirname(output_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    create_trans_planckian_figure(json_file, output_file)

