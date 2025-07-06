#!/usr/bin/env python3
"""
Enterprise-Scale Document Ingestion for PDF Chat Appliance
Optimized for 10,000+ page PDF processing with parallel chunking and embedding
"""

import logging
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from queue import Queue
from typing import Dict, List, Optional

import psutil

# Try PyMuPDF first (much faster), fallback to PyPDF
try:
    import fitz  # PyMuPDF

    USE_PYMUPDF = True
except ImportError:
    import pypdf

    USE_PYMUPDF = False

from llama_index.core import Document
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.vector_stores.qdrant import QdrantVectorStore
from qdrant_client import QdrantClient

logger = logging.getLogger(__name__)


@dataclass
class ProcessingProgress:
    """Track processing progress for large documents"""

    total_pages: int
    processed_pages: int
    total_chunks: int
    processed_chunks: int
    current_file: str
    start_time: float
    estimated_completion: Optional[float] = None


class EnterpriseIngestionEngine:
    """Enterprise-scale document ingestion with parallel processing"""

    def __init__(self, config, max_workers: int = 4):
        self.config = config
        self.max_workers = max_workers
        self.progress_queue = Queue()
        self.processing_stats = {}

        # Initialize Qdrant client
        qdrant_host = os.environ.get("QDRANT_HOST", "localhost")
        qdrant_port = int(os.environ.get("QDRANT_PORT", "6333"))
        self.qdrant_client = QdrantClient(host=qdrant_host, port=qdrant_port)

        # Initialize embedding model
        self.embed_model = OllamaEmbedding(
            model_name="nomic-embed-text-v1.5", base_url="http://ollama:11434"
        )

        # Initialize vector store
        self.vector_store = QdrantVectorStore(
            client=self.qdrant_client, collection_name="enterprise_docs"
        )

        # Create collection if it doesn't exist
        self._ensure_collection_exists()

    def _ensure_collection_exists(self):
        """Ensure Qdrant collection exists with optimized settings"""
        try:
            collections = self.qdrant_client.get_collections()
            collection_names = [c.name for c in collections.collections]

            if "enterprise_docs" not in collection_names:
                from qdrant_client.models import (
                    Distance,
                    OptimizersConfigDiff,
                    VectorParams,
                )

                self.qdrant_client.create_collection(
                    collection_name="enterprise_docs",
                    vectors_config=VectorParams(
                        size=768,  # nomic-embed-text-v1.5 dimension
                        distance=Distance.COSINE,
                    ),
                    optimizers_config=OptimizersConfigDiff(
                        memmap_threshold=10000,  # Optimize for large datasets
                        default_segment_number=2,
                    ),
                )
                logger.info(
                    "Created enterprise_docs collection with optimized settings"
                )
        except Exception as e:
            logger.error(f"Error ensuring collection exists: {e}")

    def extract_text_fast(self, pdf_path: str) -> str:
        """Extract text from PDF using the fastest available method"""
        try:
            if USE_PYMUPDF:
                return self._extract_with_pymupdf(pdf_path)
            else:
                return self._extract_with_pypdf(pdf_path)
        except Exception as e:
            logger.error(f"Error extracting text from {pdf_path}: {e}")
            return ""

    def _extract_with_pymupdf(self, pdf_path: str) -> str:
        """Extract text using PyMuPDF (much faster for large PDFs)"""
        text_parts = []

        try:
            doc = fitz.open(pdf_path)
            total_pages = len(doc)

            # Process pages in parallel
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                futures = []

                for page_num in range(total_pages):
                    future = executor.submit(self._extract_page_text, doc, page_num)
                    futures.append((page_num, future))

                # Collect results in order
                for page_num, future in futures:
                    try:
                        page_text = future.result(timeout=30)  # 30s timeout per page
                        if page_text.strip():
                            text_parts.append(
                                f"--- Page {page_num + 1} ---\n{page_text}"
                            )

                        # Update progress
                        self.progress_queue.put(
                            {
                                "type": "page_processed",
                                "file": pdf_path,
                                "page": page_num + 1,
                                "total_pages": total_pages,
                            }
                        )

                    except Exception as e:
                        logger.warning(f"Error processing page {page_num + 1}: {e}")
                        continue

            doc.close()
            return "\n\n".join(text_parts)

        except Exception as e:
            logger.error(f"PyMuPDF extraction failed for {pdf_path}: {e}")
            # Fallback to PyPDF
            return self._extract_with_pypdf(pdf_path)

    def _extract_page_text(self, doc, page_num: int) -> str:
        """Extract text from a single page"""
        try:
            page = doc.load_page(page_num)
            text = page.get_text()
            return text.strip()
        except Exception as e:
            logger.warning(f"Error extracting text from page {page_num}: {e}")
            return ""

    def _extract_with_pypdf(self, pdf_path: str) -> str:
        """Fallback text extraction using PyPDF"""
        text_parts = []

        try:
            with open(pdf_path, "rb") as file:
                reader = pypdf.PdfReader(file)
                total_pages = len(reader.pages)

                for page_num in range(total_pages):
                    try:
                        page = reader.pages[page_num]
                        text = page.extract_text()
                        if text.strip():
                            text_parts.append(f"--- Page {page_num + 1} ---\n{text}")

                        # Update progress
                        self.progress_queue.put(
                            {
                                "type": "page_processed",
                                "file": pdf_path,
                                "page": page_num + 1,
                                "total_pages": total_pages,
                            }
                        )

                    except Exception as e:
                        logger.warning(f"Error processing page {page_num + 1}: {e}")
                        continue

                return "\n\n".join(text_parts)

        except Exception as e:
            logger.error(f"PyPDF extraction failed for {pdf_path}: {e}")
            return ""

    def create_chunks_parallel(
        self, text: str, chunk_size: int = 1024, chunk_overlap: int = 200
    ) -> List[str]:
        """Create chunks in parallel for better performance"""
        try:
            # Use SentenceSplitter for better semantic chunking
            splitter = SentenceSplitter(
                chunk_size=chunk_size, chunk_overlap=chunk_overlap
            )

            # Create document and split
            doc = Document(text=text)
            nodes = splitter.get_nodes_from_documents([doc])

            # Extract text from nodes
            chunks = [node.text for node in nodes if node.text.strip()]

            logger.info(f"Created {len(chunks)} chunks from text")
            return chunks

        except Exception as e:
            logger.error(f"Error creating chunks: {e}")
            return []

    def embed_chunks_parallel(
        self, chunks: List[str], batch_size: int = 10
    ) -> List[List[float]]:
        """Embed chunks in parallel batches"""
        embeddings = []

        try:
            # Process in batches for better performance
            for i in range(0, len(chunks), batch_size):
                batch = chunks[i : i + batch_size]

                # Embed batch
                batch_embeddings = self.embed_model.get_text_embedding_batch(batch)
                embeddings.extend(batch_embeddings)

                # Update progress
                self.progress_queue.put(
                    {
                        "type": "chunks_embedded",
                        "processed": len(embeddings),
                        "total": len(chunks),
                    }
                )

                logger.info(
                    f"Embedded batch {i//batch_size + 1}/{(len(chunks) + batch_size - 1)//batch_size}"
                )

            return embeddings

        except Exception as e:
            logger.error(f"Error embedding chunks: {e}")
            return []

    def store_vectors_batch(
        self, chunks: List[str], embeddings: List[List[float]], metadata: Dict
    ) -> bool:
        """Store vectors in Qdrant with batch operations"""
        try:
            # Prepare points for batch insertion
            points = []
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                point = {
                    "id": f"{metadata['file_id']}_{i}",
                    "vector": embedding,
                    "payload": {
                        "text": chunk,
                        "file_name": metadata.get("file_name", ""),
                        "chunk_index": i,
                        "total_chunks": len(chunks),
                        "created_at": time.time(),
                    },
                }
                points.append(point)

            # Batch upsert to Qdrant
            self.qdrant_client.upsert(collection_name="enterprise_docs", points=points)

            logger.info(f"Stored {len(points)} vectors in Qdrant")
            return True

        except Exception as e:
            logger.error(f"Error storing vectors: {e}")
            return False

    def process_document_enterprise(self, pdf_path: str) -> Dict:
        """Process a single document with enterprise-scale optimizations"""
        start_time = time.time()
        file_id = f"{Path(pdf_path).stem}_{int(start_time)}"

        try:
            logger.info(f"Starting enterprise processing of {pdf_path}")

            # Extract text (fastest method)
            logger.info("Extracting text from PDF...")
            text = self.extract_text_fast(pdf_path)

            if not text.strip():
                return {
                    "success": False,
                    "error": "No text extracted from PDF",
                    "file": pdf_path,
                }

            # Create chunks
            logger.info("Creating semantic chunks...")
            chunks = self.create_chunks_parallel(
                text, chunk_size=1024, chunk_overlap=200
            )

            if not chunks:
                return {
                    "success": False,
                    "error": "No chunks created from text",
                    "file": pdf_path,
                }

            # Embed chunks
            logger.info("Embedding chunks...")
            embeddings = self.embed_chunks_parallel(chunks)

            if len(embeddings) != len(chunks):
                return {
                    "success": False,
                    "error": "Embedding count mismatch",
                    "file": pdf_path,
                }

            # Store vectors
            logger.info("Storing vectors in Qdrant...")
            metadata = {
                "file_id": file_id,
                "file_name": Path(pdf_path).name,
                "file_size": os.path.getsize(pdf_path),
                "total_pages": text.count("--- Page"),
                "total_chunks": len(chunks),
            }

            storage_success = self.store_vectors_batch(chunks, embeddings, metadata)

            if not storage_success:
                return {
                    "success": False,
                    "error": "Failed to store vectors",
                    "file": pdf_path,
                }

            processing_time = time.time() - start_time

            result = {
                "success": True,
                "file": pdf_path,
                "processing_time": processing_time,
                "total_pages": metadata["total_pages"],
                "total_chunks": len(chunks),
                "chunks_per_second": (
                    len(chunks) / processing_time if processing_time > 0 else 0
                ),
                "file_size_mb": metadata["file_size"] / (1024 * 1024),
            }

            logger.info(f"Successfully processed {pdf_path} in {processing_time:.2f}s")
            return result

        except Exception as e:
            logger.error(f"Error processing {pdf_path}: {e}")
            return {"success": False, "error": str(e), "file": pdf_path}

    def ingest_pdfs_enterprise(self, docs_dir: str = None) -> Dict:
        """Ingest all PDFs with enterprise-scale processing"""
        if docs_dir is None:
            docs_dir = self.config.docs_dir

        start_time = time.time()
        results = []

        try:
            # Find all PDF files
            pdf_files = list(Path(docs_dir).glob("*.pdf"))

            if not pdf_files:
                logger.warning(f"No PDF files found in {docs_dir}")
                return {
                    "success": False,
                    "error": "No PDF files found",
                    "total_files": 0,
                }

            logger.info(f"Found {len(pdf_files)} PDF files to process")

            # Process files in parallel
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                futures = {
                    executor.submit(
                        self.process_document_enterprise, str(pdf_file)
                    ): pdf_file
                    for pdf_file in pdf_files
                }

                for future in as_completed(futures):
                    pdf_file = futures[future]
                    try:
                        result = future.result(
                            timeout=600
                        )  # 10 minute timeout per file
                        results.append(result)

                        if result["success"]:
                            logger.info(f"✅ Processed {pdf_file.name}")
                        else:
                            logger.error(
                                f"❌ Failed to process {pdf_file.name}: {result.get('error')}"
                            )

                    except Exception as e:
                        logger.error(f"❌ Error processing {pdf_file.name}: {e}")
                        results.append(
                            {"success": False, "error": str(e), "file": str(pdf_file)}
                        )

            total_time = time.time() - start_time
            successful = [r for r in results if r["success"]]
            failed = [r for r in results if not r["success"]]

            summary = {
                "success": len(failed) == 0,
                "total_files": len(pdf_files),
                "successful_files": len(successful),
                "failed_files": len(failed),
                "total_processing_time": total_time,
                "average_time_per_file": (
                    total_time / len(pdf_files) if pdf_files else 0
                ),
                "total_chunks_processed": sum(
                    r.get("total_chunks", 0) for r in successful
                ),
                "results": results,
            }

            logger.info(
                f"Enterprise ingestion complete: {len(successful)}/{len(pdf_files)} files processed"
            )
            return summary

        except Exception as e:
            logger.error(f"Error in enterprise ingestion: {e}")
            return {"success": False, "error": str(e), "total_files": 0}

    def get_processing_stats(self) -> Dict:
        """Get current processing statistics"""
        return {
            "timestamp": time.time(),
            "memory_usage_mb": psutil.Process().memory_info().rss / (1024 * 1024),
            "cpu_percent": psutil.cpu_percent(),
            "processing_stats": self.processing_stats,
        }
