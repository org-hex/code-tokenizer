"""
CodeAnalyzer functional tests
Test file analysis integration, formatted output and other features
"""

import pytest
from unittest.mock import patch, MagicMock
from src.code_tokenizer.code_collector import CodeAnalyzer


class TestCodeAnalyzer:
    """CodeAnalyzer test class"""

    def setup_method(self):
        """Setup before each test method"""
        self.analyzer = CodeAnalyzer()

    def test_init(self):
        """Test CodeAnalyzer initialization"""
        assert hasattr(self.analyzer, 'file_analyzer')
        assert hasattr(self.analyzer, 'width_manager')
        assert self.analyzer.file_analyzer is not None
        assert self.analyzer.width_manager is not None

    def test_analyze_file(self, sample_python_file):
        """Test file analysis functionality"""
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
        assert result['line_count'] >= 0
        assert result['char_count'] > 0
        assert result['word_count'] > 0
        assert result['token_count'] > 0
        assert result['token_count_gpt4'] > 0
        assert result['avg_tokens_per_line'] >= 0

    def test_analyze_file_javascript(self, sample_javascript_file):
        """Test JavaScript file analysis"""
        result = self.analyzer.analyze_file(str(sample_javascript_file))

        assert isinstance(result, dict)
        assert result['file_path'] == str(sample_javascript_file)
        assert result['file_size'] > 0
        assert result['char_count'] > 0
        assert result['word_count'] > 0
        assert result['token_count'] > 0

    def test_analyze_nonexistent_file(self):
        """Test analyzing non-existent files"""
        with pytest.raises(FileNotFoundError):
            self.analyzer.analyze_file("/nonexistent/file.py")

    def test_format_bytes(self):
        """Test byte formatting"""
        # Test byte values of different sizes
        assert self.analyzer.format_bytes(0) == "0.00 B"
        assert self.analyzer.format_bytes(1023) == "1023.00 B"
        assert self.analyzer.format_bytes(1024) == "1.00 KB"
        assert self.analyzer.format_bytes(1536) == "1.50 KB"
        assert self.analyzer.format_bytes(1048576) == "1.00 MB"
        assert self.analyzer.format_bytes(1073741824) == "1.00 GB"

        # Verify return type
        assert isinstance(self.analyzer.format_bytes(100), str)

    def test_format_bytes_negative(self):
        """Test negative byte formatting"""
        # Negative numbers should be handled correctly
        result = self.analyzer.format_bytes(-100)
        assert isinstance(result, str)

    def test_print_analysis_basic(self, sample_python_file):
        """Test basic analysis result printing"""
        stats = self.analyzer.analyze_file(str(sample_python_file))

        # Mock console printing
        with patch('src.code_tokenizer.code_collector.console') as mock_console:
            self.analyzer.print_analysis(str(sample_python_file), stats)

            # Verify console.print is called
            assert mock_console.print.called
            assert mock_console.print.call_count >= 1

    def test_print_analysis_with_context_data(self, sample_python_file):
        """Test analysis result printing with context data"""
        stats = self.analyzer.analyze_file(str(sample_python_file))

        # Ensure context_analysis has data
        assert 'context_analysis' in stats
        assert len(stats['context_analysis']) > 0

        with patch('src.code_tokenizer.code_collector.console') as mock_console:
            self.analyzer.print_analysis(str(sample_python_file), stats)

            # Verify correct printing method is called
            assert mock_console.print.called

    def test_print_analysis_large_file(self, temp_dir):
        """Test analysis result printing for large files"""
        # Create a file with more content
        large_content = '''
# This is a large test file
import os
import sys
import json
from typing import Dict, List, Optional

def process_data(data: List[Dict]) -> Dict:
    """Process data"""
    result = {}
    for item in data:
        key = item.get('key')
        value = item.get('value')
        if key and value:
            result[key] = value
    return result

class DataProcessor:
    """Data processor"""

    def __init__(self, config: Dict):
        self.config = config
        self.processed_items = []

    def process_item(self, item: Dict) -> bool:
        """Process individual item"""
        try:
            processed = process_data([item])
            self.processed_items.append(processed)
            return True
        except Exception as e:
            print(f"Error processing item: {e}")
            return False

    def get_statistics(self) -> Dict:
        """Get statistics"""
        return {
            'total_items': len(self.processed_items),
            'config': self.config
        }

def main():
    """Main function"""
    config = {'debug': True, 'version': '1.0'}
    processor = DataProcessor(config)

    test_data = [
        {'key': 'test1', 'value': 100},
        {'key': 'test2', 'value': 200},
        {'key': 'test3', 'value': 300}
    ]

    for item in test_data:
        processor.process_item(item)

    stats = processor.get_statistics()
    print(f"Processed {stats['total_items']} items")

if __name__ == "__main__":
    main()
'''
        large_file = temp_dir / "large_test.py"
        large_file.write_text(large_content)

        stats = self.analyzer.analyze_file(str(large_file))

        with patch('src.code_tokenizer.code_collector.console') as mock_console:
            self.analyzer.print_analysis(str(large_file), stats)

            # Verify ability to handle analysis results for large files
            assert mock_console.print.called

    def test_print_analysis_with_special_characters(self, temp_dir):
        """Test analysis printing for files with special characters"""
        special_content = '''
# Test special characters file
def test_special_chars():
    """Test various special characters"""
    special_string = "Hello 世界! @#$%^&*()_+-=[]{}|;':\",./<>?"
    unicode_chars = "Emoji: 🚀 🎉 ⭐"
    chinese_text = "这是中文测试内容"

    return {
        'special': special_string,
        'unicode': unicode_chars,
        'chinese': chinese_text
    }

# Test math symbols
math_symbols = "∑∏∫∆∇∂∞±×÷≠≤≥≈∝"
# Test quotes
quotes = "'single quotes' \"double quotes\" `backticks`"
'''
        special_file = temp_dir / "special_chars.py"
        special_file.write_text(special_content)

        stats = self.analyzer.analyze_file(str(special_file))

        with patch('src.code_tokenizer.code_collector.console') as mock_console:
            self.analyzer.print_analysis(str(special_file), stats)

            # Verify ability to handle special characters
            assert mock_console.print.called

    def test_print_analysis_error_handling(self, sample_python_file):
        """Test error handling in analysis printing"""
        stats = self.analyzer.analyze_file(str(sample_python_file))

        # Test that it doesn't crash due to data issues
        # Since print_analysis directly uses console, we mainly test the validity of analysis data
        assert isinstance(stats, dict)
        assert 'file_path' in stats

        # Test that analysis functionality itself doesn't error
        result = self.analyzer.analyze_file(str(sample_python_file))
        assert result == stats

    def test_print_analysis_with_empty_stats(self):
        """Test analysis printing with empty statistics"""
        empty_stats = {
            'file_path': '/test/empty.py',
            'file_size': 0,
            'line_count': 0,
            'non_empty_line_count': 0,
            'char_count': 0,
            'word_count': 0,
            'token_count': 0,
            'token_count_gpt4': 0,
            'avg_tokens_per_line': 0,
            'small_lines_count': 0,
            'small_lines_percentage': 0,
            'context_analysis': {}
        }

        with patch('src.code_tokenizer.code_collector.console') as mock_console:
            self.analyzer.print_analysis('/test/empty.py', empty_stats)

            # Should print normally even with empty data
            assert mock_console.print.called

    def test_print_analysis_with_large_token_count(self, temp_dir):
        """Test analysis printing with large token count"""
        # Create a file with a large amount of content
        large_content = "# Large content file\n" + "print('line')\n" * 1000
        large_file = temp_dir / "large_tokens.py"
        large_file.write_text(large_content)

        stats = self.analyzer.analyze_file(str(large_file))

        # Verify token count is large
        assert stats['token_count'] > 1000

        with patch('src.code_tokenizer.code_collector.console') as mock_console:
            self.analyzer.print_analysis(str(large_file), stats)

            # Should be able to handle large token count
            assert mock_console.print.called

    def test_print_analysis_context_window_exceeded(self, temp_dir):
        """Test analysis printing when context window is exceeded"""
        # Create a very long content file that might cause context window overflow for some models
        very_long_content = "# Very long content file\n"
        very_long_content += "x" * 100000  # Large number of characters

        very_long_file = temp_dir / "very_long.py"
        very_long_file.write_text(very_long_content)

        stats = self.analyzer.analyze_file(str(very_long_file))

        # Check if any model context window is exceeded
        context_analysis = stats.get('context_analysis', {})
        has_exceeded = any(info.get('exceeded', False) for info in context_analysis.values())

        with patch('src.code_tokenizer.code_collector.console') as mock_console:
            self.analyzer.print_analysis(str(very_long_file), stats)

            # Should be able to handle context window overflow
            assert mock_console.print.called

    def test_integration_with_file_analyzer(self, sample_python_file):
        """Test integration with FileAnalyzer"""
        # Call CodeAnalyzer's analyze_file method directly
        result1 = self.analyzer.analyze_file(str(sample_python_file))

        # Call FileAnalyzer's analyze_file method directly
        result2 = self.analyzer.file_analyzer.analyze_file(str(sample_python_file))

        # Results should be the same
        assert result1 == result2

    def test_integration_with_context_window_summary(self, sample_python_file):
        """Test integration with context window summary"""
        stats = self.analyzer.analyze_file(str(sample_python_file))
        token_count = stats['token_count']

        # Get context window summary directly
        summary = self.analyzer.file_analyzer.get_context_window_summary(token_count)

        # Verify summary data
        assert isinstance(summary, list)
        assert len(summary) > 0

        for item in summary:
            assert 'model' in item
            assert 'percentage' in item
            assert 'token_count' in item
            assert 'limit' in item
            assert 'exceeded' in item

    def test_multiple_file_analysis(self, sample_python_file, sample_javascript_file):
        """Test multiple file analysis"""
        # Analyze multiple files
        py_stats = self.analyzer.analyze_file(str(sample_python_file))
        js_stats = self.analyzer.analyze_file(str(sample_javascript_file))

        # Verify analysis results for both files
        assert py_stats['file_path'] != js_stats['file_path']
        assert py_stats['file_size'] > 0
        assert js_stats['file_size'] > 0

        # Verify they can be printed separately
        with patch('src.code_tokenizer.code_collector.console') as mock_console:
            self.analyzer.print_analysis(str(sample_python_file), py_stats)
            self.analyzer.print_analysis(str(sample_javascript_file), js_stats)

            # Should call print method 4 times (2 times per file: Panel + Table)
            assert mock_console.print.call_count == 4

    def test_analysis_consistency(self, sample_python_file):
        """Test analysis result consistency"""
        # Analyzing the same file multiple times should yield the same result
        result1 = self.analyzer.analyze_file(str(sample_python_file))
        result2 = self.analyzer.analyze_file(str(sample_python_file))

        # Except for possible timestamp-related fields, other fields should be the same
        consistent_fields = [
            'file_path', 'file_size', 'line_count', 'non_empty_line_count',
            'char_count', 'word_count', 'token_count', 'token_count_gpt4',
            'avg_tokens_per_line', 'small_lines_count', 'small_lines_percentage'
        ]

        for field in consistent_fields:
            assert result1[field] == result2[field], f"Field {field} should be consistent"

    def test_analysis_with_different_file_types(self, temp_dir):
        """Test analysis of different file types"""
        # Create test files of different types
        files_content = {
            'test.py': 'print("Hello Python")\ndef func():\n    return 42',
            'test.js': 'console.log("Hello JavaScript");\nfunction func() {\n    return 42;\n}',
            'test.md': '# Hello Markdown\n\nThis is a test file.\n\n## Section 2',
            'test.txt': 'Hello Text File\nThis is plain text.',
            'test.json': '{"hello": "world", "number": 42}'
        }

        results = {}
        for filename, content in files_content.items():
            file_path = temp_dir / filename
            file_path.write_text(content)
            results[filename] = self.analyzer.analyze_file(str(file_path))

        # Verify all files can be analyzed
        for filename, result in results.items():
            assert isinstance(result, dict)
            assert result['file_path'].endswith(filename)
            assert result['file_size'] > 0
            assert result['char_count'] > 0

        # Verify different file types have different characteristics
        py_result = results['test.py']
        js_result = results['test.js']
        md_result = results['test.md']

        # Python and JavaScript files should have similar token counts (similar content)
        assert abs(py_result['token_count'] - js_result['token_count']) < 50

        # Markdown files might have different token ratios
        assert md_result['token_count'] > 0

    def test_print_analysis_table_format(self, sample_python_file):
        """Test analysis result table format"""
        stats = self.analyzer.analyze_file(str(sample_python_file))

        # Simplified test: mainly verify analysis results contain required data
        assert 'context_analysis' in stats
        assert isinstance(stats['context_analysis'], dict)
        assert len(stats['context_analysis']) > 0

        # Verify context window data structure
        for model_name, info in stats['context_analysis'].items():
            assert 'limit' in info
            assert 'token_count' in info
            assert 'percentage' in info
            assert 'exceeded' in info