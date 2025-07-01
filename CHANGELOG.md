# Changelog

All notable changes to the PDF Chat Appliance project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-06-30

### Added
- Modular package structure with `pdfchat/` package
- Typer-based CLI with unified interface (`pdfchat.py`)
- Centralized configuration management (`config.py`)
- PDF ingestion module (`ingestion.py`)
- Flask-based API server (`server.py`)
- Utility functions (`utils.py`)
- Comprehensive test suite (`tests/`)
- Professional documentation (`docs/`)
- YAML configuration support
- Health check endpoint (`/health`)
- CLI commands: `ingest`, `serve`, `config`, `version`

### Changed
- Restructured project from monolithic scripts to modular architecture
- Moved original scripts to `scripts/` directory
- Rewritten `README.md` with professional format
- Updated `requirements.txt` with new dependencies

### Removed
- Direct script execution (now through CLI)

## [0.1.0] - Pre-modularization

### Added
- Basic PDF ingestion with llama-index
- Simple Flask query server
- Docker support
- Basic README

[1.0.0]: https://github.com/your-org/pdf-chat-appliance/releases/tag/v1.0.0 