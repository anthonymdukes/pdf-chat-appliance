# Architecture Overview

## 🏗️ System Components
- **Ollama**: Provides local LLM inference for answering questions
- **llama-index**: Handles PDF chunking, embedding, and semantic search
- **ChromaDB**: Vector database for storing and retrieving embeddings
- **WebUI**: User interface for uploading PDFs and chatting
- **CLI (Typer)**: Unified command-line interface for all operations

---

## 🔄 Data Flow
1. **Ingestion**: PDFs are chunked and embedded (llama-index), then stored in ChromaDB
2. **Query**: User question is embedded, matched against ChromaDB, and context is sent to Ollama for answer generation
3. **Serving**: WebUI/API/CLI all route through the same backend logic

---

## 🗂️ Modular Boundaries
- `pdfchat/ingestion.py`: Handles PDF loading, chunking, embedding
- `pdfchat/server.py`: API and WebUI server logic
- `pdfchat/config.py`: Centralized configuration
- `pdfchat/utils.py`: Shared helpers

---

## 📊 System Diagram

```mermaid
graph TD
  A[PDF Upload/CLI] --> B[llama-index: Chunk & Embed]
  B --> C[ChromaDB: Store Vectors]
  D[User Query (WebUI/API/CLI)] --> E[llama-index: Embed Query]
  E --> F[ChromaDB: Similarity Search]
  F --> G[Ollama: LLM Answer]
  G --> H[Response to User]
```

---

## 🔗 Extensibility
- Swap out LLMs or vector DBs by editing `config.py` or `config/default.yaml`
- Add new endpoints or UI features by extending `server.py` or WebUI 