"""Code Tokenizer Package

For code file collection, analysis and token calculation.
"""

__author__ = "Code Tokenizer Team"

from pathlib import Path

def _get_version_from_pyproject():
    """Get version from pyproject.toml (development fallback)"""
    try:
        # Try to find pyproject.toml relative to this file
        current_dir = Path(__file__).parent.parent.parent
        pyproject_path = current_dir / "pyproject.toml"

        if pyproject_path.exists():
            with open(pyproject_path, "r", encoding="utf-8") as f:
                content = f.read()
                # Simple parsing - look for version = "x.x.x"
                for line in content.split('\n'):
                    line = line.strip()
                    if line.startswith('version = '):
                        # Extract version from version = "x.x.x"
                        version_str = line.split(' = ')[1].strip('"\'')
                        return version_str
    except Exception:
        pass

    # Fallback version if reading fails
    return "1.0.1"

def _get_version():
    """Get version using importlib.metadata with development fallback"""
    try:
        from importlib.metadata import version
        return version("code-tokenizer")
    except Exception:
        # Fallback to pyproject.toml reading for development
        return _get_version_from_pyproject()

__version__ = _get_version()

from .constants import (
    DEFAULT_EXCLUDE_PATTERNS,
    DEFAULT_FILE_PATTERNS,
    CONTEXT_WINDOWS,
)
from .utils import format_tokens, format_bytes

__all__ = [
    "DEFAULT_EXCLUDE_PATTERNS",
    "DEFAULT_FILE_PATTERNS",
    "CONTEXT_WINDOWS",
    "format_tokens",
    "format_bytes",
]