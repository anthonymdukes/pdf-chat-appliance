# PDF Chat Appliance

## 🦾 Mission
A production-ready, self-hosted AI appliance for querying your own PDFs using state-of-the-art LLMs, embeddings, and a modern WebUI. Built for privacy, speed, and extensibility.

---

## ✨ Features
- Drop-in PDF ingestion and semantic search
- Fast, local LLM-powered Q&A (Ollama, llama-index, ChromaDB)
- WebUI and CLI modes
- Modular, extensible Python codebase
- Dockerized for easy deployment
- Configurable, with optional OVA/Proxmox support

---

## 🚀 Installation

### Prerequisites
- Python 3.9+
- Docker (for containerized deployment)
- (Optional) Ollama, llama-index, ChromaDB dependencies

### Steps
1. Clone the repo:
   ```sh
   git clone https://github.com/your-org/pdf-chat-appliance.git
   cd pdf-chat-appliance
   ```
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
3. (Optional) Start with Docker:
   ```sh
   docker-compose up --build
   ```

---

## 🛠️ Usage

### CLI (Typer-based)
```sh
python pdfchat.py ingest <pdf-folder> [--config config/default.yaml]
python pdfchat.py serve [--host 0.0.0.0 --port 5000]
python pdfchat.py config show
```

### WebUI
- Start the server: `python pdfchat.py serve`
- Open your browser to `http://localhost:5000`
- Upload PDFs and start chatting!

---

## ⚙️ Configuration
- All config options are in `config/default.yaml` (or override via CLI flags)
- See `docs/usage.md`, `docs/configuration.md`, and `docs/deployment.md` for advanced options

---

## 📦 Deployment
- Docker: `docker-compose up --build`
- OVA/Proxmox: See `docs/deployment.md` (optional)

---

## 🧠 Long-Term Memory & Persistence
PDF Chat Appliance now supports persistent storage of user interactions, conversation history, and document insights across sessions.

- **Backends:**
  - Default: SQLite (local, file-based)
  - Extensible: PostgreSQL, ChromaDB, JSONL (future)
- **Data Stored:**
  - User sessions, Q&A pairs, document insights, and logs
- **Location:**
  - All persistent data is stored in the `/data/` directory (configurable)
- **Configuration:**
  - Backend and data path can be set in `config.py` or via CLI
- **API:**
  - Unified memory API for CRUD and search operations

See [docs/memory.md](docs/memory.md) for details and developer onboarding.

---

## 📝 Documentation
- [Usage Guide](docs/usage.md)
- [Architecture Overview](docs/architecture.md)
- [Configuration Guide](docs/configuration.md)
- [Deployment Guide](docs/deployment.md)
- [Manual Installation Guide](docs/manual-install.md)
- [Long-Term Memory & Persistence](docs/memory.md)

---

## 🛠️ Installation Options

### Quick Start (OVA)
1. Download the OVA file
2. Import into VMware/VirtualBox/Proxmox
3. Start VM and access at `http://<VM_IP>`

### Manual Installation
For custom deployments or testing, see our [Manual Installation Guide](docs/manual-install.md) for step-by-step instructions on:
- VM creation (VMware, VirtualBox, Proxmox)
- Ubuntu 22.04/24.04 installation
- Python environment setup
- Ollama installation and configuration
- Service configuration and testing

### Docker
```bash
git clone https://github.com/your-org/pdf-chat-appliance.git
cd pdf-chat-appliance
docker-compose up --build
```

## 👥 Credits & License
- Built by the open-source community
- Licensed under MIT (see LICENSE)

