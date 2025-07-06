# LLM Specialist Knowledge Log

Use this file to track deep-dive learnings, cheat sheets, CLI examples, or key takeaways.

## Current Training Focus - 2025-07-06

### Active Responsibilities
- **RAG Loop Optimization**: Implement efficient retrieval-augmented generation for large PDF documents
- **Prompt Template Management**: Design and maintain optimized prompt templates for different use cases
- **Embedding Tuning**: Optimize embedding models and strategies for document similarity
- **Performance Monitoring**: Track and optimize LLM performance, latency, and accuracy
- **Multimodal Processing**: Support for text, image, and structured data processing

### Key Implementation Patterns

#### Document Processing Pipeline
```python
# document_processor.py
from llama_index import Document, VectorStoreIndex, ServiceContext
from llama_index.embeddings import HuggingFaceEmbedding
from llama_index.node_parser import SentenceSplitter

class DocumentProcessor:
    def __init__(self):
        self.embedding_model = HuggingFaceEmbedding("all-MiniLM-L6-v2")
        self.node_parser = SentenceSplitter(chunk_size=512, chunk_overlap=50)
        self.service_context = ServiceContext.from_defaults(
            embed_model=self.embedding_model,
            node_parser=self.node_parser
        )
    
    def process_document(self, file_path: str) -> VectorStoreIndex:
        # Load document
        documents = SimpleDirectoryReader(file_path).load_data()
        
        # Parse into nodes
        nodes = self.node_parser.get_nodes_from_documents(documents)
        
        # Create index
        index = VectorStoreIndex(nodes, service_context=self.service_context)
        return index
```

#### Query Engine with Hybrid Search
```python
# query_engine.py
from llama_index import VectorStoreIndex
from llama_index.retrievers import VectorIndexRetriever
from llama_index.query_engine import RetrieverQueryEngine

class HybridQueryEngine:
    def __init__(self, index: VectorStoreIndex):
        self.retriever = VectorIndexRetriever(
            index=index,
            similarity_top_k=5,
            vector_store_query_mode="hybrid"
        )
        self.query_engine = RetrieverQueryEngine.from_args(
            retriever=self.retriever,
            response_mode="compact"
        )
    
    def query(self, question: str) -> str:
        response = self.query_engine.query(question)
        return response.response
```

#### Prompt Template Management
```python
# prompt_templates.py
from llama_index.prompts import PromptTemplate

class PromptManager:
    def __init__(self):
        self.qa_template = PromptTemplate(
            "Context information is below.\n"
            "---------------------\n"
            "{context_str}\n"
            "---------------------\n"
            "Given the context information and no prior knowledge, "
            "answer the question: {query_str}\n"
            "Answer: "
        )
        
        self.summary_template = PromptTemplate(
            "Please provide a concise summary of the following text:\n"
            "{text}\n"
            "Summary: "
        )
    
    def get_qa_prompt(self, context: str, question: str) -> str:
        return self.qa_template.format(
            context_str=context,
            query_str=question
        )
```

### Best Practices Implemented

- **Chunking Strategies**: Semantic chunking with overlap for better context preservation
- **Retrieval Optimization**: Hybrid search combining dense and sparse retrieval
- **Response Synthesis**: Template-based responses with source attribution
- **Performance Caching**: Intelligent caching of embeddings and responses
- **Quality Evaluation**: Automated evaluation of retrieval and response quality

### Performance Optimization Strategies

#### Embedding Caching
```python
# embedding_cache.py
import hashlib
import pickle
from pathlib import Path

class EmbeddingCache:
    def __init__(self, cache_dir: str = "cache/embeddings"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def get_cache_key(self, text: str) -> str:
        return hashlib.md5(text.encode()).hexdigest()
    
    def get_embedding(self, text: str) -> List[float]:
        cache_key = self.get_cache_key(text)
        cache_file = self.cache_dir / f"{cache_key}.pkl"
        
        if cache_file.exists():
            with open(cache_file, 'rb') as f:
                return pickle.load(f)
        
        # Generate embedding and cache
        embedding = self.generate_embedding(text)
        with open(cache_file, 'wb') as f:
            pickle.dump(embedding, f)
        
        return embedding
```

### Current Focus Areas

1. **Documentation Structure Remediation**: Supporting Phase 2 consolidation efforts
2. **RAG Optimization**: Implementing efficient retrieval-augmented generation
3. **Prompt Engineering**: Creating creative and effective prompt templates
4. **GPU Integration**: Optimizing LLM performance with GPU acceleration
5. **Performance Monitoring**: Tracking and optimizing LLM performance metrics

### Recent Learnings

- **Document Loading**: Support for 100+ file formats with custom loaders
- **Text Splitting**: Intelligent chunking with overlap and metadata preservation
- **Embedding Models**: Integration with OpenAI, HuggingFace, and custom embeddings
- **Vector Stores**: Support for ChromaDB, Qdrant, Pinecone, and custom stores
- **Query Engines**: Multiple retrieval strategies (dense, sparse, hybrid)

### GPU Architecture Knowledge

#### NVIDIA GPU Architecture Mastery
- **T4 GPUs**: Entry-level inference with 16GB VRAM, perfect for small models and development
- **A100 GPUs**: Enterprise-grade with 40-80GB VRAM, ideal for large-scale deployments
- **A6000 GPUs**: Workstation class with 48GB VRAM, excellent for development and testing
- **RTX 4090**: Consumer GPU with 24GB VRAM, cost-effective for development

#### GPU Memory Management Strategies
- **Dynamic Model Loading**: Intelligent model loading based on available VRAM
- **Batch Optimization**: Adaptive batch sizes for memory constraints
- **Fallback Mechanisms**: Graceful CPU fallback when GPU unavailable
- **Performance Monitoring**: Real-time GPU utilization tracking

---

**Last Updated:** 2025-07-06  
**Status:** Active training and implementation  
**Next Review:** 2025-07-07
