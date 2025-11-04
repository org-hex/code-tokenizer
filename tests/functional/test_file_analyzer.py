"""
FileAnalyzer functional tests
Test file analysis, token calculation, encoding detection and other core features
"""

import pytest
import tempfile
from pathlib import Path
from src.code_tokenizer.core import FileAnalyzer


class TestFileAnalyzer:
    """FileAnalyzer test class"""

    def setup_method(self):
        """Setup before each test method"""
        self.analyzer = FileAnalyzer()

    def test_init(self):
        """Test FileAnalyzer initialization"""
        analyzer = FileAnalyzer()
        assert hasattr(analyzer, 'gpt35_encoding')
        assert hasattr(analyzer, 'gpt4_encoding')

    def test_analyze_file_basic(self, sample_python_file):
        """Test basic file analysis functionality"""
        result = self.analyzer.analyze_file(str(sample_python_file))

        # Verify the returned data structure
        assert isinstance(result, dict)
        assert 'file_path' in result
        assert 'file_size' in result
        assert 'line_count' in result
        assert 'non_empty_line_count' in result
        assert 'char_count' in result
        assert 'word_count' in result
        assert 'token_count' in result
        assert 'token_count_gpt4' in result
        assert 'avg_tokens_per_line' in result
        assert 'small_lines_count' in result
        assert 'small_lines_percentage' in result
        assert 'context_analysis' in result

        # Verify the correctness of basic data
        assert result['file_path'] == str(sample_python_file)
        assert result['file_size'] > 0
        assert result['line_count'] > 0
        assert result['char_count'] > 0
        assert result['word_count'] > 0
        assert result['token_count'] > 0
        assert result['token_count_gpt4'] > 0
        assert result['avg_tokens_per_line'] >= 0

    def test_analyze_nonexistent_file(self):
        """Test analyzing non-existent files"""
        with pytest.raises(FileNotFoundError):
            self.analyzer.analyze_file("/nonexistent/file.py")

    def test_read_file_with_encoding_utf8(self, temp_dir):
        """Test UTF-8 encoded file reading"""
        content = "这是一个测试文件\nTest file content\n测试中文编码"
        file_path = temp_dir / "test_utf8.txt"
        file_path.write_text(content, encoding='utf-8')

        read_content = FileAnalyzer.read_file_with_encoding(file_path)
        assert read_content == content

    def test_read_file_with_encoding_latin1(self, temp_dir):
        """Test Latin-1 encoded file reading"""
        content = "Simple test content\nBasic ASCII text"
        file_path = temp_dir / "test_latin1.txt"
        file_path.write_text(content, encoding='latin-1')

        read_content = FileAnalyzer.read_file_with_encoding(file_path)
        assert read_content == content

    def test_read_file_with_encoding_gbk(self, temp_dir):
        """Test GBK encoded file reading"""
        content = "这是GBK编码的测试文件\n中文内容测试"
        file_path = temp_dir / "test_gbk.txt"
        file_path.write_text(content, encoding='gbk')

        read_content = FileAnalyzer.read_file_with_encoding(file_path)
        assert read_content == content

    def test_read_nonexistent_file(self, temp_dir):
        """Test reading non-existent files"""
        nonexistent_file = temp_dir / "nonexistent.txt"
        with pytest.raises(FileNotFoundError):
            FileAnalyzer.read_file_with_encoding(nonexistent_file)

    def test_calculate_tokens(self):
        """Test token calculation"""
        content = "Hello, world! This is a test."
        gpt35_tokens, gpt4_tokens = self.analyzer.calculate_tokens(content)

        assert isinstance(gpt35_tokens, int)
        assert isinstance(gpt4_tokens, int)
        assert gpt35_tokens > 0
        assert gpt4_tokens > 0

    def test_calculate_tokens_empty_content(self):
        """Test token calculation for empty content"""
        gpt35_tokens, gpt4_tokens = self.analyzer.calculate_tokens("")

        assert gpt35_tokens == 0
        assert gpt4_tokens == 0

    def test_calculate_tokens_invalid_content(self):
        """Test token calculation for invalid content (should return 0 without crashing)"""
        # Use some content that might cause tiktoken errors
        invalid_content = None
        gpt35_tokens, gpt4_tokens = self.analyzer.calculate_tokens(invalid_content)

        # Should return 0 instead of crashing
        assert gpt35_tokens == 0
        assert gpt4_tokens == 0

    def test_count_chinese_words(self):
        """Test Chinese word count"""
        content = "这是一个测试\nHello world\n测试中英文统计123"
        word_count = FileAnalyzer.count_chinese_words(content)

        assert isinstance(word_count, int)
        assert word_count > 0
        # Should count Chinese characters, letters, numbers
        expected_chars = len(['这', '是', '一', '个', '测', '试', 'H', 'e', 'l', 'l', 'o', 'w', 'o', 'r', 'l', 'd', '测', '试', '中', '英', '文', '统', '计', '1', '2', '3'])
        assert word_count == expected_chars

    def test_count_chinese_words_empty(self):
        """Test Chinese word count for empty content"""
        word_count = FileAnalyzer.count_chinese_words("")
        assert word_count == 0

    def test_calculate_small_lines_ratio(self):
        """Test short line ratio calculation"""
        content = """短行
这是一个比较长的行，包含很多字符
x
y
这是一个中等长度的行
z
超长行超长行超长行超长行超长行超长行超长行超长行超长行超长行"""

        small_count, small_percentage = FileAnalyzer.calculate_small_lines_ratio(content)

        assert isinstance(small_count, int)
        assert isinstance(small_percentage, float)
        assert small_count == 4  # "短行", "x", "y", "z"
        assert 0 <= small_percentage <= 100

    def test_calculate_small_lines_ratio_empty(self):
        """Test short line ratio calculation for empty content"""
        small_count, small_percentage = FileAnalyzer.calculate_small_lines_ratio("")

        assert small_count == 0
        assert small_percentage == 0

    def test_calculate_small_lines_ratio_all_empty_lines(self):
        """Test content with only empty lines"""
        content = "\n\n\n\n"

        small_count, small_percentage = FileAnalyzer.calculate_small_lines_ratio(content)

        assert small_count == 0
        assert small_percentage == 0

    def test_analyze_context_windows(self):
        """Test context window analysis"""
        token_count = 1000

        context_analysis = self.analyzer.analyze_context_windows(token_count)

        assert isinstance(context_analysis, dict)
        assert len(context_analysis) > 0

        # Verify analysis results for each model
        for model_name, info in context_analysis.items():
            assert isinstance(model_name, str)
            assert isinstance(info, dict)
            assert 'limit' in info
            assert 'token_count' in info
            assert 'percentage' in info
            assert 'exceeded' in info

            assert info['limit'] > 0
            assert info['token_count'] == token_count
            assert 0 <= info['percentage'] <= 100
            assert isinstance(info['exceeded'], bool)

    def test_get_context_window_summary(self):
        """Test context window summary"""
        token_count = 1000

        summary = self.analyzer.get_context_window_summary(token_count)

        assert isinstance(summary, list)
        assert len(summary) > 0

        # Verify structure of each summary item
        for item in summary:
            assert isinstance(item, dict)
            assert 'model' in item
            assert 'percentage' in item
            assert 'token_count' in item
            assert 'limit' in item
            assert 'exceeded' in item

            assert isinstance(item['model'], str)
            assert isinstance(item['percentage'], float)
            assert isinstance(item['token_count'], int)
            assert isinstance(item['limit'], int)
            assert isinstance(item['exceeded'], bool)

    def test_get_project_statistics_empty(self):
        """Test empty project statistics"""
        stats = self.analyzer.get_project_statistics([])
        assert stats == {}

    def test_get_project_statistics_single_file(self, sample_python_file):
        """Test single file project statistics"""
        file_analysis = self.analyzer.analyze_file(str(sample_python_file))
        project_stats = self.analyzer.get_project_statistics([file_analysis])

        assert isinstance(project_stats, dict)
        assert 'total_files' in project_stats
        assert 'total_tokens' in project_stats
        assert 'total_size' in project_stats
        assert 'total_lines' in project_stats
        assert 'total_non_empty_lines' in project_stats
        assert 'empty_lines' in project_stats
        assert 'empty_line_percentage' in project_stats
        assert 'total_small_lines' in project_stats
        assert 'small_lines_percentage' in project_stats
        assert 'avg_file_size' in project_stats
        assert 'avg_tokens_per_file' in project_stats

        # Verify correctness of statistics
        assert project_stats['total_files'] == 1
        assert project_stats['total_tokens'] == file_analysis['token_count']
        assert project_stats['total_size'] == file_analysis['file_size']
        assert project_stats['total_lines'] == file_analysis['line_count']
        assert project_stats['avg_file_size'] == file_analysis['file_size']
        assert project_stats['avg_tokens_per_file'] == file_analysis['token_count']

    def test_get_project_statistics_multiple_files(self, sample_python_file, sample_javascript_file):
        """Test multi-file project statistics"""
        file1_analysis = self.analyzer.analyze_file(str(sample_python_file))
        file2_analysis = self.analyzer.analyze_file(str(sample_javascript_file))
        project_stats = self.analyzer.get_project_statistics([file1_analysis, file2_analysis])

        # Verify summary statistics
        assert project_stats['total_files'] == 2
        assert project_stats['total_tokens'] == file1_analysis['token_count'] + file2_analysis['token_count']
        assert project_stats['total_size'] == file1_analysis['file_size'] + file2_analysis['file_size']
        assert project_stats['total_lines'] == file1_analysis['line_count'] + file2_analysis['line_count']

        # Verify averages
        expected_avg_size = (file1_analysis['file_size'] + file2_analysis['file_size']) / 2
        assert abs(project_stats['avg_file_size'] - expected_avg_size) < 0.01

        expected_avg_tokens = (file1_analysis['token_count'] + file2_analysis['token_count']) / 2
        assert abs(project_stats['avg_tokens_per_file'] - expected_avg_tokens) < 0.01

    def test_file_analysis_with_actual_python_content(self, temp_dir):
        """Test file analysis with actual Python code"""
        python_code = '''
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

if __name__ == "__main__":
    calc = Calculator()
    print(calc.add(5, 3))
    print(f"Fibonacci(10) = {fibonacci(10)}")
'''
        file_path = temp_dir / "actual_code.py"
        file_path.write_text(python_code)

        result = self.analyzer.analyze_file(str(file_path))

        # Verify analysis results for actual code
        assert result['line_count'] > 10  # Should have enough lines
        assert result['char_count'] > 100  # Should have enough characters
        assert result['word_count'] > 20  # Should have enough words
        assert result['token_count'] > 10  # Should have enough tokens
        assert result['non_empty_line_count'] > 0
        assert result['avg_tokens_per_line'] > 0

    def test_file_analysis_with_minimal_content(self, temp_dir):
        """Test file analysis with minimal content"""
        minimal_content = "x"
        file_path = temp_dir / "minimal.py"
        file_path.write_text(minimal_content)

        result = self.analyzer.analyze_file(str(file_path))

        assert result['line_count'] == 0  # No newline characters
        assert result['char_count'] == 1
        assert result['word_count'] == 1
        assert result['token_count'] >= 1
        assert result['non_empty_line_count'] == 1  # Has one non-empty line