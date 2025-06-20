# PDF Chat Appliance

A lightweight, self-hosted AI assistant that runs entirely on CPU and lets you query large PDFs using natural language.

---

## 🧱 Tech Stack

- Ubuntu Server 24.04 (OVA ready)
- Ollama (LLM inference engine)
- Open WebUI (chat interface)
- llama-index + ChromaDB (document indexing)
- CPU-only setup — no GPU required

---

## 📁 How to Use

1. Drop PDFs into the `documents/` folder
2. Run:
   ```bash
   python3 load_all.py
```

3. Start the query server:

   ```bash
   python3 query_server.py
   ```
4. Access the web UI at: `http://<host>:3000`
5. Chat with your documents!

---

## 🔁 Optional Enhancements

* Add Samba share to expose `/documents`
* Add cron or inotify trigger to auto-load new PDFs
* Deploy as OVA from Proxmox or VirtualBox

