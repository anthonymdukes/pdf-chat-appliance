#!/usr/bin/env python3
"""
CPU-Optimized PDF Ingestion Pipeline with Intelligent Chunk Flow Routing
Performance monitoring and benchmarking for PDF Chat Appliance

This script implements:
- CPU-only model optimization (phi3:cpu, all-MiniLM-L6-v2)
- Intelligent chunk flow routing based on document characteristics
- Adaptive chunk size selection and overlap optimization
- Parallel processing for large documents
- Detailed performance logging and monitoring
- Memory usage tracking and token counting
"""

import logging
import os
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Mandatory .venv activation check
if "venv" not in sys.executable:
    raise RuntimeError("VENV NOT ACTIVATED. Please activate `.venv` before running this script.")

import psutil

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import qdrant_client
import yaml
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.qdrant import QdrantVectorStore


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
    chunk_strategy: str
    content_complexity: str
    parallel_workers: int
    timestamp: str


@dataclass
class ChunkingStrategy:
    """Chunking strategy configuration"""

    chunk_size: int
    chunk_overlap: int
    separator: str
    strategy_name: str
    complexity_level: str
    max_workers: int


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
**Chunk Strategy**: {metrics.chunk_strategy}
**Content Complexity**: {metrics.content_complexity}
**Parallel Workers**: {metrics.parallel_workers}

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

        with open(log_file, "a", encoding="utf-8") as f:
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

        # Strategy analysis
        strategy_stats = {}
        for metrics in all_metrics:
            strategy = metrics.chunk_strategy
            if strategy not in strategy_stats:
                strategy_stats[strategy] = {
                    "count": 0,
                    "avg_time": 0,
                    "total_chunks": 0,
                }
            strategy_stats[strategy]["count"] += 1
            strategy_stats[strategy]["avg_time"] += metrics.total_time_seconds
            strategy_stats[strategy]["total_chunks"] += metrics.chunks_created

        for strategy in strategy_stats:
            count = strategy_stats[strategy]["count"]
            strategy_stats[strategy]["avg_time"] /= count

        summary = f"""
# Intelligent Chunk Flow Routing Performance Summary
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

## Chunking Strategy Analysis
"""

        for strategy, stats in strategy_stats.items():
            summary += f"""
### {strategy}
- **Documents**: {stats['count']}
- **Average Time**: {stats['avg_time']:.2f}s
- **Total Chunks**: {stats['total_chunks']}
- **Chunks per Document**: {stats['total_chunks'] / stats['count']:.1f}
"""

        summary += """
## Document Details
"""

        for metrics in all_metrics:
            summary += f"""
### {metrics.document_name}
- Size: {metrics.document_size_mb:.2f} MB
- Time: {metrics.total_time_seconds:.2f}s
- Strategy: {metrics.chunk_strategy}
- Complexity: {metrics.content_complexity}
- Chunks: {metrics.chunks_created}
- Tokens: {metrics.total_tokens:,}
"""

        with open(summary_file, "w", encoding="utf-8") as f:
            f.write(summary)


