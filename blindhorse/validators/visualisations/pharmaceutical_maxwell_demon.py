import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.patches import Circle, Rectangle, FancyArrowPatch, FancyBboxPatch, Wedge
from pathlib import Path

plt.style.use('seaborn-v0_8-paper')
sns.set_palette("husl")
plt.rcParams['figure.figsize'] = (20, 16)
plt.rcParams['font.size'] = 9

def load_all_data(base_dir='public'):
    """Load all validation results"""
    results = {}
    files = {
        'hardware': 'hardware_oscillation_results.json',
        'harmonic': 'harmonic_network_results.json',
        'sentropy': 'sentropy_results.json',
        'gear': 'gear_ratio_results.json',
        'phase': 'phase_lock_results.json',
        'semantic': 'semantic_gravity_results.json',
        'trans': 'trans_planckian_results.json',
        'categorical': 'categorical_state_results.json',
        'therapeutic': 'therapeutic_prediction_results.json'
    }

    for key, filename in files.items():
        try:
            with open(f'{base_dir}/{filename}', 'r') as f:
                results[key] = json.load(f)
        except Exception as e:
            print(f"Warning: Could not load {filename}: {e}")
            results[key] = None

    return results

def plot_framework_architecture(ax, data):
    """Panel A: Complete Framework Architecture"""
    ax.axis('off')
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)

    # Title
    ax.text(5, 9.7, 'Pharmaceutical Maxwell Demon Architecture',
           ha='center', fontsize=15, fontweight='bold')

    # Layer 1: Hardware (Bottom)
    layer1 = FancyBboxPatch((0.5, 0.5), 9, 1.5, boxstyle="round,pad=0.1",
                            facecolor='#3498db', alpha=0.3, edgecolor='black', linewidth=3)
    ax.add_patch(layer1)
    ax.text(5, 1.25, 'Hardware Oscillation Harvesting',
           ha='center', fontsize=12, fontweight='bold')
    if data['hardware']:
        n_freqs = len(data['hardware'].get('frequencies', []))
        ax.text(5, 0.8, f'{n_freqs} oscillators | 11 orders magnitude',
               ha='center', fontsize=9)

    # Layer 2: Harmonic Network
    layer2 = FancyBboxPatch((0.5, 2.3), 9, 1.5, boxstyle="round,pad=0.1",
                            facecolor='#e74c3c', alpha=0.3, edgecolor='black', linewidth=3)
    ax.add_patch(layer2)
    ax.text(5, 3.05, 'Harmonic Coincidence Network',
           ha='center', fontsize=12, fontweight='bold')
    if data['harmonic']:
        nodes = data['harmonic'].get('harmonic_expansion', {}).get('num_nodes', 0)
        edges = data['harmonic'].get('topology', {}).get('num_edges', 0)
        ax.text(5, 2.6, f'{nodes} nodes | {edges:,} edges',
               ha='center', fontsize=9)

    # Layer 3: S-Entropy Space
    layer3 = FancyBboxPatch((0.5, 4.1), 4, 1.5, boxstyle="round,pad=0.1",
                            facecolor='#f39c12', alpha=0.3, edgecolor='black', linewidth=3)
    ax.add_patch(layer3)
    ax.text(2.5, 4.85, 'S-Entropy Coordinates',
           ha='center', fontsize=11, fontweight='bold')
    ax.text(2.5, 4.4, '3D categorical space',
           ha='center', fontsize=9)

    # Layer 3b: Maxwell Demon
    layer3b = FancyBboxPatch((5.5, 4.1), 4, 1.5, boxstyle="round,pad=0.1",
                             facecolor='#9b59b6', alpha=0.3, edgecolor='black', linewidth=3)
    ax.add_patch(layer3b)
    ax.text(7.5, 4.85, 'Maxwell Demon',
           ha='center', fontsize=11, fontweight='bold')
    ax.text(7.5, 4.4, '3-stage information sorting',
           ha='center', fontsize=9)

    # Layer 4: Therapeutic Mechanisms
    layer4 = FancyBboxPatch((0.5, 5.9), 4, 1.5, boxstyle="round,pad=0.1",
                            facecolor='#1abc9c', alpha=0.3, edgecolor='black', linewidth=3)
    ax.add_patch(layer4)
    ax.text(2.5, 6.65, 'Gear Networks',
           ha='center', fontsize=11, fontweight='bold')
    if data['gear']:
        n_cases = len(data['gear'].get('test_cases', []))
        ax.text(2.5, 6.2, f'{n_cases} pathways tested',
               ha='center', fontsize=9)

    # Layer 4b: Phase Lock
    layer4b = FancyBboxPatch((5.5, 5.9), 4, 1.5, boxstyle="round,pad=0.1",
                             facecolor='#e67e22', alpha=0.3, edgecolor='black', linewidth=3)
    ax.add_patch(layer4b)
    ax.text(7.5, 6.65, 'Phase-Lock Dynamics',
           ha='center', fontsize=11, fontweight='bold')
    if data['phase']:
        n_drugs = len(data['phase'].get('drug_modified_coupling', {}).get('results', []))
        ax.text(7.5, 6.2, f'{n_drugs} drugs tested',
               ha='center', fontsize=9)

    # Layer 5: Output
    layer5 = FancyBboxPatch((0.5, 7.7), 9, 1.5, boxstyle="round,pad=0.1",
                            facecolor='#2ecc71', alpha=0.3, edgecolor='black', linewidth=3)
    ax.add_patch(layer5)
    ax.text(5, 8.45, 'Therapeutic Prediction',
           ha='center', fontsize=12, fontweight='bold')
    if data['therapeutic']:
        accuracy = data['therapeutic'].get('accuracy_test', {}).get('accuracy', 0)
        ax.text(5, 8.0, f'Accuracy: {accuracy:.0%} | O(1) prediction',
               ha='center', fontsize=9)

    # Draw arrows between layers
    for y_from, y_to in [(2, 2.3), (3.8, 4.1), (5.6, 5.9), (7.4, 7.7)]:
        arrow = FancyArrowPatch((5, y_from), (5, y_to),
                               arrowstyle='->', mutation_scale=20, linewidth=2.5,
                               color='black', alpha=0.5)
        ax.add_patch(arrow)

