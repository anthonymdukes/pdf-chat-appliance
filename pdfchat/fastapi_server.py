"""
FastAPI-based query server for PDF Chat Appliance.

Provides REST API endpoints for querying ingested PDF documents
using semantic search and LLM-based responses with comprehensive
OpenAPI documentation generation.
"""

import logging
import os
import signal
import sys
import time
from typing import Dict, List, Optional

# Mandatory .venv activation check
if "venv" not in sys.executable:
    raise RuntimeError("VENV NOT ACTIVATED. Please activate `.venv` before running this script.")

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .config import Config
from .ingestion import PDFIngestion

# Import chat history if available
try:
    from memory.api import MemoryAPI
    from memory.models import Message
    CHAT_HISTORY_AVAILABLE = True
except ImportError:
    CHAT_HISTORY_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("Chat history not available")

# Setup logger
logger = logging.getLogger(__name__)


# Pydantic Models for API Documentation
class QueryRequest(BaseModel):
    """Request model for PDF queries."""
    query: str = Field(..., description="The query text to search for in PDF documents")
    user_id: Optional[str] = Field(default="default", description="User identifier for chat history")
    document_id: Optional[str] = Field(default=None, description="Specific document ID to search in")
    max_results: Optional[int] = Field(default=5, description="Maximum number of results to return", ge=1, le=20)


class SourceNode(BaseModel):
    """Model for source document nodes."""
    content: str = Field(..., description="Text content from the source document")
    metadata: Dict = Field(..., description="Metadata about the source document")
    score: Optional[float] = Field(None, description="Similarity score for the result")


class QueryAnalysis(BaseModel):
    """Model for query analysis results."""
    vendors: List[str] = Field(..., description="Vendor technologies mentioned in the query")
    is_cross_vendor: bool = Field(..., description="Whether the query involves multiple vendors")
    query_type: str = Field(..., description="Type of query (installation, integration, troubleshooting, general)")


class QueryResponse(BaseModel):
    """Response model for PDF queries."""
    answer: str = Field(..., description="The generated answer to the query")
    sources: List[SourceNode] = Field(..., description="Source documents used to generate the answer")
    query_analysis: QueryAnalysis = Field(..., description="Analysis of the query content")
    processing_time: Optional[float] = Field(None, description="Time taken to process the query in seconds")
    fallback_answer: Optional[str] = Field(None, description="Fallback answer for cross-vendor queries")


class DocumentInfo(BaseModel):
    """Model for document information."""
    name: str = Field(..., description="Document filename")
    path: str = Field(..., description="Full path to the document")
    size: int = Field(..., description="Document size in bytes")
    modified: float = Field(..., description="Last modification timestamp")


class DocumentsResponse(BaseModel):
    """Response model for document listing."""
    documents: List[DocumentInfo] = Field(..., description="List of available PDF documents")


class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str = Field(..., description="Health status of the service")
    timestamp: float = Field(..., description="Current timestamp")
    version: str = Field(..., description="API version")
    uptime: float = Field(..., description="Service uptime in seconds")


class IngestionResponse(BaseModel):
    """Response model for document ingestion."""
    status: str = Field(..., description="Ingestion status")
    message: str = Field(..., description="Ingestion result message")
    documents_processed: Optional[int] = Field(None, description="Number of documents processed")


