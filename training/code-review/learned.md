# Code Review Knowledge Log

Use this file to track deep-dive learnings, cheat sheets, CLI examples, or key takeaways.

## Current Training Focus - 2025-07-06

### Active Responsibilities
- **Quality Standards**: Implement comprehensive code review standards and best practices
- **Automated Review**: Enhance automated code review with static analysis and security scanning
- **Review Process**: Design efficient review workflows and processes
- **Performance Review**: Include performance analysis and optimization review
- **Knowledge Sharing**: Facilitate knowledge sharing and learning through reviews

### Key Implementation Patterns

#### Automated Code Review System
```python
# automated_code_review.py
import subprocess
import json
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

class ReviewStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    CHANGES_REQUESTED = "changes_requested"
    COMMENTED = "commented"

class IssueSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class CodeIssue:
    file_path: str
    line_number: int
    severity: IssueSeverity
    message: str
    rule_id: str
    category: str
    fix_suggestion: Optional[str] = None

class AutomatedCodeReviewer:
    def __init__(self, project_root: str):
        self.project_root = project_root
        self.review_results: Dict[str, ReviewResult] = {}
        
    def run_ruff_analysis(self, file_path: str) -> List[CodeIssue]:
        """Run Ruff static analysis on a file"""
        issues = []
        
        try:
            result = subprocess.run(
                ['ruff', 'check', '--output-format=json', file_path],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            
            if result.returncode == 0:
                return issues  # No issues found
            
            # Parse Ruff output
            try:
                ruff_output = json.loads(result.stdout)
                for issue in ruff_output:
                    issues.append(CodeIssue(
                        file_path=issue.get('filename', file_path),
                        line_number=issue.get('location', {}).get('row', 0),
                        severity=self._map_ruff_severity(issue.get('code', '')),
                        message=issue.get('message', ''),
                        rule_id=issue.get('code', ''),
                        category='style',
                        fix_suggestion=issue.get('fix', {}).get('message', '')
                    ))
            except json.JSONDecodeError:
                pass
        
        except Exception as e:
            issues.append(CodeIssue(
                file_path=file_path,
                line_number=0,
                severity=IssueSeverity.HIGH,
                message=f"Error running Ruff analysis: {e}",
                rule_id='ERROR',
                category='system'
            ))
        
        return issues
```

#### Code Review Workflow Integration
```python
# review_workflow.py
import requests
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

@dataclass
class ReviewComment:
    path: str
    line: int
    message: str
    suggestion: Optional[str] = None

@dataclass
class PullRequestReview:
    pr_number: int
    status: str  # APPROVED, CHANGES_REQUESTED, COMMENTED
    comments: List[ReviewComment]
    body: str

class GitHubReviewIntegration:
    def __init__(self, token: str, owner: str, repo: str):
        self.token = token
        self.owner = owner
        self.repo = repo
        self.base_url = f"https://api.github.com/repos/{owner}/{repo}"
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
    
    def get_review_templates(self) -> Dict[str, str]:
        """Get review templates for different scenarios"""
        return {
            "approval": "✅ Code review completed. All checks passed. Ready for merge.",
            "minor_changes": "⚠️ Minor issues found. Please address the comments before merging.",
            "major_changes": "❌ Significant issues found. Please address all comments and request another review.",
            "security_issues": "🚨 Security issues detected. Please address these critical security concerns.",
            "performance_issues": "🐌 Performance issues identified. Please optimize the code before merging."
        }
```

### Best Practices Implemented

- **Review Checklists**: Implement comprehensive review checklists for different code types
- **Automated Tools**: Set up automated code quality checks and static analysis
- **Security Review**: Include security considerations in every code review
- **Performance Analysis**: Assess code performance and optimization opportunities
- **Process Improvement**: Continuously improve review processes based on feedback

### Current Focus Areas

1. **Documentation Structure Remediation**: Supporting Phase 2 consolidation efforts
2. **Quality Standards**: Implementing comprehensive code review standards
3. **Automated Review**: Enhancing automated code review with static analysis
4. **Review Process**: Designing efficient review workflows and processes
5. **Performance Review**: Including performance analysis and optimization review

### Recent Learnings

- **Review Checklist**: Implement comprehensive review checklists for different code types
- **Review Speed**: Balance thoroughness with review speed for team productivity
- **Constructive Feedback**: Provide constructive, actionable feedback to developers
- **Security Review**: Include security considerations in every code review
- **Performance Review**: Assess code performance and optimization opportunities

### Review Templates

#### Approval Template
```
✅ Code review completed. All checks passed. Ready for merge.
```

#### Minor Changes Template
```
⚠️ Minor issues found. Please address the comments before merging.
```

#### Major Changes Template
```
❌ Significant issues found. Please address all comments and request another review.
```

#### Security Issues Template
```
🚨 Security issues detected. Please address these critical security concerns.
```

#### Performance Issues Template
```
🐌 Performance issues identified. Please optimize the code before merging.
```

---

**Last Updated:** 2025-07-06  
**Status:** Active training and implementation  
**Next Review:** 2025-07-07