def plot_validation_summary(ax, data):
    """Panel B: Validation Summary Heatmap"""
    # Validators and their claims
    validators = [
        ('Hardware', 'hardware'),
        ('Harmonic', 'harmonic'),
        ('S-Entropy', 'sentropy'),
        ('Gear Ratio', 'gear'),
        ('Phase Lock', 'phase'),
        ('Semantic', 'semantic'),
        ('Trans-Planck', 'trans'),
        ('Categorical', 'categorical'),
        ('Therapeutic', 'therapeutic')
    ]

    # Extract validation status
    validation_matrix = []
    labels = []

    for name, key in validators:
        if data[key] and 'claims_validated' in data[key]:
            claims = data[key]['claims_validated']
            row = [1 if v else 0 for v in claims.values()]
            validation_matrix.append(row)
            labels.append(name)
        else:
            validation_matrix.append([0.5] * 4)  # Gray for missing
            labels.append(f'{name}*')

    # Pad rows to same length
    max_len = max(len(row) for row in validation_matrix)
    validation_matrix = [row + [0.5] * (max_len - len(row)) for row in validation_matrix]

    # Plot heatmap
    im = ax.imshow(validation_matrix, cmap='RdYlGn', aspect='auto', vmin=0, vmax=1)

    # Set ticks
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels, fontsize=10)
    ax.set_xticks(range(max_len))
    ax.set_xticklabels([f'C{i+1}' for i in range(max_len)], fontsize=9)
    ax.set_xlabel('Claims', fontweight='bold', fontsize=11)
    ax.set_title('Validation Status\n(Green=Validated, Red=Failed, Gray=Missing)',
                fontweight='bold', fontsize=12)

    # Add colorbar
    cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label('Validation', rotation=270, labelpad=15, fontsize=10)

    # Add grid
    ax.set_xticks(np.arange(max_len)-.5, minor=True)
    ax.set_yticks(np.arange(len(labels))-.5, minor=True)
    ax.grid(which="minor", color="w", linestyle='-', linewidth=2)

