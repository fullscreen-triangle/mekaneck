"""
Pharmaceutical BMD Validation Suite Orchestrator

Runs all validators in sequence, collects results, generates visualizations,
and produces comprehensive validation report.
"""

import json
import time
from pathlib import Path
from typing import Dict, List

from .validators import (
    HardwareOscillationValidator,
    HarmonicNetworkValidator,
    SEntropyValidator,
    MaxwellDemonValidator,
    GearRatioValidator,
    PhaseLockValidator,
    SemanticGravityValidator,
    TransPlanckianValidator,
    CategoricalStateValidator,
    TherapeuticPredictionValidator,
)
from .visualization import PharmBMDVisualizer


class PharmBMDValidationSuite:
    """Orchestrates complete pharmaceutical BMD validation."""
    
    def __init__(self, output_dir: Path = Path("results")):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.results: Dict = {}
        self.start_time = None
        self.end_time = None
        
    def run_complete_validation(self, 
                                skip_visualizations: bool = False,
                                skip_validators: List[str] = None) -> Dict:
        """
        Run complete validation suite.
        
        Args:
            skip_visualizations: If True, skip visualization generation
            skip_validators: List of validator names to skip
            
        Returns:
            Complete results dictionary
        """
        skip_validators = skip_validators or []
        
        print("\n" + "="*70)
        print(" "*15 + "PHARMACEUTICAL MAXWELL DEMON")
        print(" "*18 + "VALIDATION SUITE")
        print("="*70)
        
        self.start_time = time.time()
        
        # 1. Hardware Oscillation Validation
        if "hardware" not in skip_validators:
            try:
                print("\n" + "="*70)
                print("VALIDATOR 1/10: Hardware Oscillation Harvesting")
                print("="*70)
                validator = HardwareOscillationValidator()
                self.results["hardware"] = validator.run_validation()
            except Exception as e:
                print(f"ERROR in Hardware Oscillation Validator: {e}")
                self.results["hardware"] = {"error": str(e)}
        
        # 2. Harmonic Network Validation
        if "harmonic" not in skip_validators:
            try:
                print("\n" + "="*70)
                print("VALIDATOR 2/10: Harmonic Coincidence Network")
                print("="*70)
                
                # Get base frequencies from hardware validator
                if "hardware" in self.results and "frequencies" in self.results["hardware"]:
                    base_freqs = [(f["source"], f["frequency_hz"]) 
                                 for f in self.results["hardware"]["frequencies"]]
                else:
                    # Use defaults if hardware validator failed
                    base_freqs = [
                        ("CPU_Core", 3.5e9),
                        ("Screen_LED_Red", 4.6e14),
                        ("Screen_LED_Green", 5.7e14),
                        ("Screen_LED_Blue", 6.4e14),
                        ("WiFi_2.4GHz", 2.4e9),
                        ("Screen_Refresh", 144.0),
                        ("Temperature", 1.0),
                    ]
                
                validator = HarmonicNetworkValidator(n_max_harmonics=150)
                self.results["harmonic"] = validator.run_validation(base_freqs)
            except Exception as e:
                print(f"ERROR in Harmonic Network Validator: {e}")
                self.results["harmonic"] = {"error": str(e)}
        
        # 3. S-Entropy Validation
        if "sentropy" not in skip_validators:
            try:
                print("\n" + "="*70)
                print("VALIDATOR 3/10: S-Entropy Coordinate Mapping")
                print("="*70)
                
                # Get frequencies from hardware validator
                if "hardware" in self.results and "frequencies" in self.results["hardware"]:
                    freqs_data = [(f["frequency_hz"], f["source"]) 
                                 for f in self.results["hardware"]["frequencies"]]
                else:
                    freqs_data = [
                        (3.5e9, "CPU"), (4.6e14, "LED_Red"), (2.4e9, "WiFi"),
                        (1.0, "Temp"), (144.0, "Refresh")
                    ]
                
                validator = SEntropyValidator()
                self.results["sentropy"] = validator.run_validation(freqs_data)
            except Exception as e:
                print(f"ERROR in S-Entropy Validator: {e}")
                self.results["sentropy"] = {"error": str(e)}
        
        # 4. Maxwell Demon Validation
        if "maxwell" not in skip_validators:
            try:
                print("\n" + "="*70)
                print("VALIDATOR 4/10: Maxwell Demon Decomposition")
                print("="*70)
                validator = MaxwellDemonValidator(decomposition_depth=10)
                self.results["maxwell"] = validator.run_validation()
            except Exception as e:
                print(f"ERROR in Maxwell Demon Validator: {e}")
                self.results["maxwell"] = {"error": str(e)}
        
        # 5. Gear Ratio Validation
        if "gear" not in skip_validators:
            try:
                print("\n" + "="*70)
                print("VALIDATOR 5/10: Gear Ratio Prediction")
                print("="*70)
                validator = GearRatioValidator()
                self.results["gear"] = validator.run_validation()
            except Exception as e:
                print(f"ERROR in Gear Ratio Validator: {e}")
                self.results["gear"] = {"error": str(e)}
        
        # 6. Phase-Lock Validation
        if "phase_lock" not in skip_validators:
            try:
                print("\n" + "="*70)
                print("VALIDATOR 6/10: Phase-Lock Network Dynamics")
                print("="*70)
                validator = PhaseLockValidator()
                self.results["phase_lock"] = validator.run_validation()
            except Exception as e:
                print(f"ERROR in Phase-Lock Validator: {e}")
                self.results["phase_lock"] = {"error": str(e)}
        
        # 7. Semantic Gravity Validation
        if "semantic" not in skip_validators:
            try:
                print("\n" + "="*70)
                print("VALIDATOR 7/10: Semantic Gravity Navigation")
                print("="*70)
                validator = SemanticGravityValidator(dimensions=8)
                self.results["semantic"] = validator.run_validation()
            except Exception as e:
                print(f"ERROR in Semantic Gravity Validator: {e}")
                self.results["semantic"] = {"error": str(e)}
        
        # 8. Trans-Planckian Validation
        if "trans_planckian" not in skip_validators:
            try:
                print("\n" + "="*70)
                print("VALIDATOR 8/10: Trans-Planckian Temporal Precision")
                print("="*70)
                validator = TransPlanckianValidator()
                self.results["trans_planckian"] = validator.run_validation()
            except Exception as e:
                print(f"ERROR in Trans-Planckian Validator: {e}")
                self.results["trans_planckian"] = {"error": str(e)}
        
        # 9. Categorical State Validation
        if "categorical" not in skip_validators:
            try:
                print("\n" + "="*70)
                print("VALIDATOR 9/10: Categorical State Transitions")
                print("="*70)
                validator = CategoricalStateValidator()
                self.results["categorical"] = validator.run_validation()
            except Exception as e:
                print(f"ERROR in Categorical State Validator: {e}")
                self.results["categorical"] = {"error": str(e)}
        
        # 10. Therapeutic Prediction Validation
        if "therapeutic" not in skip_validators:
            try:
                print("\n" + "="*70)
                print("VALIDATOR 10/10: Therapeutic Prediction (Complete Pipeline)")
                print("="*70)
                validator = TherapeuticPredictionValidator()
                self.results["therapeutic"] = validator.run_validation()
            except Exception as e:
                print(f"ERROR in Therapeutic Prediction Validator: {e}")
                self.results["therapeutic"] = {"error": str(e)}
        
        self.end_time = time.time()
        
        # Generate visualizations
        if not skip_visualizations:
            try:
                visualizer = PharmBMDVisualizer()
                visualizer.generate_all_visualizations(self.results)
            except Exception as e:
                print(f"ERROR generating visualizations: {e}")
        
        # Generate final report
        self.generate_report()
        
        # Save complete results
        self.save_complete_results()
        
        return self.results
    
    def generate_report(self):
        """Generate comprehensive validation report."""
        print("\n" + "="*70)
        print(" "*20 + "VALIDATION REPORT")
        print("="*70)
        
        total_time = self.end_time - self.start_time
        
        # Count validations
        total_validators = len(self.results)
        successful = sum(1 for r in self.results.values() if "error" not in r)
        
        print(f"\nExecution Summary:")
        print(f"  Total validators: {total_validators}")
        print(f"  Successful: {successful}")
        print(f"  Failed: {total_validators - successful}")
        print(f"  Total time: {total_time:.2f} seconds")
        
        # Count claims
        total_claims = 0
        validated_claims = 0
        
        for validator_name, results in self.results.items():
            if "claims_validated" in results:
                claims = results["claims_validated"]
                total_claims += len(claims)
                validated_claims += sum(1 for c in claims.values() if c)
        
        validation_rate = validated_claims / total_claims if total_claims > 0 else 0
        
        print(f"\nValidation Summary:")
        print(f"  Total claims: {total_claims}")
        print(f"  Validated: {validated_claims}")
        print(f"  Validation rate: {validation_rate:.1%}")
        
        # Overall status
        if validation_rate >= 0.9:
            status = "✓ EXCELLENT - Framework validated"
            status_emoji = "🎉"
        elif validation_rate >= 0.8:
            status = "✓ GOOD - Most claims validated"
            status_emoji = "✅"
        elif validation_rate >= 0.7:
            status = "⚠ ACCEPTABLE - Needs review"
            status_emoji = "⚠️"
        else:
            status = "✗ NEEDS WORK - Significant issues"
            status_emoji = "❌"
        
        print(f"\n{status_emoji} Overall Status: {status}")
        
        # Individual validator status
        print(f"\nValidator Status:")
        for validator_name, results in self.results.items():
            if "error" in results:
                print(f"  ✗ {validator_name}: ERROR")
            elif "claims_validated" in results:
                claims = results["claims_validated"]
                n_claims = len(claims)
                n_validated = sum(1 for c in claims.values() if c)
                rate = n_validated / n_claims if n_claims > 0 else 0
                emoji = "✓" if rate >= 0.8 else "⚠" if rate >= 0.6 else "✗"
                print(f"  {emoji} {validator_name}: {n_validated}/{n_claims} ({rate:.0%})")
            else:
                print(f"  ? {validator_name}: Unknown status")
        
        print("\n" + "="*70)
        
    def save_complete_results(self):
        """Save complete results to JSON."""
        output_file = self.output_dir / "complete_validation_results.json"
        
        # Add metadata
        results_with_metadata = {
            "metadata": {
                "suite": "Pharmaceutical Maxwell Demon Validation",
                "version": "0.1.0",
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "total_time_seconds": self.end_time - self.start_time,
            },
            "results": self.results,
        }
        
        with open(output_file, 'w') as f:
            json.dump(results_with_metadata, f, indent=2)
        
        print(f"\n✓ Complete results saved to: {output_file}")


def main():
    """Main entry point for validation suite."""
    suite = PharmBMDValidationSuite()
    suite.run_complete_validation()
    
    print("\n" + "="*70)
    print(" "*15 + "VALIDATION SUITE COMPLETE")
    print("="*70)
    print("\nResults saved in ./results/ directory")
    print("  - JSON files: Individual validator results")
    print("  - PNG files: Visualizations")
    print("  - complete_validation_results.json: Full suite results")
    print("\n")


if __name__ == "__main__":
    main()

