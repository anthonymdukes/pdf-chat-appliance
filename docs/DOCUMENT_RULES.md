# DOCUMENT_RULES.md

## Document Formatting & Emoji Policy (Effective 2025-07-06)

This file defines the authoritative formatting, emoji, and documentation hygiene rules for the PDF Chat Appliance project. All contributors and agents must comply.

---

## 🚫 Restricted File Types (Emoji Ban)

Emojis are strictly prohibited in the following file types:

| File Type/Extension | Reason | Examples |
|---------------------|--------|----------|
| `.py`               | Breaks syntax/parsing | Python, pytest, Ruff |
| `.sh`, `.ps1`       | Breaks CLI parsing    | bash, PowerShell     |
| `.json`             | Invalid encoding      | OpenAPI, VS Code    |
| `.yaml`, `.yml`     | Invalid indentation   | GitHub Actions, K8s |
| `.toml`             | Type errors/crash     | pyproject.toml      |
| `.ini`              | Legacy parsing issues | dotenv, Windows     |
| `.env`              | Breaks env parsing    | Docker, Python      |
| `.mdc`              | Breaks rule engine    | Cursor, agent rules |
| `.md` (all Markdown)| Automation/CLI risk   | README, learned.md  |
| `README.md`         | CLI/badge failures    | Main project doc    |
| `learned.md`        | Machine readability   | Agent logs          |
| `TRAINING.md`       | Machine readability   | Training log        |

---

## Emoji-Safe Zones (Allowed Only In):
- Console logs (not persisted)
- Code comments (not rendered)
- UX mockups (outside markdown or CI flows)

---

## Formatting & Documentation Best Practices
- Use clear, descriptive headings and consistent structure
- Follow markdownlint rules (see .markdownlint.json)
- Use only ASCII and standard Unicode text (no emoji, pictograms, or symbols)
- Prefer semantic sectioning: `#`, `##`, `###` for hierarchy
- Use code blocks for commands, code, and config examples
- Keep lines ≤ 120 characters
- No trailing whitespace or multiple consecutive blank lines
- All documentation changes must be logged in `DOC_CHANGELOG.md`

---

## Pre-commit & Review Rules
- All documentation and markdown files must pass markdownlint before commit
- All code/scripts/configs must pass their respective linters (Black, Ruff, yamllint, etc.)
- No emojis in any restricted file type (see above)
- All documentation changes must be logged in `DOC_CHANGELOG.md`
- The docs-maintainer is responsible for enforcing these rules and updating this file as needed

---

## Change Tracking
- All changes to documentation rules, formatting, or policy must be logged in `DOC_CHANGELOG.md`
- This file is the single source of truth for documentation formatting and emoji policy 

---

## Documentation Templates & Onboarding

### .mdc File Header Example
```
# [Agent Role] Agent Rule for PDF Chat Appliance

## Responsibilities
- ...

## Creative Identity
- Persona: [e.g., Docu the Documentarian]
- Metaphor: [e.g., Documentation as a living library]
- Visual/UX Style: [e.g., Visual storytelling, diagrams]

## Last Updated
- YYYY-MM-DD
```

### Session Notes Template
```
## [date] - [agent/role] Session Log
- **Summary:**
- **Actions:**
- **Blockers:**
- **Outcomes:**
```

### Changelog Entry Template
```
## [YYYY-MM-DD] [File/Area]
- **Summary:**
- **Before/After:**
- **Reviewer:**
```

### Creative Identity Log Example
```
- Persona: Docu the Documentarian
- Metaphor: Documentation as a living library
- Visual/UX Style: Visual storytelling, diagrams
```

### Linting & Automation
- The markdownlint configuration is in `.markdownlint.json` at the project root.
- To check formatting: `npx markdownlint .`
- Consider using spell check (`cspell`) and TOC generation (`doctoc`).
- Onboarding and contribution steps should be added to a `CONTRIBUTING.md` or this section. 

---

## Onboarding & Contributor Guidance

### Getting Started
- **Read this DOCUMENT_RULES.md** for formatting, emoji, and contribution policies.
- **Explore `/docs/` and `agent-shared/README.md`** for an overview of documentation structure and key files.
- **For agent-specific knowledge, see `training/[role]/learned.md` and `.cursor/rules/*.mdc`.**

### How to Contribute Documentation
1. **Identify the file to update or create.**
   - Use the templates below for `.mdc`, session notes, changelogs, and creative identity logs.
2. **Edit using a Markdown editor with linting support** (e.g., VS Code with markdownlint plugin).
3. **Run markdownlint and spell check before committing:**
   - `npx markdownlint .`
   - `npx cspell "**/*.md"`
   - (Optional) Generate or update TOC with `npx doctoc .` or VS Code TOC plugin.
4. **Log your change in `DOC_CHANGELOG.md`** using the changelog template.
5. **If you add a new file or script, update `agent-shared/README.md`.**
6. **For major changes, summarize in `session_notes.md` under the appropriate section.**

### Automation
- **Pre-commit hooks:** Add `markdownlint` and `cspell` to your Git pre-commit config for automatic checks.
- **CI/CD:** Integrate markdownlint, spell check, and TOC validation in your pipeline (see project scripts or ask docs-maintainer).

### Visual Documentation Map (Planned)
- A visual map of documentation structure and agent knowledge flow will be added to `/docs/` in a future update. 