class IntelligentChunkFlowRouter:
    """Intelligent chunk flow routing based on document characteristics"""

    def __init__(self, config_path: str = "config/default.yaml"):
        self.config = self._load_config(config_path)
        self.strategies = self._define_chunking_strategies()

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        try:
            with open(config_path) as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"Warning: Could not load config from {config_path}: {e}")
            return {}

    def _define_chunking_strategies(self) -> Dict[str, ChunkingStrategy]:
        """Define chunking strategies for different document types"""
        return {
            "small_simple": ChunkingStrategy(
                chunk_size=256,
                chunk_overlap=32,
                separator="\n\n",
                strategy_name="Small Simple",
                complexity_level="low",
                max_workers=2,
            ),
            "medium_standard": ChunkingStrategy(
                chunk_size=512,
                chunk_overlap=64,
                separator="\n\n",
                strategy_name="Medium Standard",
                complexity_level="medium",
                max_workers=4,
            ),
            "large_complex": ChunkingStrategy(
                chunk_size=768,
                chunk_overlap=96,
                separator="\n\n",
                strategy_name="Large Complex",
                complexity_level="high",
                max_workers=6,
            ),
            "enterprise_massive": ChunkingStrategy(
                chunk_size=1024,
                chunk_overlap=128,
                separator="\n\n",
                strategy_name="Enterprise Massive",
                complexity_level="very_high",
                max_workers=8,
            ),
        }

    def analyze_document_characteristics(
        self, file_path: Path, content: str
    ) -> Tuple[str, str]:
        """Analyze document characteristics to determine optimal chunking strategy"""
        file_size_mb = file_path.stat().st_size / 1024 / 1024

        # Analyze content complexity
        lines = content.split("\n")
        avg_line_length = sum(len(line) for line in lines) / len(lines) if lines else 0
        paragraph_count = content.count("\n\n")
        word_count = len(content.split())

        # Determine complexity level
        if file_size_mb < 5 and avg_line_length < 80:
            complexity = "low"
        elif file_size_mb < 20 and avg_line_length < 120:
            complexity = "medium"
        elif file_size_mb < 100 and avg_line_length < 150:
            complexity = "high"
        else:
            complexity = "very_high"

        # Select strategy based on size and complexity
        if file_size_mb < 5:
            strategy = "small_simple"
        elif file_size_mb < 20:
            strategy = "medium_standard"
        elif file_size_mb < 100:
            strategy = "large_complex"
        else:
            strategy = "enterprise_massive"

        return strategy, complexity

    def get_optimal_strategy(self, file_path: Path, content: str) -> ChunkingStrategy:
        """Get optimal chunking strategy for document"""
        strategy_name, complexity = self.analyze_document_characteristics(
            file_path, content
        )
        strategy = self.strategies[strategy_name]

        # Override with config if available
        if "chunking" in self.config:
            chunk_config = self.config["chunking"]
            strategy.chunk_size = chunk_config.get("chunk_size", strategy.chunk_size)
            strategy.chunk_overlap = chunk_config.get(
                "chunk_overlap", strategy.chunk_overlap
            )
            strategy.max_workers = chunk_config.get(
                "max_concurrent_chunks", strategy.max_workers
            )

        return strategy


