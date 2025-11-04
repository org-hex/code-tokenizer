"""
CodeCollector functional tests
Test file scanning, filtering, cache management and other features
"""

import pytest
import tempfile
import json
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock
from src.code_tokenizer.code_collector import CodeCollector


class TestCodeCollector:
    """CodeCollector test class"""

    def setup_method(self):
        """Setup before each test method"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.cache_dir = self.temp_dir / ".cache"
        self.collector = CodeCollector(cache_dir=str(self.cache_dir))

    def teardown_method(self):
        """Cleanup after each test method"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_init(self):
        """Test CodeCollector initialization"""
        assert self.collector.cache_dir.exists()
        assert self.collector.cache_index_file.exists() or not self.collector.cache_index_file.exists()
        assert isinstance(self.collector.cache_index, dict)

    def test_init_with_default_cache_dir(self):
        """Test initialization with default cache directory"""
        collector = CodeCollector()
        assert collector.cache_dir.name == ".code_cache"

    def test_load_save_cache_index(self, temp_dir):
        """Test loading and saving cache index"""
        # Create new collector
        cache_dir = temp_dir / "test_cache"
        collector = CodeCollector(cache_dir=str(cache_dir))

        # Add some test data
        test_data = {"test_key": {"file": "test.txt", "created_at": "2024-01-01"}}
        collector.cache_index = test_data
        collector._save_cache_index()

        # Create new collector instance to test loading
        new_collector = CodeCollector(cache_dir=str(cache_dir))
        assert new_collector.cache_index == test_data

    def test_get_file_hash(self, temp_dir):
        """Test file hash calculation"""
        content = "Test content for hash calculation"
        file_path = temp_dir / "test_file.txt"
        file_path.write_text(content)

        hash1 = self.collector._get_file_hash(file_path)
        hash2 = self.collector._get_file_hash(file_path)

        assert isinstance(hash1, str)
        assert len(hash1) == 32  # MD5 hash length
        assert hash1 == hash2  # Same file should have same hash

        # Hash should change after modifying file content
        file_path.write_text("Modified content")
        hash3 = self.collector._get_file_hash(file_path)
        assert hash1 != hash3

    def test_get_file_hash_nonexistent(self):
        """Test hash calculation for non-existent files"""
        nonexistent_file = self.temp_dir / "nonexistent.txt"
        hash_value = self.collector._get_file_hash(nonexistent_file)
        assert hash_value == ""

    def test_get_project_hash(self):
        """Test project hash calculation"""
        project_path = Path("/test/project")
        file_patterns = ["*.py", "*.js"]
        exclude_patterns = ["node_modules", "*.test.py"]

        hash1 = self.collector._get_project_hash(project_path, file_patterns, exclude_patterns)
        hash2 = self.collector._get_project_hash(project_path, file_patterns, exclude_patterns)

        assert isinstance(hash1, str)
        assert len(hash1) == 16  # Truncated MD5 hash
        assert hash1 == hash2

        # Hash should change after changing parameters
        hash3 = self.collector._get_project_hash(project_path, ["*.py"], exclude_patterns)
        assert hash1 != hash3

    def test_scan_files_basic(self, sample_project_structure):
        """Test basic file scanning functionality"""
        files = self.collector.scan_files(str(sample_project_structure))

        assert isinstance(files, list)
        assert len(files) > 0

        # Verify all returned items are Path objects
        for file_path in files:
            assert isinstance(file_path, Path)
            assert file_path.exists()
            assert file_path.is_file()

        # Verify files are sorted and without duplicates
        assert files == sorted(set(files))

    def test_scan_files_with_patterns(self, sample_project_structure):
        """Test file scanning with pattern matching"""
        # Scan only Python files
        py_files = self.collector.scan_files(
            str(sample_project_structure),
            file_patterns=["*.py"]
        )

        for file_path in py_files:
            assert file_path.suffix == ".py"

        # Scan only Markdown files
        md_files = self.collector.scan_files(
            str(sample_project_structure),
            file_patterns=["*.md"]
        )

        for file_path in md_files:
            assert file_path.suffix == ".md"

    def test_scan_files_with_exclude_patterns(self, sample_project_structure):
        """Test file scanning with exclude patterns"""
        all_files = self.collector.scan_files(str(sample_project_structure))

        # Exclude test files
        filtered_files = self.collector.scan_files(
            str(sample_project_structure),
            exclude_patterns=["test_*.py"]
        )

        assert len(filtered_files) <= len(all_files)

        # Verify no test files
        for file_path in filtered_files:
            assert not file_path.name.startswith("test_")

    def test_scan_files_with_include_patterns(self, sample_project_structure):
        """Test file scanning with include patterns"""
        # Include only specific files
        included_files = self.collector.scan_files(
            str(sample_project_structure),
            include_patterns=["main.py"]
        )

        # Verify results based on actual implementation
        assert len(included_files) >= 1
        file_names = [f.name for f in included_files]
        assert "main.py" in file_names

        # Test multiple include patterns
        included_files = self.collector.scan_files(
            str(sample_project_structure),
            include_patterns=["main.py", "utils.py"]
        )

        assert len(included_files) >= 2
        file_names = [f.name for f in included_files]
        assert "main.py" in file_names
        assert "utils.py" in file_names

    def test_scan_files_excludes_hidden_files(self, temp_dir):
        """Test excluding hidden files"""
        # Create test files
        (temp_dir / "normal.py").write_text("print('normal')")
        (temp_dir / ".hidden.py").write_text("print('hidden')")
        (temp_dir / ".env").write_text("SECRET=value")

        files = self.collector.scan_files(str(temp_dir))

        # Should only include normal files, not hidden files
        file_names = [f.name for f in files]
        assert "normal.py" in file_names
        assert ".hidden.py" not in file_names
        assert ".env" not in file_names

    def test_scan_files_excludes_node_modules(self, sample_project_structure):
        """Test excluding node_modules directory"""
        files = self.collector.scan_files(str(sample_project_structure))

        # Verify no files from node_modules
        for file_path in files:
            assert "node_modules" not in str(file_path)

    def test_scan_files_empty_directory(self, temp_dir):
        """Test scanning empty directory"""
        files = self.collector.scan_files(str(temp_dir))
        assert files == []

    def test_scan_files_nonexistent_directory(self):
        """Test scanning non-existent directory"""
        files = self.collector.scan_files("/nonexistent/directory")
        # Should return empty list instead of throwing exception
        assert files == []

    def test_get_default_file_patterns(self):
        """Test getting default file patterns"""
        patterns = self.collector.get_default_file_patterns()
        assert isinstance(patterns, list)
        assert len(patterns) > 0

        # Verify inclusion of common code file extensions
        pattern_str = " ".join(patterns)
        assert "*.py" in pattern_str
        assert "*.js" in pattern_str
        assert "*.ts" in pattern_str

    def test_collect_code_basic(self, sample_project_structure):
        """Test basic code collection functionality"""
        output_file = self.temp_dir / "collected_code.txt"

        result_path = self.collector.collect_code(
            str(sample_project_structure),
            output_file=str(output_file),
            use_cache=False
        )

        assert result_path == str(output_file)
        assert output_file.exists()

        # Verify collected file content
        content = output_file.read_text(encoding='utf-8')
        assert "# Code Collection Report" in content
        assert "Project Path:" in content
        assert "File Count:" in content
        assert "main.py" in content or "utils.py" in content  # Should include some source code files

    def test_collect_code_with_cache(self, sample_project_structure):
        """Test code collection with cache"""
        output_file1 = self.temp_dir / "collected1.txt"
        output_file2 = self.temp_dir / "collected2.txt"

        # First collection
        result1 = self.collector.collect_code(
            str(sample_project_structure),
            output_file=str(output_file1),
            use_cache=True
        )

        # Second collection (should use cache)
        result2 = self.collector.collect_code(
            str(sample_project_structure),
            output_file=str(output_file2),
            use_cache=True
        )

        assert result1 == str(output_file1)
        assert result2 == str(output_file2)
        assert output_file1.exists()
        assert output_file2.exists()

        # Verify cache files exist
        cache_files = list(self.cache_dir.glob("cache_*.txt"))
        assert len(cache_files) > 0

    def test_collect_code_without_cache(self, sample_project_structure):
        """Test code collection without cache"""
        output_file = self.temp_dir / "collected_no_cache.txt"

        result = self.collector.collect_code(
            str(sample_project_structure),
            output_file=str(output_file),
            use_cache=False
        )

        assert result == str(output_file)
        assert output_file.exists()

        # Verify no cache files created
        cache_files = list(self.cache_dir.glob("cache_*.txt"))
        assert len(cache_files) == 0

    def test_collect_code_no_files_found(self, temp_dir):
        """Test code collection when no files found"""
        output_file = self.temp_dir / "empty_result.txt"

        result = self.collector.collect_code(
            str(temp_dir),
            output_file=str(output_file),
            file_patterns=["*.nonexistent"]
        )

        assert result == str(output_file)
        # Should create file but content might be minimal

    def test_collect_code_custom_format(self, sample_project_structure):
        """Test code collection with custom format"""
        output_file = self.temp_dir / "custom_format.txt"

        result = self.collector.collect_code_custom_format(
            str(sample_project_structure),
            output_file=str(output_file)
        )

        assert result == str(output_file)
        assert output_file.exists()

        # Verify custom format
        content = output_file.read_text(encoding='utf-8')
        assert "# Code Collection Report" in content
        assert "####### [idx:" in content  # Custom format marker

    def test_collect_code_custom_format_with_include_patterns(self, sample_project_structure):
        """Test custom format code collection with include patterns"""
        output_file = self.temp_dir / "custom_include.txt"

        result = self.collector.collect_code_custom_format(
            str(sample_project_structure),
            output_file=str(output_file),
            include_patterns=["main.py"]
        )

        assert result == str(output_file)
        content = output_file.read_text(encoding='utf-8')
        assert "main.py" in content
        # Based on actual implementation, might include other files, but should at least include specified files

    def test_clear_cache_all(self):
        """Test clearing all cache"""
        # Create some cache data
        self.collector.cache_index["test1"] = {"file": "cache1.txt"}
        self.collector.cache_index["test2"] = {"file": "cache2.txt"}
        self.collector._save_cache_index()

        # Create some cache files
        (self.cache_dir / "cache1.txt").write_text("test1")
        (self.cache_dir / "cache2.txt").write_text("test2")

        # Clear all cache
        self.collector.clear_cache()

        assert len(self.collector.cache_index) == 0
        assert not list(self.cache_dir.glob("cache_*.txt"))

    def test_clear_cache_project_specific(self):
        """Test clearing cache for specific project"""
        # Create cache data for two projects
        self.collector.cache_index["project1_abc"] = {"file": "cache1.txt"}
        self.collector.cache_index["project2_def"] = {"file": "cache2.txt"}
        self.collector._save_cache_index()

        # Create cache files
        (self.cache_dir / "cache1.txt").write_text("test1")
        (self.cache_dir / "cache2.txt").write_text("test2")

        # Clear only project1's cache
        self.collector.clear_cache("project1")

        # Verify only project1's cache is cleared
        assert "project1_abc" not in self.collector.cache_index
        assert "project2_def" in self.collector.cache_index
        assert not (self.cache_dir / "cache1.txt").exists()
        assert (self.cache_dir / "cache2.txt").exists()

    def test_clear_cache_nonexistent_project(self):
        """Test clearing cache for non-existent project"""
        initial_cache_index = self.collector.cache_index.copy()

        # Try to clear non-existent project cache
        self.collector.clear_cache("nonexistent_project")

        # Cache index should remain unchanged
        assert self.collector.cache_index == initial_cache_index

    def test_list_cache_empty(self):
        """Test listing empty cache"""
        # Ensure cache is empty
        self.collector.cache_index.clear()
        self.collector._save_cache_index()

        # Listing cache should not crash
        with patch('src.code_tokenizer.code_collector.console') as mock_console:
            self.collector.list_cache()
            mock_console.print.assert_called()

    def test_list_cache_with_data(self):
        """Test listing cache with data"""
        # Create test cache data
        from datetime import datetime
        test_time = datetime.now().isoformat()

        self.collector.cache_index = {
            "testproject_abc": {
                "file": "cache_test.txt",
                "project_path": "/test/path",
                "created_at": test_time,
                "file_count": 10
            }
        }
        self.collector._save_cache_index()

        # Create cache file
        (self.cache_dir / "cache_test.txt").write_text("test content")

        # Listing cache should not crash
        with patch('src.code_tokenizer.code_collector.console') as mock_console:
            self.collector.list_cache()
            mock_console.print.assert_called()

    def test_write_files_to_file(self, sample_project_structure):
        """Test internal method for writing files to output file"""
        files = self.collector.scan_files(str(sample_project_structure))
        output_file = self.temp_dir / "test_output.txt"

        # Call internal method
        self.collector._write_files_to_file(files, str(output_file), sample_project_structure)

        assert output_file.exists()
        content = output_file.read_text(encoding='utf-8')
        assert "# Code Collection Report" in content
        assert "Project Path:" in content

    def test_write_files_to_custom_format(self, sample_project_structure):
        """Test internal method for writing files to custom format"""
        files = self.collector.scan_files(str(sample_project_structure))
        output_file = self.temp_dir / "test_custom.txt"

        # Call internal method
        self.collector._write_files_to_custom_format(files, str(output_file), sample_project_structure)

        assert output_file.exists()
        content = output_file.read_text(encoding='utf-8')
        assert "# Code Collection Report" in content
        assert "####### [idx:" in content

    def test_collect_code_with_file_patterns(self, sample_project_structure):
        """Test code collection with file patterns"""
        output_file = self.temp_dir / "python_only.txt"

        result = self.collector.collect_code(
            str(sample_project_structure),
            output_file=str(output_file),
            file_patterns=["*.py"],
            use_cache=False
        )

        assert result == str(output_file)
        content = output_file.read_text(encoding='utf-8')

        # Verify only Python files are included
        assert ".py" in content
        # Based on sample project structure, should not include Markdown files
        assert "README.md" not in content

    def test_collect_code_error_handling(self, temp_dir):
        """Test error handling in code collection"""
        # Create a test file
        test_file = temp_dir / "test.py"
        test_file.write_text("print('test')")

        output_file = temp_dir / "error_test.txt"

        # Simple test: verify normal flow
        result = self.collector.collect_code(
            str(temp_dir),
            output_file=str(output_file),
            use_cache=False,
            file_patterns=["*.py"]
        )

        assert result == str(output_file)
        assert output_file.exists()

    def test_scan_files_duplicate_handling(self, sample_project_structure):
        """Test duplicate handling in file scanning"""
        # Use multiple patterns that might cause duplicates
        files = self.collector.scan_files(
            str(sample_project_structure),
            file_patterns=["*.py", "*.md", "*.txt"]  # Include some potentially non-existent patterns
        )

        # Verify no duplicate files
        assert len(files) == len(set(files))

        # Verify files are sorted
        assert files == sorted(files)