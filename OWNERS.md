# OWNERS.md

## Agent Domain Ownership Map

This document defines which agents own which domains within the PDF Chat Appliance project. Each domain has a primary owner and fallback/escalation responsibilities.

---

## Core System Domains

### **PDF Ingestion Pipeline**
- **Primary Owner:** `@python-engineer`
- **Fallback:** `@api-builder`
- **Escalation:** `@system-architect`
- **Scope:** Document processing, chunking, embedding generation, vector storage

### **API & Backend Services**
- **Primary Owner:** `@api-builder`
- **Fallback:** `@python-engineer`
- **Escalation:** `@system-architect`
- **Scope:** FastAPI endpoints, middleware, authentication, rate limiting

### **Database & Vector Storage**
- **Primary Owner:** `@db-specialist`
- **Fallback:** `@python-engineer`
- **Escalation:** `@system-architect`
- **Scope:** Qdrant, SQLite, data migrations, schema management

### **LLM Integration & Prompt Management**
- **Primary Owner:** `@llm-specialist`
- **Fallback:** `@prompt-strategy`
- **Escalation:** `@system-architect`
- **Scope:** Ollama integration, prompt templates, model selection

---

## Development & Quality Domains

### **Code Quality & Standards**
- **Primary Owner:** `@coding-style`
- **Fallback:** `@code-review`
- **Escalation:** `@rule-governor`
- **Scope:** Linting, formatting, style enforcement, pre-commit hooks

### **Testing & Quality Assurance**
- **Primary Owner:** `@qa-tester`
- **Fallback:** `@python-engineer`
- **Escalation:** `@system-architect`
- **Scope:** Unit tests, integration tests, performance testing, security scanning

### **Code Review Process**
- **Primary Owner:** `@code-review`
- **Fallback:** `@qa-tester`
- **Escalation:** `@rule-governor`
- **Scope:** Pull request reviews, code quality gates, merge approvals

---

## Infrastructure & Operations Domains

### **Deployment & Monitoring**
- **Primary Owner:** `@deployment-monitor`
- **Fallback:** `@environment`
- **Escalation:** `@system-architect`
- **Scope:** Docker, service health, monitoring, alerting

### **Environment Management**
- **Primary Owner:** `@environment`
- **Fallback:** `@deployment-monitor`
- **Escalation:** `@system-architect`
- **Scope:** Virtual environments, dependency management, configuration

### **Security & Compliance**
- **Primary Owner:** `@security-checks`
- **Fallback:** `@global-governance`
- **Escalation:** `@rule-governor`
- **Scope:** Vulnerability scanning, security policies, compliance validation

---

## Project Management Domains

### **Task & Sprint Management**
- **Primary Owner:** `@task-manager`
- **Fallback:** `@agent-orchestrator`
- **Escalation:** `@system-architect`
- **Scope:** Epic/story tracking, sprint planning, velocity monitoring

### **Documentation & Knowledge Management**
- **Primary Owner:** `@docs-maintainer`
- **Fallback:** `@system-architect`
- **Escalation:** `@rule-governor`
- **Scope:** API docs, user guides, architecture documentation

### **Repository & Version Control**
- **Primary Owner:** `@repo-management`
- **Fallback:** `@task-manager`
- **Escalation:** `@system-architect`
- **Scope:** Git workflows, branching strategy, release management

---

## Governance & Coordination Domains

### **Agent Orchestration & Flow**
- **Primary Owner:** `@agent-orchestrator`
- **Fallback:** `@system-architect`
- **Escalation:** `@rule-governor`
- **Scope:** Agent coordination, workflow enforcement, deadlock resolution

### **Rule Governance & Policy**
- **Primary Owner:** `@rule-governor`
- **Fallback:** `@global-governance`
- **Escalation:** `@system-architect`
- **Scope:** Agent rule validation, policy enforcement, conflict resolution

### **Global Governance & Compliance**
- **Primary Owner:** `@global-governance`
- **Fallback:** `@rule-governor`
- **Escalation:** `@system-architect`
- **Scope:** Enterprise policies, legal compliance, ethical boundaries

---

## Specialized Domains

### **Performance Optimization**
- **Primary Owner:** `@observability`
- **Fallback:** `@python-engineer`
- **Escalation:** `@system-architect`
- **Scope:** Performance monitoring, bottleneck identification, optimization

### **Training & Knowledge Transfer**
- **Primary Owner:** `@docs-maintainer`
- **Fallback:** `@system-architect`
- **Escalation:** `@rule-governor`
- **Scope:** Agent training coordination, knowledge base maintenance

### **Architecture & System Design**
- **Primary Owner:** `@system-architect`
- **Fallback:** `@senior-dev`
- **Escalation:** `@rule-governor`
- **Scope:** System architecture, design patterns, technical decisions

---

## Escalation Matrix

### **Level 1 Escalation (Domain Issues)**
- Contact the fallback owner for the specific domain
- If unresolved within 24 hours, escalate to Level 2

### **Level 2 Escalation (Cross-Domain Issues)**
- Contact the escalation owner (usually `@system-architect`)
- If unresolved within 48 hours, escalate to Level 3

### **Level 3 Escalation (System-Wide Issues)**
- Contact `@rule-governor` or `@global-governance`
- May require human intervention or policy changes

---

## Ownership Transfer Protocol

1. **Temporary Transfer:** For planned absences or overload
   - Primary owner notifies fallback owner
   - Transfer documented in `session_notes.md`
   - Duration specified and tracked

2. **Permanent Transfer:** For role changes or domain reallocation
   - Requires approval from `@system-architect`
   - Documented in `OWNERS.md` and `session_notes.md`
   - Knowledge transfer session required

---

**Last Updated:** 2025-07-06  
**Updated By:** `@system-architect`  
**Next Review:** 2025-07-13 