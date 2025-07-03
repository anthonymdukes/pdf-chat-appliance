# 🧠 Cursor Agent Rules Index

This file lists and describes all `.mdc` agent rules in `.cursor/rules/`.

Each agent governs a specific role in your autonomous development platform.  
Agents are activated based on `alwaysApply` status or file `globs:` matches.

---

| Agent File              | Summary                                        | alwaysApply | globs present |
|-------------------------|------------------------------------------------|-------------|----------------|
| `agent-flow.mdc`        | Defines the execution sequence of all agents  | ✅           | ❌             |
| `agent-orchestrator.mdc`| Detects flow violations, reroutes execution   | ✅           | ❌             |
| `api-builder.mdc`       | Implements ingestion and chunking APIs        | ✅           | ❌ (implicitly scoped) |
| `code-review.mdc`       | Checks for code hygiene, style, modularity    | ✅           | ❌             |
| `coding-style.mdc`      | Global style and formatting guide             | ✅           | ❌             |
| `core.mdc`              | Foundation for safety, scope, and sanity      | ✅           | ❌             |
| `db-specialist.mdc`     | Owns vector DB schema and namespace rules     | ❌           | ✅             |
| `docs-maintainer.mdc`   | Maintains all user/developer markdown         | ✅           | ✅             |
| `environment.mdc`       | Resets and verifies environment setup scripts | ❌           | ✅             |
| `global-governance.mdc` | Immutable policy across all agents            | ✅           | ❌             |
| `llm-config.mdc`        | Maps models to agent roles and tasks          | ✅           | ❌             |
| `llm-specialist.mdc`    | Tunes prompts, fallbacks, and model behavior  | ❌           | ✅             |
| `observability.mdc`     | Handles logs, telemetry, trace generation     | ❌           | ✅             |
| `project-structure.mdc` | Sets file/folder boundaries per agent scope   | ✅           | ❌             |
| `prompt-strategy.mdc`   | Enforces single-task prompting and precision  | ✅           | ❌             |
| `python-engineer.mdc`   | Validates Python idioms, typing, and async    | ❌           | ✅             |
| `qa-tester.mdc`         | Owns Pytest coverage and test verification    | ✅           | ❌             |
| `repo-management.mdc`   | Manages Git structure, CI, and changelogs     | ❌           | ✅             |
| `rule-governor.mdc`     | Creates and validates `.mdc` rules            | ✅           | ❌             |
| `security-checks.mdc`   | Detects secrets, unsafe IO, and auth gaps     | ❌           | ✅             |
| `senior-dev.mdc`        | Handles architectural refactors and structure | ❌           | ✅             |
| `system-architect.mdc`  | Owns project design, folder layout, and flow  | ✅           | ❌             |
| `task-manager.mdc`      | Enforces task boundaries and status logging   | ✅           | ❌             |

---

### ✅ Rule Governance

- All rules must comply with `global-governance.mdc`
- New rules must be:
  - Proposed by `system-architect`
  - Created by `rule-governor`
  - Logged in `TASK.md` by `task-manager`
  - Indexed here by `repo-management`

---

_Last updated: 2025-07-02_

