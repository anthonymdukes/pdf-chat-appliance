# DECISION_LOG.md

## Architecture & Policy Memory

This document logs major architectural decisions, policy changes, and technical choices made by the PDF Chat Appliance team. Each entry includes the decision rationale, affected domains, and implementation status.

---

## Decision Log Entries

### **2025-07-06: Mandatory .venv Activation Policy**

**Initiator:** `@system-architect`  
**Status:** ✅ IMPLEMENTED  
**Affected Domains:** All Python development, deployment, testing

**Decision:** All Python scripts and agents must operate exclusively within the project's virtual environment (`.venv`).

**Rationale:**
- Prevents import resolution failures (`fastapi`, `uvicorn`, `pydantic`)
- Eliminates global Python interference
- Ensures agent parity across all tools and scripts
- Enables reliable pre-commit checks, tests, and deployment automation

**Implementation:**
- Added mandatory `.venv` checks to all Python files
- Updated session notes and documentation
- Installed dependencies in `.venv`
- Reduced pyright errors from 15 to 9

**Affected Files:**
- `pdfchat/fastapi_server.py`
- `scripts/enterprise_performance_test.py`
- `test_fastapi_server.py`
- `run_server.py`
- `scripts/generate_docs.py`
- `scripts/embed_all.py`
- `session_notes.md`
- `docs/DOC_CHANGELOG.md`

---

### **2025-07-06: Emoji Ban Policy Enforcement**

**Initiator:** `@docs-maintainer`  
**Status:** ✅ IMPLEMENTED  
**Affected Domains:** Documentation, scripts, configuration files

**Decision:** Emojis are strictly prohibited in all critical file types (`.py`, `.md`, `.json`, `.yaml`, `.ps1`, `.sh`, etc.).

**Rationale:**
- Breaks syntax/parsing in various file types
- Causes automation and CLI failures
- Improves machine readability
- Ensures consistent formatting across all project files

**Implementation:**
- Swept 15+ files across docs, scripts, and training directories
- Removed 50+ emojis from status indicators, headers, console output
- Fixed PowerShell linter error with `$error` variable
- Updated `DOCUMENT_RULES.md` with comprehensive policy

**Affected Files:**
- All documentation files in `/docs/`
- All script files in `/scripts/`
- Training files in `/training/`
- Configuration files

---

### **2025-07-06: Phase 4 - Intelligent Team Simulation Layer**

**Initiator:** `@system-architect`  
**Status:** 🔄 IN PROGRESS  
**Affected Domains:** All agent roles, team dynamics, collaboration

**Decision:** Implement intelligent team simulation layer with real-world engineering team dynamics.

**Rationale:**
- Transition from automation → autonomous engineering culture
- Enable intelligent collaboration, role ownership, long-term memory
- Implement peer review, sprints, and health tracking
- Create self-improving, domain-owned, feedback-driven team

**Implementation:**
- Created `OWNERS.md` for agent domain ownership mapping
- Created `docs/DECISION_LOG.md` for architecture memory
- Creating sprint planning and team health tracking
- Updating all `.mdc` files with new strategic responsibilities

**Affected Files:**
- `OWNERS.md`
- `docs/DECISION_LOG.md`
- `.ai/SPRINTS.md` (in progress)
- `docs/agent-feedback.md` (in progress)
- `docs/team-health.md` (in progress)
- All `.mdc` files in `.cursor/rules/`

---

### **2025-07-06: FastAPI Import Resolution**

**Initiator:** `@python-engineer`  
**Status:** ✅ IMPLEMENTED  
**Affected Domains:** API development, backend services

**Decision:** Install and resolve FastAPI, Uvicorn, and Pydantic dependencies within `.venv`.

**Rationale:**
- Resolve import errors in `pdfchat/fastapi_server.py`
- Enable proper type checking and development
- Ensure consistent dependency management
- Support API documentation generation

**Implementation:**
- Installed `fastapi`, `uvicorn`, `pydantic` in `.venv`
- Resolved import errors for FastAPI, Uvicorn, Pydantic
- Reduced pyright errors from 15 to 9
- Updated memory API imports (`ChatHistoryAPI` → `MemoryAPI`, `ChatMessage` → `Message`)

**Affected Files:**
- `pdfchat/fastapi_server.py`
- `test_fastapi_server.py`
- `memory/api.py`
- `memory/models.py`

---

### **2025-07-06: Memory API Refactoring**

**Initiator:** `@python-engineer`  
**Status:** ✅ IMPLEMENTED  
**Affected Domains:** Database, chat history, memory management

**Decision:** Refactor memory API imports to use correct class names and method signatures.

**Rationale:**
- Fix import errors for `ChatHistoryAPI` and `ChatMessage`
- Align with actual implementation in `memory/api.py` and `memory/models.py`
- Ensure proper method calls and data flow
- Maintain chat history functionality

**Implementation:**
- Changed `ChatHistoryAPI` → `MemoryAPI`
- Changed `ChatMessage` → `Message`
- Updated method calls (`get_history` → `get_messages`)
- Added platform check for signal handling (Windows compatibility)

**Affected Files:**
- `pdfchat/fastapi_server.py`
- `pdfchat/server.py`
- `memory/api.py`
- `memory/models.py`

---

## Decision Categories

### **Architecture Decisions**
- System design patterns
- Technology choices
- Integration approaches
- Scalability considerations

### **Policy Decisions**
- Development standards
- Code quality requirements
- Documentation policies
- Security requirements

### **Process Decisions**
- Workflow changes
- Team dynamics
- Communication protocols
- Quality gates

### **Technical Decisions**
- Dependency management
- Configuration changes
- Performance optimizations
- Bug fixes and refactoring

---

## Decision Lifecycle

1. **Proposal:** Decision is proposed with rationale
2. **Review:** Relevant agents review and provide feedback
3. **Approval:** Decision is approved by appropriate authority
4. **Implementation:** Decision is implemented across affected domains
5. **Validation:** Decision is validated and tested
6. **Documentation:** Decision is logged with full context

---

## Decision Impact Tracking

Each decision entry includes:
- **Impact Level:** Low/Medium/High
- **Rollback Plan:** How to reverse if needed
- **Success Metrics:** How to measure success
- **Review Date:** When to reassess the decision

---

**Last Updated:** 2025-07-06  
**Updated By:** `@system-architect`  
**Next Review:** 2025-07-13 