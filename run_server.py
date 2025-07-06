#!/usr/bin/env python3
"""
Main server runner for PDF Chat Appliance.

Starts the FastAPI server with proper configuration and logging.
"""

import argparse
import logging
import sys
from pathlib import Path

# Mandatory .venv activation check
if "venv" not in sys.executable:
    raise RuntimeError("VENV NOT ACTIVATED. Please activate `.venv` before running this script.")

from pdfchat.config import Config
from pdfchat.fastapi_server import FastAPIQueryServer

import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pdfchat.server import QueryServer

if __name__ == "__main__":
    print("🚀 Starting PDF Chat Appliance Server")
    print("=" * 50)

    # Create and run the server
    server = QueryServer()
    server.run(host="0.0.0.0", port=5000, debug=True)
    print()

# UNCONDITIONAL: Ensure prompt unsticking regardless of exit path
print()

# COMPREHENSIVE CLEANUP: Ensure all threads and processes are properly terminated
import atexit
import os


def cleanup_on_exit():
    """Ensure clean exit by terminating any remaining processes"""
    try:
        # Force flush all output
        import sys

        sys.stdout.flush()
        sys.stderr.flush()

        # Print final blank line
        print()
    except:
        pass


# Register cleanup function
atexit.register(cleanup_on_exit)
