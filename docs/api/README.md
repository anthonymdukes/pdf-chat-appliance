# PDF Chat Appliance API Documentation

Welcome to the PDF Chat Appliance API documentation. This comprehensive guide provides everything you need to integrate with our intelligent PDF document querying system.

## Quick Navigation

- **[API Reference](./reference.md)** - Complete API endpoint documentation
- **[Getting Started](./getting-started.md)** - Quick start guide for new users
- **[Authentication](./authentication.md)** - API authentication and security
- **[Examples](./examples.md)** - Code examples and use cases
- **[Error Handling](./errors.md)** - Error codes and troubleshooting
- **[Rate Limits](./rate-limits.md)** - API usage limits and quotas
- **[Changelog](./changelog.md)** - API version history and changes

## Getting Started

### Base URL
```
Development: http://localhost:5000
Production:  https://api.pdfchat-appliance.com
```

### Interactive Documentation
- **Swagger UI**: `/docs` - Interactive API explorer
- **ReDoc**: `/redoc` - Alternative documentation view
- **OpenAPI Schema**: `/openapi.json` - Machine-readable API specification

## Authentication

Currently, the API supports basic authentication. API keys may be required for production use.

```bash
# Example with curl
curl -X POST "http://localhost:5000/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "How do I install VMware vSphere?"}'
```

## API Endpoints Overview

| Endpoint | Method | Description | Status |
|----------|--------|-------------|--------|
| `/health` | GET | System health check | Active |
| `/query` | POST | Query PDF documents | Active |
| `/ingest` | POST | Ingest PDF documents | Active |
| `/documents` | GET | List available documents | Active |

## Key Features

### Intelligent Query Processing
- **Semantic Search**: Advanced vector-based document search
- **LLM-Powered Responses**: Natural language understanding and generation
- **Vendor Analysis**: Automatic detection of vendor-specific content
- **Cross-Vendor Support**: Integration guidance for multiple technologies

### Document Management
- **PDF Processing**: Automatic text extraction and chunking
- **Metadata Extraction**: Document properties and structure analysis
- **Version Control**: Document versioning and change tracking
- **Batch Operations**: Efficient processing of multiple documents

### Performance & Reliability
- **Async Processing**: Background document ingestion
- **Timeout Handling**: Robust error handling and recovery
- **Caching**: Intelligent response caching for performance
- **Monitoring**: Comprehensive health and performance metrics

## Usage Examples

### Basic Query
```python
import requests

response = requests.post("http://localhost:5000/query", json={
    "query": "How do I install VMware vSphere?",
    "max_results": 5
})

print(response.json())
```

### Document Ingestion
```python
response = requests.post("http://localhost:5000/ingest")
print(f"Ingestion status: {response.json()['status']}")
```

### Health Check
```python
response = requests.get("http://localhost:5000/health")
health = response.json()
print(f"Service status: {health['status']}")
print(f"Uptime: {health['uptime']} seconds")
```

## SDKs and Libraries

### Python
```bash
pip install pdfchat-appliance-client
```

### JavaScript/Node.js
```bash
npm install pdfchat-appliance-client
```

### Go
```bash
go get github.com/pdfchat-appliance/client
```

## Support

- **Documentation**: [docs.pdfchat-appliance.com](https://docs.pdfchat-appliance.com)
- **API Status**: [status.pdfchat-appliance.com](https://status.pdfchat-appliance.com)
- **Support Email**: support@pdfchat-appliance.com
- **GitHub Issues**: [github.com/pdfchat-appliance/issues](https://github.com/pdfchat-appliance/issues)

## Versioning

The API follows semantic versioning (SemVer). The current version is **v1.3.0**.

- **Major versions**: Breaking changes
- **Minor versions**: New features, backward compatible
- **Patch versions**: Bug fixes, backward compatible

## License

This API is licensed under the MIT License. See [LICENSE](../LICENSE) for details.

---

**Last Updated**: 2025-01-27  
**API Version**: 1.3.0  
**Documentation Version**: 1.0.0 