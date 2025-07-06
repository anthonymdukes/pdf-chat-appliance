#!/usr/bin/env python3
"""
Diagram Validation Script

Validates that all diagram source files have corresponding exports.
Checks for missing .svg, .png, or .mmd files for each .drawio source.

Usage:
    python scripts/validate-diagrams.py
"""

import os
import sys
import glob
from pathlib import Path
from typing import List, Dict, Tuple
import json
from datetime import datetime

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def check_venv():
    """Ensure we're running in the project's virtual environment."""
    if 'venv' not in sys.executable:
        print("❌ ERROR: Must run in project virtual environment")
        print(f"Current interpreter: {sys.executable}")
        print("Please activate .venv before running this script")
        sys.exit(1)
    print(f"✅ Virtual environment: {sys.executable}")

def get_diagram_files() -> Dict[str, List[Path]]:
    """Get all diagram files organized by type."""
    diagrams_dir = project_root / "agent-shared" / "diagrams"
    
    if not diagrams_dir.exists():
        print(f"❌ Diagrams directory not found: {diagrams_dir}")
        return {}
    
    files = {
        'drawio': [],
        'mmd': [],
        'svg': [],
        'png': [],
        'other': []
    }
    
    for file_path in diagrams_dir.glob("*"):
        if file_path.is_file():
            suffix = file_path.suffix.lower()
            if suffix == '.drawio':
                files['drawio'].append(file_path)
            elif suffix == '.mmd':
                files['mmd'].append(file_path)
            elif suffix == '.svg':
                files['svg'].append(file_path)
            elif suffix == '.png':
                files['png'].append(file_path)
            else:
                files['other'].append(file_path)
    
    return files

def analyze_diagram_completeness(files: Dict[str, List[Path]]) -> Dict[str, Dict]:
    """Analyze completeness of diagram exports."""
    analysis = {}
    
    # Check each .drawio file for corresponding exports
    for drawio_file in files['drawio']:
        base_name = drawio_file.stem
        analysis[base_name] = {
            'source': drawio_file,
            'has_mmd': False,
            'has_svg': False,
            'has_png': False,
            'missing': [],
            'status': 'incomplete'
        }
        
        # Check for Mermaid version
        mmd_file = drawio_file.parent / f"{base_name}.mmd"
        if mmd_file.exists():
            analysis[base_name]['has_mmd'] = True
        else:
            analysis[base_name]['missing'].append('mmd')
        
        # Check for SVG export
        svg_file = drawio_file.parent / f"{base_name}.svg"
        if svg_file.exists():
            analysis[base_name]['has_svg'] = True
        else:
            analysis[base_name]['missing'].append('svg')
        
        # Check for PNG export
        png_file = drawio_file.parent / f"{base_name}.png"
        if png_file.exists():
            analysis[base_name]['has_png'] = True
        else:
            analysis[base_name]['missing'].append('png')
        
        # Determine status
        if not analysis[base_name]['missing']:
            analysis[base_name]['status'] = 'complete'
        elif len(analysis[base_name]['missing']) == 1 and 'png' in analysis[base_name]['missing']:
            analysis[base_name]['status'] = 'acceptable'  # PNG optional
        else:
            analysis[base_name]['status'] = 'incomplete'
    
    # Check orphaned files (exports without source)
    orphaned = []
    for export_type in ['mmd', 'svg', 'png']:
        for export_file in files[export_type]:
            base_name = export_file.stem
            drawio_file = export_file.parent / f"{base_name}.drawio"
            if not drawio_file.exists():
                orphaned.append({
                    'file': export_file,
                    'type': export_type,
                    'base_name': base_name
                })
    
    analysis['_orphaned'] = orphaned
    
    return analysis

