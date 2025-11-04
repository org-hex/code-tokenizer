"""
Tests for code_collector module
"""

import pytest
import tempfile
import os
from pathlib import Path
from code_tokenizer.code_collector import CodeCollector, CodeAnalyzer


class TestCodeCollector:
    """Test CodeCollector class"""

    def setup_method(self):
        """Setup test environment"""
        self.collector = CodeCollector()
        self.temp_dir = Path(tempfile.mkdtemp())

    def teardown_method(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_scan_files_with_empty_directory(self):
        """Test scanning empty directory"""
        files = self.collector.scan_files(str(self.temp_dir))
        assert files == []

    def test_scan_files_with_python_files(self):
        """Test scanning directory with Python files"""
        # Create test files
        (self.temp_dir / "test1.py").touch()
        (self.temp_dir / "test2.py").touch()
        (self.temp_dir / "readme.md").touch()

        files = self.collector.scan_files(str(self.temp_dir))

        # Should find Python files but not markdown
        assert len(files) == 2
        assert any(f.endswith("test1.py") for f in files)
        assert any(f.endswith("test2.py") for f in files)
        assert not any(f.endswith("readme.md") for f in files)

    def test_scan_files_with_custom_patterns(self):
        """Test scanning with custom file patterns"""
        # Create test files
        (self.temp_dir / "test.py").touch()
        (self.temp_dir / "test.js").touch()
        (self.temp_dir / "test.txt").touch()

        files = self.collector.scan_files(str(self.temp_dir), patterns="*.js")

        # Should only find JavaScript files
        assert len(files) == 1
        assert files[0].endswith("test.js")

    def test_exclude_directories(self):
        """Test excluding directories"""
        # Create directory structure
        (self.temp_dir / "src").mkdir()
        (self.temp_dir / "vendor").mkdir()
        (self.temp_dir / "src" / "app.py").touch()
        (self.temp_dir / "vendor" / "lib.py").touch()

        files = self.collector.scan_files(
            str(self.temp_dir),
            exclude="vendor"
        )

        # Should find files in src but not in vendor
        assert len(files) == 1
        assert "src" in files[0]
        assert "vendor" not in files[0]


class TestCodeAnalyzer:
    """Test CodeAnalyzer class"""

    def setup_method(self):
        """Setup test environment"""
        self.analyzer = CodeAnalyzer()

    def test_analyze_empty_file(self):
        """Test analyzing empty file"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("")
            f.flush()

            result = self.analyzer.analyze_file(f.name)

            assert result['total_lines'] == 0
            assert result['total_words'] == 0
            assert result['total_chars'] == 0
            assert result['total_tokens'] == 0

            os.unlink(f.name)

    def test_analyze_simple_python_file(self):
        """Test analyzing simple Python file"""
        python_code = '''
def hello_world():
    """Print hello world message"""
    print("Hello, World!")

if __name__ == "__main__":
    hello_world()
'''

        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.py') as f:
            f.write(python_code)
            f.flush()

            result = self.analyzer.analyze_file(f.name)

            assert result['total_lines'] > 0
            assert result['total_words'] > 0
            assert result['total_chars'] > 0
            assert result['total_tokens'] > 0
            assert 'file_size' in result
            assert 'file_name' in result

            os.unlink(f.name)

    def test_token_calculation_for_different_models(self):
        """Test token calculation for different AI models"""
        text = "Hello, world! This is a test for token calculation."

        tokens_gpt35 = self.analyzer.calculate_tokens(text, "gpt-3.5-turbo")
        tokens_gpt4 = self.analyzer.calculate_tokens(text, "gpt-4")
        tokens_claude = self.analyzer.calculate_tokens(text, "Claude-4")

        # All models should return positive token counts
        assert tokens_gpt35 > 0
        assert tokens_gpt4 > 0
        assert tokens_claude > 0

        # GPT-3.5 and GPT-4 should use the same tokenizer (tiktoken)
        assert tokens_gpt35 == tokens_gpt4

    def test_calculate_tokens_with_empty_text(self):
        """Test token calculation with empty text"""
        tokens = self.analyzer.calculate_tokens("", "gpt-3.5-turbo")
        assert tokens == 0

    def test_calculate_tokens_with_none_text(self):
        """Test token calculation with None text"""
        tokens = self.analyzer.calculate_tokens(None, "gpt-3.5-turbo")
        assert tokens == 0

    def test_supported_models(self):
        """Test that all supported models return positive tokens"""
        text = "This is a test for supported models."

        supported_models = [
            "gpt-3.5-turbo",
            "gpt-4",
            "gpt-4-32k",
            "gpt-4-turbo",
            "Claude-4"
        ]

        for model in supported_models:
            tokens = self.analyzer.calculate_tokens(text, model)
            assert tokens > 0, f"Model {model} should return positive tokens"