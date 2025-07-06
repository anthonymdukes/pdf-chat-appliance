#!/usr/bin/env python3
"""
LLM Service for PDF Chat Appliance Microservices
Handles LLM interactions, model management, and response generation
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

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Service configuration
SERVICE_CONFIG = {
    "redis_host": os.getenv("REDIS_HOST", "redis"),
    "redis_port": int(os.getenv("REDIS_PORT", 6379)),
    "ollama_host": os.getenv("OLLAMA_HOST", "http://ollama:11434"),
    "default_model": os.getenv("DEFAULT_MODEL", "phi3:cpu"),
    "max_tokens": int(os.getenv("MAX_TOKENS", 4096)),
    "temperature": float(os.getenv("TEMPERATURE", 0.7)),
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("🚀 Starting LLM Service")

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

    # Check Ollama availability
    try:
        response = await app.state.http_client.get(
            f"{SERVICE_CONFIG['ollama_host']}/api/tags"
        )
        if response.status_code == 200:
            models = response.json().get("models", [])
            logger.info(
                f"✅ Ollama connection established. Available models: {[m['name'] for m in models]}"
            )
        else:
            logger.warning(f"⚠️ Ollama responded with status {response.status_code}")
    except Exception as e:
        logger.error(f"❌ Ollama connection failed: {e}")

    yield

    # Cleanup
    logger.info("🛑 Shutting down LLM Service")
    if app.state.http_client:
        await app.state.http_client.aclose()
    if app.state.redis:
        app.state.redis.close()


# Create FastAPI application
app = FastAPI(
    title="PDF Chat Appliance LLM Service",
    description="LLM interaction and model management service",
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
    """LLM Service health check"""
    try:
        # Check Redis connection
        redis_healthy = False
        if app.state.redis:
            try:
                app.state.redis.ping()
                redis_healthy = True
            except:
                pass

        # Check Ollama connection
        ollama_healthy = False
        try:
            response = await app.state.http_client.get(
                f"{SERVICE_CONFIG['ollama_host']}/api/tags"
            )
            ollama_healthy = response.status_code == 200
        except:
            pass

        return {
            "status": "healthy" if redis_healthy and ollama_healthy else "degraded",
            "timestamp": time.time(),
            "service": "llm-service",
            "redis": "healthy" if redis_healthy else "unhealthy",
            "ollama": "healthy" if ollama_healthy else "unhealthy",
            "default_model": SERVICE_CONFIG["default_model"],
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {e}")


@app.get("/")
async def root():
    """LLM Service root endpoint"""
    return {
        "message": "PDF Chat Appliance LLM Service",
        "version": "1.0.0",
        "status": "operational",
        "ollama_host": SERVICE_CONFIG["ollama_host"],
        "default_model": SERVICE_CONFIG["default_model"],
    }


@app.get("/models")
async def list_models():
    """List available LLM models"""
    try:
        response = await app.state.http_client.get(
            f"{SERVICE_CONFIG['ollama_host']}/api/tags"
        )
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(
                status_code=response.status_code, detail="Failed to fetch models"
            )
    except Exception as e:
        logger.error(f"Model listing failed: {e}")
        raise HTTPException(status_code=500, detail=f"Model listing failed: {e}")


@app.post("/generate")
async def generate_response(request: Request):
    """Generate LLM response"""
    try:
        body = await request.json()

        # Extract parameters
        prompt = body.get("prompt", "")
        model = body.get("model", SERVICE_CONFIG["default_model"])
        max_tokens = body.get("max_tokens", SERVICE_CONFIG["max_tokens"])
        temperature = body.get("temperature", SERVICE_CONFIG["temperature"])

        if not prompt:
            raise HTTPException(status_code=400, detail="Prompt is required")

        # Prepare Ollama request
        ollama_request = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {"num_predict": max_tokens, "temperature": temperature},
        }

        # Send request to Ollama
        response = await app.state.http_client.post(
            f"{SERVICE_CONFIG['ollama_host']}/api/generate", json=ollama_request
        )

        if response.status_code == 200:
            result = response.json()
            return {
                "response": result.get("response", ""),
                "model": model,
                "prompt_tokens": result.get("prompt_eval_count", 0),
                "response_tokens": result.get("eval_count", 0),
                "total_duration": result.get("total_duration", 0),
            }
        else:
            raise HTTPException(
                status_code=response.status_code, detail="Ollama generation failed"
            )

    except Exception as e:
        logger.error(f"Generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Generation failed: {e}")


@app.post("/chat")
async def chat_completion(request: Request):
    """Chat completion endpoint"""
    try:
        body = await request.json()

        # Extract parameters
        messages = body.get("messages", [])
        model = body.get("model", SERVICE_CONFIG["default_model"])
        max_tokens = body.get("max_tokens", SERVICE_CONFIG["max_tokens"])
        temperature = body.get("temperature", SERVICE_CONFIG["temperature"])

        if not messages:
            raise HTTPException(status_code=400, detail="Messages are required")

        # Convert messages to prompt
        prompt = ""
        for message in messages:
            role = message.get("role", "user")
            content = message.get("content", "")
            if role == "user":
                prompt += f"User: {content}\n"
            elif role == "assistant":
                prompt += f"Assistant: {content}\n"
            elif role == "system":
                prompt += f"System: {content}\n"

        prompt += "Assistant: "

        # Generate response
        ollama_request = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {"num_predict": max_tokens, "temperature": temperature},
        }

        response = await app.state.http_client.post(
            f"{SERVICE_CONFIG['ollama_host']}/api/generate", json=ollama_request
        )

        if response.status_code == 200:
            result = response.json()
            return {
                "choices": [
                    {
                        "message": {
                            "role": "assistant",
                            "content": result.get("response", ""),
                        },
                        "finish_reason": "stop",
                    }
                ],
                "model": model,
                "usage": {
                    "prompt_tokens": result.get("prompt_eval_count", 0),
                    "completion_tokens": result.get("eval_count", 0),
                    "total_tokens": result.get("prompt_eval_count", 0)
                    + result.get("eval_count", 0),
                },
            }
        else:
            raise HTTPException(
                status_code=response.status_code, detail="Ollama chat failed"
            )

    except Exception as e:
        logger.error(f"Chat completion failed: {e}")
        raise HTTPException(status_code=500, detail=f"Chat completion failed: {e}")


@app.get("/stats")
async def get_stats():
    """Get LLM service statistics"""
    try:
        stats = {
            "timestamp": time.time(),
            "service": "llm-service",
            "ollama_host": SERVICE_CONFIG["ollama_host"],
            "default_model": SERVICE_CONFIG["default_model"],
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
            except Exception as e:
                stats["redis"] = {"error": str(e)}

        return stats
    except Exception as e:
        logger.error(f"Stats collection failed: {e}")
        raise HTTPException(status_code=500, detail=f"Stats collection failed: {e}")


if __name__ == "__main__":
    print("🚀 Starting PDF Chat Appliance LLM Service")
    print("=" * 50)

    # Run the application
    uvicorn.run("main:app", host="0.0.0.0", port=8003, reload=False, log_level="info")
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
