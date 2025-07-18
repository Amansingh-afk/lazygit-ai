"""
Enhanced rule-based commit message generation for lazygit-ai.

Uses advanced patterns, heuristics, and analysis to generate meaningful commit messages
that follow conventional commit standards without requiring AI assistance.
"""

import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

from .analyzer import GitAnalysis
from ..utils.config import ConfigManager


@dataclass
class CommitPattern:
    """Represents a commit pattern with type, scope, and description."""
    type: str
    scope: Optional[str]
    description: str
    confidence: float  # 0.0 to 1.0


class EnhancedRuleEngine:
    """Enhanced rule-based commit message generator with sophisticated analysis."""
    
    def __init__(self, config: ConfigManager) -> None:
        """Initialize enhanced rule engine with configuration."""
        self.config = config
        self.commit_config = config.get_commit_config()
        self.rules_config = config.get_rules_config()
        
        # Enhanced patterns for better detection
        self._init_patterns()
    
    def _init_patterns(self) -> None:
        """Initialize enhanced patterns for commit analysis."""
        # File type patterns with confidence scores
        self.file_type_patterns = {
            "docs": {
                "patterns": ["readme", "docs", "documentation", "*.md", "*.rst", "*.txt"],
                "type": "docs",
                "confidence": 0.9
            },
            "tests": {
                "patterns": ["test", "spec", "*.test.", "*.spec.", "test_", "spec_"],
                "type": "test",
                "confidence": 0.9
            },
            "config": {
                "patterns": ["config", "settings", "env", "*.conf", "*.cfg", "*.ini", "*.toml", "*.yaml", "*.yml"],
                "type": "chore",
                "confidence": 0.8
            },
            "style": {
                "patterns": ["style", "css", "scss", "less", "*.css", "*.scss", "*.less"],
                "type": "style",
                "confidence": 0.8
            },
            "deps": {
                "patterns": ["requirements", "package.json", "pyproject.toml", "Cargo.toml", "go.mod"],
                "type": "chore",
                "confidence": 0.7
            }
        }
        
        # Diff content patterns
        self.diff_patterns = {
            "fix": {
                "patterns": [
                    r"fix\s+", r"bug\s+", r"issue\s+", r"error\s+", r"exception\s+",
                    r"crash\s+", r"fail\s+", r"broken\s+", r"wrong\s+", r"incorrect\s+"
                ],
                "type": "fix",
                "confidence": 0.8
            },
            "feat": {
                "patterns": [
                    r"add\s+", r"new\s+", r"implement\s+", r"create\s+", r"introduce\s+",
                    r"feature\s+", r"functionality\s+", r"capability\s+"
                ],
                "type": "feat",
                "confidence": 0.7
            },
            "refactor": {
                "patterns": [
                    r"refactor\s+", r"cleanup\s+", r"restructure\s+", r"reorganize\s+",
                    r"simplify\s+", r"extract\s+", r"consolidate\s+"
                ],
                "type": "refactor",
                "confidence": 0.7
            },
            "perf": {
                "patterns": [
                    r"performance\s+", r"optimize\s+", r"speed\s+", r"fast\s+",
                    r"efficient\s+", r"cache\s+", r"memory\s+"
                ],
                "type": "perf",
                "confidence": 0.8
            },
            "style": {
                "patterns": [
                    r"style\s+", r"format\s+", r"indent\s+", r"whitespace\s+",
                    r"lint\s+", r"prettier\s+", r"beautify\s+"
                ],
                "type": "style",
                "confidence": 0.8
            }
        }
        
        # Function and method patterns
        self.function_patterns = [
            r"def\s+(\w+)",  # Python
            r"function\s+(\w+)",  # JavaScript
            r"fn\s+(\w+)",  # Rust
            r"func\s+(\w+)",  # Go
            r"public\s+\w+\s+(\w+)\s*\(",  # Java/C#
        ]
        
        # Version bump patterns
        self.version_patterns = [
            r"version\s*[=:]\s*['\"]?(\d+\.\d+\.\d+)['\"]?",
            r"__version__\s*=\s*['\"]?(\d+\.\d+\.\d+)['\"]?",
            r'"version":\s*"(\d+\.\d+\.\d+)"',
        ]
    
    def generate_message(self, analysis: GitAnalysis) -> str:
        """Generate an enhanced commit message based on comprehensive analysis."""
        # Analyze all possible patterns
        patterns = self._analyze_all_patterns(analysis)
        
        # Select the best pattern
        best_pattern = self._select_best_pattern(patterns)
        
        # Generate final message
        return self._format_final_message(best_pattern, analysis)
    
    def _analyze_all_patterns(self, analysis: GitAnalysis) -> List[CommitPattern]:
        """Analyze all possible commit patterns from the analysis."""
        patterns = []
        
        # 1. Branch-based patterns (highest priority)
        if analysis.branch_type:
            branch_pattern = self._analyze_branch_pattern(analysis)
            if branch_pattern:
                patterns.append(branch_pattern)
        
        # 2. Comment-based patterns (high priority)
        comment_patterns = self._analyze_comment_patterns(analysis)
        patterns.extend(comment_patterns)
        
        # 3. File-based patterns
        file_patterns = self._analyze_file_patterns(analysis)
        patterns.extend(file_patterns)
        
        # 4. Diff-based patterns
        diff_patterns = self._analyze_diff_patterns(analysis)
        patterns.extend(diff_patterns)
        
        # 5. Function-based patterns
        function_patterns = self._analyze_function_patterns(analysis)
        patterns.extend(function_patterns)
        
        # 6. Version-based patterns
        version_patterns = self._analyze_version_patterns(analysis)
        patterns.extend(version_patterns)
        
        # 7. Statistics-based patterns
        stats_patterns = self._analyze_stats_patterns(analysis)
        patterns.extend(stats_patterns)
        
        return patterns
    
    def _analyze_branch_pattern(self, analysis: GitAnalysis) -> Optional[CommitPattern]:
        """Analyze branch name for commit pattern."""
        if not analysis.branch_type:
            return None
        
        commit_type = self._normalize_commit_type(analysis.branch_type)
        scope = analysis.branch_scope
        
        # Generate description from branch scope
        if scope:
            description = f"implement {scope.replace('-', ' ').replace('_', ' ')}"
        else:
            description = "implement feature"
        
        return CommitPattern(
            type=commit_type,
            scope=scope,
            description=description,
            confidence=0.9
        )
    
    def _analyze_comment_patterns(self, analysis: GitAnalysis) -> List[CommitPattern]:
        """Analyze TODO, FIX, and BUG comments."""
        patterns = []
        
        # TODO comments
        if analysis.todos and self.rules_config["enable_todos"]:
            for todo in analysis.todos[:2]:  # Take first 2 TODO comments
                clean_todo = self._clean_comment_text(todo)
                patterns.append(CommitPattern(
                    type="feat",
                    scope=None,
                    description=clean_todo,
                    confidence=0.8
                ))
        
        # FIX comments
        if analysis.fixes and self.rules_config["enable_fixes"]:
            for fix in analysis.fixes[:2]:
                clean_fix = self._clean_comment_text(fix)
                patterns.append(CommitPattern(
                    type="fix",
                    scope=None,
                    description=clean_fix,
                    confidence=0.9
                ))
        
        # BUG comments
        if analysis.bugs and self.rules_config["enable_bugs"]:
            for bug in analysis.bugs[:2]:
                clean_bug = self._clean_comment_text(bug)
                patterns.append(CommitPattern(
                    type="fix",
                    scope=None,
                    description=clean_bug,
                    confidence=0.9
                ))
        
        return patterns
    
    def _analyze_file_patterns(self, analysis: GitAnalysis) -> List[CommitPattern]:
        """Analyze file types and names for patterns."""
        patterns = []
        
        for file_path in analysis.staged_files:
            file_lower = file_path.lower()
            file_name = file_path.split("/")[-1]
            
            # Check file type patterns
            for file_type, config in self.file_type_patterns.items():
                for pattern in config["patterns"]:
                    if pattern in file_lower or file_name.endswith(pattern.replace("*", "")):
                        scope = self._extract_scope_from_path(file_path)
                        description = self._generate_file_description(file_type, file_name)
                        
                        patterns.append(CommitPattern(
                            type=config["type"],
                            scope=scope,
                            description=description,
                            confidence=config["confidence"]
                        ))
                        break  # Found a match for this file type
        
        return patterns
    
    def _analyze_diff_patterns(self, analysis: GitAnalysis) -> List[CommitPattern]:
        """Analyze diff content for patterns."""
        patterns = []
        diff_lower = analysis.staged_diff.lower()
        
        for pattern_type, config in self.diff_patterns.items():
            for pattern in config["patterns"]:
                if re.search(pattern, diff_lower):
                    # Extract context around the pattern
                    context = self._extract_diff_context(analysis.staged_diff, pattern)
                    description = self._generate_diff_description(pattern_type, context)
                    
                    patterns.append(CommitPattern(
                        type=config["type"],
                        scope=None,
                        description=description,
                        confidence=config["confidence"]
                    ))
                    break  # Found a match for this pattern type
        
        return patterns
    
    def _analyze_function_patterns(self, analysis: GitAnalysis) -> List[CommitPattern]:
        """Analyze function and method changes."""
        patterns = []
        
        for pattern in self.function_patterns:
            matches = re.findall(pattern, analysis.staged_diff, re.MULTILINE)
            if matches:
                # Get the most common function name
                function_name = max(set(matches), key=matches.count)
                description = f"update {function_name} function"
                
                patterns.append(CommitPattern(
                    type="refactor",
                    scope=None,
                    description=description,
                    confidence=0.6
                ))
                break
        
        return patterns
    
    def _analyze_version_patterns(self, analysis: GitAnalysis) -> List[CommitPattern]:
        """Analyze version bump patterns."""
        patterns = []
        
        for pattern in self.version_patterns:
            matches = re.findall(pattern, analysis.staged_diff, re.MULTILINE)
            if matches:
                version = matches[0]
                description = f"bump version to {version}"
                
                patterns.append(CommitPattern(
                    type="chore",
                    scope="version",
                    description=description,
                    confidence=0.9
                ))
                break
        
        return patterns
    
    def _analyze_stats_patterns(self, analysis: GitAnalysis) -> List[CommitPattern]:
        """Analyze git statistics for patterns."""
        patterns = []
        
        insertions = analysis.stats.get("insertions", 0)
        deletions = analysis.stats.get("deletions", 0)
        files_changed = len(analysis.staged_files)
        
        # Large additions
        if insertions > deletions * 3 and insertions > 50:
            patterns.append(CommitPattern(
                type="feat",
                scope=None,
                description="add new features",
                confidence=0.6
            ))
        
        # Large deletions
        elif deletions > insertions * 3 and deletions > 50:
            patterns.append(CommitPattern(
                type="refactor",
                scope=None,
                description="remove unused code",
                confidence=0.6
            ))
        
        # Single file changes
        elif files_changed == 1:
            file_name = analysis.staged_files[0].split("/")[-1]
            patterns.append(CommitPattern(
                type="fix",
                scope=None,
                description=f"update {file_name}",
                confidence=0.5
            ))
        
        return patterns
    
    def _select_best_pattern(self, patterns: List[CommitPattern]) -> CommitPattern:
        """Select the best commit pattern based on confidence and specificity."""
        if not patterns:
            return CommitPattern(
                type="feat",
                scope=None,
                description="update code",
                confidence=0.1
            )
        
        # Sort by confidence, then by specificity
        sorted_patterns = sorted(
            patterns,
            key=lambda p: (p.confidence, len(p.description)),
            reverse=True
        )
        
        return sorted_patterns[0]
    
    def _format_final_message(self, pattern: CommitPattern, analysis: GitAnalysis) -> str:
        """Format the final commit message."""
        # Determine scope
        scope = pattern.scope or self._determine_scope(analysis)
        
        # Clean and enhance description
        description = self._enhance_description(pattern.description, analysis)
        
        # Format according to configuration
        if self.commit_config["conventional"]:
            return self._format_conventional(pattern.type, scope, description)
        else:
            return description
    
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
    
    def _enhance_description(self, description: str, analysis: GitAnalysis) -> str:
        """Enhance the description with additional context."""
        # Clean the description
        description = self._clean_description(description)
        
        # Check for specific patterns and enhance accordingly
        enhanced_description = self._apply_specific_enhancements(description, analysis)
        
        # Ensure it starts with a verb
        enhanced_description = self._ensure_verb_start(enhanced_description)
        
        # Truncate if too long
        max_length = self.commit_config["max_length"]
        if len(enhanced_description) > max_length:
            enhanced_description = enhanced_description[:max_length-3] + "..."
        
        return enhanced_description
    
    def _apply_specific_enhancements(self, description: str, analysis: GitAnalysis) -> str:
        """Apply specific enhancements based on analysis context."""
        # Version bump enhancement
        if analysis.version_changes:
            version = analysis.version_changes[0]
            if "version" not in description.lower():
                if analysis.file_types.get("docs"):
                    return f"update documentation and bump version to {version}"
                else:
                    return f"{description} and bump version to {version}"
        
        # Documentation updates
        if analysis.file_types.get("docs") and "documentation" not in description.lower():
            if analysis.file_types.get("config"):
                return f"update documentation and {description}"
            else:
                return f"update documentation"
        
        # Git-related fixes
        if analysis.branch_scope and "git" in analysis.branch_scope:
            if "detection" in analysis.branch_scope or "staged" in analysis.branch_scope:
                return "improve git staged file detection"
            elif "llm" in analysis.branch_scope:
                return "clean up LLM code"
        
        # TUI-related fixes
        if analysis.branch_scope and "tui" in analysis.branch_scope:
            if analysis.color_changes:
                return "improve color scheme consistency in TUI"
            else:
                return "improve TUI consistency"
        
        # Color scheme changes
        if analysis.color_changes and not analysis.branch_scope:
            return "improve color scheme consistency"
        
        # Function changes
        if analysis.function_changes:
            function_name = analysis.function_changes[0]
            return f"update {function_name} function"
        
        # Configuration changes
        if analysis.config_changes:
            return "update configuration"
        
        # Bug fixes
        if analysis.bugs or analysis.fixes:
            if analysis.bugs:
                bug_text = analysis.bugs[0]
                return f"fix {bug_text.lower()}"
            elif analysis.fixes:
                fix_text = analysis.fixes[0]
                return f"fix {fix_text.lower()}"
        
        # TODO comments
        if analysis.todos:
            todo_text = analysis.todos[0]
            return f"implement {todo_text.lower()}"
        
        # File-specific descriptions
        if len(analysis.staged_files) == 1:
            file_name = analysis.staged_files[0].split("/")[-1]
            if file_name.endswith(".md"):
                return "update documentation"
            elif file_name.endswith(".py"):
                return "update code"
            elif file_name.endswith((".toml", ".yaml", ".yml", ".json")):
                return "update configuration"
        
        # Default enhancement
        return description
    
    def _clean_description(self, text: str) -> str:
        """Clean and format description text."""
        # Remove extra whitespace
        text = re.sub(r"\s+", " ", text.strip())
        
        # Remove common prefixes
        text = re.sub(r"^(TODO|FIX|BUG)[:\s]*", "", text, flags=re.IGNORECASE)
        
        # Capitalize first letter
        if text:
            text = text[0].upper() + text[1:]
        
        return text
    
    def _clean_comment_text(self, text: str) -> str:
        """Clean comment text for use in commit messages."""
        # Remove comment markers
        text = re.sub(r"^[#/]*\s*", "", text.strip())
        text = re.sub(r"\s*[#/]*$", "", text)
        
        # Remove TODO/FIX/BUG prefixes
        text = re.sub(r"^(TODO|FIX|BUG)[:\s]*", "", text, flags=re.IGNORECASE)
        
        # Clean up whitespace
        text = re.sub(r"\s+", " ", text.strip())
        
        return text
    
    def _extract_scope_from_path(self, file_path: str) -> Optional[str]:
        """Extract scope from file path."""
        path_parts = file_path.split("/")
        if len(path_parts) > 1:
            return path_parts[0].lower()
        return None
    
    def _generate_file_description(self, file_type: str, file_name: str) -> str:
        """Generate description based on file type."""
        descriptions = {
            "docs": "update documentation",
            "tests": "add tests",
            "config": "update configuration",
            "style": "improve styling",
            "deps": "update dependencies"
        }
        
        base_desc = descriptions.get(file_type, "update code")
        
        # Add file name if it's specific
        if file_name and file_name not in ["README.md", "requirements.txt", "package.json"]:
            return f"{base_desc} for {file_name}"
        
        return base_desc
    
    def _extract_diff_context(self, diff: str, pattern: str) -> str:
        """Extract context around a pattern in the diff."""
        lines = diff.split("\n")
        context_lines = []
        
        for i, line in enumerate(lines):
            if re.search(pattern, line, re.IGNORECASE):
                # Get surrounding lines for context
                start = max(0, i - 2)
                end = min(len(lines), i + 3)
                context_lines.extend(lines[start:end])
                break
        
        return "\n".join(context_lines[:5])  # Limit to 5 lines
    
    def _generate_diff_description(self, pattern_type: str, context: str) -> str:
        """Generate description based on diff pattern type."""
        descriptions = {
            "fix": "fix issues",
            "feat": "add new features",
            "refactor": "refactor code",
            "perf": "improve performance",
            "style": "improve code style"
        }
        
        return descriptions.get(pattern_type, "update code")
    
    def _ensure_verb_start(self, text: str) -> str:
        """Ensure description starts with a verb."""
        # Common verbs for commit messages
        verbs = [
            "add", "update", "fix", "remove", "refactor", "improve", "enhance",
            "implement", "create", "delete", "modify", "change", "optimize",
            "clean", "format", "style", "test", "document", "configure",
            "bump", "upgrade", "downgrade", "replace", "rename", "move"
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
            "clean", "format", "style", "test", "document", "configure",
            "bump", "upgrade", "downgrade", "replace", "rename", "move"
        ]
        
        message_lower = message.lower()
        for verb in imperative_verbs:
            if message_lower.startswith(verb):
                return True
        
        return False


# Backward compatibility - alias the new class to the old name
RuleEngine = EnhancedRuleEngine 