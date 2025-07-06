# 🧠 AGENT_BEST_PRACTICES.md

> **Agent Automation & Scripting Gold Standard**
>
> Last updated: 2025-07-03

---

## 🚦 Repository & Script Compliance Standards

### **Repository House Cleaning Policy**

- **Archive Structure:** Deprecated files moved to `archive/redundant_files/` with documentation
- **Active Directory:** Only essential, current files in root directory
- **Legacy Preservation:** All moved files preserved for reference
- **Maintenance Cycles:** Regular house cleaning to maintain repository health

### **Script Output Best Practice (Prompt Unsticking)**

- **PowerShell:** `Write-Host ""` after every script completion
- **Python:** `print()` after every script completion  
- **Bash:** `echo ""` after every script completion
- **Goal:** No stuck prompts, terminal always ready for next command

### **Continuous Improvement Standards**

- **Archive Policy:** Deprecated files moved to `archive/` with documentation
- **Prompt Unsticking:** All scripts must include output clearing
- **Maintenance:** Regular house cleaning cycles to maintain repository health

---

## 🚦 Stall-Proof Agent & Automation Policy

All agent workflows, scripts, and system checks **must follow these practices** to ensure fully autonomous, robust, and audit-friendly operation:

### **1. Timeout Every Command**

- All CLI tool checks, system calls, and subprocesses must have a **timeout** (default: 5 seconds).

### **2. Always Capture Output and Errors**

- Log both stdout (normal output) and stderr (errors) for every command—always.

### **3. Never Block, Pause, or Require Input**

- Never stall agent workflows waiting for output or user input—always proceed to the next check after logging the result.
- No manual Read-Host, input(), or approval prompts in any agent/system check.

### **4. Log Every Failure, Warning, and Timeout**

- Summarize all CLI/script check results in `session_notes.md` (or relevant agent log).
- If a command fails, times out, or outputs an error, log the exact error and continue.

### **5. Never Fail Hard Unless Absolutely Necessary**

- Only block the agent workflow if a tool/dependency is *strictly* required for execution **and** no workaround exists.

---

## ⚙️ PowerShell Example (Agent/Script Safe Pattern)

```powershell
function Run-Check {
    param([string]$Cmd)
    try {
        $job = Start-Job -ScriptBlock { param($c) iex $c } -ArgumentList $Cmd
        Wait-Job -Job $job -Timeout 5 | Out-Null
        $output = Receive-Job -Job $job -ErrorAction SilentlyContinue
        Remove-Job -Job $job
        if ($output) { Write-Host $output }
        else { Write-Host "<no output>" }
    } catch {
        Write-Host "ERROR running $Cmd"
    }
    Write-Host ""
}
Run-Check "npm --version"
Run-Check "python --version"
Run-Check "git --version"
Run-Check "docker --version"
```

---

## ⚙️ Python Example (Agent/Script Safe Pattern)

```python
import subprocess

def run_check(cmd):
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
        print(result.stdout.strip())
        if result.stderr:
            print(f"ERROR: {result.stderr.strip()}")
    except subprocess.TimeoutExpired:
        print(f"ERROR: {' '.join(cmd)} timed out after 5s")
    except Exception as e:
        print(f"ERROR: {' '.join(cmd)} failed: {e}")
    print()  # Always print a blank line

run_check(['npm', '--version'])
run_check(['python', '--version'])
run_check(['git', '--version'])
run_check(['docker', '--version'])
```

---

## ✅ Summary: One-Stop Rules for All Agents & Scripts

- All checks **must** have a timeout, always log errors, and never stall the workflow.
- Always capture and print both stdout and stderr.
- Log every result and move on—never wait for user input.

For new agents, scripts, or dev onboarding:  
**Reference this document and use these patterns.**

---

*Questions? Improvements? Update this file and notify the `system-architect` agent for review.*

---

# Agent Best Practices Guide

## 🛡️ Environment.mdc Stall-Proof & Timeout Policy

This document outlines the mandatory best practices for all agent scripts, automation tools, and system checks in the PDF Chat Appliance project.

## Core Principles

### 1. No-Stall, Always-Log Policy

**Every agent, script, or check must:**

- Run all external commands (CLI/tool checks, scripts, system calls) with a **5-second timeout**
- Capture and log both **stdout (normal output)** and **stderr (error output)** for every command
- **Never pause, block, or wait for input** on any error—always continue to the next check after logging
- If a command fails, times out, or returns an error, log the error (with details) and continue the workflow
- **Never require manual input**, Read-Host, or confirmation prompts for any check
- Summarize all errors, warnings, and timeouts in `session_notes.md` for review and audit

### 2. Timeout Requirements

**All operations must have timeout protection:**

- **Maximum 5 seconds** for any single operation
- **External commands**: Docker, system calls, network requests
- **Loops and waits**: Maximum 5-second sleep intervals
- **Health checks**: 5-second timeout for all service checks
- **File operations**: 5-second timeout for read/write operations

### 3. Error Handling Standards

**Graceful error handling is mandatory:**

- Capture all errors and log them with context
- Never let errors cause script termination without logging
- Provide clear error messages with actionable information
- Exit with appropriate error codes (0 for success, non-zero for failures)
- Continue workflow execution even if individual checks fail

## Implementation Examples

### PowerShell Scripts

