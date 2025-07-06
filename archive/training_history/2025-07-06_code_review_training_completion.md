# Code Review Training History Archive

**Archived:** 2025-07-06  
**Source:** training/code-review/learned.md  
**Reason:** Historical training completion records (Phase 2 consolidation)

---

## Training Assignment - Phase 2b (2025-07-06)

### Code Review Best Practices & Quality Standards

- **Date**: 2025-07-06
- **Source**: https://google.github.io/eng-practices/review/
- **Summary**: Google's code review best practices and quality standards
- **Notes**: 
  - **Review Checklist**: Implement comprehensive review checklists for different code types
  - **Review Speed**: Balance thoroughness with review speed for team productivity
  - **Constructive Feedback**: Provide constructive, actionable feedback to developers
  - **Security Review**: Include security considerations in every code review
  - **Performance Review**: Assess code performance and optimization opportunities
  - **Documentation Review**: Ensure code is properly documented and maintainable
  - **Testing Review**: Verify adequate test coverage and test quality

### Automated Code Review & Static Analysis

- **Date**: 2025-07-06
- **Source**: https://docs.astral.sh/ruff/
- **Summary**: Ruff static analysis and automated code review patterns
- **Notes**:
  - **Static Analysis**: Implement comprehensive static analysis tools
  - **Automated Checks**: Set up automated code quality checks in CI/CD
  - **Custom Rules**: Create custom linting rules for project-specific requirements
  - **Performance Analysis**: Use profiling tools to identify performance issues
  - **Security Scanning**: Integrate security scanning tools into review process
  - **Code Metrics**: Track code quality metrics and trends over time
  - **Integration**: Integrate review tools with development workflows

### Code Review Workflow & Process

- **Date**: 2025-07-06
- **Source**: https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/reviewing-changes-in-pull-requests
- **Summary**: GitHub pull request review workflow and process patterns
- **Notes**:
  - **Review Workflow**: Implement standardized review workflows and processes
  - **Review Templates**: Create review templates for consistent feedback
  - **Review Assignment**: Automate review assignment based on expertise and availability
  - **Review Tracking**: Track review metrics and performance indicators
  - **Escalation Process**: Implement escalation processes for complex reviews
  - **Knowledge Sharing**: Facilitate knowledge sharing through review comments
  - **Continuous Improvement**: Continuously improve review processes based on feedback

---

## Key Responsibilities Added

1. **Quality Standards**: Implement comprehensive code review standards and best practices
2. **Automated Review**: Enhance automated code review with static analysis and security scanning
3. **Review Process**: Design efficient review workflows and processes
4. **Performance Review**: Include performance analysis and optimization review
5. **Knowledge Sharing**: Facilitate knowledge sharing and learning through reviews

## Best Practices Implemented

- **Review Checklists**: Implement comprehensive review checklists for different code types
- **Automated Tools**: Set up automated code quality checks and static analysis
- **Security Review**: Include security considerations in every code review
- **Performance Analysis**: Assess code performance and optimization opportunities
- **Process Improvement**: Continuously improve review processes based on feedback

## Code Review Implementation Patterns

### Automated Code Review System
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

