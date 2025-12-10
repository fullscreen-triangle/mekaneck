#!/usr/bin/env python3
"""
Quick fix script to update all validators to use the NumpyEncoder for JSON serialization.
"""

import re
from pathlib import Path

# List of validator files to update
validator_files = [
    "blindhorse/validators/hardware_oscillation.py",
    "blindhorse/validators/harmonic_network.py",
    "blindhorse/validators/sentropy.py",
    "blindhorse/validators/maxwell_demon.py",
    "blindhorse/validators/gear_ratio.py",
    "blindhorse/validators/phase_lock.py",
    "blindhorse/validators/semantic_gravity.py",
    "blindhorse/validators/trans_planckian.py",
    "blindhorse/validators/categorical_state.py",
    "blindhorse/validators/therapeutic_prediction.py",
]

def fix_imports(content: str) -> str:
    """Add utils import if not present."""
    if "from ..utils import save_json" in content:
        return content
    
    # Find where to insert (after other imports)
    lines = content.split('\n')
    import_section_end = 0
    for i, line in enumerate(lines):
        if line.strip() and not line.strip().startswith(('"""', '#', 'import', 'from')):
            import_section_end = i
            break
    
    # Insert new import
    lines.insert(import_section_end - 1, "from ..utils import save_json")
    return '\n'.join(lines)

def fix_save_results(content: str) -> str:
    """Replace json.dump with save_json."""
    # Pattern: with open(...) as f:\n        json.dump(results, f, ...)
    pattern = r'(\s+)with open\(output_file, [\'"]w[\'"]\) as f:\s*\n\s+json\.dump\(results, f[^\)]*\)'
    
    replacement = r'\1save_json(results, output_file)'
    
    content = re.sub(pattern, replacement, content)
    
    return content

def main():
    print("Fixing JSON serialization in validators...")
    
    for filepath in validator_files:
        path = Path(filepath)
        if not path.exists():
            print(f"  ⚠ Skipping {filepath} (not found)")
            continue
        
        print(f"  Processing {filepath}...")
        
        # Read file
        content = path.read_text(encoding='utf-8')
        
        # Apply fixes
        content = fix_imports(content)
        content = fix_save_results(content)
        
        # Write back
        path.write_text(content, encoding='utf-8')
        
        print(f"  ✓ Fixed {filepath}")
    
    print("\n✓ All validators updated!")

if __name__ == "__main__":
    main()

