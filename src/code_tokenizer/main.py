#!/usr/bin/env python3
"""
Code Tokenizer - CLI tool for counting AI model tokens in code projects
"""

import click
import json
import csv
from datetime import datetime
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn

from code_tokenizer.code_collector import CodeCollector, CodeAnalyzer
from code_tokenizer.core import FileAnalyzer
from code_tokenizer.constants import DEFAULT_EXCLUDE_PATTERNS
from code_tokenizer.utils import format_tokens, format_bytes
from code_tokenizer.table_width_manager import TableWidthManager

console = Console()
width_manager = TableWidthManager(console)

@click.command()
@click.version_option(version="1.0.0")
@click.option('--package', '-p', metavar='[filename.txt]', help='Package code into single file for AI analysis')
@click.option('--max-show', '-m', default=10, help='Show top N largest files (default 10)')
@click.option('--exclude', '-e', multiple=True, metavar='[pattern]', help='Exclude files/folders (wildcards supported)')
@click.option('--include', '-i', multiple=True, metavar='[pattern]', help='Force include specific files')
@click.option('--save-csv', '-s', metavar='[filename.csv]', help='Save as CSV format')
@click.option('--json-save', metavar='[filename.json]', help='Save as JSON format')
@click.option('--json', 'output_json', is_flag=True, help='Output pure JSON data')
@click.argument('project_path', type=click.Path(exists=True, path_type=Path), required=False)
def cli(project_path: Optional[Path], max_show: int, package: Optional[str],
        save_csv: Optional[str], json_save: Optional[str], output_json: bool,
        exclude: tuple, include: tuple):
    """AI project token statistics tool - Quickly analyze AI model token usage in codebase"""

    # Use current directory as default
    if project_path is None:
        project_path = Path('.')

    # If package parameter is specified, execute packaging functionality
    if package:
        run_package_command(project_path, package, exclude, include)
        return

    # Execute analysis functionality
    file_token_info = run_analysis(project_path, max_show, output_json, exclude, include)

    # If there are analysis results and save options are specified, execute save
    if file_token_info:
        if save_csv:
            save_to_csv(file_token_info, save_csv, project_path)
        if json_save:
            save_to_json(file_token_info, json_save, project_path)


