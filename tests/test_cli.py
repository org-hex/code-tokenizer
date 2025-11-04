"""
Tests for CLI functionality
"""

import pytest
import tempfile
import os
from click.testing import CliRunner
from unittest.mock import patch
import main


class TestCLI:
    """Test CLI commands"""

    def setup_method(self):
        """Setup test environment"""
        self.runner = CliRunner()
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir)

    def create_test_files(self):
        """Create test files for testing"""
        # Create a Python file
        with open(os.path.join(self.temp_dir, "test.py"), 'w') as f:
            f.write('''
def hello():
    print("Hello, World!")

if __name__ == "__main__":
    hello()
''')

        # Create a JavaScript file
        with open(os.path.join(self.temp_dir, "test.js"), 'w') as f:
            f.write('''
function hello() {
    console.log("Hello, World!");
}

hello();
''')

        # Create a directory to exclude
        os.makedirs(os.path.join(self.temp_dir, "node_modules"))
        with open(os.path.join(self.temp_dir, "node_modules", "external.js"), 'w') as f:
            f.write('console.log("This should be excluded");')

    def test_cli_help_command(self):
        """Test CLI help command"""
        result = self.runner.invoke(main.cli, ['--help'])
        assert result.exit_code == 0
        assert 'collect' in result.output
        assert 'analyze' in result.output
        assert 'scan' in result.output

    def test_cli_info_command(self):
        """Test CLI info command"""
        result = self.runner.invoke(main.cli, ['info'])
        assert result.exit_code == 0
        assert 'Code Tokenizer' in result.output
        assert 'MIT License' in result.output

    def test_cli_collect_command(self):
        """Test CLI collect command"""
        self.create_test_files()

        result = self.runner.invoke(main.cli, [
            'collect',
            self.temp_dir,
            '--no-cache'  # Disable cache for testing
        ])

        assert result.exit_code == 0
        assert 'Token Statistics' in result.output

    def test_cli_collect_with_patterns(self):
        """Test CLI collect command with patterns"""
        self.create_test_files()

        result = self.runner.invoke(main.cli, [
            'collect',
            self.temp_dir,
            '--patterns', '*.py',
            '--no-cache'
        ])

        assert result.exit_code == 0

    def test_cli_collect_with_exclude(self):
        """Test CLI collect command with exclude"""
        self.create_test_files()

        result = self.runner.invoke(main.cli, [
            'collect',
            self.temp_dir,
            '--exclude', 'node_modules',
            '--no-cache'
        ])

        assert result.exit_code == 0

    def test_cli_collect_with_output(self):
        """Test CLI collect command with output file"""
        self.create_test_files()
        output_file = os.path.join(self.temp_dir, "output.txt")

        result = self.runner.invoke(main.cli, [
            'collect',
            self.temp_dir,
            '--output', output_file,
            '--no-cache'
        ])

        assert result.exit_code == 0
        assert os.path.exists(output_file)

        # Check that output file has content
        with open(output_file, 'r') as f:
            content = f.read()
            assert len(content) > 0

    def test_cli_scan_command(self):
        """Test CLI scan command"""
        self.create_test_files()

        result = self.runner.invoke(main.cli, [
            'scan',
            self.temp_dir
        ])

        assert result.exit_code == 0
        assert 'test.py' in result.output
        assert 'test.js' in result.output

    def test_cli_analyze_command(self):
        """Test CLI analyze command"""
        # Create a test file to analyze
        test_file = os.path.join(self.temp_dir, "test.txt")
        with open(test_file, 'w') as f:
            f.write('Hello, World!\nThis is a test file.')

        result = self.runner.invoke(main.cli, [
            'analyze',
            test_file
        ])

        assert result.exit_code == 0
        assert 'File Analysis' in result.output

    def test_cli_analyze_nonexistent_file(self):
        """Test CLI analyze command with nonexistent file"""
        result = self.runner.invoke(main.cli, [
            'analyze',
            '/path/to/nonexistent/file.txt'
        ])

        assert result.exit_code != 0

    def test_cli_collect_nonexistent_directory(self):
        """Test CLI collect command with nonexistent directory"""
        result = self.runner.invoke(main.cli, [
            'collect',
            '/path/to/nonexistent/directory'
        ])

        assert result.exit_code != 0

    def test_cli_cache_list_command(self):
        """Test CLI cache list command"""
        result = self.runner.invoke(main.cli, ['cache-list'])
        assert result.exit_code == 0

    def test_cli_cache_clear_command(self):
        """Test CLI cache clear command"""
        result = self.runner.invoke(main.cli, ['cache-clear'])
        assert result.exit_code == 0

    @patch('main.CodeCollector')
    def test_cli_collect_with_mock(self, mock_collector):
        """Test CLI collect command with mocked collector"""
        self.create_test_files()

        # Setup mock
        mock_instance = mock_collector.return_value
        mock_instance.collect_files.return_value = {
            'total_files': 2,
            'total_tokens': 100,
            'files': []
        }

        result = self.runner.invoke(main.cli, [
            'collect',
            self.temp_dir,
            '--no-cache'
        ])

        assert result.exit_code == 0
        mock_collector.return_value.collect_files.assert_called_once()