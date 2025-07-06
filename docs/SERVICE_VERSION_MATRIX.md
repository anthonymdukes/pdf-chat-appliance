# Service Version Matrix

## Overview
This document tracks the actual installed versions versus required versions for all target services in the PDF Chat Appliance environment.

## Environment Information
- **Platform**: Ubuntu-22.04 (WSL2)
- **Last Updated**: 2025-07-04 11:36:00
- **Agent**: deployment-monitor
- **Sprint**: 2.6 - Environment Preparation & Deployment Readiness

## Core Infrastructure

### Operating System
| Component | Required | Installed | Status | Notes |
|-----------|----------|-----------|--------|-------|
| Ubuntu | 20.04+ | 22.04 | ✅ | LTS version, fully supported |
| WSL | 2.0+ | 2.0 | ✅ | Latest WSL2 with GPU support |
| Kernel | 5.4+ | 6.6.87.2 | ✅ | Microsoft WSL2 kernel |

### Python Environment
| Component | Required | Installed | Status | Notes |
|-----------|----------|-----------|--------|-------|
| Python | 3.8+ | 3.10.12 | ✅ | Exceeds minimum requirement |
| pip | 20.0+ | 22.0.2 | ✅ | Latest stable version |

### GPU & CUDA
| Component | Required | Installed | Status | Notes |
|-----------|----------|-----------|--------|-------|
| NVIDIA Driver | 450+ | 576.80 | ✅ | Latest stable driver |
| CUDA | 11.0+ | 12.9 | ✅ | Latest CUDA version |
| GPU Memory | 8GB+ | 12GB | ✅ | NVIDIA TITAN V |

## Container Platform

### Docker
| Component | Required | Installed | Status | Notes |
|-----------|----------|-----------|--------|-------|
| Docker Engine | 20.10+ | 27.5.1 | ✅ | Latest stable version |
| Docker Compose | 1.29+ | 1.29.2 | ✅ | Compatible version |

## AI/ML Services

### Ollama
| Component | Required | Installed | Status | Notes |
|-----------|----------|-----------|--------|-------|
| Ollama | Latest | Pending | 🔄 | To be installed |
| CUDA Support | Required | ✅ | ✅ | CUDA 12.9 available |
| GPU Memory | 8GB+ | 12GB | ✅ | Sufficient for large models |

### FastAPI
| Component | Required | Installed | Status | Notes |
|-----------|----------|-----------|--------|-------|
| FastAPI | 0.100+ | Pending | 🔄 | To be installed |
| Uvicorn | 0.20+ | Pending | 🔄 | To be installed |
| Pydantic | 2.0+ | Pending | 🔄 | To be installed |

### Vector Databases

#### ChromaDB
| Component | Required | Installed | Status | Notes |
|-----------|----------|-----------|--------|-------|
| ChromaDB | 0.4.0+ | Pending | 🔄 | To be installed |
| Python | 3.8+ | 3.10.12 | ✅ | Compatible |
| Docker | Optional | 27.5.1 | ✅ | Available |

#### Qdrant
| Component | Required | Installed | Status | Notes |
|-----------|----------|-----------|--------|-------|
| Qdrant | 1.0+ | Pending | 🔄 | To be installed |
| Python Client | Latest | Pending | 🔄 | To be installed |
| Docker | Optional | 27.5.1 | ✅ | Available |

## Data Storage

### PostgreSQL
| Component | Required | Installed | Status | Notes |
|-----------|----------|-----------|--------|-------|
| PostgreSQL | 12+ | Pending | 🔄 | To be installed |
| Docker | Optional | 27.5.1 | ✅ | Available |
| Port | 5432 | Available | ✅ | Port ready |

### Redis
| Component | Required | Installed | Status | Notes |
|-----------|----------|-----------|--------|-------|
| Redis | 6.0+ | Pending | 🔄 | To be installed |
| Docker | Optional | 27.5.1 | ✅ | Available |
| Port | 6379 | Available | ✅ | Port ready |

## Development Tools

