# Long-Term Memory & Persistence

## Overview

The PDF Chat Appliance features a modular long-term memory layer for storing user interactions, conversation history, and document insights across sessions.

---

## Architecture

- **Modular memory package (`memory/`)**
- **ORM models:** Session, Message, DocumentInsight
- **Backends:** SQLite (default), extensible to PostgreSQL, ChromaDB, JSONL
- **Unified API:** All memory operations go through `memory/api.py`
- **Persistent storage:** `/data/` directory (configurable)

### System Diagram

```mermaid
graph TD
  A[User/Assistant Interaction] --> B[Memory API]
  B --> C[SQLite Backend]
  B --> D[ChromaDB Backend]
  B --> E[JSONL Log]
  C --> F[/data/memory.db]
  E --> G[/data/session_logs.jsonl]
```

---

## Supported Backends

- **SQLite:** Local, file-based, default for most deployments
- **PostgreSQL:** For remote or enterprise deployments (future)
- **ChromaDB:** For vector/semantic memory (already used for embeddings)
- **JSONL:** For append-only logs or export/import

---

## Data Types Stored

- **Session:** Conversation context, user ID, timestamps
- **Message:** Q&A pairs, role (user/assistant), feedback
- **Document Insight:** Summaries, key findings, tags, last accessed
- **Session Log:** (Optional) Flat log of all interactions

---

## Usage

- All persistent data is stored in `/data/` (default, configurable)
- Memory API is used by the backend for CRUD and search
- Data survives process restarts and can be exported/imported

---

## Developer Onboarding

- Add new backends by implementing the backend interface and updating `api.py`
- Use SQLAlchemy for ORM models and migrations
- See `memory/models.py`, `sqlite_backend.py`, and `api.py` for examples
- Run tests in `tests/memory/` to validate changes

---

## Configuration

- Backend and data path are set in `config.py` or via CLI
- Migration scripts can be added in `memory/migrations/` (Alembic recommended)

---

## Further Reading

- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Alembic Migrations](https://alembic.sqlalchemy.org/)
- [ChromaDB](https://www.trychroma.com/)