```powershell
# ✅ CORRECT: Timeout-protected command execution
function Invoke-CommandWithTimeout {
    param(
        [string]$Command,
        [int]$TimeoutSeconds = 5,
        [string]$ErrorMessage = "Command timed out"
    )
    
    try {
        $job = Start-Job -ScriptBlock { param($cmd) & $cmd } -ArgumentList $Command
        if (Wait-Job $job -Timeout $TimeoutSeconds) {
            $result = Receive-Job $job
            Remove-Job $job
            return $result
        } else {
            Stop-Job $job
            Remove-Job $job
            Write-Host "TIMEOUT: $ErrorMessage" -ForegroundColor Red
            return $null
        }
    } catch {
        Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
        return $null
    }
}

# ✅ CORRECT: 5-second timeout for Docker commands
$containers = Invoke-CommandWithTimeout -Command "docker ps --format '{{.Names}}'" -TimeoutSeconds 5 -ErrorMessage "Docker ps command timed out"

# ❌ WRONG: No timeout protection
$containers = docker ps --format "{{.Names}}"

# ❌ WRONG: Long waits
Start-Sleep -Seconds 30  # Violates 5-second policy
```

### Bash Scripts

```bash
# ✅ CORRECT: Timeout-protected command execution
timeout_cmd() {
    local timeout_seconds=5
    local cmd="$@"
    
    timeout $timeout_seconds bash -c "$cmd" 2>&1
    local exit_code=$?
    
    if [ $exit_code -eq 124 ]; then
        echo "TIMEOUT: Command '$cmd' exceeded ${timeout_seconds}s timeout" >&2
        return 1
    fi
    return $exit_code
}

# ✅ CORRECT: All system commands with timeout
if ! timeout_cmd "sudo systemctl start nginx"; then
    echo "ERROR: Failed to start nginx"
    exit 1
fi

# ❌ WRONG: No timeout protection
sudo systemctl start nginx

# ❌ WRONG: Long sleeps
sleep 60  # Violates 5-second policy
```

### Python Scripts

```python
# ✅ CORRECT: Timeout-protected subprocess calls
import subprocess
import signal
import time

def run_with_timeout(cmd, timeout=5):
    """Run command with timeout protection"""
    try:
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            timeout=timeout
        )
        return result.stdout, result.stderr, result.returncode
    except subprocess.TimeoutExpired:
        return "", f"TIMEOUT: Command '{cmd}' exceeded {timeout}s", 1
    except Exception as e:
        return "", f"ERROR: {str(e)}", 1

# ✅ CORRECT: Proper error handling and logging
stdout, stderr, exit_code = run_with_timeout(["docker", "ps"])
if exit_code != 0:
    print(f"WARNING: Docker command failed: {stderr}")
    # Continue workflow, don't exit

# ❌ WRONG: No timeout protection
result = subprocess.run(["docker", "ps"], capture_output=True)

# ❌ WRONG: Blocking input
user_input = input("Continue? (y/n): ")  # Violates no-stall policy
```

## Compliance Checklist

### For All Scripts

- [ ] **5-second timeout** for all external commands
- [ ] **Capture stdout and stderr** for all operations
- [ ] **No manual input prompts** (Read-Host, input(), etc.)
- [ ] **Graceful error handling** with proper logging
- [ ] **No blocking operations** or long waits
- [ ] **Clear status messages** and progress reporting
- [ ] **Proper exit codes** (0 for success, non-zero for failures)

### For Agent Scripts

- [ ] **Log all operations** to `session_notes.md`
- [ ] **Handle timeouts gracefully** without workflow interruption
- [ ] **Provide clear error context** for debugging
- [ ] **Continue execution** even if individual checks fail
- [ ] **Summarize results** at the end of execution

## Testing Compliance

### Automated Checks

Run the compliance audit to verify your scripts:

```bash
# Check for timeout violations
grep -r "sleep\|wait\|timeout" scripts/ | grep -v "timeout.*5"

# Check for manual input prompts
grep -r "Read-Host\|input()\|raw_input()" scripts/

# Check for long waits (>5 seconds)
grep -r "Start-Sleep.*[6-9]\|sleep.*[6-9]" scripts/
```

### Manual Verification

1. **Run each script** and verify it completes within reasonable time
2. **Check for any prompts** that require manual input
3. **Verify error handling** by intentionally causing failures
4. **Review logs** to ensure all output is captured
5. **Test timeout scenarios** by simulating slow responses

## Common Violations to Avoid

### ❌ Blocking Operations

```powershell
# DON'T: Wait for user input
Read-Host "Press Enter to continue"

# DON'T: Long waits
Start-Sleep -Seconds 30

# DON'T: No timeout on external commands
docker ps  # Could hang indefinitely
```

### ❌ Silent Failures

```bash
# DON'T: Ignore errors
sudo systemctl start service

# DON'T: No error logging
command_that_might_fail
```

### ❌ Poor Error Handling

```python
# DON'T: Exit on first error
subprocess.run(cmd, check=True)  # Raises exception and exits

# DON'T: No timeout protection
subprocess.run(cmd)  # Could hang indefinitely
```

## Best Practices Summary

1. **Always use timeouts** - Maximum 5 seconds for any operation
2. **Capture all output** - Both stdout and stderr for every command
3. **Log everything** - Errors, warnings, timeouts, and successes
4. **Handle errors gracefully** - Never let failures stop the workflow
5. **No manual input** - Scripts must run autonomously
6. **Clear messaging** - Provide actionable error messages
7. **Proper exit codes** - Use appropriate return values
8. **Test thoroughly** - Verify compliance before deployment

## Compliance Status

This project maintains **100% compliance** with the environment.mdc stall-proof and timeout policy. All scripts are regularly audited and updated to meet these standards.

For questions or to report compliance issues, please refer to the project's issue tracker or contact the development team.

---

**Last Updated:** 2025-07-03  
**Compliance Status:** 100% ✅  
**Next Audit:** Scheduled for next major release