@dataclass
class ReviewResult:
    file_path: str
    issues: List[CodeIssue]
    metrics: Dict[str, Any]
    status: ReviewStatus
    review_comments: List[str] = None

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
                # Fallback to parsing stderr
                for line in result.stderr.split('\n'):
                    if ':' in line:
                        parts = line.split(':')
                        if len(parts) >= 3:
                            issues.append(CodeIssue(
                                file_path=parts[0],
                                line_number=int(parts[1]) if parts[1].isdigit() else 0,
                                severity=IssueSeverity.MEDIUM,
                                message=':'.join(parts[2:]),
                                rule_id='RUFF',
                                category='style'
                            ))
        
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
    
    def run_security_scan(self, file_path: str) -> List[CodeIssue]:
        """Run security analysis on a file"""
        issues = []
        
        try:
            result = subprocess.run(
                ['bandit', '-f', 'json', '-r', file_path],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            
            try:
                bandit_output = json.loads(result.stdout)
                for issue in bandit_output.get('results', []):
                    issues.append(CodeIssue(
                        file_path=issue.get('filename', file_path),
                        line_number=issue.get('line_number', 0),
                        severity=self._map_bandit_severity(issue.get('issue_severity', '')),
                        message=issue.get('issue_text', ''),
                        rule_id=issue.get('test_id', ''),
                        category='security',
                        fix_suggestion=issue.get('more_info', '')
                    ))
            except json.JSONDecodeError:
                pass
        
        except Exception as e:
            issues.append(CodeIssue(
                file_path=file_path,
                line_number=0,
                severity=IssueSeverity.MEDIUM,
                message=f"Error running security scan: {e}",
                rule_id='ERROR',
                category='system'
            ))
        
        return issues
    
    def _map_ruff_severity(self, code: str) -> IssueSeverity:
        """Map Ruff error codes to severity levels"""
        if code.startswith('E'):  # Error
            return IssueSeverity.HIGH
        elif code.startswith('W'):  # Warning
            return IssueSeverity.MEDIUM
        elif code.startswith('F'):  # Fatal
            return IssueSeverity.CRITICAL
        else:
            return IssueSeverity.LOW
    
    def _map_bandit_severity(self, severity: str) -> IssueSeverity:
        """Map Bandit severity to internal severity levels"""
        severity_map = {
            'LOW': IssueSeverity.LOW,
            'MEDIUM': IssueSeverity.MEDIUM,
            'HIGH': IssueSeverity.HIGH
        }
        return severity_map.get(severity.upper(), IssueSeverity.MEDIUM)
    
    def calculate_metrics(self, file_path: str) -> Dict[str, Any]:
        """Calculate code quality metrics for a file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
            
            metrics = {
                'total_lines': len(lines),
                'code_lines': len([l for l in lines if l.strip() and not l.strip().startswith('#')]),
                'comment_lines': len([l for l in lines if l.strip().startswith('#')]),
                'blank_lines': len([l for l in lines if not l.strip()]),
                'complexity': self._calculate_complexity(content),
                'maintainability_index': self._calculate_maintainability(content)
            }
            
            return metrics
        
        except Exception as e:
            return {
                'error': str(e),
                'total_lines': 0,
                'code_lines': 0,
                'comment_lines': 0,
                'blank_lines': 0,
                'complexity': 0,
                'maintainability_index': 0
            }
    
    def _calculate_complexity(self, content: str) -> int:
        """Calculate cyclomatic complexity"""
        complexity = 1  # Base complexity
        
        # Count control flow statements
        complexity += content.count('if ')
        complexity += content.count('elif ')
        complexity += content.count('for ')
        complexity += content.count('while ')
        complexity += content.count('except ')
        complexity += content.count('and ')
        complexity += content.count('or ')
        
        return complexity
    
    def _calculate_maintainability_index(self, content: str) -> float:
        """Calculate maintainability index (simplified)"""
        lines = content.split('\n')
        code_lines = len([l for l in lines if l.strip() and not l.strip().startswith('#')])
        comment_lines = len([l for l in lines if l.strip().startswith('#')])
        
        if code_lines == 0:
            return 100.0
        
        # Simplified maintainability index
        comment_ratio = comment_lines / code_lines if code_lines > 0 else 0
        complexity = self._calculate_complexity(content)
        
        # Higher is better (0-100 scale)
        maintainability = 100 - (complexity * 2) + (comment_ratio * 10)
        return max(0, min(100, maintainability))
    
    def review_file(self, file_path: str) -> ReviewResult:
        """Review a single file"""
        issues = []
        
        # Run static analysis
        issues.extend(self.run_ruff_analysis(file_path))
        
        # Run security scan
        issues.extend(self.run_security_scan(file_path))
        
        # Calculate metrics
        metrics = self.calculate_metrics(file_path)
        
        # Determine review status
        critical_issues = len([i for i in issues if i.severity == IssueSeverity.CRITICAL])
        high_issues = len([i for i in issues if i.severity == IssueSeverity.HIGH])
        
        if critical_issues > 0:
            status = ReviewStatus.CHANGES_REQUESTED
        elif high_issues > 0:
            status = ReviewStatus.COMMENTED
        elif issues:
            status = ReviewStatus.COMMENTED
        else:
            status = ReviewStatus.APPROVED
        
        # Generate review comments
        review_comments = []
        for issue in issues:
            comment = f"{issue.severity.value.upper()}: {issue.message}"
            if issue.fix_suggestion:
                comment += f" Suggestion: {issue.fix_suggestion}"
            review_comments.append(comment)
        
        result = ReviewResult(
            file_path=file_path,
            issues=issues,
            metrics=metrics,
            status=status,
            review_comments=review_comments
        )
        
        self.review_results[file_path] = result
        return result
    
    def review_directory(self, directory: str) -> Dict[str, ReviewResult]:
        """Review all Python files in a directory"""
        results = {}
        
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    results[file_path] = self.review_file(file_path)
        
        return results
    
    def generate_review_report(self) -> Dict[str, Any]:
        """Generate comprehensive review report"""
        total_files = len(self.review_results)
        total_issues = sum(len(result.issues) for result in self.review_results.values())
        
        issues_by_severity = {
            'critical': 0,
            'high': 0,
            'medium': 0,
            'low': 0
        }
        
        issues_by_category = {
            'style': 0,
            'security': 0,
            'system': 0
        }
        
        for result in self.review_results.values():
            for issue in result.issues:
                issues_by_severity[issue.severity.value] += 1
                issues_by_category[issue.category] += 1
        
        status_counts = {
            'approved': 0,
            'commented': 0,
            'changes_requested': 0
        }
        
        for result in self.review_results.values():
            status_counts[result.status.value] += 1
        
        return {
            'summary': {
                'total_files': total_files,
                'total_issues': total_issues,
                'files_with_issues': sum(1 for r in self.review_results.values() if r.issues),
                'approval_rate': (status_counts['approved'] / total_files * 100) if total_files > 0 else 0
            },
            'issues_by_severity': issues_by_severity,
            'issues_by_category': issues_by_category,
            'status_counts': status_counts,
            'files': {
                file_path: {
                    'status': result.status.value,
                    'issue_count': len(result.issues),
                    'metrics': result.metrics
                }
                for file_path, result in self.review_results.items()
            }
        }

# Usage example
def main():
    reviewer = AutomatedCodeReviewer(".")
    
    # Review specific file
    result = reviewer.review_file("pdfchat/server.py")
    print(f"Review result for server.py: {result.status.value}")
    print(f"Issues found: {len(result.issues)}")
    
    # Review entire project
    results = reviewer.review_directory("pdfchat")
    
    # Generate report
    report = reviewer.generate_review_report()
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()
```

### Code Review Workflow Integration
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
    
    def get_pull_request(self, pr_number: int) -> Dict[str, Any]:
        """Get pull request details"""
        response = requests.get(
            f"{self.base_url}/pulls/{pr_number}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def get_pull_request_files(self, pr_number: int) -> List[Dict[str, Any]]:
        """Get files changed in a pull request"""
        response = requests.get(
            f"{self.base_url}/pulls/{pr_number}/files",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def create_review(self, pr_number: int, review: PullRequestReview) -> Dict[str, Any]:
        """Create a pull request review"""
        comments = []
        for comment in review.comments:
            comments.append({
                "path": comment.path,
                "line": comment.line,
                "body": comment.message
            })
        
        data = {
            "body": review.body,
            "event": review.status.upper(),
            "comments": comments
        }
        
        response = requests.post(
            f"{self.base_url}/pulls/{pr_number}/reviews",
            headers=self.headers,
            json=data
        )
        response.raise_for_status()
        return response.json()
    
    def get_review_templates(self) -> Dict[str, str]:
        """Get review templates for different scenarios"""
        return {
            "approval": "✅ Code review completed. All checks passed. Ready for merge.",
            "minor_changes": "⚠️ Minor issues found. Please address the comments before merging.",
            "major_changes": "❌ Significant issues found. Please address all comments and request another review.",
            "security_issues": "🚨 Security issues detected. Please address these critical security concerns.",
            "performance_issues": "🐌 Performance issues identified. Please optimize the code before merging."
        }
    
    def auto_review_pull_request(self, pr_number: int, reviewer: AutomatedCodeReviewer) -> PullRequestReview:
        """Automatically review a pull request"""
        # Get PR details
        pr = self.get_pull_request(pr_number)
        files = self.get_pull_request_files(pr_number)
        
        all_comments = []
        total_issues = 0
        critical_issues = 0
        high_issues = 0
        
        # Review each changed file
        for file_info in files:
            if file_info['filename'].endswith('.py'):
                # Download file content for review
                file_content = requests.get(file_info['raw_url']).text
                
                # Save temporarily for review
                temp_file = f"temp_{file_info['filename'].replace('/', '_')}"
                with open(temp_file, 'w') as f:
                    f.write(file_content)
                
                # Review the file
                result = reviewer.review_file(temp_file)
                
                # Convert issues to comments
                for issue in result.issues:
                    all_comments.append(ReviewComment(
                        path=file_info['filename'],
                        line=issue.line_number,
                        message=f"{issue.severity.value.upper()}: {issue.message}",
                        suggestion=issue.fix_suggestion
                    ))
                    
                    total_issues += 1
                    if issue.severity == IssueSeverity.CRITICAL:
                        critical_issues += 1
                    elif issue.severity == IssueSeverity.HIGH:
                        high_issues += 1
                
                # Clean up temp file
                os.remove(temp_file)
        
        # Determine review status
        if critical_issues > 0:
            status = "CHANGES_REQUESTED"
            body = self.get_review_templates()["security_issues"]
        elif high_issues > 0:
            status = "COMMENTED"
            body = self.get_review_templates()["major_changes"]
        elif total_issues > 0:
            status = "COMMENTED"
            body = self.get_review_templates()["minor_changes"]
        else:
            status = "APPROVED"
            body = self.get_review_templates()["approval"]
        
        return PullRequestReview(
            pr_number=pr_number,
            status=status,
            comments=all_comments,
            body=body
        )

# Usage example
def main():
    # Initialize components
    reviewer = AutomatedCodeReviewer(".")
    github_integration = GitHubReviewIntegration(
        token="your_github_token",
        owner="your_username",
        repo="your_repo"
    )
    
    # Auto-review a pull request
    pr_number = 123
    review = github_integration.auto_review_pull_request(pr_number, reviewer)
    
    # Submit the review
    result = github_integration.create_review(pr_number, review)
    print(f"Review submitted: {result['state']}")

if __name__ == "__main__":
    main()
```

## Training Status: ✅ COMPLETED

- Enhanced code review standards with comprehensive checklists
- Implemented automated code review with static analysis and security scanning
- Designed efficient review workflows and processes
- Updated `code-review.mdc` with new responsibilities

## ✅ Role Alignment Summary
- My `.mdc` reflects my training: ✅ Yes
- Learned concepts directly enhance my duties: ✅ Yes
- Any scope updates applied: ✅ Yes (Enhanced with quality standards, automated review, review process, performance review, knowledge sharing) 