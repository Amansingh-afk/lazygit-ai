# Contributing to lazygit-ai

Thank you for your interest in contributing to lazygit-ai! This document provides guidelines and information for contributors.

## 🚀 Quick Start

1. **Fork** the repository
2. **Clone** your fork: `git clone https://github.com/yourusername/lazygit-ai.git`
3. **Install** in development mode: `pip install -e ".[dev]"`
4. **Create** a feature branch: `git checkout -b feat/amazing-feature`
5. **Make** your changes and add tests
6. **Run** tests: `pytest`
7. **Commit** your changes: `git commit -m 'feat: add amazing feature'`
8. **Push** to your branch: `git push origin feat/amazing-feature`
9. **Open** a Pull Request

## 🛠️ Development Setup

### Prerequisites

- Python 3.8 or higher
- Git
- LazyGit (for testing integration)

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/lazygit-ai.git
cd lazygit-ai

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=lazygit_ai

# Run specific test file
pytest tests/test_rules.py

# Run with verbose output
pytest -v
```

### Code Quality

```bash
# Format code
black lazygit_ai tests

# Sort imports
isort lazygit_ai tests

# Lint code
flake8 lazygit_ai tests

# Type checking
mypy lazygit_ai
```

## 📋 Development Guidelines

### Code Style

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guidelines
- Use [Black](https://black.readthedocs.io/) for code formatting
- Use [isort](https://pycqa.github.io/isort/) for import sorting
- Use [flake8](https://flake8.pycqa.org/) for linting
- Use [mypy](https://mypy.readthedocs.io/) for type checking

### Commit Messages

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

Types:
- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation only changes
- `style`: Changes that do not affect the meaning of the code
- `refactor`: A code change that neither fixes a bug nor adds a feature
- `perf`: A code change that improves performance
- `test`: Adding missing tests or correcting existing tests
- `chore`: Changes to the build process or auxiliary tools

### Testing

- Write tests for all new features and bug fixes
- Maintain test coverage above 80%
- Use descriptive test names
- Test both success and failure cases
- Mock external dependencies

### Documentation

- Add docstrings to all public functions and classes
- Update README.md for user-facing changes
- Update inline comments for complex logic
- Keep documentation up to date with code changes

## 🏗️ Project Structure

```
lazygit_ai/
├── cli.py              # Main CLI entry point
├── core/               # Core functionality
│   ├── analyzer.py     # Git analysis
│   ├── rules.py        # Rule-based commit generation
│   └── llm.py          # AI integration
├── ui/                 # User interface
│   ├── display.py      # Rich terminal output
│   └── tui.py          # Textual-based TUI
├── utils/              # Utilities
│   ├── config.py       # Configuration management
│   ├── git.py          # Git wrapper
│   └── shortcuts.py    # LazyGit integration
└── tests/              # Test suite
    ├── test_analyzer.py
    ├── test_rules.py
    ├── test_llm.py
    └── test_ui.py
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest

# Run specific test category
pytest tests/test_core/
pytest tests/test_ui/

# Run with coverage
pytest --cov=lazygit_ai --cov-report=html

# Run integration tests
pytest tests/test_integration/
```

### Writing Tests

- Use descriptive test names
- Test both success and failure cases
- Mock external dependencies
- Use fixtures for common setup
- Test edge cases and error conditions

Example test structure:

```python
import pytest
from lazygit_ai.core.rules import RuleEngine
from lazygit_ai.utils.config import ConfigManager

class TestRuleEngine:
    def test_generate_message_with_todo(self):
        """Test commit message generation with TODO comment."""
        config = ConfigManager()
        engine = RuleEngine(config)
        # Test implementation...
    
    def test_generate_message_without_changes(self):
        """Test commit message generation with no staged changes."""
        # Test implementation...
```

## 🐛 Bug Reports

When reporting bugs, please include:

1. **Description** of the bug
2. **Steps** to reproduce
3. **Expected** behavior
4. **Actual** behavior
5. **Environment** details (OS, Python version, etc.)
6. **Error** messages or logs
7. **Screenshots** if applicable

## 💡 Feature Requests

When requesting features, please include:

1. **Description** of the feature
2. **Use case** and motivation
3. **Proposed** implementation approach
4. **Alternatives** considered
5. **Impact** on existing functionality

## 🔄 Pull Request Process

1. **Fork** the repository
2. **Create** a feature branch
3. **Make** your changes
4. **Add** tests for new functionality
5. **Update** documentation
6. **Run** the test suite
7. **Ensure** code quality checks pass
8. **Commit** with conventional commit messages
9. **Push** to your fork
10. **Open** a Pull Request

### Pull Request Guidelines

- Provide a clear description of changes
- Include tests for new functionality
- Update documentation if needed
- Ensure all CI checks pass
- Respond to review comments promptly
- Keep commits atomic and focused

## 📝 Documentation

### Code Documentation

- Use Google-style docstrings
- Document all public functions and classes
- Include type hints
- Provide usage examples

Example:

```python
def generate_commit_message(analysis: GitAnalysis) -> str:
    """Generate a commit message based on git analysis.
    
    Args:
        analysis: Git analysis results containing staged files, diff, etc.
        
    Returns:
        A formatted commit message following conventional commit standards.
        
    Raises:
        ValueError: If no staged files are found.
        
    Example:
        >>> analysis = GitAnalyzer(git_wrapper).analyze()
        >>> message = generate_commit_message(analysis)
        >>> print(message)
        'feat(auth): add login form validation'
    """
    # Implementation...
```

### User Documentation

- Keep README.md up to date
- Provide clear installation instructions
- Include usage examples
- Document configuration options
- Add troubleshooting section

## 🚀 Release Process

### Versioning

We use [Semantic Versioning](https://semver.org/):

- **MAJOR**: Incompatible API changes
- **MINOR**: New functionality in a backward-compatible manner
- **PATCH**: Backward-compatible bug fixes

### Release Steps

1. **Update** version in `pyproject.toml`
2. **Update** `__version__` in `lazygit_ai/__init__.py`
3. **Update** CHANGELOG.md
4. **Create** release branch
5. **Run** full test suite
6. **Create** GitHub release
7. **Publish** to PyPI

## 🤝 Community

### Getting Help

- **Issues**: Use GitHub Issues for bug reports and feature requests
- **Discussions**: Use GitHub Discussions for questions and ideas
- **Code of Conduct**: Be respectful and inclusive

### Communication

- Be respectful and inclusive
- Use clear and concise language
- Provide context for questions
- Help others when possible

## 📄 License

By contributing to lazygit-ai, you agree that your contributions will be licensed under the MIT License.

## 🙏 Acknowledgments

Thank you to all contributors who help make lazygit-ai better!

---

**Happy coding! 🚀** 