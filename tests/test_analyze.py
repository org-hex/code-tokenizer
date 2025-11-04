"""
Tests for analyze module
"""

import pytest
import tempfile
import os
from code_tokenizer.core import FileAnalyzer


class TestFileAnalyzer:
    """Test FileAnalyzer class"""

    def setup_method(self):
        """Setup test environment"""
        self.analyzer = FileAnalyzer()

    def test_analyze_python_file(self):
        """Test analyzing Python file"""
        python_content = '''
import os
import sys

def calculate_sum(a, b):
    """Calculate the sum of two numbers"""
    return a + b

class Calculator:
    """Simple calculator class"""

    def __init__(self):
        self.history = []

    def add(self, a, b):
        result = calculate_sum(a, b)
        self.history.append(f"{a} + {b} = {result}")
        return result

if __name__ == "__main__":
    calc = Calculator()
    print(calc.add(5, 3))
'''

        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.py') as f:
            f.write(python_content)
            f.flush()

            result = self.analyzer.analyze_file(f.name)

            assert result is not None
            assert 'lines' in result
            assert 'words' in result
            assert 'chars' in result
            assert 'size' in result
            assert 'encoding' in result
            assert result['lines'] > 0
            assert result['words'] > 0
            assert result['chars'] > 0
            assert result['size'] > 0

            os.unlink(f.name)

    def test_analyze_empty_file(self):
        """Test analyzing empty file"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("")
            f.flush()

            result = self.analyzer.analyze_file(f.name)

            assert result is not None
            assert result['lines'] == 0
            assert result['words'] == 0
            assert result['chars'] == 0
            assert result['size'] == 0

            os.unlink(f.name)

    def test_analyze_nonexistent_file(self):
        """Test analyzing nonexistent file"""
        result = self.analyzer.analyze_file("/path/to/nonexistent/file.txt")
        assert result is None

    def test_detect_encoding_utf8(self):
        """Test UTF-8 encoding detection"""
        content = "Hello, world! 🌍"

        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as f:
            f.write(content)
            f.flush()

            encoding = self.analyzer.detect_encoding(f.name)
            assert encoding.lower() in ['utf-8', 'utf8']

            os.unlink(f.name)

    def test_analyze_file_with_special_characters(self):
        """Test analyzing file with special characters"""
        content = '''
Test Chinese characters
Test with émojis 🚀 🌟
Special chars: àáâãäå
'''

        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as f:
            f.write(content)
            f.flush()

            result = self.analyzer.analyze_file(f.name)

            assert result is not None
            assert result['lines'] > 0
            assert result['chars'] > 0
            assert '🚀' in str(result.get('content', ''))
            assert 'Test' in str(result.get('content', ''))

            os.unlink(f.name)

    def test_count_words_with_special_characters(self):
        """Test word counting with special characters"""
        test_cases = [
            ("Hello world", 2),
            ("Hello, world!", 2),
            ("One-word", 1),
            ("", 0),
            ("   ", 0),
            ("Hello   world   test", 3),
        ]

        for text, expected_count in test_cases:
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
                f.write(text)
                f.flush()

                result = self.analyzer.analyze_file(f.name)
                assert result['words'] == expected_count

                os.unlink(f.name)

    def test_analyze_large_file(self):
        """Test analyzing larger file"""
        # Create a file with many lines
        lines = ["Line number {}: This is a test line with some content.".format(i)
                for i in range(100)]

        content = "\n".join(lines)

        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write(content)
            f.flush()

            result = self.analyzer.analyze_file(f.name)

            assert result is not None
            assert result['lines'] == 100
            assert result['words'] > 100  # Each line has multiple words
            assert result['size'] > 0

            os.unlink(f.name)