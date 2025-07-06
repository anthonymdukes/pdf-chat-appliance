# SHARED_DIRECTORY_USAGE.md

## Cross-Environment Shared Directory Guidelines

This document defines the usage, conventions, and policies for the `agent-shared/` directory, which serves as the universal workspace for cross-environment agent collaboration.

---

## Directory Overview

### **Purpose**
The `agent-shared/` directory serves as a persistent, OS-agnostic shared workspace for all agents, enabling seamless collaboration across Windows, WSL, and future Docker environments.

### **Access Paths**

| Environment | Path | Notes |
|-------------|------|-------|
| **Windows** | `D:\repos\pdf-chat-appliance\agent-shared` | Native Windows access |
| **WSL** | `/mnt/d/repos/pdf-chat-appliance/agent-shared` | WSL mount point |
| **WSL Symlink** | `~/agent-shared` | Optional symlink for convenience |

---

## Directory Structure

```
agent-shared/
├── logs/                    # Agent execution logs and traces
├── test-results/           # Test outputs and benchmarks
├── model-outputs/          # LLM responses and embeddings
├── debug-files/            # Debug artifacts and trace files
├── ingestion-data/         # PDF processing and chunking outputs
├── api-data/              # FastAPI request/response logs
├── cross-agent/           # Inter-agent communication artifacts
└── temp/                  # Temporary files (auto-cleanup)
```

---

## File Naming Conventions

### **General Format**
```
[category]_[agent]_[timestamp]_[description].[extension]
```

### **Examples**
- `test_result_qa-tester_20250706_143022_pyright_scan.json`
- `model_output_llm-specialist_20250706_143045_embedding_benchmark.json`
- `debug_file_system-architect_20250706_143112_architecture_decision.log`
- `ingestion_data_deployment-monitor_20250706_143135_pdf_processing.json`
- `api_data_api-builder_20250706_143158_request_trace.json`

### **Timestamp Format**
- **Format:** `YYYYMMDD_HHMMSS`
- **Example:** `20250706_143022` (July 6, 2025, 14:30:22)

---

## Usage Guidelines

### **Do's**
- ✅ Use appropriate subdirectories for file organization
- ✅ Follow naming conventions for all files
- ✅ Include timestamps in filenames for traceability
- ✅ Log file creation in `session_notes.md`
- ✅ Use cross-platform compatible paths
- ✅ Clean up temporary files after use
- ✅ Validate file permissions across environments

### **Don'ts**
- ❌ Don't delete files without logging in `session_notes.md`
- ❌ Don't use absolute paths that are environment-specific
- ❌ Don't create files without proper naming conventions
- ❌ Don't leave large files without cleanup plans
- ❌ Don't overwrite files without versioning
- ❌ Don't use special characters in filenames

---

## Agent Responsibilities

### **All Agents**
- Must use `agent-shared/` for cross-environment file operations
- Must follow naming conventions for all shared files
- Must log file operations in `session_notes.md`
- Must respect cleanup policies and file retention

### **@docs-maintainer**
- Maintain this documentation
- Review and approve naming convention changes
- Monitor directory usage and organization

### **@deployment-monitor**
- Validate cross-environment access
- Monitor directory permissions and availability
- Ensure WSL bridge functionality

### **@system-architect**
- Define directory structure and organization
- Establish file retention and cleanup policies
- Coordinate cross-agent file sharing patterns

---

## File Categories and Usage

### **logs/**
- **Purpose:** Agent execution logs and traces
- **Retention:** 30 days
- **Format:** `.log`, `.txt`
- **Example:** `logs/system-architect_20250706_143022_decision_trace.log`

### **test-results/**
- **Purpose:** Test outputs, benchmarks, and validation results
- **Retention:** 90 days
- **Format:** `.json`, `.xml`, `.html`
- **Example:** `test-results/qa-tester_20250706_143045_pyright_scan.json`

### **model-outputs/**
- **Purpose:** LLM responses, embeddings, and model artifacts
- **Retention:** 7 days (large files)
- **Format:** `.json`, `.pkl`, `.npy`
- **Example:** `model-outputs/llm-specialist_20250706_143112_embedding_benchmark.json`

### **debug-files/**
- **Purpose:** Debug artifacts and trace files
- **Retention:** 7 days
- **Format:** `.log`, `.txt`, `.json`
- **Example:** `debug-files/api-builder_20250706_143135_request_trace.log`

### **ingestion-data/**
- **Purpose:** PDF processing and chunking outputs
- **Retention:** 30 days
- **Format:** `.json`, `.txt`
- **Example:** `ingestion-data/deployment-monitor_20250706_143158_pdf_processing.json`