def plot_performance_metrics(ax, data):
    """Panel C: Performance Metrics"""
    # Key performance metrics
    metrics = {}

    if data['therapeutic']:
        acc = data['therapeutic'].get('accuracy_test', {})
        metrics['Prediction\nAccuracy'] = acc.get('accuracy', 0) * 100
        speedup = data['therapeutic'].get('speedup_test', {}).get('speedup_factor', 0)
        metrics['Speedup\nvs MD'] = min(speedup / 1000, 100) # Normalize to 0-100

    if data['semantic']:
        results = data['semantic'].get('complexity_reduction', {}).get('results', [])
        if results:
            valid_speedups = [r['speedup'] for r in results if r['speedup']]
            if valid_speedups:
                metrics['Semantic\nSpeedup'] = min(np.log10(max(valid_speedups)) * 10, 100)

    if data['harmonic']:
        enhancement = data['harmonic'].get('enhancement', {})
        F = enhancement.get('F_graph', 0)
        metrics['Network\nEnhancement'] = min(F / 1000, 100)

    if data['gear']:
        stats = data['gear'].get('statistics', {}).get('gear_ratios', {})
        mean_ratio = stats.get('mean', 0)
        metrics['Mean Gear\nRatio'] = min(mean_ratio / 50, 100)

    if data['phase']:
        results = data['phase'].get('drug_modified_coupling', {}).get('results', [])
        if results:
            mean_R = np.mean([r['R_drug'] for r in results])
            metrics['Phase\nCoherence'] = mean_R * 100

    # Plot radar chart IN THE PROVIDED AX
    categories = list(metrics.keys())
    values = list(metrics.values())

    if not categories:
        ax.text(0.5, 0.5, 'No metrics available', ha='center', va='center',
               transform=ax.transAxes, fontsize=14)
        return

    # Number of variables
    N = len(categories)
    angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
    values += values[:1]  # Complete the circle
    angles += angles[:1]

    # Convert current ax to polar - remove ax assignment!
    ax.remove()  # Remove the cartesian axes
    # Get the position and create polar axes in that position
    return categories, values, angles  # Return data for polar plot creation

