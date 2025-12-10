import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from matplotlib.patches import Rectangle

plt.style.use('seaborn-v0_8-paper')
sns.set_palette("husl")
plt.rcParams['figure.figsize'] = (16, 12)
plt.rcParams['font.size'] = 10

def load_data(json_file):
    with open(json_file, 'r') as f:
        return json.load(f)

def plot_predicted_vs_known(ax, data):
    """Panel A: Predicted vs Known Efficacy"""
    predictions = data['accuracy_test']['predictions']
    
    # Extract data
    known = np.array([p['known_efficacy'] for p in predictions])
    predicted = np.array([p['predicted_efficacy'] for p in predictions])
    errors = np.array([p['efficacy_error'] for p in predictions])
    names = [p['drug_name'] for p in predictions]
    
    # Get pathways from test_drugs
    drug_pathways = {drug['name']: drug['target_pathway'] for drug in data['test_drugs']}
    pathways = [drug_pathways.get(name, 'Unknown') for name in names]
    
    # Get unique pathways and assign colors
    unique_pathways = list(set(pathways))
    colors = plt.cm.tab10(np.linspace(0, 1, len(unique_pathways)))
    pathway_colors = {pathway: colors[i] for i, pathway in enumerate(unique_pathways)}
    
    # Plot perfect prediction line
    ax.plot([0, 1], [0, 1], 'k--', linewidth=2, label='Perfect Prediction', alpha=0.5)
    
    # Plot points with error bars
    for i, (k, p, e, name, pathway) in enumerate(zip(known, predicted, errors, names, pathways)):
        ax.errorbar(k, p, yerr=e, fmt='o', markersize=12,
                   color=pathway_colors[pathway], capsize=5, capthick=2,
                   alpha=0.7, linewidth=2)
        ax.annotate(name.replace('_', ' '), (k, p), xytext=(5, 5), textcoords='offset points',
                   fontsize=7, alpha=0.7)
    
    # Compute regression
    slope, intercept, r_value, p_value, std_err = stats.linregress(known, predicted)
    line_x = np.array([0, 1])
    line_y = slope * line_x + intercept
    ax.plot(line_x, line_y, 'r-', linewidth=2,
           label=f'Fit: y={slope:.2f}x+{intercept:.2f}, R²={r_value**2:.3f}')
    
    ax.set_xlabel('Known Efficacy', fontweight='bold', fontsize=12)
    ax.set_ylabel('Predicted Efficacy', fontweight='bold', fontsize=12)
    ax.set_title('Therapeutic Prediction Accuracy',
                fontweight='bold', fontsize=14)
    ax.legend(loc='upper left', fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(-0.05, 1.05)
    ax.set_ylim(-0.05, 1.05)
    
    # Add accuracy box
    accuracy = data['accuracy_test']['accuracy']
    ax.text(0.95, 0.05, f'Accuracy: {accuracy:.1%}',
            transform=ax.transAxes, ha='right', va='bottom',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='lightgreen', alpha=0.7),
            fontsize=11, fontweight='bold')

def plot_error_distribution(ax, data):
    """Panel B: Error Distribution"""
    predictions = data['accuracy_test']['predictions']
    errors = np.array([p['efficacy_error'] for p in predictions])
    
    # Create histogram
    n, bins, patches = ax.hist(errors, bins=15, edgecolor='black', alpha=0.7, color='#3498db')
    
    # Color bars based on magnitude
    for i, patch in enumerate(patches):
        if bins[i] < 0.1:
            patch.set_facecolor('green')
        elif bins[i] < 0.2:
            patch.set_facecolor('orange')
        else:
            patch.set_facecolor('red')
    
    # Add vertical line for mean
    mean_error = np.mean(errors)
    ax.axvline(mean_error, color='red', linestyle='--', linewidth=2, label=f'Mean: {mean_error:.3f}')
    
    # Add vertical line for target (88% accuracy = 12% error)
    target_error = 0.12
    ax.axvline(target_error, color='green', linestyle='--', linewidth=2, label=f'Target: {target_error:.3f}')
    
    ax.set_xlabel('Efficacy Error (|Predicted - Known|)', fontweight='bold', fontsize=12)
    ax.set_ylabel('Frequency', fontweight='bold', fontsize=12)
    ax.set_title('Prediction Error Distribution',
                fontweight='bold', fontsize=14)
    ax.legend(loc='upper right', fontsize=10)
    ax.grid(axis='y', alpha=0.3)

