"""
Utility functions for PDF Chat Appliance.

This module provides shared helper functions used across the application.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional


def ensure_directory(path: str) -> None:
    """Ensure a directory exists, creating it if necessary."""
    Path(path).mkdir(parents=True, exist_ok=True)


def load_json_config(config_path: str) -> Dict[str, Any]:
    """Load configuration from JSON file."""
    if os.path.exists(config_path):
        with open(config_path) as f:
            return json.load(f)
    return {}


def save_json_config(config: Dict[str, Any], config_path: str) -> None:
    """Save configuration to JSON file."""
    ensure_directory(os.path.dirname(config_path))
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)


def validate_pdf_directory(docs_dir: str) -> bool:
    """Validate that the documents directory contains PDFs."""
    if not os.path.exists(docs_dir):
        return False

    pdf_files = list(Path(docs_dir).rglob("*.pdf"))
    return len(pdf_files) > 0


def get_pdf_count(docs_dir: str) -> int:
    """Get the number of PDF files in the documents directory."""
    if not os.path.exists(docs_dir):
        return 0

    pdf_files = list(Path(docs_dir).rglob("*.pdf"))
    return len(pdf_files)


def format_response(response: str, max_length: Optional[int] = None) -> str:
    """Format and truncate response if needed."""
    if max_length and len(response) > max_length:
        return response[:max_length] + "..."
    return response
