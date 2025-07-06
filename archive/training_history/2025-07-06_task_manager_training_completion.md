# Task Manager Training History Archive

**Archived:** 2025-07-06  
**Source:** training/task-manager/learned.md  
**Reason:** Historical training completion records (Phase 2 consolidation)

---

## Training Assignment - Phase 2b (2025-07-06)

### Agile Task Management & Workflow Tracking

- **Date**: 2025-07-06
- **Source**: https://www.atlassian.com/agile/scrum/backlog
- **Summary**: Scrum backlog management and task prioritization patterns
- **Notes**: 
  - **Backlog Refinement**: Continuous backlog grooming and story point estimation
  - **Sprint Planning**: Coordinate sprint planning sessions and capacity planning
  - **Task Breakdown**: Break down epics into manageable stories and tasks
  - **Dependency Management**: Track and manage task dependencies and blockers
  - **Velocity Tracking**: Monitor team velocity and predict sprint capacity
  - **Burndown Charts**: Generate and maintain sprint burndown charts
  - **Retrospectives**: Facilitate sprint retrospectives and process improvements

### Project Management & Status Tracking

- **Date**: 2025-07-06
- **Source**: https://www.pmi.org/pmbok-guide-standards/foundational/pmbok
- **Summary**: PMBOK project management principles and status tracking
- **Notes**:
  - **Project Planning**: Develop comprehensive project plans and schedules
  - **Risk Management**: Identify, assess, and mitigate project risks
  - **Stakeholder Management**: Manage stakeholder expectations and communications
  - **Quality Management**: Ensure project deliverables meet quality standards
  - **Change Management**: Handle scope changes and impact assessment
  - **Resource Management**: Optimize resource allocation and utilization
  - **Performance Monitoring**: Track project performance and KPIs

### Workflow Automation & Integration

- **Date**: 2025-07-06
- **Source**: https://docs.github.com/en/issues/tracking-your-work-with-issues
- **Summary**: GitHub Issues workflow automation and integration patterns
- **Notes**:
  - **Issue Templates**: Create standardized issue templates for different types
  - **Automated Workflows**: Implement automated issue assignment and status updates
  - **Integration**: Integrate with CI/CD pipelines and deployment workflows
  - **Reporting**: Generate automated reports and dashboards
  - **Notifications**: Set up automated notifications for status changes
  - **Metrics**: Track key metrics and performance indicators
  - **Custom Fields**: Implement custom fields for project-specific tracking

---

## Key Responsibilities Added

1. **Agile Management**: Implement comprehensive agile task management with backlog refinement and sprint planning
2. **Project Tracking**: Enhance project management with risk assessment and stakeholder management
3. **Workflow Automation**: Design automated workflows for task assignment and status tracking
4. **Performance Monitoring**: Implement performance tracking and KPI monitoring
5. **Process Improvement**: Facilitate continuous process improvement through retrospectives

## Best Practices Implemented

- **Backlog Management**: Continuous backlog grooming and story point estimation
- **Sprint Planning**: Coordinate sprint planning sessions and capacity planning
- **Dependency Tracking**: Track and manage task dependencies and blockers
- **Velocity Monitoring**: Monitor team velocity and predict sprint capacity
- **Automated Reporting**: Generate automated reports and dashboards

## Task Management Implementation Patterns

