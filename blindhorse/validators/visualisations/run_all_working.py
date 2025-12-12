#!/usr/bin/env python3
"""
Run ALL visualization scripts including new additions.
"""

import subprocess
import sys

print("="*80)
print(" "*20 + "PHARMACEUTICAL MAXWELL DEMON")
print(" "*20 + "COMPLETE VISUALIZATION SUITE")
print("="*80)

scripts = [
    ("1. Therapeutic Prediction", "therapeutic.py"),
    ("2. S-Entropy Space", "entropy.py"),
    ("3. Categorical State", "state.py"),
    ("4. Gear Ratios", "gears.py"),
    ("5. Phase-Lock Dynamics", "phases.py"),
    ("6. Semantic Gravity", "gravity.py"),
    ("7. Trans-Planckian Precision", "transplanckian.py"),
    ("8. H+ Field Dynamics", "hplus_field.py"),
    ("9. Oxygen Phase Lock & Categorical Exclusion", "oxygen_categorical.py"),
    ("10. MASTER: Pharmaceutical Maxwell Demon", "pharmaceutical_maxwell_demon.py"),
]

success_count = 0
failed_count = 0
failed_scripts = []

for name, script in scripts:
    print(f"\n{'-'*80}")
    print(f"Running: {name}")
    print(f"Script: {script}")
    print(f"{'-'*80}")
    
    try:
        result = subprocess.run([sys.executable, script], 
                              capture_output=True, 
                              text=True,
                              timeout=120)
        
        if result.returncode == 0:
            print(f"[OK] SUCCESS")
            success_count += 1
        else:
            print(f"[FAIL] FAILED")
            if result.stderr:
                print(f"Error: {result.stderr[:400]}")
            failed_count += 1
            failed_scripts.append(name)
            
    except subprocess.TimeoutExpired:
        print(f"[FAIL] TIMEOUT")
        failed_count += 1
        failed_scripts.append(name)
    except Exception as e:
        print(f"[FAIL] EXCEPTION: {e}")
        failed_count += 1
        failed_scripts.append(name)

print(f"\n{'='*80}")
print(" "*25 + "FINAL SUMMARY")
print(f"{'='*80}")
print(f"\n  Total Scripts:     {len(scripts)}")
print(f"  [OK] Success:      {success_count}")
print(f"  [FAIL] Failed:     {failed_count}")
print(f"  Success Rate:      {success_count/len(scripts)*100:.1f}%")

if failed_scripts:
    print(f"\n  Failed Scripts:")
    for script in failed_scripts:
        print(f"    - {script}")
else:
    print(f"\n  [SUCCESS] ALL VISUALIZATIONS GENERATED!")

print(f"\n  Output Directory:  {sys.path[0]}")
print(f"  Figure Format:     PNG (300 DPI)")
print(f"  Panel Count:       {len(scripts) * 4} panels across {len(scripts)} figures")
print(f"\n{'='*80}\n")
