"""
Query server for PDF Chat Appliance.

This module provides the Flask-based API server for handling PDF queries
and serving the WebUI interface.
"""

from flask import Flask, request, jsonify
from typing import Optional, Dict, Any
from llama_index.core import StorageContext, load_index_from_storage
from llama_index.vector_stores.chroma import ChromaVectorStore

from .config import Config
from .ingestion import PDFIngestion


class QueryServer:
    """Flask-based query server for PDF Chat Appliance."""
    
    def __init__(self, config: Optional[Config] = None):
        """Initialize the query server."""
        self.config = config or Config()
        self.app = Flask(__name__)
        self.ingestion = PDFIngestion(self.config)
        self._setup_routes()
    
    def _setup_routes(self) -> None:
        """Setup Flask routes."""
        
        @self.app.route("/query", methods=["POST"])
        def query():
            """Handle PDF queries."""
            try:
                data = request.get_json()
                if not data or "question" not in data:
                    return jsonify({"error": "Missing 'question' in request"}), 400
                
                question = data["question"]
                top_k = data.get("top_k", 3)
                
                # Load existing index
                index = self.ingestion.load_existing_index()
                query_engine = index.as_query_engine()
                
                # Process query
                response = query_engine.query(question)
                
                return jsonify({
                    "answer": str(response),
                    "question": question,
                    "top_k": top_k
                })
                
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route("/health", methods=["GET"])
        def health():
            """Health check endpoint."""
            return jsonify({"status": "healthy", "service": "pdf-chat-appliance"})
        
        @self.app.route("/", methods=["GET"])
        def index():
            """Simple index page."""
            return """
            <h1>PDF Chat Appliance</h1>
            <p>API is running. Use POST /query to ask questions about your PDFs.</p>
            <p>Example: curl -X POST http://localhost:5000/query -H "Content-Type: application/json" -d '{"question": "What is this document about?"}'</p>
            """
    
    def run(self, host: Optional[str] = None, port: Optional[int] = None, debug: bool = False) -> None:
        """Run the Flask server."""
        host = host or self.config.host
        port = port or self.config.port
        
        print(f"[+] Starting PDF Chat Appliance server on {host}:{port}")
        self.app.run(host=host, port=port, debug=debug) 