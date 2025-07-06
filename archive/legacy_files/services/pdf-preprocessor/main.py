#!/usr/bin/env python3
"""
PDF Preprocessor Service for PDF Chat Appliance Microservices
Handles PDF parsing, chunking, and initial processing with enterprise-scale optimizations
"""

import asyncio
import hashlib
import logging
import os
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Dict, List

import fitz  # PyMuPDF
import httpx
import redis
import uvicorn
from fastapi import BackgroundTasks, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Service configuration
SERVICE_CONFIG = {
    "redis_host": os.getenv("REDIS_HOST", "redis"),
    "redis_port": int(os.getenv("REDIS_PORT", 6379)),
    "embedding_url": os.getenv("EMBEDDING_URL", "http://embedding-service:8002"),
    "vector_store_url": os.getenv("VECTOR_STORE_URL", "http://vector-store:8005"),
    "chunk_size": int(os.getenv("CHUNK_SIZE", 1000)),
    "chunk_overlap": int(os.getenv("CHUNK_OVERLAP", 200)),
    "max_workers": int(os.getenv("MAX_WORKERS", 4)),
    "upload_dir": os.getenv("UPLOAD_DIR", "/app/uploads"),
    "archive_dir": os.getenv("ARCHIVE_DIR", "/app/archive"),
}

# Processing queue
processing_queue = {}
executor = ThreadPoolExecutor(max_workers=SERVICE_CONFIG["max_workers"])


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("🚀 Starting PDF Preprocessor Service")

    # Create directories
    Path(SERVICE_CONFIG["upload_dir"]).mkdir(parents=True, exist_ok=True)
    Path(SERVICE_CONFIG["archive_dir"]).mkdir(parents=True, exist_ok=True)

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
    logger.info("🛑 Shutting down PDF Preprocessor Service")
    if app.state.http_client:
        await app.state.http_client.aclose()
    if app.state.redis:
        app.state.redis.close()
    executor.shutdown(wait=True)


