"""
PDF ingestion and vectorization for PDF Chat Appliance.
Enterprise-scale multi-vendor documentation system with cross-vendor intelligence.

This module handles loading PDFs, chunking them, and creating embeddings
for semantic search using llama-index and FAISS.
"""

import os
import asyncio
import hashlib
from concurrent.futures import ThreadPoolExecutor
from typing import List, Optional, Iterator, Dict, Set
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.core.storage import StorageContext
from llama_index.core.node_parser import SimpleNodeParser
from llama_index.core.schema import TextNode

# Try to import optional dependencies, provide stubs if not available
import os
# Set environment variable to use local embeddings to avoid OpenAI fallback
os.environ["LLAMA_INDEX_EMBED_MODEL"] = "local"

try:
    from llama_index.embeddings.ollama import OllamaEmbedding
    from llama_index.core import Settings
    # Use Ollama embeddings since we're running Ollama locally
    Settings.embed_model = OllamaEmbedding(model_name="mistral")
    print(f"[DEBUG] Using Ollama embeddings with mistral model", flush=True)
except ImportError:
    print("[DEBUG] OllamaEmbedding not available, using default embedding")

try:
    from llama_index.vector_stores.qdrant import QdrantVectorStore
    from qdrant_client import QdrantClient
except ImportError:
    # For testing purposes, create stubs
    class QdrantVectorStore:
        def __init__(self, client=None, collection_name=None):
            self.client = client
            self.collection_name = collection_name
    
    class QdrantClient:
        def __init__(self, host=None, port=None):
            self.host = host
            self.port = port

from .config import Config

# Remove debug file write that won't work in test environment
# with open("/app/logs/embedding_debug.txt", "w") as dbg:
#     dbg.write("[DEBUG] Entered ingestion.py top-level\n")

class EnterpriseVendorManager:
    """Manages multi-vendor document collections and cross-vendor intelligence."""
    
    def __init__(self, config: Config):
        self.config = config
        self.enterprise_config = getattr(config, 'enterprise', {})
        self.cross_vendor_config = getattr(config, 'cross_vendor', {})
        self.vendor_collections = {}
        self.vendor_metadata = {}
        
    def detect_vendor(self, file_path: str, content: str = None) -> str:
        """Detect vendor from filename and content."""
        filename = os.path.basename(file_path).lower()
        content_lower = (content or '').lower()
        
        # Vendor detection patterns
        vendor_patterns = {
            'vmware': ['vmware', 'vcf', 'vcloud', 'esxi', 'vcenter', 'nsx', 'vsan'],
            'cisco': ['cisco', 'nexus', 'catalyst', 'ios', 'nx-os', 'aci'],
            'dell': ['dell', 'emc', 'powermax', 'unity', 'vxrail'],
            'hpe': ['hpe', 'hewlett', 'packard', 'proliant', 'synergy'],
            'juniper': ['juniper', 'junos', 'mx', 'qfx', 'srx'],
            'arista': ['arista', 'eos', 'cloudvision'],
            'nutanix': ['nutanix', 'acropolis', 'prism'],
            'pure': ['pure', 'storage', 'flasharray', 'flashblade']
        }
        
        # Check filename and content for vendor indicators
        for vendor, patterns in vendor_patterns.items():
            if any(pattern in filename for pattern in patterns):
                return vendor
            if content and any(pattern in content_lower for pattern in patterns):
                return vendor
        
        return 'unknown'
    
    def get_vendor_collection_name(self, vendor: str) -> str:
        """Get collection name for vendor."""
        return f"pdfchat_docs_{vendor}"
    
    def create_vendor_collection(self, vendor: str) -> QdrantVectorStore:
        """Create or get vendor-specific collection."""
        collection_name = self.get_vendor_collection_name(vendor)
        
        if collection_name not in self.vendor_collections:
            client = QdrantClient(host="qdrant", port=6333)
            vector_store = QdrantVectorStore(client=client, collection_name=collection_name)
            self.vendor_collections[collection_name] = vector_store
            
            # Initialize vendor metadata
            self.vendor_metadata[vendor] = {
                'document_count': 0,
                'total_chunks': 0,
                'last_updated': None,
                'topics': set()
            }
        
        return self.vendor_collections[collection_name]
    
    def get_cross_vendor_collections(self) -> List[QdrantVectorStore]:
        """Get all vendor collections for cross-vendor search."""
        return list(self.vendor_collections.values())