### Agile Task Management System
```python
# agile_task_manager.py
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum

class TaskStatus(Enum):
    BACKLOG = "backlog"
    SPRINT = "sprint"
    IN_PROGRESS = "in-progress"
    REVIEW = "review"
    DONE = "done"
    BLOCKED = "blocked"

class TaskPriority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class Task:
    id: str
    title: str
    description: str
    status: TaskStatus
    priority: TaskPriority
    story_points: int
    assignee: Optional[str] = None
    epic: Optional[str] = None
    dependencies: List[str] = None
    blockers: List[str] = None
    created_at: datetime = None
    updated_at: datetime = None
    completed_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
        if self.blockers is None:
            self.blockers = []
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()

@dataclass
class Sprint:
    id: str
    name: str
    start_date: datetime
    end_date: datetime
    goals: List[str]
    tasks: List[str]
    status: str  # planning, active, completed
    velocity_target: int = 0
    actual_velocity: int = 0

class AgileTaskManager:
    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self.sprints: Dict[str, Sprint] = {}
        self.current_sprint: Optional[str] = None
        self.epics: Dict[str, Dict[str, Any]] = {}
        
    def create_task(self, task_id: str, title: str, description: str, 
                   story_points: int, priority: TaskPriority = TaskPriority.MEDIUM) -> Task:
        """Create a new task"""
        task = Task(
            id=task_id,
            title=title,
            description=description,
            status=TaskStatus.BACKLOG,
            priority=priority,
            story_points=story_points
        )
        
        self.tasks[task_id] = task
        return task
    
    def update_task_status(self, task_id: str, status: TaskStatus, assignee: str = None):
        """Update task status and optionally assign"""
        if task_id not in self.tasks:
            raise ValueError(f"Task {task_id} not found")
        
        task = self.tasks[task_id]
        task.status = status
        task.updated_at = datetime.now()
        
        if assignee:
            task.assignee = assignee
        
        if status == TaskStatus.DONE:
            task.completed_at = datetime.now()
    
    def add_task_dependency(self, task_id: str, dependency_id: str):
        """Add a dependency to a task"""
        if task_id not in self.tasks or dependency_id not in self.tasks:
            raise ValueError("Task or dependency not found")
        
        if dependency_id not in self.tasks[task_id].dependencies:
            self.tasks[task_id].dependencies.append(dependency_id)
    
    def add_task_blocker(self, task_id: str, blocker_id: str):
        """Add a blocker to a task"""
        if task_id not in self.tasks or blocker_id not in self.tasks:
            raise ValueError("Task or blocker not found")
        
        if blocker_id not in self.tasks[task_id].blockers:
            self.tasks[task_id].blockers.append(blocker_id)
            self.tasks[task_id].status = TaskStatus.BLOCKED
    
    def get_ready_tasks(self) -> List[Task]:
        """Get tasks that are ready to be worked on"""
        ready_tasks = []
        
        for task in self.tasks.values():
            if task.status == TaskStatus.SPRINT:
                # Check if all dependencies are completed
                dependencies_met = True
                for dep_id in task.dependencies:
                    if dep_id in self.tasks:
                        dep_task = self.tasks[dep_id]
                        if dep_task.status != TaskStatus.DONE:
                            dependencies_met = False
                            break
                
                if dependencies_met and not task.blockers:
                    ready_tasks.append(task)
        
        return ready_tasks
    
    def get_task_metrics(self) -> Dict[str, Any]:
        """Get comprehensive task metrics"""
        total_tasks = len(self.tasks)
        completed_tasks = len([t for t in self.tasks.values() if t.status == TaskStatus.DONE])
        in_progress_tasks = len([t for t in self.tasks.values() if t.status == TaskStatus.IN_PROGRESS])
        blocked_tasks = len([t for t in self.tasks.values() if t.status == TaskStatus.BLOCKED])
        
        total_story_points = sum(t.story_points for t in self.tasks.values())
        completed_story_points = sum(t.story_points for t in self.tasks.values() if t.status == TaskStatus.DONE)
        
        # Calculate velocity (story points per sprint)
        if self.current_sprint and self.current_sprint in self.sprints:
            sprint = self.sprints[self.current_sprint]
            sprint_tasks = [t for t in self.tasks.values() if t.id in sprint.tasks]
            sprint_completed = [t for t in sprint_tasks if t.status == TaskStatus.DONE]
            velocity = sum(t.story_points for t in sprint_completed)
        else:
            velocity = 0
        
        return {
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'in_progress_tasks': in_progress_tasks,
            'blocked_tasks': blocked_tasks,
            'completion_rate': (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0,
            'total_story_points': total_story_points,
            'completed_story_points': completed_story_points,
            'story_point_completion_rate': (completed_story_points / total_story_points * 100) if total_story_points > 0 else 0,
            'velocity': velocity,
            'average_story_points_per_task': total_story_points / total_tasks if total_tasks > 0 else 0
        }
    
    def create_sprint(self, sprint_id: str, name: str, start_date: datetime, 
                     end_date: datetime, goals: List[str]) -> Sprint:
        """Create a new sprint"""
        sprint = Sprint(
            id=sprint_id,
            name=name,
            start_date=start_date,
            end_date=end_date,
            goals=goals,
            tasks=[],
            status="planning"
        )
        
        self.sprints[sprint_id] = sprint
        return sprint
    
    def add_task_to_sprint(self, sprint_id: str, task_id: str):
        """Add a task to a sprint"""
        if sprint_id not in self.sprints:
            raise ValueError(f"Sprint {sprint_id} not found")
        if task_id not in self.tasks:
            raise ValueError(f"Task {task_id} not found")
        
        sprint = self.sprints[sprint_id]
        if task_id not in sprint.tasks:
            sprint.tasks.append(task_id)
        
        # Update task status
        self.tasks[task_id].status = TaskStatus.SPRINT
    
    def start_sprint(self, sprint_id: str):
        """Start a sprint"""
        if sprint_id not in self.sprints:
            raise ValueError(f"Sprint {sprint_id} not found")
        
        sprint = self.sprints[sprint_id]
        sprint.status = "active"
        self.current_sprint = sprint_id
        
        # Update task statuses
        for task_id in sprint.tasks:
            if task_id in self.tasks:
                self.tasks[task_id].status = TaskStatus.SPRINT
    
    def complete_sprint(self, sprint_id: str):
        """Complete a sprint"""
        if sprint_id not in self.sprints:
            raise ValueError(f"Sprint {sprint_id} not found")
        
        sprint = self.sprints[sprint_id]
        sprint.status = "completed"
        
        # Calculate actual velocity
        completed_tasks = [t for t in self.tasks.values() 
                          if t.id in sprint.tasks and t.status == TaskStatus.DONE]
        sprint.actual_velocity = sum(t.story_points for t in completed_tasks)
        
        if self.current_sprint == sprint_id:
            self.current_sprint = None
    
    def export_tasks(self, filepath: str):
        """Export tasks to JSON file"""
        data = {
            'tasks': [asdict(task) for task in self.tasks.values()],
            'sprints': [asdict(sprint) for sprint in self.sprints.values()],
            'current_sprint': self.current_sprint,
            'epics': self.epics
        }
        
        # Convert datetime objects to ISO format
        for task_data in data['tasks']:
            if task_data['created_at']:
                task_data['created_at'] = task_data['created_at'].isoformat()
            if task_data['updated_at']:
                task_data['updated_at'] = task_data['updated_at'].isoformat()
            if task_data['completed_at']:
                task_data['completed_at'] = task_data['completed_at'].isoformat()
        
        for sprint_data in data['sprints']:
            if sprint_data['start_date']:
                sprint_data['start_date'] = sprint_data['start_date'].isoformat()
            if sprint_data['end_date']:
                sprint_data['end_date'] = sprint_data['end_date'].isoformat()
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

# Usage example
def main():
    manager = AgileTaskManager()
    
    # Create tasks
    tasks = [
        manager.create_task("task-1", "Implement PDF parsing", "Parse PDF files and extract text", 5, TaskPriority.HIGH),
        manager.create_task("task-2", "Add vector embeddings", "Generate embeddings for extracted text", 8, TaskPriority.HIGH),
        manager.create_task("task-3", "Implement search", "Search through embedded vectors", 13, TaskPriority.MEDIUM),
        manager.create_task("task-4", "Add UI", "Create web interface", 8, TaskPriority.MEDIUM),
        manager.create_task("task-5", "Add tests", "Write comprehensive tests", 5, TaskPriority.LOW)
    ]
    
    # Add dependencies
    manager.add_task_dependency("task-2", "task-1")
    manager.add_task_dependency("task-3", "task-2")
    manager.add_task_dependency("task-4", "task-3")
    
    # Update task statuses
    manager.update_task_status("task-1", TaskStatus.DONE, "developer-1")
    manager.update_task_status("task-2", TaskStatus.IN_PROGRESS, "developer-2")
    
    # Get ready tasks
    ready_tasks = manager.get_ready_tasks()
    print(f"Ready tasks: {[task.title for task in ready_tasks]}")
    
    # Get metrics
    metrics = manager.get_task_metrics()
    print(f"Task metrics: {metrics}")
    
    # Export data
    manager.export_tasks("tasks_export.json")

if __name__ == "__main__":
    main()
```

