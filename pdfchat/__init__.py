"""
PDF Chat Appliance - Main Package

A production-ready, self-hosted AI appliance for querying PDFs using
state-of-the-art LLMs, embeddings, and a modern WebUI.
"""

import logging
import os

from .config import Config
from .ingestion import PDFIngestion
from .server import QueryServer


# Configure logging
def setup_logging(log_level: str = "INFO") -> None:
    """Setup logging configuration for the application."""
    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))

    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Create file handler for logs directory
    logs_dir = "logs"
    os.makedirs(logs_dir, exist_ok=True)
    file_handler = logging.FileHandler(os.path.join(logs_dir, "pdfchat.log"))
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    # Configure specific loggers
    loggers = {
        "pdfchat": logging.getLogger("pdfchat"),
        "memory": logging.getLogger("memory"),
        "llama_index": logging.getLogger("llama_index"),
        "chromadb": logging.getLogger("chromadb"),
    }

    # Set specific levels for different components
    for _logger_name, logger in loggers.items():
        logger.setLevel(getattr(logging, log_level.upper()))

# Package metadata
__version__ = "1.0.0"
__author__ = "PDF Chat Appliance Team"

__all__ = ["Config", "PDFIngestion", "QueryServer"]
