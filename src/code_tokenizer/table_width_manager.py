#!/usr/bin/env python3
"""
Table Width Manager
Provides table display functionality with adaptive terminal window width
"""

import os
import shutil
from typing import List, Optional
from rich.table import Table
from rich.console import Console


class TableWidthManager:
    """Table width manager supporting adaptive terminal width"""

    def __init__(self,
                 console: Optional[Console] = None,
                 min_width: int = 80,
                 max_width: Optional[int] = None,
                 margin_ratio: float = 0.9):
        """
        Initialize the table width manager

        Args:
            console: Rich Console instance, creates new instance if None
            min_width: Minimum table width
            max_width: Maximum table width, None means no limit
            margin_ratio: Margin ratio, actual width = terminal width * margin_ratio
        """
        self.console = console or Console()
        self.min_width = min_width
        self.max_width = max_width
        self.margin_ratio = margin_ratio

    def get_terminal_width(self) -> int:
        """
        Get terminal width

        Returns:
            Terminal width, returns default value if failed to get width
        """
        try:
            # First try to get from console
            width = self.console.width
            if width > 0:
                return width
        except (AttributeError, OSError):
            pass

        try:
            # Try to get using shutil
            width = shutil.get_terminal_size().columns
            if width > 0:
                return width
        except (OSError, AttributeError):
            pass

        try:
            # Try to get using os
            width = os.get_terminal_size().columns
            if width > 0:
                return width
        except (OSError, AttributeError):
            pass

        # All methods failed, return default value
        return 80

    def calculate_available_width(self) -> int:
        """
        Calculate available table width

        Returns:
            Available width with margin ratio and max/min limits applied
        """
        terminal_width = self.get_terminal_width()
        available_width = int(terminal_width * self.margin_ratio)

        # Apply maximum width limit
        if self.max_width is not None:
            available_width = min(available_width, self.max_width)

        # Apply minimum width limit
        available_width = max(available_width, self.min_width)

        return available_width

    def calculate_column_widths(self,
                               column_ratios: List[float],
                               fixed_widths: Optional[List[int]] = None,
                               min_column_widths: Optional[List[int]] = None) -> List[int]:
        """
        Calculate column widths by ratio

        Args:
            column_ratios: Width ratio list for each column
            fixed_widths: Width list for fixed-width columns, None means no fixed-width columns
            min_column_widths: Minimum width list for each column, None means use default minimum width

        Returns:
            Actual width list for each column
        """
        if fixed_widths is None:
            fixed_widths = []

        if min_column_widths is None:
            min_column_widths = [8] * len(column_ratios)  # Default minimum width 8 characters

        available_width = self.calculate_available_width()

        # Calculate total fixed width
        total_fixed_width = sum(fixed_widths)

        # Calculate distributable width
        distributable_width = available_width - total_fixed_width

        # If distributable width <= 0, use minimum width
        if distributable_width <= 0:
            return min_column_widths

        # Calculate total ratio
        total_ratio = sum(column_ratios)
        if total_ratio <= 0:
            return min_column_widths

        # Distribute width by ratio
        column_widths = []
        for i, ratio in enumerate(column_ratios):
            if i < len(fixed_widths) and fixed_widths[i] > 0:
                # Fixed width column
                width = fixed_widths[i]
            else:
                # Ratio width column
                width = int(distributable_width * (ratio / total_ratio))

            # Ensure not less than minimum width
            min_width = min_column_widths[i] if i < len(min_column_widths) else 8
            width = max(width, min_width)

            column_widths.append(width)

        # Adjust total to match available width (due to rounding errors)
        total_calculated = sum(column_widths)
        if total_calculated != available_width:
            # Find the widest column for adjustment
            max_index = column_widths.index(max(column_widths))
            column_widths[max_index] += available_width - total_calculated

        return column_widths

    def create_adaptive_table(self,
                            headers: List[str],
                            table_type: Optional[str] = None,
                            column_ratios: Optional[List[float]] = None,
                            fixed_widths: Optional[List[int]] = None,
                            min_column_widths: Optional[List[int]] = None,
                            title: Optional[str] = None,
                            show_header: bool = True,
                            show_lines: Optional[bool] = None,
                            expand: bool = False,
                            **kwargs) -> Table:
        """
        Create adaptive table

        Args:
            headers: Header list
            table_type: Table type for getting preset style configuration
            column_ratios: Column width ratios, None means equal distribution
            fixed_widths: Fixed width column list
            min_column_widths: Minimum width list for each column
            title: Table title
            show_header: Whether to show header
            show_lines: Whether to show lines, None means use preset configuration
            expand: Whether to expand to available width
            **kwargs: Other parameters passed to Table

        Returns:
            Rich Table instance
        """
        # Get style configuration
        style_config = {}
        if table_type:
            style_config = self.get_table_style_config(table_type)

        # Determine show_lines value
        if show_lines is None:
            show_lines = style_config.get('show_lines', True)

        # Set beautiful table style
        from rich.box import ROUNDED, SIMPLE_HEAD

        # Select border style based on table type
        box_styles = {
            'rules': ROUNDED,
            'files': SIMPLE_HEAD,
            'context': SIMPLE_HEAD,
            'stats': ROUNDED,
            'cache': ROUNDED,
            'analysis': SIMPLE_HEAD
        }

        table = Table(
            title=title,
            show_header=show_header,
            show_lines=show_lines,
            expand=expand,
            box=box_styles.get(table_type, SIMPLE_HEAD),
            style=style_config.get('table_style', 'none'),
            header_style=style_config.get('header_style', 'bold white'),
            border_style=style_config.get('border_style', 'bright_black'),
            pad_edge=style_config.get('pad_edge', True),
            **kwargs
        )

        # If no ratios specified, distribute equally
        if column_ratios is None:
            column_ratios = [1.0] * len(headers)

        # Calculate column widths
        column_widths = self.calculate_column_widths(
            column_ratios, fixed_widths, min_column_widths
        )

        # Add columns
        for header, width in zip(headers, column_widths):
            table.add_column(header, width=width)

        return table

    def get_default_column_ratios(self, table_type: str) -> List[float]:
        """
        Get default column width ratio configuration

        Args:
            table_type: Table type ('rules', 'files', 'context', 'stats', 'cache')

        Returns:
            Column width ratio list
        """
        configs = {
            'rules': [0.2, 0.8],  # Rule type, Rule content
            'files': [0.08, 0.56, 0.18, 0.18],  # Rank, File path, File size, Token count
            'context': [0.2, 0.12, 0.3, 0.24, 0.14],  # Model, Usage ratio, Progress bar, Token count, Status
            'stats': [0.4, 0.18, 0.4, 0.18],  # Stat item 1, Value 1, Stat item 2, Value 2
            'cache': [0.14, 0.12, 0.18, 0.56],  # Project, File count, Creation time, Project path
            'analysis': [0.24, 0.16, 0.30, 0.30]  # Model, Usage ratio, Token count, Status
        }

        return configs.get(table_type, [1.0] * 4)  # Default 4 columns equal distribution

    def get_default_min_widths(self, table_type: str) -> List[int]:
        """
        Get default minimum column width configuration

        Args:
            table_type: Table type

        Returns:
            Minimum column width list
        """
        configs = {
            'rules': [12, 30],
            'files': [6, 30, 14, 14],
            'context': [16, 10, 22, 20, 8],
            'stats': [20, 14, 20, 14],
            'cache': [12, 8, 16, 25],
            'analysis': [18, 10, 16, 16]
        }

        return configs.get(table_type, [8] * 4)  # Default minimum width 8

    def get_table_style_config(self, table_type: str) -> dict:
        """
        Get table style configuration

        Args:
            table_type: Table type

        Returns:
            Style configuration dictionary
        """
        configs = {
            'rules': {
                'table_style': 'cyan',
                'header_style': 'bold cyan',
                'border_style': 'bright_black',
                'show_lines': True,
                'pad_edge': True
            },
            'files': {
                'table_style': 'none',
                'header_style': 'bold blue',
                'border_style': 'bright_black',
                'show_lines': False,
                'pad_edge': True
            },
            'context': {
                'table_style': 'none',
                'header_style': 'bold magenta',
                'border_style': 'bright_black',
                'show_lines': False,
                'pad_edge': True
            },
            'stats': {
                'table_style': 'none',
                'header_style': 'bold green',
                'border_style': 'bright_black',
                'show_lines': False,
                'pad_edge': True
            },
            'cache': {
                'table_style': 'cyan',
                'header_style': 'bold cyan',
                'border_style': 'bright_black',
                'show_lines': True,
                'pad_edge': True
            },
            'analysis': {
                'table_style': 'none',
                'header_style': 'bold yellow',
                'border_style': 'bright_black',
                'show_lines': True,
                'pad_edge': True
            }
        }

        return configs.get(table_type, {
            'table_style': 'none',
            'header_style': 'bold white',
            'border_style': 'bright_black',
            'show_lines': True,
            'pad_edge': True
        })