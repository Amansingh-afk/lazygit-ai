"""
Configuration management for lazygit-ai.

Handles user preferences, AI provider settings, and commit message formatting.
"""

import os
import subprocess
from pathlib import Path
from typing import Any, Dict, Optional

import toml
from rich.console import Console


class ConfigManager:
    """Manages lazygit-ai configuration."""
    
    def __init__(self) -> None:
        """Initialize configuration manager."""
        self.config_dir = Path.home() / ".config" / "lazygit-ai"
        self.config_file = self.config_dir / "config.toml"
        self._config: Optional[Dict[str, Any]] = None
        
        # Ensure config directory exists
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Load or create default config
        self._load_config()
    
    def _load_config(self) -> None:
        """Load configuration from file or create default."""
        if self.config_file.exists():
            try:
                with open(self.config_file, "r") as f:
                    self._config = toml.load(f)
            except Exception:
                self._config = self._get_default_config()
        else:
            self._config = self._get_default_config()
            self._save_config()
    
    def _save_config(self) -> None:
        """Save configuration to file."""
        try:
            with open(self.config_file, "w") as f:
                toml.dump(self._config, f)
        except Exception as e:
            raise RuntimeError(f"Failed to save configuration: {e}")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            "ai": {
                "provider": "none",  # openai, anthropic, ollama, none
                "model": "gpt-4",    # Model name for the provider
                "temperature": 0.3,  # Creativity level (0.0-1.0)
                "max_tokens": 150,   # Maximum tokens for AI response
                "timeout": 30,       # Timeout in seconds
            },
            "commit": {
                "conventional": True,     # Use conventional commit format
                "max_length": 72,        # Maximum commit message length
                "scope_style": "lowercase",  # lowercase, kebab-case, camelCase
                "include_scope": True,   # Include scope in commit messages
                "auto_scope": True,      # Auto-detect scope from files/branch
            },
            "rules": {
                "enable_todos": True,     # Parse TODO comments
                "enable_fixes": True,     # Parse FIX comments
                "enable_bugs": True,      # Parse BUG comments
                "branch_analysis": True,  # Use branch name for context
                "file_type_analysis": True,  # Analyze file types
                "diff_analysis": True,    # Analyze git diff patterns
            },
            "ui": {
                "show_banner": True,      # Show ASCII banner
                "colors": True,           # Enable colored output
                "interactive": True,      # Use interactive TUI
                "copy_to_clipboard": True,  # Copy commit message to clipboard
            },
            "lazygit": {
                "auto_install": True,     # Auto-install shortcuts
                "default_key": "C",       # Default key binding
                "default_context": "files",  # Default context
            },
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation."""
        keys = key.split(".")
        value = self._config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value using dot notation."""
        keys = key.split(".")
        config = self._config
        
        # Navigate to the parent of the target key
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # Set the value
        config[keys[-1]] = value
        self._save_config()
    
    def ai_enabled(self) -> bool:
        """Check if AI enhancement is enabled."""
        provider = self.get("ai.provider", "none")
        return provider != "none"
    
    def get_ai_config(self) -> Dict[str, Any]:
        """Get AI configuration."""
        return {
            "provider": self.get("ai.provider", "none"),
            "model": self.get("ai.model", "gpt-4"),
            "temperature": self.get("ai.temperature", 0.3),
            "max_tokens": self.get("ai.max_tokens", 150),
            "timeout": self.get("ai.timeout", 30),
        }
    
    def get_commit_config(self) -> Dict[str, Any]:
        """Get commit message configuration."""
        return {
            "conventional": self.get("commit.conventional", True),
            "max_length": self.get("commit.max_length", 72),
            "scope_style": self.get("commit.scope_style", "lowercase"),
            "include_scope": self.get("commit.include_scope", True),
            "auto_scope": self.get("commit.auto_scope", True),
        }
    
    def get_rules_config(self) -> Dict[str, Any]:
        """Get rules configuration."""
        return {
            "enable_todos": self.get("rules.enable_todos", True),
            "enable_fixes": self.get("rules.enable_fixes", True),
            "enable_bugs": self.get("rules.enable_bugs", True),
            "branch_analysis": self.get("rules.branch_analysis", True),
            "file_type_analysis": self.get("rules.file_type_analysis", True),
            "diff_analysis": self.get("rules.diff_analysis", True),
        }
    
    def get_ui_config(self) -> Dict[str, Any]:
        """Get UI configuration."""
        return {
            "show_banner": self.get("ui.show_banner", True),
            "colors": self.get("ui.colors", True),
            "interactive": self.get("ui.interactive", True),
            "copy_to_clipboard": self.get("ui.copy_to_clipboard", True),
        }
    
    def get_lazygit_config(self) -> Dict[str, Any]:
        """Get LazyGit integration configuration."""
        return {
            "auto_install": self.get("lazygit.auto_install", True),
            "default_key": self.get("lazygit.default_key", "C"),
            "default_context": self.get("lazygit.default_context", "files"),
        }
    
    def show_config(self, console: Console) -> None:
        """Display current configuration."""
        console.print("[blue]📋 Current Configuration[/blue]")
        console.print()
        
        # AI Configuration
        ai_config = self.get_ai_config()
        console.print("[bold]🤖 AI Settings:[/bold]")
        console.print(f"  Provider: {ai_config['provider']}")
        console.print(f"  Model: {ai_config['model']}")
        console.print(f"  Temperature: {ai_config['temperature']}")
        console.print(f"  Max Tokens: {ai_config['max_tokens']}")
        console.print(f"  Timeout: {ai_config['timeout']}s")
        console.print()
        
        # Commit Configuration
        commit_config = self.get_commit_config()
        console.print("[bold]📝 Commit Settings:[/bold]")
        console.print(f"  Conventional: {commit_config['conventional']}")
        console.print(f"  Max Length: {commit_config['max_length']}")
        console.print(f"  Scope Style: {commit_config['scope_style']}")
        console.print(f"  Include Scope: {commit_config['include_scope']}")
        console.print(f"  Auto Scope: {commit_config['auto_scope']}")
        console.print()
        
        # Rules Configuration
        rules_config = self.get_rules_config()
        console.print("[bold]🔍 Rules Settings:[/bold]")
        console.print(f"  Enable TODOs: {rules_config['enable_todos']}")
        console.print(f"  Enable Fixes: {rules_config['enable_fixes']}")
        console.print(f"  Enable Bugs: {rules_config['enable_bugs']}")
        console.print(f"  Branch Analysis: {rules_config['branch_analysis']}")
        console.print(f"  File Type Analysis: {rules_config['file_type_analysis']}")
        console.print(f"  Diff Analysis: {rules_config['diff_analysis']}")
        console.print()
        
        # UI Configuration
        ui_config = self.get_ui_config()
        console.print("[bold]🖥️  UI Settings:[/bold]")
        console.print(f"  Show Banner: {ui_config['show_banner']}")
        console.print(f"  Colors: {ui_config['colors']}")
        console.print(f"  Interactive: {ui_config['interactive']}")
        console.print(f"  Copy to Clipboard: {ui_config['copy_to_clipboard']}")
        console.print()
        
        # LazyGit Configuration
        lazygit_config = self.get_lazygit_config()
        console.print("[bold]🎯 LazyGit Settings:[/bold]")
        console.print(f"  Auto Install: {lazygit_config['auto_install']}")
        console.print(f"  Default Key: {lazygit_config['default_key']}")
        console.print(f"  Default Context: {lazygit_config['default_context']}")
        console.print()
        
        console.print(f"[dim]Config file: {self.config_file}[/dim]")
    
    def edit_config(self, console: Console) -> None:
        """Open configuration file in default editor."""
        console.print(f"[blue]📝 Opening config file in editor...[/blue]")
        console.print(f"File: {self.config_file}")
        console.print()
        
        # Try to open with default editor
        editor = os.environ.get("EDITOR")
        if not editor:
            # Try common editors
            for ed in ["nano", "vim", "code", "notepad"]:
                try:
                    subprocess.run([ed, "--version"], capture_output=True, check=True)
                    editor = ed
                    break
                except (subprocess.CalledProcessError, FileNotFoundError):
                    continue
        
        if editor:
            try:
                subprocess.run([editor, str(self.config_file)], check=True)
                console.print("[green]✅ Config file opened successfully![/green]")
                console.print("[dim]Save the file and restart lazygit-ai for changes to take effect.[/dim]")
            except subprocess.CalledProcessError:
                console.print(f"[red]❌ Failed to open editor: {editor}[/red]")
                console.print(f"[dim]Please manually edit: {self.config_file}[/dim]")
        else:
            console.print("[yellow]⚠️  No editor found[/yellow]")
            console.print(f"[dim]Please manually edit: {self.config_file}[/dim]")
    
    def reset_config(self, console: Console) -> None:
        """Reset configuration to defaults."""
        console.print("[yellow]⚠️  This will reset all configuration to defaults![/yellow]")
        console.print("Are you sure? (y/N): ", end="")
        
        try:
            response = input().strip().lower()
            if response in ["y", "yes"]:
                self._config = self._get_default_config()
                self._save_config()
                console.print("[green]✅ Configuration reset to defaults![/green]")
            else:
                console.print("[blue]Reset cancelled.[/blue]")
        except KeyboardInterrupt:
            console.print("\n[blue]Reset cancelled.[/blue]")
    
    def validate_config(self) -> bool:
        """Validate configuration values."""
        try:
            # Validate AI settings
            ai_config = self.get_ai_config()
            if ai_config["temperature"] < 0 or ai_config["temperature"] > 1:
                return False
            
            if ai_config["max_tokens"] < 1:
                return False
            
            if ai_config["timeout"] < 1:
                return False
            
            # Validate commit settings
            commit_config = self.get_commit_config()
            if commit_config["max_length"] < 10:
                return False
            
            if commit_config["scope_style"] not in ["lowercase", "kebab-case", "camelCase"]:
                return False
            
            return True
        except Exception:
            return False
    
    def get_env_overrides(self) -> Dict[str, Any]:
        """Get configuration overrides from environment variables."""
        overrides = {}
        
        # AI provider overrides
        if os.environ.get("LAZYGIT_AI_PROVIDER"):
            overrides["ai.provider"] = os.environ["LAZYGIT_AI_PROVIDER"]
        
        if os.environ.get("LAZYGIT_AI_MODEL"):
            overrides["ai.model"] = os.environ["LAZYGIT_AI_MODEL"]
        
        if os.environ.get("LAZYGIT_AI_TEMPERATURE"):
            try:
                overrides["ai.temperature"] = float(os.environ["LAZYGIT_AI_TEMPERATURE"])
            except ValueError:
                pass
        
        # Commit message overrides
        if os.environ.get("LAZYGIT_AI_MAX_LENGTH"):
            try:
                overrides["commit.max_length"] = int(os.environ["LAZYGIT_AI_MAX_LENGTH"])
            except ValueError:
                pass
        
        # Apply overrides
        for key, value in overrides.items():
            self.set(key, value)
        
        return overrides 