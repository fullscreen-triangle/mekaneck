#!/usr/bin/env python3
"""
Master script to generate all validation figures from JSON results.
This script loads data from the results directory and creates publication-quality visualizations.
"""

import os
import sys
from pathlib import Path

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent))

def ensure_dirs():
    """Ensure output directories exist"""
    output_dir = Path(__file__).parent.parent.parent / 'results' / 'visualizations'
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir

def generate_categorical_state():
    """Generate categorical state figure"""
    print("\n" + "="*70)
    print("GENERATING CATEGORICAL STATE FIGURE")
    print("="*70)
    
    try:
        # Use the fixed version
        from state_fixed import create_categorical_state_figure
        
        json_file = '../../results/categorical_state/categorical_state_results.json'
        output_file = '../../results/visualizations/categorical_state_figure.png'
        
        if not Path(json_file).exists():
            print(f"✗ JSON file not found: {json_file}")
            return False
        
        create_categorical_state_figure(json_file, output_file)
        return True
        
    except Exception as e:
        print(f"✗ Error generating categorical state figure: {e}")
        import traceback
        traceback.print_exc()
        return False

def generate_summary():
    """Generate summary statistics"""
    print("\n" + "="*70)
    print("VALIDATION SUMMARY")
    print("="*70)
    
    results_dir = Path(__file__).parent.parent.parent / 'results'
    
    validators = [
        'hardware_oscillation',
        'harmonic_network',
        'sentropy',
        'gear_ratio',
        'phase_lock',
        'semantic_gravity',
        'trans_planckian',
        'categorical_state',
        'therapeutic_prediction'
    ]
    
    total_validators = len(validators)
    successful = 0
    
    for validator in validators:
        json_file = results_dir / validator / f'{validator}_results.json'
        if json_file.exists():
            successful += 1
            print(f"  ✓ {validator}: results found")
        else:
            print(f"  ✗ {validator}: results missing")
    
    print(f"\nResults Summary:")
    print(f"  Total validators: {total_validators}")
    print(f"  Successful: {successful}")
    print(f"  Missing: {total_validators - successful}")
    print(f"  Success rate: {successful/total_validators*100:.1f}%")

def main():
    """Main execution"""
    print("="*70)
    print(" "*15 + "VALIDATION FIGURE GENERATION")
    print("="*70)
    
    # Ensure output directories
    output_dir = ensure_dirs()
    print(f"\nOutput directory: {output_dir}")
    
    # Track success
    figures_generated = 0
    figures_failed = 0
    
    # Generate each figure
    if generate_categorical_state():
        figures_generated += 1
    else:
        figures_failed += 1
    
    # TODO: Add other figures as they are fixed
    # - Hardware oscillation
    # - Gear ratios
    # - Semantic gravity
    # - Phase lock
    # - Etc.
    
    # Generate summary
    generate_summary()
    
    # Final report
    print("\n" + "="*70)
    print(" "*15 + "GENERATION COMPLETE")
    print("="*70)
    print(f"\nFigures generated: {figures_generated}")
    print(f"Figures failed: {figures_failed}")
    print(f"\nAll outputs saved to: {output_dir}")
    print("="*70)

if __name__ == "__main__":
    main()