def plot_information_flow(ax, data):
    """Panel D: Information Flow Diagram"""
    ax.axis('off')
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)

    # Title
    ax.text(5, 9.7, 'Information Flow: Hardware → Therapeutic Action',
           ha='center', fontsize=12, fontweight='bold')

    # Create flow diagram
    stages = [
        ('Hardware\nOscillations', 1.5, '#3498db'),
        ('Harmonic\nNetwork', 3.5, '#e74c3c'),
        ('S-Entropy\nMapping', 5.5, '#f39c12'),
        ('Categorical\nSelection', 7.5, '#9b59b6'),
        ('Therapeutic\nAction', 9.3, '#2ecc71')
    ]

    y_center = 5
    box_width = 1.8
    box_height = 1.2

    for i, (label, x, color) in enumerate(stages):
        # Draw box
        box = FancyBboxPatch((x - box_width/2, y_center - box_height/2),
                            box_width, box_height, boxstyle="round,pad=0.1",
                            facecolor=color, alpha=0.6, edgecolor='black', linewidth=2.5)
        ax.add_patch(box)
        ax.text(x, y_center, label, ha='center', va='center',
               fontsize=9, fontweight='bold')

        # Draw arrow to next stage
        if i < len(stages) - 1:
            next_x = stages[i+1][1]
            arrow = FancyArrowPatch((x + box_width/2, y_center),
                                   (next_x - box_width/2, y_center),
                                   arrowstyle='->', mutation_scale=20, linewidth=2.5,
                                   color='black', alpha=0.7)
            ax.add_patch(arrow)

    # Add information labels
    info_labels = [
        (2.5, 4.2, 'Resonance'),
        (4.5, 4.2, '3D Coords'),
        (6.5, 4.2, 'Sorting'),
        (8.4, 4.2, 'Drug → Target')
    ]

    for x, y, label in info_labels:
        ax.text(x, y, label, ha='center', fontsize=8, style='italic', color='#7f8c8d')

    # Add complexity annotations
    ax.text(1.5, 2.5, 'O(n)', ha='center', fontsize=9,
           bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
    ax.text(9.3, 2.5, 'O(1)', ha='center', fontsize=9,
           bbox=dict(boxstyle='round,pad=0.3', facecolor='lightgreen', alpha=0.8))

    # Draw complexity reduction arrow
    arrow_complex = FancyArrowPatch((1.5, 2.3), (9.3, 2.3),
                                   arrowstyle='<->', mutation_scale=15, linewidth=2,
                                   color='green')
    ax.add_patch(arrow_complex)
    ax.text(5.4, 2.0, 'Complexity Reduction', ha='center', fontsize=9,
           color='green', fontweight='bold')

def create_pharmaceutical_maxwell_demon_figure(base_dir='public',
                                               output_file='pharmaceutical_maxwell_demon_figure.png'):
    """Main function to create comprehensive 4-panel figure"""
    print(f"Loading all validation data from {base_dir}...")
    data = load_all_data(base_dir)

    # Create figure with GridSpec for complex layout
    fig = plt.figure(figsize=(20, 16))
    fig.suptitle('Pharmaceutical Biological Maxwell Demon: Complete Framework Validation',
                fontsize=18, fontweight='bold', y=0.995)

    # Panel A: Architecture (Top, spans 2 columns)
    ax1 = plt.subplot2grid((4, 3), (0, 0), colspan=3, rowspan=2)
    plot_framework_architecture(ax1, data)
    ax1.text(-0.05, 1.02, 'A', transform=ax1.transAxes,
            fontsize=24, fontweight='bold', va='top')

    # Panel B: Validation Summary (Bottom left)
    ax2 = plt.subplot2grid((4, 3), (2, 0), colspan=1, rowspan=2)
    plot_validation_summary(ax2, data)
    ax2.text(-0.15, 1.02, 'B', transform=ax2.transAxes,
            fontsize=24, fontweight='bold', va='top')

    # Panel C: Performance Metrics (Bottom middle) - Create as polar from start
    ax3 = plt.subplot2grid((4, 3), (2, 1), colspan=1, rowspan=2, projection='polar')

    # Get metrics data
    metrics = {}
    if data['therapeutic']:
        acc = data['therapeutic'].get('accuracy_test', {})
        metrics['Prediction\nAccuracy'] = acc.get('accuracy', 0) * 100
        speedup = data['therapeutic'].get('speedup_test', {}).get('speedup_factor', 0)
        metrics['Speedup\nvs MD'] = min(speedup / 1000, 100)
    if data['semantic']:
        results = data['semantic'].get('complexity_reduction', {}).get('results', [])
        if results:
            valid_speedups = [r['speedup'] for r in results if r['speedup']]
            if valid_speedups:
                metrics['Semantic\nSpeedup'] = min(np.log10(max(valid_speedups)) * 10, 100)
    if data['harmonic']:
        enhancement = data['harmonic'].get('enhancement', {})
        F = enhancement.get('F_graph', 0)
        metrics['Network\nEnhancement'] = min(F / 1000, 100)
    if data['gear']:
        stats = data['gear'].get('statistics', {}).get('gear_ratios', {})
        mean_ratio = stats.get('mean', 0)
        metrics['Mean Gear\nRatio'] = min(mean_ratio / 50, 100)
    if data['phase']:
        results = data['phase'].get('drug_modified_coupling', {}).get('results', [])
        if results:
            mean_R = np.mean([r['R_drug'] for r in results])
            metrics['Phase\nCoherence'] = mean_R * 100

    # Plot radar chart
    if metrics:
        categories = list(metrics.keys())
        values = list(metrics.values())
        N = len(categories)
        angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
        values += values[:1]
        angles += angles[:1]

        ax3.plot(angles, values, 'o-', linewidth=2, color='#3498db')
        ax3.fill(angles, values, alpha=0.25, color='#3498db')
        ax3.set_xticks(angles[:-1])
        ax3.set_xticklabels(categories, fontsize=9)
        ax3.set_ylim(0, 100)
        ax3.set_yticks([25, 50, 75, 100])
        ax3.set_yticklabels(['25%', '50%', '75%', '100%'], fontsize=8)
        ax3.grid(True)
        ax3.set_title('Performance Metrics\n(Normalized 0-100%)',
                     fontweight='bold', fontsize=12, pad=20)

    ax3.text(-0.15, 1.15, 'C', transform=ax3.transAxes,
            fontsize=24, fontweight='bold', va='top')

    # Panel D: Information Flow (Bottom right)
    ax4 = plt.subplot2grid((4, 3), (2, 2), colspan=1, rowspan=2)
    plot_information_flow(ax4, data)
    ax4.text(-0.05, 1.02, 'D', transform=ax4.transAxes,
            fontsize=24, fontweight='bold', va='top')

    plt.tight_layout(rect=[0, 0, 1, 0.99])
    plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"[OK] Master figure saved to {output_file}")
    plt.close()

    return fig

# Run
if __name__ == "__main__":
    import sys
    import os

    # Default paths
    base_dir = 'public'
    output_file = 'pharmaceutical_maxwell_demon_figure.png'

    # Override with command line args if provided
    if len(sys.argv) > 1:
        base_dir = sys.argv[1]
    if len(sys.argv) > 2:
        output_file = sys.argv[2]

    # Ensure output directory exists
    output_dir = os.path.dirname(output_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    create_pharmaceutical_maxwell_demon_figure(base_dir, output_file)

