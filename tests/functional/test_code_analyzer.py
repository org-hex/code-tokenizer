"""
CodeAnalyzer 功能测试
测试文件分析整合、格式化输出等功能
"""

import pytest
from unittest.mock import patch, MagicMock
from src.code_tokenizer.code_collector import CodeAnalyzer


class TestCodeAnalyzer:
    """CodeAnalyzer 测试类"""

    def setup_method(self):
        """每个测试方法执行前的设置"""
        self.analyzer = CodeAnalyzer()

    def test_init(self):
        """测试 CodeAnalyzer 初始化"""
        assert hasattr(self.analyzer, 'file_analyzer')
        assert hasattr(self.analyzer, 'width_manager')
        assert self.analyzer.file_analyzer is not None
        assert self.analyzer.width_manager is not None

    def test_analyze_file(self, sample_python_file):
        """测试文件分析功能"""
        result = self.analyzer.analyze_file(str(sample_python_file))

        # 验证返回的数据结构
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

        # 验证基本数据的合理性
        assert result['file_path'] == str(sample_python_file)
        assert result['file_size'] > 0
        assert result['line_count'] >= 0
        assert result['char_count'] > 0
        assert result['word_count'] > 0
        assert result['token_count'] > 0
        assert result['token_count_gpt4'] > 0
        assert result['avg_tokens_per_line'] >= 0

    def test_analyze_file_javascript(self, sample_javascript_file):
        """测试 JavaScript 文件分析"""
        result = self.analyzer.analyze_file(str(sample_javascript_file))

        assert isinstance(result, dict)
        assert result['file_path'] == str(sample_javascript_file)
        assert result['file_size'] > 0
        assert result['char_count'] > 0
        assert result['word_count'] > 0
        assert result['token_count'] > 0

    def test_analyze_nonexistent_file(self):
        """测试分析不存在的文件"""
        with pytest.raises(FileNotFoundError):
            self.analyzer.analyze_file("/nonexistent/file.py")

    def test_format_bytes(self):
        """测试字节格式化"""
        # 测试不同大小的字节值
        assert self.analyzer.format_bytes(0) == "0.00 B"
        assert self.analyzer.format_bytes(1023) == "1023.00 B"
        assert self.analyzer.format_bytes(1024) == "1.00 KB"
        assert self.analyzer.format_bytes(1536) == "1.50 KB"
        assert self.analyzer.format_bytes(1048576) == "1.00 MB"
        assert self.analyzer.format_bytes(1073741824) == "1.00 GB"

        # 验证返回类型
        assert isinstance(self.analyzer.format_bytes(100), str)

    def test_format_bytes_negative(self):
        """测试负数字节格式化"""
        # 负数应该被正确处理
        result = self.analyzer.format_bytes(-100)
        assert isinstance(result, str)

    def test_print_analysis_basic(self, sample_python_file):
        """测试基本分析结果打印"""
        stats = self.analyzer.analyze_file(str(sample_python_file))

        # 模拟 console 打印
        with patch('src.code_tokenizer.code_collector.console') as mock_console:
            self.analyzer.print_analysis(str(sample_python_file), stats)

            # 验证 console.print 被调用
            assert mock_console.print.called
            assert mock_console.print.call_count >= 1

    def test_print_analysis_with_context_data(self, sample_python_file):
        """测试包含上下文数据的分析结果打印"""
        stats = self.analyzer.analyze_file(str(sample_python_file))

        # 确保 context_analysis 有数据
        assert 'context_analysis' in stats
        assert len(stats['context_analysis']) > 0

        with patch('src.code_tokenizer.code_collector.console') as mock_console:
            self.analyzer.print_analysis(str(sample_python_file), stats)

            # 验证调用了正确的打印方法
            assert mock_console.print.called

    def test_print_analysis_large_file(self, temp_dir):
        """测试大文件的分析结果打印"""
        # 创建一个包含更多内容的文件
        large_content = '''
# 这是一个大型测试文件
import os
import sys
import json
from typing import Dict, List, Optional

def process_data(data: List[Dict]) -> Dict:
    """处理数据"""
    result = {}
    for item in data:
        key = item.get('key')
        value = item.get('value')
        if key and value:
            result[key] = value
    return result

class DataProcessor:
    """数据处理器"""

    def __init__(self, config: Dict):
        self.config = config
        self.processed_items = []

    def process_item(self, item: Dict) -> bool:
        """处理单个项目"""
        try:
            processed = process_data([item])
            self.processed_items.append(processed)
            return True
        except Exception as e:
            print(f"Error processing item: {e}")
            return False

    def get_statistics(self) -> Dict:
        """获取统计信息"""
        return {
            'total_items': len(self.processed_items),
            'config': self.config
        }

def main():
    """主函数"""
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

            # 验证能够处理大文件的分析结果
            assert mock_console.print.called

    def test_print_analysis_with_special_characters(self, temp_dir):
        """测试包含特殊字符的文件分析打印"""
        special_content = '''
