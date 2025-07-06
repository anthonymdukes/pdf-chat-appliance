#!/usr/bin/env python3
"""
HR Assignment Validation Script

Cross-references docs/hr-roster.md and docs/agent-assignments.md to ensure
data consistency and flag any issues for governance and audit readiness.

Usage:
    python scripts/validate-hr-assignments.py

Output:
    agent-shared/hr-validation-report.md
"""

import sys
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional

# Ensure we're running in the virtual environment
if 'venv' not in sys.executable:
    raise RuntimeError("This script must run in the project's virtual environment (.venv)")

def setup_paths() -> Tuple[Path, Path, Path]:
    """Setup file paths for input and output."""
    project_root = Path(__file__).parent.parent
    hr_roster = project_root / "docs" / "hr-roster.md"
    agent_assignments = project_root / "docs" / "agent-assignments.md"
    output_report = project_root / "agent-shared" / "hr-validation-report.md"
    
    # Ensure agent-shared directory exists
    output_report.parent.mkdir(exist_ok=True)
    
    return hr_roster, agent_assignments, output_report

def parse_markdown_table(content: str, table_name: str) -> List[Dict[str, str]]:
    """Parse markdown table and return list of dictionaries."""
    lines = content.split('\n')
    table_data = []
    in_table = False
    headers = []
    
    for line in lines:
        line = line.strip()
        
        # Skip empty lines and non-table content
        if not line or not line.startswith('|'):
            in_table = False
            continue
            
        # Remove leading/trailing pipes and split
        cells = [cell.strip() for cell in line.strip('|').split('|')]
        
        # Skip separator rows (containing only dashes and pipes)
        if all(re.match(r'^[\s\-:|]*$', cell) for cell in cells):
            continue
            
        if not in_table:
            # This is the header row
            headers = cells
            in_table = True
        else:
            # This is a data row
            if len(cells) == len(headers):
                row_data = {}
                for i, header in enumerate(headers):
                    row_data[header] = cells[i]
                table_data.append(row_data)
    
    return table_data

def extract_agents_from_roster(roster_content: str) -> Set[str]:
    """Extract agent names from hr-roster.md."""
    agents = set()
    
    # Parse active agents tables
    active_agents_data = parse_markdown_table(roster_content, "Active Agents")
    
    for row in active_agents_data:
        if 'Agent' in row and row['Agent'] and row['Agent'] != '*None currently assigned*':
            agent_name = row['Agent'].strip()
            if agent_name and not agent_name.startswith('*'):
                agents.add(agent_name)
    
    return agents

def extract_agents_from_assignments(assignments_content: str) -> Dict[str, List[Dict[str, str]]]:
    """Extract agent assignments from agent-assignments.md."""
    assignments = {}
    
    # Parse all assignment tables
    assignment_data = parse_markdown_table(assignments_content, "Agent Assignments")
    
    for row in assignment_data:
        if 'Agent' in row and row['Agent'] and row['Agent'] != '*None currently assigned*':
            agent_name = row['Agent'].strip()
            if agent_name and not agent_name.startswith('*'):
                if agent_name not in assignments:
                    assignments[agent_name] = []
                assignments[agent_name].append(row)
    
    return assignments

def validate_assignments(roster_agents: Set[str], assignments: Dict[str, List[Dict[str, str]]]) -> Dict[str, List[str]]:
    """Validate assignments against roster and return issues."""
    issues = {
        'orphaned_assignments': [],
        'duplicate_assignments': [],
        'missing_columns': [],
        'inconsistent_headers': []
    }
    
    # Check for orphaned assignments (agents in assignments but not in roster)
    for agent_name in assignments:
        if agent_name not in roster_agents:
            issues['orphaned_assignments'].append(agent_name)
    
    # Check for duplicate assignments to same project
    for agent_name, agent_assignments in assignments.items():
        project_assignments = {}
        for assignment in agent_assignments:
            project = assignment.get('Project', '').strip()
            status = assignment.get('Status', '').strip()
            
            if project and project != 'ALL PROJECTS':
                if project in project_assignments:
                    # Check if this is a legitimate duplicate (temporary assignment)
                    if status.lower() != 'temporary':
                        issues['duplicate_assignments'].append(
                            f"{agent_name} -> {project} (multiple assignments without temporary flag)"
                        )
                else:
                    project_assignments[project] = assignment
    
    return issues

def check_table_structure(roster_content: str, assignments_content: str) -> Dict[str, List[str]]:
    """Check for missing columns and inconsistent headers."""
    issues = {
        'missing_columns': [],
        'inconsistent_headers': []
    }
    
    # Expected columns for hr-roster.md
    expected_roster_columns = {'Agent', 'Status', 'Specialization', 'Last Updated'}
    
    # Expected columns for agent-assignments.md
    expected_assignment_columns = {'Agent', 'Project', 'Role', 'Status', 'Assigned Since'}
    
    # Parse tables to get actual columns
    roster_data = parse_markdown_table(roster_content, "HR Roster")
    assignment_data = parse_markdown_table(assignments_content, "Agent Assignments")
    
    if roster_data:
        actual_roster_columns = set(roster_data[0].keys())
        missing_roster = expected_roster_columns - actual_roster_columns
        if missing_roster:
            issues['missing_columns'].append(f"hr-roster.md missing: {', '.join(missing_roster)}")
    
    if assignment_data:
        actual_assignment_columns = set(assignment_data[0].keys())
        missing_assignment = expected_assignment_columns - actual_assignment_columns
        if missing_assignment:
            issues['missing_columns'].append(f"agent-assignments.md missing: {', '.join(missing_assignment)}")
    
    return issues

