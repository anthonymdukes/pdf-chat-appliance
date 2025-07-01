"""
PDF Chat Appliance - A production-ready, self-hosted AI appliance for querying PDFs.

This package provides modular components for PDF ingestion, serving, and configuration.
"""

__version__ = "1.0.0"
__author__ = "PDF Chat Appliance Team"

from .config import Config
from .ingestion import PDFIngestion
from .server import QueryServer

__all__ = ["Config", "PDFIngestion", "QueryServer"] 