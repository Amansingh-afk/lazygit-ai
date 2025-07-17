"""
Rule-based commit message generation for lazygit-ai.

Uses patterns, heuristics, and analysis to generate meaningful commit messages
without requiring AI assistance.
"""

import re
from typing import Dict, List, Optional

from .analyzer import GitAnalysis
from ..utils.config import ConfigManager


class RuleEngine:
    """Rule-based commit message generator."""
    
    def __init__(self, config: ConfigManager) -> None:
        """Initialize rule engine with configuration."""
        self.config = config
        self.commit_config = config.get_commit_config()
        self.rules_config = config.get_rules_config()
    
    def generate_message(self, analysis: GitAnalysis) -> str:
        """Generate a commit message based on analysis."""
        # Determine commit type
        commit_type = self._determine_commit_type(analysis)
        
        # Determine scope
        scope = self._determine_scope(analysis)
        
        # Generate description
        description = self._generate_description(analysis)
        
        # Format the message
        if self.commit_config["conventional"]:
            return self._format_conventional(commit_type, scope, description)
        else:
            return description
    
    def _determine_commit_type(self, analysis: GitAnalysis) -> str:
        """Determine the type of commit based on analysis."""
        # Check branch type first
        if analysis.branch_type:
            return self._normalize_commit_type(analysis.branch_type)
        
        # Check for specific patterns in changes
        if analysis.fixes:
            return "fix"
        
        if analysis.bugs:
            return "fix"
        
        # Check file types
        if analysis.file_types.get("tests"):
            return "test"
        
        if analysis.file_types.get("docs"):
            return "docs"
        
        if analysis.file_types.get("config"):
            return "chore"
        
        # Check for specific file patterns
        for file_path in analysis.staged_files:
            path_lower = file_path.lower()
            
            if any(pattern in path_lower for pattern in ["test", "spec"]):
                return "test"
            
            if any(pattern in path_lower for pattern in ["readme", "docs", "documentation"]):
                return "docs"
            
            if any(pattern in path_lower for pattern in ["config", "settings", "env"]):
                return "chore"
            
            if any(pattern in path_lower for pattern in ["style", "css", "scss"]):
                return "style"
        
        # Check diff patterns
        diff_lower = analysis.staged_diff.lower()
        
        if any(pattern in diff_lower for pattern in ["fix", "bug", "issue"]):
            return "fix"
        
        if any(pattern in diff_lower for pattern in ["refactor", "cleanup"]):
            return "refactor"
        
        if any(pattern in diff_lower for pattern in ["performance", "optimize"]):
            return "perf"
        
        if any(pattern in diff_lower for pattern in ["style", "format"]):
            return "style"
        
        # Default to feat for new features
        return "feat"
    
    def _normalize_commit_type(self, branch_type: str) -> str:
        """Normalize branch type to conventional commit type."""
        type_mapping = {
            "feat": "feat",
            "feature": "feat",
            "fix": "fix",
            "bugfix": "fix",
            "hotfix": "fix",
            "docs": "docs",
            "documentation": "docs",
            "test": "test",
            "testing": "test",
            "refactor": "refactor",
            "refactoring": "refactor",
            "style": "style",
            "styling": "style",
            "perf": "perf",
            "performance": "perf",
            "chore": "chore",
            "maintenance": "chore",
            "release": "release",
        }
        
        return type_mapping.get(branch_type.lower(), "feat")
    
    def _determine_scope(self, analysis: GitAnalysis) -> Optional[str]:
        """Determine the scope of the commit."""
        if not self.commit_config["include_scope"]:
            return None
        
        # Use branch scope if available
        if analysis.branch_scope:
            return self._format_scope(analysis.branch_scope)
        
        # Use scope suggestions
        if analysis.scope_suggestions:
            return self._format_scope(analysis.scope_suggestions[0])
        
        # Try to infer from file paths
        scopes = set()
        for file_path in analysis.staged_files:
            path_parts = file_path.split("/")
            if len(path_parts) > 1:
                scopes.add(path_parts[0])
        
        if scopes:
            return self._format_scope(list(scopes)[0])
        
        return None
    
    def _format_scope(self, scope: str) -> str:
        """Format scope according to configuration."""
        scope_style = self.commit_config["scope_style"]
        
        if scope_style == "lowercase":
            return scope.lower()
        elif scope_style == "kebab-case":
            return scope.lower().replace("_", "-").replace(" ", "-")
        elif scope_style == "camelCase":
            return scope.lower().title().replace(" ", "").replace("_", "").replace("-", "")
        else:
            return scope.lower()
    
    def _generate_description(self, analysis: GitAnalysis) -> str:
        """Generate the description part of the commit message."""
        # Check for TODO comments first
        if analysis.todos and self.rules_config["enable_todos"]:
            todo_text = analysis.todos[0]
            # Clean up TODO text
            todo_text = re.sub(r"^TODO[:\s]*", "", todo_text, flags=re.IGNORECASE)
            return self._clean_description(todo_text)
        
        # Check for FIX comments
        if analysis.fixes and self.rules_config["enable_fixes"]:
            fix_text = analysis.fixes[0]
            fix_text = re.sub(r"^FIX[:\s]*", "", fix_text, flags=re.IGNORECASE)
            return self._clean_description(fix_text)
        
        # Check for BUG comments
        if analysis.bugs and self.rules_config["enable_bugs"]:
            bug_text = analysis.bugs[0]
            bug_text = re.sub(r"^BUG[:\s]*", "", bug_text, flags=re.IGNORECASE)
            return self._clean_description(bug_text)
        
        # Generate based on file types and changes
        return self._generate_file_based_description(analysis)
    
    def _clean_description(self, text: str) -> str:
        """Clean and format description text."""
        # Remove extra whitespace
        text = re.sub(r"\s+", " ", text.strip())
        
        # Ensure it starts with a verb
        text = self._ensure_verb_start(text)
        
        # Truncate if too long
        max_length = self.commit_config["max_length"]
        if len(text) > max_length:
            text = text[:max_length-3] + "..."
        
        return text
    
    def _ensure_verb_start(self, text: str) -> str:
        """Ensure description starts with a verb."""
        # Common verbs for commit messages
        verbs = [
            "add", "update", "fix", "remove", "refactor", "improve", "enhance",
            "implement", "create", "delete", "modify", "change", "optimize",
            "clean", "format", "style", "test", "document", "configure"
        ]
        
        text_lower = text.lower()
        
        # Check if it already starts with a verb
        for verb in verbs:
            if text_lower.startswith(verb):
                return text
        
        # Try to extract action from common patterns
        patterns = [
            r"(?:add|create|new)\s+(.+)",
            r"(?:update|modify|change)\s+(.+)",
            r"(?:fix|resolve|solve)\s+(.+)",
            r"(?:remove|delete|drop)\s+(.+)",
            r"(?:improve|enhance|optimize)\s+(.+)",
        ]
        
        for pattern in patterns:
            match = re.match(pattern, text_lower)
            if match:
                return text
        
        # Default to "update" if no clear action
        return f"update {text}"
    
    def _generate_file_based_description(self, analysis: GitAnalysis) -> str:
        """Generate description based on file types and changes."""
        descriptions = []
        
        # File type descriptions
        if analysis.file_types.get("code"):
            descriptions.append("update code")
        
        if analysis.file_types.get("tests"):
            descriptions.append("add tests")
        
        if analysis.file_types.get("docs"):
            descriptions.append("update documentation")
        
        if analysis.file_types.get("config"):
            descriptions.append("update configuration")
        
        if analysis.file_types.get("assets"):
            descriptions.append("update assets")
        
        # Change-based descriptions
        if analysis.stats.get("insertions", 0) > analysis.stats.get("deletions", 0) * 2:
            descriptions.append("add new features")
        elif analysis.stats.get("deletions", 0) > analysis.stats.get("insertions", 0) * 2:
            descriptions.append("remove unused code")
        
        # File count descriptions
        if len(analysis.staged_files) == 1:
            file_name = analysis.staged_files[0].split("/")[-1]
            descriptions.append(f"update {file_name}")
        elif len(analysis.staged_files) <= 3:
            file_types = list(analysis.file_types.keys())
            if file_types:
                descriptions.append(f"update {file_types[0]} files")
        
        # Combine descriptions
        if descriptions:
            # Take the most specific description
            return descriptions[0]
        else:
            return "update files"
    
    def _format_conventional(self, commit_type: str, scope: Optional[str], description: str) -> str:
        """Format as conventional commit message."""
        if scope:
            return f"{commit_type}({scope}): {description}"
        else:
            return f"{commit_type}: {description}"
    
    def get_commit_type_help(self) -> Dict[str, str]:
        """Get help text for commit types."""
        return {
            "feat": "A new feature",
            "fix": "A bug fix",
            "docs": "Documentation only changes",
            "style": "Changes that do not affect the meaning of the code",
            "refactor": "A code change that neither fixes a bug nor adds a feature",
            "perf": "A code change that improves performance",
            "test": "Adding missing tests or correcting existing tests",
            "chore": "Changes to the build process or auxiliary tools",
            "release": "Create a release commit",
        }
    
    def validate_message(self, message: str) -> bool:
        """Validate a commit message."""
        if not message or len(message.strip()) == 0:
            return False
        
        if len(message) > self.commit_config["max_length"]:
            return False
        
        # Check for conventional commit format if enabled
        if self.commit_config["conventional"]:
            pattern = r"^(feat|fix|docs|style|refactor|perf|test|chore|release)(\([a-z-]+\))?:\s+.+"
            if not re.match(pattern, message):
                return False
        
        return True
    
    def suggest_improvements(self, message: str) -> List[str]:
        """Suggest improvements for a commit message."""
        suggestions = []
        
        # Check length
        if len(message) > self.commit_config["max_length"]:
            suggestions.append(f"Message is too long ({len(message)} chars). Consider shortening.")
        
        # Check for common issues
        if message.lower().startswith("update"):
            suggestions.append("Consider using a more specific verb than 'update'")
        
        if "stuff" in message.lower() or "things" in message.lower():
            suggestions.append("Avoid vague words like 'stuff' or 'things'")
        
        if message.endswith("."):
            suggestions.append("Conventional commits typically don't end with a period")
        
        # Check for imperative mood
        if not self._is_imperative(message):
            suggestions.append("Use imperative mood (e.g., 'add' not 'added')")
        
        return suggestions
    
    def _is_imperative(self, message: str) -> bool:
        """Check if message uses imperative mood."""
        # Remove conventional commit prefix
        if ":" in message:
            message = message.split(":", 1)[1].strip()
        
        # Common imperative verbs
        imperative_verbs = [
            "add", "update", "fix", "remove", "refactor", "improve", "enhance",
            "implement", "create", "delete", "modify", "change", "optimize",
            "clean", "format", "style", "test", "document", "configure"
        ]
        
        message_lower = message.lower()
        for verb in imperative_verbs:
            if message_lower.startswith(verb):
                return True
        
        return False 