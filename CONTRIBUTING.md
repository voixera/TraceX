# Contributing to TraceX

Thank you for your interest in contributing to TraceX!

## Code of Conduct

By participating, you agree to maintain a respectful and inclusive environment for everyone.

## Getting Started

### Prerequisites

- Python 3.12+
- PostgreSQL 16+
- Redis 7+
- Node.js 20+ (for web dashboard)

### Development Setup

1. Fork and clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```
3. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```
4. Set up pre-commit hooks:
   ```bash
   pre-commit install
   ```
5. Copy environment file:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=packages --cov-report=html

# Run specific test file
pytest tests/unit/test_collectors.py

# Run integration tests (requires Docker)
pytest tests/integration
```

### Code Quality

We enforce code quality through:

- **Ruff**: Fast Python linter
- **MyPy**: Static type checker
- **Pre-commit**: Automated checks

Run manually:
```bash
# Lint
ruff check .

# Type check
mypy packages/

# Format
ruff format .
```

## Project Structure

```
tracex/
├── apps/           # Application entry points
│   ├── api/        # FastAPI REST API
│   ├── bot/        # Telegram bot
│   ├── cli/        # Command-line interface
│   └── web/        # Next.js dashboard
├── packages/       # Core packages
│   ├── common/     # Shared utilities
│   ├── collectors/ # OSINT collectors
│   ├── core/       # Intelligence engine
│   ├── database/   # Database models
│   └── models/     # Pydantic schemas
├── plugins/        # Community plugins
├── tests/          # Test suites
└── docs/           # Documentation
```

## Making Changes

1. Create a branch from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes, following our coding standards:
   - Use type hints
   - Add docstrings to public functions
   - Keep functions small and focused
   - Write tests for new functionality

3. Commit with clear messages:
   ```
   feat(collectors): add Shodan API collector

   - Add Shodan collector for IP intelligence
   - Include rate limiting configuration
   - Add unit tests
   ```

4. Push and create a Pull Request

## Pull Request Guidelines

- Fill out the PR template completely
- Reference any related issues
- Ensure all tests pass
- Update documentation if needed
- Keep PRs focused on single concerns

## Adding Collectors

Create a new collector in `packages/collectors/`:

```python
# packages/collectors/mysource.py
from packages.collectors.base import BaseCollector
from packages.models.schemas import TargetType

class MySourceCollector(BaseCollector):
    name = "mysource"
    description = "My data source collector"
    target_types = [TargetType.DOMAIN]

    async def _collect_impl(self, context):
        # Your collection logic here
        return {
            "entities": [...],
            "relationships": [...],
            "evidence": [...],
            "errors": []
        }
```

## Reporting Issues

When reporting bugs:
- Use the Bug Report template
- Include OS/environment details
- Provide minimal reproduction steps
- Include relevant logs (no sensitive data)

When requesting features:
- Use the Feature Request template
- Explain the use case
- Describe expected behavior
- Consider backwards compatibility

## Questions?

- GitHub Discussions: For questions about using TraceX
- Discord: For real-time community chat
- Issues: For bug reports and feature requests

Thank you for making TraceX better! 🎉
