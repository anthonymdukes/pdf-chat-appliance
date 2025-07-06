# 🧠 Cursor Agent Rules Index

This file lists and describes all `.mdc` agent rules in `.cursor/rules/`.

Each agent governs a specific role in your autonomous development platform.
Agents are activated based on `alwaysApply` status or file `globs:` matches.

---

| Agent File | Summary | alwaysApply | globs present |
|------------|---------|:-----------:|:-------------:|
| `agent-flow.mdc` | Orchestrates agent execution sequence and handoffs | ✅ | ✅ |
| `agent-orchestrator.mdc` | Detects flow violations, drift, and reroutes agents | ✅ | ✅ |
| `api-builder.mdc` | Designs and maintains backend/API endpoints | ✅ | ✅ |
| `code-review.mdc` | Enforces code quality, reviews, and style | ✅ | ✅ |
| `coding-style.mdc` | Maintains Python and Markdown lint/format standards | ✅ | ✅ |
| `db-specialist.mdc` | Owns vector DB and persistent storage design/rules | ✅ | ✅ |
| `docs-maintainer.mdc` | Updates and enforces all documentation & diagrams | ✅ | ✅ |
| `environment.mdc` | Manages environment, scripts, .venv, dependencies | ✅ | ✅ |
| `global-governance.mdc` | Top-level compliance, escalation, and policy governor | ✅ | ✅ |
| `llm-config.mdc` | Manages LLM/model configuration and routing | ✅ | ✅ |
| `llm-specialist.mdc` | Tunes, evaluates, and optimizes all LLM and embeddings | ✅ | ✅ |
| `observability.mdc` | Handles logs, metrics, error/perf monitoring | ✅ | ✅ |
| `project-structure.mdc` | Maintains canonical repo folder/file structure | ✅ | ✅ |
| `prompt-strategy.mdc` | Governs prompt design, safety, and tuning | ✅ | ✅ |
| `python-engineer.mdc` | Owns core Python code, backend, CLI, and integration | ✅ | ✅ |
| `qa-tester.mdc` | Runs and enforces all automated and manual tests | ✅ | ✅ |
| `repo-management.mdc` | Handles git/VCS, backup, tagging, CI/CD, audit | ✅ | ✅ |
| `rule-governor.mdc` | Validates and coordinates all `.mdc` agent rules | ✅ | ✅ |
| `security-checks.mdc` | Performs security, secrets, and compliance validation | ✅ | ✅ |
| `senior-dev.mdc` | Leads complex refactors, migrations, technical debt | ✅ | ✅ |
| `system-architect.mdc` | Defines architecture, structure, and project vision | ✅ | ✅ |
| `task-manager.mdc` | Tracks story/task status and workflow progression | ✅ | ✅ |
| `workflow-pdfchat.mdc` | Enforces agile workflow and status gating | ❌ | ✅ |

---

## ✅ Rule Governance

- All rules must comply with `global-governance.mdc`
- New rules must be:
  - Proposed by `system-architect`
  - Created by `rule-governor`
  - Logged in `TASK.md` by `task-manager`
  - Indexed here by `repo-management`

---

**Last updated: 2025-07-03**
