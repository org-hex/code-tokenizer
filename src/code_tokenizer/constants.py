"""Global constant definitions"""

# Default exclusion patterns
DEFAULT_EXCLUDE_PATTERNS = [
    "vendor", "node_modules", ".git", "__pycache__",
    "target", "build", "dist", ".venv", "venv", "env",
    ".github", ".code_cache", "code_collected_*.txt", 
    "output","package-lock.json"
]

# Default file patterns
DEFAULT_FILE_PATTERNS = [
    "*.go", "*.py", "*.js", "*.ts", "*.java", "*.cpp", "*.c",
    "*.h", "*.hpp", "*.yaml", "*.yml", "*.sh", "*.md",
    "*.json", "*.xml", "*.sql", "*.html", "*.css", "*.vue",
    "*.jsx", "*.tsx", "*.php", "*.rb", "*.swift", "*.kt"
]

# Context window configuration
CONTEXT_WINDOWS = {
    "GPT-4 (8K)": 8192,
    "GPT-4 (32K)": 32768,
    "GPT-4 Turbo (128K)": 128000,
    "Claude-4 (200K)": 200000
}