from ..utils import save_json
"""
Harmonic Coincidence Network Validator

Validates Claims:
1. Harmonic expansion creates ~1,950 oscillator nodes (N_max=150)
2. Coincidence threshold yields ~253,013 edges (Δf=10^9 Hz)
3. Average degree ⟨k⟩ ≈ 259.5
4. Network enhancement F_graph ≈ 59,428
5. Small-world topology emerges

Tests network construction, topology analysis, and enhancement factor calculation.
"""

import numpy as np
import networkx as nx
from dataclasses import dataclass
from typing import List, Dict, Tuple, Set
import json
from pathlib import Path
import time


@dataclass
class HarmonicNode:
    """Represents a harmonic oscillator node."""
    id: int
    base_source: str
    harmonic_number: int
    frequency_hz: float
    

class HarmonicNetworkValidator:
    """Validates harmonic coincidence network construction and properties."""
    
    def __init__(self, 
                 n_max_harmonics: int = 150,
                 coincidence_threshold_hz: float = 1e9,
                 output_dir: Path = Path("results/harmonic_network")):
        self.n_max = n_max_harmonics
        self.threshold = coincidence_threshold_hz
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.nodes: List[HarmonicNode] = []
        self.graph: nx.Graph = nx.Graph()
        
    def generate_harmonic_expansion(self, base_frequencies: List[Tuple[str, float]]) -> List[HarmonicNode]:
        """
        Generate harmonic expansion from base frequencies.
        
        For each base frequency f₀, generate harmonics: n·f₀ where n=1,2,...,N_max
        
        Args:
            base_frequencies: List of (source_name, frequency_hz) tuples
            
        Returns:
            List of harmonic oscillator nodes
        """
        nodes = []
        node_id = 0
        
        for source, f0 in base_frequencies:
            for n in range(1, self.n_max + 1):
                fn = n * f0
                nodes.append(HarmonicNode(
                    id=node_id,
                    base_source=source,
                    harmonic_number=n,
                    frequency_hz=fn
                ))
                node_id += 1
        
        return nodes
    
    def build_coincidence_graph(self, nodes: List[HarmonicNode]) -> nx.Graph:
        """
        Build graph with edges between harmonically coincident oscillators.
        
        Add edge (i,j) if |f_i - f_j| < threshold
        
        Claim: ~253,013 edges for threshold = 10^9 Hz
        """
        G = nx.Graph()
        
        # Add all nodes
        for node in nodes:
            G.add_node(node.id, 
                      source=node.base_source,
                      harmonic=node.harmonic_number,
                      frequency=node.frequency_hz)
        
        # Add edges for coincident frequencies
        print(f"  Building edges (may take a moment for {len(nodes)} nodes)...")
        
        # Optimized: sort by frequency and only check nearby nodes
        sorted_nodes = sorted(nodes, key=lambda n: n.frequency_hz)
        
        edge_count = 0
        for i, node_i in enumerate(sorted_nodes):
            # Only check nodes within frequency threshold
            j = i + 1
            while j < len(sorted_nodes):
                node_j = sorted_nodes[j]
                freq_diff = abs(node_i.frequency_hz - node_j.frequency_hz)
                
                if freq_diff > self.threshold:
                    break  # All subsequent nodes too far
                
                if node_i.id != node_j.id:  # No self-loops
                    G.add_edge(node_i.id, node_j.id, freq_diff=freq_diff)
                    edge_count += 1
                
                j += 1
            
            if (i + 1) % 200 == 0:
                print(f"    Processed {i+1}/{len(sorted_nodes)} nodes, {edge_count} edges so far")
        
        print(f"  ✓ Graph built: {len(nodes)} nodes, {edge_count} edges")
        
        return G
    
    def analyze_network_topology(self, G: nx.Graph) -> Dict:
        """
        Analyze network topology properties.
        
        Claims to validate:
        - Average degree: ⟨k⟩ ≈ 259.5
        - Clustering coefficient: ρ ≈ 0.133
        - Small-world properties
        """
        print("  Computing network statistics...")
        
        # Basic properties
        num_nodes = G.number_of_nodes()
        num_edges = G.number_of_edges()
        
        # Degree distribution
        degrees = dict(G.degree())
        degree_values = list(degrees.values())
        avg_degree = np.mean(degree_values) if degree_values else 0
        std_degree = np.std(degree_values) if degree_values else 0
        
        # Clustering coefficient (sample if large)
        if num_nodes > 1000:
            # Sample 1000 nodes for clustering
            sample_nodes = np.random.choice(list(G.nodes()), 
                                          size=min(1000, num_nodes), 
                                          replace=False)
            clustering_sample = nx.clustering(G, nodes=sample_nodes)
            avg_clustering = np.mean(list(clustering_sample.values()))
        else:
            avg_clustering = nx.average_clustering(G)
        
        # Connected components
        num_components = nx.number_connected_components(G)
        largest_cc = max(nx.connected_components(G), key=len) if num_components > 0 else set()
        largest_cc_size = len(largest_cc)
        
        # Density
        density = nx.density(G)
        
        topology = {
            "num_nodes": num_nodes,
            "num_edges": num_edges,
            "average_degree": avg_degree,
            "std_degree": std_degree,
            "avg_clustering": avg_clustering,
            "density": density,
            "num_components": num_components,
            "largest_component_size": largest_cc_size,
            "degree_distribution": {
                "min": int(min(degree_values)) if degree_values else 0,
                "max": int(max(degree_values)) if degree_values else 0,
                "median": float(np.median(degree_values)) if degree_values else 0,
                "q25": float(np.percentile(degree_values, 25)) if degree_values else 0,
                "q75": float(np.percentile(degree_values, 75)) if degree_values else 0,
            }
        }
        
        return topology
    
    def compute_enhancement_factor(self, topology: Dict) -> Dict:
        """
        Compute network enhancement factor.
        
        Formula: F_graph = ⟨k⟩² / (1 + ρ)
        
        Where:
        - ⟨k⟩: average degree
        - ρ: clustering coefficient
        
        Claim: F_graph ≈ 59,428
        """
        k_avg = topology["average_degree"]
        rho = topology["avg_clustering"]
        
        F_graph = (k_avg ** 2) / (1 + rho)
        
        enhancement = {
            "k_avg": k_avg,
            "rho": rho,
            "F_graph": F_graph,
            "claim_value": 59428,
            "relative_error": abs(F_graph - 59428) / 59428,
            "claim_validated": abs(F_graph - 59428) / 59428 < 0.5,  # Within 50%
        }
        
        return enhancement
    
    def validate_small_world_properties(self, G: nx.Graph, topology: Dict) -> Dict:
        """
        Validate small-world network properties.
        
        Small-world networks have:
        1. High clustering (C >> C_random)
        2. Short path length (L ≈ L_random)
        """
        n = topology["num_nodes"]
        k = topology["average_degree"]
        C = topology["avg_clustering"]
        
        # Expected values for random graph
        C_random = k / n if n > 0 else 0
        
        # Compute on largest component for path length
        if topology["num_components"] > 0:
            largest_cc = max(nx.connected_components(G), key=len)
            G_largest = G.subgraph(largest_cc).copy()
            
            if len(G_largest) > 1:
                # Sample path lengths for large graphs
                if len(G_largest) > 500:
                    sample_nodes = np.random.choice(list(G_largest.nodes()), 
                                                  size=min(100, len(G_largest)), 
                                                  replace=False)
                    path_lengths = []
                    for node in sample_nodes:
                        lengths = nx.single_source_shortest_path_length(G_largest, node)
                        path_lengths.extend(lengths.values())
                    L = np.mean(path_lengths) if path_lengths else 0
                else:
                    L = nx.average_shortest_path_length(G_largest)
            else:
                L = 0
        else:
            L = 0
        
        L_random = np.log(n) / np.log(k) if k > 1 else 0
        
        # Small-world coefficient
        sigma = (C / C_random) / (L / L_random) if C_random > 0 and L_random > 0 else 0
        
        small_world = {
            "clustering_actual": C,
            "clustering_random": C_random,
            "clustering_ratio": C / C_random if C_random > 0 else 0,
            "path_length_actual": L,
            "path_length_random": L_random,
            "path_length_ratio": L / L_random if L_random > 0 else 0,
            "small_world_coefficient": sigma,
            "is_small_world": sigma > 1,  # σ >> 1 indicates small-world
        }
        
        return small_world
    
    def run_validation(self, base_frequencies: List[Tuple[str, float]]) -> Dict:
        """
        Run complete harmonic network validation.
        
        Args:
            base_frequencies: List of (source_name, frequency_hz) tuples
            
        Returns:
            Comprehensive results dictionary
        """
        print("="*70)
        print("HARMONIC COINCIDENCE NETWORK VALIDATION")
        print("="*70)
        
        start_time = time.time()
        
        # Generate harmonic expansion
        print(f"\n1. Generating harmonic expansion (N_max={self.n_max})...")
        self.nodes = self.generate_harmonic_expansion(base_frequencies)
        print(f"  ✓ Created {len(self.nodes)} harmonic oscillator nodes")
        
        # Build coincidence graph
        print(f"\n2. Building coincidence graph (threshold={self.threshold:.2e} Hz)...")
        self.graph = self.build_coincidence_graph(self.nodes)
        
        # Analyze topology
        print("\n3. Analyzing network topology...")
        topology = self.analyze_network_topology(self.graph)
        
        # Compute enhancement factor
        print("\n4. Computing enhancement factor...")
        enhancement = self.compute_enhancement_factor(topology)
        
        # Validate small-world properties
        print("\n5. Validating small-world properties...")
        small_world = self.validate_small_world_properties(self.graph, topology)
        
        elapsed_time = time.time() - start_time
        
        # Compile results
        results = {
            "validator": "HarmonicNetworkValidator",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "parameters": {
                "n_max_harmonics": self.n_max,
                "coincidence_threshold_hz": self.threshold,
                "num_base_frequencies": len(base_frequencies),
            },
            "harmonic_expansion": {
                "num_nodes": len(self.nodes),
                "claim_value": 1950,
                "relative_error": abs(len(self.nodes) - 1950) / 1950,
            },
            "topology": topology,
            "enhancement": enhancement,
            "small_world": small_world,
            "computation_time_seconds": elapsed_time,
            "claims_validated": {
                "node_count_1950": abs(len(self.nodes) - 1950) / 1950 < 0.2,
                "edge_count_253k": abs(topology["num_edges"] - 253013) / 253013 < 0.5,
                "avg_degree_259": abs(topology["average_degree"] - 259.5) / 259.5 < 0.5,
                "enhancement_59k": enhancement["claim_validated"],
                "small_world_topology": small_world["is_small_world"],
            },
        }
        
        # Save results
        self.save_results(results)
        
        # Save graph
        self.save_graph()
        
        # Print summary
        self.print_summary(results)
        
        return results
    
    def save_results(self, results: Dict):
        """Save validation results to JSON."""
        output_file = self.output_dir / "harmonic_network_results.json"
        
        # Remove non-serializable objects
        results_copy = results.copy()
        
        with open(output_file, 'w') as f:
            json.dump(results_copy, f, indent=2)
        print(f"\n✓ Results saved to: {output_file}")
    
    def save_graph(self):
        """Save graph to file for visualization."""
        output_file = self.output_dir / "harmonic_network.gexf"
        nx.write_gexf(self.graph, output_file)
        print(f"✓ Graph saved to: {output_file}")
    
    def print_summary(self, results: Dict):
        """Print validation summary."""
        print("\n" + "="*70)
        print("VALIDATION SUMMARY")
        print("="*70)
        
        # Nodes
        exp = results["harmonic_expansion"]
        print(f"\nHarmonic Expansion:")
        print(f"  Nodes created: {exp['num_nodes']}")
        print(f"  Claim: ~1,950 nodes")
        print(f"  Error: {exp['relative_error']*100:.1f}%")
        print(f"  Status: {'✓ VALIDATED' if results['claims_validated']['node_count_1950'] else '✗ FAILED'}")
        
        # Topology
        topo = results["topology"]
        print(f"\nNetwork Topology:")
        print(f"  Edges: {topo['num_edges']:,}")
        print(f"  Claim: ~253,013 edges")
        print(f"  Average degree: {topo['average_degree']:.1f}")
        print(f"  Claim: ~259.5")
        print(f"  Clustering: {topo['avg_clustering']:.3f}")
        print(f"  Status: {'✓ VALIDATED' if results['claims_validated']['avg_degree_259'] else '✗ FAILED'}")
        
        # Enhancement
        enh = results["enhancement"]
        print(f"\nEnhancement Factor:")
        print(f"  F_graph = {enh['F_graph']:.0f}")
        print(f"  Claim: ~59,428")
        print(f"  Error: {enh['relative_error']*100:.1f}%")
        print(f"  Status: {'✓ VALIDATED' if enh['claim_validated'] else '✗ FAILED'}")
        
        # Small-world
        sw = results["small_world"]
        print(f"\nSmall-World Properties:")
        print(f"  Coefficient σ: {sw['small_world_coefficient']:.2f}")
        print(f"  Status: {'✓ SMALL-WORLD' if sw['is_small_world'] else '✗ NOT SMALL-WORLD'}")
        
        print("\n" + "="*70)

