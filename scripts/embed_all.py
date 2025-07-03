#!/usr/bin/env python3
"""
CPU-Optimized PDF Ingestion Pipeline for Large Documents
Performance monitoring and benchmarking for PDF Chat Appliance

This script implements:
- CPU-only model optimization (phi3:cpu, all-MiniLM-L6-v2)
- Modular ingestion (1 PDF = 1 cycle)
- Detailed performance logging
- Memory usage tracking
- Token counting and timing metrics
"""

import os
import sys
import time
import json
import logging
import psutil
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.core.schema import TextNode
import qdrant_client

# Performance monitoring setup
@dataclass
class PerformanceMetrics:
    """Performance metrics for ingestion pipeline"""
    document_name: str
    document_size_mb: float
    chunk_time_seconds: float
    embedding_time_seconds: float
    total_tokens: int
    chunks_created: int
    memory_usage_mb: float
    cpu_usage_percent: float
    total_time_seconds: float
    timestamp: str

class PerformanceLogger:
    """Handles performance logging to logs/perf/ directory"""
    
    def __init__(self, log_dir: str = "logs/perf"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def log_metrics(self, metrics: PerformanceMetrics) -> None:
        """Log performance metrics to file"""
        log_file = self.log_dir / f"ingestion_{self.session_id}.md"
        
        log_entry = f"""
## Document: {metrics.document_name}
**Timestamp**: {metrics.timestamp}
**Session ID**: {self.session_id}

### Performance Metrics
- **Document Size**: {metrics.document_size_mb:.2f} MB
- **Total Time**: {metrics.total_time_seconds:.2f} seconds
- **Chunking Time**: {metrics.chunk_time_seconds:.2f} seconds
- **Embedding Time**: {metrics.embedding_time_seconds:.2f} seconds
- **Chunks Created**: {metrics.chunks_created}
- **Total Tokens**: {metrics.total_tokens:,}
- **Memory Usage**: {metrics.memory_usage_mb:.2f} MB
- **CPU Usage**: {metrics.cpu_usage_percent:.1f}%

### Performance Analysis
- **Chunking Rate**: {metrics.chunks_created / metrics.chunk_time_seconds:.1f} chunks/sec
- **Embedding Rate**: {metrics.chunks_created / metrics.embedding_time_seconds:.1f} embeddings/sec
- **Tokens per Second**: {metrics.total_tokens / metrics.total_time_seconds:.0f} tokens/sec
- **MB per Second**: {metrics.document_size_mb / metrics.total_time_seconds:.2f} MB/sec

---
"""
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)
            
    def log_summary(self, all_metrics: List[PerformanceMetrics]) -> None:
        """Log summary statistics"""
        if not all_metrics:
            return
            
        summary_file = self.log_dir / f"summary_{self.session_id}.md"
        
        total_docs = len(all_metrics)
        total_time = sum(m.total_time_seconds for m in all_metrics)
        total_tokens = sum(m.total_tokens for m in all_metrics)
        total_chunks = sum(m.chunks_created for m in all_metrics)
        avg_memory = sum(m.memory_usage_mb for m in all_metrics) / total_docs
        avg_cpu = sum(m.cpu_usage_percent for m in all_metrics) / total_docs
        
        summary = f"""
# Ingestion Performance Summary
**Session ID**: {self.session_id}
**Date**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Overall Statistics
- **Documents Processed**: {total_docs}
- **Total Processing Time**: {total_time:.2f} seconds
- **Total Tokens**: {total_tokens:,}
- **Total Chunks**: {total_chunks}
- **Average Memory Usage**: {avg_memory:.2f} MB
- **Average CPU Usage**: {avg_cpu:.1f}%

## Performance Rates
- **Average Processing Rate**: {total_docs / total_time:.2f} docs/sec
- **Average Token Rate**: {total_tokens / total_time:.0f} tokens/sec
- **Average Chunk Rate**: {total_chunks / total_time:.1f} chunks/sec

## Document Details
"""
        
        for metrics in all_metrics:
            summary += f"""
### {metrics.document_name}
- Size: {metrics.document_size_mb:.2f} MB
- Time: {metrics.total_time_seconds:.2f}s
- Chunks: {metrics.chunks_created}
- Tokens: {metrics.total_tokens:,}
"""
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(summary)