class EnterpriseSemanticChunker:
    """Advanced semantic chunking for enterprise documentation."""
    
    def __init__(self, config: Config):
        self.config = config
        self.chunking_config = getattr(config, 'chunking', {})
        
    def extract_document_structure(self, text: str) -> Dict:
        """Extract document structure (headers, sections, etc.)."""
        lines = text.split('\n')
        structure = {
            'headers': [],
            'sections': [],
            'tables': [],
            'code_blocks': []
        }
        
        for i, line in enumerate(lines):
            line_stripped = line.strip()
            if not line_stripped:
                continue
                
            # Detect headers (common patterns)
            if (line_stripped.isupper() and len(line_stripped) > 5 or
                line_stripped.startswith('#') or
                (len(line_stripped) > 3 and line_stripped.endswith(':') and 
                 not line_stripped.startswith(' '))):
                structure['headers'].append({
                    'text': line_stripped,
                    'line': i,
                    'level': self._estimate_header_level(line_stripped)
                })
            
            # Detect tables (simple heuristic)
            if '|' in line_stripped and line_stripped.count('|') >= 2:
                structure['tables'].append({'line': i, 'text': line_stripped})
            
            # Detect code blocks
            if line_stripped.startswith('```') or line_stripped.startswith('    '):
                structure['code_blocks'].append({'line': i, 'text': line_stripped})
        
        return structure
    
    def _estimate_header_level(self, text: str) -> int:
        """Estimate header level based on text characteristics."""
        if text.startswith('#'):
            return text.count('#')
        elif text.isupper():
            return 1 if len(text) < 50 else 2
        elif text.endswith(':'):
            return 3
        return 4
    
    def semantic_chunk_document(self, text: str, vendor: str = None) -> List[Dict]:
        """Create semantic chunks preserving document structure."""
        structure = self.extract_document_structure(text)
        chunks = []
        
        chunk_size = self.chunking_config.get('chunk_size', 384)
        chunk_overlap = self.chunking_config.get('chunk_overlap', 64)
        
        # Create chunks that respect document structure
        current_chunk = ""
        current_metadata = {'vendor': vendor, 'headers': [], 'chunk_type': 'content'}
        
        for i, char in enumerate(text):
            current_chunk += char
            
            # Check if we're at a good breaking point
            if len(current_chunk) >= chunk_size:
                # Try to break at sentence or paragraph boundary
                last_period = current_chunk.rfind('.')
                last_newline = current_chunk.rfind('\n\n')
                
                break_point = max(last_period, last_newline)
                if break_point > chunk_size - chunk_overlap:
                    # Create chunk
                    chunk_text = current_chunk[:break_point + 1]
                    chunks.append({
                        'text': chunk_text.strip(),
                        'metadata': current_metadata.copy(),
                        'start_char': i - len(current_chunk),
                        'end_char': i - len(current_chunk) + break_point
                    })
                    
                    # Prepare next chunk with overlap
                    overlap_start = max(0, break_point - chunk_overlap)
                    current_chunk = current_chunk[overlap_start:]
        
        # Add final chunk
        if current_chunk.strip():
            chunks.append({
                'text': current_chunk.strip(),
                'metadata': current_metadata.copy(),
                'start_char': len(text) - len(current_chunk),
                'end_char': len(text)
            })
        
        return chunks

