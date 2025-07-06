Generated: 2025-01-27 23:59:00

# PDF Chat Appliance API Documentation

## Overview

The PDF Chat Appliance provides a comprehensive REST API for document ingestion, querying, and intelligent chunk flow monitoring. The API is built on Flask and supports enterprise-scale multi-vendor documentation processing.

## Base URL

```
http://localhost:5000
```

## Authentication

Currently, the API does not require authentication for local development. For production deployments, consider implementing API key authentication.

## Endpoints

### Health Check

**GET** `/health`

Check the health status of the API server.

**Response:**

```json
{
  "status": "healthy",
  "timestamp": "2025-07-03T12:45:52.123456",
  "version": "1.0.0"
}
```

### Document Management

**GET** `/documents`

List all ingested documents with metadata.

**Response:**

```json
{
  "status": "success",
  "documents": [
    {
      "name": "sample-small.pdf",
      "size_mb": 0.15,
      "uploaded": 1730571234.567,
      "type": "PDF"
    }
  ],
  "count": 1,
  "timestamp": "2025-07-03T12:45:52.123456"
}
```

### Query Interface

**POST** `/query`

Submit a question about ingested documents.

**Request Body:**

```json
{
  "question": "What are the key features of VMware vSphere?",
  "context_length": 2000,
  "temperature": 0.7
}
```

**Response:**

```json
{
  "answer": "VMware vSphere provides virtualization capabilities...",
  "sources": [
    {
      "document": "vmware-vsphere-guide.pdf",
      "page": 15,
      "content": "vSphere includes ESXi hypervisor..."
    }
  ],
  "confidence": 0.85,
  "processing_time": 2.34
}
```

### Document Upload

**POST** `/upload`

Upload a new PDF document for ingestion.

**Request:** Multipart form data with PDF file.

**Response:**

```json
{
  "status": "success",
  "filename": "uploaded-document.pdf",
  "size_mb": 2.5,
  "message": "Document uploaded successfully"
}
```

### Context Retrieval

**POST** `/context`

Get relevant context for a query without generating a response.

**Request Body:**

```json
{
  "question": "How to configure network settings?",
  "max_results": 5
}
```

**Response:**

```json
{
  "context": "Network configuration involves...",
  "sources": [...],
  "relevance_score": 0.92
}
```

## Intelligent Chunk Flow Monitoring

### Ingestion Status

**GET** `/ingestion/status`

Get current ingestion pipeline status and performance metrics.

**Response:**

```json
{
  "pipeline_status": "operational",
  "last_ingestion": "2025-07-03T12:30:00.000000",
  "total_documents": 15,
  "total_chunks": 1250,
  "total_tokens": 45000,
  "performance_metrics": {
    "avg_processing_time": 8.5,
    "avg_chunks_per_doc": 83.3,
    "avg_tokens_per_doc": 3000
  },
  "chunking_strategies_used": {
    "Small Simple": 5,
    "Medium Standard": 8,
    "Large Complex": 2
  },
  "system_health": {
    "qdrant_connected": true,
    "embedding_model_loaded": true,
    "memory_usage_mb": 512.5,
    "cpu_usage_percent": 15.2
  },
  "timestamp": "2025-07-03T12:45:52.123456"
}
```

### Chunk Flow Metrics

**GET** `/ingestion/chunk-flow`

Get detailed chunk flow routing metrics and strategy analysis.

**Response:**

```json
{
  "strategies_used": {
    "Small Simple": {
      "count": 5,
      "complexity_levels": ["low", "low", "low", "low", "low"],
      "avg_processing_time": 3.2
    },
    "Medium Standard": {
      "count": 8,
      "complexity_levels": ["medium", "medium", "medium", "medium", "medium", "medium", "medium", "medium"],
      "avg_processing_time": 7.8
    }
  },
  "performance_by_strategy": {
    "Small Simple": {
      "avg_chunks_per_doc": 25,
      "avg_tokens_per_doc": 1200,
      "efficiency_score": 0.95
    }
  },
  "recent_ingestions": [
    {
      "document": "sample-small.pdf",
      "strategy": "Small Simple",
      "processing_time": 7.23,
      "chunks_created": 18,
      "tokens_processed": 4055
    }
  ],
  "system_recommendations": [
    "Strategy 'Medium Standard' is used 61.5% of the time - consider optimizing for this document type"
  ],
  "timestamp": "2025-07-03T12:45:52.123456"
}
```

