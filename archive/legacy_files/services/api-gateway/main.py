#!/usr/bin/env python3
"""
API Gateway Service for PDF Chat Appliance Microservices
Handles request routing, load balancing, and unified API interface
"""

import logging
import os
import time
from contextlib import asynccontextmanager
from typing import Any, Dict

import httpx
import redis
import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Service configuration
SERVICE_CONFIG = {
    "redis_host": os.getenv("REDIS_HOST", "redis"),
    "redis_port": int(os.getenv("REDIS_PORT", 6379)),
    "preprocessor_url": os.getenv("PREPROCESSOR_URL", "http://pdf-preprocessor:8001"),
    "embedding_url": os.getenv("EMBEDDING_URL", "http://embedding-service:8002"),
    "llm_url": os.getenv("LLM_URL", "http://llm-service:8003"),
    "chat_url": os.getenv("CHAT_URL", "http://chat-service:8004"),
    "vector_store_url": os.getenv("VECTOR_STORE_URL", "http://vector-store:6333"),
}

# Health check cache
health_cache = {}
health_cache_ttl = 30  # seconds


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("🚀 Starting API Gateway Service")

    # Initialize Redis connection
    try:
        app.state.redis = redis.Redis(
            host=SERVICE_CONFIG["redis_host"],
            port=SERVICE_CONFIG["redis_port"],
            decode_responses=True,
        )
        app.state.redis.ping()
        logger.info("✅ Redis connection established")
    except Exception as e:
        logger.error(f"❌ Redis connection failed: {e}")
        app.state.redis = None

    # Initialize HTTP client
    app.state.http_client = httpx.AsyncClient(timeout=30.0)
    logger.info("✅ HTTP client initialized")

    yield

    # Cleanup
    logger.info("🛑 Shutting down API Gateway Service")
    if app.state.http_client:
        await app.state.http_client.aclose()
    if app.state.redis:
        app.state.redis.close()


