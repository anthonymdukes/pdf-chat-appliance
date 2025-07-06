#!/usr/bin/env python3
"""
Role Audit Validation Script

Validates that all active agents listed in docs/hr-roster.md have submitted
proper role validation responses in session_notes.md under #role-validation.

Usage:
    python scripts/validate-role-audit.py

Output:
    - Console report of validation status
    - Detailed report written to agent-shared/role-audit-report.md
    - Exit code 0 for PASS, 1 for FAIL
"""

import os
import sys
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Set, Tuple

# Ensure we're running in the virtual environment
if 'venv' not in sys.executable:
    print("ERROR: Script must run in project virtual environment")
    print(f"Current interpreter: {sys.executable}")
    sys.exit(1)

def get_project_root() -> Path:
    """Get the project root directory."""
    current = Path.cwd()
    while current != current.parent:
        if (current / "README.md").exists() and (current / "PLANNING.md").exists():
            return current
        current = current.parent
    raise RuntimeError("Could not find project root")

def read_hr_roster() -> List[str]:
    """Extract active agent names from docs/hr-roster.md."""
    hr_roster_path = get_project_root() / "docs" / "hr-roster.md"
    
    if not hr_roster_path.exists():
        print(f"ERROR: HR roster not found at {hr_roster_path}")
        sys.exit(1)
    
    active_agents = []
    in_active_section = False
    
    with open(hr_roster_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            
            # Check for active section headers
            if line.startswith("### Active Agents") or line.startswith("#### Core Project Agents") or line.startswith("#### Shared Agents"):
                in_active_section = True
                continue
            
            # Check for other section headers that end active section
            if line.startswith("### ") and not line.startswith("### Active Agents"):
                in_active_section = False
                continue
            
            # Extract agent names from table rows
            if in_active_section and line.startswith("|") and "| Active |" in line:
                parts = line.split("|")
                if len(parts) >= 2:
                    agent_name = parts[1].strip()
                    if agent_name and agent_name != "Agent":
                        active_agents.append(agent_name)
    
    return active_agents

def read_session_notes() -> Dict[str, Dict[str, str]]:
    """Extract role validation entries from session_notes.md."""
    session_notes_path = get_project_root() / "session_notes.md"
    
    if not session_notes_path.exists():
        print(f"ERROR: Session notes not found at {session_notes_path}")
        sys.exit(1)
    
    role_validations = {}
    in_role_validation_section = False
    current_agent = None
    current_data = {}
    
    with open(session_notes_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the role-validation section
    role_validation_match = re.search(r'#role-validation\s*\n(.*?)(?=\n##|\n#|\Z)', 
                                     content, re.DOTALL)
    
    if not role_validation_match:
        print("WARNING: No #role-validation section found in session_notes.md")
        return {}
    
    role_validation_content = role_validation_match.group(1)
    
    # Parse each agent entry
    agent_entries = re.findall(r'- agent: ([^\n]+)\s*\n(.*?)(?=\n- agent:|\Z)', 
                              role_validation_content, re.DOTALL)
    
    for agent_name, entry_content in agent_entries:
        agent_name = agent_name.strip()
        data = {}
        
        # Extract each field
        for field in ['responsibilities', 'globs', 'dependencies', 'unclaimed-domain', 'status']:
            pattern = rf'- {field}: ([^\n]+(?:\n[^\n-]+)*)'
            match = re.search(pattern, entry_content, re.DOTALL)
            if match:
                data[field] = match.group(1).strip()
        
        if data:
            role_validations[agent_name] = data
    
    return role_validations

def validate_role_audit() -> Tuple[bool, Dict[str, List[str]]]:
    """Validate that all active agents have role validation entries."""
    active_agents = read_hr_roster()
    role_validations = read_session_notes()
    
    print(f"Found {len(active_agents)} active agents in HR roster")
    print(f"Found {len(role_validations)} role validation entries")
    
    # Check for missing agents
    missing_agents = []
    for agent in active_agents:
        if agent not in role_validations:
            missing_agents.append(agent)
    
    # Check for incomplete validations
    incomplete_agents = []
    for agent, data in role_validations.items():
        required_fields = ['responsibilities', 'globs', 'dependencies', 'unclaimed-domain', 'status']
        missing_fields = [field for field in required_fields if field not in data or not data[field]]
        if missing_fields:
            incomplete_agents.append(f"{agent} (missing: {', '.join(missing_fields)})")
    
    # Check for invalid status
    invalid_status_agents = []
    for agent, data in role_validations.items():
        if 'status' in data and data['status'] != 'role-validation-complete':
            invalid_status_agents.append(f"{agent} (status: {data.get('status', 'missing')})")
    
    # Determine overall result
    issues = {
        'missing': missing_agents,
        'incomplete': incomplete_agents,
        'invalid_status': invalid_status_agents
    }
    
    has_issues = any(issues.values())
    
    return not has_issues, issues

def generate_report(validation_passed: bool, issues: Dict[str, List[str]], 
                   active_agents: List[str], role_validations: Dict[str, Dict[str, str]]) -> str:
    """Generate a detailed audit report."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    report = f"""# Role Audit Report

**Generated:** {timestamp}  
**Status:** {'PASS' if validation_passed else 'FAIL'}  
**Total Active Agents:** {len(active_agents)}  
**Total Validations:** {len(role_validations)}

## Summary

"""
    
    if validation_passed:
        report += "✅ **AUDIT PASSED** - All active agents have complete role validations\n\n"
    else:
        report += "❌ **AUDIT FAILED** - Issues found with role validations\n\n"
    
    # Issues section
    if any(issues.values()):
        report += "## Issues Found\n\n"
        
        if issues['missing']:
            report += f"### Missing Role Validations ({len(issues['missing'])})\n"
            for agent in issues['missing']:
                report += f"- {agent}\n"
            report += "\n"
        
        if issues['incomplete']:
            report += f"### Incomplete Validations ({len(issues['incomplete'])})\n"
            for agent in issues['incomplete']:
                report += f"- {agent}\n"
            report += "\n"
        
        if issues['invalid_status']:
            report += f"### Invalid Status ({len(issues['invalid_status'])})\n"
            for agent in issues['invalid_status']:
                report += f"- {agent}\n"
            report += "\n"
    
    # Agent status table
    report += "## Agent Status\n\n"
    report += "| Agent | Status | Validation Complete |\n"
    report += "|-------|--------|-------------------|\n"
    
    for agent in sorted(active_agents):
        if agent in role_validations:
            status = role_validations[agent].get('status', 'missing')
            complete = '✅' if status == 'role-validation-complete' else '❌'
        else:
            status = 'missing'
            complete = '❌'
        
        report += f"| {agent} | {status} | {complete} |\n"
    
    # Recommendations
    report += "\n## Recommendations\n\n"
    
    if validation_passed:
        report += "- ✅ All agents have completed role validations\n"
        report += "- ✅ Ready for rule-governor enforcement audit\n"
        report += "- ✅ Organization audit system operational\n"
    else:
        report += "- ❌ Missing agents must submit role validations\n"
        report += "- ❌ Incomplete validations must be completed\n"
        report += "- ❌ Invalid status entries must be corrected\n"
        report += "- ❌ Audit cannot proceed until all issues resolved\n"
    
    return report

def main():
    """Main validation function."""
    print("Role Audit Validation Script")
    print("=" * 40)
    
    try:
        # Run validation
        validation_passed, issues = validate_role_audit()
        
        # Get data for report
        active_agents = read_hr_roster()
        role_validations = read_session_notes()
        
        # Generate and write report
        report = generate_report(validation_passed, issues, active_agents, role_validations)
        
        report_path = get_project_root() / "agent-shared" / "role-audit-report.md"
        report_path.parent.mkdir(exist_ok=True)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        # Print summary
        print(f"\nValidation {'PASSED' if validation_passed else 'FAILED'}")
        print(f"Report written to: {report_path}")
        
        if not validation_passed:
            print("\nIssues found:")
            for issue_type, agents in issues.items():
                if agents:
                    print(f"  {issue_type}: {len(agents)} agents")
        
        # Exit with appropriate code
        sys.exit(0 if validation_passed else 1)
        
    except Exception as e:
        print(f"ERROR: Validation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 