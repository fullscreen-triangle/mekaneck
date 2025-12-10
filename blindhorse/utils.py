"""
Utility functions for Blindhorse validation suite.
"""

import json
import numpy as np
from pathlib import Path


class NumpyEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles numpy types."""
    
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, np.bool_):
            return bool(obj)
        elif isinstance(obj, Path):
            return str(obj)
        return super().default(obj)


def save_json(data: dict, filepath: Path):
    """
    Save data to JSON file with proper numpy type handling.
    
    Args:
        data: Dictionary to save
        filepath: Output file path
    """
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2, cls=NumpyEncoder)


def load_json(filepath: Path) -> dict:
    """
    Load JSON file.
    
    Args:
        filepath: Input file path
        
    Returns:
        Loaded dictionary
    """
    with open(filepath, 'r') as f:
        return json.load(f)

