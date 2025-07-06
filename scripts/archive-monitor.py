#!/usr/bin/env python3
"""
Archive Monitor Script

Monitors file sizes across the repository and triggers archive events when thresholds are exceeded.
Part of Phase 3 automation for documentation structure remediation.

Usage:
    python scripts/archive-monitor.py [--check] [--report] [--threshold 500]
"""

import os
import sys
import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# Ensure we're running in the virtual environment
if 'venv' not in sys.executable:
    raise RuntimeError("This script must be run within the .venv virtual environment")

class ArchiveMonitor:
    """Monitor file sizes and trigger archive events."""
    
    def __init__(self, threshold: int = 500):
        self.threshold = threshold
        self.repo_root = Path(__file__).parent.parent
        self.archive_dir = self.repo_root / "archive"
        self.monitor_log = self.repo_root / "agent-shared" / "archive-monitor-log.json"
        
    def get_file_sizes(self) -> List[Tuple[Path, int]]:
        """Get all markdown files and their line counts."""
        files = []
        
        # Scan for .md files in key directories
        scan_dirs = [
            self.repo_root,
            self.repo_root / "docs",
            self.repo_root / "agent-shared",
            self.repo_root / "training"
        ]
        
        for scan_dir in scan_dirs:
            if scan_dir.exists():
                for md_file in scan_dir.rglob("*.md"):
                    # Skip archive files
                    if "archive" in str(md_file):
                        continue
                    
                    try:
                        with open(md_file, 'r', encoding='utf-8') as f:
                            lines = len(f.readlines())
                        files.append((md_file, lines))
                    except Exception as e:
                        print(f"Warning: Could not read {md_file}: {e}")
        
        return sorted(files, key=lambda x: x[1], reverse=True)
    
    def check_thresholds(self) -> Dict[str, List[Dict]]:
        """Check which files exceed thresholds."""
        files = self.get_file_sizes()
        results = {
            "critical": [],  # >1000 lines
            "warning": [],   # 500-1000 lines
            "normal": []     # <500 lines
        }
        
        for file_path, lines in files:
            file_info = {
                "file": str(file_path.relative_to(self.repo_root)),
                "lines": lines,
                "size_kb": file_path.stat().st_size / 1024,
                "last_modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
            }
            
            if lines > 1000:
                results["critical"].append(file_info)
            elif lines > 500:
                results["warning"].append(file_info)
            else:
                results["normal"].append(file_info)
        
        return results
    
    def generate_report(self) -> str:
        """Generate a human-readable report."""
        results = self.check_thresholds()
        
        report = f"""# Archive Monitor Report
Generated: {datetime.now().isoformat()}
Threshold: {self.threshold} lines

## Critical Files (>1000 lines)
"""
        
        if results["critical"]:
            for file_info in results["critical"]:
                report += f"- **{file_info['file']}**: {file_info['lines']} lines ({file_info['size_kb']:.1f}KB)\n"
        else:
            report += "- No critical files found ✅\n"
        
        report += "\n## Warning Files (500-1000 lines)\n"
        
        if results["warning"]:
            for file_info in results["warning"]:
                report += f"- **{file_info['file']}**: {file_info['lines']} lines ({file_info['size_kb']:.1f}KB)\n"
        else:
            report += "- No warning files found ✅\n"
        
        report += f"\n## Normal Files (<500 lines)\n"
        report += f"- {len(results['normal'])} files within normal range ✅\n"
        
        # Summary
        total_files = len(results["critical"]) + len(results["warning"]) + len(results["normal"])
        report += f"\n## Summary\n"
        report += f"- Total files scanned: {total_files}\n"
        report += f"- Critical files: {len(results['critical'])}\n"
        report += f"- Warning files: {len(results['warning'])}\n"
        report += f"- Normal files: {len(results['normal'])}\n"
        
        return report
    
    def log_event(self, event_type: str, details: Dict):
        """Log archive monitoring events."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "details": details
        }
        
        # Load existing log
        log_data = []
        if self.monitor_log.exists():
            try:
                with open(self.monitor_log, 'r') as f:
                    log_data = json.load(f)
            except json.JSONDecodeError:
                log_data = []
        
        # Add new entry
        log_data.append(log_entry)
        
        # Keep only last 100 entries
        if len(log_data) > 100:
            log_data = log_data[-100:]
        
        # Write updated log
        self.monitor_log.parent.mkdir(parents=True, exist_ok=True)
        with open(self.monitor_log, 'w') as f:
            json.dump(log_data, f, indent=2)
    
    def check_archive_health(self) -> Dict:
        """Check the health of archive directories."""
        health = {
            "archive_dirs": {},
            "total_archived_files": 0,
            "archive_size_mb": 0
        }
        
        if not self.archive_dir.exists():
            return health
        
        for archive_subdir in self.archive_dir.iterdir():
            if archive_subdir.is_dir():
                files = list(archive_subdir.rglob("*.md"))
                size_mb = sum(f.stat().st_size for f in files) / (1024 * 1024)
                
                health["archive_dirs"][archive_subdir.name] = {
                    "files": len(files),
                    "size_mb": size_mb,
                    "last_modified": datetime.fromtimestamp(archive_subdir.stat().st_mtime).isoformat()
                }
                
                health["total_archived_files"] += len(files)
                health["archive_size_mb"] += size_mb
        
        return health
    
    def suggest_archives(self) -> List[Dict]:
        """Suggest files that should be archived."""
        results = self.check_thresholds()
        suggestions = []
        
        for file_info in results["critical"] + results["warning"]:
            file_path = Path(file_info["file"])
            
            # Determine archive category based on file location and content
            if "session_notes" in file_info["file"]:
                category = "session_notes"
            elif "task" in file_info["file"].lower():
                category = "task_history"
            elif "doc" in file_info["file"].lower() and "change" in file_info["file"].lower():
                category = "doc_changes"
            elif "training" in file_info["file"].lower():
                category = "training_records"
            else:
                category = "general"
            
            suggestion = {
                "file": file_info["file"],
                "lines": file_info["lines"],
                "suggested_archive": f"archive/{category}/{datetime.now().strftime('%Y-%m-%d')}_{category}_{file_path.stem}.md",
                "reason": f"File exceeds {self.threshold} line threshold ({file_info['lines']} lines)",
                "priority": "high" if file_info["lines"] > 1000 else "medium"
            }
            
            suggestions.append(suggestion)
        
        return suggestions

def main():
    parser = argparse.ArgumentParser(description="Archive Monitor for Documentation Structure")
    parser.add_argument("--check", action="store_true", help="Check file sizes and thresholds")
    parser.add_argument("--report", action="store_true", help="Generate detailed report")
    parser.add_argument("--threshold", type=int, default=500, help="Line count threshold (default: 500)")
    parser.add_argument("--health", action="store_true", help="Check archive directory health")
    parser.add_argument("--suggest", action="store_true", help="Suggest files for archiving")
    
    args = parser.parse_args()
    
    monitor = ArchiveMonitor(threshold=args.threshold)
    
    if args.check:
        results = monitor.check_thresholds()
        print(f"Archive Monitor Check - Threshold: {args.threshold} lines")
        print(f"Critical files: {len(results['critical'])}")
        print(f"Warning files: {len(results['warning'])}")
        print(f"Normal files: {len(results['normal'])}")
        
        # Log the check event
        monitor.log_event("threshold_check", {
            "threshold": args.threshold,
            "critical_count": len(results["critical"]),
            "warning_count": len(results["warning"]),
            "normal_count": len(results["normal"])
        })
        
        if results["critical"]:
            print("\nCritical files found:")
            for file_info in results["critical"]:
                print(f"  - {file_info['file']}: {file_info['lines']} lines")
    
    if args.report:
        report = monitor.generate_report()
        print(report)
        
        # Save report to file
        report_file = monitor.repo_root / "agent-shared" / f"archive-monitor-report-{datetime.now().strftime('%Y%m%d-%H%M%S')}.md"
        report_file.parent.mkdir(parents=True, exist_ok=True)
        with open(report_file, 'w') as f:
            f.write(report)
        print(f"\nReport saved to: {report_file}")
    
    if args.health:
        health = monitor.check_archive_health()
        print("Archive Directory Health Check:")
        print(f"Total archived files: {health['total_archived_files']}")
        print(f"Total archive size: {health['archive_size_mb']:.2f}MB")
        
        for dir_name, dir_info in health["archive_dirs"].items():
            print(f"\n{dir_name}:")
            print(f"  Files: {dir_info['files']}")
            print(f"  Size: {dir_info['size_mb']:.2f}MB")
            print(f"  Last modified: {dir_info['last_modified']}")
    
    if args.suggest:
        suggestions = monitor.suggest_archives()
        if suggestions:
            print("Archive Suggestions:")
            for suggestion in suggestions:
                print(f"\n{suggestion['file']} ({suggestion['lines']} lines)")
                print(f"  Priority: {suggestion['priority']}")
                print(f"  Suggested archive: {suggestion['suggested_archive']}")
                print(f"  Reason: {suggestion['reason']}")
        else:
            print("No archive suggestions - all files within thresholds")
    
    # If no specific action requested, run check by default
    if not any([args.check, args.report, args.health, args.suggest]):
        results = monitor.check_thresholds()
        print(f"Archive Monitor - Files exceeding {args.threshold} lines: {len(results['critical']) + len(results['warning'])}")
        
        if results["critical"]:
            print("Critical files (>1000 lines):")
            for file_info in results["critical"][:5]:  # Show top 5
                print(f"  - {file_info['file']}: {file_info['lines']} lines")

if __name__ == "__main__":
    main() 