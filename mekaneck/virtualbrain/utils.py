"""
Utility functions for the Virtual Brain framework.

Provides JSON encoding, file I/O, and other utilities.
"""

import json
from pathlib import Path
from typing import Dict, Any
import numpy as np


class NumpyEncoder(json.JSONEncoder):
    """JSON encoder that handles numpy types."""

    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, np.bool_):
            return bool(obj)
        if isinstance(obj, Path):
            return str(obj)
        return super().default(obj)


def save_json(data: Dict[str, Any], filepath: Path) -> None:
    """
    Save dictionary to JSON file.

    Args:
        data: Dictionary to save
        filepath: Output file path
    """
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)

    with open(filepath, "w") as f:
        json.dump(data, f, indent=2, cls=NumpyEncoder)


def load_json(filepath: Path) -> Dict[str, Any]:
    """
    Load dictionary from JSON file.

    Args:
        filepath: Input file path

    Returns:
        Loaded dictionary
    """
    with open(filepath, "r") as f:
        return json.load(f)


def format_scientific(value: float, precision: int = 3) -> str:
    """Format number in scientific notation."""
    return f"{value:.{precision}e}"


def format_percentage(value: float, precision: int = 1) -> str:
    """Format number as percentage."""
    return f"{value * 100:.{precision}f}%"
