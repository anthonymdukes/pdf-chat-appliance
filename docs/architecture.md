# Architecture Overview

## 🏗️ System Components
- **Ollama**: Provides local LLM inference for answering questions
- **llama-index**: Handles PDF chunking, embedding, and semantic search
- **Qdrant**: Vector database for storing and retrieving embeddings
- **Open WebUI**: Modern user interface for uploading PDFs and chatting
- **CLI (Typer)**: Unified command-line interface for all operations
- **Multi-Agent System**: Autonomous AI agents for development and maintenance

---

## 🔄 Data Flow
1. **Ingestion**: PDFs are chunked and embedded (llama-index), then stored in Qdrant
2. **Query**: User question is embedded, matched against Qdrant, and context is sent to Ollama for answer generation
3. **Serving**: Open WebUI/API/CLI all route through the same backend logic

---

## 🗂️ Modular Boundaries
- `pdfchat/ingestion.py`: Handles PDF loading, chunking, embedding
- `pdfchat/server.py`: API and WebUI server logic
- `pdfchat/config.py`: Centralized configuration
- `pdfchat/utils.py`: Shared helpers
- `memory/`: Long-term memory and conversation persistence
- `.cursor/rules/`: Multi-agent development system configuration

---

## 📊 System Diagram

```mermaid
graph TD
  A[PDF Upload/Open WebUI] --> B[llama-index: Chunk & Embed]
  B --> C[Qdrant: Store Vectors]
  D[User Query (Open WebUI/API/CLI)] --> E[llama-index: Embed Query]
  E --> F[Qdrant: Similarity Search]
  F --> G[Ollama: LLM Answer]
  G --> H[Response to User]
  
  I[Multi-Agent System] --> J[Development & Maintenance]
  J --> K[system-architect]
  J --> L[api-builder]
  J --> M[code-review]
  J --> N[qa-tester]
  J --> O[observability]
  J --> P[docs-maintainer]
```

---

## 🧠 Multi-Agent Development System

This project uses autonomous AI agents powered by `.cursor/rules/*.mdc` files for development:

- **system-architect**: Manages architecture, folder structure, and design
- **api-builder**: Implements ingestion and API functionality
- **code-review**: Enforces code quality and standards
- **qa-tester**: Manages testing and quality assurance
- **observability**: Handles logging, monitoring, and telemetry
- **docs-maintainer**: Maintains documentation and guides

All agents follow the execution flow defined in `agent-flow.mdc` and use models specified in `llm-config.mdc`.

---

## 🔗 Extensibility
- Swap out LLMs or vector DBs by editing `config.py` or `config/default.yaml`
- Add new endpoints or UI features by extending `server.py` or Open WebUI
- Extend agent system by adding new `.mdc` rules in `.cursor/rules/` 