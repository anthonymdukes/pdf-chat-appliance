"""
Query server for PDF Chat Appliance.
Enterprise-scale multi-vendor documentation system.

This module provides the Flask-based API server for handling PDF queries
and serving the WebUI interface.
"""

import os
import logging
from llama_index.core import Settings

# Setup logger for this module
logger = logging.getLogger(__name__)

# Try to import optional dependencies, provide stubs if not available
try:
    from llama_index.embeddings.huggingface import HuggingFaceEmbedding
    from llama_index.llms.ollama import Ollama
    # Use nomic-embed-text-v1.5 for embeddings as specified in llm-config.mdc
    Settings.embed_model = HuggingFaceEmbedding(model_name="nomic-ai/nomic-embed-text-v1.5", trust_remote_code=True)
    Settings.llm = Ollama(model="mistral", base_url="http://ollama:11434")
    logger.info("Using nomic-embed-text-v1.5 for embeddings and mistral for LLM as per llm-config.mdc")
except ImportError:
    logger.warning("HuggingFaceEmbedding/Ollama not available, using default")

from flask import Flask, request, jsonify
from typing import Optional, Dict, Any, List
from llama_index.core.storage import StorageContext
from werkzeug.exceptions import BadRequest

try:
    from qdrant_client import QdrantClient
    from llama_index.vector_stores.qdrant import QdrantVectorStore
except ImportError:
    # For testing purposes, these imports are handled in ingestion.py
    pass

from .config import Config
from .ingestion import PDFIngestion

# Import chat history if available
try:
    from memory.chat_history import ChatHistoryDB
except ImportError:
    # Create a stub for testing
    class ChatHistoryDB:
        def __init__(self):
            pass
        def get_history(self, user_id, document_id, limit=10):
            return []
        def add_message(self, user_id, document_id, message, response):
            pass

class EnterpriseCrossVendorQuery:
    """Handles cross-vendor intelligence queries for enterprise infrastructure design."""
    
    def __init__(self, config):
        self.config = config
        self.cross_vendor_config = getattr(config, 'cross_vendor', {})
        
    def parse_cross_vendor_query(self, question: str) -> Dict:
        """Parse query to identify vendors and integration requirements."""
        question_lower = question.lower()
        
        # Vendor detection in queries
        vendors_mentioned = []
        vendor_keywords = {
            'vmware': ['vmware', 'vcf', 'vcloud', 'esxi', 'vcenter', 'nsx', 'vsan'],
            'cisco': ['cisco', 'nexus', 'catalyst', 'ios', 'nx-os', 'aci'],
            'dell': ['dell', 'emc', 'powermax', 'unity', 'vxrail'],
            'hpe': ['hpe', 'hewlett', 'packard', 'proliant', 'synergy']
        }
        
        for vendor, keywords in vendor_keywords.items():
            if any(keyword in question_lower for keyword in keywords):
                vendors_mentioned.append(vendor)
        
        # Integration patterns
        integration_patterns = {
            'configuration': ['configure', 'setup', 'install', 'deploy'],
            'compatibility': ['compatible', 'support', 'work with', 'integrate'],
            'best_practices': ['best practice', 'recommend', 'should', 'optimal'],
            'troubleshooting': ['issue', 'problem', 'error', 'troubleshoot', 'fix']
        }
        
        query_type = 'general'
        for pattern_type, keywords in integration_patterns.items():
            if any(keyword in question_lower for keyword in keywords):
                query_type = pattern_type
                break
        
        return {
            'vendors': vendors_mentioned,
            'query_type': query_type,
            'is_cross_vendor': len(vendors_mentioned) > 1,
            'primary_vendor': vendors_mentioned[0] if vendors_mentioned else None
        }
    
    def build_cross_vendor_context(self, query_analysis: Dict, search_results: List) -> str:
        """Build enhanced context for cross-vendor queries."""
        context_parts = []
        
        if query_analysis['is_cross_vendor']:
            context_parts.append(f"CROSS-VENDOR INTEGRATION QUERY")
            context_parts.append(f"Vendors involved: {', '.join(query_analysis['vendors'])}")
            context_parts.append(f"Query type: {query_analysis['query_type']}")
            context_parts.append("")
        
        # Group results by vendor
        vendor_results = {}
        for result in search_results:
            vendor = getattr(result, 'metadata', {}).get('vendor', 'unknown')
            if vendor not in vendor_results:
                vendor_results[vendor] = []
            vendor_results[vendor].append(result)
        
        # Build vendor-specific sections
        for vendor, results in vendor_results.items():
            context_parts.append(f"=== {vendor.upper()} DOCUMENTATION ===")
            for result in results[:3]:  # Top 3 results per vendor
                context_parts.append(str(result))
                context_parts.append("")
        
        return "\n".join(context_parts)
    
    def enhance_cross_vendor_prompt(self, question: str, context: str, query_analysis: Dict) -> str:
        """Create enhanced prompt for cross-vendor queries."""
        base_prompt = f"""You are an expert enterprise infrastructure consultant with deep knowledge of multi-vendor integrations.

Query Analysis:
- Vendors involved: {', '.join(query_analysis['vendors']) if query_analysis['vendors'] else 'General'}
- Query type: {query_analysis['query_type']}
- Cross-vendor integration: {query_analysis['is_cross_vendor']}

Context from vendor documentation:
{context}

Question: {question}

Please provide a comprehensive answer that:
1. Addresses the specific integration between the mentioned vendors
2. Includes step-by-step configuration guidance when applicable
3. Highlights compatibility considerations and requirements
4. Mentions any known limitations or best practices
5. Provides alternative approaches if multiple options exist

Answer:"""
        
        return base_prompt

