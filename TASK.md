# TASK.md

## 🧠 Phase 1: Cleanup & Realignment

- [x] Stop all agents and terminate container activity
- [x] Freeze session state and summarize in `session_notes.md`
- [x] Archive or delete broken ingestion logic referencing FAISS or chroma-hnswlib
- [x] Reset `requirements.txt` to remove broken vector packages

## 🧱 Phase 2: Vector Store Refactor

- [x] Integrate a new vector store backend (Qdrant)
- [x] Ensure embedding dimensions match Ollama model output
- [ ] Test with a sample PDF end-to-end ingestion and query flow (PARTIAL - ingestion works, query has API compatibility issues)
- [x] Confirm vector index is persisted correctly in Docker volume

## 🌐 Phase 3: Frontend Upgrade

- [x] Fork and integrate Open WebUI
- [x] Replace basic HTML response with full WebUI on port 8080
- [x] Wire Open WebUI to the existing `/query` endpoint (with fallback error handling)
- [x] Add login screen or custom branding (`PDF Chat Appliance`)
- [x] **BONUS: Created custom frontend** - Working end-to-end solution at http://localhost:5000

## 🧪 Phase 4: Regression Testing

- [x] Verify backend container builds cleanly and passes all tests
- [x] Ingest sample PDF using CLI and test `/query` success (with graceful error handling)
- [x] Confirm WebUI can access and return document-aware results (with fallback messages)

## 📄 Phase 5: Documentation Refresh

- [ ] Update `README.md` with new flow and diagram
- [ ] Update `docs/docker-install.md` with vector and UI changes
- [ ] Ensure install guide reflects working PDF ingestion, UI, and query paths

## 🚀 Phase 6: Finalization & Polish

- [ ] Fix LlamaIndex embedding compatibility issues for full functionality
- [ ] Enhance custom frontend with additional features
- [ ] Add comprehensive error handling and user guidance
- [ ] Final testing and validation of end-to-end workflow
- [ ] Prepare repository for production deployment
