# Cursor Rules & Coding Standards

## General Principles

### Code Organization
- Keep files under 500 lines
- Use clear, descriptive names
- Follow single responsibility principle
- Group related functionality in modules

### Documentation
- All public functions must have Google-style docstrings
- Include type hints for all function parameters and returns
- Document complex logic with inline comments
- Keep README and docs up to date

### Testing
- Write tests for all new functionality
- Include expected, edge, and failure cases
- Use pytest for testing framework
- Maintain test coverage above 80%

## Python Standards

### Imports
- Use absolute imports for external packages
- Use relative imports for internal modules
- Group imports: stdlib, third-party, local
- Alphabetize within groups

### Naming Conventions
- Classes: PascalCase (`PDFIngestion`)
- Functions/Variables: snake_case (`load_documents`)
- Constants: UPPER_SNAKE_CASE (`DEFAULT_PORT`)
- Private methods: leading underscore (`_setup_routes`)

### Type Hints
```python
from typing import List, Optional, Dict, Any

def process_documents(docs: List[str], config: Optional[Config] = None) -> Dict[str, Any]:
    """Process a list of documents."""
    pass
```

### Error Handling
- Use specific exception types
- Provide meaningful error messages
- Log errors appropriately
- Don't catch and ignore exceptions

## Project-Specific Rules

### Configuration
- Use centralized config management
- Support environment variable overrides
- Validate configuration on startup
- Provide sensible defaults

### CLI Commands
- Use Typer for CLI interface
- Provide helpful error messages
- Include usage examples
- Support both short and long options

### API Design
- Use consistent HTTP status codes
- Return JSON responses
- Include error details in responses
- Version APIs appropriately

### Database/Memory
- Use SQLAlchemy for ORM
- Implement proper connection management
- Handle migrations gracefully
- Support multiple backends

## File Structure

### Required Files
- `README.md` - Project overview and quick start
- `requirements.txt` - Pinned dependencies
- `pyproject.toml` - Project metadata and build config
- `CHANGELOG.md` - Version history
- `PLANNING.md` - Development roadmap

### Documentation
- `docs/usage.md` - User guide
- `docs/architecture.md` - System design
- `docs/configuration.md` - Config options
- `docs/deployment.md` - Deployment guide

### Testing
- `tests/` - All test files
- Mirror source structure in tests
- Use descriptive test names
- Include integration tests

## Quality Assurance

### Before Committing
- All tests pass
- No linting errors
- Documentation updated
- Version bumped if needed

### Code Review Checklist
- [ ] Follows naming conventions
- [ ] Includes proper docstrings
- [ ] Has appropriate tests
- [ ] Handles errors gracefully
- [ ] No security vulnerabilities
- [ ] Performance considerations

### Performance Guidelines
- Use async/await for I/O operations
- Implement proper caching
- Monitor memory usage
- Profile slow operations

## Security

### Input Validation
- Validate all user inputs
- Sanitize file paths
- Use parameterized queries
- Implement rate limiting

### Authentication/Authorization
- Use secure authentication methods
- Implement proper session management
- Validate permissions
- Log security events

### Data Protection
- Encrypt sensitive data
- Use secure communication protocols
- Implement proper backup procedures
- Follow data retention policies 