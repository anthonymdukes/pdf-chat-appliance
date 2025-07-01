"""
Configuration management for PDF Chat Appliance.

This module provides centralized configuration for all components including
paths, model settings, and server configuration.
"""

import os
from dataclasses import dataclass
from typing import Optional
import yaml


@dataclass
class Config:
    """Centralized configuration for PDF Chat Appliance."""
    
    # Paths
    docs_dir: str = "documents"
    persist_dir: str = "chroma_store"
    
    # Embedding model
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    # Server settings
    host: str = "0.0.0.0"
    port: int = 5000
    
    # LLM settings (for future Ollama integration)
    llm_model: Optional[str] = None
    llm_base_url: Optional[str] = None
    
    @classmethod
    def from_yaml(cls, config_path: str = "config/default.yaml") -> "Config":
        """Load configuration from YAML file."""
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config_data = yaml.safe_load(f)
                return cls(**config_data)
        return cls()
    
    def to_yaml(self, config_path: str = "config/default.yaml") -> None:
        """Save configuration to YAML file."""
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        with open(config_path, 'w') as f:
            yaml.dump(self.__dict__, f, default_flow_style=False)
    
    def __post_init__(self):
        """Ensure directories exist."""
        os.makedirs(self.docs_dir, exist_ok=True)
        os.makedirs(self.persist_dir, exist_ok=True)


# Global config instance
config = Config() 