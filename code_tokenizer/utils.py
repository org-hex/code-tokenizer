"""Common utility functions"""

import math
from typing import Union


def format_tokens(token_count: Union[int, float]) -> str:
    """Format token count display, show as k unit for values greater than 1000"""
    if token_count >= 1000:
        return f"{token_count/1000:.1f}k"
    else:
        # For floating point numbers, display directly without thousand separators
        if isinstance(token_count, float):
            return f"{token_count:.0f}" if token_count.is_integer() else f"{token_count:.1f}"
        else:
            return f"{token_count}"


def format_bytes(bytes_value: int) -> str:
    """Format byte count into human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.2f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.2f} TB"