### **api-data/**
- **Purpose:** FastAPI request/response logs and data
- **Retention:** 14 days
- **Format:** `.json`, `.log`
- **Example:** `api-data/api-builder_20250706_143201_request_log.json`

### **cross-agent/**
- **Purpose:** Inter-agent communication artifacts
- **Retention:** 7 days
- **Format:** `.json`, `.txt`
- **Example:** `cross-agent/system-architect_20250706_143224_handoff_data.json`

### **temp/**
- **Purpose:** Temporary files for immediate processing
- **Retention:** 24 hours (auto-cleanup)
- **Format:** Various
- **Example:** `temp/llm-specialist_20250706_143247_temp_processing.json`

---

## Cleanup Policy

### **Automatic Cleanup**
- **temp/**: Files older than 24 hours
- **model-outputs/**: Files older than 7 days
- **debug-files/**: Files older than 7 days
- **cross-agent/**: Files older than 7 days

### **Manual Cleanup**
- **logs/**: Monthly review and cleanup
- **test-results/**: Quarterly review and cleanup
- **ingestion-data/**: Monthly review and cleanup
- **api-data/**: Bi-weekly review and cleanup

### **Cleanup Process**
1. Log cleanup operations in `session_notes.md`
2. Archive important files before deletion
3. Update `DOC_CHANGELOG.md` with cleanup summary
4. Notify affected agents of cleanup actions

---

## Cross-Environment Validation

### **Windows Validation**
```powershell
# Test write access
New-Item -Path "agent-shared\test\windows_test.txt" -ItemType File -Force
# Test read access
Get-Content "agent-shared\test\windows_test.txt"
```

### **WSL Validation**
```bash
# Test write access
mkdir -p /mnt/d/repos/pdf-chat-appliance/agent-shared/test
echo "WSL test" > /mnt/d/repos/pdf-chat-appliance/agent-shared/test/wsl_test.txt
# Test read access
cat /mnt/d/repos/pdf-chat-appliance/agent-shared/test/wsl_test.txt
```

## Finalized Multi-Environment Workflow Use Cases

### **Use Case 1: GPU-Accelerated Model Testing**
```
1. Windows: Agent coordination and test planning
2. WSL: GPU-accelerated model loading and inference
3. agent-shared/model-outputs/: Store model results and performance metrics
4. Windows: Analyze results and coordinate next steps
```

### **Use Case 2: Cross-Platform Package Validation**
```
1. Windows: Package dependency analysis and planning
2. WSL: Linux-native package installation and testing
3. agent-shared/test-results/: Store package compatibility results
4. Windows: Validate cross-platform compatibility
```

### **Use Case 3: Performance Benchmarking**
```
1. Windows: Benchmark definition and coordination
2. WSL: GPU-accelerated performance testing
3. agent-shared/test-results/: Store benchmark data and metrics
4. Windows: Performance analysis and optimization planning
```

### **Use Case 4: System Signal Validation**
```
1. Windows: Signal handling requirements definition
2. WSL: Linux signal validation and testing
3. agent-shared/debug-files/: Store signal handling logs
4. Windows: Cross-platform signal compatibility analysis
```

### **Path Compatibility**
- Use relative paths when possible
- Avoid environment-specific path separators
- Test file operations across all environments
- Validate permissions and access rights

---

## Monitoring and Maintenance

### **Directory Health Checks**
- Weekly validation of cross-environment access
- Monthly review of file organization and usage
- Quarterly cleanup of old files and directories
- Continuous monitoring of disk space usage

### **Performance Considerations**
- Monitor file sizes and growth patterns
- Implement compression for large files
- Consider archiving strategies for long-term storage
- Optimize file I/O operations across environments

---

## Troubleshooting

### **Common Issues**
1. **Permission Denied**: Check file permissions across environments
2. **Path Not Found**: Verify WSL mount point and symlink setup
3. **File Locked**: Ensure no processes are actively using files
4. **Disk Space**: Monitor and manage storage usage

### **Resolution Steps**
1. Check file permissions and ownership
2. Validate WSL bridge connectivity
3. Review file usage and cleanup policies
4. Consult `session_notes.md` for recent changes
5. Escalate to `@deployment-monitor` if needed

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-07-06 | Initial documentation created |
| 1.1 | 2025-07-06 | Added cleanup policies and monitoring |

---

**This document is maintained by @docs-maintainer and should be updated as the shared directory usage evolves.** 