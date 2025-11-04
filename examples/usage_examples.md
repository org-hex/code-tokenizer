# Usage Examples

This document provides practical examples of how to use the Code Tokenizer tool.

## Basic Usage

### 1. Analyze Current Project

```bash
# Analyze all files in current project
python main.py collect .

# Analyze with custom output file
python main.py collect . --output my_project_tokens.txt

# Analyze without using cache
python main.py collect . --no-cache
```

### 2. Analyze Specific File Types

```bash
# Only Python files
python main.py collect . --patterns "*.py"

# Multiple file types
python main.py collect . --patterns "*.py,*.js,*.go"

# Web development files
python main.py collect . --patterns "*.js,*.jsx,*.ts,*.tsx,*.vue,*.html,*.css"
```

### 3. Exclude Directories

```bash
# Exclude common directories
python main.py collect . --exclude "vendor,node_modules,.git,__pycache__"

# Multiple exclusions
python main.py collect . --exclude "vendor,node_modules,build,dist,tests"
```

### 4. Scan Project Files

```bash
# Scan for supported files
python main.py scan .

# Scan with patterns
python main.py scan . --patterns "*.py,*.js"

# Scan with exclusions
python main.py scan . --exclude "vendor,node_modules"
```

### 5. Analyze Existing Token Files

```bash
# Analyze generated token file
python main.py analyze project_tokens.txt

# Analyze any text file
python main.py analyze ../large_code_file.txt
```

### 6. Cache Management

```bash
# List all cached calculations
python main.py cache-list

# Clear specific project cache
python main.py cache-clear --project myproject

# Clear all caches
python main.py cache-clear
```

## Advanced Examples

### Analyze Multiple Projects

```bash
# Analyze different projects
python main.py collect ~/projects/web-app --output web-app-tokens.txt
python main.py collect ~/projects/mobile-app --output mobile-app-tokens.txt

# Compare results
python main.py analyze web-app-tokens.txt
python main.py analyze mobile-app-tokens.txt
```

### Custom File Patterns

```bash
# Configuration files only
python main.py collect . --patterns "*.yaml,*.yml,*.json,*.toml"

# Documentation only
python main.py collect . --patterns "*.md,*.rst,*.txt"

# Specific language projects
python main.py collect . --patterns "*.go" --exclude "vendor"
python main.py collect . --patterns "*.java" --exclude "target,build"
```

### Integration with Development Workflow

```bash
# Before AI code review
python main.py collect src/ --patterns "*.py,*.js" --output for-ai-review.txt

# Check if project fits in context window
python main.py collect . --output full-project.txt
python main.py analyze full-project.txt

# Cost estimation for analysis
python main.py analyze project-tokens.txt
```

## Sample Output

### Token Collection Output

```
🔍 Scanning project: /path/to/project
📁 Found 15 files
🎯 Collecting code...
💾 Results saved to: project_tokens.txt

📊 Token Statistics:
- GPT-3.5 Turbo: 1,234 tokens
- GPT-4: 1,234 tokens
- GPT-4 32K: 1,234 tokens
- GPT-4 Turbo: 1,234 tokens
- Claude-4: 987 tokens
```

### Analysis Output

```
📊 File Analysis Report
File: project_tokens.txt
Size: 45.6 KB
Lines: 234
Characters: 46,789

🎯 Token Statistics:
GPT-4: 1,234 tokens (15% of 8K context)
GPT-4 32K: 1,234 tokens (4% of 32K context)
GPT-4 Turbo: 1,234 tokens (1% of 128K context)
Claude-4: 987 tokens (1% of 200K context)

✅ Project is suitable for direct submission to all mainstream AI models for analysis
```

## Tips and Best Practices

1. **Use Specific Patterns**: Focus on relevant file types to get accurate token counts
2. **Exclude Build Artifacts**: Always exclude build directories, node_modules, vendor, etc.
3. **Cache Management**: Use cache for speed, disable cache when files change frequently
4. **Context Window Planning**: Check token counts against AI model context limits
5. **Cost Estimation**: Use token counts to estimate AI API costs

## Integration Examples

### Pre-commit Hook

```bash
#!/bin/sh
# .git/hooks/pre-commit

echo "🔍 Checking project token count..."
python main.py collect . --output pre-commit-tokens.txt --no-cache

python main.py analyze pre-commit-tokens.txt
rm pre-commit-tokens.txt
```

### CI/CD Pipeline

```yaml
# .github/workflows/token-check.yml
name: Token Check
on: [push, pull_request]

jobs:
  token-check:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    - run: |
        pip install -e .
        python main.py collect . --output ci-tokens.txt
        python main.py analyze ci-tokens.txt
```

## Troubleshooting

### Common Issues

1. **Permission Denied**: Ensure you have read access to target directories
2. **No Files Found**: Check your file patterns and exclusion rules
3. **Large File Warnings**: Consider using file patterns to exclude large files
4. **Cache Issues**: Use `--no-cache` flag to bypass caching problems

### Getting Help

```bash
# Show help
python main.py --help

# Show command-specific help
python main.py collect --help
python main.py analyze --help
python main.py scan --help

# Show tool information
python main.py info
```