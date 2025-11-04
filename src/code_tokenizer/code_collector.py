#!/usr/bin/env python3
"""
Code Collection and Analysis Tool
Supports project code scanning, cache management, statistical analysis and other functions
"""

import os
import json
import hashlib
import fnmatch
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Set
import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from .core import FileAnalyzer
from .constants import DEFAULT_EXCLUDE_PATTERNS, DEFAULT_FILE_PATTERNS
from .utils import format_tokens, format_bytes
from .table_width_manager import TableWidthManager

console = Console()

class CodeCollector:
    """Code Collector"""

    def __init__(self, cache_dir: str = ".code_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.cache_index_file = self.cache_dir / "cache_index.json"
        self.cache_index = self._load_cache_index()
        self.width_manager = TableWidthManager(console)

    def _load_cache_index(self) -> Dict:
        """Load cache index"""
        if self.cache_index_file.exists():
            try:
                with open(self.cache_index_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return {}
        return {}

    def _save_cache_index(self):
        """Save cache index"""
        with open(self.cache_index_file, 'w', encoding='utf-8') as f:
            json.dump(self.cache_index, f, ensure_ascii=False, indent=2)

    def _get_file_hash(self, file_path: Path) -> str:
        """Calculate file hash value"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except (IOError, OSError):
            return ""

    def _get_project_hash(self, project_path: Path, file_patterns: List[str],
                         exclude_patterns: List[str]) -> str:
        """Calculate project hash value"""
        hash_source = f"{project_path}_{sorted(file_patterns)}_{sorted(exclude_patterns)}"
        return hashlib.md5(hash_source.encode()).hexdigest()[:16]

    def scan_files(self, project_path: str, file_patterns: List[str] = None,
                  exclude_patterns: List[str] = None, include_patterns: List[str] = None) -> List[Path]:
        """Scan project files"""
        if file_patterns is None:
            file_patterns = DEFAULT_FILE_PATTERNS

        if exclude_patterns is None:
            exclude_patterns = DEFAULT_EXCLUDE_PATTERNS

        if include_patterns is None:
            include_patterns = []

        project_path = Path(project_path)
        files = []
        processed_files = set()

        # First process files in include_patterns (highest priority)
        if include_patterns:
            for include_pattern in include_patterns:
                for file_path in project_path.rglob(include_pattern):
                    # Exclude directories
                    if file_path.is_dir():
                        continue

                    # Avoid duplicate processing
                    if file_path in processed_files:
                        continue

                    processed_files.add(file_path)

                    # For included files, only check exact matches to avoid hidden files being incorrectly excluded
                    should_exclude = False
                    for exclude_pattern in exclude_patterns:
                        # For included files, use stricter matching method
                        if (fnmatch.fnmatch(str(file_path), exclude_pattern) or
                            fnmatch.fnmatch(file_path.name, exclude_pattern)):
                            should_exclude = True
                            break

                    if not should_exclude:
                        files.append(file_path)

        # Then process default file patterns
        for pattern in file_patterns:
            for file_path in project_path.rglob(pattern):
                # Exclude directories
                if file_path.is_dir():
                    continue

                # Avoid duplicate processing
                if file_path in processed_files:
                    continue

                processed_files.add(file_path)

                # Check for hidden files (filename starts with dot)
                if file_path.name.startswith('.'):
                    continue

                # Check exclusion patterns (using wildcard matching and substring matching)
                should_exclude = False
                for exclude_pattern in exclude_patterns:
                    # Try multiple matching methods
                    if (fnmatch.fnmatch(str(file_path), exclude_pattern) or
                        fnmatch.fnmatch(file_path.name, exclude_pattern) or
                        fnmatch.fnmatch(str(file_path), f"*{exclude_pattern}*") or
                        exclude_pattern in str(file_path) or
                        exclude_pattern in file_path.name):
                        should_exclude = True
                        break

                if not should_exclude:
                    files.append(file_path)

        # Remove duplicates and sort
        files = sorted(list(set(files)))
        return files

    def get_default_file_patterns(self) -> List[str]:
        """Get default file pattern list"""
        return DEFAULT_FILE_PATTERNS

    def _write_files_to_file(self, files: List[Path], output_file: str, project_path: Path):
        """Write file contents to file (internal method)"""
        with open(output_file, 'w', encoding='utf-8') as f:
            # Write header information
            f.write(f"# Code Collection Report\n")
            f.write(f"# Project Path: {project_path}\n")
            f.write(f"# Collection Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"# File Count: {len(files)}\n")
            f.write("#" + "="*80 + "\n\n")

            for i, file_path in enumerate(files, 1):
                try:
                    relative_path = file_path.relative_to(project_path)

                    f.write(f"--- [{i:03d}] - [{relative_path}] ---\n")
                    f.write(f"File Size: {file_path.stat().st_size} bytes\n")
                    f.write(f"Modified Time: {datetime.fromtimestamp(file_path.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write("\n")

                    # Read file content
                    try:
                        with open(file_path, 'r', encoding='utf-8') as src:
                            content = src.read()
                            f.write(content)
                    except UnicodeDecodeError:
                        # Try other encodings
                        try:
                            with open(file_path, 'r', encoding='gbk') as src:
                                content = src.read()
                                f.write(content)
                                f.write("\n\n[Note: Read using GBK encoding]\n\n")
                        except UnicodeDecodeError:
                            f.write("\n\n[Note: File contains binary content, cannot be displayed]\n\n")

                    f.write("\n" + "-"*80 + "\n\n")

                except Exception as e:
                    f.write(f"\n\n[Error: Unable to read file - {str(e)}]\n\n")
                    f.write("-"*80 + "\n\n")

    def _write_files_to_custom_format(self, files: List[Path], output_file: str, project_path: Path):
        """Write file contents to file (custom format)"""
        with open(output_file, 'w', encoding='utf-8') as f:
            # Write header information
            f.write(f"# Code Collection Report\n")
            f.write(f"# Project Path: {project_path}\n")
            f.write(f"# Collection Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"# File Count: {len(files)}\n")
            f.write("#" + "="*80 + "\n\n")

            for i, file_path in enumerate(files, 1):
                try:
                    relative_path = file_path.relative_to(project_path)

                    # Calculate file line count
                    try:
                        with open(file_path, 'r', encoding='utf-8') as src:
                            content = src.read()
                            # Count newline characters to match wc -l
                            line_count = content.count('\n')
                    except UnicodeDecodeError:
                        try:
                            with open(file_path, 'r', encoding='gbk') as src:
                                content = src.read()
                                # Count newline characters to match wc -l
                                line_count = content.count('\n')
                        except UnicodeDecodeError:
                            content = ""
                            line_count = 0

                    # Use required format
                    f.write(f"####### [idx:{i}] - [path:{relative_path}] - [rows:{line_count}] #######\n")

                    # Write file content
                    if content:
                        f.write(content)
                        # Ensure file content ends with newline
                        if not content.endswith('\n'):
                            f.write('\n')
                    else:
                        f.write("[File content is empty or cannot be read]\n")

                    f.write("\n\n")

                except Exception as e:
                    f.write(f"####### [{i}] - [{file_path.relative_to(project_path)}] - [ERROR] #######\n")
                    f.write(f"[Error: Unable to read file - {str(e)}]\n\n")

    def collect_code(self, project_path: str, output_file: str = None,
                    file_patterns: List[str] = None,
                    exclude_patterns: List[str] = None,
                    use_cache: bool = True) -> str:
        """Collect code to file"""
        project_path = Path(project_path).resolve()

        if output_file is None:
            output_file = f"code_collected_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

        # Generate project cache key
        project_hash = self._get_project_hash(project_path, file_patterns or [],
                                            exclude_patterns or [])
        cache_key = f"{project_path.name}_{project_hash}"

        # Check cache
        if use_cache and cache_key in self.cache_index:
            cache_file = self.cache_dir / self.cache_index[cache_key]["file"]
            if cache_file.exists():
                console.print(f"[green]✓[/green] Using cache file: {cache_file}")
                # Copy cache file to target location
                with open(cache_file, 'r', encoding='utf-8') as src, \
                     open(output_file, 'w', encoding='utf-8') as dst:
                    dst.write(src.read())
                return output_file

        # Scan files
        console.print("[blue]🔍[/blue] Scanning project files...")
        files = self.scan_files(project_path, file_patterns, exclude_patterns)

        if not files:
            console.print("[red]❌[/red] No files found")
            return output_file

        # Collect code
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console
        ) as progress:

            task = progress.add_task("[cyan]Collecting code files...", total=len(files))

            with open(output_file, 'w', encoding='utf-8') as f:
                # Write header information
                f.write(f"# Code Collection Report\n")
                f.write(f"# Project Path: {project_path}\n")
                f.write(f"# Collection Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"# File Count: {len(files)}\n")
                f.write(f"# File Patterns: {', '.join(file_patterns or ['Default'])}\n")
                f.write(f"# Exclude Patterns: {', '.join(exclude_patterns or ['Default'])}\n")
                f.write("#" + "="*80 + "\n\n")

                for i, file_path in enumerate(files, 1):
                    progress.update(task, advance=1, description=f"[cyan]Processing: {file_path.name}")

                    try:
                        relative_path = file_path.relative_to(project_path)

                        f.write(f"--- [{i:03d}] - [{relative_path}] ---\n")
                        f.write(f"File Size: {file_path.stat().st_size} bytes\n")
                        f.write(f"Modified Time: {datetime.fromtimestamp(file_path.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')}\n")
                        f.write("\n")

                        # Read file content
                        try:
                            with open(file_path, 'r', encoding='utf-8') as src:
                                content = src.read()
                                f.write(content)
                        except UnicodeDecodeError:
                            # Try other encodings
                            try:
                                with open(file_path, 'r', encoding='gbk') as src:
                                    content = src.read()
                                    f.write(content)
                                    f.write("\n\n[Note: Read using GBK encoding]\n\n")
                            except UnicodeDecodeError:
                                f.write("\n\n[Note: File contains binary content, cannot be displayed]\n\n")

                        f.write("\n" + "-"*80 + "\n\n")

                    except Exception as e:
                        f.write(f"\n\n[Error: Unable to read file - {str(e)}]\n\n")
                        f.write("-"*80 + "\n\n")

        # Save to cache
        if use_cache:
            cache_file_name = f"cache_{project_hash}.txt"
            cache_file = self.cache_dir / cache_file_name

            # Copy to cache directory
            with open(output_file, 'r', encoding='utf-8') as src, \
                 open(cache_file, 'w', encoding='utf-8') as dst:
                dst.write(src.read())

            # Update cache index
            self.cache_index[cache_key] = {
                "file": cache_file_name,
                "project_path": str(project_path),
                "created_at": datetime.now().isoformat(),
                "file_count": len(files),
                "file_patterns": file_patterns,
                "exclude_patterns": exclude_patterns
            }
            self._save_cache_index()

            console.print(f"[green]✓[/green] Saved to cache: {cache_file}")

        console.print(f"[green]✓[/green] Code collection completed: {output_file}")
        console.print(f"[blue]📊[/blue] Processed {len(files)} files")

        return output_file

    def collect_code_custom_format(self, project_path: str, output_file: str = None,
                                 file_patterns: List[str] = None,
                                 exclude_patterns: List[str] = None,
                                 include_patterns: List[str] = None,
                                 use_cache: bool = False) -> str:
        """Collect code to file (custom format)"""
        project_path = Path(project_path).resolve()

        if output_file is None:
            output_file = f"code_collected_custom_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

        # Scan files
        files = self.scan_files(project_path, file_patterns, exclude_patterns, include_patterns)

        if not files:
            console.print("[red]❌[/red] No files found")
            return output_file

        # Collect code
        console.print("[blue]📝[/blue] Collecting code files...")
        # Write using custom format
        self._write_files_to_custom_format(files, output_file, project_path)

        return output_file

    def clear_cache(self, project_name: str = None):
        """Clear cache"""
        if project_name:
            # Clear cache for specific project
            keys_to_remove = [k for k in self.cache_index.keys() if project_name in k]
            for key in keys_to_remove:
                cache_file = self.cache_dir / self.cache_index[key]["file"]
                if cache_file.exists():
                    cache_file.unlink()
                del self.cache_index[key]
            console.print(f"[green]✓[/green] Cleared cache for project '{project_name}'")
        else:
            # Clear all cache
            for cache_file in self.cache_dir.glob("cache_*.txt"):
                cache_file.unlink()
            self.cache_index.clear()
            console.print("[green]✓[/green] Cleared all cache")

        self._save_cache_index()

    def list_cache(self):
        """List cache"""
        if not self.cache_index:
            console.print("[yellow]📭[/yellow] No cache available")
            return

        # Create cache list table using adaptive table width manager
        table = self.width_manager.create_adaptive_table(
            headers=["Project", "File Count", "Created Time", "Project Path"],
            table_type='cache',
            column_ratios=self.width_manager.get_default_column_ratios('cache'),
            min_column_widths=self.width_manager.get_default_min_widths('cache'),
            title="Cache List"
        )

        # Set column styles and alignment
        table.columns[0].style = "cyan"
        table.columns[1].justify = "right"
        table.columns[2].style = "green"
        table.columns[3].style = "blue"
        table.columns[3].overflow = "fold"

        for key, info in self.cache_index.items():
            project_name = key.split('_')[0]
            created_at = datetime.fromisoformat(info["created_at"]).strftime('%Y-%m-%d %H:%M')
            table.add_row(
                project_name,
                str(info["file_count"]),
                created_at,
                info["project_path"][:50] + "..." if len(info["project_path"]) > 50 else info["project_path"]
            )

        console.print(table)


class CodeAnalyzer:
    """Code Analyzer - Uses core module to provide analysis functionality"""

    def __init__(self):
        self.file_analyzer = FileAnalyzer()
        self.width_manager = TableWidthManager(console)

    def analyze_file(self, file_path: str) -> Dict:
        """Analyze file statistics"""
        return self.file_analyzer.analyze_file(file_path)

    def format_bytes(self, bytes_value: int) -> str:
        """Format bytes"""
        return format_bytes(bytes_value)

    def print_analysis(self, file_path: str, stats: Dict):
        """Print analysis results"""
        console.print(Panel(
            f"[bold blue]📊 File Analysis Report[/bold blue]\n\n"
            f"File Path: {file_path}\n"
            f"File Size: {self.format_bytes(stats['file_size'])}\n"
            f"Total Lines: {stats['line_count']:,}\n"
            f"Non-empty Lines: {stats['non_empty_line_count']:,}\n"
            f"Character Count: {stats['char_count']:,}\n"
            f"Word Count: {stats['word_count']:,}\n"
            f"Token Count (GPT-3.5): {format_tokens(stats['token_count'])}\n"
            f"Token Count (GPT-4): {format_tokens(stats['token_count_gpt4'])}\n"
            f"Average Tokens per Line: {stats['avg_tokens_per_line']:.2f}",
            title="Analysis Results"
        ))

        # Use core module's context window analysis
        context_summary = self.file_analyzer.get_context_window_summary(stats['token_count'])

        # Create context window table using adaptive table width manager
        table = self.width_manager.create_adaptive_table(
            headers=["Model", "Usage Ratio", "Token Count", "Status"],
            table_type='analysis',
            column_ratios=self.width_manager.get_default_column_ratios('analysis'),
            min_column_widths=self.width_manager.get_default_min_widths('analysis'),
            title="Context Window Usage"
        )

        # Set column styles and alignment
        table.columns[0].style = "cyan"
        table.columns[1].justify = "right"
        table.columns[2].justify = "right"
        table.columns[3].style = "bold"
        table.columns[3].justify = "right"

        for item in context_summary:
            if item['exceeded']:
                status = "[red]⚠️ Exceeded[/red]"
            else:
                status = "[green]✓ Available[/green]"

            percentage_str = f"{item['percentage']:.1f}%"

            table.add_row(
                item['model'],
                percentage_str,
                f"{format_tokens(item['token_count'])}/{format_tokens(item['limit'])}",
                status
            )

        console.print(table)