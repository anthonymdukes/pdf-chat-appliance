# PDF Chat Appliance - Project Tools Documentation

## Overview

This document catalogs all tools, linters, formatters, and utilities used in the PDF Chat Appliance project. It serves as a reference for developers and agents to understand the tooling stack, versions, and usage patterns.

## Tool Categories

### Code Quality & Linting

#### Python Tools

| Tool | Version | Purpose | Usage | Status |
|------|---------|---------|-------|--------|
| **Black** | 25.1.0 | Code formatting (PEP 8 compliant) | `python -m black .` | Active |
| **Ruff** | 0.12.2 | Fast Python linter/formatter | `python -m ruff check . --fix` | Active |
| **Flake8** | 7.3.0 | Style guide enforcement | `python -m flake8 .` | Active |
| **MyPy** | 1.16.1 | Static type checking | `python -m mypy .` | Active |
| **isort** | 6.0.1 | Import sorting | `python -m isort .` | Active |

#### Markdown Tools

| Tool | Version | Purpose | Usage | Status |
|------|---------|---------|-------|--------|
| **markdownlint** | Latest | Markdown linting | `markdownlint . --fix` | Active |

#### YAML Tools

| Tool | Version | Purpose | Usage | Status |
|------|---------|---------|-------|--------|
| **yamllint** | 1.37.1 | YAML validation | `python -m yamllint .` | Active |

#### PowerShell Tools

| Tool | Version | Purpose | Usage | Status |
|------|---------|---------|-------|--------|
| **PSScriptAnalyzer** | 1.24.0 | PowerShell linting | `Invoke-ScriptAnalyzer -Path .` | Active |

### Container & Deployment

| Tool | Version | Purpose | Usage | Status |
|------|---------|---------|-------|--------|
| **Docker** | 28.3.0 | Containerization | `docker --version` | Active |
| **Docker Compose** | v2.38.1 | Multi-container orchestration | `docker-compose --version` | Active |

### Package Management

| Tool | Version | Purpose | Usage | Status |
|------|---------|---------|-------|--------|
| **pip** | 25.1.1 | Python package manager | `pip install <package>` | Active |

### Development & Debugging

| Tool | Version | Purpose | Usage | Status |
|------|---------|---------|-------|--------|
| **psutil** | 7.0.0 | System monitoring | Import in Python | Active |
| **PyMuPDF** | 1.26.3 | PDF processing | Import in Python | Active |
| **PyYAML** | 6.0.2 | YAML processing | Import in Python | Active |

## Configuration Files

### Python Configuration (`pyproject.toml`)

```toml
[tool.black]
line-length = 88
target-version = ['py38', 'py39', 'py310', 'py311', 'py312']

[tool.isort]
profile = "black"
line_length = 88
known_first_party = ["pdfchat", "memory", "tests"]

[tool.flake8]
max-line-length = 88
extend-ignore = ["E203", "W503", "E501"]

[tool.ruff]
target-version = "py38"
line-length = 88
select = ["E", "W", "F", "I", "B", "C4", "UP"]
```

### YAML Configuration (`.yamllint`)

```yaml
extends: default

rules:
  line-length: disable
  truthy:
    check-keys: false
  document-end: disable
  empty-lines:
    max: 2
    max-end: 1
```

### Pre-commit Configuration (`.pre-commit-config.yaml`)

Automated checks run on commit:

- Black formatting
- isort import sorting
- Flake8 linting
- Ruff linting/fixing
- MyPy type checking
- YAML validation
- Markdown linting
- PowerShell linting

## Installation Instructions

### For New Team Members

1. **Python Environment Setup:**

   ```bash
   python -m pip install -e ".[dev]"
   ```

2. **PowerShell Tools:**

   ```powershell
   Install-Module -Name PSScriptAnalyzer -Force
   ```

3. **Markdown Linting:**

   ```bash
   npm install -g markdownlint-cli
   ```

4. **Docker:**
   - Install Docker Desktop for Windows
   - Verify with `docker --version`

## Workflow Integration

### Pre-commit Hooks

All tools are integrated into pre-commit hooks for automated quality checks:

```bash
# Install pre-commit hooks
pre-commit install

# Run all hooks manually
pre-commit run --all-files
```

### CI/CD Integration

Tools are configured to run in CI/CD pipelines:

- Code formatting (Black)
- Linting (Ruff, Flake8)
- Type checking (MyPy)
- Documentation validation (markdownlint)

## Current Compliance Status

### Fully Compliant

- **Black:** All Python files formatted
- **isort:** All imports sorted
- **PSScriptAnalyzer:** All PowerShell scripts compliant

### Partially Compliant

- **Ruff:** 102 issues remaining (mostly in legacy files)
- **Flake8:** Some issues in legacy microservices
- **MyPy:** Type checking issues in some modules
- **markdownlint:** Line length and heading issues

### Needs Configuration

- **yamllint:** Configuration parsing issues

## Tool Recommendations

### Recommended Additions

1. **Performance Profiling:**
   - `cProfile` for Python performance analysis
   - `memory_profiler` for memory usage tracking

2. **Security Scanning:**
   - `bandit` for security vulnerability scanning
   - `safety` for dependency vulnerability checking

3. **Documentation:**
   - `pydocstyle` for docstring style checking
   - `sphinx` for documentation generation

4. **Testing:**
   - `pytest-cov` for coverage reporting
   - `pytest-mock` for mocking utilities

### Optimization Opportunities

1. **Replace Flake8 with Ruff:** Ruff is significantly faster and can replace most Flake8 functionality
2. **Add pre-commit hooks:** Automate all quality checks
3. **Implement type checking:** Gradually add type hints and MyPy compliance
4. **Add security scanning:** Integrate security tools into CI/CD

## Maintenance Schedule

### Weekly

- Check for tool updates
- Review compliance reports
- Update documentation

### Monthly

- Evaluate new tools
- Review performance metrics
- Update tool configurations

### Quarterly

- Major tool version updates
- Workflow optimization review
- Team training on new tools

## Troubleshooting

### Common Issues

1. **YAML Linting Errors:**
   - Check `.yamllint` configuration
   - Verify YAML syntax

2. **Import Sorting Issues:**
   - Run `python -m isort . --diff` to see changes
   - Update `pyproject.toml` configuration

3. **Type Checking Errors:**
   - Add type hints gradually
   - Use `# type: ignore` for problematic imports

4. **PowerShell Linting:**
   - Use approved verbs in function names
   - Follow PowerShell best practices

## Version History

### 2025-07-03

- Added comprehensive tooling stack
- Implemented Black, Ruff, isort, Flake8, MyPy
- Added markdownlint and PSScriptAnalyzer
- Created pre-commit configuration
- Established compliance baseline

---

**Last Updated:** 2025-07-03  
**Maintained By:** System Architect & Docs Maintainer  
**Next Review:** 2025-07-10
