# Docker Deployment Guide

This guide covers deploying PDF Chat Appliance using Docker and Docker Compose.

## Quick Start

### Prerequisites
- Docker Engine 20.10+
- Docker Compose 2.0+
- At least 4GB RAM available for containers

### Basic Deployment
```bash
# Clone the repository
git clone https://github.com/your-org/pdf-chat-appliance.git
cd pdf-chat-appliance

# Create necessary directories
mkdir -p data documents logs

# Start all services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f pdfchat
```

### Access the Application
- **Web Interface**: http://localhost:5000
- **API Health Check**: http://localhost:5000/health
- **Ollama API**: http://localhost:11434
- **ChromaDB API**: http://localhost:8000 (if enabled)

## Service Architecture

### Core Services

#### PDF Chat Appliance (`pdfchat`)
- **Port**: 5000
- **Purpose**: Main application server
- **Features**: PDF ingestion, query processing, REST API
- **Health Check**: `/health` endpoint

#### Ollama (`ollama`)
- **Port**: 11434
- **Purpose**: Local LLM inference
- **Features**: Model management, text generation
- **Health Check**: `/api/tags` endpoint

#### ChromaDB (`chromadb`) - Optional
- **Port**: 8000
- **Purpose**: Vector database for embeddings
- **Features**: Document storage, similarity search
- **Health Check**: `/api/v1/heartbeat` endpoint

#### Nginx (`nginx`) - Optional
- **Ports**: 80, 443
- **Purpose**: Reverse proxy with SSL termination
- **Features**: Rate limiting, security headers, load balancing

## Configuration

### Environment Variables

#### PDF Chat Appliance
```yaml
environment:
  - PYTHONPATH=/app
  - PDFCHAT_CONFIG_FILE=/app/config/default.yaml
  - PDFCHAT_LOG_LEVEL=INFO
```

#### Ollama
```yaml
environment:
  - OLLAMA_HOST=0.0.0.0
  - OLLAMA_ORIGINS=*
```

#### ChromaDB
```yaml
environment:
  - CHROMA_SERVER_HOST=0.0.0.0
  - CHROMA_SERVER_HTTP_PORT=8000
  - CHROMA_SERVER_CORS_ALLOW_ORIGINS=["*"]
```

### Volume Mounts

#### Data Persistence
```yaml
volumes:
  - ./data:/app/data              # Application data
  - ./documents:/app/documents    # PDF storage
  - ./config:/app/config          # Configuration files
  - pdfchat_logs:/app/logs        # Application logs
  - ollama_data:/root/.ollama     # Ollama models
  - chromadb_data:/chroma/chroma  # Vector database
```

## Deployment Scenarios

### Development Environment
```bash
# Use development configuration
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# Access development tools
docker-compose -f docker-compose.yml -f docker-compose.dev.yml exec dev-tools bash
```

### Production Environment
```bash
# Production deployment
docker-compose -f docker-compose.yml up -d

# With custom configuration
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### Minimal Deployment (PDF Chat + Ollama only)
```bash
# Create minimal compose file
cat > docker-compose.minimal.yml <<EOF
version: "3.9"
services:
  pdfchat:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - ./data:/app/data
      - ./documents:/app/documents
    depends_on:
      - ollama
    networks:
      - pdfchat-network

  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    networks:
      - pdfchat-network

volumes:
  ollama_data:

networks:
  pdfchat-network:
    driver: bridge
EOF

# Deploy minimal setup
docker-compose -f docker-compose.minimal.yml up -d
```

## Usage Examples

### Ingest PDFs
```bash
# Using Docker exec
docker-compose exec pdfchat python pdfchat.py ingest /app/documents

# Or mount documents and run locally
docker run --rm -v $(pwd)/documents:/app/documents pdf-chat-appliance python pdfchat.py ingest /app/documents
```

### Query PDFs
```bash
# Health check
curl http://localhost:5000/health

# Query documents
curl -X POST http://localhost:5000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is this document about?", "top_k": 3}'
```

### Manage Ollama Models
```bash
# List models
curl http://localhost:11434/api/tags

# Pull a model
docker-compose exec ollama ollama pull mistral

# Run a model
docker-compose exec ollama ollama run mistral "Hello, world!"
```

## Monitoring and Logs

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f pdfchat
docker-compose logs -f ollama

# Last 100 lines
docker-compose logs --tail=100 pdfchat
```

### Health Checks
```bash
# Check service health
docker-compose ps

# Manual health check
curl http://localhost:5000/health
curl http://localhost:11434/api/tags
```

### Resource Usage
```bash
# Container resource usage
docker stats

# Disk usage
docker system df
```

## Troubleshooting

### Common Issues

#### Service Won't Start
```bash
# Check logs
docker-compose logs pdfchat

# Check container status
docker-compose ps

# Restart service
docker-compose restart pdfchat
```

#### Port Conflicts
```bash
# Check what's using the port
sudo netstat -tlnp | grep :5000

# Use different ports
docker-compose up -d -p 5001:5000
```

#### Memory Issues
```bash
# Check memory usage
docker stats

# Increase memory limits in docker-compose.yml
services:
  pdfchat:
    deploy:
      resources:
        limits:
          memory: 2G
```

#### Permission Issues
```bash
# Fix volume permissions
sudo chown -R $USER:$USER data documents logs

# Or run with proper user
services:
  pdfchat:
    user: "1000:1000"
```

### Debugging

#### Interactive Shell
```bash
# Access container shell
docker-compose exec pdfchat bash

# Run commands inside container
docker-compose exec pdfchat python pdfchat.py config show
```

#### Development Mode
```bash
# Run with debug logging
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

# Attach debugger
docker-compose -f docker-compose.yml -f docker-compose.dev.yml exec pdfchat python -m debugpy --listen 0.0.0.0:5678 pdfchat.py serve
```

## Security Considerations

### Network Security
- Use internal Docker networks
- Expose only necessary ports
- Implement rate limiting via Nginx

### Data Security
- Use named volumes for sensitive data
- Implement proper backup strategies
- Consider encryption for data at rest

### Access Control
- Use environment variables for secrets
- Implement authentication if needed
- Regular security updates

## Backup and Recovery

### Backup Strategy
```bash
# Backup data volumes
docker run --rm -v pdfchat_logs:/data -v $(pwd)/backups:/backup alpine tar czf /backup/pdfchat_logs.tar.gz -C /data .
docker run --rm -v ollama_data:/data -v $(pwd)/backups:/backup alpine tar czf /backup/ollama_data.tar.gz -C /data .
```

### Recovery
```bash
# Restore from backup
docker run --rm -v pdfchat_logs:/data -v $(pwd)/backups:/backup alpine tar xzf /backup/pdfchat_logs.tar.gz -C /data
```

## Performance Tuning

### Resource Limits
```yaml
services:
  pdfchat:
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1.0'
        reservations:
          memory: 1G
          cpus: '0.5'
```

### Scaling
```bash
# Scale PDF Chat service
docker-compose up -d --scale pdfchat=3

# Use load balancer
docker-compose up -d nginx
```

## Updates and Maintenance

### Update Application
```bash
# Pull latest changes
git pull

# Rebuild and restart
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Update Dependencies
```bash
# Update requirements
pip freeze > requirements.txt

# Rebuild with new requirements
docker-compose build --no-cache pdfchat
docker-compose up -d
```

### Cleanup
```bash
# Remove unused containers
docker container prune

# Remove unused images
docker image prune

# Remove unused volumes
docker volume prune

# Full cleanup
docker system prune -a
``` 