def plot_speedup_comparison(ax, data):
    """Panel C: Computational Speedup"""
    speedup_data = data['speedup_test']
    
    # Data
    methods = ['MD Simulation\n(Traditional)', 'PharmBMD\n(Framework)']
    times = [
        speedup_data['md_simulation_time_seconds'],
        speedup_data['pharmbmd_prediction_time_seconds']
    ]
    
    # Create bar plot (log scale)
    bars = ax.bar(methods, times, color=['#e74c3c', '#2ecc71'], alpha=0.7, edgecolor='black', linewidth=2)
    
    # Add value labels
    for bar, time in zip(bars, times):
        height = bar.get_height()
        label = f'{time:.0f}s' if time >= 1 else f'{time*1000:.1f}ms'
        ax.text(bar.get_x() + bar.get_width()/2., height,
                label,
                ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    ax.set_yscale('log')
    ax.set_ylabel('Computation Time (seconds, log scale)', fontweight='bold', fontsize=12)
    ax.set_title('Computational Speedup vs MD Simulation',
                fontweight='bold', fontsize=14)
    ax.grid(axis='y', alpha=0.3)
    
    # Add speedup annotation
    speedup = speedup_data['speedup_factor']
    ax.text(0.5, 0.95, f'Speedup: {speedup:.0f}×',
            transform=ax.transAxes, ha='center', va='top',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.7),
            fontsize=13, fontweight='bold')

def plot_pathway_accuracy(ax, data):
    """Panel D: Per-Pathway Accuracy"""
    predictions = data['accuracy_test']['predictions']
    
    # Get pathways from test_drugs
    drug_pathways = {drug['name']: drug['target_pathway'] for drug in data['test_drugs']}
    
    # Group by pathway
    pathway_stats = {}
    for pred in predictions:
        name = pred['drug_name']
        pathway = drug_pathways.get(name, 'Unknown')
        error = pred['efficacy_error']
        
        if pathway not in pathway_stats:
            pathway_stats[pathway] = []
        pathway_stats[pathway].append(error)
    
    # Calculate mean and std for each pathway
    pathways = list(pathway_stats.keys())
    mean_errors = [np.mean(pathway_stats[p]) for p in pathways]
    std_errors = [np.std(pathway_stats[p]) if len(pathway_stats[p]) > 1 else 0 for p in pathways]
    
    # Sort by mean error
    sorted_indices = np.argsort(mean_errors)
    pathways = [pathways[i] for i in sorted_indices]
    mean_errors = [mean_errors[i] for i in sorted_indices]
    std_errors = [std_errors[i] for i in sorted_indices]
    
    # Color based on error
    colors = ['green' if e < 0.1 else 'orange' if e < 0.2 else 'red' for e in mean_errors]
    
    # Create horizontal bar plot
    y_pos = np.arange(len(pathways))
    bars = ax.barh(y_pos, mean_errors, xerr=std_errors, color=colors, alpha=0.7,
                   edgecolor='black', linewidth=2, capsize=5)
    
    # Add value labels
    for i, (bar, mean, std) in enumerate(zip(bars, mean_errors, std_errors)):
        width = bar.get_width()
        label = f'{mean:.3f}'
        if std > 0:
            label += f' ± {std:.3f}'
        ax.text(width + max(std_errors)*0.1, i, label,
                ha='left', va='center', fontsize=9, fontweight='bold')
    
    ax.set_yticks(y_pos)
    ax.set_yticklabels(pathways)
    ax.set_xlabel('Mean Efficacy Error', fontweight='bold', fontsize=12)
    ax.set_title('Accuracy by Target Pathway',
                fontweight='bold', fontsize=14)
    ax.grid(axis='x', alpha=0.3)
    
    # Add target line
    ax.axvline(0.12, color='green', linestyle='--', linewidth=2, alpha=0.5, label='Target (88% acc)')
    ax.legend(loc='lower right', fontsize=9)

def create_therapeutic_figure(json_file, output_file='therapeutic_prediction_figure.png'):
    """Main function to create 4-panel figure"""
    print(f"Loading data from {json_file}...")
    data = load_data(json_file)
    
    fig = plt.figure(figsize=(16, 12))
    fig.suptitle('Therapeutic Prediction Validation: End-to-End Pipeline',
                fontsize=16, fontweight='bold', y=0.995)
    
    # Panel A: Top-left
    ax1 = plt.subplot(2, 2, 1)
    plot_predicted_vs_known(ax1, data)
    ax1.text(-0.1, 1.05, 'A', transform=ax1.transAxes,
            fontsize=20, fontweight='bold', va='top')
    
    # Panel B: Top-right
    ax2 = plt.subplot(2, 2, 2)
    plot_error_distribution(ax2, data)
    ax2.text(-0.1, 1.05, 'B', transform=ax2.transAxes,
            fontsize=20, fontweight='bold', va='top')
    
    # Panel C: Bottom-left
    ax3 = plt.subplot(2, 2, 3)
    plot_speedup_comparison(ax3, data)
    ax3.text(-0.1, 1.05, 'C', transform=ax3.transAxes,
            fontsize=20, fontweight='bold', va='top')
    
    # Panel D: Bottom-right
    ax4 = plt.subplot(2, 2, 4)
    plot_pathway_accuracy(ax4, data)
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
    json_file = 'public/therapeutic_prediction_results.json'
    output_file = 'therapeutic_prediction_figure.png'
    
    # Override with command line args if provided
    if len(sys.argv) > 1:
        json_file = sys.argv[1]
    if len(sys.argv) > 2:
        output_file = sys.argv[2]
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_file) if os.path.dirname(output_file) else '.', exist_ok=True)
    
    create_therapeutic_figure(json_file, output_file)
