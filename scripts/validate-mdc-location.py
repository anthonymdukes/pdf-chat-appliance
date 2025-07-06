#!/usr/bin/env python3
"""
MDC Location Validation Script

Enforces the rule that all .mdc agent files must live inside .cursor/rules/ directory.
Scans the entire repository to detect any .mdc files outside the approved path.

Usage:
    python scripts/validate-mdc-location.py

Output:
    agent-shared/mdc-location-report.md
"""

import sys
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Tuple

# Ensure we're running in the virtual environment
if 'venv' not in sys.executable:
    raise RuntimeError("This script must run in the project's virtual environment (.venv)")

def setup_paths() -> Tuple[Path, Path]:
    """Setup file paths for scanning and output."""
    project_root = Path(__file__).parent.parent
    output_report = project_root / "agent-shared" / "mdc-location-report.md"
    
    # Ensure agent-shared directory exists
    output_report.parent.mkdir(exist_ok=True)
    
    return project_root, output_report

def scan_for_mdc_files(project_root: Path) -> List[Path]:
    """Scan the entire repository for .mdc files."""
    mdc_files = []
    
    # Walk through all directories
    for root, dirs, files in os.walk(project_root):
        # Skip .git directory
        if '.git' in dirs:
            dirs.remove('.git')
        
        # Skip .venv directory
        if '.venv' in dirs:
            dirs.remove('.venv')
        
        # Skip __pycache__ directories
        if '__pycache__' in dirs:
            dirs.remove('__pycache__')
        
        # Check files in current directory
        for file in files:
            if file.endswith('.mdc'):
                file_path = Path(root) / file
                mdc_files.append(file_path)
    
    return mdc_files

def categorize_mdc_files(mdc_files: List[Path], project_root: Path) -> Dict[str, List[Path]]:
    """Categorize .mdc files by location."""
    categorized = {
        'approved': [],
        'violations': []
    }
    
    approved_path = project_root / '.cursor' / 'rules'
    
    for file_path in mdc_files:
        # Check if file is in the approved location
        if approved_path in file_path.parents or file_path.parent == approved_path:
            categorized['approved'].append(file_path)
        else:
            categorized['violations'].append(file_path)
    
    return categorized

def generate_report(categorized_files: Dict[str, List[Path]], project_root: Path) -> str:
    """Generate the validation report."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    approved_count = len(categorized_files['approved'])
    violation_count = len(categorized_files['violations'])
    
    # Determine overall status
    overall_status = "✅ PASS" if violation_count == 0 else "❌ FAIL"
    
    report = f"""# MDC Location Validation Report

> Generated: {timestamp}  
> Status: {overall_status}  
> Violations: {violation_count}

## Summary

- **Approved .mdc Files**: {approved_count}
- **Location Violations**: {violation_count}
- **Compliance Status**: {'Compliant' if violation_count == 0 else 'Non-Compliant'}

## Validation Results

### ✅ Approved Locations

All .mdc files must be located in: `.cursor/rules/`

**Approved Files Found:**
"""
    
    if categorized_files['approved']:
        for file_path in sorted(categorized_files['approved']):
            relative_path = file_path.relative_to(project_root)
            report += f"- `{relative_path}`\n"
    else:
        report += "- No .mdc files found in approved location\n"
    
    report += "\n### ❌ Location Violations\n\n"
    
    if categorized_files['violations']:
        report += "**Files Found Outside Approved Location:**\n\n"
        for file_path in sorted(categorized_files['violations']):
            relative_path = file_path.relative_to(project_root)
            report += f"- `{relative_path}`\n"
        
        report += f"""
### 🔧 Required Actions

**Immediate Actions Required:**
1. **Move Violating Files**: All .mdc files must be moved to `.cursor/rules/`
2. **Update References**: Update any references to moved files
3. **Verify Compliance**: Re-run this validation script after moving files

**Compliance Rules:**
- ✅ **Allowed**: `.cursor/rules/*.mdc`
- ❌ **Forbidden**: Any other location (e.g., `agent-core/`, `project/.mdc/`, etc.)

**Example Commands:**
```bash
# Move violating files to approved location
mv path/to/violating/file.mdc .cursor/rules/

# Verify compliance
python scripts/validate-mdc-location.py
```

### 📋 Action Items

- **Violations to Address**: {violation_count} files need to be moved
- **Compliance Target**: 100% of .mdc files in `.cursor/rules/`
- **Next Validation**: Run script after moving files

"""
    else:
        report += "**No violations found!** All .mdc files are in the correct location.\n\n"
        report += "### ✅ Compliance Achieved\n\n"
        report += "All .mdc files are properly located in `.cursor/rules/` directory.\n\n"
    
    report += f"""
## File Information

- **Project Root**: `{project_root.name}`
- **Approved Path**: `.cursor/rules/`
- **Validation Script**: `scripts/validate-mdc-location.py`
- **Report Generated**: {timestamp}
- **Total .mdc Files**: {approved_count + violation_count}

## Compliance Rules

### ✅ Allowed Locations
- `.cursor/rules/*.mdc` - **ONLY APPROVED LOCATION**

### ❌ Forbidden Locations
- `agent-core/*.mdc` - Not allowed
- `project/.mdc/*.mdc` - Not allowed
- `docs/*.mdc` - Not allowed
- Any other directory - Not allowed

### 🔒 Enforcement
- This script is part of the sprint pre-check loop
- Non-zero exit code if violations are found
- Required for agent compliance and audit safety

---

*This report is automatically generated by the MDC location validation script. Run the script again to update this report.*
"""
    
    return report

def main():
    """Main validation function."""
    print("MDC Location Validation Script")
    print("=" * 40)
    
    try:
        # Setup paths
        project_root, output_report_path = setup_paths()
        
        print(f"Scanning repository: {project_root}")
        
        # Scan for .mdc files
        print("Scanning for .mdc files...")
        mdc_files = scan_for_mdc_files(project_root)
        
        print(f"Found {len(mdc_files)} .mdc files")
        
        # Categorize files
        print("Categorizing files by location...")
        categorized_files = categorize_mdc_files(mdc_files, project_root)
        
        print(f"Approved: {len(categorized_files['approved'])}")
        print(f"Violations: {len(categorized_files['violations'])}")
        
        # Generate report
        print("Generating validation report...")
        report = generate_report(categorized_files, project_root)
        
        # Write report
        with open(output_report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"Validation report written to: {output_report_path}")
        
        # Print summary
        violation_count = len(categorized_files['violations'])
        
        if violation_count == 0:
            print("✅ Validation PASSED - All .mdc files in approved location")
            return True
        else:
            print(f"❌ Validation FAILED - {violation_count} violations found")
            print("Check the validation report for details")
            return False
        
    except Exception as e:
        print(f"❌ Validation script failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

# Ensure terminal prompt returns
print() 