### Core Packages
| Component | Required | Installed | Status | Notes |
|-----------|----------|-----------|--------|-------|
| git | 2.0+ | 2.34.1 | ✅ | Latest stable version |
| curl | 7.0+ | 7.81.0 | ✅ | Latest stable version |
| build-essential | Any | 12.9ubuntu3 | ✅ | Development tools |

## Python ML/AI Packages

### Core ML Libraries
| Component | Required | Installed | Status | Notes |
|-----------|----------|-----------|--------|-------|
| torch | 2.0+ | Pending | 🔄 | To be installed with CUDA |
| transformers | 4.20+ | Pending | 🔄 | To be installed |
| sentence-transformers | 2.0+ | Pending | 🔄 | To be installed |
| numpy | 1.20+ | Pending | 🔄 | To be installed |
| pandas | 1.3+ | Pending | 🔄 | To be installed |

### Web Framework
| Component | Required | Installed | Status | Notes |
|-----------|----------|-----------|--------|-------|
| fastapi | 0.100+ | Pending | 🔄 | To be installed |
| uvicorn | 0.20+ | Pending | 🔄 | To be installed |
| pydantic | 2.0+ | Pending | 🔄 | To be installed |

### Database Clients
| Component | Required | Installed | Status | Notes |
|-----------|----------|-----------|--------|-------|
| psycopg2-binary | 2.9+ | Pending | 🔄 | To be installed |
| redis | 4.0+ | Pending | 🔄 | To be installed |
| chromadb | 0.4.0+ | Pending | 🔄 | To be installed |
| qdrant-client | 1.0+ | Pending | 🔄 | To be installed |

## Network Configuration

### Port Requirements
| Service | Port | Required | Available | Status | Notes |
|---------|------|----------|-----------|--------|-------|
| Ollama | 11434 | Yes | Yes | ✅ | Ready for deployment |
| FastAPI | 7860 | Yes | Yes | ✅ | Ready for deployment |
| FastAPI Alt | 8000 | Optional | Yes | ✅ | Alternative port |
| PostgreSQL | 5432 | Optional | Yes | ✅ | Ready for deployment |
| Redis | 6379 | Optional | Yes | ✅ | Ready for deployment |
| Qdrant | 6333 | Optional | Yes | ✅ | Ready for deployment |

## Installation Status Summary

### ✅ Completed
- Operating system and kernel
- Python 3.10.12 environment
- CUDA 12.9 with NVIDIA TITAN V
- Docker 27.5.1 and docker-compose
- Core development packages
- Network port availability
- System resource allocation

### 🔄 Pending Installation
- Ollama (GPU-accelerated LLM inference)
- FastAPI and web framework packages
- Vector database packages (ChromaDB/Qdrant)
- Data storage packages (PostgreSQL/Redis)
- Python ML/AI packages (torch, transformers, etc.)

### 📋 Installation Priority
1. **High Priority**: Ollama, FastAPI, torch (with CUDA)
2. **Medium Priority**: Vector databases, transformers, sentence-transformers
3. **Low Priority**: PostgreSQL, Redis, monitoring tools

## Version Compatibility Notes

### CUDA Compatibility
- **torch**: Must install CUDA-enabled version for GPU acceleration
- **transformers**: Compatible with CUDA 12.9
- **Ollama**: Requires CUDA 11.0+ (✅ CUDA 12.9 available)

### Python Compatibility
- All packages require Python 3.8+ (✅ Python 3.10.12 available)
- Pydantic v2+ required for FastAPI (✅ Compatible)

### Docker Compatibility
- All services support containerized deployment (✅ Docker 27.5.1 available)
- Docker Compose available for orchestration (✅ 1.29.2 installed)

## Next Steps
1. Install Python ML/AI packages with CUDA support
2. Deploy Ollama for GPU-accelerated inference
3. Configure FastAPI with vector database integration
4. Validate all service interconnections
5. Establish monitoring and logging infrastructure

---

**Last Updated**: 2025-07-04 11:36:00  
**Agent**: deployment-monitor  
**Sprint**: 2.6 - Environment Preparation & Deployment Readiness 