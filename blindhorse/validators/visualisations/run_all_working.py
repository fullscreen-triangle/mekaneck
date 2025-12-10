#!/usr/bin/env python3
"""
Run all WORKING visualization scripts.
Updated to include all new visualizations.
"""

import subprocess
import sys

print("="*70)
print(" "*15 + "RUNNING ALL VISUALIZATION SCRIPTS")
print("="*70)

scripts = [
    ("1. Therapeutic Prediction", "therapeutic.py"),
    ("2. S-Entropy Space", "entropy.py"),
    ("3. Categorical State", "state.py"),
    ("4. Gear Ratios", "gears.py"),
    ("5. Phase-Lock Dynamics", "phases.py"),
    ("6. Semantic Gravity", "gravity.py"),
    ("7. Harmonic Network", "harmonic.py"),
    ("8. Trans-Planckian Precision", "transplanckian.py"),
    ("9. MASTER: Pharmaceutical Maxwell Demon", "pharmaceutical_maxwell_demon.py"),
]

success_count = 0
failed_count = 0
failed_scripts = []

for name, script in scripts:
    print(f"\n{'-'*70}")
    print(f"Running: {name}")
    print(f"{'-'*70}")
    
    try:
        result = subprocess.run([sys.executable, script], 
                              capture_output=True, 
                              text=True,
                              timeout=120)
        
        if result.returncode == 0:
            print(f"SUCCESS: {name}")
            success_count += 1
        else:
            print(f"FAILED: {name}")
            print(f"Error: {result.stderr[:300]}")
            failed_count += 1
            failed_scripts.append(name)
            
    except subprocess.TimeoutExpired:
        print(f"TIMEOUT: {name}")
        failed_count += 1
        failed_scripts.append(name)
    except Exception as e:
        print(f"EXCEPTION: {name} - {e}")
        failed_count += 1
        failed_scripts.append(name)

print(f"\n{'='*70}")
print(" "*20 + "FINAL SUMMARY")
print(f"{'='*70}")
print(f"SUCCESS: {success_count}/{len(scripts)}")
print(f"FAILED: {failed_count}/{len(scripts)}")
print(f"Success Rate: {success_count/len(scripts)*100:.1f}%")

if failed_scripts:
    print(f"\nFailed Scripts:")
    for script in failed_scripts:
        print(f"  - {script}")

print(f"\nAll generated figures saved in current directory")
print(f"{'='*70}\n")