### GitHub Issues Integration
```python
# github_issues_integration.py
import requests
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

@dataclass
class GitHubIssue:
    number: int
    title: str
    body: str
    state: str
    assignee: Optional[str] = None
    labels: List[str] = None
    milestone: Optional[str] = None
    created_at: str = None
    updated_at: str = None

class GitHubIssuesIntegration:
    def __init__(self, token: str, owner: str, repo: str):
        self.token = token
        self.owner = owner
        self.repo = repo
        self.base_url = f"https://api.github.com/repos/{owner}/{repo}"
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
    
    def create_issue(self, title: str, body: str, labels: List[str] = None, 
                    assignee: str = None, milestone: int = None) -> Dict[str, Any]:
        """Create a new GitHub issue"""
        data = {
            "title": title,
            "body": body
        }
        
        if labels:
            data["labels"] = labels
        if assignee:
            data["assignee"] = assignee
        if milestone:
            data["milestone"] = milestone
        
        response = requests.post(
            f"{self.base_url}/issues",
            headers=self.headers,
            json=data
        )
        
        response.raise_for_status()
        return response.json()
    
    def update_issue(self, issue_number: int, **kwargs) -> Dict[str, Any]:
        """Update an existing GitHub issue"""
        response = requests.patch(
            f"{self.base_url}/issues/{issue_number}",
            headers=self.headers,
            json=kwargs
        )
        
        response.raise_for_status()
        return response.json()
    
    def get_issues(self, state: str = "open", labels: List[str] = None, 
                  assignee: str = None, milestone: int = None) -> List[Dict[str, Any]]:
        """Get GitHub issues with filters"""
        params = {"state": state}
        
        if labels:
            params["labels"] = ",".join(labels)
        if assignee:
            params["assignee"] = assignee
        if milestone:
            params["milestone"] = milestone
        
        response = requests.get(
            f"{self.base_url}/issues",
            headers=self.headers,
            params=params
        )
        
        response.raise_for_status()
        return response.json()
    
    def create_issue_template(self, template_name: str, template_content: str):
        """Create an issue template"""
        template_path = f".github/ISSUE_TEMPLATE/{template_name}.md"
        
        # This would typically be done through a git commit
        # For demonstration, we'll just return the template content
        return {
            "template_name": template_name,
            "template_path": template_path,
            "content": template_content
        }
    
    def sync_with_task_manager(self, task_manager):
        """Sync task manager data with GitHub issues"""
        synced_issues = []
        
        for task in task_manager.tasks.values():
            # Create or update issue for each task
            issue_data = {
                "title": task.title,
                "body": f"{task.description}\n\n**Story Points:** {task.story_points}\n**Priority:** {task.priority.name}\n**Status:** {task.status.value}",
                "labels": [task.status.value, f"priority-{task.priority.name.lower()}"]
            }
            
            if task.assignee:
                issue_data["assignee"] = task.assignee
            
            # Check if issue already exists (by title)
            existing_issues = self.get_issues()
            existing_issue = None
            
            for issue in existing_issues:
                if issue["title"] == task.title:
                    existing_issue = issue
                    break
            
            if existing_issue:
                # Update existing issue
                updated_issue = self.update_issue(existing_issue["number"], **issue_data)
                synced_issues.append(updated_issue)
            else:
                # Create new issue
                new_issue = self.create_issue(**issue_data)
                synced_issues.append(new_issue)
        
        return synced_issues

# Example issue templates
BUG_REPORT_TEMPLATE = """
## Bug Description
[Describe the bug clearly and concisely]

## Steps to Reproduce
1. [First step]
2. [Second step]
3. [And so on...]

## Expected Behavior
[What you expected to happen]

## Actual Behavior
[What actually happened]

## Environment
- OS: [e.g. Windows 10]
- Browser: [e.g. Chrome 91]
- Version: [e.g. 1.0.0]

## Additional Context
[Add any other context about the problem here]
"""

FEATURE_REQUEST_TEMPLATE = """
## Feature Description
[Describe the feature you'd like to see]

## Problem Statement
[Describe the problem this feature would solve]

## Proposed Solution
[Describe your proposed solution]

## Alternative Solutions
[Describe any alternative solutions you've considered]

## Additional Context
[Add any other context or screenshots about the feature request here]
"""

TASK_TEMPLATE = """
## Task Description
[Describe the task to be completed]

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

## Story Points
[Estimated story points]

## Priority
[High/Medium/Low]

## Dependencies
[List any dependencies]

## Additional Notes
[Any additional information]
"""
```

## Training Status: ✅ COMPLETED

- Enhanced agile task management with comprehensive backlog refinement
- Implemented project tracking with risk assessment and stakeholder management
- Designed automated workflows for task assignment and status tracking
- Updated `task-manager.mdc` with new responsibilities

## ✅ Role Alignment Summary
- My `.mdc` reflects my training: ✅ Yes
- Learned concepts directly enhance my duties: ✅ Yes
- Any scope updates applied: ✅ Yes (Enhanced with agile management, project tracking, workflow automation, performance monitoring, process improvement) 