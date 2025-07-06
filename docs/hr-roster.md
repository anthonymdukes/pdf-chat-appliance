# HR Roster - Agent Status & Lifecycle

> Managed by `hr-coordinator` agent  
> Last updated: 2025-07-06  
> Status: Active

## Agent Registry

### Active Agents

#### Core Project Agents

| Agent | Status | Specialization | Last Updated | Audit Complete |
|-------|--------|----------------|--------------|---------------|
| system-architect | Active | Architecture design, technical planning, system modeling | 2025-07-06 | true |
| api-builder | Active | FastAPI development, API optimization, RESTful design | 2025-07-06 | true |
| llm-specialist | Active | LLM integration, RAG optimization, model management | 2025-07-06 | true |
| db-specialist | Active | Database design, vector store management, data modeling | 2025-07-06 | true |
| python-engineer | Active | Core Python development, refactoring, code optimization | 2025-07-06 | true |
| code-review | Active | Code quality, review processes, standards enforcement | 2025-07-06 | true |
| qa-tester | Active | Testing, quality assurance, automated testing | 2025-07-06 | true |
| docs-maintainer | Active | Documentation, knowledge management, technical writing | 2025-07-06 | true |
| deployment-monitor | Active | Deployment, infrastructure monitoring, DevOps | 2025-07-06 | true |
| observability | Active | System monitoring, performance tracking, metrics | 2025-07-06 | true |
| security-checks | Active | Security validation, compliance, threat assessment | 2025-07-06 | true |
| senior-dev | Active | Complex refactoring, architectural migrations, technical leadership | 2025-07-06 | true |
| task-manager | Active | Agile workflow, task tracking, project management | 2025-07-06 | true |
| agent-flow | Active | Workflow orchestration, agent coordination, process design | 2025-07-06 | true |
| agent-orchestrator | Active | High-level agent coordination, planning, system orchestration | 2025-07-06 | true |
| rule-governor | Active | Agent rule validation, governance, policy enforcement | 2025-07-06 | true |
| global-governance | Active | Global policy, compliance oversight, strategic governance | 2025-07-06 | true |
| project-structure | Active | Repository structure, organization, file management | 2025-07-06 | true |
| prompt-strategy | Active | Prompt engineering, optimization, LLM interaction design | 2025-07-06 | true |
| repo-management | Active | Version control, repository management, Git operations | 2025-07-06 | true |
| coding-style | Active | Code formatting, style enforcement, linting standards | 2025-07-06 | true |
| environment | Active | Environment setup, management, configuration | 2025-07-06 | true |
| llm-config | Active | LLM configuration, model management, AI infrastructure | 2025-07-06 | true |
| workflow-pdfchat | Active | PDF chat specific workflow management, domain expertise | 2025-07-06 | true |

#### Shared Agents (agent-core/)

| Agent | Status | Specialization | Last Updated | Audit Complete |
|-------|--------|----------------|--------------|---------------|
| hr-coordinator | Active | Agent onboarding, lifecycle tracking, organizational management | 2025-07-06 | true |
| training-lead | Active | Agent training, skill development, learning programs | 2025-07-06 | true |
| agent-bootstrapper | Active | New agent creation, initialization, profile setup | 2025-07-06 | true |

### Temporary Agents

| Agent | Status | Specialization | Expiration Date | Last Updated |
|-------|--------|----------------|-----------------|--------------|
| *None currently assigned* | - | - | - | - |

### Retired Agents

| Agent | Status | Previous Specialization | Retirement Date | Reason | Last Updated |
|-------|--------|------------------------|-----------------|--------|--------------|
| *None currently retired* | - | - | - | - | - |

## Agent Lifecycle Management

### Onboarding Process

1. **agent-bootstrapper** creates initial agent profile
2. **hr-coordinator** assigns placement and status
3. **system-architect** validates technical fit
4. **training-lead** schedules onboarding
5. **docs-maintainer** updates team documentation

### Status Transitions

- **Draft** → **Active**: Agent created, assigned, and operational
- **Active** → **Temporary**: Short-term assignment or trial period
- **Active** → **Retired**: Agent deprecated or replaced
- **Temporary** → **Active**: Trial successful, permanent assignment
- **Temporary** → **Retired**: Trial unsuccessful, agent deprecated

### Placement Rules

#### agent-core/ (Shared Agents)
- Cross-project agents serving multiple projects
- Core infrastructure and governance agents
- Training and HR coordination agents

#### project-name/.mdc/ (Project-Specific Agents)
- Agents dedicated to specific project needs
- Domain-specific expertise and workflows
- Project-local configuration and optimization

#### project-name/.mdc/temp/ or agent-core/temp-agents/ (Temporary Roles)
- Short-term project needs
- Experimental or trial agents
- Temporary workload spikes

## Agent Performance Tracking

### Key Metrics

- **Assignment Duration**: How long agents have been in current role
- **Skill Development**: Progress in training and specialization
- **Collaboration Score**: Effectiveness in cross-agent coordination
- **Performance Rating**: Overall effectiveness and contribution

### Performance Reviews

- **Monthly**: Status and skill development review
- **Quarterly**: Performance and contribution assessment
- **Annual**: Comprehensive evaluation and planning

## Recent Changes

### 2025-07-06: HR File Structure Correction
- **Event**: Executive directive for HR file cleanup and structure correction
- **Impact**: Removed project assignments from hr-roster.md, focused on agent identity and skills
- **Status**: Phase 1 complete, agent-assignments.md creation pending

### 2025-07-06: HR Coordinator Onboarding
- **Event**: hr-coordinator agent activated
- **Impact**: Centralized agent lifecycle management
- **Status**: Active and operational

### 2025-07-06: MDC Post-Deduplication Audit Complete
- **Event**: All agent .mdc files updated for post-deduplication realignment
- **Impact**: Every agent role now has a clear, non-overlapping scope and explicit coordination dependencies
- **Status**: Audit complete, all agents compliant and ready for new agent onboarding and Sprint 2.8

### 2025-07-06: Post-Realignment Gap Analysis Complete
- **Event:** Comprehensive gap analysis conducted by ai-chief-of-staff
- **Impact:** Confirmed 26 active agents with all critical functions covered, identified 3 optional enhancement areas
- **Status:** Audit complete, system ready for multi-project expansion and Sprint 2.8

## Next Actions

1. **Create agent-assignments.md**: Track project assignments separately
2. **Performance Baseline**: Establish metrics for all active agents
3. **Training Coordination**: Schedule skill development sessions
4. **Documentation Updates**: Ensure all agent profiles reflect new structure

---

*This roster is maintained by the hr-coordinator agent and tracks agent identity, lifecycle, and skill specializations only.* 