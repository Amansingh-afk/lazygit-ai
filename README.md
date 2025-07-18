# 🚀 lazygit-ai

> **AI-powered commit message generator that integrates seamlessly with LazyGit**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Transform your Git workflow with intelligent commit message generation. `lazygit-ai` combines rule-based analysis with optional AI enhancement to create meaningful, semantic commit messages that follow conventional commit standards.

## ✨ Features

### 🧠 Smart Commit Generation
- **Rule-based engine**: Analyzes git diff, branch names, and file types
- **AI fallback**: Optional LLM enhancement when rules aren't sufficient
- **Conventional commits**: Follows `<type>(<scope>): <description>` format
- **Offline-first**: Works without internet, AI enhancement optional

### 🎯 LazyGit Integration
- **Native feel**: Press `C` in LazyGit to generate commits
- **Auto-installation**: One command to set up LazyGit shortcuts
- **Beautiful UI**: Clean, professional terminal interface

### ✏️ Advanced Editing Experience
- **In-place editing**: Edit commit messages directly within the interface
- **Direct key press**: Instant response without pressing Enter
- **Pre-filled messages**: Start editing with AI-generated content
- **Keyboard shortcuts**: Quick actions with single key presses

### 🔧 Developer Experience
- **Zero configuration**: Works out of the box
- **Extensible**: Easy to add custom rules and LLM providers
- **Cross-platform**: Works on macOS, Linux, and Windows
- **Fallback support**: Graceful degradation when advanced features unavailable

## 🚀 Quick Start

### Installation

```bash
# Install from source (recommended for now)
git clone https://github.com/yourusername/lazygit-ai.git
cd lazygit-ai
pip install -e .

# Or install globally (when published)
pip install lazygit-ai
```

### Basic Usage

```bash
# Generate a commit message for staged changes
lazygit-ai commit

# Skip AI enhancement (rule-based only)
lazygit-ai commit --no-ai

# Install LazyGit integration (one-time setup)
lazygit-ai install-shortcut

# Show help and ASCII art
lazygit-ai help
```

### LazyGit Integration

After running `lazygit-ai install-shortcut`, you can:

1. Stage your changes in LazyGit
2. Press `C` in the Files context
3. Review and edit the generated commit message
4. Accept to commit or copy to clipboard

## 🎨 Demo

### Beautiful Interface with In-Place Editing
```
╭─────────────────────────────────────────────────────────────────────────────────── 🚀 lazygit-ai - Commit Message Editor ────────────────────────────────────────────────────────────────────────────────────╮
│                                                                                                                                                                                                              │
│  ╭─────────────────────────────────────────────────────────────────────────────────────── ✎ Edit commit message ───────────────────────────────────────────────────────────────────────────────────────╮  │
│  │                                                                                                                                                                                                        │  │
│  │  ✎ feat(cli): add in-place editor for commit messages                                                                                                                                                 │  │
│  │                                                                                                                                                                                                        │  │
│  ╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯  │
│  Branch: feature/inplace-editor                                                                                                                                                                             │
│  Files: 2                                                                                                                                                                                                   │
│  Changes: 2 files (new feature)                                                                                                                                                                             │
│                                                                                                                                                                                                              │
│  Press Enter to finish editing, a to accept, c to copy, q to quit                                                                                                                                          │
│                                                                                                                                                                                                              │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

### Key Features
- **Direct edit mode**: Opens immediately in editing mode - no need to press 'e'
- **Enter to finish**: Press Enter to complete editing and return to action menu
- **Quick actions**: Press 'a' to accept, 'c' to copy, 'q' to quit after editing
- **Pre-filled content**: Start with AI-generated commit messages
- **Keyboard navigation**: Use arrow keys, Home, End, Backspace during editing
- **Fallback support**: Works even when advanced terminal features unavailable

### Help Command
```
╭───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│                                                                                                                                             │
│ ██╗     █████╗ ███████╗██╗   ██╗ ██████╗ ██╗███████╗████████╗                                                                             │
│ ██║    ██╔══██╗╚══███╔╝╚██╗ ██╔╝██╔════╝ ██║██╔════╝╚══██╔══╝                                                                             │
│ ██║    ███████║  ███╔╝  ╚████╔╝ ██║  ███╗██║█████╗     ██║                                                                                │
│ ██║    ██╔══██║ ███╔╝    ╚██╔╝  ██║   ██║██║██╔══╝     ██║                                                                                │
│ ███████╗██║  ██║███████╗   ██║   ╚██████╔╝██║██║        ██║                                                                                │
│ ╚══════╝╚═╝  ╚═╝╚══════╝   ╚═╝    ╚═════╝ ╚═╝╚═╝        ╚═╝                                                                                │
│                                                                                                                                             │
│ AI-powered commit message generator for LazyGit                                                                                             │
│                                                                                                                                             │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

## 🏗️ Architecture

### Core Components

```
lazygit_ai/
├── cli.py              # Main CLI entry point
├── core/
│   ├── analyzer.py     # Git diff and branch analysis
│   ├── rules.py        # Rule-based commit generation
│   └── llm.py          # AI integration layer
├── ui/
│   ├── tui.py          # Beautiful terminal UI with in-place editing
│   └── display.py      # Rich terminal output
├── utils/
│   ├── git.py          # Git wrapper utilities
│   ├── config.py       # Configuration management
│   └── shortcuts.py    # LazyGit integration
└── tests/              # Test suite
```

### Rule-Based Engine

The rule-based engine analyzes:

