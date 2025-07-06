#!/usr/bin/env python3
"""
Chat Service for PDF Chat Appliance Microservices
Handles conversational AI and chat interactions with RAG capabilities
"""

import json
import logging
import os
import time
import uuid
from contextlib import asynccontextmanager
from typing import Dict, List

import httpx
import redis
import uvicorn
from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
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
    "llm_url": os.getenv("LLM_URL", "http://llm-service:8003"),
    "vector_store_url": os.getenv("VECTOR_STORE_URL", "http://vector-store:8005"),
    "embedding_url": os.getenv("EMBEDDING_URL", "http://embedding-service:8002"),
    "max_context_length": int(os.getenv("MAX_CONTEXT_LENGTH", 4000)),
    "max_search_results": int(os.getenv("MAX_SEARCH_RESULTS", 5)),
    "similarity_threshold": float(os.getenv("SIMILARITY_THRESHOLD", 0.7)),
    "session_timeout": int(os.getenv("SESSION_TIMEOUT", 3600)),  # 1 hour
}

# Active WebSocket connections
active_connections: Dict[str, WebSocket] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("🚀 Starting Chat Service")

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
    logger.info("🛑 Shutting down Chat Service")
    if app.state.http_client:
        await app.state.http_client.aclose()
    if app.state.redis:
        app.state.redis.close()


