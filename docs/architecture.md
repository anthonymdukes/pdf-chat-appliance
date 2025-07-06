Generated: 2025-01-27 23:59:00

# Architecture Overview

## System Components

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

## Modular Boundaries

- `pdfchat/ingestion.py`: Handles PDF loading, chunking, embedding
- `pdfchat/server.py`: API and WebUI server logic
- `pdfchat/config.py`: Centralized configuration
- `pdfchat/utils.py`: Shared helpers
- `memory/`: Long-term memory and conversation persistence
- `.cursor/rules/`: Multi-agent development system configuration

---

## 📊 System Diagram

```mermaid
graph TB
    %% Title
    title["PDF Chat Appliance Architecture"]
    
    %% User Interface Layer
    subgraph UI["User Interface Layer"]
        Web[Web UI (Flask)]
        CLI[CLI (Typer)]
        API[REST API (FastAPI)]
    end
    
    %% Ingestion Pipeline
    subgraph IP["Ingestion Pipeline"]
        PU[PDF Upload & Validation]
        SC[Semantic Chunking (phi3:cpu)]
        EG[Embedding Generation (all-MiniLM-L6-v2)]
        VS[Vector Storage (Qdrant)]
    end
    
    %% Query Processing
    subgraph QP["Query Processing"]
        QI[Query Input & Preprocessing]
        SS[Similarity Search (Qdrant)]
        CA[Context Assembly & RAG]
    end
    
    %% LLM Layer
    subgraph LLM["LLM Layer"]
        OL[Ollama (Local LLMs)]
        MS[Model Selection (phi3, mistral, llama2)]
        RG[Response Generation]
    end
    
    %% Data Storage
    subgraph DS["Data Storage"]
        QD[Qdrant Vector Database]
        SQL[SQLite (Metadata & Logs)]
        FS[File Storage (PDFs, Configs)]
    end
    
    %% Observability
    subgraph OB["Observability"]
        SL[Structured Logging]
        PM[Performance Metrics]
        HM[Health Monitoring]
    end
    
    %% Configuration
    subgraph CF["Configuration"]
        YC[YAML Configuration]
        EV[Environment Variables]
        AR[Agent Rules (.mdc)]
    end
    
    %% Data Flow Arrows
    %% User Interface to Ingestion
    Web --> PU
    CLI --> PU
    API --> PU
    
    %% User Interface to Query Processing
    Web --> QI
    CLI --> QI
    API --> QI
    
    %% Ingestion to Data Storage
    PU --> QD
    SC --> QD
    EG --> QD
    VS --> QD
    
    %% Query Processing to Data Storage
    QI --> QD
    SS --> QD
    CA --> QD
    
    %% Query Processing to LLM Layer
    CA --> OL
    CA --> MS
    MS --> RG
    
    %% LLM Layer to User Interface
    RG --> Web
    RG --> CLI
    RG --> API
    
    %% Observability Connections (dashed)
    OB -.-> IP
    OB -.-> QP
    OB -.-> LLM
    
    %% Configuration Connections (dashed)
    CF -.-> IP
    CF -.-> QP
    CF -.-> LLM
    
    %% Styling
    classDef ui fill:#dae8fc,stroke:#6c8ebf,stroke-width:2px
    classDef ingestion fill:#fff2cc,stroke:#d6b656,stroke-width:2px
    classDef query fill:#d5e8d4,stroke:#82b366,stroke-width:2px
    classDef llm fill:#e1d5e7,stroke:#9673a6,stroke-width:2px
    classDef storage fill:#f8cecc,stroke:#b85450,stroke-width:2px
    classDef observability fill:#ffe6cc,stroke:#d79b00,stroke-width:2px
    classDef config fill:#f5f5f5,stroke:#666666,stroke-width:2px
    
    class UI,Web,CLI,API ui
    class IP,PU,SC,EG,VS ingestion
    class QP,QI,SS,CA query
    class LLM,OL,MS,RG llm
    class DS,QD,SQL,FS storage
    class OB,SL,PM,HM observability
    class CF,YC,EV,AR config 
```

---

## Multi-Agent Development System

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
