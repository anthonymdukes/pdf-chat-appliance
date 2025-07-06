# Architecture Diagrams

This directory contains visual architecture diagrams for the PDF Chat Appliance project and Enterprise Agent Reorganization.

## Available Diagrams

### PDF Chat Appliance Architecture

**Files:**
- `pdf-chat-architecture.drawio` - Draw.io source file
- `pdf-chat-architecture.mmd` - Mermaid source file

**Description:** Comprehensive architecture diagram showing the complete PDF Chat Appliance system including:
- User Interface Layer (Web UI, CLI, REST API)
- Ingestion Pipeline (PDF upload, chunking, embedding, storage)
- Query Processing (similarity search, context assembly, RAG)
- LLM Layer (Ollama, model selection, response generation)
- Data Storage (Qdrant, SQLite, file storage)
- Observability (logging, metrics, monitoring)
- Configuration (YAML, environment variables, agent rules)

**Usage:**
- Open `pdf-chat-architecture.drawio` in Draw.io for editing
- Use `pdf-chat-architecture.mmd` for embedding in markdown documentation

### Enterprise Agent Reorganization

**Files:**
- `org-chart.drawio` - Draw.io source file
- `org-chart.mmd` - Mermaid source file

**Description:** Organizational structure diagram showing the enterprise agent reorganization including:
- Enterprise Architect (top level)
- Agent Core Division (system architect, task manager, agent flow, etc.)
- Development Division (API builder, python engineer, database specialist, etc.)
- Quality Division (code review, QA tester, coding style, etc.)
- Operations Division (environment, repository management, docs maintainer, etc.)
- Shared Services (orchestration, compliance, cross-division coordination)

**Usage:**
- Open `org-chart.drawio` in Draw.io for editing
- Use `org-chart.mmd` for embedding in markdown documentation

## Diagramming Tool

### Draw.io Container

The project uses a local Draw.io container for diagram creation and editing:

**Access:** `http://localhost:8081`

**Container Details:**
- Image: `jgraph/drawio:latest`
- Port: 8081
- Volume Mount: `agent-shared/diagrams/` → `/opt/drawio/diagrams/`

**Start Container:**
```bash
docker run -d --name drawio -p 8081:8080 -v ${PWD}/agent-shared/diagrams:/opt/drawio/diagrams jgraph/drawio:latest
```

**Stop Container:**
```bash
docker stop drawio
docker rm drawio
```

## Usage Guidelines

### Creating New Diagrams

1. **Draw.io Format:**
   - Use Draw.io for complex architecture diagrams
   - Save as `.drawio` files in this directory
   - Export to `.png` or `.svg` for documentation

2. **Mermaid Format:**
   - Use Mermaid for simple flow diagrams
   - Save as `.mmd` files in this directory
   - Embed directly in markdown documentation

### Diagram Standards

1. **Color Coding:**
   - **Blue:** User Interface components
   - **Yellow:** Ingestion/Processing components
   - **Green:** Query/Data components
   - **Purple:** LLM/AI components
   - **Red:** Storage/Infrastructure components
   - **Orange:** Observability/Monitoring components
   - **Gray:** Configuration/Management components

2. **Arrow Types:**
   - **Solid Arrow:** Direct data flow
   - **Dashed Arrow:** Monitoring/configuration connections
   - **Gray Dashed:** Cross-division collaboration

3. **Naming Conventions:**
   - Use descriptive, consistent naming
   - Include technology stack information where relevant
   - Maintain clear component boundaries

### Documentation Integration

**Markdown Embedding:**
```markdown
# PDF Chat Appliance Architecture

```mermaid
graph TB
    %% Include mermaid diagram content here
```
```

**Export for Documentation:**
- Export Draw.io diagrams as `.png` or `.svg`
- Use high resolution for documentation
- Include source files for future editing

## Maintenance

### Version Control
- Keep source files (`.drawio`, `.mmd`) in version control
- Export images for documentation as needed
- Document major changes in commit messages

### Updates
- Update diagrams when architecture changes
- Maintain consistency across all diagrams
- Review and validate diagram accuracy regularly

### Collaboration
- Use Draw.io for collaborative editing
- Share diagram links for review
- Maintain clear ownership and review processes

## Related Documentation

- `docs/ROOT_ARCHITECTURE.md` - Architecture documentation
- `docs/TEAM_STRUCTURE.md` - Team organization documentation
- `agent-shared/diagramming-tool-eval.md` - Tool evaluation and selection

## Support

For diagram-related questions or issues:
1. Check the Draw.io container status
2. Review diagram standards and guidelines
3. Consult the tool evaluation document
4. Contact the system architect or docs maintainer 