def generate_report(analysis: Dict[str, Dict], files: Dict[str, List[Path]]) -> str:
    """Generate a comprehensive validation report."""
    report = []
    report.append("# Diagram Validation Report")
    report.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"**Total Files:** {sum(len(f) for f in files.values())}")
    report.append("")
    
    # Summary statistics
    total_drawio = len(files['drawio'])
    complete = sum(1 for a in analysis.values() if isinstance(a, dict) and a.get('status') == 'complete')
    acceptable = sum(1 for a in analysis.values() if isinstance(a, dict) and a.get('status') == 'acceptable')
    incomplete = sum(1 for a in analysis.values() if isinstance(a, dict) and a.get('status') == 'incomplete')
    
    report.append("## Summary")
    report.append(f"- **Total Diagrams:** {total_drawio}")
    report.append(f"- **Complete:** {complete} ✅")
    report.append(f"- **Acceptable:** {acceptable} ⚠️")
    report.append(f"- **Incomplete:** {incomplete} ❌")
    report.append("")
    
    # Detailed analysis
    report.append("## Detailed Analysis")
    
    for diagram_name, details in analysis.items():
        if diagram_name.startswith('_'):
            continue
            
        status_icon = {
            'complete': '✅',
            'acceptable': '⚠️',
            'incomplete': '❌'
        }.get(details['status'], '❓')
        
        report.append(f"### {status_icon} {diagram_name}")
        report.append(f"- **Source:** {details['source'].name}")
        report.append(f"- **Status:** {details['status']}")
        
        exports = []
        if details['has_mmd']:
            exports.append("✅ Mermaid (.mmd)")
        if details['has_svg']:
            exports.append("✅ SVG (.svg)")
        if details['has_png']:
            exports.append("✅ PNG (.png)")
        
        report.append(f"- **Exports:** {', '.join(exports) if exports else 'None'}")
        
        if details['missing']:
            report.append(f"- **Missing:** {', '.join(details['missing'])}")
        
        report.append("")
    
    # Orphaned files
    if analysis.get('_orphaned'):
        report.append("## Orphaned Export Files")
        report.append("These export files exist without corresponding .drawio sources:")
        report.append("")
        
        for orphan in analysis['_orphaned']:
            report.append(f"- **{orphan['file'].name}** (type: {orphan['type']})")
        
        report.append("")
    
    # Recommendations
    report.append("## Recommendations")
    
    if incomplete > 0:
        report.append("### Immediate Actions Required:")
        for diagram_name, details in analysis.items():
            if diagram_name.startswith('_'):
                continue
            if details['status'] == 'incomplete':
                missing = ', '.join(details['missing'])
                report.append(f"- Export **{diagram_name}** to: {missing}")
        report.append("")
    
    if analysis.get('_orphaned'):
        report.append("### Cleanup Actions:")
        report.append("- Review orphaned export files")
        report.append("- Remove or rename as needed")
        report.append("")
    
    report.append("### Best Practices:")
    report.append("- Always export .svg for documentation")
    report.append("- Include .mmd for markdown embedding")
    report.append("- PNG exports are optional but recommended")
    report.append("- Keep source .drawio files in version control")
    
    return "\n".join(report)

def save_report(report: str, analysis: Dict[str, Dict]) -> None:
    """Save the validation report and analysis data."""
    # Save human-readable report
    report_file = project_root / "agent-shared" / "diagram-validation-report.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    # Save machine-readable analysis
    analysis_file = project_root / "agent-shared" / "diagram-validation-data.json"
    analysis_data = {
        'timestamp': datetime.now().isoformat(),
        'analysis': analysis,
        'summary': {
            'total_drawio': len([k for k in analysis.keys() if not k.startswith('_')]),
            'complete': len([a for a in analysis.values() if isinstance(a, dict) and a.get('status') == 'complete']),
            'acceptable': len([a for a in analysis.values() if isinstance(a, dict) and a.get('status') == 'acceptable']),
            'incomplete': len([a for a in analysis.values() if isinstance(a, dict) and a.get('status') == 'incomplete']),
            'orphaned': len(analysis.get('_orphaned', []))
        }
    }
    
    with open(analysis_file, 'w', encoding='utf-8') as f:
        json.dump(analysis_data, f, indent=2, default=str)
    
    print(f"📄 Report saved: {report_file}")
    print(f"📊 Data saved: {analysis_file}")

def main():
    """Main validation function."""
    print("🔍 Diagram Validation Script")
    print("=" * 50)
    
    # Check virtual environment
    check_venv()
    print()
    
    # Get diagram files
    print("📁 Scanning diagram files...")
    files = get_diagram_files()
    
    if not files['drawio']:
        print("❌ No .drawio files found in agent-shared/diagrams/")
        return
    
    print(f"✅ Found {len(files['drawio'])} diagram source files")
    print()
    
    # Analyze completeness
    print("🔍 Analyzing diagram completeness...")
    analysis = analyze_diagram_completeness(files)
    
    # Generate and display report
    report = generate_report(analysis, files)
    print(report)
    
    # Save reports
    print("\n💾 Saving validation reports...")
    save_report(report, analysis)
    
    # Exit with appropriate code
    incomplete_count = len([a for a in analysis.values() if isinstance(a, dict) and a.get('status') == 'incomplete'])
    if incomplete_count > 0:
        print(f"\n❌ Validation failed: {incomplete_count} incomplete diagrams")
        sys.exit(1)
    else:
        print("\n✅ All diagrams are complete or acceptable")
        sys.exit(0)

if __name__ == "__main__":
    main()

print() 