class FastAPIQueryServer:
    """FastAPI-based server for handling PDF queries with comprehensive documentation."""

    def __init__(self, config: Config):
        """Initialize the FastAPI query server."""
        self.config = config
        self.start_time = time.time()
        self.ingestion = PDFIngestion(config)
        self.chat_db: Optional[MemoryAPI] = None

        # Initialize chat history if available
        if CHAT_HISTORY_AVAILABLE:
            try:
                self.chat_db = MemoryAPI()
                logger.info("Chat history initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize chat history: {e}")

        # Create FastAPI app with comprehensive documentation
        self.app = FastAPI(
            title="PDF Chat Appliance API",
            description="""
            **PDF Chat Appliance** - Intelligent PDF document querying and analysis system.
            
            This API provides endpoints for:
            * **Querying PDF documents** using natural language
            * **Document ingestion and management**
            * **Health monitoring and system status**
            
            ## Features
            * Semantic search across PDF documents
            * LLM-powered query responses
            * Vendor-specific content analysis
            * Chat history tracking
            * Cross-vendor integration support
            """,
            version="1.3.0",
            docs_url="/docs",
            redoc_url="/redoc",
            openapi_url="/openapi.json",
        )

        # Add CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # Setup routes
        self._setup_routes()

    def _setup_routes(self):
        """Setup FastAPI routes with comprehensive documentation."""
        
        @self.app.get(
            "/health",
            response_model=HealthResponse,
            summary="Health Check",
            description="Check the health status of the PDF Chat Appliance service.",
            tags=["System"]
        )
        async def health_check():
            """Health check endpoint with comprehensive status information."""
            return HealthResponse(
                status="healthy",
                timestamp=time.time(),
                version="1.3.0",
                uptime=time.time() - self.start_time
            )

        @self.app.post(
            "/query",
            response_model=QueryResponse,
            summary="Query PDF Documents",
            description="Query PDF documents using natural language with semantic search and LLM-powered responses.",
            tags=["Query"]
        )
        async def query(request: QueryRequest):
            """Handle PDF queries with comprehensive error handling and documentation."""
            try:
                # Get chat history for context if available
                if self.chat_db and request.document_id:
                    try:
                        _ = self.chat_db.get_messages(request.document_id)
                    except Exception as e:
                        logger.warning(f"Failed to retrieve chat history: {e}")

                # Process the query
                max_results = request.max_results or 5
                response = self._process_query(request.query, max_results)

                # Store chat history if available
                if self.chat_db and request.document_id:
                    try:
                        self.chat_db.add_message(
                            session_id=request.document_id,
                            role="user",
                            content=request.query,
                            response_time=None
                        )
                        self.chat_db.add_message(
                            session_id=request.document_id,
                            role="assistant",
                            content=response["answer"],
                            response_time=None
                        )
                    except Exception as e:
                        logger.warning(f"Failed to store chat history: {e}")

                return QueryResponse(**response)

            except Exception as e:
                logger.error(f"Query error: {e}")
                raise HTTPException(status_code=500, detail=f"Query processing failed: {str(e)}")

        @self.app.post(
            "/ingest",
            response_model=IngestionResponse,
            summary="Ingest PDF Documents",
            description="Ingest PDF documents for querying with background processing.",
            tags=["Documents"]
        )
        async def ingest_documents(background_tasks: BackgroundTasks):
            """Handle document ingestion requests with background processing."""
            try:
                background_tasks.add_task(self.ingestion.ingest_pdfs)
                
                return IngestionResponse(
                    status="success",
                    message="Document ingestion started successfully",
                    documents_processed=None
                )

            except Exception as e:
                logger.error(f"Ingestion error: {e}")
                raise HTTPException(status_code=500, detail=f"Document ingestion failed: {str(e)}")

        @self.app.get(
            "/documents",
            response_model=DocumentsResponse,
            summary="List Available Documents",
            description="List all available PDF documents that can be queried.",
            tags=["Documents"]
        )
        async def list_documents():
            """List available documents with comprehensive metadata."""
            try:
                docs_dir = self.config.docs_dir
                if not os.path.exists(docs_dir):
                    return DocumentsResponse(documents=[])

                documents = []
                for file in os.listdir(docs_dir):
                    if file.lower().endswith(".pdf"):
                        file_path = os.path.join(docs_dir, file)
                        documents.append(
                            DocumentInfo(
                                name=file,
                                path=file_path,
                                size=os.path.getsize(file_path),
                                modified=os.path.getmtime(file_path),
                            )
                        )

                return DocumentsResponse(documents=documents)

            except Exception as e:
                logger.error(f"Error listing documents: {e}")
                raise HTTPException(status_code=500, detail=f"Failed to list documents: {str(e)}")

    def _process_query(self, query_text: str, max_results: int = 5) -> Dict:
        """Process a query and return results with comprehensive error handling."""
        try:
            import platform
            if platform.system() != "Windows":
                signal.signal(signal.SIGALRM, self._timeout_handler)
                signal.alarm(45)

            try:
                index = self.ingestion.load_existing_index()
                query_engine = index.as_query_engine(
                    similarity_top_k=max_results,
                    response_mode="compact",
                )
                response = query_engine.query(query_text)
                query_analysis = self._analyze_query(query_text)

                enhanced_response = {
                    "answer": response.response,
                    "sources": [
                        {
                            "content": node.text,
                            "metadata": node.metadata,
                            "score": node.score if hasattr(node, "score") else None,
                        }
                        for node in response.source_nodes
                    ],
                    "query_analysis": query_analysis,
                    "processing_time": getattr(response, "processing_time", None),
                }

                if query_analysis["is_cross_vendor"]:
                    fallback_answer = f"""I understand you're asking about integrating {' and '.join(query_analysis['vendors'])} technologies.

While I'm having difficulty accessing the full documentation at the moment, here are some general considerations for {query_analysis['query_type']} scenarios:

1. **Compatibility**: Ensure both systems support the required protocols and data formats
2. **Authentication**: Verify authentication mechanisms are compatible
3. **Data Mapping**: Check field mappings and data type conversions
4. **Error Handling**: Implement robust error handling for cross-system failures
5. **Performance**: Monitor latency and throughput across the integration

For specific implementation details, I recommend consulting the official documentation for both {' and '.join(query_analysis['vendors'])} systems."""

                    enhanced_response["fallback_answer"] = fallback_answer

                return enhanced_response

            except TimeoutError:
                if platform.system() != "Windows":
                    signal.alarm(0)
                raise Exception("Query timed out after 45 seconds") from None
            finally:
                if platform.system() != "Windows":
                    signal.alarm(0)

        except Exception as e:
            logger.error(f"Query processing error: {e}")
            raise

    def _analyze_query(self, query_text: str) -> Dict:
        """Analyze query for vendor-specific content and query type."""
        query_lower = query_text.lower()
        vendors = []

        if "vmware" in query_lower:
            vendors.append("VMware")
        if "microsoft" in query_lower or "azure" in query_lower:
            vendors.append("Microsoft")
        if "aws" in query_lower or "amazon" in query_lower:
            vendors.append("AWS")
        if "google" in query_lower or "gcp" in query_lower:
            vendors.append("Google Cloud")

        query_type = "general"
        if any(word in query_lower for word in ["install", "setup", "configure"]):
            query_type = "installation"
        elif any(word in query_lower for word in ["integrate", "connect", "api"]):
            query_type = "integration"
        elif any(word in query_lower for word in ["troubleshoot", "error", "issue"]):
            query_type = "troubleshooting"

        return {
            "vendors": vendors,
            "is_cross_vendor": len(vendors) > 1,
            "query_type": query_type,
        }

    def _timeout_handler(self, signum, frame):
        """Handle query timeout."""
        raise TimeoutError("Query processing timed out")

    def run(self, host: str = "0.0.0.0", port: int = 5000, debug: bool = False):
        """Run the FastAPI server with uvicorn."""
        import uvicorn
        
        logger.info(f"Starting PDF Chat FastAPI Server on {host}:{port}")
        logger.info(f"API Documentation available at: http://{host}:{port}/docs")
        logger.info(f"ReDoc Documentation available at: http://{host}:{port}/redoc")
        logger.info(f"OpenAPI Schema available at: http://{host}:{port}/openapi.json")
        
        uvicorn.run(
            self.app,
            host=host,
            port=port,
            log_level="debug" if debug else "info",
            access_log=True,
        )