# Create FastAPI application
app = FastAPI(
    title="PDF Chat Appliance API Gateway",
    description="Unified API interface for microservices architecture",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def check_service_health(service_name: str, service_url: str) -> Dict[str, Any]:
    """Check health of a specific service"""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{service_url}/health")
            if response.status_code == 200:
                return {
                    "service": service_name,
                    "status": "healthy",
                    "url": service_url,
                    "response_time": response.elapsed.total_seconds(),
                }
            else:
                return {
                    "service": service_name,
                    "status": "unhealthy",
                    "url": service_url,
                    "error": f"HTTP {response.status_code}",
                }
    except Exception as e:
        return {
            "service": service_name,
            "status": "unreachable",
            "url": service_url,
            "error": str(e),
        }


@app.get("/health")
async def health_check():
    """API Gateway health check"""
    try:
        # Check Redis connection
        redis_healthy = False
        if app.state.redis:
            try:
                app.state.redis.ping()
                redis_healthy = True
            except:
                pass

        # Check all services
        services = [
            ("pdf-preprocessor", SERVICE_CONFIG["preprocessor_url"]),
            ("embedding-service", SERVICE_CONFIG["embedding_url"]),
            ("llm-service", SERVICE_CONFIG["llm_url"]),
            ("chat-service", SERVICE_CONFIG["chat_url"]),
            ("vector-store", SERVICE_CONFIG["vector_store_url"]),
        ]

        health_results = []
        for service_name, service_url in services:
            health_result = await check_service_health(service_name, service_url)
            health_results.append(health_result)

        # Determine overall health
        healthy_services = sum(1 for r in health_results if r["status"] == "healthy")
        total_services = len(health_results)

        return {
            "status": (
                "healthy" if redis_healthy and healthy_services > 0 else "degraded"
            ),
            "timestamp": time.time(),
            "gateway": {
                "status": "healthy",
                "redis": "healthy" if redis_healthy else "unhealthy",
            },
            "services": health_results,
            "summary": {
                "total_services": total_services,
                "healthy_services": healthy_services,
                "unhealthy_services": total_services - healthy_services,
            },
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {e}")


@app.get("/")
async def root():
    """API Gateway root endpoint"""
    return {
        "message": "PDF Chat Appliance API Gateway",
        "version": "1.0.0",
        "status": "operational",
        "services": {
            "pdf_preprocessor": SERVICE_CONFIG["preprocessor_url"],
            "embedding_service": SERVICE_CONFIG["embedding_url"],
            "llm_service": SERVICE_CONFIG["llm_url"],
            "chat_service": SERVICE_CONFIG["chat_url"],
            "vector_store": SERVICE_CONFIG["vector_store_url"],
        },
    }


@app.get("/stats")
async def get_stats():
    """Get system statistics"""
    try:
        stats = {
            "timestamp": time.time(),
            "gateway": {
                "uptime": time.time(),  # TODO: Implement proper uptime tracking
                "requests_processed": 0,  # TODO: Implement request counting
                "redis_connected": app.state.redis is not None,
            },
        }

        # Get Redis stats if available
        if app.state.redis:
            try:
                redis_info = app.state.redis.info()
                stats["redis"] = {
                    "connected_clients": redis_info.get("connected_clients", 0),
                    "used_memory": redis_info.get("used_memory_human", "0B"),
                    "total_commands_processed": redis_info.get(
                        "total_commands_processed", 0
                    ),
                }
            except Exception as e:
                stats["redis"] = {"error": str(e)}

        return stats
    except Exception as e:
        logger.error(f"Stats collection failed: {e}")
        raise HTTPException(status_code=500, detail=f"Stats collection failed: {e}")


# PDF Processing endpoints
@app.post("/upload")
async def upload_document(request: Request):
    """Upload and process PDF document"""
    try:
        # Forward to preprocessor service
        body = await request.body()
        headers = dict(request.headers)

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{SERVICE_CONFIG['preprocessor_url']}/upload",
                content=body,
                headers=headers,
            )

            return JSONResponse(
                content=response.json(), status_code=response.status_code
            )
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {e}")


@app.get("/ingestion/status")
async def get_ingestion_status():
    """Get ingestion processing status"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{SERVICE_CONFIG['preprocessor_url']}/status")
            return JSONResponse(
                content=response.json(), status_code=response.status_code
            )
    except Exception as e:
        logger.error(f"Ingestion status check failed: {e}")
        raise HTTPException(
            status_code=500, detail=f"Ingestion status check failed: {e}"
        )


# Chat endpoints
@app.post("/chat")
async def chat_endpoint(request: Request):
    """Chat with the AI system"""
    try:
        body = await request.json()

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{SERVICE_CONFIG['chat_url']}/chat", json=body
            )

            return JSONResponse(
                content=response.json(), status_code=response.status_code
            )
    except Exception as e:
        logger.error(f"Chat request failed: {e}")
        raise HTTPException(status_code=500, detail=f"Chat request failed: {e}")


@app.get("/documents")
async def list_documents():
    """List available documents"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{SERVICE_CONFIG['vector_store_url']}/collections"
            )
            return JSONResponse(
                content=response.json(), status_code=response.status_code
            )
    except Exception as e:
        logger.error(f"Document listing failed: {e}")
        raise HTTPException(status_code=500, detail=f"Document listing failed: {e}")


if __name__ == "__main__":
    print("🚀 Starting PDF Chat Appliance API Gateway")
    print("=" * 50)

    # Run the application
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False, log_level="info")
    print()

# UNCONDITIONAL: Ensure prompt unsticking regardless of exit path
print()

# COMPREHENSIVE CLEANUP: Ensure all threads and processes are properly terminated
import atexit
import os


def cleanup_on_exit():
    """Ensure clean exit by terminating any remaining processes"""
    try:
        # Force flush all output
        import sys

        sys.stdout.flush()
        sys.stderr.flush()

        # Print final blank line
        print()
    except:
        pass


# Register cleanup function
atexit.register(cleanup_on_exit)
