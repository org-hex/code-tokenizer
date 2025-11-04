#!/usr/bin/env python3
"""
Core Code Analysis Module
Provides unified file analysis, token calculation, encoding handling and other core functions
"""

import os
import re
import tiktoken
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .constants import CONTEXT_WINDOWS
from .utils import format_bytes


class FileAnalyzer:
    """File Analyzer - Provides unified file analysis functionality"""

    def __init__(self):
        """Initialize the file analyzer"""
        # Initialize tokenizer
        try:
            self.gpt35_encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
            self.gpt4_encoding = tiktoken.encoding_for_model("gpt-4")
        except Exception as e:
            raise RuntimeError(f"Failed to initialize tokenizer: {e}")

  
    @staticmethod
    def calculate_small_lines_ratio(content: str) -> Tuple[int, float]:
        """Calculate the count and ratio of lines with less than 3 characters (excluding spaces, newlines, tabs)"""
        lines = content.split('\n')
        small_lines_count = 0
        total_lines = len(lines)

        for line in lines:
            # Remove whitespace characters (spaces, tabs, etc.) but keep other characters
            trimmed_line = line.strip()
            if trimmed_line and len(trimmed_line) < 3:
                small_lines_count += 1

        # Only calculate ratio for non-empty lines
        non_empty_lines = len([line for line in lines if line.strip()])
        small_lines_percentage = (small_lines_count / non_empty_lines * 100) if non_empty_lines > 0 else 0

        return small_lines_count, small_lines_percentage

    @staticmethod
    def read_file_with_encoding(file_path: Path) -> str:
        """Read file content with support for multiple encoding formats"""
        if not file_path.exists():
            raise FileNotFoundError(f"File does not exist: {file_path}")

        # Try different encoding formats
        encodings = ['utf-8', 'gbk', 'latin-1']

        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    return f.read()
            except UnicodeDecodeError:
                continue

        # If all encodings fail, try reading as binary and decode
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
                return content.decode('utf-8', errors='ignore')
        except Exception as e:
            raise IOError(f"Unable to read file {file_path}: {e}")

    @staticmethod
    def count_chinese_words(content: str) -> int:
        """Count Chinese words"""
        # Match Chinese characters, letters, numbers, punctuation
        words = re.findall(r'[\w\u4e00-\u9fff]', content)
        return len(words)

    def calculate_tokens(self, content: str) -> Tuple[int, int]:
        """Calculate token count, returns (GPT-3.5 tokens, GPT-4 tokens)"""
        try:
            # GPT-3.5 token calculation
            gpt35_tokens = self.gpt35_encoding.encode(content)
            gpt35_token_count = len(gpt35_tokens)

            # GPT-4 token calculation
            gpt4_tokens = self.gpt4_encoding.encode(content)
            gpt4_token_count = len(gpt4_tokens)

            return gpt35_token_count, gpt4_token_count
        except Exception as e:
            # If token calculation fails, return 0
            return 0, 0

    def analyze_context_windows(self, token_count: int) -> Dict[str, Dict]:
        """Analyze context window usage"""
        context_analysis = {}

        for model_name, limit in CONTEXT_WINDOWS.items():
            percentage = (token_count / limit) * 100
            context_analysis[model_name] = {
                'limit': limit,
                'token_count': token_count,
                'percentage': percentage,
                'exceeded': percentage > 100
            }

        return context_analysis

    def analyze_file(self, file_path: str) -> Dict:
        """Analyze complete file statistics"""
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"File does not exist: {file_path}")

        # Get file size
        try:
            file_size = file_path.stat().st_size
        except OSError as e:
            raise IOError(f"Unable to get file size: {e}")

        # Read file content
        try:
            content = self.read_file_with_encoding(file_path)
        except Exception as e:
            raise IOError(f"Unable to read file content: {e}")

        # Basic statistics - count newline characters to match wc -l
        line_count = content.count('\n')
        lines = content.split('\n')
        non_empty_lines = [line for line in lines if line.strip()]
        non_empty_line_count = len(non_empty_lines)
        char_count = len(content)

        # Word count (supports Chinese)
        word_count = self.count_chinese_words(content)

        # Token statistics
        token_count, token_count_gpt4 = self.calculate_tokens(content)

        # Average tokens per line
        avg_tokens_per_line = token_count / non_empty_line_count if non_empty_line_count > 0 else 0

        # Calculate small lines ratio
        small_lines_count, small_lines_percentage = self.calculate_small_lines_ratio(content)

        # Context window analysis
        context_analysis = self.analyze_context_windows(token_count)

        return {
            'file_path': str(file_path),
            'file_size': file_size,
            'line_count': line_count,
            'non_empty_line_count': non_empty_line_count,
            'char_count': char_count,
            'word_count': word_count,
            'token_count': token_count,
            'token_count_gpt4': token_count_gpt4,
            'avg_tokens_per_line': avg_tokens_per_line,
            'small_lines_count': small_lines_count,
            'small_lines_percentage': small_lines_percentage,
            'context_analysis': context_analysis
        }

    def get_context_window_summary(self, token_count: int) -> List[Dict]:
        """Get context window summary information for display"""
        context_analysis = self.analyze_context_windows(token_count)
        summary = []

        for model_name, info in context_analysis.items():
            summary.append({
                'model': model_name,
                'percentage': info['percentage'],
                'token_count': info['token_count'],
                'limit': info['limit'],
                'exceeded': info['exceeded']
            })

        return summary

    def get_project_statistics(self, file_analyses: List[Dict]) -> Dict:
        """Calculate complete project statistics"""
        if not file_analyses:
            return {}

        total_files = len(file_analyses)
        total_tokens = sum(info['token_count'] for info in file_analyses)
        total_size = sum(info['file_size'] for info in file_analyses)
        total_lines = sum(info['line_count'] for info in file_analyses)
        total_non_empty_lines = sum(info['non_empty_line_count'] for info in file_analyses)

        # Calculate empty line percentage
        empty_lines = total_lines - total_non_empty_lines
        empty_line_percentage = (empty_lines / total_lines * 100) if total_lines > 0 else 0

        # Calculate small lines percentage
        total_small_lines = sum(info.get('small_lines_count', 0) for info in file_analyses)
        small_lines_percentage = (total_small_lines / total_non_empty_lines * 100) if total_non_empty_lines > 0 else 0

        # Calculate average file size
        avg_file_size = total_size / total_files if total_files > 0 else 0
        avg_tokens_per_file = total_tokens / total_files if total_files > 0 else 0

        return {
            'total_files': total_files,
            'total_tokens': total_tokens,
            'total_size': total_size,
            'total_lines': total_lines,
            'total_non_empty_lines': total_non_empty_lines,
            'empty_lines': empty_lines,
            'empty_line_percentage': empty_line_percentage,
            'total_small_lines': total_small_lines,
            'small_lines_percentage': small_lines_percentage,
            'avg_file_size': avg_file_size,
            'avg_tokens_per_file': avg_tokens_per_file
        }