#!/usr/bin/env python3
"""
PDF Chat Appliance - Main Entry Point

This is the main entry point for the PDF Chat Appliance server.
It initializes the QueryServer and runs the Flask application.
"""

import argparse
import logging
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from pdfchat import QueryServer, Config

def main():
    """Main entry point for the PDF Chat Appliance."""
    parser = argparse.ArgumentParser(description="PDF Chat Appliance Server")
    parser.add_argument("command", choices=["serve"], help="Command to run")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=5000, help="Port to bind to")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    
    args = parser.parse_args()
    
    if args.command == "serve":
        try:
            # Initialize configuration
            config = Config()
            
            # Create and run the server
            server = QueryServer(config)
            server.run(host=args.host, port=args.port, debug=args.debug)
            
        except Exception as e:
            logging.error(f"Failed to start server: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main() 