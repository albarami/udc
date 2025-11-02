"""
Helper functions for the intelligence system.
Will be populated as needed during development.
"""

from typing import Any, Dict, List


def format_currency(amount: float, currency: str = "QR") -> str:
    """Format currency amount with proper formatting"""
    if amount >= 1_000_000_000:
        return f"{currency} {amount / 1_000_000_000:.1f}bn"
    elif amount >= 1_000_000:
        return f"{currency} {amount / 1_000_000:.1f}m"
    elif amount >= 1_000:
        return f"{currency} {amount / 1_000:.1f}k"
    else:
        return f"{currency} {amount:.2f}"


def extract_numbers(text: str) -> List[float]:
    """Extract all numbers from text"""
    import re
    pattern = r'-?\d+(?:\.\d+)?'
    matches = re.findall(pattern, text)
    return [float(m) for m in matches]


def calculate_percentage_change(old_value: float, new_value: float) -> float:
    """Calculate percentage change between two values"""
    if old_value == 0:
        return 0.0
    return ((new_value - old_value) / old_value) * 100
