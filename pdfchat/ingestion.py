"""
PDF ingestion and vectorization for PDF Chat Appliance.

This module handles loading PDFs, chunking them, and creating embeddings
for semantic search using llama-index and ChromaDB.
"""

import os
from typing import List, Optional
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.core.storage import StorageContext
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore

from .config import Config


class PDFIngestion:
    """Handles PDF ingestion and vectorization."""
    
    def __init__(self, config: Optional[Config] = None):
        """Initialize PDF ingestion with configuration."""
        self.config = config or Config()
        self.embed_model = HuggingFaceEmbedding(
            model_name=self.config.embedding_model
        )
    
    def load_documents(self, docs_dir: Optional[str] = None) -> List:
        """Load documents from the specified directory."""
        docs_dir = docs_dir or self.config.docs_dir
        print(f"[+] Loading PDFs from {docs_dir}...")
        
        if not os.path.exists(docs_dir):
            raise FileNotFoundError(f"Documents directory not found: {docs_dir}")
        
        documents = SimpleDirectoryReader(docs_dir, recursive=True).load_data()
        print(f"[+] Loaded {len(documents)} documents")
        return documents
    
    def create_vector_store(self, documents: List) -> VectorStoreIndex:
        """Create vector store from documents."""
        print(f"[+] Converting {len(documents)} files to vector store...")
        
        vector_store = ChromaVectorStore(persist_dir=self.config.persist_dir)
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        
        index = VectorStoreIndex.from_documents(
            documents,
            storage_context=storage_context,
            embed_model=self.embed_model
        )
        
        index.storage_context.persist()
        print("[✓] Vector database updated.")
        return index
    
    def ingest_pdfs(self, docs_dir: Optional[str] = None) -> VectorStoreIndex:
        """Complete PDF ingestion workflow."""
        documents = self.load_documents(docs_dir)
        return self.create_vector_store(documents)
    
    def load_existing_index(self) -> VectorStoreIndex:
        """Load existing vector store index."""
        vector_store = ChromaVectorStore(persist_dir=self.config.persist_dir)
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        return storage_context.load_index_from_storage(storage_context) 