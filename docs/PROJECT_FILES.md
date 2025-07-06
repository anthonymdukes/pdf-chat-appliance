# Project Files Documentation

## Current File Structure (GPU-Enabled Workflow)

This document describes the current project structure after the environment reset and file audit for GPU-enabled development.

## Root Directory Files

### Core Application Files

- **`pdfchat/`** - Main application package (Python modules)
- **`run_server.py`** - Standalone server entry point
- **`requirements.txt`** - Python dependencies
- **`pyproject.toml`** - Project configuration and build settings

### Docker Configuration Files

- **`docker-compose.yml`** - **CANONICAL** - Production deployment with Qdrant, Ollama, WebUI
- **`docker-compose.dev.yml`** - Development environment with debugging tools
- **`Dockerfile`** - Production container build
- **`Dockerfile.dev`** - Development container build
- **`.dockerignore`** - Docker build exclusions

### Configuration Files

- **`config/`** - Application configuration files
- **`nginx.conf`** - Nginx reverse proxy configuration (used in production)
- **`.env`** - Environment variables (if present)

### Documentation Files

- **`README.md`** - Main project documentation
- **`PLANNING.md`** - System architecture and planning
- **`TASK.md`** - Current task queue and status
- **`CHANGELOG.md`** - Version history and changes
- **`LICENSE`** - Project license
- **`docs/`** - Comprehensive documentation

### Agent System Files

- **`.ai/`** - Agent planning and story management
- **`.cursor/`** - Cursor IDE agent rules
- **`RULES_INDEX.md`** - Agent rules index
- **`AGENT_BEST_PRACTICES.md`** - Agent development guidelines
- **`session_notes.md`** - Session logs and agent activity

### Data Directories

- **`data/`** - Application data storage
- **`documents/`** - PDF document storage
- **`uploads/`** - File upload directory
- **`custom_docs/`** - Custom documentation
- **`memory/`** - Chat history and session data

### Development Files

- **`tests/`** - Test suite
- **`scripts/`** - Utility scripts
- **`.venv/`** - Python virtual environment
- **`.git/`** - Git repository
- **`.github/`** - GitHub workflows and templates
- **`.gitignore`** - Git exclusions

### Deployment Files

- **`docker/`** - Docker deployment documentation
- **`packer/`** - OVA build configuration for VMware deployment
- **`ssl/`** - SSL certificates (if present)

### System Files

- **`SYSTEM_OVERVIEW.md`** - System architecture overview

## Archived Files

### Legacy Configurations (`archive/legacy_configs/`)

- **`docker-compose.microservices.yml`** - Legacy microservices architecture (Redis, API Gateway, etc.)

### Legacy Files (`archive/legacy_files/`)

- **`services/`** - Legacy microservices implementation
- **`monitoring/`** - Legacy Prometheus/Grafana monitoring stack
- **`app/`** - Empty legacy application directory
- **`chroma_store/`** - Legacy ChromaDB storage (replaced by Qdrant)
- **`custom_store/`** - Empty legacy custom storage
- **`embeddings/`** - Legacy embedding storage
- **`test_docs/`** - Empty test documentation directory

## Docker Compose Files

### Current Files

1. **`docker-compose.yml`** - **PRIMARY** - Production deployment
   - PDF Chat Appliance (port 5000)
   - Ollama LLM (port 11434)
   - Qdrant Vector Database (port 6333)
   - Open WebUI (port 8080)
   - Nginx reverse proxy (ports 80, 443)

2. **`docker-compose.dev.yml`** - Development environment
   - Development container with debugging tools
   - Volume mounts for live code editing
   - Debug port (5678) for IDE integration

### Archived Files

- **`docker-compose.microservices.yml`** - Legacy microservices stack
  - Redis for caching
  - API Gateway
  - Separate services for LLM, embedding, vector store, etc.
  - Prometheus/Grafana monitoring

## File Retention Rationale

### Kept Files

- **Core application files** - Required for GPU-enabled workflow
- **Current Docker configurations** - Active deployment stack
- **Documentation** - Essential for development and deployment
- **Agent system files** - Required for autonomous development
- **Data directories** - Required for application functionality
- **Development files** - Required for testing and development
- **Deployment files** - Required for production deployment

### Archived Files

- **Legacy microservices** - Replaced by simplified monolithic architecture
- **Legacy monitoring** - Not integrated with current stack
- **Empty directories** - No content, potential confusion
- **Legacy storage** - Replaced by Qdrant vector database
- **Legacy configurations** - Superseded by current Docker setup

## Next Steps for GPU-Enabled Workflow

1. **Update Docker configurations** for GPU support
2. **Add CUDA dependencies** to requirements.txt
3. **Modify Dockerfiles** for GPU-enabled base images
4. **Update documentation** for GPU deployment
5. **Add GPU monitoring** and resource management
6. **Optimize for GPU acceleration** in core application

## Archive Recovery

If any archived files are needed for reference or recovery:

- **Legacy configs**: `archive/legacy_configs/`
- **Legacy files**: `archive/legacy_files/`
- **Log archives**: `logs_archive_*.zip`
- **Session archives**: `session_logs_archive_*.zip`

All archived files are preserved and can be restored if needed for future development or reference.