def generate_report(roster_agents: Set[str], assignments: Dict[str, List[Dict[str, str]]], 
                   validation_issues: Dict[str, List[str]], structure_issues: Dict[str, List[str]]) -> str:
    """Generate the validation report."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Count total issues
    total_issues = sum(len(issues) for issues in validation_issues.values()) + \
                   sum(len(issues) for issues in structure_issues.values())
    
    # Determine overall status
    overall_status = "✅ PASS" if total_issues == 0 else "❌ FAIL"
    
    report = f"""# HR Assignment Validation Report

> Generated: {timestamp}  
> Status: {overall_status}  
> Total Issues: {total_issues}

## Summary

- **Roster Agents**: {len(roster_agents)}
- **Assigned Agents**: {len(assignments)}
- **Validation Issues**: {total_issues}

## Validation Results

### ✅ Cross-Reference Check

**Roster Agents Found:**
{chr(10).join(f"- {agent}" for agent in sorted(roster_agents))}

**Assigned Agents Found:**
{chr(10).join(f"- {agent}" for agent in sorted(assignments.keys()))}

### ❌ Issues Found

"""
    
    # Add validation issues
    for issue_type, issues in validation_issues.items():
        if issues:
            report += f"#### {issue_type.replace('_', ' ').title()}\n"
            for issue in issues:
                report += f"- {issue}\n"
            report += "\n"
    
    # Add structure issues
    for issue_type, issues in structure_issues.items():
        if issues:
            report += f"#### {issue_type.replace('_', ' ').title()}\n"
            for issue in issues:
                report += f"- {issue}\n"
            report += "\n"
    
    if total_issues == 0:
        report += "### ✅ No Issues Found\n\nAll HR files are consistent and properly structured.\n\n"
    else:
        report += """### 🔧 Suggested Fixes

1. **For Orphaned Assignments**: Add missing agents to `docs/hr-roster.md`
2. **For Duplicate Assignments**: Review and clarify assignment status or remove duplicates
3. **For Missing Columns**: Add required columns to the respective files
4. **For Inconsistent Headers**: Standardize table headers across both files

### 📋 Action Items

"""
        for issue_type, issues in validation_issues.items():
            if issues:
                report += f"- **{issue_type.replace('_', ' ').title()}**: {len(issues)} items to address\n"
        
        for issue_type, issues in structure_issues.items():
            if issues:
                report += f"- **{issue_type.replace('_', ' ').title()}**: {len(issues)} items to address\n"
    
    report += f"""
## File Information

- **hr-roster.md**: {len(roster_agents)} agents tracked
- **agent-assignments.md**: {len(assignments)} agents assigned
- **Validation Script**: `scripts/validate-hr-assignments.py`
- **Report Generated**: {timestamp}

---

*This report is automatically generated by the HR validation script. Run the script again to update this report.*
"""
    
    return report

def main():
    """Main validation function."""
    print("HR Assignment Validation Script")
    print("=" * 40)
    
    try:
        # Setup paths
        hr_roster_path, agent_assignments_path, output_report_path = setup_paths()
        
        # Check if input files exist
        if not hr_roster_path.exists():
            raise FileNotFoundError(f"HR roster file not found: {hr_roster_path}")
        if not agent_assignments_path.exists():
            raise FileNotFoundError(f"Agent assignments file not found: {agent_assignments_path}")
        
        print(f"Reading HR roster: {hr_roster_path}")
        with open(hr_roster_path, 'r', encoding='utf-8') as f:
            roster_content = f.read()
        
        print(f"Reading agent assignments: {agent_assignments_path}")
        with open(agent_assignments_path, 'r', encoding='utf-8') as f:
            assignments_content = f.read()
        
        # Extract data
        print("Extracting agent data...")
        roster_agents = extract_agents_from_roster(roster_content)
        assignments = extract_agents_from_assignments(assignments_content)
        
        print(f"Found {len(roster_agents)} agents in roster")
        print(f"Found {len(assignments)} agents with assignments")
        
        # Validate
        print("Validating assignments...")
        validation_issues = validate_assignments(roster_agents, assignments)
        structure_issues = check_table_structure(roster_content, assignments_content)
        
        # Generate report
        print("Generating validation report...")
        report = generate_report(roster_agents, assignments, validation_issues, structure_issues)
        
        # Write report
        with open(output_report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"Validation report written to: {output_report_path}")
        
        # Print summary
        total_issues = sum(len(issues) for issues in validation_issues.values()) + \
                       sum(len(issues) for issues in structure_issues.values())
        
        if total_issues == 0:
            print("✅ Validation PASSED - No issues found")
        else:
            print(f"❌ Validation FAILED - {total_issues} issues found")
            print("Check the validation report for details")
        
        return total_issues == 0
        
    except Exception as e:
        print(f"❌ Validation script failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 