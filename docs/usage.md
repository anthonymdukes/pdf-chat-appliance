# Usage Guide

## 📥 PDF Ingestion Workflow

1. Place your PDFs in a folder (e.g., `./pdfs`)
2. Ingest with CLI:

   ```sh
   python pdfchat.py ingest ./pdfs
   ```

3. PDFs are chunked, embedded, and indexed for semantic search.

---

## WebUI Usage

- Start the server:

  ```sh
  python pdfchat.py serve
  ```

- Open your browser to [http://localhost:8000](http://localhost:8000)
- Upload PDFs, ask questions, and get instant answers.

---

## 🖧 API/Endpoint Access

- Default API endpoint: `POST /query`
- Example request:

  ```json
  {
    "question": "What is the main topic of the document?",
    "top_k": 3
  }
  ```

- Response:

  ```json
  {
    "answers": ["...", "...", "..."]
  }
  ```

---

## 📝 Sample Queries

- "Summarize the attached PDF."
- "List all key findings."
- "What are the main risks mentioned?"

---

## Advanced CLI Options

- `--config`: Specify a custom config file
- `--host`, `--port`: Change server binding
- See `python pdfchat.py --help` for all commands