class CPUOptimizedIngestionPipeline:
    """CPU-optimized ingestion pipeline for large documents"""
    
    def __init__(self, 
                 docs_path: str = "./uploads",
                 qdrant_host: str = "localhost",
                 qdrant_port: int = 6333,
                 collection_name: str = "pdf-documents"):
        
        self.docs_path = Path(docs_path)
        self.qdrant_host = qdrant_host
        self.qdrant_port = qdrant_port
        self.collection_name = collection_name
        self.logger = PerformanceLogger()
        
        # Initialize CPU-optimized models
        self.embed_model = HuggingFaceEmbedding(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            trust_remote_code=True
        )
        
        # Optimized chunking for CPU
        self.parser = SentenceSplitter(
            chunk_size=512,  # Smaller chunks for CPU efficiency
            chunk_overlap=50,  # Minimal overlap for speed
            separator="\n\n"  # Paragraph-based splitting
        )
        
        # Initialize Qdrant connection
        self.client = qdrant_client.QdrantClient(
            host=qdrant_host, 
            port=qdrant_port
        )
        self.vector_store = QdrantVectorStore(
            client=self.client, 
            collection_name=collection_name
        )
        
    def get_system_metrics(self) -> Tuple[float, float]:
        """Get current system memory and CPU usage"""
        process = psutil.Process()
        memory_mb = process.memory_info().rss / 1024 / 1024
        cpu_percent = psutil.cpu_percent(interval=0.1)
        return memory_mb, cpu_percent
        
    def count_tokens_approximate(self, text: str) -> int:
        """Approximate token count (rough estimate)"""
        # Simple approximation: 1 token ≈ 4 characters
        return len(text) // 4
        
    def process_single_document(self, file_path: Path) -> PerformanceMetrics:
        """Process a single document with detailed timing"""
        print(f"Processing: {file_path.name}")
        
        # Get initial system metrics
        start_memory, start_cpu = self.get_system_metrics()
        start_time = time.time()
        
        # Document size
        file_size_mb = file_path.stat().st_size / 1024 / 1024
        
        # Load document
        documents = SimpleDirectoryReader(input_files=[str(file_path)]).load_data()
        if not documents:
            raise ValueError(f"No content found in {file_path}")
            
        document = documents[0]
        content = getattr(document, 'text', '')
        
        # Chunking phase
        chunk_start = time.time()
        nodes = self.parser.get_nodes_from_documents(documents)
        chunk_time = time.time() - chunk_start
        
        # Embedding phase
        embed_start = time.time()
        index = VectorStoreIndex(
            nodes, 
            vector_store=self.vector_store, 
            embed_model=self.embed_model
        )
        embed_time = time.time() - embed_start
        
        # Final metrics
        total_time = time.time() - start_time
        end_memory, end_cpu = self.get_system_metrics()
        
        # Calculate metrics
        total_tokens = sum(self.count_tokens_approximate(getattr(node, 'text', '')) for node in nodes)
        chunks_created = len(nodes)
        memory_usage = max(start_memory, end_memory)
        cpu_usage = (start_cpu + end_cpu) / 2
        
        metrics = PerformanceMetrics(
            document_name=file_path.name,
            document_size_mb=file_size_mb,
            chunk_time_seconds=chunk_time,
            embedding_time_seconds=embed_time,
            total_tokens=total_tokens,
            chunks_created=chunks_created,
            memory_usage_mb=memory_usage,
            cpu_usage_percent=cpu_usage,
            total_time_seconds=total_time,
            timestamp=datetime.now().isoformat()
        )
        
        # Log metrics
        self.logger.log_metrics(metrics)
        
        print(f"✅ Completed: {file_path.name}")
        print(f"   Time: {total_time:.2f}s | Chunks: {chunks_created} | Tokens: {total_tokens:,}")
        
        return metrics
        
    def process_all_documents(self, max_documents: Optional[int] = None) -> List[PerformanceMetrics]:
        """Process all documents in the directory with performance monitoring"""
        if not self.docs_path.exists():
            print(f"Error: Directory {self.docs_path} does not exist")
            return []
            
        # Find all PDF files
        pdf_files = list(self.docs_path.glob("*.pdf"))
        if not pdf_files:
            print(f"No PDF files found in {self.docs_path}")
            return []
            
        if max_documents:
            pdf_files = pdf_files[:max_documents]
            
        print(f"Found {len(pdf_files)} PDF files to process")
        print("=" * 60)
        
        all_metrics = []
        
        for i, pdf_file in enumerate(pdf_files, 1):
            print(f"\n[{i}/{len(pdf_files)}] Processing: {pdf_file.name}")
            
            try:
                metrics = self.process_single_document(pdf_file)
                all_metrics.append(metrics)
                
            except Exception as e:
                print(f"❌ Error processing {pdf_file.name}: {e}")
                continue
                
        # Log summary
        if all_metrics:
            self.logger.log_summary(all_metrics)
            print(f"\n✅ Processing complete! Summary logged to logs/perf/")
            
        return all_metrics

def main():
    """Main execution function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="CPU-Optimized PDF Ingestion Pipeline")
    parser.add_argument("--docs-path", default="./uploads", help="Path to documents directory")
    parser.add_argument("--qdrant-host", default="localhost", help="Qdrant host")
    parser.add_argument("--qdrant-port", type=int, default=6333, help="Qdrant port")
    parser.add_argument("--collection", default="pdf-documents", help="Qdrant collection name")
    parser.add_argument("--max-docs", type=int, help="Maximum number of documents to process")
    
    args = parser.parse_args()
    
    print("🚀 CPU-Optimized PDF Ingestion Pipeline")
    print("=" * 60)
    print(f"Documents: {args.docs_path}")
    print(f"Qdrant: {args.qdrant_host}:{args.qdrant_port}")
    print(f"Collection: {args.collection}")
    if args.max_docs:
        print(f"Max Documents: {args.max_docs}")
    print("=" * 60)
    
    # Initialize pipeline
    pipeline = CPUOptimizedIngestionPipeline(
        docs_path=args.docs_path,
        qdrant_host=args.qdrant_host,
        qdrant_port=args.qdrant_port,
        collection_name=args.collection
    )
    
    # Process documents
    start_time = time.time()
    metrics = pipeline.process_all_documents(max_documents=args.max_docs)
    total_time = time.time() - start_time
    
    if metrics:
        print(f"\n🎉 Pipeline completed successfully!")
        print(f"Total time: {total_time:.2f} seconds")
        print(f"Documents processed: {len(metrics)}")
        print(f"Performance logs: logs/perf/")
    else:
        print("\n❌ No documents were processed successfully")

if __name__ == "__main__":
    main()