1. **Branch names**: `feat/login-ui` → `feat(login-ui)`
2. **File types**: `.test.js` → `test`, `.md` → `docs`
3. **Code comments**: `// TODO:`, `# FIX:`, `/* BUG: */`
4. **Git diff patterns**: Added/deleted lines, function changes

### AI Enhancement

When rules produce generic results, the AI fallback:

1. Formats git diff into a clean prompt
2. Sends to configured LLM (OpenAI, Claude, or local)
3. Merges rule insights with AI suggestions
4. Returns enhanced commit message

### Advanced UX Implementation

The in-place editor provides a seamless editing experience:

1. **Direct Key Press Detection**: Uses the `keyboard` library for instant response
2. **Fallback Mechanisms**: Gracefully degrades to traditional input when needed
3. **Cursor Positioning**: ANSI escape codes for precise cursor control
4. **Real-time Updates**: Live text editing with immediate visual feedback
5. **Cross-platform Support**: Works on Windows, macOS, and Linux

#### Technical Features
- **Threaded Input**: Non-blocking key press detection
- **Terminal Raw Mode**: Direct character input without line buffering
- **ANSI Escape Sequences**: Precise cursor positioning and line clearing
- **Error Handling**: Robust fallback to traditional input methods
- **Test Compatibility**: Works seamlessly in automated testing environments

## ⚙️ Configuration

### Environment Variables

```bash
# OpenAI (optional)
OPENAI_API_KEY=your_openai_key

# Anthropic (optional)
ANTHROPIC_API_KEY=your_anthropic_key

# Local LLM (optional)
OLLAMA_BASE_URL=http://localhost:11434
```

### Config File

Create `~/.config/lazygit-ai/config.toml`:

```toml
[ai]
provider = "openai"  # openai, anthropic, ollama, or none
model = "gpt-4"      # Model name for the provider
temperature = 0.3    # Creativity level (0.0-1.0)

[commit]
conventional = true   # Use conventional commit format
max_length = 72      # Maximum commit message length
scope_style = "lowercase"  # lowercase, kebab-case, camelCase

[rules]
enable_todos = true   # Parse TODO comments
enable_fixes = true   # Parse FIX comments
branch_analysis = true # Use branch name for context
```

## 🛠️ Development

### Setup

```bash
git clone https://github.com/yourusername/lazygit-ai.git
cd lazygit-ai
pip install -e ".[dev]"
pre-commit install
```

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=lazygit_ai

# Run specific test categories
pytest tests/test_core/     # Core functionality tests
pytest tests/test_ui/       # UI component tests
pytest tests/test_utils/    # Utility function tests
```

### Code Quality

```bash
# Format code
black lazygit_ai tests
isort lazygit_ai tests

# Lint code
flake8 lazygit_ai tests
mypy lazygit_ai

# Run all quality checks
pre-commit run --all-files
```

## 🎨 UI Features

### Clean Design
- **Boxed interface**: Everything wrapped in a beautiful blue border
- **Color-coded elements**: Cyan for commit messages, yellow for info, dimmed shortcuts
- **Professional layout**: Clean spacing and typography
- **Terminal clearing**: Clean slate on every action

### Interactive Actions
- **Direct key press**: Press keys directly without Enter - instant response
- **Accept**: Press `a` to create commit with suggested message
- **Edit**: Press `e` to modify the commit message inline
- **Copy**: Press `c` to copy message to clipboard
- **Quit**: Press `q` to exit without committing

### Smart Defaults
- **Responsive interface**: No need to press Enter after actions
- **Keyboard shortcuts**: Simple a/e/c/q mappings for quick access
- **Context awareness**: Shows branch, files, and changes
- **Fallback support**: Gracefully falls back to traditional input if needed

## 🧹 Codebase Quality

### Clean Architecture
- **Minimal dependencies**: Only essential imports and libraries
- **No debugging code**: Production-ready without debug prints or test artifacts
- **Optimized imports**: Removed unused imports and redundant code
- **Clean error handling**: Proper error management without verbose logging
- **Streamlined UI**: Simplified interface code with essential functionality only

### Performance Optimizations
- **Efficient Git operations**: Optimized Git wrapper for faster analysis
- **Smart caching**: Configurable caching for repeated operations
- **Memory efficient**: Minimal memory footprint for large repositories
- **Fast startup**: Quick initialization and response times

### Code Standards
- **Type hints**: Full type annotation coverage
- **Docstrings**: Comprehensive documentation for all public APIs
- **Error handling**: Robust exception handling with graceful fallbacks
- **Cross-platform**: Works consistently across Windows, macOS, and Linux

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Workflow

1. Fork the repository
2. Create a feature branch: `git checkout -b feat/amazing-feature`
3. Make your changes and add tests
4. Run the test suite: `pytest`
5. Commit your changes: `git commit -m 'feat: add amazing feature'`
6. Push to the branch: `git push origin feat/amazing-feature`
7. Open a Pull Request

## 📋 Roadmap

- [x] **Phase 1**: Rule-based commit generation ✅
- [x] **Phase 2**: LLM fallback integration ✅
- [x] **Phase 3**: LazyGit shortcut integration ✅
- [x] **Phase 4**: Advanced UX and polishing ✅
- [ ] **Phase 5**: PR description generation
- [ ] **Phase 6**: Changelog generation
- [ ] **Phase 7**: Merge conflict explanation

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [LazyGit](https://github.com/jesseduffield/lazygit) for the amazing Git TUI
- [Conventional Commits](https://www.conventionalcommits.org/) for the commit format standard
- [Rich](https://rich.readthedocs.io/) for the beautiful terminal UI framework

---

**Made with ❤️ for the developer community**

If you find this tool helpful, please give it a ⭐ on GitHub!
