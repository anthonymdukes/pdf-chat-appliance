# TEAM_STRUCTURE.md

> Managed by `hr-coordinator` agent  
> Last updated: 2025-07-06  
> Status: Active

## Organizational Overview

### Project-Based Architecture (Flat, Focused, Autonomous)

We have transitioned from a division-based structure to a **project-based model** where:

- **Each project** (`pdf-appliance/`, `proxmox-build/`, `win11-performance/`) is isolated
- **Shared agents** live in `agent-core/`
- **Cross-project knowledge** lives in `shared-knowledge/`
- **All projects** follow a standard scaffold (`docs/`, `.ai/`, `.mdc/`, `diagrams/`)

### Global Registry

The global agent registry lives in `RUNN.md` and is maintained by the `hr-coordinator` agent.

## Current Project Structure

### PDF Chat Appliance Project
- **Location**: `/pdf-chat-appliance`
- **Status**: Active
- **Focus**: PDF processing, RAG implementation, enterprise deployment

### Agent Assignments

#### Core Project Agents (PDF Chat Appliance)
- **system-architect** - Architecture design and technical planning
- **api-builder** - FastAPI development and API optimization
- **llm-specialist** - LLM integration and RAG optimization
- **db-specialist** - Database design and vector store management
- **python-engineer** - Core Python development and refactoring
- **code-review** - Code quality and review processes
- **qa-tester** - Testing and quality assurance
- **docs-maintainer** - Documentation and knowledge management
- **deployment-monitor** - Deployment and infrastructure monitoring
- **observability** - System monitoring and performance tracking
- **security-checks** - Security validation and compliance
- **senior-dev** - Complex refactoring and architectural migrations
- **task-manager** - Agile workflow and task tracking
- **agent-flow** - Workflow orchestration and agent coordination
- **agent-orchestrator** - High-level agent coordination and planning
- **rule-governor** - Agent rule validation and governance
- **global-governance** - Global policy and compliance oversight
- **project-structure** - Repository structure and organization
- **prompt-strategy** - Prompt engineering and optimization
- **repo-management** - Version control and repository management
- **coding-style** - Code formatting and style enforcement
- **environment** - Environment setup and management
- **llm-config** - LLM configuration and model management
- **workflow-pdfchat** - PDF chat specific workflow management

#### Shared Agents (agent-core/)
- **hr-coordinator** - Agent onboarding, lifecycle tracking, and role assignments
- **training-lead** - Agent training and skill development
- **agent-bootstrapper** - New agent creation and initialization

## Agent Status Tracking

### Active Agents
All agents listed above are currently **active** and assigned to their respective projects.

### Temporary Agents
- None currently assigned

### Retired Agents
- None currently retired

## Agent Placement Rules

### agent-core/ (Shared Agents)
- Cross-project agents that serve multiple projects
- Core infrastructure and governance agents
- Training and HR coordination agents

### project-name/.mdc/ (Project-Specific Agents)
- Agents dedicated to specific project needs
- Domain-specific expertise and workflows
- Project-local configuration and optimization

### project-name/.mdc/temp/ or agent-core/temp-agents/ (Temporary Roles)
- Short-term project needs
- Experimental or trial agents
- Temporary workload spikes

## Collaboration Patterns

### Cross-Project Coordination
- **hr-coordinator** manages agent assignments and status
- **training-lead** coordinates skill development across projects
- **global-governance** ensures compliance and policy alignment

### Project-Specific Workflows
- Each project maintains its own `.ai/` planning structure
- Project-specific agents coordinate with shared agents as needed
- Knowledge sharing through `shared-knowledge/` directory

## Next Steps

1. **Phase 1 Complete**: HR coordinator infrastructure established
2. **Phase 2 Pending**: Agent flow rewiring and rule compliance updates
3. **Future**: Additional project onboarding and agent scaling

---

*This document is maintained by the hr-coordinator agent and updated whenever agent assignments or status changes occur.* 