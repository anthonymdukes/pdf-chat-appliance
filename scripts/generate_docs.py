#!/usr/bin/env python3
"""
Automated Documentation Generation Script

This script automates the generation of comprehensive documentation
for the PDF Chat Appliance project.
"""

import os
import sys
import json
import subprocess
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Mandatory .venv activation check
if "venv" not in sys.executable:
    raise RuntimeError("VENV NOT ACTIVATED. Please activate `.venv` before running this script.")

import markdown

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

class DocumentationGenerator:
    """Automated documentation generation system."""
    
    def __init__(self):
        """Initialize the documentation generator."""
        self.project_root = project_root
        self.docs_dir = project_root / "docs"
        self.api_docs_dir = self.docs_dir / "api"
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
    def _prepend_generated_timestamp(self, content: str) -> str:
        """Ensure the content starts with a 'Generated: <timestamp>' line."""
        gen_line = f"Generated: {self.timestamp}\n\n"
        if not content.lstrip().startswith("Generated:") and not content.lstrip().startswith("# Generated"):
            return gen_line + content
        return content
    
    def generate_changelog(self) -> str:
        """Generate changelog from git commits."""
        try:
            # Get git log for the last 30 days
            result = subprocess.run(
                ["git", "log", "--since=30 days ago", "--pretty=format:%h - %s (%an, %ad)", "--date=short"],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            
            if result.returncode == 0:
                commits = result.stdout.strip().split('\n')
                changelog = self._format_changelog(commits)
                return self._prepend_generated_timestamp(changelog)
            else:
                return "Unable to generate changelog from git commits."
                
        except Exception as e:
            return f"Error generating changelog: {e}"
    
    def _format_changelog(self, commits: List[str]) -> str:
        """Format commits into a changelog."""
        if not commits:
            return "No recent commits found."
        
        changelog = f"# Changelog\n\n"
        changelog += f"**Generated**: {self.timestamp}\n\n"
        
        # Group commits by date
        commits_by_date = {}
        for commit in commits:
            if commit.strip():
                # Extract date from commit line
                match = re.search(r'\(([^,]+), (\d{4}-\d{2}-\d{2})\)', commit)
                if match:
                    date = match.group(2)
                    if date not in commits_by_date:
                        commits_by_date[date] = []
                    commits_by_date[date].append(commit)
        
        # Sort dates and format
        for date in sorted(commits_by_date.keys(), reverse=True):
            changelog += f"## {date}\n\n"
            for commit in commits_by_date[date]:
                # Clean up commit message
                clean_commit = re.sub(r'\([^)]+\)$', '', commit).strip()
                changelog += f"- {clean_commit}\n"
            changelog += "\n"
        
        return changelog
    
    def generate_api_documentation(self) -> str:
        """Generate comprehensive API documentation."""
        api_docs = f"# API Documentation\n\n"
        api_docs += f"**Generated**: {self.timestamp}\n\n"
        
        # API Overview
        api_docs += "## Overview\n\n"
        api_docs += "The PDF Chat Appliance API provides intelligent PDF document querying capabilities.\n\n"
        
        # Endpoints
        api_docs += "## Endpoints\n\n"
        
        endpoints = [
            {
                "method": "GET",
                "path": "/health",
                "description": "Health check endpoint",
                "response": "System health status"
            },
            {
                "method": "POST", 
                "path": "/query",
                "description": "Query PDF documents",
                "response": "Intelligent response with sources"
            },
            {
                "method": "POST",
                "path": "/ingest", 
                "description": "Ingest PDF documents",
                "response": "Ingestion status"
            },
            {
                "method": "GET",
                "path": "/documents",
                "description": "List available documents", 
                "response": "Document metadata"
            }
        ]
        
        for endpoint in endpoints:
            api_docs += f"### {endpoint['method']} {endpoint['path']}\n\n"
            api_docs += f"{endpoint['description']}\n\n"
            api_docs += f"**Response**: {endpoint['response']}\n\n"
        
        return self._prepend_generated_timestamp(api_docs)
    
    def generate_readme_updates(self) -> str:
        """Generate README updates based on code changes."""
        try:
            # Check for recent changes
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            
            if result.returncode == 0:
                changes = result.stdout.strip().split('\n')
                update_suggestions = self._analyze_changes(changes)
                return self._prepend_generated_timestamp(update_suggestions)
            else:
                return "Unable to analyze recent changes."
                
        except Exception as e:
            return f"Error analyzing changes: {e}"
    
    def _analyze_changes(self, changes: List[str]) -> str:
        """Analyze git changes and suggest README updates."""
        if not changes or changes == ['']:
            return "No recent changes detected."
        
        update_suggestions = f"# README Update Suggestions\n\n"
        update_suggestions += f"**Generated**: {self.timestamp}\n\n"
        
        # Categorize changes
        new_files = []
        modified_files = []
        deleted_files = []
        
        for change in changes:
            if change.strip():
                status = change[:2]
                filename = change[3:]
                
                if status.startswith('A'):
                    new_files.append(filename)
                elif status.startswith('M'):
                    modified_files.append(filename)
                elif status.startswith('D'):
                    deleted_files.append(filename)
        
        # Generate suggestions
        if new_files:
            update_suggestions += "## New Files Added\n\n"
            for file in new_files:
                update_suggestions += f"- `{file}` - Consider adding to README\n"
            update_suggestions += "\n"
        
        if modified_files:
            update_suggestions += "## Modified Files\n\n"
            for file in modified_files:
                if file.endswith('.py'):
                    update_suggestions += f"- `{file}` - Check if API changes need documentation\n"
                elif file.endswith('.md'):
                    update_suggestions += f"- `{file}` - Documentation updated\n"
            update_suggestions += "\n"
        
        if deleted_files:
            update_suggestions += "## Deleted Files\n\n"
            for file in deleted_files:
                update_suggestions += f"- `{file}` - Remove from README if referenced\n"
            update_suggestions += "\n"
        
        return update_suggestions
    
    def generate_documentation_health_report(self) -> str:
        """Generate documentation health monitoring report."""
        health_report = f"# Documentation Health Report\n\n"
        health_report += f"**Generated**: {self.timestamp}\n\n"
        
        # Check documentation coverage
        health_report += "## Coverage Analysis\n\n"
        
        # Check API documentation
        api_files = list(self.api_docs_dir.glob("*.md")) if self.api_docs_dir.exists() else []
        health_report += f"### API Documentation\n"
        health_report += f"- Files: {len(api_files)}\n"
        health_report += f"- Status: {'Complete' if len(api_files) >= 2 else 'Incomplete'}\n\n"
        
        # Check main documentation
        main_docs = list(self.docs_dir.glob("*.md"))
        health_report += f"### Main Documentation\n"
        health_report += f"- Files: {len(main_docs)}\n"
        health_report += f"- Status: {'Complete' if len(main_docs) >= 5 else 'Incomplete'}\n\n"
        
        # Check for broken links
        health_report += "## Link Validation\n\n"
        broken_links = self._check_broken_links()
        if broken_links:
            health_report += "### Broken Links Found\n\n"
            for link in broken_links:
                health_report += f"- {link}\n"
        else:
            health_report += "No broken links detected\n"
        
        health_report += "\n"
        
        # Documentation freshness
        health_report += "## Freshness Check\n\n"
        health_report += f"Last documentation update: {self._get_last_doc_update()}\n"
        health_report += f"Status: {'Recent' if self._is_docs_fresh() else 'Needs update'}\n\n"
        
        return self._prepend_generated_timestamp(health_report)
    
    def _check_broken_links(self) -> List[str]:
        """Check for broken links in documentation."""
        broken_links = []
        
        # Simple regex to find markdown links
        link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        
        for md_file in self.docs_dir.rglob("*.md"):
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    matches = re.findall(link_pattern, content)
                    
                    for text, link in matches:
                        if link.startswith('http'):
                            # External link - could add validation here
                            pass
                        elif link.startswith('./') or link.startswith('../'):
                            # Relative link - check if file exists
                            link_path = md_file.parent / link
                            if not link_path.exists():
                                broken_links.append(f"{md_file}: {text} -> {link}")
            except Exception:
                pass
        
        return broken_links
    
    def _get_last_doc_update(self) -> str:
        """Get the last documentation update timestamp."""
        try:
            result = subprocess.run(
                ["git", "log", "-1", "--format=%cd", "--date=short", "--", "docs/"],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
            else:
                return "Unknown"
        except Exception:
            return "Unknown"
    
    def _is_docs_fresh(self) -> bool:
        """Check if documentation is fresh (updated within last 7 days)."""
        last_update = self._get_last_doc_update()
        if last_update == "Unknown":
            return False
        
        try:
            from datetime import datetime, timedelta
            last_date = datetime.strptime(last_update, "%Y-%m-%d")
            return (datetime.now() - last_date).days <= 7
        except Exception:
            return False
    
    def generate_all_documentation(self):
        """Generate all documentation components."""
        print("Starting automated documentation generation...")
        
        # Create docs directory if it doesn't exist
        self.docs_dir.mkdir(exist_ok=True)
        self.api_docs_dir.mkdir(exist_ok=True)
        
        # Generate changelog
        print("Generating changelog...")
        changelog = self.generate_changelog()
        changelog_path = self.docs_dir / "CHANGELOG.md"
        with open(changelog_path, 'w', encoding='utf-8') as f:
            f.write(changelog)
        
        # Generate API documentation
        print("Generating API documentation...")
        api_docs = self.generate_api_documentation()
        api_docs_path = self.api_docs_dir / "generated_api.md"
        with open(api_docs_path, 'w', encoding='utf-8') as f:
            f.write(api_docs)
        
        # Generate README updates
        print("Generating README update suggestions...")
        readme_updates = self.generate_readme_updates()
        readme_path = self.docs_dir / "README_UPDATES.md"
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_updates)
        
        # Generate health report
        print("Generating documentation health report...")
        health_report = self.generate_documentation_health_report()
        health_path = self.docs_dir / "HEALTH_REPORT.md"
        with open(health_path, 'w', encoding='utf-8') as f:
            f.write(health_report)
        
        # Generate documentation index
        print("Generating documentation index...")
        index = self._generate_documentation_index()
        index_path = self.docs_dir / "INDEX.md"
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(index)
        
        print("Documentation generation complete!")
        print(f"Generated files:")
        print(f"   - {changelog_path}")
        print(f"   - {api_docs_path}")
        print(f"   - {readme_path}")
        print(f"   - {health_path}")
        print(f"   - {index_path}")
    
    def _generate_documentation_index(self) -> str:
        """Generate a comprehensive documentation index."""
        index = f"# Documentation Index\n\n"
        index += f"**Generated**: {self.timestamp}\n\n"
        
        index += "## Documentation Structure\n\n"
        
        # Main documentation
        index += "### Main Documentation\n\n"
        main_docs = list(self.docs_dir.glob("*.md"))
        for doc in sorted(main_docs):
            if doc.name != "INDEX.md":
                index += f"- [{doc.stem}](./{doc.name})\n"
        
        # API documentation
        if self.api_docs_dir.exists():
            index += "\n### API Documentation\n\n"
            api_docs = list(self.api_docs_dir.glob("*.md"))
            for doc in sorted(api_docs):
                index += f"- [{doc.stem}](./api/{doc.name})\n"
        
        index += "\n## 🔄 Automation Status\n\n"
        index += "This documentation is automatically generated and updated.\n"
        index += "For manual updates, edit the source files and regenerate.\n\n"
        
        return self._prepend_generated_timestamp(index)

def main():
    """Main function to run documentation generation."""
    generator = DocumentationGenerator()
    generator.generate_all_documentation()

if __name__ == "__main__":
    main() 