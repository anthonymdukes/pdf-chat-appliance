"""
Tests for the Config module.
"""

import pytest
import tempfile
import os
from pathlib import Path
from pdfchat.config import Config


class TestConfig:
    """Test cases for Config class."""
    
    def test_default_config(self):
        """Test expected use case: default configuration."""
        config = Config()
        assert config.docs_dir == "documents"
        assert config.persist_dir == "chroma_store"
        assert config.embedding_model == "sentence-transformers/all-MiniLM-L6-v2"
        assert config.host == "0.0.0.0"
        assert config.port == 5000
    
    def test_custom_config(self):
        """Test edge case: custom configuration values."""
        config = Config(
            docs_dir="custom_docs",
            persist_dir="custom_store",
            port=8080
        )
        assert config.docs_dir == "custom_docs"
        assert config.persist_dir == "custom_store"
        assert config.port == 8080
    
    def test_from_yaml_nonexistent_file(self):
        """Test failure case: loading from non-existent YAML file."""
        config = Config.from_yaml("nonexistent.yaml")
        # Should return default config when file doesn't exist
        assert config.docs_dir == "documents"
        assert config.persist_dir == "chroma_store"
    
    def test_to_yaml_and_from_yaml(self):
        """Test expected use case: save and load YAML configuration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = os.path.join(temp_dir, "test_config.yaml")
            
            # Create config and save to YAML
            original_config = Config(docs_dir="test_docs", port=9000)
            original_config.to_yaml(config_path)
            
            # Load from YAML
            loaded_config = Config.from_yaml(config_path)
            
            # Verify values are preserved
            assert loaded_config.docs_dir == "test_docs"
            assert loaded_config.port == 9000
            assert loaded_config.host == "0.0.0.0"  # default value
    
    def test_post_init_creates_directories(self):
        """Test expected use case: directories are created on initialization."""
        with tempfile.TemporaryDirectory() as temp_dir:
            docs_dir = os.path.join(temp_dir, "test_docs")
            persist_dir = os.path.join(temp_dir, "test_store")
            
            config = Config(docs_dir=docs_dir, persist_dir=persist_dir)
            
            # Verify directories were created
            assert os.path.exists(docs_dir)
            assert os.path.exists(persist_dir) 