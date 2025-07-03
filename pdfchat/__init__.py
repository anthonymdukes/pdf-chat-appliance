"""
PDF Chat Appliance - Enterprise-scale multi-vendor documentation system.

This package provides a complete solution for ingesting, processing, and querying
PDF documents using local LLMs and vector search capabilities.
"""

import logging
import os
from pathlib import Path

# Configure logging for the entire package
def setup_logging(log_level: str = "INFO", log_dir: str = "logs"):
    """Setup structured logging for PDF Chat Appliance."""
    
    # Create logs directory if it doesn't exist
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)
    
    # Configure logging format
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=log_format,
        datefmt=date_format,
        handlers=[
            logging.FileHandler(log_path / "pdfchat.log"),
            logging.StreamHandler()  # Console output
        ]
    )
    
    # Create specific loggers for different components
    loggers = {
        'pdfchat.server': logging.getLogger('pdfchat.server'),
        'pdfchat.ingestion': logging.getLogger('pdfchat.ingestion'),
        'pdfchat.config': logging.getLogger('pdfchat.config'),
        'pdfchat.utils': logging.getLogger('pdfchat.utils'),
    }
    
    # Set specific levels for different components
    for logger_name, logger in loggers.items():
        logger.setLevel(getattr(logging, log_level.upper()))
    
    return loggers

# Auto-setup logging when package is imported
if not logging.getLogger().handlers:
    setup_logging()

__version__ = "1.0.0"
__author__ = "PDF Chat Appliance Team"

from .config import Config
from .ingestion import PDFIngestion
from .server import QueryServer

__all__ = ["Config", "PDFIngestion", "QueryServer"] 