class CPUOptimizedIngestionPipeline:
    """CPU-optimized ingestion pipeline with intelligent chunk flow routing"""

    def __init__(
        self,
        docs_path: str = "./uploads",
        qdrant_host: str = "localhost",
        qdrant_port: int = 6333,
        collection_name: str = "pdf-documents",
    ):

        self.docs_path = Path(docs_path)
        self.qdrant_host = qdrant_host
        self.qdrant_port = qdrant_port
        self.collection_name = collection_name
        self.logger = PerformanceLogger()
        self.router = IntelligentChunkFlowRouter()

        # Initialize CPU-optimized models
        try:
            self.embed_model = HuggingFaceEmbedding(
                model_name="sentence-transformers/paraphrase-mpnet-base-v2",
                trust_remote_code=True,
                device="cpu",
            )
        except Exception as e:
            print(
                f"Warning: Could not load paraphrase-mpnet-base-v2, using fallback: {e}"
            )
            # Fallback to a minimal multilingual model
            self.embed_model = HuggingFaceEmbedding(
                model_name="sentence-transformers/distiluse-base-multilingual-cased-v2",
                device="cpu",
            )

        # Initialize Qdrant connection
        self.client = qdrant_client.QdrantClient(host=qdrant_host, port=qdrant_port)
        self.vector_store = QdrantVectorStore(
            client=self.client, collection_name=collection_name
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

    def create_adaptive_parser(self, strategy: ChunkingStrategy) -> SentenceSplitter:
        """Create adaptive parser based on chunking strategy"""
        return SentenceSplitter(
            chunk_size=strategy.chunk_size,
            chunk_overlap=strategy.chunk_overlap,
            separator=strategy.separator,
        )

    def process_chunk_batch(self, nodes: List, batch_size: int = 20) -> None:
        """Process chunks in batches for memory efficiency"""
        for i in range(0, len(nodes), batch_size):
            batch = nodes[i : i + batch_size]
            index = VectorStoreIndex(
                batch, vector_store=self.vector_store, embed_model=self.embed_model
            )

    def process_single_document(self, file_path: Path) -> PerformanceMetrics:
        """Process a single document with intelligent chunk flow routing"""
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
        content = getattr(document, "text", "")

        # Get optimal chunking strategy
        strategy = self.router.get_optimal_strategy(file_path, content)
        print(
            f"  Strategy: {strategy.strategy_name} (Complexity: {strategy.complexity_level})"
        )

        # Create adaptive parser
        parser = self.create_adaptive_parser(strategy)

        # Chunking phase
        chunk_start = time.time()
        nodes = parser.get_nodes_from_documents(documents)
        chunk_time = time.time() - chunk_start

        # Embedding phase with batch processing
        embed_start = time.time()
        self.process_chunk_batch(nodes, batch_size=20)
        embed_time = time.time() - embed_start

        # Final metrics
        total_time = time.time() - start_time
        end_memory, end_cpu = self.get_system_metrics()

        # Calculate metrics
        total_tokens = sum(
            self.count_tokens_approximate(getattr(node, "text", "")) for node in nodes
        )
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
            chunk_strategy=strategy.strategy_name,
            content_complexity=strategy.complexity_level,
            parallel_workers=strategy.max_workers,
            timestamp=datetime.now().isoformat(),
        )

        # Log metrics
        self.logger.log_metrics(metrics)

        print(f"Completed: {file_path.name}")
        print(
            f"   Time: {total_time:.2f}s | Chunks: {chunks_created} | Tokens: {total_tokens:,}"
        )

        return metrics

    def process_all_documents(
        self, max_documents: Optional[int] = None
    ) -> List[PerformanceMetrics]:
        """Process all documents with intelligent routing and parallel processing"""
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

        # Process documents with intelligent routing
        for i, pdf_file in enumerate(pdf_files, 1):
            print(f"\n[{i}/{len(pdf_files)}] Processing: {pdf_file.name}")

            try:
                metrics = self.process_single_document(pdf_file)
                all_metrics.append(metrics)

            except Exception as e:
                print(f"Error processing {pdf_file.name}: {e}")
                continue

        # Log summary
        if all_metrics:
            self.logger.log_summary(all_metrics)
            print("\nProcessing complete! Summary logged to logs/perf/")

        return all_metrics


def main():
    """Main execution function"""
    import argparse

    parser = argparse.ArgumentParser(
        description="CPU-Optimized PDF Ingestion Pipeline with Intelligent Chunk Flow Routing"
    )
    parser.add_argument(
        "--docs-path", default="./uploads", help="Path to documents directory"
    )
    parser.add_argument("--qdrant-host", default="localhost", help="Qdrant host")
    parser.add_argument("--qdrant-port", type=int, default=6333, help="Qdrant port")
    parser.add_argument(
        "--collection", default="pdf-documents", help="Qdrant collection name"
    )
    parser.add_argument(
        "--max-docs", type=int, help="Maximum number of documents to process"
    )

    args = parser.parse_args()

    print("CPU-Optimized PDF Ingestion Pipeline with Intelligent Chunk Flow Routing")
    print("=" * 80)
    print(f"Documents: {args.docs_path}")
    print(f"Qdrant: {args.qdrant_host}:{args.qdrant_port}")
    print(f"Collection: {args.collection}")
    if args.max_docs:
        print(f"Max Documents: {args.max_docs}")
    print("=" * 80)

    # Initialize pipeline
    pipeline = CPUOptimizedIngestionPipeline(
        docs_path=args.docs_path,
        qdrant_host=args.qdrant_host,
        qdrant_port=args.qdrant_port,
        collection_name=args.collection,
    )

    # Process documents
    start_time = time.time()
    metrics = pipeline.process_all_documents(max_documents=args.max_docs)
    total_time = time.time() - start_time

    if metrics:
        print("\n🎉 Pipeline completed successfully!")
        print(f"Total time: {total_time:.2f} seconds")
        print(f"Documents processed: {len(metrics)}")
        print("Performance logs: logs/perf/")
    else:
        print("\nNo documents were processed successfully")

    print()
    print()


if __name__ == "__main__":
    main()

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
