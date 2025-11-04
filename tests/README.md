# Testing Guide

This folder contains functional tests for the code-tokenizer package.

## Quick Start

### Run all tests
```bash
uv run pytest
```

### Run specific test file
```bash
uv run pytest tests/functional/test_file_analyzer.py
uv run pytest tests/functional/test_code_collector.py
uv run pytest tests/functional/test_code_analyzer.py
```

### Run with verbose output
```bash
uv run pytest -v
```

### Check test coverage
```bash
uv run pytest --cov=src/code_tokenizer --cov-report=term-missing
```

## Test Structure

- `tests/functional/` - Contains all functional tests
  - `test_file_analyzer.py` - FileAnalyzer core functionality tests
  - `test_code_collector.py` - CodeCollector functionality tests
  - `test_code_analyzer.py` - CodeAnalyzer integration tests

## Notes

- Uses uv for dependency management
- Requires pytest and pytest-cov for coverage reporting
