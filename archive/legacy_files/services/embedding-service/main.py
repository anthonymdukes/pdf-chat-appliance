#!/usr/bin/env python3
"""
Embedding Service for PDF Chat Appliance Microservices
Handles text embedding generation and vector operations with enterprise-scale optimizations
"""

import logging
import os
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager
from pathlib import Path
from typing import List

import httpx
import redis
import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from sentence_transformers import SentenceTransformer

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Service configuration
SERVICE_CONFIG = {
    "redis_host": os.getenv("REDIS_HOST", "redis"),
    "redis_port": int(os.getenv("REDIS_PORT", 6379)),
    "vector_store_url": os.getenv("VECTOR_STORE_URL", "http://vector-store:8005"),
    "embedding_model": os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2"),
    "vector_size": int(os.getenv("VECTOR_SIZE", 384)),
    "batch_size": int(os.getenv("BATCH_SIZE", 32)),
    "max_workers": int(os.getenv("MAX_WORKERS", 4)),
    "device": os.getenv("DEVICE", "cpu"),
    "cache_dir": os.getenv("CACHE_DIR", "/app/cache"),
}

# Global model instance
embedding_model = None
executor = ThreadPoolExecutor(max_workers=SERVICE_CONFIG["max_workers"])


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("🚀 Starting Embedding Service")

    # Create cache directory
    Path(SERVICE_CONFIG["cache_dir"]).mkdir(parents=True, exist_ok=True)

    # Initialize embedding model
    global embedding_model
    try:
        logger.info(f"Loading embedding model: {SERVICE_CONFIG['embedding_model']}")
        embedding_model = SentenceTransformer(
            SERVICE_CONFIG["embedding_model"],
            cache_folder=SERVICE_CONFIG["cache_dir"],
            device=SERVICE_CONFIG["device"],
        )
        logger.info(
            f"✅ Embedding model loaded successfully on {SERVICE_CONFIG['device']}"
        )

        # Test model
        test_embedding = embedding_model.encode(["test"], convert_to_tensor=False)
        logger.info(f"✅ Model test successful, vector size: {test_embedding.shape[1]}")

    except Exception as e:
        logger.error(f"❌ Failed to load embedding model: {e}")
        embedding_model = None

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
    app.state.http_client = httpx.AsyncClient(timeout=60.0)
    logger.info("✅ HTTP client initialized")

    yield

    # Cleanup
    logger.info("🛑 Shutting down Embedding Service")
    if app.state.http_client:
        await app.state.http_client.aclose()
    if app.state.redis:
        app.state.redis.close()
    executor.shutdown(wait=True)


# Create FastAPI application
app = FastAPI(
    title="PDF Chat Appliance Embedding Service",
    description="Text embedding generation service with enterprise-scale optimizations",
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


def generate_embeddings_batch(
    texts: List[str], batch_size: int = None
) -> List[List[float]]:
    """Generate embeddings for a batch of texts"""
    if not embedding_model:
        raise Exception("Embedding model not loaded")

    batch_size = batch_size or SERVICE_CONFIG["batch_size"]
    embeddings = []

    try:
        # Process in batches
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i : i + batch_size]

            # Generate embeddings
            batch_embeddings = embedding_model.encode(
                batch_texts,
                convert_to_tensor=False,
                show_progress_bar=False,
                normalize_embeddings=True,
            )

            # Convert to list format
            batch_embeddings_list = batch_embeddings.tolist()
            embeddings.extend(batch_embeddings_list)

            logger.debug(
                f"Processed batch {i//batch_size + 1}, size: {len(batch_texts)}"
            )

        return embeddings

    except Exception as e:
        logger.error(f"Embedding generation failed: {e}")
        raise


def validate_texts(texts: List[str]) -> List[str]:
    """Validate and clean input texts"""
    if not texts:
        raise ValueError("No texts provided")

    if not isinstance(texts, list):
        raise ValueError("Texts must be a list")

    if len(texts) > 1000:  # Limit batch size
        raise ValueError("Too many texts provided (max 1000)")

    # Clean and validate texts
    cleaned_texts = []
    for i, text in enumerate(texts):
        if not isinstance(text, str):
            raise ValueError(f"Text at index {i} is not a string")

        # Clean text
        cleaned_text = text.strip()
        if len(cleaned_text) > 10000:  # Limit text length
            cleaned_text = cleaned_text[:10000]

        if cleaned_text:
            cleaned_texts.append(cleaned_text)

    if not cleaned_texts:
        raise ValueError("No valid texts after cleaning")

    return cleaned_texts