class LargeFileProcessor:
    """Optimized processor for large PDF files with enterprise features."""
    
    def __init__(self, config: Config):
        self.config = config
        self.chunking_config = getattr(config, 'chunking', {})
        self.file_config = getattr(config, 'file_processing', {})
        self.vendor_manager = EnterpriseVendorManager(config)
        self.semantic_chunker = EnterpriseSemanticChunker(config)
        
        # Setup optimized node parser for large files
        self.node_parser = SimpleNodeParser.from_defaults(
            chunk_size=self.chunking_config.get('chunk_size', 384),
            chunk_overlap=self.chunking_config.get('chunk_overlap', 64)
        )
    
    def process_enterprise_document(self, file_path: str, progress_callback=None) -> Dict:
        """Process enterprise document with vendor detection and optimization."""
        try:
            # Load and analyze document
            documents = SimpleDirectoryReader(input_files=[file_path]).load_data()
            
            if not documents:
                raise ValueError(f"No content found in {file_path}")
            
            document = documents[0]
            content = getattr(document, 'text', '')
            
            # Detect vendor
            vendor = self.vendor_manager.detect_vendor(file_path, content)
            
            if progress_callback:
                progress_callback(f"Detected vendor: {vendor}")
            
            # Get vendor-specific collection
            vector_store = self.vendor_manager.create_vendor_collection(vendor)
            
            # Use semantic chunking for better enterprise document processing
            if self.chunking_config.get('semantic_chunking', True):
                chunks = self.semantic_chunker.semantic_chunk_document(content, vendor)
                
                # Convert to TextNode objects
                nodes = []
                for i, chunk in enumerate(chunks):
                    node = TextNode(
                        text=chunk['text'],
                        metadata={
                            **chunk['metadata'],
                            'vendor': vendor,
                            'source_file': os.path.basename(file_path),
                            'chunk_id': i,
                            'file_hash': hashlib.md5(file_path.encode()).hexdigest()
                        }
                    )
                    nodes.append(node)
            else:
                # Fallback to standard chunking
                nodes = self.node_parser.get_nodes_from_documents(documents)
                for node in nodes:
                    node.metadata.update({
                        'vendor': vendor,
                        'source_file': os.path.basename(file_path)
                    })
            
            if progress_callback:
                progress_callback(f"Created {len(nodes)} semantic chunks")
            
            return {
                'vendor': vendor,
                'nodes': nodes,
                'vector_store': vector_store,
                'metadata': {
                    'file_path': file_path,
                    'chunk_count': len(nodes),
                    'content_length': len(content)
                }
            }
            
        except Exception as e:
            print(f"[ERROR] Enterprise document processing failed: {e}", flush=True)
            raise

