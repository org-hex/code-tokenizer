#!/usr/bin/env python3
"""
Sample Python project for testing Code Tokenizer
"""

import os
import sys
from pathlib import Path
from typing import List, Optional


class FileManager:
    """Simple file manager class"""

    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.files: List[str] = []

    def add_file(self, file_path: str) -> None:
        """Add a file to the manager"""
        if self.base_path.joinpath(file_path).exists():
            self.files.append(file_path)
        else:
            raise FileNotFoundError(f"File not found: {file_path}")

    def list_files(self) -> List[str]:
        """List all managed files"""
        return self.files.copy()

    def get_file_size(self, file_path: str) -> int:
        """Get file size in bytes"""
        full_path = self.base_path.joinpath(file_path)
        if full_path.exists():
            return full_path.stat().st_size
        return 0


def process_files(directory: str, pattern: Optional[str] = None) -> List[str]:
    """Process files in directory with optional pattern matching"""
    base_path = Path(directory)
    manager = FileManager(directory)

    if not base_path.exists():
        raise ValueError(f"Directory not found: {directory}")

    # Find files
    if pattern:
        files = list(base_path.glob(pattern))
    else:
        files = list(base_path.rglob("*.py"))

    # Add files to manager
    for file_path in files:
        relative_path = file_path.relative_to(base_path)
        manager.add_file(str(relative_path))

    return manager.list_files()


def calculate_total_size(file_list: List[str], base_path: str) -> int:
    """Calculate total size of files"""
    total_size = 0
    manager = FileManager(base_path)

    for file_path in file_list:
        total_size += manager.get_file_size(file_path)

    return total_size


def main():
    """Main function"""
    try:
        # Get current directory
        current_dir = os.getcwd()

        # Process Python files
        python_files = process_files(current_dir, "*.py")
        print(f"Found {len(python_files)} Python files")

        # Calculate total size
        total_size = calculate_total_size(python_files, current_dir)
        print(f"Total size: {total_size} bytes")

        # Display files
        print("\nFiles:")
        for file_path in python_files:
            manager = FileManager(current_dir)
            size = manager.get_file_size(file_path)
            print(f"  {file_path} ({size} bytes)")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()