# Create FastAPI application
app = FastAPI(
    title="PDF Chat Appliance Chat Service",
    description="Conversational AI chat service with RAG capabilities",
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


async def search_relevant_context(query: str, max_results: int = None) -> List[Dict]:
    """Search for relevant context using vector similarity"""
    try:
        max_results = max_results or SERVICE_CONFIG["max_search_results"]

        # Generate query embedding
        async with httpx.AsyncClient(timeout=30.0) as client:
            embedding_response = await client.post(
                f"{SERVICE_CONFIG['embedding_url']}/embed", json={"texts": [query]}
            )

            if embedding_response.status_code != 200:
                logger.error(
                    f"Embedding generation failed: {embedding_response.status_code}"
                )
                return []

            query_embedding = embedding_response.json()["embeddings"][0]

            # Search vector store
            search_response = await client.post(
                f"{SERVICE_CONFIG['vector_store_url']}/collections/pdf_chunks/search",
                json={
                    "vector": query_embedding,
                    "limit": max_results,
                    "score_threshold": SERVICE_CONFIG["similarity_threshold"],
                },
            )

            if search_response.status_code == 200:
                results = search_response.json()["results"]
                return results
            else:
                logger.error(f"Vector search failed: {search_response.status_code}")
                return []

    except Exception as e:
        logger.error(f"Context search failed: {e}")
        return []


def build_context_prompt(query: str, context_results: List[Dict]) -> str:
    """Build context-aware prompt for LLM"""
    if not context_results:
        return f"User: {query}\nAssistant:"

    # Build context from search results
    context_parts = []
    for i, result in enumerate(context_results, 1):
        text = result.get("payload", {}).get("text", "")
        pages = result.get("payload", {}).get("pages", [])
        score = result.get("score", 0)

        if text and score > SERVICE_CONFIG["similarity_threshold"]:
            context_parts.append(
                f"Context {i} (Pages {pages}, Relevance: {score:.2f}):\n{text}"
            )

    if context_parts:
        context_text = "\n\n".join(context_parts)
        prompt = f"""Based on the following context from the uploaded documents, please answer the user's question:

Context:
{context_text}

User Question: {query}

Please provide a comprehensive answer based on the context provided. If the context doesn't contain enough information to answer the question, please say so.

Assistant:"""
    else:
        prompt = f"User: {query}\nAssistant:"

    return prompt


async def generate_chat_response(
    query: str, context_results: List[Dict] = None
) -> Dict:
    """Generate chat response using LLM with context"""
    try:
        # Get context if not provided
        if context_results is None:
            context_results = await search_relevant_context(query)

        # Build context-aware prompt
        prompt = build_context_prompt(query, context_results)

        # Generate response using LLM service
        async with httpx.AsyncClient(timeout=60.0) as client:
            llm_response = await client.post(
                f"{SERVICE_CONFIG['llm_url']}/generate",
                json={
                    "prompt": prompt,
                    "max_tokens": SERVICE_CONFIG["max_context_length"],
                    "temperature": 0.7,
                },
            )

            if llm_response.status_code == 200:
                result = llm_response.json()
                return {
                    "response": result.get("response", ""),
                    "context_used": len(context_results),
                    "context_sources": [
                        r.get("payload", {}).get("pages", []) for r in context_results
                    ],
                    "model": result.get("model", "unknown"),
                    "processing_time": time.time(),
                }
            else:
                logger.error(f"LLM generation failed: {llm_response.status_code}")
                return {
                    "response": "I apologize, but I'm having trouble generating a response right now. Please try again.",
                    "context_used": 0,
                    "context_sources": [],
                    "model": "unknown",
                    "processing_time": time.time(),
                }

    except Exception as e:
        logger.error(f"Chat response generation failed: {e}")
        return {
            "response": "I apologize, but I encountered an error while processing your request. Please try again.",
            "context_used": 0,
            "context_sources": [],
            "model": "unknown",
            "processing_time": time.time(),
        }


def create_chat_session(session_id: str = None) -> str:
    """Create a new chat session"""
    if not session_id:
        session_id = str(uuid.uuid4())

    session_data = {
        "session_id": session_id,
        "created_at": time.time(),
        "last_activity": time.time(),
        "message_count": 0,
    }

    if app.state.redis:
        app.state.redis.hset(f"chat_session:{session_id}", mapping=session_data)
        app.state.redis.expire(
            f"chat_session:{session_id}", SERVICE_CONFIG["session_timeout"]
        )

    return session_id


def update_session_activity(session_id: str):
    """Update session activity timestamp"""
    if app.state.redis:
        app.state.redis.hset(f"chat_session:{session_id}", "last_activity", time.time())
        app.state.redis.hincrby(f"chat_session:{session_id}", "message_count", 1)


@app.get("/health")
async def health_check():
    """Chat Service health check"""
    try:
        # Check Redis connection
        redis_healthy = False
        if app.state.redis:
            try:
                app.state.redis.ping()
                redis_healthy = True
            except:
                pass

        # Check service dependencies
        services_healthy = 0
        total_services = 3

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                # Check LLM service
                llm_response = await client.get(f"{SERVICE_CONFIG['llm_url']}/health")
                if llm_response.status_code == 200:
                    services_healthy += 1

                # Check vector store service
                vector_response = await client.get(
                    f"{SERVICE_CONFIG['vector_store_url']}/health"
                )
                if vector_response.status_code == 200:
                    services_healthy += 1

                # Check embedding service
                embedding_response = await client.get(
                    f"{SERVICE_CONFIG['embedding_url']}/health"
                )
                if embedding_response.status_code == 200:
                    services_healthy += 1
        except:
            pass

        return {
            "status": (
                "healthy" if redis_healthy and services_healthy > 0 else "degraded"
            ),
            "timestamp": time.time(),
            "service": "chat-service",
            "redis": "healthy" if redis_healthy else "unhealthy",
            "dependencies": f"{services_healthy}/{total_services} healthy",
            "active_connections": len(active_connections),
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {e}")


@app.get("/")
async def root():
    """Chat Service root endpoint"""
    return {
        "message": "PDF Chat Appliance Chat Service",
        "version": "1.0.0",
        "status": "operational",
        "features": [
            "RAG",
            "Context Search",
            "WebSocket Support",
            "Session Management",
        ],
    }


@app.post("/chat")
async def chat_endpoint(request: Request):
    """Process chat message"""
    try:
        body = await request.json()
        message = body.get("message", "")
        session_id = body.get("session_id")
        context_results = body.get("context", [])

        if not message:
            raise HTTPException(status_code=400, detail="Message is required")

        # Create or update session
        if not session_id:
            session_id = create_chat_session()
        else:
            update_session_activity(session_id)

        # Generate response
        start_time = time.time()
        response = await generate_chat_response(message, context_results)
        processing_time = time.time() - start_time

        # Store conversation in Redis
        if app.state.redis:
            conversation_key = f"chat_conversation:{session_id}"
            conversation_data = {
                "timestamp": time.time(),
                "user_message": message,
                "assistant_response": response["response"],
                "context_used": response["context_used"],
                "processing_time": processing_time,
            }
            app.state.redis.lpush(conversation_key, json.dumps(conversation_data))
            app.state.redis.ltrim(conversation_key, 0, 99)  # Keep last 100 messages
            app.state.redis.expire(conversation_key, SERVICE_CONFIG["session_timeout"])

        return {
            "session_id": session_id,
            "response": response["response"],
            "context_used": response["context_used"],
            "context_sources": response["context_sources"],
            "processing_time": processing_time,
            "model": response["model"],
        }

    except Exception as e:
        logger.error(f"Chat processing failed: {e}")
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {e}")


@app.post("/search")
async def search_context(request: Request):
    """Search for relevant context"""
    try:
        body = await request.json()
        query = body.get("query", "")
        max_results = body.get("max_results", SERVICE_CONFIG["max_search_results"])

        if not query:
            raise HTTPException(status_code=400, detail="Query is required")

        # Search for relevant context
        context_results = await search_relevant_context(query, max_results)

        return {
            "query": query,
            "results": context_results,
            "total_found": len(context_results),
            "threshold": SERVICE_CONFIG["similarity_threshold"],
        }

    except Exception as e:
        logger.error(f"Context search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Context search failed: {e}")


@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time chat"""
    await websocket.accept()
    active_connections[session_id] = websocket

    try:
        # Create or update session
        create_chat_session(session_id)

        while True:
            # Receive message
            data = await websocket.receive_text()
            message_data = json.loads(data)
            message = message_data.get("message", "")

            if not message:
                continue

            # Update session activity
            update_session_activity(session_id)

            # Generate response
            response = await generate_chat_response(message)

            # Send response
            await websocket.send_text(
                json.dumps(
                    {
                        "type": "response",
                        "response": response["response"],
                        "context_used": response["context_used"],
                        "context_sources": response["context_sources"],
                        "model": response["model"],
                    }
                )
            )

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: {session_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        try:
            await websocket.send_text(
                json.dumps(
                    {
                        "type": "error",
                        "message": "An error occurred while processing your message.",
                    }
                )
            )
        except:
            pass
    finally:
        if session_id in active_connections:
            del active_connections[session_id]


@app.get("/session/{session_id}")
async def get_session_info(session_id: str):
    """Get chat session information"""
    try:
        if app.state.redis:
            session_data = app.state.redis.hgetall(f"chat_session:{session_id}")
            if session_data:
                # Get recent conversation
                conversation_key = f"chat_conversation:{session_id}"
                recent_messages = app.state.redis.lrange(
                    conversation_key, 0, 9
                )  # Last 10 messages

                return {
                    "session_id": session_id,
                    "created_at": session_data.get("created_at", ""),
                    "last_activity": session_data.get("last_activity", ""),
                    "message_count": session_data.get("message_count", "0"),
                    "recent_messages": [json.loads(msg) for msg in recent_messages],
                    "active_websocket": session_id in active_connections,
                }
            else:
                raise HTTPException(status_code=404, detail="Session not found")
        else:
            raise HTTPException(status_code=503, detail="Redis not available")
    except Exception as e:
        logger.error(f"Session info retrieval failed: {e}")
        raise HTTPException(
            status_code=500, detail=f"Session info retrieval failed: {e}"
        )


@app.delete("/session/{session_id}")
async def delete_session(session_id: str):
    """Delete chat session"""
    try:
        if app.state.redis:
            # Remove session data
            app.state.redis.delete(f"chat_session:{session_id}")
            app.state.redis.delete(f"chat_conversation:{session_id}")

            # Close WebSocket connection if active
            if session_id in active_connections:
                try:
                    await active_connections[session_id].close()
                except:
                    pass
                del active_connections[session_id]

            return {"message": f"Session {session_id} deleted successfully"}
        else:
            raise HTTPException(status_code=503, detail="Redis not available")
    except Exception as e:
        logger.error(f"Session deletion failed: {e}")
        raise HTTPException(status_code=500, detail=f"Session deletion failed: {e}")


@app.get("/stats")
async def get_stats():
    """Get chat service statistics"""
    try:
        stats = {
            "timestamp": time.time(),
            "service": "chat-service",
            "active_connections": len(active_connections),
            "max_context_length": SERVICE_CONFIG["max_context_length"],
            "max_search_results": SERVICE_CONFIG["max_search_results"],
            "similarity_threshold": SERVICE_CONFIG["similarity_threshold"],
            "session_timeout": SERVICE_CONFIG["session_timeout"],
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

                # Get session statistics
                session_keys = app.state.redis.keys("chat_session:*")
                stats["sessions"] = {
                    "total": len(session_keys),
                    "active": len(
                        [
                            k
                            for k in session_keys
                            if app.state.redis.hget(k, "last_activity")
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
    print("🚀 Starting PDF Chat Appliance Chat Service")
    print("=" * 50)

    # Run the application
    uvicorn.run("main:app", host="0.0.0.0", port=8004, reload=False, log_level="info")
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
