"""
LazyGit shortcut management for lazygit-ai.

Handles installation and management of custom commands in LazyGit configuration.
"""

import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Optional

import yaml


class LazyGitShortcutManager:
    """Manages LazyGit shortcuts for lazygit-ai."""
    
    def __init__(self) -> None:
        """Initialize shortcut manager."""
        self.config_dir = Path.home() / ".config" / "lazygit"
        self.config_file = self.config_dir / "config.yml"
        self._config: Optional[Dict] = None
    
    def is_lazygit_installed(self) -> bool:
        """Check if LazyGit is installed and accessible."""
        return shutil.which("lazygit") is not None
    
    def _load_config(self) -> Dict:
        """Load LazyGit configuration."""
        if self._config is not None:
            return self._config
        
        if not self.config_file.exists():
            self._config = self._get_default_config()
            self._save_config()
        else:
            try:
                with open(self.config_file, "r") as f:
                    self._config = yaml.safe_load(f) or {}
            except Exception:
                self._config = self._get_default_config()
        
        return self._config
    
    def _save_config(self) -> None:
        """Save LazyGit configuration."""
        # Ensure config directory exists
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(self.config_file, "w") as f:
                yaml.dump(self._config, f, default_flow_style=False, sort_keys=False)
        except Exception as e:
            raise RuntimeError(f"Failed to save LazyGit configuration: {e}")
    
    def _get_default_config(self) -> Dict:
        """Get default LazyGit configuration."""
        return {
            "gui": {
                "showBottomLine": False,
                "mouseEvents": True,
            },
            "git": {
                "paging": {
                    "colorArg": "always",
                    "useConfig": False,
                },
            },
            "customCommands": [],
        }
    
    def _ensure_custom_commands_section(self) -> None:
        """Ensure customCommands section exists in config."""
        if "customCommands" not in self._config:
            self._config["customCommands"] = []
    
    def get_shortcut_command(self, key: str, context: str) -> Optional[Dict]:
        """Get existing shortcut command for key and context."""
        self._load_config()
        self._ensure_custom_commands_section()
        
        for command in self._config["customCommands"]:
            if command.get("key") == key and command.get("context") == context:
                return command
        
        return None
    
    def install_shortcut(self, key: str, context: str, force: bool = False) -> bool:
        """
        Install LazyGit shortcut for lazygit-ai.
        
        Args:
            key: Key binding (e.g., "C")
            context: LazyGit context (e.g., "files")
            force: Overwrite existing shortcut
            
        Returns:
            True if successful, False if shortcut already exists
        """
        self._load_config()
        self._ensure_custom_commands_section()
        
        # Check if shortcut already exists
        existing = self.get_shortcut_command(key, context)
        if existing and not force:
            return False
        
        # Remove existing shortcut if force is True
        if existing and force:
            self._config["customCommands"].remove(existing)
        
        # Create new shortcut
        shortcut = {
            "key": key,
            "context": context,
            "command": "lazygit-ai commit",
            "description": "AI commit",
            "subprocess": True,
        }
        
        self._config["customCommands"].append(shortcut)
        self._save_config()
        
        return True
    
    def uninstall_shortcut(self, key: str, context: str) -> bool:
        """
        Remove LazyGit shortcut.
        
        Args:
            key: Key binding to remove
            context: LazyGit context
            
        Returns:
            True if shortcut was removed, False if not found
        """
        self._load_config()
        self._ensure_custom_commands_section()
        
        existing = self.get_shortcut_command(key, context)
        if not existing:
            return False
        
        self._config["customCommands"].remove(existing)
        self._save_config()
        
        return True
    
    def list_shortcuts(self) -> List[Dict]:
        """List all installed shortcuts."""
        self._load_config()
        self._ensure_custom_commands_section()
        
        return self._config["customCommands"].copy()
    
    def get_lazygit_config_path(self) -> Path:
        """Get the path to LazyGit configuration file."""
        return self.config_file
    
    def backup_config(self) -> Path:
        """Create a backup of the current LazyGit configuration."""
        if not self.config_file.exists():
            raise FileNotFoundError("LazyGit configuration file not found")
        
        backup_path = self.config_file.with_suffix(f".backup.{int(Path().stat().st_mtime)}")
        
        try:
            shutil.copy2(self.config_file, backup_path)
            return backup_path
        except Exception as e:
            raise RuntimeError(f"Failed to backup configuration: {e}")
    
    def restore_config(self, backup_path: Path) -> bool:
        """Restore LazyGit configuration from backup."""
        if not backup_path.exists():
            return False
        
        try:
            shutil.copy2(backup_path, self.config_file)
            self._config = None  # Reset cached config
            return True
        except Exception:
            return False
    
    def validate_config(self) -> bool:
        """Validate LazyGit configuration structure."""
        try:
            self._load_config()
            
            # Check required sections
            if "customCommands" not in self._config:
                return False
            
            # Validate custom commands
            for command in self._config["customCommands"]:
                required_fields = ["key", "context", "command"]
                if not all(field in command for field in required_fields):
                    return False
            
            return True
        except Exception:
            return False
    
    def get_shortcut_yaml(self, key: str, context: str) -> str:
        """Get YAML representation of a shortcut for documentation."""
        shortcut = {
            "key": key,
            "context": context,
            "command": "lazygit-ai commit",
            "description": "AI commit",
            "subprocess": True,
        }
        
        return yaml.dump([shortcut], default_flow_style=False, sort_keys=False)
    
    def install_multiple_shortcuts(self, shortcuts: List[Dict], force: bool = False) -> Dict[str, bool]:
        """
        Install multiple shortcuts at once.
        
        Args:
            shortcuts: List of shortcut dictionaries
            force: Overwrite existing shortcuts
            
        Returns:
            Dictionary mapping shortcut keys to success status
        """
        results = {}
        
        for shortcut in shortcuts:
            key = shortcut.get("key")
            context = shortcut.get("context")
            
            if key and context:
                success = self.install_shortcut(key, context, force)
                results[f"{key}:{context}"] = success
        
        return results
    
    def get_default_shortcuts(self) -> List[Dict]:
        """Get recommended default shortcuts for lazygit-ai."""
        return [
            {
                "key": "C",
                "context": "files",
                "command": "lazygit-ai commit",
                "description": "AI commit",
                "subprocess": True,
            },
            {
                "key": "A",
                "context": "files",
                "command": "lazygit-ai commit --no-ai",
                "description": "Rule-based commit",
                "subprocess": True,
            },
            {
                "key": "X",
                "context": "files",
                "command": "lazygit-ai commit --copy",
                "description": "Copy commit message",
                "subprocess": True,
            },
        ]
    
    def install_default_shortcuts(self, force: bool = False) -> Dict[str, bool]:
        """Install recommended default shortcuts."""
        return self.install_multiple_shortcuts(self.get_default_shortcuts(), force)
    
    def show_shortcut_help(self) -> str:
        """Get help text for using shortcuts in LazyGit."""
        return """
LazyGit Shortcuts for lazygit-ai:

1. Stage your changes in LazyGit
2. Use the following shortcuts in the Files context:

   [C] - Generate AI-powered commit message
   [A] - Generate rule-based commit message (no AI)
   [X] - Copy commit message to clipboard

3. Review and edit the generated commit message
4. Accept to commit or copy to clipboard

To install these shortcuts, run:
   lazygit-ai install-shortcut

To customize shortcuts, edit your LazyGit config:
   ~/.config/lazygit/config.yml
""" 