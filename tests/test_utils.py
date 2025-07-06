"""
Tests for the utils module.
"""

import os
import tempfile

from pdfchat.utils import (
    ensure_directory,
    format_response,
    get_pdf_count,
    load_json_config,
    save_json_config,
    validate_pdf_directory,
)


class TestUtils:
    """Test cases for utility functions."""

    def test_ensure_directory(self):
        """Test expected use case: creating directories."""
        with tempfile.TemporaryDirectory() as temp_dir:
            new_dir = os.path.join(temp_dir, "test_dir", "subdir")
            ensure_directory(new_dir)
            assert os.path.exists(new_dir)

    def test_ensure_directory_already_exists(self):
        """Test edge case: directory already exists."""
        with tempfile.TemporaryDirectory() as temp_dir:
            ensure_directory(temp_dir)  # Should not raise error
            assert os.path.exists(temp_dir)

    def test_load_json_config_nonexistent(self):
        """Test failure case: loading non-existent JSON config."""
        config = load_json_config("nonexistent.json")
        assert config == {}

    def test_save_and_load_json_config(self):
        """Test expected use case: save and load JSON configuration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = os.path.join(temp_dir, "test_config.json")
            test_config = {"key": "value", "number": 42}

            save_json_config(test_config, config_path)

            loaded_config = load_json_config(config_path)
            assert loaded_config == test_config

    def test_validate_pdf_directory_with_pdfs(self):
        """Test expected use case: directory with PDF files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a dummy PDF file
            pdf_file = os.path.join(temp_dir, "test.pdf")
            with open(pdf_file, "w") as f:
                f.write("dummy pdf content")

            assert validate_pdf_directory(temp_dir) is True

    def test_validate_pdf_directory_no_pdfs(self):
        """Test edge case: directory without PDF files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a non-PDF file
            txt_file = os.path.join(temp_dir, "test.txt")
            with open(txt_file, "w") as f:
                f.write("text content")

            assert validate_pdf_directory(temp_dir) is False

    def test_validate_pdf_directory_nonexistent(self):
        """Test failure case: non-existent directory."""
        assert validate_pdf_directory("nonexistent_dir") is False

    def test_get_pdf_count(self):
        """Test expected use case: counting PDF files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create multiple PDF files
            for i in range(3):
                pdf_file = os.path.join(temp_dir, f"test_{i}.pdf")
                with open(pdf_file, "w") as f:
                    f.write(f"pdf content {i}")

            # Create a non-PDF file
            txt_file = os.path.join(temp_dir, "test.txt")
            with open(txt_file, "w") as f:
                f.write("text content")

            assert get_pdf_count(temp_dir) == 3

    def test_format_response_no_truncation(self):
        """Test expected use case: response within limit."""
        response = "Short response"
        formatted = format_response(response, max_length=20)
        assert formatted == response

    def test_format_response_with_truncation(self):
        """Test edge case: response exceeds limit."""
        response = "This is a very long response that should be truncated"
        formatted = format_response(response, max_length=20)
        assert len(formatted) == 23  # 20 chars + "..."
        assert formatted.endswith("...")

    def test_format_response_no_max_length(self):
        """Test edge case: no max_length specified."""
        response = "Any length response"
        formatted = format_response(response)
        assert formatted == response
