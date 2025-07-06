"""
Flask-based query server for PDF Chat Appliance.

Provides REST API endpoints for querying ingested PDF documents
using semantic search and LLM-based responses.
"""

import logging
import os
import signal
import time
import logging
import platform
from typing import Dict, List, Optional

from flask import Flask, jsonify, request
from werkzeug.exceptions import BadRequest

# Qdrant client import removed as it was unused
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


class QueryServer:
    """Flask-based server for handling PDF queries."""

    def __init__(self, config: Config):
        """Initialize the query server."""
        self.config = config
        self.app = Flask(__name__)
        self.ingestion = PDFIngestion(config)
        self.chat_db: Optional[MemoryAPI] = None

        # Initialize chat history if available
        if CHAT_HISTORY_AVAILABLE:
            try:
                self.chat_db = MemoryAPI()
                logger.info("Chat history initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize chat history: {e}")

        # Setup routes
        self._setup_routes()

    def _setup_routes(self):
        """Setup Flask routes."""
        self.app.route("/health")(self.health_check)
        self.app.route("/query", methods=["POST"])(self.query)
        self.app.route("/ingest", methods=["POST"])(self.ingest_documents)
        self.app.route("/documents", methods=["GET"])(self.list_documents)

    def health_check(self):
        """Health check endpoint."""
        return jsonify({"status": "healthy", "timestamp": time.time()})

    def query(self):
        """Handle PDF queries."""
        try:
            data = request.get_json()
            if not data:
                raise BadRequest("No JSON data provided")

            query_text = data.get("query")
            if not query_text:
                raise BadRequest("No query text provided")

            user_id = data.get("user_id", "default")
            document_id = data.get("document_id")
            max_results = data.get("max_results", 5)

            # Get chat history for context if available
            if self.chat_db and document_id:
                try:
                    # Retrieve chat history for context (stored but not used in current implementation)
                    # Note: Using document_id as session_id for now
                    _ = self.chat_db.get_messages(document_id)
                except Exception as e:
                    logger.warning(f"Failed to retrieve chat history: {e}")

            # Process the query
            response = self._process_query(query_text, max_results)

            # Store chat history if available
            if self.chat_db and document_id:
                try:
                    self.chat_db.add_message(
                        session_id=document_id,
                        role="user",
                        content=query_text,
                        response_time=None
                    )
                    self.chat_db.add_message(
                        session_id=document_id,
                        role="assistant", 
                        content=response["answer"],
                        response_time=None
                    )
                except Exception as e:
                    logger.warning(f"Failed to store chat history: {e}")

            return jsonify(response)

        except BadRequest as e:
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            logger.error(f"Query error: {e}")
            return jsonify({"error": "Internal server error"}), 500

    def _process_query(self, query_text: str, max_results: int = 5) -> Dict:
        """Process a query and return results."""
        try:
            # Set timeout for query processing (Unix/Linux only)
            if platform.system() != "Windows":
                signal.signal(signal.SIGALRM, self._timeout_handler)
                signal.alarm(45)  # 45 second timeout

            try:
                # Load existing index
                index = self.ingestion.load_existing_index()

                # Create query engine
                query_engine = index.as_query_engine(
                    similarity_top_k=max_results,
                    response_mode="compact",
                )

                # Execute query
                response = query_engine.query(query_text)

                # Analyze query for vendor-specific content
                query_analysis = self._analyze_query(query_text)

                # Enhanced response with metadata
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

                # Add vendor-specific fallback if needed
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

            # Enhanced response metadata
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

        # Check for vendor mentions
        if "vmware" in query_lower:
            vendors.append("VMware")
        if "microsoft" in query_lower or "azure" in query_lower:
            vendors.append("Microsoft")
        if "aws" in query_lower or "amazon" in query_lower:
            vendors.append("AWS")
        if "google" in query_lower or "gcp" in query_lower:
            vendors.append("Google Cloud")

        # Determine query type
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

    def ingest_documents(self):
        """Handle document ingestion requests."""
        try:
            data = request.get_json()
            if not data:
                raise BadRequest("No JSON data provided")

            # Process the ingestion
            self.ingestion.ingest_pdfs()

            return jsonify({"status": "success", "message": "Documents ingested successfully"})

        except BadRequest as e:
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            logger.error(f"Ingestion error: {e}")
            return jsonify({"error": "Internal server error"}), 500

    def list_documents(self):
        """List available documents."""
        try:
            docs_dir = self.config.docs_dir
            if not os.path.exists(docs_dir):
                return jsonify({"documents": []})

            documents = []
            for file in os.listdir(docs_dir):
                if file.lower().endswith(".pdf"):
                    file_path = os.path.join(docs_dir, file)
                    documents.append(
                        {
                            "name": file,
                            "path": file_path,
                            "size": os.path.getsize(file_path),
                            "modified": os.path.getmtime(file_path),
                        }
                    )

            return jsonify({"documents": documents})

        except Exception as e:
            logger.error(f"Error listing documents: {e}")
            return jsonify({"error": "Internal server error"}), 500

    def run(self, host: str = "0.0.0.0", port: int = 5000, debug: bool = False):
        """Run the Flask server."""
        logger.info(f"Starting PDF Chat Server on {host}:{port}")
        self.app.run(host=host, port=port, debug=debug)
