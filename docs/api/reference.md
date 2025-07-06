# API Reference

Complete reference documentation for the PDF Chat Appliance API v1.3.0.

## Base URL

```
Development: http://localhost:5000
Production:  https://api.pdfchat-appliance.com
```

## Authentication

Currently, the API supports basic authentication. API keys may be required for production use.

## Endpoints

### Health Check

#### `GET /health`

Check the health status of the PDF Chat Appliance service.

**Response**

```json
{
  "status": "healthy",
  "timestamp": 1640995200.0,
  "version": "1.3.0",
  "uptime": 3600.0
}
```

**Response Fields**

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | Health status of the service |
| `timestamp` | float | Current timestamp |
| `version` | string | API version |
| `uptime` | float | Service uptime in seconds |

**Example**

```bash
curl -X GET "http://localhost:5000/health"
```

---

### Query PDF Documents

#### `POST /query`

Query PDF documents using natural language with semantic search and LLM-powered responses.

**Request Body**

```json
{
  "query": "How do I install VMware vSphere?",
  "user_id": "user123",
  "document_id": "vmware-docs.pdf",
  "max_results": 5
}
```

**Request Fields**

| Field | Type | Required | Description | Default |
|-------|------|----------|-------------|---------|
| `query` | string | Yes | The query text to search for in PDF documents | - |
| `user_id` | string | No | User identifier for chat history | "default" |
| `document_id` | string | No | Specific document ID to search in | null |
| `max_results` | integer | No | Maximum number of results to return (1-20) | 5 |

**Response**

```json
{
  "answer": "To install VMware vSphere, you need to...",
  "sources": [
    {
      "content": "VMware vSphere installation requires...",
      "metadata": {
        "file_name": "vmware-docs.pdf",
        "page": 15
      },
      "score": 0.95
    }
  ],
  "query_analysis": {
    "vendors": ["VMware"],
    "is_cross_vendor": false,
    "query_type": "installation"
  },
  "processing_time": 2.5,
  "fallback_answer": null
}
```

**Response Fields**

| Field | Type | Description |
|-------|------|-------------|
| `answer` | string | The generated answer to the query |
| `sources` | array | Source documents used to generate the answer |
| `sources[].content` | string | Text content from the source document |
| `sources[].metadata` | object | Metadata about the source document |
| `sources[].score` | float | Similarity score for the result |
| `query_analysis` | object | Analysis of the query content |
| `query_analysis.vendors` | array | Vendor technologies mentioned in the query |
| `query_analysis.is_cross_vendor` | boolean | Whether the query involves multiple vendors |
| `query_analysis.query_type` | string | Type of query (installation, integration, troubleshooting, general) |
| `processing_time` | float | Time taken to process the query in seconds |
| `fallback_answer` | string | Fallback answer for cross-vendor queries |

**Example**

```bash
curl -X POST "http://localhost:5000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How do I install VMware vSphere?",
    "user_id": "user123",
    "max_results": 5
  }'
```

---

### Ingest PDF Documents

#### `POST /ingest`

Ingest PDF documents for querying with background processing.

**Request Body**

No request body required.

**Response**

```json
{
  "status": "success",
  "message": "Document ingestion started successfully",
  "documents_processed": null
}
```

**Response Fields**

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | Ingestion status |
| `message` | string | Ingestion result message |
| `documents_processed` | integer | Number of documents processed (null for background processing) |

**Example**

```bash
curl -X POST "http://localhost:5000/ingest"
```

---

### List Available Documents

#### `GET /documents`

List all available PDF documents that can be queried.

**Response**

```json
{
  "documents": [
    {
      "name": "vmware-docs.pdf",
      "path": "/app/documents/vmware-docs.pdf",
      "size": 2048576,
      "modified": 1640995200.0
    }
  ]
}
```

**Response Fields**

| Field | Type | Description |
|-------|------|-------------|
| `documents` | array | List of available PDF documents |
| `documents[].name` | string | Document filename |
| `documents[].path` | string | Full path to the document |
| `documents[].size` | integer | Document size in bytes |
| `documents[].modified` | float | Last modification timestamp |

**Example**

```bash
curl -X GET "http://localhost:5000/documents"
```

---

## Error Responses

All endpoints may return the following error responses:

### 400 Bad Request

```json
{
  "detail": "Validation error message"
}
```

### 500 Internal Server Error

```json
{
  "detail": "Internal server error message"
}
```

## Rate Limits

- **Default**: 100 requests per minute per IP
- **Burst**: 10 requests per second
- **Documentation**: See [Rate Limits](./rate-limits.md) for details

## Status Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 429 | Too Many Requests |
| 500 | Internal Server Error |
| 503 | Service Unavailable |

---

**Last Updated**: 2025-01-27  
**API Version**: 1.3.0 