class PDFIngestion:
    """Handles PDF ingestion and vectorization."""
    
    def __init__(self, config: Optional[Config] = None):
        """Initialize PDF ingestion with configuration."""
        self.config = config or Config()
        self.large_file_processor = LargeFileProcessor(self.config)
    
    def is_large_file(self, file_path: str) -> bool:
        """Check if file is considered large and needs optimized processing."""
        max_size_mb = getattr(self.config, 'file_processing', {}).get('max_file_size_mb', 50)
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        return file_size_mb > 10  # Consider files > 10MB as large
    
    def load_documents(self, docs_dir: Optional[str] = None) -> List:
        """Load documents from the specified directory, skipping hidden/system files and validating fields."""
        docs_dir = docs_dir or self.config.docs_dir
        print(f"[+] Loading PDFs from {docs_dir}...")
        
        if not os.path.exists(docs_dir):
            raise FileNotFoundError(f"Documents directory not found: {docs_dir}")
        
        # Process multiple document types, skip hidden/system files
        supported_extensions = ['.pdf', '.txt', '.md', '.docx', '.csv', '.rtf']
        all_files = [f for f in os.listdir(docs_dir) if any(f.lower().endswith(ext) for ext in supported_extensions) and not f.startswith('.')]
        if not all_files:
            print(f"[!] No supported document files found after filtering hidden/system files. Supported types: {supported_extensions}")
            return []
        
        # Use SimpleDirectoryReader as before
        documents = SimpleDirectoryReader(docs_dir, recursive=True).load_data()
        print(f"[+] Loaded {len(documents)} documents (raw)")
        
        # Debug: print type and repr of each loaded document
        for i, doc in enumerate(documents):
            print(f"[DEBUG] Document {i}: type={type(doc)}, repr={repr(doc)}")
        
        # Validate and filter documents
        valid_documents = []
        for i, doc in enumerate(documents):
            # Defensive: check for required fields (text, id, metadata)
            text = getattr(doc, 'text', None)
            doc_id = getattr(doc, 'doc_id', None) or getattr(doc, 'id_', None) or getattr(doc, 'id', None)
            if not text or not isinstance(text, str) or not text.strip():
                print(f"[!] Skipping document {i}: missing or empty text field.")
                continue
            if not doc_id or not isinstance(doc_id, str):
                print(f"[!] Skipping document {i}: missing or invalid id field.")
                continue
            # Optionally check for other fields as needed
            valid_documents.append(doc)
        print(f"[+] {len(valid_documents)} valid documents after validation.")
        if len(valid_documents) < len(documents):
            print(f"[!] Skipped {len(documents) - len(valid_documents)} malformed or empty documents.")
        return valid_documents
    
    def create_vector_store_optimized(self, documents: List, progress_callback=None) -> VectorStoreIndex:
        """Create vector store with large file optimizations."""
        print(f"[+] Converting {len(documents)} files to vector store with optimization...")
        
        # Setup Qdrant connection
        qdrant_host = "qdrant"
        qdrant_port = 6333
        collection_name = "pdfchat_docs"
        print(f"[DEBUG] Connecting to Qdrant at {qdrant_host}:{qdrant_port}", flush=True)
        client = QdrantClient(host=qdrant_host, port=qdrant_port)
        vector_store = QdrantVectorStore(client=client, collection_name=collection_name)
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        
        # Check for large files and use optimized processing
        large_files = []
        regular_files = []
        
        for doc in documents:
            # Estimate document size (approximate)
            text_size = len(getattr(doc, 'text', ''))
            if text_size > 50000:  # Large text documents
                large_files.append(doc)
            else:
                regular_files.append(doc)
        
        if large_files:
            print(f"[+] Processing {len(large_files)} large files with optimization")
            if progress_callback:
                progress_callback(f"Processing {len(large_files)} large files")
            
            # Use optimized processing for large files
            all_nodes = []
            for doc in large_files:
                # Create temporary file for stream processing
                import tempfile
                with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tmp:
                    tmp.write(getattr(doc, 'text', ''))
                    tmp_path = tmp.name
                
                try:
                    for node in self.large_file_processor.stream_process_document(tmp_path, progress_callback):
                        all_nodes.append(node)
                finally:
                    os.unlink(tmp_path)
            
            # Create index from optimized nodes
            index = VectorStoreIndex(
                nodes=all_nodes,
                storage_context=storage_context
                # Settings.embed_model is set at import time when OllamaEmbedding is available
            )
        
        # Process regular files normally
        if regular_files:
            print(f"[+] Processing {len(regular_files)} regular files normally")
            for i, doc in enumerate(regular_files):
                doc_id = getattr(doc, 'doc_id', None) or getattr(doc, 'id_', None) or getattr(doc, 'id', None)
                text = getattr(doc, 'text', None)
                meta = getattr(doc, 'metadata', None)
                # Sanitize metadata: remove None values
                if isinstance(meta, dict):
                    sanitized_meta = {k: v for k, v in meta.items() if v is not None}
                    doc.metadata = sanitized_meta
                    print(f"[DEBUG] Document {i}: id={doc_id}, text_len={len(text) if text else 0}, sanitized_metadata={sanitized_meta}")
                else:
                    print(f"[DEBUG] Document {i}: id={doc_id}, text_len={len(text) if text else 0}, metadata={meta}")
            
            # Use standard processing for regular files
            if not large_files:  # Only create index if we didn't already create one
                index = VectorStoreIndex.from_documents(
                    regular_files,
                    storage_context=storage_context
                    # Settings.embed_model is set at import time when OllamaEmbedding is available
                )
        
        index.storage_context.persist()
        print("[✓] Qdrant vector database updated with optimizations.", flush=True)
        return index
    
    def create_vector_store(self, documents: List) -> VectorStoreIndex:
        """Create vector store from documents, with debug output and error tracing."""
        return self.create_vector_store_optimized(documents)
    
    def ingest_pdfs(self, docs_dir: Optional[str] = None) -> VectorStoreIndex:
        """Complete PDF ingestion workflow."""
        documents = self.load_documents(docs_dir)
        return self.create_vector_store(documents)
    
    def load_existing_index(self) -> VectorStoreIndex:
        """Load existing vector store index."""
        try:
            qdrant_host = "qdrant"
            qdrant_port = 6333
            collection_name = "pdfchat_docs"
            client = QdrantClient(host=qdrant_host, port=qdrant_port)
            vector_store = QdrantVectorStore(client=client, collection_name=collection_name)
            storage_context = StorageContext.from_defaults(vector_store=vector_store)
            return VectorStoreIndex.from_vector_store(vector_store, storage_context=storage_context)
        except Exception as e:
            print(f"[ERROR] Failed to load existing index: {e}", flush=True)
            raise Exception(f"Vector store not available: {str(e)}")
 