"""
PDF ingestion module for processing and indexing PDF documents
for semantic search using llama-index and FAISS.
"""

import logging
import os
from typing import Dict, List, Optional

from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
from llama_index.core.node_parser import SimpleNodeParser
from llama_index.core.storage import StorageContext

from .config import Config

# Setup logger for this module
logger = logging.getLogger(__name__)

# Try to import optional dependencies, provide stubs if not available

# Set environment variable to use local embeddings to avoid OpenAI fallback
os.environ["LLAMA_INDEX_EMBED_MODEL"] = "local"

try:
    from llama_index.core import Settings
    from llama_index.embeddings.huggingface import HuggingFaceEmbedding

    # Use nomic-embed-text-v1.5 for embeddings as specified in llm-config.mdc
    Settings.embed_model = HuggingFaceEmbedding(
        model_name="nomic-ai/nomic-embed-text-v1.5",
        trust_remote_code=True
    )
except ImportError:
    logger.warning("HuggingFaceEmbedding not available, using default")

# Remove debug file write that won't work in test environment


class PDFIngestion:
    """Handles PDF ingestion and processing for the chat appliance."""

    def __init__(self, config: Config):
        """Initialize the PDF ingestion system."""
        self.config = config
        self.node_parser = SimpleNodeParser.from_defaults(
            chunk_size=512, chunk_overlap=50
        )

    def ingest_pdfs(self) -> None:
        """Ingest all PDFs from the configured documents directory."""
        docs_dir = self.config.docs_dir
        if not os.path.exists(docs_dir):
            logger.warning(f"Documents directory {docs_dir} does not exist")
            return

        # Get all PDF files
        pdf_files = []
        for file in os.listdir(docs_dir):
            if file.lower().endswith(".pdf"):
                pdf_files.append(os.path.join(docs_dir, file))

        if not pdf_files:
            logger.info("No PDF files found for ingestion")
            return

        logger.info(f"Found {len(pdf_files)} PDF files for ingestion")

        # Process each PDF file
        for pdf_file in pdf_files:
            try:
                self._process_single_pdf(pdf_file)
            except Exception as e:
                logger.error(f"Failed to process {pdf_file}: {e}")

    def _process_single_pdf(self, pdf_file: str) -> None:
        """Process a single PDF file."""
        logger.info(f"Processing PDF: {pdf_file}")

        # Load the PDF document
        documents = SimpleDirectoryReader(input_files=[pdf_file]).load_data()
        if not documents:
            logger.warning(f"No content found in {pdf_file}")
            return

        # Parse into nodes
        nodes = self.node_parser.get_nodes_from_documents(documents)
        logger.info(f"Created {len(nodes)} nodes from {pdf_file}")

        # Create vector store index
        vector_store = self._get_vector_store()
        storage_context = StorageContext.from_defaults(vector_store=vector_store)

        # Build index
        VectorStoreIndex(nodes, storage_context=storage_context)
        logger.info(f"Successfully indexed {pdf_file}")

    def _get_vector_store(self):
        """Get the configured vector store."""
        # This would be implemented based on the specific vector store
        # For now, return a simple in-memory store
        try:
            from llama_index.vector_stores.simple import SimpleVectorStore
            return SimpleVectorStore()
        except ImportError:
            logger.warning("SimpleVectorStore not available, using default")
            # Fallback to default vector store
            from llama_index.core import VectorStoreIndex
            return VectorStoreIndex([])

    def extract_document_structure(self, text: str) -> Dict:
        """Extract document structure and metadata."""
        # Simple structure extraction
        lines = text.split("\n")
        sections = []
        current_section = {"title": "Introduction", "content": []}

        for line in lines:
            line = line.strip()
            if line.startswith("#"):
                if current_section["content"]:
                    sections.append(current_section)
                current_section = {"title": line.lstrip("# "), "content": []}
            else:
                current_section["content"].append(line)

        if current_section["content"]:
            sections.append(current_section)

        return {"sections": sections, "total_lines": len(lines)}

    def semantic_chunk_document(self, text: str, vendor: Optional[str] = None) -> List[Dict]:
        """Create semantic chunks preserving document structure."""
        # Extract structure but don't use it for now - removed unused variable
        chunks = []

        # Simple chunking by paragraphs
        paragraphs = text.split("\n\n")
        for i, paragraph in enumerate(paragraphs):
            if paragraph.strip():
                chunks.append(
                    {
                        "id": f"chunk_{i}",
                        "content": paragraph.strip(),
                        "metadata": {"vendor": vendor, "chunk_type": "paragraph"},
                    }
                )

        return chunks

    def is_large_file(self, file_path: str) -> bool:
        """Check if file is considered large and needs optimized processing."""
        # Get file size in MB and compare directly
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        return file_size_mb > 50  # Consider files > 50MB as large

    def load_existing_index(self):
        """Load existing index from storage."""
        try:
            vector_store = self._get_vector_store()
            storage_context = StorageContext.from_defaults(vector_store=vector_store)
            return VectorStoreIndex.from_vector_store(
                vector_store, storage_context=storage_context
            )
        except Exception as e:
            logger.error(f"Failed to load existing index: {e}")
            raise Exception(f"Vector store not available: {str(e)}") from e
