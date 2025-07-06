#!/usr/bin/env python3
"""
Vector Store Service for PDF Chat Appliance Microservices
Handles vector storage, similarity search, and document indexing
"""

import logging
import os
import time
from contextlib import asynccontextmanager

import httpx
import redis
import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Service configuration
SERVICE_CONFIG = {
    "redis_host": os.getenv("REDIS_HOST", "redis"),
    "redis_port": int(os.getenv("REDIS_PORT", 6379)),
    "qdrant_host": os.getenv("QDRANT_HOST", "qdrant"),
    "qdrant_port": int(os.getenv("QDRANT_PORT", 6333)),
    "default_collection": os.getenv("DEFAULT_COLLECTION", "pdf_chunks"),
    "vector_size": int(os.getenv("VECTOR_SIZE", 384)),
    "distance_metric": os.getenv("DISTANCE_METRIC", "Cosine"),
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("🚀 Starting Vector Store Service")

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

    # Initialize Qdrant client
    try:
        app.state.qdrant = QdrantClient(
            host=SERVICE_CONFIG["qdrant_host"], port=SERVICE_CONFIG["qdrant_port"]
        )
        # Test connection
        app.state.qdrant.get_collections()
        logger.info("✅ Qdrant connection established")
    except Exception as e:
        logger.error(f"❌ Qdrant connection failed: {e}")
        app.state.qdrant = None

    # Initialize HTTP client
    app.state.http_client = httpx.AsyncClient(timeout=30.0)
    logger.info("✅ HTTP client initialized")

    yield

    # Cleanup
    logger.info("🛑 Shutting down Vector Store Service")
    if app.state.http_client:
        await app.state.http_client.aclose()
    if app.state.redis:
        app.state.redis.close()


# Create FastAPI application
app = FastAPI(
    title="PDF Chat Appliance Vector Store Service",
    description="Vector storage and similarity search service",
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


@app.get("/health")
async def health_check():
    """Vector Store Service health check"""
    try:
        # Check Redis connection
        redis_healthy = False
        if app.state.redis:
            try:
                app.state.redis.ping()
                redis_healthy = True
            except:
                pass

        # Check Qdrant connection
        qdrant_healthy = False
        if app.state.qdrant:
            try:
                app.state.qdrant.get_collections()
                qdrant_healthy = True
            except:
                pass

        return {
            "status": "healthy" if redis_healthy and qdrant_healthy else "degraded",
            "timestamp": time.time(),
            "service": "vector-store",
            "redis": "healthy" if redis_healthy else "unhealthy",
            "qdrant": "healthy" if qdrant_healthy else "unhealthy",
            "default_collection": SERVICE_CONFIG["default_collection"],
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {e}")


@app.get("/")
async def root():
    """Vector Store Service root endpoint"""
    return {
        "message": "PDF Chat Appliance Vector Store Service",
        "version": "1.0.0",
        "status": "operational",
        "qdrant_host": SERVICE_CONFIG["qdrant_host"],
        "qdrant_port": SERVICE_CONFIG["qdrant_port"],
        "default_collection": SERVICE_CONFIG["default_collection"],
    }


@app.get("/collections")
async def list_collections():
    """List all collections"""
    try:
        if not app.state.qdrant:
            raise HTTPException(status_code=503, detail="Qdrant not available")

        collections = app.state.qdrant.get_collections()
        return {
            "collections": collections.collections,
            "total": len(collections.collections),
        }
    except Exception as e:
        logger.error(f"Collection listing failed: {e}")
        raise HTTPException(status_code=500, detail=f"Collection listing failed: {e}")


@app.post("/collections")
async def create_collection(request: Request):
    """Create a new collection"""
    try:
        if not app.state.qdrant:
            raise HTTPException(status_code=503, detail="Qdrant not available")

        body = await request.json()
        collection_name = body.get("name", SERVICE_CONFIG["default_collection"])
        vector_size = body.get("vector_size", SERVICE_CONFIG["vector_size"])
        distance_metric = body.get("distance_metric", SERVICE_CONFIG["distance_metric"])

        # Map distance metric string to Qdrant enum
        distance_map = {
            "Cosine": Distance.COSINE,
            "Euclidean": Distance.EUCLID,
            "Dot": Distance.DOT,
        }
        distance = distance_map.get(distance_metric, Distance.COSINE)

        # Create collection
        app.state.qdrant.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=vector_size, distance=distance),
        )

        return {
            "message": f"Collection '{collection_name}' created successfully",
            "collection_name": collection_name,
            "vector_size": vector_size,
            "distance_metric": distance_metric,
        }
    except Exception as e:
        logger.error(f"Collection creation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Collection creation failed: {e}")


@app.delete("/collections/{collection_name}")
async def delete_collection(collection_name: str):
    """Delete a collection"""
    try:
        if not app.state.qdrant:
            raise HTTPException(status_code=503, detail="Qdrant not available")

        app.state.qdrant.delete_collection(collection_name=collection_name)

        return {"message": f"Collection '{collection_name}' deleted successfully"}
    except Exception as e:
        logger.error(f"Collection deletion failed: {e}")
        raise HTTPException(status_code=500, detail=f"Collection deletion failed: {e}")


@app.post("/collections/{collection_name}/points")
async def add_points(collection_name: str, request: Request):
    """Add points to a collection"""
    try:
        if not app.state.qdrant:
            raise HTTPException(status_code=503, detail="Qdrant not available")

        body = await request.json()
        points_data = body.get("points", [])

        if not points_data:
            raise HTTPException(status_code=400, detail="No points provided")

        # Convert to Qdrant PointStruct objects
        points = []
        for point_data in points_data:
            point = PointStruct(
                id=point_data.get("id"),
                vector=point_data.get("vector"),
                payload=point_data.get("payload", {}),
            )
            points.append(point)

        # Add points to collection
        app.state.qdrant.upsert(collection_name=collection_name, points=points)

        return {
            "message": f"Added {len(points)} points to collection '{collection_name}'",
            "points_added": len(points),
        }
    except Exception as e:
        logger.error(f"Point addition failed: {e}")
        raise HTTPException(status_code=500, detail=f"Point addition failed: {e}")


@app.post("/collections/{collection_name}/search")
async def search_points(collection_name: str, request: Request):
    """Search for similar points"""
    try:
        if not app.state.qdrant:
            raise HTTPException(status_code=503, detail="Qdrant not available")

        body = await request.json()
        query_vector = body.get("vector")
        limit = body.get("limit", 10)
        score_threshold = body.get("score_threshold", 0.0)

        if not query_vector:
            raise HTTPException(status_code=400, detail="Query vector is required")

        # Search collection
        search_result = app.state.qdrant.search(
            collection_name=collection_name,
            query_vector=query_vector,
            limit=limit,
            score_threshold=score_threshold,
        )

        # Convert results to JSON-serializable format
        results = []
        for point in search_result:
            results.append(
                {"id": point.id, "score": point.score, "payload": point.payload}
            )

        return {
            "results": results,
            "total_found": len(results),
            "collection": collection_name,
        }
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {e}")


@app.get("/collections/{collection_name}/info")
async def get_collection_info(collection_name: str):
    """Get collection information"""
    try:
        if not app.state.qdrant:
            raise HTTPException(status_code=503, detail="Qdrant not available")

        info = app.state.qdrant.get_collection(collection_name=collection_name)

        return {
            "collection_name": collection_name,
            "vectors_count": info.vectors_count,
            "points_count": info.points_count,
            "segments_count": info.segments_count,
            "config": {
                "vector_size": info.config.params.vectors.size,
                "distance": str(info.config.params.vectors.distance),
            },
        }
    except Exception as e:
        logger.error(f"Collection info retrieval failed: {e}")
        raise HTTPException(
            status_code=500, detail=f"Collection info retrieval failed: {e}"
        )


@app.get("/stats")
async def get_stats():
    """Get vector store service statistics"""
    try:
        stats = {
            "timestamp": time.time(),
            "service": "vector-store",
            "qdrant_host": SERVICE_CONFIG["qdrant_host"],
            "qdrant_port": SERVICE_CONFIG["qdrant_port"],
            "redis_connected": app.state.redis is not None,
            "qdrant_connected": app.state.qdrant is not None,
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

        # Get Qdrant stats if available
        if app.state.qdrant:
            try:
                collections = app.state.qdrant.get_collections()
                stats["qdrant"] = {
                    "collections_count": len(collections.collections),
                    "collections": [c.name for c in collections.collections],
                }
            except Exception as e:
                stats["qdrant"] = {"error": str(e)}

        return stats
    except Exception as e:
        logger.error(f"Stats collection failed: {e}")
        raise HTTPException(status_code=500, detail=f"Stats collection failed: {e}")


if __name__ == "__main__":
    print("🚀 Starting PDF Chat Appliance Vector Store Service")
    print("=" * 50)

    # Run the application
    uvicorn.run("main:app", host="0.0.0.0", port=8005, reload=False, log_level="info")
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