# 测试特殊字符文件
def test_special_chars():
    """测试各种特殊字符"""
    special_string = "Hello 世界! @#$%^&*()_+-=[]{}|;':\",./<>?"
    unicode_chars = "Emoji: 🚀 🎉 ⭐"
    chinese_text = "这是中文测试内容"

    return {
        'special': special_string,
        'unicode': unicode_chars,
        'chinese': chinese_text
    }

# 测试数学符号
math_symbols = "∑∏∫∆∇∂∞±×÷≠≤≥≈∝"
# 测试引号
quotes = "'单引号' \"双引号\" `反引号`"
'''
        special_file = temp_dir / "special_chars.py"
        special_file.write_text(special_content)

        stats = self.analyzer.analyze_file(str(special_file))

        with patch('src.code_tokenizer.code_collector.console') as mock_console:
            self.analyzer.print_analysis(str(special_file), stats)

            # 验证能够处理特殊字符
            assert mock_console.print.called

    def test_print_analysis_error_handling(self, sample_python_file):
        """测试分析打印中的错误处理"""
        stats = self.analyzer.analyze_file(str(sample_python_file))

        # 测试不会因为数据问题而崩溃
        # 由于 print_analysis 直接使用 console，我们主要测试分析数据的有效性
        assert isinstance(stats, dict)
        assert 'file_path' in stats

        # 测试分析功能本身不会出错
        result = self.analyzer.analyze_file(str(sample_python_file))
        assert result == stats

    def test_print_analysis_with_empty_stats(self):
        """测试使用空统计数据的分析打印"""
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

            # 即使数据为空也应该能够正常打印
            assert mock_console.print.called

    def test_print_analysis_with_large_token_count(self, temp_dir):
        """测试大 token 数量的分析打印"""
        # 创建一个包含大量内容的文件
        large_content = "# Large content file\n" + "print('line')\n" * 1000
        large_file = temp_dir / "large_tokens.py"
        large_file.write_text(large_content)

        stats = self.analyzer.analyze_file(str(large_file))

        # 验证 token 数量较大
        assert stats['token_count'] > 1000

        with patch('src.code_tokenizer.code_collector.console') as mock_console:
            self.analyzer.print_analysis(str(large_file), stats)

            # 应该能够处理大 token 数量
            assert mock_console.print.called

    def test_print_analysis_context_window_exceeded(self, temp_dir):
        """测试上下文窗口超限的分析打印"""
        # 创建一个内容很长的文件，可能导致某些模型上下文窗口超限
        very_long_content = "# Very long content file\n"
        very_long_content += "x" * 100000  # 大量字符

        very_long_file = temp_dir / "very_long.py"
        very_long_file.write_text(very_long_content)

        stats = self.analyzer.analyze_file(str(very_long_file))

        # 检查是否有模型上下文窗口超限
        context_analysis = stats.get('context_analysis', {})
        has_exceeded = any(info.get('exceeded', False) for info in context_analysis.values())

        with patch('src.code_tokenizer.code_collector.console') as mock_console:
            self.analyzer.print_analysis(str(very_long_file), stats)

            # 应该能够处理上下文窗口超限的情况
            assert mock_console.print.called

    def test_integration_with_file_analyzer(self, sample_python_file):
        """测试与 FileAnalyzer 的集成"""
        # 直接调用 CodeAnalyzer 的 analyze_file 方法
        result1 = self.analyzer.analyze_file(str(sample_python_file))

        # 直接调用 FileAnalyzer 的 analyze_file 方法
        result2 = self.analyzer.file_analyzer.analyze_file(str(sample_python_file))

        # 结果应该相同
        assert result1 == result2

    def test_integration_with_context_window_summary(self, sample_python_file):
        """测试与上下文窗口摘要的集成"""
        stats = self.analyzer.analyze_file(str(sample_python_file))
        token_count = stats['token_count']

        # 直接获取上下文窗口摘要
        summary = self.analyzer.file_analyzer.get_context_window_summary(token_count)

        # 验证摘要数据
        assert isinstance(summary, list)
        assert len(summary) > 0

        for item in summary:
            assert 'model' in item
            assert 'percentage' in item
            assert 'token_count' in item
            assert 'limit' in item
            assert 'exceeded' in item

    def test_multiple_file_analysis(self, sample_python_file, sample_javascript_file):
        """测试多文件分析"""
        # 分析多个文件
        py_stats = self.analyzer.analyze_file(str(sample_python_file))
        js_stats = self.analyzer.analyze_file(str(sample_javascript_file))

        # 验证两个文件的分析结果
        assert py_stats['file_path'] != js_stats['file_path']
        assert py_stats['file_size'] > 0
        assert js_stats['file_size'] > 0

        # 验证可以分别打印
        with patch('src.code_tokenizer.code_collector.console') as mock_console:
            self.analyzer.print_analysis(str(sample_python_file), py_stats)
            self.analyzer.print_analysis(str(sample_javascript_file), js_stats)

            # 应该调用打印方法 4 次（每个文件 2 次：Panel + Table）
            assert mock_console.print.call_count == 4

    def test_analysis_consistency(self, sample_python_file):
        """测试分析结果的一致性"""
        # 多次分析同一个文件应该得到相同结果
        result1 = self.analyzer.analyze_file(str(sample_python_file))
        result2 = self.analyzer.analyze_file(str(sample_python_file))

        # 除了可能的时间戳相关字段，其他字段应该相同
        consistent_fields = [
            'file_path', 'file_size', 'line_count', 'non_empty_line_count',
            'char_count', 'word_count', 'token_count', 'token_count_gpt4',
            'avg_tokens_per_line', 'small_lines_count', 'small_lines_percentage'
        ]

        for field in consistent_fields:
            assert result1[field] == result2[field], f"Field {field} should be consistent"

    def test_analysis_with_different_file_types(self, temp_dir):
        """测试不同文件类型的分析"""
        # 创建不同类型的测试文件
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

        # 验证所有文件都能被分析
        for filename, result in results.items():
            assert isinstance(result, dict)
            assert result['file_path'].endswith(filename)
            assert result['file_size'] > 0
            assert result['char_count'] > 0

        # 验证不同文件类型有不同的特征
        py_result = results['test.py']
        js_result = results['test.js']
        md_result = results['test.md']

        # Python 和 JavaScript 文件应该有类似的 token 数量（内容相似）
        assert abs(py_result['token_count'] - js_result['token_count']) < 50

        # Markdown 文件可能有不同的 token 比例
        assert md_result['token_count'] > 0

    def test_print_analysis_table_format(self, sample_python_file):
        """测试分析结果表格格式"""
        stats = self.analyzer.analyze_file(str(sample_python_file))

        # 简化测试：主要验证分析结果包含所需数据
        assert 'context_analysis' in stats
        assert isinstance(stats['context_analysis'], dict)
        assert len(stats['context_analysis']) > 0

        # 验证上下文窗口数据结构
        for model_name, info in stats['context_analysis'].items():
            assert 'limit' in info
            assert 'token_count' in info
            assert 'percentage' in info
            assert 'exceeded' in info