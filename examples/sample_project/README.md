# Sample Project

This is a sample project containing various file types to demonstrate the Code Tokenizer tool.

## Files

- `main.py` - Python file demonstrating file management functionality
- `utils.js` - JavaScript file with utility classes for string and array operations
- `README.md` - This file

## Usage

You can use this sample project to test the Code Tokenizer:

```bash
# Analyze all files in this sample project
code-tokenizer collect examples/sample_project/

# Analyze only Python files
code-tokenizer collect examples/sample_project/ --patterns "*.py"

# Analyze only JavaScript files
code-tokenizer collect examples/sample_project/ --patterns "*.js"

# Scan for supported files
code-tokenizer scan examples/sample_project/
```

## Expected Output

When you run the Code Tokenizer on this sample project, you should see:

- Python files: 1 (main.py)
- JavaScript files: 1 (utils.js)
- Markdown files: 1 (README.md)
- Total tokens: Varies by AI model (approximately 500-800 tokens)

This sample project provides a good test case for the tokenizer with different file types and code structures.