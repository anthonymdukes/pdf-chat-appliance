#!/usr/bin/env python3
"""
PDF Chat Appliance CLI

A unified command-line interface for the PDF Chat Appliance.
"""

import typer
from pathlib import Path
from typing import Optional

from pdfchat import __version__, Config, PDFIngestion, QueryServer
from pdfchat.utils import validate_pdf_directory, get_pdf_count

app = typer.Typer(
    name="pdfchat",
    help="PDF Chat Appliance - Query your PDFs with AI",
    add_completion=False
)


@app.command()
def ingest(
    docs_dir: str = typer.Argument(
        "documents",
        help="Directory containing PDF files to ingest"
    ),
    config_file: Optional[str] = typer.Option(
        None,
        "--config",
        "-c",
        help="Path to configuration file"
    )
):
    """Ingest PDFs from a directory into the vector database."""
    try:
        # Load configuration
        config = Config.from_yaml(config_file) if config_file else Config()
        
        # Validate input directory
        if not validate_pdf_directory(docs_dir):
            typer.echo(f"❌ No PDF files found in {docs_dir}")
            raise typer.Exit(1)
        
        pdf_count = get_pdf_count(docs_dir)
        typer.echo(f"📄 Found {pdf_count} PDF files in {docs_dir}")
        
        # Ingest PDFs
        ingestion = PDFIngestion(config)
        ingestion.ingest_pdfs(docs_dir)
        
        typer.echo("✅ PDF ingestion completed successfully!")
        
    except Exception as e:
        typer.echo(f"❌ Error during ingestion: {e}")
        raise typer.Exit(1)


@app.command()
def serve(
    host: str = typer.Option(
        "0.0.0.0",
        "--host",
        "-h",
        help="Host to bind the server to"
    ),
    port: int = typer.Option(
        5000,
        "--port",
        "-p",
        help="Port to bind the server to"
    ),
    debug: bool = typer.Option(
        False,
        "--debug",
        help="Enable debug mode"
    ),
    config_file: Optional[str] = typer.Option(
        None,
        "--config",
        "-c",
        help="Path to configuration file"
    )
):
    """Start the PDF Chat Appliance server."""
    try:
        # Load configuration
        config = Config.from_yaml(config_file) if config_file else Config()
        config.host = host
        config.port = port
        
        # Start server
        server = QueryServer(config)
        typer.echo(f"🚀 Starting server on {host}:{port}")
        server.run(host=host, port=port, debug=debug)
        
    except Exception as e:
        typer.echo(f"❌ Error starting server: {e}")
        raise typer.Exit(1)


@app.command()
def config(
    action: str = typer.Argument(
        "show",
        help="Action to perform: show, edit, reset"
    ),
    config_file: str = typer.Option(
        "config/default.yaml",
        "--config",
        "-c",
        help="Path to configuration file"
    )
):
    """Manage configuration."""
    try:
        if action == "show":
            config = Config.from_yaml(config_file)
            typer.echo("📋 Current Configuration:")
            for key, value in config.__dict__.items():
                typer.echo(f"  {key}: {value}")
                
        elif action == "edit":
            config = Config.from_yaml(config_file)
            config.to_yaml(config_file)
            typer.echo(f"✅ Configuration saved to {config_file}")
            
        elif action == "reset":
            config = Config()
            config.to_yaml(config_file)
            typer.echo(f"✅ Configuration reset and saved to {config_file}")
            
        else:
            typer.echo(f"❌ Unknown action: {action}")
            raise typer.Exit(1)
            
    except Exception as e:
        typer.echo(f"❌ Error managing configuration: {e}")
        raise typer.Exit(1)


@app.command()
def version():
    """Show version information."""
    typer.echo(f"PDF Chat Appliance v{__version__}")


if __name__ == "__main__":
    app() 