### Strategy Optimization

**POST** `/ingestion/optimize`

Optimize chunking strategy based on document characteristics.

**Request Body:**

```json
{
  "document_path": "./uploads/large-document.pdf"
}
```

**Response:**

```json
{
  "document_path": "./uploads/large-document.pdf",
  "document_size_mb": 45.2,
  "recommended_strategy": {
    "name": "Large Complex",
    "chunk_size": 768,
    "chunk_overlap": 96,
    "complexity_level": "high",
    "max_workers": 6
  },
  "analysis": {
    "content_length": 1250000,
    "estimated_chunks": 1627,
    "estimated_tokens": 312500
  },
  "timestamp": "2025-07-03T12:45:52.123456"
}
```

### Batch Ingestion

**POST** `/ingestion/batch`

Batch ingest multiple documents with intelligent chunk flow routing.

**Request Body:**

```json
{
  "document_paths": [
    "./uploads/doc1.pdf",
    "./uploads/doc2.pdf",
    "./uploads/doc3.pdf"
  ],
  "max_documents": 10
}
```

**Response:**

```json
{
  "status": "completed",
  "documents_processed": 3,
  "total_time": 25.7,
  "total_chunks": 245,
  "total_tokens": 12500,
  "performance_summary": {
    "avg_processing_time": 8.57,
    "avg_chunks_per_doc": 81.7,
    "avg_tokens_per_doc": 4166.7
  },
  "strategy_breakdown": {
    "Small Simple": {
      "count": 1,
      "total_time": 7.23,
      "total_chunks": 18
    },
    "Medium Standard": {
      "count": 2,
      "total_time": 18.47,
      "total_chunks": 227
    }
  },
  "timestamp": "2025-07-03T12:45:52.123456"
}
```

## System Statistics

**GET** `/stats`

Get system statistics and performance metrics.

**Response:**

```json
{
  "documents_processed": 15,
  "total_chunks": 1250,
  "total_tokens": 45000,
  "avg_response_time": 2.34,
  "system_uptime": 86400,
  "memory_usage_mb": 512.5,
  "cpu_usage_percent": 15.2
}
```

## Error Handling

All endpoints return appropriate HTTP status codes:

- **200**: Success
- **400**: Bad Request (invalid input)
- **404**: Not Found (document not found)
- **500**: Internal Server Error

Error responses include a descriptive message:

```json
{
  "error": "Document not found",
  "guidance": "Please check the document path and try again",
  "details": "File './uploads/missing.pdf' does not exist"
}
```

## Chunking Strategies

The system uses intelligent chunk flow routing with four adaptive strategies:

### Small Simple

- **Chunk Size:** 256 tokens
- **Overlap:** 32 tokens
- **Workers:** 2
- **Use Case:** Small, simple documents (< 5MB)

### Medium Standard

- **Chunk Size:** 512 tokens
- **Overlap:** 64 tokens
- **Workers:** 4
- **Use Case:** Standard documents (5-20MB)

### Large Complex

- **Chunk Size:** 768 tokens
- **Overlap:** 96 tokens
- **Workers:** 6
- **Use Case:** Large, complex documents (20-100MB)

### Enterprise Massive

- **Chunk Size:** 1024 tokens
- **Overlap:** 128 tokens
- **Workers:** 8
- **Use Case:** Enterprise-scale documents (> 100MB)

## Performance Monitoring

The API includes comprehensive performance monitoring:

- **Real-time metrics** for processing time, memory usage, and CPU utilization
- **Strategy analysis** to optimize chunking based on document characteristics
- **Batch processing** for efficient handling of multiple documents
- **System health** monitoring for Qdrant and embedding models

## Rate Limiting

Currently, no rate limiting is implemented. For production deployments, consider implementing rate limiting based on your requirements.

## CORS

CORS is enabled for local development. Configure appropriate CORS settings for production deployments.

---

*Last Updated: 2025-07-03*
*Version: 1.0.0*