def run_analysis(project_path: Path, max_files: int, output_json: bool = False,
                 exclude: tuple = (), include: tuple = ()):
    """Run analysis functionality and return analysis results"""
    collector = CodeCollector()
    analyzer = CodeAnalyzer()

    if not output_json:
        console.print(f"[bold blue]🔍 Analyzing project: {project_path.resolve()}[/bold blue]")
        console.print()

    try:
        # Build exclusion pattern list: default exclusions + user custom exclusions
        exclude_patterns = list(DEFAULT_EXCLUDE_PATTERNS) + list(exclude)

        # Show file filtering rules (only show when analyzing directory)
        if not output_json and not project_path.is_file():
            console.print("[bold yellow]🔍 File Filtering Rules[/bold yellow]\n")

            # Use adaptive table width manager to create rules table
            rules_table = width_manager.create_adaptive_table(
                headers=["Rule Type", "Rule Content"],
                table_type='rules',
                column_ratios=width_manager.get_default_column_ratios('rules'),
                min_column_widths=width_manager.get_default_min_widths('rules')
            )

            # Set column styles
            rules_table.columns[0].style = "cyan"
            rules_table.columns[1].style = "black"

            # Show default analysis rules
            default_file_patterns = collector.get_default_file_patterns()
            rules_table.add_row("Default Analysis", ", ".join(default_file_patterns))

            # Show default exclusion rules
            rules_table.add_row("Default Excluded", ", ".join(DEFAULT_EXCLUDE_PATTERNS))

            # Show user custom exclusion rules
            if exclude:
                rules_table.add_row("User Excluded", ", ".join(exclude))

            # Show user custom inclusion rules
            if include:
                rules_table.add_row("User Included", ", ".join(include))

            console.print(rules_table)
            console.print()
            console.print("[cyan]Scanning project files...[/cyan]")

        # Detect path type and handle accordingly
        if project_path.is_file():
            # Single file processing
            files = [project_path]
        else:
            # Directory scanning processing
            files = collector.scan_files(project_path, exclude_patterns=exclude_patterns, include_patterns=list(include))
            # Filter out previously collected files
            files = [f for f in files if not f.name.startswith('code_collected_')]

        if not files:
            if output_json:
                print(json.dumps({"error": "No files found"}, ensure_ascii=False))
            else:
                console.print("[red]❌ No files found[/red]")
            return None

        if not output_json:
            if project_path.is_file():
                console.print(f"[green]✓[/green] Analyzing file: {project_path.name}")
            else:
                console.print(f"[green]✓[/green] Found {len(files)} files")
            console.print()

        # Analyze token count for each file
        file_token_info = []
        file_analyses = []  # Store detailed analysis information

        if not json:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                console=console
            ) as progress:

                task = progress.add_task("[cyan]Analyzing file tokens...", total=len(files))

                for file_path in files:
                    progress.update(task, advance=1, description=f"[cyan]Analyzing: {file_path.name}[/cyan]\n")

                    try:
                        file_stats = analyzer.analyze_file(file_path)
                        # For single file, use filename; for directory, use relative path
                        if project_path.is_file():
                            relative_path = file_path.name
                        else:
                            relative_path = file_path.relative_to(project_path)

                        file_token_info.append({
                            'path': str(relative_path),
                            'file_path': str(file_path),
                            'token_count': file_stats['token_count'],
                            'file_size': file_stats['file_size']
                        })

                        # Save detailed analysis information
                        file_analyses.append(file_stats)
                    except Exception:
                        continue
        else:
            # JSON output mode, no progress bar
            for file_path in files:
                try:
                    file_stats = analyzer.analyze_file(file_path)
                    # For single file, use filename; for directory, use relative path
                    if project_path.is_file():
                        relative_path = file_path.name
                    else:
                        relative_path = file_path.relative_to(project_path)

                    file_token_info.append({
                        'path': str(relative_path),
                        'file_path': str(file_path),
                        'token_count': file_stats['token_count'],
                        'file_size': file_stats['file_size']
                    })

                    # Save detailed analysis information
                    file_analyses.append(file_stats)
                except Exception:
                    continue

        # Sort by token count
        file_token_info.sort(key=lambda x: x['token_count'], reverse=True)

        # Calculate basic statistics
        total_tokens = sum(info['token_count'] for info in file_token_info)
        total_size = sum(info['file_size'] for info in file_token_info)

        # Calculate detailed statistics
        file_analyzer = FileAnalyzer()
        project_stats = file_analyzer.get_project_statistics(file_analyses)

        # If it's JSON output mode, output JSON and return
        if output_json:
            result = {
                'project_path': str(project_path.resolve()),
                'total_files': len(files),
                'total_tokens': total_tokens,
                'total_size': total_size,
                'files': file_token_info
            }
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            # Display rich content
            display_files = file_token_info[:max_files]

            if project_path.is_file():
                # Single file analysis, no list title displayed
                console.print()
            else:
                console.print(f"[bold]📊 Project File List (sorted by token size, showing top {len(display_files)})[/bold]")
                console.print()

            # Use adaptive table width manager to create file list table
            table = width_manager.create_adaptive_table(
                headers=["Rank", "File Path", "File Size", "Token Count"],
                table_type='files',
                column_ratios=width_manager.get_default_column_ratios('files'),
                min_column_widths=width_manager.get_default_min_widths('files')
            )

            # Set column styles and alignment
            table.columns[0].style = "cyan"
            table.columns[0].justify = "left"
            table.columns[1].style = "blue"
            table.columns[1].overflow = "fold"
            table.columns[2].style = "yellow"
            table.columns[2].justify = "right"
            table.columns[3].style = "green"
            table.columns[3].justify = "right"

            for i, info in enumerate(display_files, 1):
                # Use core module to format file size
                file_analyzer = FileAnalyzer()
                size_str = format_bytes(info['file_size'])

                table.add_row(
                    str(i),
                    str(info['path']),
                    size_str,
                    format_tokens(info['token_count'])
                )

            # Check if all files should be displayed
            if len(files) > max_files:
                # Only show some files, separate with ...
                table.add_row("...", "...", "...", "...")

            console.print(table)
            console.print()

            # Display context window usage - use core module
            console.print("[bold blue]🎯 Context Window Usage[/bold blue]\n")

            file_analyzer = FileAnalyzer()
            context_summary = file_analyzer.get_context_window_summary(total_tokens)

            # Use adaptive table width manager to create context window table
            context_table = width_manager.create_adaptive_table(
                headers=["Model", "Usage Ratio", "Progress Bar", "Token Count", "Status"],
                table_type='context',
                column_ratios=width_manager.get_default_column_ratios('context'),
                min_column_widths=width_manager.get_default_min_widths('context')
            )

            # Set column styles and alignment
            context_table.columns[0].style = "cyan"
            context_table.columns[1].justify = "right"
            context_table.columns[2].justify = "center"
            context_table.columns[3].justify = "right"
            context_table.columns[4].style = "bold"
            context_table.columns[4].justify = "right"

            for item in context_summary:
                if item['exceeded']:
                    status = "[red]⚠️ Exceeded[/red]"
                else:
                    status = "[green]✓ Available[/green]"

                percentage_str = f"{item['percentage']:.1f}%"

                # Create progress bar (mirror display, usage ratio on the right)
                if item['percentage'] >= 100:
                    bar_percentage = 100  # Limit max display to 100%
                else:
                    bar_percentage = item['percentage']

                # Mirror progress bar display, empty on left, filled on right
                bar_width = 20
                filled_length = int(bar_width * bar_percentage / 100)
                if filled_length > bar_width:
                    filled_length = bar_width

                # Use more aesthetic characters
                empty_chars = "░"
                filled_chars = "█"

                # Choose color based on status
                if item['exceeded']:
                    # Use red when exceeded
                    progress_bar = f"[red]{empty_chars * (bar_width - filled_length)}{filled_chars * filled_length}[/red]"
                else:
                    # Use green when normal
                    progress_bar = f"[green]{empty_chars * (bar_width - filled_length)}{filled_chars * filled_length}[/green]"

                context_table.add_row(
                    item['model'],
                    percentage_str,
                    progress_bar,
                    f"{format_tokens(item['token_count'])}/{format_tokens(item['limit'])}",
                    status
                )

            console.print(context_table)
            console.print()

            # Display project comprehensive statistics
            if project_stats:
                if project_path.is_file():
                    # Single file analysis, simplified statistics
                    console.print("[bold magenta]📈 File Statistics[/bold magenta]")

                    # Use adaptive table width manager to create single file statistics table
                    stats_table = width_manager.create_adaptive_table(
                        headers=["Stat Item", "Value", "Stat Item", "Value"],
                        table_type='stats',
                        column_ratios=width_manager.get_default_column_ratios('stats'),
                        min_column_widths=width_manager.get_default_min_widths('stats')
                    )

                    # Set column styles and alignment
                    stats_table.columns[0].style = "cyan"
                    stats_table.columns[1].justify = "right"
                    stats_table.columns[2].style = "cyan"
                    stats_table.columns[3].justify = "right"

                    # Single file arranged in 2 rows 4 columns
                    stats_data = [
                        ("Total Tokens", f"[bold bright_green]✓ {format_tokens(project_stats['total_tokens'])}[/bold bright_green]",
                         "File Size", format_bytes(project_stats['total_size'])),
                        ("Total Lines", f"{project_stats['total_lines']:,}",
                         "Empty Line Ratio", f"{project_stats['empty_line_percentage']:.1f}%")
                    ]

                    for item1, value1, item2, value2 in stats_data:
                        if item2:  # If second column has data
                            stats_table.add_row(item1, value1, item2, value2)
                        else:  # Last row only has data in first column
                            stats_table.add_row(item1, value1, "", "")

                else:
                    # Directory analysis, complete statistics
                    console.print("[bold magenta]📈 Project Comprehensive Statistics[/bold magenta]\n")

                    # Use adaptive table width manager to create directory statistics table
                    stats_table = width_manager.create_adaptive_table(
                        headers=["Stat Item", "Value", "Stat Item", "Value"],
                        table_type='stats',
                        column_ratios=width_manager.get_default_column_ratios('stats'),
                        min_column_widths=width_manager.get_default_min_widths('stats')
                    )

                    # Set column styles and alignment
                    stats_table.columns[0].style = "cyan"
                    stats_table.columns[1].justify = "right"
                    stats_table.columns[2].style = "cyan"
                    stats_table.columns[3].justify = "right"

                    # Add statistical data, arranged in two columns, highlight total tokens, put total tokens and file count on the last line
                    stats_data = [
                        ("Total File Size", format_bytes(project_stats['total_size']), "Total Lines", f"{project_stats['total_lines']:,}"),
                        ("Average File Size", format_bytes(project_stats['avg_file_size']), "Avg Tokens per File", format_tokens(project_stats['avg_tokens_per_file'])),
                        ("Empty Line Ratio", f"{project_stats['empty_line_percentage']:.1f}%", "Lines < 3 Chars", f"{project_stats.get('small_lines_percentage', 0):.1f}%"),
                        ("Total Files", f"{project_stats['total_files']:,} files", "Total Tokens", f"[bold bright_green]✓ {format_tokens(project_stats['total_tokens'])}[/bold bright_green]")
                    ]

                    for item1, value1, item2, value2 in stats_data:
                        if item2:  # If second column has data
                            stats_table.add_row(item1, value1, item2, value2)
                        else:  # Last row only has data in first column
                            stats_table.add_row(item1, value1, "", "")

                console.print(stats_table)
                console.print()

        return file_token_info

    except Exception as e:
        if output_json:
            print(json.dumps({"error": f"Error during analysis: {str(e)}"}, ensure_ascii=False))
        else:
            console.print(f"[red]❌[/red] Error during analysis: {str(e)}")
            raise click.Abort()


