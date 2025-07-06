# Microservices Pipeline Architecture

> **PDF Chat Appliance - Enterprise-Scale Microservices Design**
>
> Last updated: 2025-07-03

---

## 🎯 Architecture Overview

### **Current Monolith Problems:**

- Single point of failure in `pdfchat` container
- Resource contention (4 CPU, 8GB RAM for all operations)
- No parallel processing capabilities
- Limited horizontal scaling
- Mixed responsibilities (API, ingestion, embedding)

### **Microservices Solution:**

- **Horizontal Scaling:** Scale individual services independently
- **Fault Tolerance:** Isolated failures don't bring down entire system
- **Resource Optimization:** Dedicated resources per service
- **Parallel Processing:** Queue-based asynchronous processing
- **Enterprise Ready:** Production-grade reliability and monitoring

---

## 🏭 Service Architecture

### **1. 📄 Pre-Processing Service (`pdf-preprocessor`)**

```yaml
Service: pdf-preprocessor
Purpose: PDF parsing, format detection, initial chunking
Technology: Python + PyMuPDF + FastAPI
Resources: 2 CPU, 4GB RAM
Scaling: Horizontal (multiple workers)
Input: Raw PDF files
Output: Structured text chunks + metadata
```

**Responsibilities:**

- PDF text extraction with PyMuPDF
- Document format detection and validation
- Initial semantic chunking
- Metadata extraction (pages, size, structure)
- Error handling and retry logic

### **2. 🔄 Ingestion Orchestrator (`ingestion-orchestrator`)**

```yaml
Service: ingestion-orchestrator
Purpose: Queue management, workflow orchestration
Technology: Python + Celery + Redis + FastAPI
Resources: 1 CPU, 2GB RAM
Scaling: Single instance (orchestrator)
Input: Processing requests
Output: Orchestrated workflow
```

**Responsibilities:**

- Queue management (Redis-based)
- Workflow orchestration
- Progress tracking
- Error recovery and retry logic
- Load balancing across workers

### **3. Embedding Service (`embedding-service`)**

```yaml
Service: embedding-service
Purpose: Vector embedding generation
Technology: Python + sentence-transformers + FastAPI
Resources: 2 CPU, 6GB RAM
Scaling: Horizontal (multiple workers)
Input: Text chunks
Output: Vector embeddings
```

**Responsibilities:**

- Text chunk embedding with sentence-transformers
- Batch processing optimization
- Model management and caching
- Embedding quality validation
- Multi-model support (nomic-embed-text-v1.5, etc.)

### **4. Vector Storage Service (`vector-store`)**

```yaml
Service: vector-store
Purpose: Optimized vector database
Technology: Qdrant + Python API
Resources: 2 CPU, 8GB RAM
Scaling: Single instance (with clustering)
Input: Vector embeddings + metadata
Output: Vector search results
```

**Responsibilities:**

- Vector storage and indexing
- Semantic search optimization
- Collection management
- Backup and recovery
- Performance monitoring

### **5. 🤖 LLM Service (`llm-service`)**

```yaml
Service: llm-service
Purpose: Large Language Model inference
Technology: Ollama + Python API
Resources: 4 CPU, 12GB RAM
Scaling: Horizontal (multiple instances)
Input: Context + queries
Output: Generated responses
```

**Responsibilities:**

- LLM model management (Mistral, Phi3, etc.)
- Context-aware response generation
- Prompt engineering and optimization
- Response quality validation
- Multi-model load balancing

### **6. 🌐 API Gateway (`api-gateway`)**

```yaml
Service: api-gateway
Purpose: Unified API interface
Technology: FastAPI + Nginx
Resources: 1 CPU, 2GB RAM
Scaling: Horizontal (load balancer)
Input: Client requests
Output: Service responses
```

**Responsibilities:**

- Request routing and load balancing
- Authentication and authorization
- Rate limiting and throttling
- Request/response transformation
- API documentation (OpenAPI/Swagger)

### **7. 💬 Chat Service (`chat-service`)**

```yaml
Service: chat-service
Purpose: Conversational AI interface
Technology: Python + FastAPI + WebSocket
Resources: 2 CPU, 4GB RAM
Scaling: Horizontal (multiple instances)
Input: User messages
Output: AI responses
```

**Responsibilities:**

- Conversation management
- Context window management
- Response streaming
- Chat history persistence
- Real-time communication

### **8. 📊 Monitoring Service (`monitoring-service`)**

```yaml
Service: monitoring-service
Purpose: System monitoring and observability
Technology: Prometheus + Grafana + Python
Resources: 1 CPU, 2GB RAM
Scaling: Single instance
Input: Service metrics
Output: Dashboards and alerts
```

**Responsibilities:**

- Metrics collection and aggregation
- Performance monitoring
- Health checks and alerting
- Log aggregation and analysis
- Capacity planning insights

---

## 🔄 Data Flow Architecture

### **Upload Flow:**