class QueryServer:
    """Flask-based query server for PDF Chat Appliance with enterprise features."""
    
    def __init__(self, config: Optional[Config] = None):
        """Initialize the query server."""
        self.config = config or Config()
        self.app = Flask(__name__)
        self.ingestion = PDFIngestion(self.config)
        self.chat_db = ChatHistoryDB()
        self.cross_vendor_query = EnterpriseCrossVendorQuery(self.config)
        self._setup_routes()
    
    def _setup_routes(self) -> None:
        """Setup Flask routes."""
        
        @self.app.errorhandler(404)
        def not_found(error):
            return jsonify({
                "error": "Endpoint not found",
                "guidance": "Please check the API documentation at / for available endpoints",
                "available_endpoints": [
                    "/health", "/stats", "/documents", "/query", "/upload", "/context"
                ]
            }), 404
        
        @self.app.errorhandler(500)
        def internal_error(error):
            logger.error(f"Internal server error: {error}")
            return jsonify({
                "error": "Internal server error",
                "guidance": "Please check the server logs for details and try again later"
            }), 500
        
        @self.app.route("/query", methods=["POST"])
        def query():
            """Handle PDF queries with cross-vendor intelligence."""
            try:
                try:
                    data = request.get_json()
                except BadRequest:
                    return jsonify({
                        "error": "Invalid JSON in request body",
                        "guidance": "Please ensure your request contains valid JSON with a 'question' field"
                    }), 400
                if not data or "question" not in data:
                    return jsonify({
                        "error": "Missing 'question' in request",
                        "guidance": "Please include a 'question' field in your JSON request",
                        "example": {
                            "question": "What is the main topic of the document?",
                            "top_k": 5,
                            "user_id": "anonymous"
                        }
                    }), 400
                question = data["question"]
                top_k = data.get("top_k", 5)  # Increased for cross-vendor queries
                user_id = data.get("user_id", "anonymous")
                document_id = data.get("document_id", None)
                
                # Parse for cross-vendor intelligence
                query_analysis = self.cross_vendor_query.parse_cross_vendor_query(question)
                
                # Retrieve chat history for context
                chat_history = self.chat_db.get_history(user_id, document_id, limit=10)
                context = "\n".join([f"User: {msg.message}\nBot: {msg.response}" for msg in chat_history])
                
                # Try to use vector store with enhanced cross-vendor search
                try:
                    # Load existing index (will need to support multi-collection search)
                    index = self.ingestion.load_existing_index()
                    
                    # Configure query engine with enhanced parameters
                    query_engine = index.as_query_engine(
                        response_mode="tree_summarize",  # Better for cross-vendor synthesis
                        similarity_top_k=top_k,
                        verbose=True
                    )
                    
                    # Enhanced prompt for cross-vendor queries
                    if query_analysis['is_cross_vendor']:
                        enhanced_question = self.cross_vendor_query.enhance_cross_vendor_prompt(
                            question, "", query_analysis
                        )
                    else:
                        enhanced_question = question
                    
                    # Process query with timeout handling
                    import signal
                    def timeout_handler(signum, frame):
                        raise TimeoutError("Query timed out")
                    
                    signal.signal(signal.SIGALRM, timeout_handler)
                    signal.alarm(45)  # Extended timeout for cross-vendor queries
                    
                    try:
                        response = query_engine.query(enhanced_question)
                        answer = str(response)
                        signal.alarm(0)  # Cancel timeout
                        
                        # Add cross-vendor context if applicable
                        if query_analysis['is_cross_vendor']:
                            answer = f"🔗 Cross-Vendor Integration Analysis ({', '.join(query_analysis['vendors'])})\n\n{answer}"
                        
                    except TimeoutError:
                        signal.alarm(0)
                        raise Exception("Query timed out after 45 seconds")
                    
                    # Enhanced response metadata
                    response_metadata = {
                        "vendors_detected": query_analysis['vendors'],
                        "query_type": query_analysis['query_type'],
                        "is_cross_vendor": query_analysis['is_cross_vendor']
                    }
                    
                    # Store chat history
                    self.chat_db.add_message(user_id, document_id, question, answer)
                    
                    return jsonify({
                        "answer": answer,
                        "question": question,
                        "metadata": response_metadata
                    })
                    
                except Exception as e:
                    logger.error(f"Query processing failed: {e}")
                    
                    # Enhanced fallback for cross-vendor queries
                    if query_analysis['is_cross_vendor']:
                        fallback_answer = f"""I understand you're asking about integrating {' and '.join(query_analysis['vendors'])} technologies. 
                        
While I'm having difficulty accessing the full documentation at the moment, here are some general considerations for {query_analysis['query_type']} scenarios:

1. **Compatibility Check**: Verify version compatibility matrices between vendors
2. **Network Requirements**: Ensure proper network connectivity and protocols
3. **Documentation**: Consult both vendors' integration guides
4. **Support**: Check if the integration is officially supported
5. **Testing**: Always test in a lab environment first

For specific configuration steps, please ensure the relevant vendor documentation has been uploaded to the system.

Technical error: {str(e)}"""
                    else:
                        fallback_answer = f"I apologize, but I'm having difficulty processing your query right now. Technical error: {str(e)}"
                    
                    return jsonify({
                        "answer": fallback_answer,
                        "question": question,
                        "warning": "Fallback response due to technical issues",
                        "metadata": query_analysis
                    })
                    
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route("/upload", methods=["POST"])
        def upload_pdfs():
            """Upload PDF files and ingest them."""
            try:
                if 'files' not in request.files:
                    return jsonify({"error": "No files provided"}), 400
                
                files = request.files.getlist('files')
                if not files or all(file.filename == '' for file in files):
                    return jsonify({"error": "No files selected"}), 400
                
                uploaded_count = 0
                supported_extensions = ['.pdf', '.txt', '.md', '.docx', '.csv', '.rtf']
                for file in files:
                    if file and any(file.filename.lower().endswith(ext) for ext in supported_extensions):
                        # Save file to documents directory
                        import os
                        docs_dir = self.config.docs_dir
                        os.makedirs(docs_dir, exist_ok=True)
                        file_path = os.path.join(docs_dir, file.filename)
                        file.save(file_path)
                        uploaded_count += 1
                
                if uploaded_count > 0:
                    # Try to ingest the documents
                    try:
                        self.ingestion.ingest_pdfs()
                        return jsonify({
                            "message": f"Successfully uploaded and processed {uploaded_count} PDF(s)",
                            "uploaded_count": uploaded_count
                        })
                    except Exception as e:
                        return jsonify({
                            "message": f"Successfully uploaded {uploaded_count} PDF(s), but processing failed: {str(e)}",
                            "uploaded_count": uploaded_count,
                            "warning": "Document processing failed - check logs for details"
                        })
                else:
                    return jsonify({"error": "No valid PDF files uploaded"}), 400
                    
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route("/context", methods=["POST"])
        def get_context():
            """Get relevant PDF context for a query (for Open WebUI integration)."""
            try:
                try:
                    data = request.get_json()
                except BadRequest:
                    return jsonify({"error": "Invalid JSON in request body"}), 400
                if not data or "query" not in data:
                    return jsonify({"error": "Missing 'query' in request"}), 400
                
                query = data["query"]
                top_k = data.get("top_k", 3)
                
                # Load existing index
                index = self.ingestion.load_existing_index()
                query_engine = index.as_query_engine()
                
                # Get relevant context
                response = query_engine.query(query)
                
                return jsonify({
                    "context": str(response),
                    "query": query,
                    "top_k": top_k,
                    "source": "PDF Chat Appliance"
                })
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route("/health", methods=["GET"])
        def health():
            """Health check endpoint."""
            return jsonify({
                "status": "healthy", 
                "service": "pdf-chat-appliance",
                "version": "1.0.0",
                "models": {
                    "embedding": "nomic-embed-text-v1.5",
                    "llm": "mistral"
                },
                "vector_store": "qdrant"
            })
        
        @self.app.route("/stats", methods=["GET"])
        def get_stats():
            """Get system statistics and document counts."""
            try:
                import os
                docs_dir = self.config.docs_dir
                if os.path.exists(docs_dir):
                    files = [f for f in os.listdir(docs_dir) if f.endswith(('.pdf', '.txt', '.md', '.docx', '.csv', '.rtf'))]
                    total_size = sum(os.path.getsize(os.path.join(docs_dir, f)) for f in files)
                else:
                    files = []
                    total_size = 0
                
                return jsonify({
                    "documents": {
                        "count": len(files),
                        "total_size_mb": round(total_size / (1024 * 1024), 2),
                        "types": {
                            "pdf": len([f for f in files if f.endswith('.pdf')]),
                            "txt": len([f for f in files if f.endswith('.txt')]),
                            "md": len([f for f in files if f.endswith('.md')]),
                            "docx": len([f for f in files if f.endswith('.docx')]),
                            "csv": len([f for f in files if f.endswith('.csv')]),
                            "rtf": len([f for f in files if f.endswith('.rtf')])
                        }
                    },
                    "system": {
                        "vector_store": "qdrant",
                        "embedding_model": "nomic-embed-text-v1.5",
                        "llm_model": "mistral"
                    }
                })
            except Exception as e:
                logger.error(f"Failed to get stats: {e}")
                return jsonify({"error": str(e)}), 500
        
        @self.app.route("/documents", methods=["GET"])
        def list_documents():
            """List all uploaded documents."""
            try:
                import os
                docs_dir = self.config.docs_dir
                if not os.path.exists(docs_dir):
                    return jsonify({"documents": []})
                
                documents = []
                for filename in os.listdir(docs_dir):
                    if filename.endswith(('.pdf', '.txt', '.md', '.docx', '.csv', '.rtf')):
                        file_path = os.path.join(docs_dir, filename)
                        stat = os.stat(file_path)
                        documents.append({
                            "name": filename,
                            "size_mb": round(stat.st_size / (1024 * 1024), 2),
                            "uploaded": stat.st_mtime,
                            "type": filename.split('.')[-1].upper()
                        })
                
                return jsonify({"documents": documents})
            except Exception as e:
                logger.error(f"Failed to list documents: {e}")
                return jsonify({"error": str(e)}), 500
        
        @self.app.route("/", methods=["GET"])
        def index():
            """API-only endpoint - redirect to Open WebUI."""
            return jsonify({
                "message": "PDF Chat Appliance API",
                "description": "This is a backend-first appliance. Use Open WebUI at http://localhost:8080 for all document chat functionality.",
                "endpoints": {
                    "health": "/health",
                    "stats": "/stats (system statistics)",
                    "documents": "/documents (list uploaded files)",
                    "query": "/query (document chat)",
                    "upload": "/upload (document ingestion)",
                    "context": "/context"
                },
                "frontend": "http://localhost:8080 (Open WebUI - PRIMARY interface)",
                "note": "All document upload and chat functionality is accessed through Open WebUI"
            })
    
    def run(self, host: Optional[str] = None, port: Optional[int] = None, debug: bool = False) -> None:
        """Run the Flask server."""
        host = host or self.config.host
        port = port or self.config.port
        
        logger.info(f"Starting PDF Chat Appliance server on {host}:{port}")
        self.app.run(host=host, port=port, debug=debug) 