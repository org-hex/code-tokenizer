"""
Pytest configuration and fixtures for code-tokenizer tests
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


@pytest.fixture
def sample_typescript_file(temp_dir):
    """Create a sample TypeScript file for testing"""
    ts_content = '''
// TypeScript interfaces and classes
interface User {
    id: number;
    name: string;
    email: string;
    isActive: boolean;
}

interface Product {
    id: number;
    title: string;
    price: number;
    category: string;
}

class UserService {
    private users: User[] = [];

    constructor() {
        this.loadUsers();
    }

    private loadUsers(): void {
        // Load users from API or storage
        this.users = [
            { id: 1, name: "John Doe", email: "john@example.com", isActive: true },
            { id: 2, name: "Jane Smith", email: "jane@example.com", isActive: false }
        ];
    }

    public getUsers(): User[] {
        return this.users.filter(user => user.isActive);
    }

    public getUserById(id: number): User | undefined {
        return this.users.find(user => user.id === id);
    }

    public addUser(user: Omit<User, 'id'>): User {
        const newUser: User = {
            id: Math.max(...this.users.map(u => u.id)) + 1,
            ...user
        };
        this.users.push(newUser);
        return newUser;
    }
}

class ProductService {
    private products: Product[] = [];

    constructor() {
        this.loadProducts();
    }

    private loadProducts(): void {
        this.products = [
            { id: 1, title: "Laptop", price: 999.99, category: "Electronics" },
            { id: 2, title: "Book", price: 19.99, category: "Education" },
            { id: 3, title: "Coffee", price: 4.99, category: "Food" }
        ];
    }

    public getProductsByCategory(category: string): Product[] {
        return this.products.filter(product => product.category === category);
    }

    public getProductsUnderPrice(maxPrice: number): Product[] {
        return this.products.filter(product => product.price <= maxPrice);
    }
}

// Usage examples
const userService = new UserService();
const productService = new ProductService();

const activeUsers = userService.getUsers();
const electronics = productService.getProductsByCategory("Electronics");
const affordableItems = productService.getProductsUnderPrice(100);

console.log(`Active users: ${activeUsers.length}`);
console.log(`Electronics: ${electronics.length}`);
console.log(`Affordable items: ${affordableItems.length}`);
'''

    file_path = temp_dir / "sample.ts"
    file_path.write_text(ts_content)
    return file_path


@pytest.fixture
def sample_json_file(temp_dir):
    """Create a sample JSON file for testing"""
    json_content = {
        "project": {
            "name": "test-project",
            "version": "1.0.0",
            "description": "A test project for code tokenizer",
            "dependencies": {
                "pytest": "^7.0.0",
                "click": "^8.0.0",
                "rich": "^13.0.0",
                "tiktoken": "^0.5.0"
            },
            "scripts": {
                "test": "pytest tests/",
                "lint": "flake8 src/",
                "build": "python -m build"
            }
        },
        "users": [
            {
                "id": 1,
                "name": "Alice",
                "email": "alice@example.com",
                "roles": ["admin", "developer"],
                "active": True
            },
            {
                "id": 2,
                "name": "Bob",
                "email": "bob@example.com",
                "roles": ["user"],
                "active": True
            }
        ],
        "settings": {
            "debug": True,
            "logLevel": "INFO",
            "maxConnections": 100,
            "timeout": 30
        }
    }

    import json
    file_path = temp_dir / "config.json"
    file_path.write_text(json.dumps(json_content, indent=2))
    return file_path


@pytest.fixture
def sample_markdown_file(temp_dir):
    """Create a sample Markdown file for testing"""
    md_content = '''# Code Tokenizer Project

This is a comprehensive code analysis and token calculation tool.

## Features

- **File Analysis**: Analyze various file types and calculate statistics
- **Token Calculation**: Calculate tokens for different AI models
- **Encoding Support**: Support multiple file encodings (UTF-8, GBK, Latin-1)
- **Project Scanning**: Scan entire projects with customizable patterns
- **Cache Management**: Intelligent caching for improved performance
- **Rich Output**: Beautiful formatted output using Rich library

## Installation

```bash
pip install code-tokenizer
```

## Usage

### Basic File Analysis

```python
from code_tokenizer import FileAnalyzer

analyzer = FileAnalyzer()
result = analyzer.analyze_file("example.py")
print(f"Tokens: {result['token_count']}")
```

### Project Analysis

```python
from code_tokenizer import CodeCollector

collector = CodeCollector()
files = collector.scan_files("/path/to/project")
print(f"Found {len(files)} files")
```

## Supported File Types

- Python (.py)
- JavaScript (.js)
- TypeScript (.ts)
- JSON (.json)
- Markdown (.md)
- And many more...

## Configuration

The tool can be configured with various options:

- File patterns to include/exclude
- Cache settings
- Output formats
- Token calculation models

## API Reference

### FileAnalyzer

Main class for analyzing individual files.

#### Methods

- `analyze_file(file_path)`: Analyze a single file
- `calculate_tokens(content)`: Calculate tokens for content
- `read_file_with_encoding(file_path)`: Read file with encoding detection

### CodeCollector

Class for collecting and managing multiple files.

#### Methods

- `scan_files(project_path, ...)`: Scan project for files
- `collect_code(...)`: Collect code to output file
- `clear_cache()`: Clear analysis cache

## Examples

### Example 1: Simple Analysis

```python
from code_tokenizer import FileAnalyzer

analyzer = FileAnalyzer()
result = analyzer.analyze_file("my_script.py")

print(f"File size: {result['file_size']} bytes")
print(f"Lines: {result['line_count']}")
print(f"Tokens: {result['token_count']}")
```

### Example 2: Project Scanning

```python
from code_tokenizer import CodeCollector

collector = CodeCollector()
files = collector.scan_files(
    "/my/project",
    file_patterns=["*.py", "*.js"],
    exclude_patterns=["test_*.py", "node_modules"]
)

print(f"Found {len(files)} files")
for file in files:
    print(f"  - {file}")
```

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## License

MIT License - see [LICENSE](LICENSE) file for details.

---

*Built with ❤️ for the developer community*
'''

    file_path = temp_dir / "README.md"
    file_path.write_text(md_content)
    return file_path


@pytest.fixture
def sample_large_file(temp_dir):
    """Create a larger sample file for testing performance"""
    lines = []

    # Add header
    lines.append("# Large Test File")
    lines.append("")
    lines.append("This file contains a lot of content to test performance.")
    lines.append("")

    # Add many similar functions
    for i in range(100):
        lines.extend([
            f"def function_{i}():",
            f'    """Function {i} - does some computation"""',
            f"    result = 0",
            f"    for j in range({i * 10}):",
            f"        result += j * 2",
            f"    return result",
            ""
        ])

    # Add a class with many methods
    lines.extend([
        "class LargeClass:",
        '    """A class with many methods for testing"""',
        "    def __init__(self):",
        "        self.data = list(range(1000))",
        ""
    ])

    for i in range(50):
        lines.extend([
            f"    def method_{i}(self):",
            f'        """Method {i} - processes data"""',
            f"        return sum(self.data[:{i * 20}])",
            ""
        ])

    content = "\n".join(lines)
    file_path = temp_dir / "large_file.py"
    file_path.write_text(content)
    return file_path


@pytest.fixture
def empty_file(temp_dir):
    """Create an empty file for testing edge cases"""
    file_path = temp_dir / "empty.txt"
    file_path.write_text("")
    return file_path


@pytest.fixture
def binary_file(temp_dir):
    """Create a binary file for testing encoding handling"""
    file_path = temp_dir / "binary.bin"

    # Create some binary data
    binary_data = bytes(range(256))  # All possible byte values
    file_path.write_bytes(binary_data)
    return file_path