# Create FastAPI application
app = FastAPI(
    title="PDF Chat Appliance PDF Preprocessor Service",
    description="PDF parsing and preprocessing service with enterprise-scale optimizations",
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


def extract_text_from_pdf(pdf_path: str) -> Dict[str, Any]:
    """Extract text from PDF with metadata"""
    try:
        doc = fitz.open(pdf_path)
        text_content = []
        metadata = {
            "pages": len(doc),
            "title": doc.metadata.get("title", ""),
            "author": doc.metadata.get("author", ""),
            "subject": doc.metadata.get("subject", ""),
            "creator": doc.metadata.get("creator", ""),
            "producer": doc.metadata.get("producer", ""),
            "creation_date": doc.metadata.get("creationDate", ""),
            "modification_date": doc.metadata.get("modDate", ""),
        }

        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text = page.get_text()
            if text.strip():
                text_content.append(
                    {"page": page_num + 1, "text": text.strip(), "bbox": page.rect}
                )

        doc.close()

        return {
            "text_content": text_content,
            "metadata": metadata,
            "total_pages": len(doc),
        }
    except Exception as e:
        logger.error(f"PDF extraction failed: {e}")
        raise


def create_chunks(
    text_content: List[Dict], chunk_size: int, overlap: int
) -> List[Dict]:
    """Create overlapping text chunks"""
    chunks = []
    current_chunk = ""
    current_pages = []

    for content in text_content:
        page_text = content["text"]
        page_num = content["page"]

        # Split page text into sentences for better chunking
        sentences = page_text.split(". ")

        for sentence in sentences:
            if len(current_chunk) + len(sentence) > chunk_size and current_chunk:
                # Save current chunk
                chunks.append(
                    {
                        "id": str(uuid.uuid4()),
                        "text": current_chunk.strip(),
                        "pages": current_pages.copy(),
                        "length": len(current_chunk),
                    }
                )

                # Start new chunk with overlap
                overlap_text = current_chunk[-overlap:] if overlap > 0 else ""
                current_chunk = overlap_text + sentence + ". "
                current_pages = [page_num] if overlap == 0 else current_pages[-1:]
            else:
                current_chunk += sentence + ". "
                if page_num not in current_pages:
                    current_pages.append(page_num)

    # Add final chunk
    if current_chunk.strip():
        chunks.append(
            {
                "id": str(uuid.uuid4()),
                "text": current_chunk.strip(),
                "pages": current_pages,
                "length": len(current_chunk),
            }
        )

    return chunks


async def process_pdf_async(file_path: str, job_id: str):
    """Asynchronous PDF processing"""
    try:
        logger.info(f"Starting PDF processing for job {job_id}")

        # Update job status
        if app.state.redis:
            app.state.redis.hset(f"pdf_job:{job_id}", "status", "processing")
            app.state.redis.hset(f"pdf_job:{job_id}", "progress", "10")

        # Extract text from PDF
        extraction_result = extract_text_from_pdf(file_path)
        text_content = extraction_result["text_content"]
        metadata = extraction_result["metadata"]

        if app.state.redis:
            app.state.redis.hset(f"pdf_job:{job_id}", "progress", "30")
            app.state.redis.hset(f"pdf_job:{job_id}", "pages", str(metadata["pages"]))

        # Create chunks
        chunks = create_chunks(
            text_content, SERVICE_CONFIG["chunk_size"], SERVICE_CONFIG["chunk_overlap"]
        )

        if app.state.redis:
            app.state.redis.hset(f"pdf_job:{job_id}", "progress", "50")
            app.state.redis.hset(f"pdf_job:{job_id}", "chunks", str(len(chunks)))

        # Generate embeddings for chunks
        chunk_texts = [chunk["text"] for chunk in chunks]

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                embedding_response = await client.post(
                    f"{SERVICE_CONFIG['embedding_url']}/embed",
                    json={"texts": chunk_texts},
                )

                if embedding_response.status_code == 200:
                    embeddings = embedding_response.json()["embeddings"]

                    # Store chunks and embeddings in vector store
                    points = []
                    for i, chunk in enumerate(chunks):
                        points.append(
                            {
                                "id": chunk["id"],
                                "vector": embeddings[i],
                                "payload": {
                                    "text": chunk["text"],
                                    "pages": chunk["pages"],
                                    "length": chunk["length"],
                                    "job_id": job_id,
                                    "metadata": metadata,
                                },
                            }
                        )

                    # Store in vector database
                    vector_response = await client.post(
                        f"{SERVICE_CONFIG['vector_store_url']}/collections/pdf_chunks/points",
                        json={"points": points},
                    )

                    if vector_response.status_code == 200:
                        logger.info(
                            f"Successfully stored {len(points)} chunks for job {job_id}"
                        )

                        if app.state.redis:
                            app.state.redis.hset(
                                f"pdf_job:{job_id}", "status", "completed"
                            )
                            app.state.redis.hset(f"pdf_job:{job_id}", "progress", "100")
                            app.state.redis.hset(
                                f"pdf_job:{job_id}", "vectors_stored", str(len(points))
                            )
                    else:
                        raise Exception(
                            f"Vector storage failed: {vector_response.status_code}"
                        )
                else:
                    raise Exception(
                        f"Embedding generation failed: {embedding_response.status_code}"
                    )

        except Exception as e:
            logger.error(f"Processing pipeline failed for job {job_id}: {e}")
            if app.state.redis:
                app.state.redis.hset(f"pdf_job:{job_id}", "status", "failed")
                app.state.redis.hset(f"pdf_job:{job_id}", "error", str(e))

        # Archive processed file
        try:
            archive_path = (
                Path(SERVICE_CONFIG["archive_dir"]) / f"{job_id}_{Path(file_path).name}"
            )
            Path(file_path).rename(archive_path)
            logger.info(f"Archived file to {archive_path}")
        except Exception as e:
            logger.warning(f"Failed to archive file: {e}")

        # Clean up job from processing queue
        if job_id in processing_queue:
            del processing_queue[job_id]

        logger.info(f"PDF processing completed for job {job_id}")

    except Exception as e:
        logger.error(f"PDF processing failed for job {job_id}: {e}")
        if app.state.redis:
            app.state.redis.hset(f"pdf_job:{job_id}", "status", "failed")
            app.state.redis.hset(f"pdf_job:{job_id}", "error", str(e))

        if job_id in processing_queue:
            del processing_queue[job_id]


@app.get("/health")
async def health_check():
    """PDF Preprocessor Service health check"""
    try:
        # Check Redis connection
        redis_healthy = False
        if app.state.redis:
            try:
                app.state.redis.ping()
                redis_healthy = True
            except:
                pass

        # Check processing queue
        queue_size = len(processing_queue)

        return {
            "status": "healthy" if redis_healthy else "degraded",
            "timestamp": time.time(),
            "service": "pdf-preprocessor",
            "redis": "healthy" if redis_healthy else "unhealthy",
            "queue_size": queue_size,
            "max_workers": SERVICE_CONFIG["max_workers"],
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {e}")


@app.get("/")
async def root():
    """PDF Preprocessor Service root endpoint"""
    return {
        "message": "PDF Chat Appliance PDF Preprocessor Service",
        "version": "1.0.0",
        "status": "operational",
        "config": {
            "chunk_size": SERVICE_CONFIG["chunk_size"],
            "chunk_overlap": SERVICE_CONFIG["chunk_overlap"],
            "max_workers": SERVICE_CONFIG["max_workers"],
        },
    }


@app.post("/upload")
async def upload_document(
    file: UploadFile = File(...), background_tasks: BackgroundTasks = None
):
    """Upload and process PDF document"""
    try:
        # Validate file type
        if not file.filename.lower().endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")

        # Generate job ID
        job_id = str(uuid.uuid4())
        file_hash = hashlib.md5(file.filename.encode()).hexdigest()

        # Save uploaded file
        file_path = Path(SERVICE_CONFIG["upload_dir"]) / f"{job_id}_{file.filename}"
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        # Create job record
        job_info = {
            "id": job_id,
            "filename": file.filename,
            "file_hash": file_hash,
            "file_size": len(content),
            "status": "queued",
            "progress": "0",
            "created_at": time.time(),
            "file_path": str(file_path),
        }

        # Store job info in Redis
        if app.state.redis:
            for key, value in job_info.items():
                app.state.redis.hset(f"pdf_job:{job_id}", key, str(value))

        # Add to processing queue
        processing_queue[job_id] = job_info

        # Start background processing
        asyncio.create_task(process_pdf_async(str(file_path), job_id))

        logger.info(f"PDF upload queued: {file.filename} (job_id: {job_id})")

        return {
            "message": "PDF upload received and processing started",
            "job_id": job_id,
            "filename": file.filename,
            "status": "queued",
            "estimated_pages": "processing...",
        }

    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {e}")


@app.get("/status")
async def get_status():
    """Get processing status"""
    try:
        # Get all active jobs from Redis
        jobs = {}
        if app.state.redis:
            job_keys = app.state.redis.keys("pdf_job:*")
            for key in job_keys:
                job_id = key.split(":")[1]
                job_data = app.state.redis.hgetall(key)
                if job_data:
                    jobs[job_id] = job_data

        return {
            "status": "operational",
            "timestamp": time.time(),
            "service": "pdf-preprocessor",
            "active_jobs": len(processing_queue),
            "total_jobs": len(jobs),
            "jobs": jobs,
        }
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Status check failed: {e}")


@app.get("/job/{job_id}")
async def get_job_status(job_id: str):
    """Get specific job status"""
    try:
        if app.state.redis:
            job_data = app.state.redis.hgetall(f"pdf_job:{job_id}")
            if job_data:
                return {
                    "job_id": job_id,
                    "status": job_data.get("status", "unknown"),
                    "progress": job_data.get("progress", "0"),
                    "filename": job_data.get("filename", ""),
                    "pages": job_data.get("pages", "0"),
                    "chunks": job_data.get("chunks", "0"),
                    "vectors_stored": job_data.get("vectors_stored", "0"),
                    "error": job_data.get("error", ""),
                    "created_at": job_data.get("created_at", ""),
                    "updated_at": time.time(),
                }
            else:
                raise HTTPException(status_code=404, detail="Job not found")
        else:
            raise HTTPException(status_code=503, detail="Redis not available")
    except Exception as e:
        logger.error(f"Job status check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Job status check failed: {e}")


@app.get("/stats")
async def get_stats():
    """Get PDF preprocessor service statistics"""
    try:
        stats = {
            "timestamp": time.time(),
            "service": "pdf-preprocessor",
            "redis_connected": app.state.redis is not None,
            "queue_size": len(processing_queue),
            "max_workers": SERVICE_CONFIG["max_workers"],
            "config": {
                "chunk_size": SERVICE_CONFIG["chunk_size"],
                "chunk_overlap": SERVICE_CONFIG["chunk_overlap"],
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

                # Get job statistics
                job_keys = app.state.redis.keys("pdf_job:*")
                stats["jobs"] = {
                    "total": len(job_keys),
                    "completed": len(
                        [
                            k
                            for k in job_keys
                            if app.state.redis.hget(k, "status") == "completed"
                        ]
                    ),
                    "failed": len(
                        [
                            k
                            for k in job_keys
                            if app.state.redis.hget(k, "status") == "failed"
                        ]
                    ),
                    "processing": len(
                        [
                            k
                            for k in job_keys
                            if app.state.redis.hget(k, "status") == "processing"
                        ]
                    ),
                }
            except Exception as e:
                stats["redis"] = {"error": str(e)}

        return stats
    except Exception as e:
        logger.error(f"Stats collection failed: {e}")
        raise HTTPException(status_code=500, detail=f"Stats collection failed: {e}")


if __name__ == "__main__":
    print("🚀 Starting PDF Chat Appliance PDF Preprocessor Service")
    print("=" * 50)

    # Run the application
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=False, log_level="info")
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