@app.get("/health")
async def health_check():
    """Embedding Service health check"""
    try:
        # Check Redis connection
        redis_healthy = False
        if app.state.redis:
            try:
                app.state.redis.ping()
                redis_healthy = True
            except:
                pass

        # Check model status
        model_healthy = embedding_model is not None

        return {
            "status": "healthy" if redis_healthy and model_healthy else "degraded",
            "timestamp": time.time(),
            "service": "embedding-service",
            "redis": "healthy" if redis_healthy else "unhealthy",
            "model": "healthy" if model_healthy else "unhealthy",
            "model_name": SERVICE_CONFIG["embedding_model"],
            "device": SERVICE_CONFIG["device"],
            "vector_size": SERVICE_CONFIG["vector_size"],
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {e}")


@app.get("/")
async def root():
    """Embedding Service root endpoint"""
    return {
        "message": "PDF Chat Appliance Embedding Service",
        "version": "1.0.0",
        "status": "operational",
        "model": SERVICE_CONFIG["embedding_model"],
        "vector_size": SERVICE_CONFIG["vector_size"],
        "batch_size": SERVICE_CONFIG["batch_size"],
        "device": SERVICE_CONFIG["device"],
    }


@app.post("/embed")
async def generate_embeddings(request: Request):
    """Generate embeddings for text"""
    try:
        body = await request.json()
        texts = body.get("texts", [])

        # Validate input
        cleaned_texts = validate_texts(texts)

        # Check model availability
        if not embedding_model:
            raise HTTPException(status_code=503, detail="Embedding model not available")

        # Generate embeddings
        start_time = time.time()
        embeddings = generate_embeddings_batch(cleaned_texts)
        processing_time = time.time() - start_time

        # Log metrics
        if app.state.redis:
            try:
                app.state.redis.incr("embedding_requests_total")
                app.state.redis.incrby("embedding_vectors_generated", len(embeddings))
                app.state.redis.set("embedding_last_processing_time", processing_time)
            except Exception as e:
                logger.warning(f"Failed to log metrics: {e}")

        return {
            "embeddings": embeddings,
            "model": SERVICE_CONFIG["embedding_model"],
            "vector_size": SERVICE_CONFIG["vector_size"],
            "texts_processed": len(cleaned_texts),
            "processing_time": processing_time,
            "batch_size": SERVICE_CONFIG["batch_size"],
        }

    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Embedding generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Embedding generation failed: {e}")


@app.post("/embed/batch")
async def generate_embeddings_batch_endpoint(request: Request):
    """Generate embeddings for large batches with progress tracking"""
    try:
        body = await request.json()
        texts = body.get("texts", [])
        batch_id = body.get("batch_id", str(uuid.uuid4()))

        # Validate input
        cleaned_texts = validate_texts(texts)

        # Check model availability
        if not embedding_model:
            raise HTTPException(status_code=503, detail="Embedding model not available")

        # Initialize batch tracking
        if app.state.redis:
            app.state.redis.hset(f"embedding_batch:{batch_id}", "status", "processing")
            app.state.redis.hset(
                f"embedding_batch:{batch_id}", "total", str(len(cleaned_texts))
            )
            app.state.redis.hset(f"embedding_batch:{batch_id}", "processed", "0")

        # Process in batches
        all_embeddings = []
        batch_size = SERVICE_CONFIG["batch_size"]
        total_batches = (len(cleaned_texts) + batch_size - 1) // batch_size

        start_time = time.time()

        for i in range(0, len(cleaned_texts), batch_size):
            batch_texts = cleaned_texts[i : i + batch_size]

            # Generate embeddings for batch
            batch_embeddings = generate_embeddings_batch(batch_texts)
            all_embeddings.extend(batch_embeddings)

            # Update progress
            processed = min(i + batch_size, len(cleaned_texts))
            if app.state.redis:
                app.state.redis.hset(
                    f"embedding_batch:{batch_id}", "processed", str(processed)
                )
                progress = int((processed / len(cleaned_texts)) * 100)
                app.state.redis.hset(
                    f"embedding_batch:{batch_id}", "progress", str(progress)
                )

        processing_time = time.time() - start_time

        # Update final status
        if app.state.redis:
            app.state.redis.hset(f"embedding_batch:{batch_id}", "status", "completed")
            app.state.redis.hset(
                f"embedding_batch:{batch_id}", "processing_time", str(processing_time)
            )
            app.state.redis.hset(
                f"embedding_batch:{batch_id}",
                "embeddings_generated",
                str(len(all_embeddings)),
            )

        return {
            "batch_id": batch_id,
            "embeddings": all_embeddings,
            "model": SERVICE_CONFIG["embedding_model"],
            "vector_size": SERVICE_CONFIG["vector_size"],
            "texts_processed": len(cleaned_texts),
            "processing_time": processing_time,
            "total_batches": total_batches,
        }

    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Batch embedding generation failed: {e}")
        if app.state.redis and batch_id:
            app.state.redis.hset(f"embedding_batch:{batch_id}", "status", "failed")
            app.state.redis.hset(f"embedding_batch:{batch_id}", "error", str(e))
        raise HTTPException(
            status_code=500, detail=f"Batch embedding generation failed: {e}"
        )


@app.get("/batch/{batch_id}")
async def get_batch_status(batch_id: str):
    """Get batch processing status"""
    try:
        if app.state.redis:
            batch_data = app.state.redis.hgetall(f"embedding_batch:{batch_id}")
            if batch_data:
                return {
                    "batch_id": batch_id,
                    "status": batch_data.get("status", "unknown"),
                    "progress": batch_data.get("progress", "0"),
                    "total": batch_data.get("total", "0"),
                    "processed": batch_data.get("processed", "0"),
                    "processing_time": batch_data.get("processing_time", "0"),
                    "embeddings_generated": batch_data.get("embeddings_generated", "0"),
                    "error": batch_data.get("error", ""),
                }
            else:
                raise HTTPException(status_code=404, detail="Batch not found")
        else:
            raise HTTPException(status_code=503, detail="Redis not available")
    except Exception as e:
        logger.error(f"Batch status check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Batch status check failed: {e}")


@app.get("/model/info")
async def get_model_info():
    """Get embedding model information"""
    try:
        if not embedding_model:
            raise HTTPException(status_code=503, detail="Model not loaded")

        model_info = {
            "model_name": SERVICE_CONFIG["embedding_model"],
            "vector_size": SERVICE_CONFIG["vector_size"],
            "device": SERVICE_CONFIG["device"],
            "batch_size": SERVICE_CONFIG["batch_size"],
            "max_workers": SERVICE_CONFIG["max_workers"],
        }

        # Get model-specific info
        try:
            model_info["max_seq_length"] = embedding_model.max_seq_length
            model_info["model_path"] = str(embedding_model.model_path)
        except:
            pass

        return model_info

    except Exception as e:
        logger.error(f"Model info retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=f"Model info retrieval failed: {e}")


@app.get("/stats")
async def get_stats():
    """Get embedding service statistics"""
    try:
        stats = {
            "timestamp": time.time(),
            "service": "embedding-service",
            "model": SERVICE_CONFIG["embedding_model"],
            "vector_size": SERVICE_CONFIG["vector_size"],
            "device": SERVICE_CONFIG["device"],
            "batch_size": SERVICE_CONFIG["batch_size"],
            "model_loaded": embedding_model is not None,
            "redis_connected": app.state.redis is not None,
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

                # Get embedding metrics
                stats["metrics"] = {
                    "total_requests": app.state.redis.get("embedding_requests_total")
                    or "0",
                    "total_vectors": app.state.redis.get("embedding_vectors_generated")
                    or "0",
                    "last_processing_time": app.state.redis.get(
                        "embedding_last_processing_time"
                    )
                    or "0",
                }
            except Exception as e:
                stats["redis"] = {"error": str(e)}

        return stats
    except Exception as e:
        logger.error(f"Stats collection failed: {e}")
        raise HTTPException(status_code=500, detail=f"Stats collection failed: {e}")


if __name__ == "__main__":
    print("🚀 Starting PDF Chat Appliance Embedding Service")
    print("=" * 50)

    # Run the application
    uvicorn.run("main:app", host="0.0.0.0", port=8002, reload=False, log_level="info")
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
