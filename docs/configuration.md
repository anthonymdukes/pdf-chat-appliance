Generated: 2025-01-27 23:59:00

# Configuration Guide

## Overview

PDF Chat Appliance uses a centralized configuration system with YAML files and environment variables.

## Configuration Files

### Default Configuration

Location: `config/default.yaml`

```yaml
# Paths (OVA-specific)
docs_dir: "/var/lib/pdfchat/documents"
persist_dir: "/var/lib/pdfchat/chroma_store"

# Embedding model
embedding_model: "sentence-transformers/all-MiniLM-L6-v2"

# Server settings
host: "0.0.0.0"
port: 5000

# LLM settings (for future Ollama integration)
llm_model: null
llm_base_url: null

# OVA-specific settings
log_dir: "/var/log/pdfchat"
config_dir: "/etc/pdfchat"
```

## Configuration Options

### Paths

- `docs_dir`: Directory containing PDF files to ingest
- `persist_dir`: Directory for ChromaDB vector storage
- `log_dir`: Directory for application logs
- `config_dir`: Directory for configuration files

### Server Settings

- `host`: Server binding address (default: 0.0.0.0)
- `port`: Server port (default: 5000)

### AI Models

- `embedding_model`: HuggingFace model for text embeddings
- `llm_model`: Ollama model name (future)
- `llm_base_url`: Ollama server URL (future)

## Environment Variables

You can override configuration using environment variables:

```bash
export PDFCHAT_HOST=127.0.0.1
export PDFCHAT_PORT=8080
export PDFCHAT_DOCS_DIR=/custom/path
```

## CLI Configuration

### View Current Configuration

```bash
pdfchat config show
```

### Reset to Defaults

```bash
pdfchat config reset
```

### Custom Configuration File

```bash
pdfchat serve --config /path/to/custom.yaml
```

## OVA Deployment

For OVA deployments, configuration is automatically set to:

- Application: `/opt/pdf-chat-appliance`
- Data: `/var/lib/pdfchat`
- Logs: `/var/log/pdfchat`
- Config: `/etc/pdfchat`

## Advanced Configuration

### Multiple Environments

Create environment-specific configs:

- `config/development.yaml`
- `config/production.yaml`
- `config/testing.yaml`

### Memory Backend Configuration

Memory layer configuration is handled separately in the memory package.