def run_package_command(project_path: Path, output: Optional[str], exclude: tuple = (), include: tuple = ()):
    """Execute packaging functionality"""
    collector = CodeCollector()
    analyzer = CodeAnalyzer()

    # Build exclusion pattern list: default exclusions + user custom exclusions
    exclude_patterns = list(DEFAULT_EXCLUDE_PATTERNS) + list(exclude)

    # First scan files to get statistical information
    files = collector.scan_files(str(project_path), exclude_patterns=exclude_patterns, include_patterns=list(include))

    if not files:
        console.print("[red]❌[/red] No files found")
        return

    # Calculate total size and token count
    total_size = sum(f.stat().st_size for f in files if f.exists())
    total_tokens = 0

    console.print("[cyan]📊[/cyan] Calculating token count...")
    for file_path in files:
        try:
            stats = analyzer.analyze_file(file_path)
            total_tokens += stats['token_count']
        except:
            continue

    # Execute collection
    output_file = collector.collect_code_custom_format(
        str(project_path),
        output,
        file_patterns=None,
        exclude_patterns=exclude_patterns,
        include_patterns=list(include),
        use_cache=False
    )

    # Display statistical information
    console.print(f"[green]✓[/green] Code collection completed: {output_file}")
    console.print(f"[blue]📊[/blue] Processed {len(files)} files in total")
    console.print(f"[yellow]💾[/yellow] Total file size: {format_bytes(total_size)}")
    console.print(f"[cyan]🎯[/cyan] Estimated token count: {format_tokens(total_tokens)}")

    # Display generated file information
    try:
        output_path = Path(output_file)
        if output_path.exists():
            output_size = output_path.stat().st_size
            # Calculate line count of generated file
            with open(output_path, 'r', encoding='utf-8') as f:
                content = f.read()
                output_lines = content.count('\n')

            console.print(f"[magenta]📄[/magenta] Generated file size: {format_bytes(output_size)}")
            console.print(f"[magenta]📝[/magenta] Generated file line count: {output_lines:,}")
    except Exception as e:
        console.print(f"[red]⚠️[/red] Unable to read generated file information: {str(e)}")


def save_to_csv(file_token_info, filename: str, project_path: Path):
    """Save analysis results to CSV file"""
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['rank', 'path', 'token_count', 'file_size']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for i, info in enumerate(file_token_info, 1):
            writer.writerow({
                'rank': i,
                'path': info['path'],
                'token_count': info['token_count'],
                'file_size': info['file_size']
            })

    console.print(f"[green]✓[/green] CSV file saved: {filename}")


def save_to_json(file_token_info, filename: str, project_path: Path):
    """Save analysis results to JSON file"""
    total_tokens = sum(info['token_count'] for info in file_token_info)
    total_size = sum(info['file_size'] for info in file_token_info)

    result = {
        'project_path': str(project_path.resolve()),
        'analysis_time': datetime.now().isoformat(),
        'total_files': len(file_token_info),
        'total_tokens': total_tokens,
        'total_size': total_size,
        'files': file_token_info
    }

    with open(filename, 'w', encoding='utf-8') as jsonfile:
        json.dump(result, jsonfile, ensure_ascii=False, indent=2)

    console.print(f"[green]✓[/green] JSON file saved: {filename}")

if __name__ == '__main__':
    cli()
