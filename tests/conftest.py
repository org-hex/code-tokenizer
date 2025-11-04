"""
Pytest configuration and fixtures
"""

import pytest
import tempfile
import os
from pathlib import Path


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing"""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    # Cleanup
    import shutil
    shutil.rmtree(temp_path)


@pytest.fixture
def sample_python_file(temp_dir):
    """Create a sample Python file for testing"""
    python_content = '''
import os
import sys

def fibonacci(n):
    """Calculate fibonacci number"""
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

class Calculator:
    """Simple calculator class"""

    def __init__(self):
        self.history = []

    def add(self, a, b):
        result = a + b
        self.history.append(f"{a} + {b} = {result}")
        return result

    def multiply(self, a, b):
        result = a * b
        self.history.append(f"{a} * {b} = {result}")
        return result

if __name__ == "__main__":
    calc = Calculator()
    print(calc.add(5, 3))
    print(calc.multiply(4, 7))
    print(f"Fibonacci(10) = {fibonacci(10)}")
'''

    file_path = temp_dir / "sample.py"
    file_path.write_text(python_content)
    return file_path


@pytest.fixture
def sample_javascript_file(temp_dir):
    """Create a sample JavaScript file for testing"""
    js_content = '''
// Utility functions for array manipulation
const ArrayUtils = {
    // Calculate sum of array elements
    sum: function(arr) {
        return arr.reduce((acc, val) => acc + val, 0);
    },

    // Find maximum value in array
    max: function(arr) {
        return Math.max(...arr);
    },

    // Filter array based on condition
    filter: function(arr, condition) {
        return arr.filter(condition);
    },

    // Map array elements
    map: function(arr, transform) {
        return arr.map(transform);
    }
};

// Example usage
const numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];
const evenNumbers = ArrayUtils.filter(numbers, x => x % 2 === 0);
const doubled = ArrayUtils.map(evenNumbers, x => x * 2);
const total = ArrayUtils.sum(doubled);

console.log("Original array:", numbers);
console.log("Even numbers:", evenNumbers);
console.log("Doubled even numbers:", doubled);
console.log("Total sum:", total);
'''

    file_path = temp_dir / "sample.js"
    file_path.write_text(js_content)
    return file_path


@pytest.fixture
def sample_project_structure(temp_dir):
    """Create a sample project structure for testing"""
    # Create directories
    (temp_dir / "src").mkdir()
    (temp_dir / "tests").mkdir()
    (temp_dir / "docs").mkdir()
    (temp_dir / "node_modules").mkdir()  # This should be excluded

    # Create main.py
    (temp_dir / "src" / "main.py").write_text('''
def main():
    """Main function"""
    print("Hello from main!")

if __name__ == "__main__":
    main()
''')

    # Create utils.py
    (temp_dir / "src" / "utils.py").write_text('''
def helper_function():
    """Helper function"""
    return "Helper result"

class HelperClass:
    """Helper class"""
    def __init__(self):
        self.value = 42

    def get_value(self):
        return self.value
''')

    # Create test file
    (temp_dir / "tests" / "test_main.py").write_text('''
import pytest
from src.main import main

def test_main():
    """Test main function"""
    # This is a test
    assert True
''')

    # Create README
    (temp_dir / "README.md").write_text('''
# Sample Project

This is a sample project for testing.

## Installation

```bash
pip install -e .
```

## Usage

```python
from src.main import main
main()
```
''')

    # Create external dependency (should be excluded)
    (temp_dir / "node_modules" / "external.js").write_text('''
// This is an external dependency
console.log("This should be excluded from token count");
''')

    return temp_dir