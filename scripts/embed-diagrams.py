#!/usr/bin/env python3
"""
Diagram Embedding Script

Automatically embeds Mermaid diagrams into documentation files.
Reads .mmd files and embeds them into specified markdown files.

Usage:
    python scripts/embed-diagrams.py
"""

import os
import sys
import re
from pathlib import Path
from typing import List, Dict, Optional
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

def get_mermaid_files() -> Dict[str, Path]:
    """Get all Mermaid diagram files."""
    diagrams_dir = project_root / "agent-shared" / "diagrams"
    
    if not diagrams_dir.exists():
        print(f"❌ Diagrams directory not found: {diagrams_dir}")
        return {}
    
    mermaid_files = {}
    for file_path in diagrams_dir.glob("*.mmd"):
        mermaid_files[file_path.stem] = file_path
    
    return mermaid_files

def read_mermaid_content(file_path: Path) -> str:
    """Read Mermaid diagram content from file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
        return content
    except Exception as e:
        print(f"❌ Error reading {file_path}: {e}")
        return ""

def get_target_documentation_files() -> Dict[str, Path]:
    """Get target documentation files for embedding."""
    docs_dir = project_root / "docs"
    
    targets = {}
    
    # Map diagram names to documentation files
    mapping = {
        'pdf-chat-architecture': 'ROOT_ARCHITECTURE.md',
        'org-chart': 'TEAM_STRUCTURE.md'
    }
    
    for diagram_name, doc_file in mapping.items():
        doc_path = docs_dir / doc_file
        if doc_path.exists():
            targets[diagram_name] = doc_path
        else:
            print(f"⚠️  Target documentation file not found: {doc_path}")
    
    return targets

def find_embed_marker(content: str, diagram_name: str) -> Optional[tuple]:
    """Find the embed marker for a specific diagram."""
    # Look for embed markers like:
    # <!-- EMBED: diagram-name -->
    # ... content ...
    # <!-- END_EMBED: diagram-name -->
    
    start_pattern = rf'<!--\s*EMBED:\s*{re.escape(diagram_name)}\s*-->'
    end_pattern = rf'<!--\s*END_EMBED:\s*{re.escape(diagram_name)}\s*-->'
    
    start_match = re.search(start_pattern, content, re.IGNORECASE)
    if not start_match:
        return None
    
    end_match = re.search(end_pattern, content, re.IGNORECASE)
    if not end_match:
        return None
    
    start_pos = start_match.start()
    end_pos = end_match.end()
    
    return (start_pos, end_pos, start_match.group(), end_match.group())

def create_embed_marker(diagram_name: str) -> tuple:
    """Create embed marker strings for a diagram."""
    start_marker = f"<!-- EMBED: {diagram_name} -->"
    end_marker = f"<!-- END_EMBED: {diagram_name} -->"
    return start_marker, end_marker

def embed_diagram_in_content(content: str, diagram_name: str, mermaid_content: str) -> str:
    """Embed Mermaid diagram content into documentation."""
    start_marker, end_marker = create_embed_marker(diagram_name)
    
    # Check if embed markers already exist
    embed_info = find_embed_marker(content, diagram_name)
    
    if embed_info:
        # Replace existing embed
        start_pos, end_pos, _, _ = embed_info
        new_content = (
            content[:start_pos] +
            f"{start_marker}\n```mermaid\n{mermaid_content}\n```\n{end_marker}" +
            content[end_pos:]
        )
        return new_content
    else:
        # Add new embed at the end of the file
        embed_section = f"\n\n{start_marker}\n```mermaid\n{mermaid_content}\n```\n{end_marker}\n"
        return content + embed_section

def backup_file(file_path: Path) -> Optional[Path]:
    """Create a backup of the original file."""
    backup_path = file_path.with_suffix(f"{file_path.suffix}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as src:
            with open(backup_path, 'w', encoding='utf-8') as dst:
                dst.write(src.read())
        print(f"📄 Backup created: {backup_path}")
        return backup_path
    except Exception as e:
        print(f"❌ Error creating backup: {e}")
        return None

def write_file_with_backup(file_path: Path, content: str) -> bool:
    """Write content to file with automatic backup."""
    # Create backup
    backup_path = backup_file(file_path)
    if not backup_path:
        return False
    
    # Write new content
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Updated: {file_path}")
        return True
    except Exception as e:
        print(f"❌ Error writing file: {e}")
        return False

def generate_embed_report(embeds: Dict[str, Dict]) -> str:
    """Generate a report of embedding operations."""
    report = []
    report.append("# Diagram Embedding Report")
    report.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")
    
    # Summary
    total_embeds = len(embeds)
    successful = sum(1 for e in embeds.values() if e['status'] == 'success')
    failed = sum(1 for e in embeds.values() if e['status'] == 'failed')
    skipped = sum(1 for e in embeds.values() if e['status'] == 'skipped')
    
    report.append("## Summary")
    report.append(f"- **Total Diagrams:** {total_embeds}")
    report.append(f"- **Successfully Embedded:** {successful} ✅")
    report.append(f"- **Failed:** {failed} ❌")
    report.append(f"- **Skipped:** {skipped} ⚠️")
    report.append("")
    
    # Detailed results
    report.append("## Detailed Results")
    
    for diagram_name, details in embeds.items():
        status_icon = {
            'success': '✅',
            'failed': '❌',
            'skipped': '⚠️'
        }.get(details['status'], '❓')
        
        report.append(f"### {status_icon} {diagram_name}")
        report.append(f"- **Target File:** {details['target_file']}")
        report.append(f"- **Status:** {details['status']}")
        
        if details['status'] == 'success':
            report.append(f"- **Action:** Embedded successfully")
            if details.get('backup_created'):
                report.append(f"- **Backup:** {details['backup_created']}")
        elif details['status'] == 'failed':
            report.append(f"- **Error:** {details.get('error', 'Unknown error')}")
        elif details['status'] == 'skipped':
            report.append(f"- **Reason:** {details.get('reason', 'Unknown reason')}")
        
        report.append("")
    
    return "\n".join(report)

def save_embed_report(report: str, embeds: Dict[str, Dict]) -> None:
    """Save the embedding report."""
    report_file = project_root / "agent-shared" / "diagram-embedding-report.md"
    
    try:
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"📄 Embedding report saved: {report_file}")
    except Exception as e:
        print(f"❌ Error saving embedding report: {e}")

def main():
    """Main embedding function."""
    print("🔗 Diagram Embedding Script")
    print("=" * 50)
    
    # Check virtual environment
    check_venv()
    print()
    
    # Get Mermaid files
    print("📁 Scanning Mermaid diagram files...")
    mermaid_files = get_mermaid_files()
    
    if not mermaid_files:
        print("❌ No .mmd files found in agent-shared/diagrams/")
        return
    
    print(f"✅ Found {len(mermaid_files)} Mermaid diagram files")
    print()
    
    # Get target documentation files
    print("📄 Identifying target documentation files...")
    target_files = get_target_documentation_files()
    
    if not target_files:
        print("❌ No target documentation files found")
        return
    
    print(f"✅ Found {len(target_files)} target documentation files")
    print()
    
    # Process each diagram
    embeds = {}
    
    for diagram_name, mermaid_path in mermaid_files.items():
        print(f"🔗 Processing: {diagram_name}")
        
        embed_info = {
            'diagram_name': diagram_name,
            'mermaid_file': str(mermaid_path),
            'status': 'failed',
            'error': None,
            'reason': None,
            'target_file': None,
            'backup_created': None
        }
        
        # Check if we have a target file for this diagram
        if diagram_name not in target_files:
            embed_info['status'] = 'skipped'
            embed_info['reason'] = f"No target documentation file mapped for {diagram_name}"
            embeds[diagram_name] = embed_info
            print(f"  ⚠️  Skipped: {embed_info['reason']}")
            continue
        
        target_file = target_files[diagram_name]
        embed_info['target_file'] = str(target_file)
        
        # Read Mermaid content
        mermaid_content = read_mermaid_content(mermaid_path)
        if not mermaid_content:
            embed_info['error'] = "Failed to read Mermaid content"
            embeds[diagram_name] = embed_info
            print(f"  ❌ Failed: {embed_info['error']}")
            continue
        
        # Read target documentation
        try:
            with open(target_file, 'r', encoding='utf-8') as f:
                doc_content = f.read()
        except Exception as e:
            embed_info['error'] = f"Failed to read target file: {e}"
            embeds[diagram_name] = embed_info
            print(f"  ❌ Failed: {embed_info['error']}")
            continue
        
        # Embed diagram
        new_content = embed_diagram_in_content(doc_content, diagram_name, mermaid_content)
        
        # Write updated content
        if write_file_with_backup(target_file, new_content):
            embed_info['status'] = 'success'
            embed_info['backup_created'] = f"{target_file}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            print(f"  ✅ Embedded successfully")
        else:
            embed_info['error'] = "Failed to write updated content"
            print(f"  ❌ Failed: {embed_info['error']}")
        
        embeds[diagram_name] = embed_info
    
    # Generate and save report
    print("\n📊 Generating embedding report...")
    report = generate_embed_report(embeds)
    print(report)
    
    save_embed_report(report, embeds)
    
    # Summary
    successful = sum(1 for e in embeds.values() if e['status'] == 'success')
    total = len(embeds)
    
    print(f"\n🎯 Embedding Summary: {successful}/{total} diagrams embedded successfully")
    
    if successful == total:
        print("✅ All diagrams embedded successfully!")
        sys.exit(0)
    else:
        print("⚠️  Some diagrams failed to embed. Check the report for details.")
        sys.exit(1)

if __name__ == "__main__":
    main()

print() 