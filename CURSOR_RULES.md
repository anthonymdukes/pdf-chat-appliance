# 📘 Cursor Rules – PDF Chat Appliance (v1.1.0-alpha)

This document describes the agent behavior, model responsibilities, execution flow, and architectural constraints for this project. It complements the `.cursorrules` file (TOML format), which is used by Cursor agents for runtime execution.

---

## 🧠 Overview

- **Agent Mode**: Multi-agent
- **Execution Strategy**: Local, self-hosted, CPU-optimized
- **Autonomy Level**: High (stack realignment mode active)
- **Vector Store**: ChromaDB with per-user/doc namespaces
- **LLM Backend**: Ollama + local embedding model

---

## 🤖 Model Assignments

| Task            | Model                             |
|-----------------|------------------------------------|
| Chunking        | `ollama:phi3`                      |
| Embedding       | `sentence-transformers:nomic-embed-text-v1.5` |
| Chat/RAG Output | `ollama:mistral`                   |

---

## 👥 Agent Roles and Responsibilities

### 🏗️ Architect

- Define architecture flow: ingestion → chunking → embedding → retrieval
- Assign models and enforce modular design
- Maintain `.cursorrules` and system folder structure

### 🛠 Builder

- Build the FastAPI ingestion pipeline
- Call `phi3` via Ollama for semantic chunking
- Call embedding model for vector generation
- Store vectors in ChromaDB under user/doc namespace
- Maintain clear function boundaries and logging

### 👀 Reviewer

- Validate modularity, logging, and error handling
- Ensure correct model usage per phase
- Enforce import hygiene and file naming standards

### ✅ Tester

- Test the full flow from upload → chunk → embed → chat
- Check for memory use, batch failure recovery, and embedding quality
- Perform regression testing and namespace isolation tests

### 📝 Logger

- Write structured logs to `/logs/{doc_id}/...`
- Track:
  - Chunking times
  - Model versions
  - Embedding latency
  - Chat inference time

### 🧾 DocWriter

- Maintain:
  - `README.md` (stack setup, usage)
  - `PLANNING.md` (architecture, constraints)
  - `TASK.md` (phases and sub-tasks)
  - `SYSTEM_OVERVIEW.md` (pipeline diagrams)

---

## 🔁 Agent Flow

> Default execution sequence for tasks:

Architect → Builder → Reviewer → Tester → Logger → DocWriter


---

## 🔒 File & Folder Governance

### Editable Files

Agents are allowed to modify:
- `README.md`
- `PLANNING.md`
- `TASK.md`
- `CURSOR_RULES.md`
- `SYSTEM_OVERVIEW.md`

### Editable Folders

Agents may create or modify:
- `api/`
- `embeddings/`
- `docker/`
- `uploads/`
- `chroma/`
- `logs/`
- `archive/`
- `session_logs/`

---

## 🧹 Environment Reset Commands

To reset the runtime state before re-deploy:

```bash
docker-compose down -v
rm -rf ./chroma ./qdrant ./uploads ./logs
ollama pull phi3
ollama pull mistral
pip install sentence-transformers
