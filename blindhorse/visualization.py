"""
Visualization Module

Creates high-quality panel charts for all validation results.
Supports multiple chart types: line plots, scatter plots, network graphs,
heatmaps, bar charts, histograms, and multi-panel figures.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.patches import Rectangle, FancyBboxPatch
import seaborn as sns
import networkx as nx
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import json


class PharmBMDVisualizer:
    """Comprehensive visualization for pharmaceutical BMD validation."""
    
    def __init__(self, output_dir: Path = Path("results/visualizations")):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Set style
        plt.style.use('seaborn-v0_8-darkgrid')
        sns.set_palette("husl")
        
    def plot_hardware_oscillations(self, results: Dict):
        """
        Plot hardware oscillation harvesting results.
        
        Creates 3-panel figure:
        - Frequency spectrum
        - Biological scale mapping
        - Range validation
        """
        fig = plt.figure(figsize=(18, 6))
        gs = gridspec.GridSpec(1, 3, figure=fig)
        
        # Extract data
        freqs = results["frequencies"]
        freq_values = [f["frequency_hz"] for f in freqs]
        freq_log = [f["frequency_log10"] for f in freqs]
        sources = [f["source"] for f in freqs]
        
        # Panel 1: Frequency spectrum
        ax1 = fig.add_subplot(gs[0, 0])
        ax1.scatter(range(len(freq_log)), freq_log, s=100, alpha=0.7, c=range(len(freq_log)), cmap='viridis')
        ax1.set_xlabel("Oscillator Index", fontsize=12)
        ax1.set_ylabel("log₁₀(Frequency / Hz)", fontsize=12)
        ax1.set_title("Hardware Oscillation Spectrum", fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        ax1.axhline(12, color='red', linestyle='--', alpha=0.5, label='Protein scale (10¹² Hz)')
        ax1.axhline(9, color='orange', linestyle='--', alpha=0.5, label='Ion channel (10⁹ Hz)')
        ax1.legend(fontsize=10)
        
        # Panel 2: Biological scale mapping
        ax2 = fig.add_subplot(gs[0, 1])
        bio_mapping = results["biological_mapping"]["biological_scale_mapping"]
        scales = list(bio_mapping.keys())
        counts = [len(bio_mapping[scale]) for scale in scales]
        
        bars = ax2.barh(scales, counts, color=plt.cm.viridis(np.linspace(0, 1, len(scales))))
        ax2.set_xlabel("Number of Oscillators", fontsize=12)
        ax2.set_ylabel("Biological Scale", fontsize=12)
        ax2.set_title("Biological Scale Coverage", fontsize=14, fontweight='bold')
        ax2.grid(axis='x', alpha=0.3)
        
        # Add counts on bars
        for i, (bar, count) in enumerate(zip(bars, counts)):
            ax2.text(count + 0.1, i, str(count), va='center', fontsize=10)
        
        # Panel 3: Range validation
        ax3 = fig.add_subplot(gs[0, 2])
        range_val = results["range_validation"]
        
        # Create box showing range
        f_min_log = np.log10(range_val["f_min_hz"])
        f_max_log = np.log10(range_val["f_max_hz"])
        
        ax3.barh([0], [range_val["orders_of_magnitude"]], left=[f_min_log], 
                height=0.5, color='green', alpha=0.7, label='Measured Range')
        ax3.axvline(f_min_log + 11, color='red', linestyle='--', linewidth=2, label='Claim (11 orders)')
        
        ax3.set_xlabel("log₁₀(Frequency / Hz)", fontsize=12)
        ax3.set_title("Frequency Range Validation", fontsize=14, fontweight='bold')
        ax3.set_yticks([])
        ax3.legend(fontsize=10)
        ax3.grid(axis='x', alpha=0.3)
        
        # Add text annotations
        ax3.text(f_min_log + range_val["orders_of_magnitude"]/2, 0, 
                f'{range_val["orders_of_magnitude"]:.1f} orders',
                ha='center', va='center', fontsize=12, fontweight='bold', color='white')
        
        plt.tight_layout()
        plt.savefig(self.output_dir / "hardware_oscillations.png", dpi=300, bbox_inches='tight')
        plt.close()
        
    def plot_harmonic_network(self, results: Dict):
        """
        Plot harmonic coincidence network results.
        
        Creates 4-panel figure:
        - Degree distribution
        - Network topology metrics
        - Enhancement factor
        - Small-world properties
        """
        fig = plt.figure(figsize=(18, 12))
        gs = gridspec.GridSpec(2, 2, figure=fig)
        
        topo = results["topology"]
        enh = results["enhancement"]
        sw = results["small_world"]
        
        # Panel 1: Degree distribution
        ax1 = fig.add_subplot(gs[0, 0])
        deg_dist = topo["degree_distribution"]
        
        # Create histogram data
        quartiles = [deg_dist["min"], deg_dist["q25"], deg_dist["median"], deg_dist["q75"], deg_dist["max"]]
        labels = ['Min', 'Q25', 'Median', 'Q75', 'Max']
        colors = plt.cm.Blues(np.linspace(0.4, 0.9, 5))
        
        ax1.bar(labels, quartiles, color=colors)
        ax1.set_ylabel("Degree", fontsize=12)
        ax1.set_title("Degree Distribution", fontsize=14, fontweight='bold')
        ax1.grid(axis='y', alpha=0.3)
        
        # Add values on bars
        for i, (label, value) in enumerate(zip(labels, quartiles)):
            ax1.text(i, value + max(quartiles)*0.02, str(value), 
                    ha='center', va='bottom', fontsize=10, fontweight='bold')
        
        # Panel 2: Network topology metrics
        ax2 = fig.add_subplot(gs[0, 1])
        metrics = {
            'Nodes': topo["num_nodes"],
            'Edges': topo["num_edges"],
            'Avg Degree': topo["average_degree"],
            'Clustering': topo["avg_clustering"] * 100,  # Percentage
            'Density': topo["density"] * 100,
        }
        
        y_pos = np.arange(len(metrics))
        values = list(metrics.values())
        
        bars = ax2.barh(y_pos, values, color=plt.cm.viridis(np.linspace(0.2, 0.8, len(metrics))))
        ax2.set_yticks(y_pos)
        ax2.set_yticklabels(list(metrics.keys()))
        ax2.set_xlabel("Value", fontsize=12)
        ax2.set_title("Network Topology Metrics", fontsize=14, fontweight='bold')
        ax2.set_xscale('log')
        ax2.grid(axis='x', alpha=0.3)
        
        # Add values
        for i, (bar, value) in enumerate(zip(bars, values)):
            ax2.text(value * 1.1, i, f'{value:.1f}', va='center', fontsize=10)
        
        # Panel 3: Enhancement factor
        ax3 = fig.add_subplot(gs[1, 0])
        
        components = ['⟨k⟩²', '1+ρ', 'F_graph']
        values = [enh["k_avg"]**2, 1 + enh["rho"], enh["F_graph"]]
        colors_enh = ['#FF6B6B', '#4ECDC4', '#45B7D1']
        
        bars = ax3.bar(components, values, color=colors_enh, alpha=0.8)
        ax3.set_ylabel("Value", fontsize=12)
        ax3.set_title(f"Enhancement Factor: F = ⟨k⟩² / (1+ρ)", fontsize=14, fontweight='bold')
        ax3.set_yscale('log')
        ax3.grid(axis='y', alpha=0.3)
        
        # Add claim line
        ax3.axhline(59428, color='red', linestyle='--', linewidth=2, label='Claim (59,428)')
        ax3.legend(fontsize=10)
        
        # Add values
        for bar, value in zip(bars, values):
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2., height * 1.1,
                    f'{value:.0f}', ha='center', va='bottom', fontsize=11, fontweight='bold')
        
        # Panel 4: Small-world properties
        ax4 = fig.add_subplot(gs[1, 1])
        
        sw_data = {
            'C/C_rand': sw["clustering_ratio"],
            'L/L_rand': sw["path_length_ratio"],
            'σ (Small-World)': sw["small_world_coefficient"],
        }
        
        y_pos = np.arange(len(sw_data))
        values = list(sw_data.values())
        colors_sw = ['#95E1D3', '#F38181', '#AA96DA']
        
        bars = ax4.barh(y_pos, values, color=colors_sw, alpha=0.8)
        ax4.set_yticks(y_pos)
        ax4.set_yticklabels(list(sw_data.keys()))
        ax4.set_xlabel("Ratio", fontsize=12)
        ax4.set_title("Small-World Properties", fontsize=14, fontweight='bold')
        ax4.axvline(1, color='black', linestyle='--', alpha=0.5, label='Random threshold')
        ax4.legend(fontsize=10)
        ax4.grid(axis='x', alpha=0.3)
        
        # Add values
        for i, (bar, value) in enumerate(zip(bars, values)):
            ax4.text(value * 1.1, i, f'{value:.2f}', va='center', fontsize=10, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(self.output_dir / "harmonic_network.png", dpi=300, bbox_inches='tight')
        plt.close()
        
    def plot_sentropy_space(self, results: Dict):
        """
        Plot S-entropy coordinate space.
        
        Creates 4-panel figure:
        - 3D projection of coordinate space
        - Coordinate ranges
        - Drug-target distances
        - Metric space validation
        """
        fig = plt.figure(figsize=(18, 12))
        gs = gridspec.GridSpec(2, 2, figure=fig)
        
        coords = results["coordinates"]
        props = results["space_properties"]
        dt_tests = results["drug_target_tests"]
        
        # Extract coordinate arrays
        s_k = [c["s_knowledge"] for c in coords]
        s_t = [c["s_time"] for c in coords]
        s_e = [c["s_entropy"] for c in coords]
        
        # Panel 1: 3D scatter (projected to 2D)
        ax1 = fig.add_subplot(gs[0, 0])
        scatter = ax1.scatter(s_k, s_t, c=s_e, s=100, alpha=0.7, cmap='plasma', edgecolors='black', linewidth=0.5)
        ax1.set_xlabel("S_knowledge", fontsize=12)
        ax1.set_ylabel("S_time", fontsize=12)
        ax1.set_title("S-Entropy Coordinate Space (S_knowledge vs S_time)", fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        cbar = plt.colorbar(scatter, ax=ax1)
        cbar.set_label("S_entropy", fontsize=11)
        
        # Panel 2: Coordinate ranges
        ax2 = fig.add_subplot(gs[0, 1])
        ranges = props["coordinate_ranges"]
        dimensions = list(ranges.keys())
        min_vals = [ranges[dim]["min"] for dim in dimensions]
        max_vals = [ranges[dim]["max"] for dim in dimensions]
        range_vals = [max_vals[i] - min_vals[i] for i in range(len(dimensions))]
        
        x = np.arange(len(dimensions))
        width = 0.35
        
        ax2.bar(x - width/2, min_vals, width, label='Min', color='#FF6B6B', alpha=0.8)
        ax2.bar(x + width/2, max_vals, width, label='Max', color='#4ECDC4', alpha=0.8)
        
        ax2.set_xticks(x)
        ax2.set_xticklabels(dimensions)
        ax2.set_ylabel("Value", fontsize=12)
        ax2.set_title("Coordinate Ranges", fontsize=14, fontweight='bold')
        ax2.legend(fontsize=10)
        ax2.grid(axis='y', alpha=0.3)
        
        # Panel 3: Drug-target categorical distances
        ax3 = fig.add_subplot(gs[1, 0])
        
        test_cases = dt_tests["test_cases"]
        labels = [tc["label"] for tc in test_cases]
        distances = [tc["categorical_distance"] for tc in test_cases]
        therapeutic = [tc["expected_therapeutic"] for tc in test_cases]
        
        colors = ['green' if t else 'red' for t in therapeutic]
        bars = ax3.bar(range(len(labels)), distances, color=colors, alpha=0.7)
        
        ax3.set_xticks(range(len(labels)))
        ax3.set_xticklabels(labels, rotation=45, ha='right')
        ax3.set_ylabel("Categorical Distance", fontsize=12)
        ax3.set_title("Drug-Target Categorical Distances", fontsize=14, fontweight='bold')
        ax3.axhline(5, color='orange', linestyle='--', linewidth=2, label='Therapeutic threshold')
        ax3.legend(fontsize=10)
        ax3.grid(axis='y', alpha=0.3)
        
        # Panel 4: Metric space validation
        ax4 = fig.add_subplot(gs[1, 1])
        
        # PCA explained variance
        dim_data = props["dimensionality"]
        pcs = ['PC1', 'PC2', 'PC3']
        variances = [
            dim_data["explained_variance_pc1"],
            dim_data["explained_variance_pc2"],
            dim_data["explained_variance_pc3"]
        ]
        
        bars = ax4.bar(pcs, variances, color=['#E74C3C', '#3498DB', '#2ECC71'], alpha=0.8)
        ax4.set_ylabel("Explained Variance", fontsize=12)
        ax4.set_title("PCA Dimensionality Analysis", fontsize=14, fontweight='bold')
        ax4.set_ylim([0, 1])
        ax4.grid(axis='y', alpha=0.3)
        
        # Add percentages on bars
        for bar, var in zip(bars, variances):
            height = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width()/2., height + 0.02,
                    f'{var*100:.1f}%', ha='center', va='bottom', fontsize=11, fontweight='bold')
        
        # Add metric space info
        metric = props["metric_space"]
        ax4.text(0.5, 0.5, f'Triangle Inequality: {metric["triangle_inequality_rate"]:.1%}\nMetric Space: {"✓" if metric["is_metric_space"] else "✗"}',
                transform=ax4.transAxes, fontsize=12, ha='center',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
        
        plt.tight_layout()
        plt.savefig(self.output_dir / "sentropy_space.png", dpi=300, bbox_inches='tight')
        plt.close()
        
    def plot_gear_ratios(self, results: Dict):
        """
        Plot gear ratio predictions and multi-scale cascade.
        """
        fig = plt.figure(figsize=(18, 12))
        gs = gridspec.GridSpec(2, 2, figure=fig)
        
        test_cases = results["test_cases"]
        stats = results["statistics"]
        cascade = results["example_cascade"]
        accuracy = results["accuracy"]
        
        # Panel 1: Gear ratios by pathway
        ax1 = fig.add_subplot(gs[0, 0])
        pathways = [tc["pathway"] for tc in test_cases]
        gear_values = [tc["gear_ratio"] for tc in test_cases]
        
        bars = ax1.bar(range(len(pathways)), gear_values, color=plt.cm.tab10(np.arange(len(pathways))), alpha=0.8)
        ax1.set_xticks(range(len(pathways)))
        ax1.set_xticklabels(pathways, rotation=45, ha='right')
        ax1.set_ylabel("Gear Ratio", fontsize=12)
        ax1.set_title("Pathway-Specific Gear Ratios", fontsize=14, fontweight='bold')
        ax1.axhline(stats["gear_ratios"]["mean"], color='red', linestyle='--', linewidth=2, label=f'Mean: {stats["gear_ratios"]["mean"]:.0f}')
        ax1.legend(fontsize=10)
        ax1.grid(axis='y', alpha=0.3)
        
        # Panel 2: Prediction accuracy
        ax2 = fig.add_subplot(gs[0, 1])
        predictions = accuracy["predictions"]
        drugs = [p["drug"] for p in predictions]
        predicted = [p["predicted_response_hr"] for p in predictions]
        measured = [p["measured_response_hr"] for p in predictions]
        
        x = np.arange(len(drugs))
        width = 0.35
        
        ax2.bar(x - width/2, predicted, width, label='Predicted', color='#3498DB', alpha=0.8)
        ax2.bar(x + width/2, measured, width, label='Measured', color='#E74C3C', alpha=0.8)
        
        ax2.set_xticks(x)
        ax2.set_xticklabels(drugs, rotation=45, ha='right')
        ax2.set_ylabel("Response Time (hours)", fontsize=12)
        ax2.set_title(f"Prediction Accuracy: {accuracy['accuracy']:.1%}", fontsize=14, fontweight='bold')
        ax2.set_yscale('log')
        ax2.legend(fontsize=10)
        ax2.grid(axis='y', alpha=0.3)
        
        # Panel 3: Multi-scale cascade
        ax3 = fig.add_subplot(gs[1, :])
        cascade_levels = cascade["cascade"]
        levels = [c["level"] for c in cascade_levels]
        names = [c["name"].replace('_', ' ') for c in cascade_levels]
        frequencies = [c["frequency_hz"] for c in cascade_levels]
        
        # Plot cascade
        colors_cascade = plt.cm.viridis(np.linspace(0, 1, len(levels)))
        bars = ax3.bar(levels, np.log10(frequencies), color=colors_cascade, alpha=0.8, edgecolor='black', linewidth=1.5)
        
        ax3.set_xticks(levels)
        ax3.set_xticklabels([f'L{l}\n{names[i][:15]}' for i, l in enumerate(levels)], rotation=0, ha='center', fontsize=9)
        ax3.set_ylabel("log₁₀(Frequency / Hz)", fontsize=12)
        ax3.set_xlabel("Biological Hierarchy Level", fontsize=12)
        ax3.set_title("Multi-Scale Gear Cascade (8 Levels)", fontsize=14, fontweight='bold')
        ax3.grid(axis='y', alpha=0.3)
        
        # Add drug entry marker
        ax3.axvline(2, color='red', linestyle='--', linewidth=3, alpha=0.7, label='Drug Entry (Protein Level)')
        ax3.legend(fontsize=11, loc='upper right')
        
        plt.tight_layout()
        plt.savefig(self.output_dir / "gear_ratios.png", dpi=300, bbox_inches='tight')
        plt.close()
        
    def plot_complete_validation_summary(self, all_results: Dict):
        """
        Create comprehensive summary panel showing all validations.
        """
        fig = plt.figure(figsize=(20, 14))
        gs = gridspec.GridSpec(4, 3, figure=fig, hspace=0.4, wspace=0.3)
        
        # Title
        fig.suptitle("Pharmaceutical Maxwell Demon - Complete Validation Summary", 
                    fontsize=20, fontweight='bold', y=0.98)
        
        # Extract validation status
        validators = [
            ("Hardware Oscillation", all_results.get("hardware", {}).get("claims_validated", {})),
            ("Harmonic Network", all_results.get("harmonic", {}).get("claims_validated", {})),
            ("S-Entropy Mapping", all_results.get("sentropy", {}).get("claims_validated", {})),
            ("Maxwell Demon", all_results.get("maxwell", {}).get("claims_validated", {})),
            ("Gear Ratio", all_results.get("gear", {}).get("claims_validated", {})),
            ("Phase-Lock", all_results.get("phase_lock", {}).get("claims_validated", {})),
            ("Semantic Gravity", all_results.get("semantic", {}).get("claims_validated", {})),
            ("Trans-Planckian", all_results.get("trans_planckian", {}).get("claims_validated", {})),
            ("Categorical State", all_results.get("categorical", {}).get("claims_validated", {})),
            ("Therapeutic Prediction", all_results.get("therapeutic", {}).get("claims_validated", {})),
        ]
        
        # Calculate overall statistics
        total_claims = sum(len(v[1]) for v in validators)
        validated_claims = sum(sum(1 for c in v[1].values() if c) for v in validators)
        validation_rate = validated_claims / total_claims if total_claims > 0 else 0
        
        # Panel 1: Overall validation status
        ax1 = fig.add_subplot(gs[0, :])
        ax1.axis('off')
        
        # Create status box
        status_text = f"""
        OVERALL VALIDATION STATUS
        
        Total Claims Tested: {total_claims}
        Claims Validated: {validated_claims}
        Validation Rate: {validation_rate:.1%}
        
        Status: {"✓ FRAMEWORK VALIDATED" if validation_rate > 0.8 else "⚠ NEEDS REVIEW"}
        """
        
        box_color = '#2ECC71' if validation_rate > 0.8 else '#E67E22'
        ax1.text(0.5, 0.5, status_text, 
                transform=ax1.transAxes, fontsize=16, ha='center', va='center',
                bbox=dict(boxstyle='round,pad=1', facecolor=box_color, alpha=0.3, edgecolor='black', linewidth=2))
        
        # Panels 2-11: Individual validator status (3x4 grid)
        for idx, (name, claims) in enumerate(validators):
            row = 1 + idx // 3
            col = idx % 3
            ax = fig.add_subplot(gs[row, col])
            
            # Count validated claims
            n_claims = len(claims)
            n_validated = sum(1 for c in claims.values() if c)
            rate = n_validated / n_claims if n_claims > 0 else 0
            
            # Color based on validation rate
            if rate >= 0.9:
                color = '#2ECC71'  # Green
            elif rate >= 0.7:
                color = '#F39C12'  # Orange
            else:
                color = '#E74C3C'  # Red
            
            # Create pie chart
            sizes = [n_validated, n_claims - n_validated]
            colors_pie = [color, '#ECF0F1']
            explode = (0.1, 0)
            
            ax.pie(sizes, explode=explode, colors=colors_pie, autopct='%1.0f%%',
                  shadow=True, startangle=90, textprops={'fontsize': 11, 'fontweight': 'bold'})
            ax.set_title(f"{name}\n{n_validated}/{n_claims} validated", 
                        fontsize=12, fontweight='bold')
        
        plt.tight_layout(rect=[0, 0, 1, 0.96])
        plt.savefig(self.output_dir / "complete_validation_summary.png", dpi=300, bbox_inches='tight')
        plt.close()
        
    def generate_all_visualizations(self, all_results: Dict):
        """Generate all visualizations from complete results."""
        print("\n" + "="*70)
        print("GENERATING VISUALIZATIONS")
        print("="*70)
        
        if "hardware" in all_results and "error" not in all_results["hardware"]:
            try:
                print("\n1. Plotting hardware oscillations...")
                self.plot_hardware_oscillations(all_results["hardware"])
                print("   ✓ Hardware oscillations plotted")
            except Exception as e:
                print(f"   ✗ Error plotting hardware oscillations: {e}")
        
        if "harmonic" in all_results and "error" not in all_results["harmonic"]:
            try:
                print("2. Plotting harmonic network...")
                self.plot_harmonic_network(all_results["harmonic"])
                print("   ✓ Harmonic network plotted")
            except Exception as e:
                print(f"   ✗ Error plotting harmonic network: {e}")
        
        if "sentropy" in all_results and "error" not in all_results["sentropy"]:
            try:
                print("3. Plotting S-entropy space...")
                self.plot_sentropy_space(all_results["sentropy"])
                print("   ✓ S-entropy space plotted")
            except Exception as e:
                print(f"   ✗ Error plotting S-entropy space: {e}")
        
        if "gear" in all_results and "error" not in all_results["gear"]:
            try:
                print("4. Plotting gear ratios...")
                self.plot_gear_ratios(all_results["gear"])
                print("   ✓ Gear ratios plotted")
            except Exception as e:
                print(f"   ✗ Error plotting gear ratios: {e}")
        
        # Always try to generate summary
        try:
            print("5. Plotting complete validation summary...")
            self.plot_complete_validation_summary(all_results)
            print("   ✓ Complete validation summary plotted")
        except Exception as e:
            print(f"   ✗ Error plotting complete summary: {e}")
        
        print(f"\n✓ Visualization generation complete!")
        print(f"  Saved to: {self.output_dir}")
        print("="*70)

