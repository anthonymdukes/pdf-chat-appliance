# Architecture Decision Record

status: approved

## Project: PDF Chat Appliance

### Architecture Principles

- Python 3.9+, modular packages
- ChromaDB for vector storage, Qdrant support
- Ollama LLM backend with local/remote options
- Flask API, Typer CLI, and optional WebUI
- Dockerized deployment for all major services

### Key Decisions

- All service initialization via bootstrap scripts
- Strict separation of data (uploads, vector db, logs)
- .venv for Python dependency isolation