```
Client → API Gateway → Ingestion Orchestrator → Pre-Processing Service → Embedding Service → Vector Storage
```

### **Query Flow:**

```
Client → API Gateway → Chat Service → LLM Service → Vector Storage → Response Generation
```

### **Monitoring Flow:**

```
All Services → Monitoring Service → Dashboards & Alerts
```

---

## Deployment Architecture

### **Development Environment:**

```yaml
Deployment: Docker Compose
Orchestration: Docker Compose
Scaling: Manual (docker-compose scale)
Monitoring: Basic health checks
```

### **Production Environment:**

```yaml
Deployment: Kubernetes
Orchestration: Kubernetes + Helm
Scaling: Horizontal Pod Autoscaler (HPA)
Monitoring: Prometheus + Grafana + AlertManager
Load Balancing: Ingress Controller (Nginx/Traefik)
```

---

## 📈 Scaling Patterns

### **Horizontal Scaling:**

- **Pre-Processing Workers:** Scale based on PDF queue depth
- **Embedding Workers:** Scale based on chunk processing queue
- **LLM Instances:** Scale based on query load
- **Chat Service:** Scale based on concurrent users

### **Vertical Scaling:**

- **Vector Storage:** Increase CPU/RAM for larger datasets
- **LLM Service:** GPU acceleration for faster inference
- **Embedding Service:** More RAM for larger batch processing

### **Auto-Scaling Triggers:**

- CPU utilization > 70%
- Memory utilization > 80%
- Queue depth > 100 items
- Response time > 2 seconds

---

## 🔧 Technology Stack

### **Core Technologies:**

- **Containerization:** Docker
- **Orchestration:** Kubernetes (prod) / Docker Compose (dev)
- **Message Queue:** Redis + Celery
- **Database:** Qdrant (vector) + PostgreSQL (metadata)
- **Monitoring:** Prometheus + Grafana
- **API Gateway:** Nginx / Traefik
- **Load Balancing:** Kubernetes Ingress

### **Service Technologies:**

- **Backend:** Python + FastAPI
- **Embedding:** sentence-transformers + PyMuPDF
- **LLM:** Ollama + custom models
- **Vector DB:** Qdrant
- **Caching:** Redis
- **Logging:** Structured JSON logging

---

## Reliability & Fault Tolerance

### **Circuit Breakers:**

- Service-to-service communication
- External API calls
- Database connections

### **Retry Logic:**

- Exponential backoff
- Maximum retry attempts
- Dead letter queues

### **Health Checks:**

- Liveness probes
- Readiness probes
- Startup probes

### **Backup & Recovery:**

- Automated backups
- Point-in-time recovery
- Disaster recovery procedures

---

## 📊 Performance Targets

### **Throughput:**

- **PDF Processing:** 100+ pages/minute
- **Embedding Generation:** 1000+ chunks/minute
- **Query Response:** < 2 seconds
- **Concurrent Users:** 1000+

### **Availability:**

- **Uptime:** 99.9% (8.76 hours downtime/year)
- **Recovery Time:** < 5 minutes
- **Data Loss:** Zero (RPO = 0)

### **Scalability:**

- **Horizontal Scaling:** 10x current capacity
- **Auto-scaling:** Response time < 2 seconds
- **Load Distribution:** Even across instances

---

## Implementation Roadmap

### **Phase 1: Foundation (Week 1-2)**

- [ ] Service decomposition design
- [ ] Docker Compose microservices setup
- [ ] Basic service communication
- [ ] Health checks and monitoring

### **Phase 2: Core Services (Week 3-4)**

- [ ] Pre-processing service implementation
- [ ] Embedding service implementation
- [ ] Vector storage optimization
- [ ] Queue-based processing

### **Phase 3: Advanced Features (Week 5-6)**

- [ ] LLM service optimization
- [ ] Chat service implementation
- [ ] API gateway setup
- [ ] Load balancing

### **Phase 4: Production Ready (Week 7-8)**

- [ ] Kubernetes deployment
- [ ] Auto-scaling implementation
- [ ] Monitoring and alerting
- [ ] Performance optimization

---

## 💰 Resource Requirements

### **Development Environment:**

- **Total CPU:** 16 cores
- **Total RAM:** 32GB
- **Storage:** 100GB SSD
- **Services:** 8 containers

### **Production Environment:**

- **Total CPU:** 64+ cores
- **Total RAM:** 128GB+
- **Storage:** 1TB+ SSD
- **Services:** 20+ containers
- **Load Balancers:** 2 instances
- **Monitoring:** Dedicated cluster

---

## 🔄 Migration Strategy

### **Blue-Green Deployment:**

1. Deploy new microservices alongside monolith
2. Gradually migrate traffic
3. Validate performance and reliability
4. Decommission monolith

### **Data Migration:**

1. Export existing vector data
2. Migrate to new vector storage
3. Validate data integrity
4. Update service configurations

### **Rollback Plan:**

1. Maintain monolith as backup
2. Quick rollback procedures
3. Data consistency checks
4. Service health validation
