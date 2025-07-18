"""
Enhanced Git analysis module for lazygit-ai.

Analyzes git state including staged changes, branch information, and file types
to provide comprehensive context for commit message generation.
"""

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Set, Any

from ..utils.git import GitWrapper


# Configuration constants for large file handling
MAX_DIFF_SIZE = 1024 * 1024  # 1MB limit for diff processing
MAX_DIFF_LINES = 10000  # 10k lines limit
MAX_PATTERN_MATCHES = 100  # Limit pattern matches per diff
CHUNK_SIZE = 8192  # 8KB chunks for streaming


@dataclass
class GitAnalysis:
    """Container for git analysis results."""
    
    # Basic information
    branch_name: str
    staged_files: List[str]
    unstaged_files: List[str]
    
    # File analysis
    file_types: Dict[str, List[str]]
    file_extensions: List[str]
    
    # Diff analysis
    staged_diff: str
    unstaged_diff: str
    
    # Statistics
    stats: Dict[str, int]
    
    # Patterns found
    todos: List[str]
    fixes: List[str]
    bugs: List[str]
    
    # Enhanced patterns
    version_changes: List[str]
    function_changes: List[str]
    color_changes: List[str]
    config_changes: List[str]
    
    # Branch analysis
    branch_type: Optional[str]
    branch_scope: Optional[str]
    
    # Context
    recent_commits: List[Dict[str, str]]
    remote_url: Optional[str]
    
    # Derived information
    primary_file_type: Optional[str]
    change_summary: str
    scope_suggestions: List[str]
    
    # Enhanced context
    change_context: Dict[str, Any]
    impact_level: str  # low, medium, high


class GitAnalyzer:
    """Enhanced analyzer for git state and commit message generation."""
    
    def __init__(self, git_wrapper: GitWrapper) -> None:
        """Initialize analyzer with git wrapper."""
        self.git = git_wrapper
    
    def analyze(self) -> GitAnalysis:
        """Perform comprehensive git analysis."""
        # Get basic information
        branch_name = self.git.get_current_branch()
        staged_files = self.git.get_staged_files()
        unstaged_files = self._get_unstaged_files()
        
        # Analyze files
        file_types = self.git.get_file_types(staged_files)
        file_extensions = self.git.get_file_extensions(staged_files)
        
        # Get diffs with size limits
        staged_diff = self._get_staged_diff_with_limits()
        unstaged_diff = self._get_unstaged_diff_with_limits()
        
        # Get statistics
        stats = self.git.get_commit_stats()
        
        # Analyze patterns in diffs (with limits)
        todos = self._extract_todos(staged_diff)
        fixes = self._extract_fixes(staged_diff)
        bugs = self._extract_bugs(staged_diff)
        
        # Enhanced pattern extraction (with limits)
        version_changes = self._extract_version_changes(staged_diff)
        function_changes = self._extract_function_changes(staged_diff)
        color_changes = self._extract_color_changes(staged_diff)
        config_changes = self._extract_config_changes(staged_diff)
        
        # Analyze branch
        branch_type, branch_scope = self._analyze_branch(branch_name)
        
        # Get context
        recent_commits = self.git.get_recent_commits(5)
        remote_url = self.git.get_remote_url()
        
        # Derive additional information
        primary_file_type = self._get_primary_file_type(file_types)
        change_summary = self._generate_change_summary(staged_files, stats, file_types)
        scope_suggestions = self._generate_scope_suggestions(staged_files, branch_scope, file_types)
        
        # Enhanced context analysis
        change_context = self._analyze_change_context(staged_files, stats, file_types, staged_diff)
        impact_level = self._determine_impact_level(stats, staged_files, file_types)
        
        return GitAnalysis(
            branch_name=branch_name,
            staged_files=staged_files,
            unstaged_files=unstaged_files,
            file_types=file_types,
            file_extensions=file_extensions,
            staged_diff=staged_diff,
            unstaged_diff=unstaged_diff,
            stats=stats,
            todos=todos,
            fixes=fixes,
            bugs=bugs,
            version_changes=version_changes,
            function_changes=function_changes,
            color_changes=color_changes,
            config_changes=config_changes,
            branch_type=branch_type,
            branch_scope=branch_scope,
            recent_commits=recent_commits,
            remote_url=remote_url,
            primary_file_type=primary_file_type,
            change_summary=change_summary,
            scope_suggestions=scope_suggestions,
            change_context=change_context,
            impact_level=impact_level,
        )
    
    def _get_staged_diff_with_limits(self) -> str:
        """Get staged diff with size and line limits."""
        try:
            import subprocess
            
            # First, check the size of the diff
            size_result = subprocess.run(
                ["git", "diff", "--cached", "--stat"],
                capture_output=True,
                text=True,
                cwd=self.git.repo_path,
                check=True,
            )
            
            # If diff is too large, get a truncated version
            if len(size_result.stdout) > MAX_DIFF_SIZE:
                # Get only the first part of the diff
                result = subprocess.run(
                    ["git", "diff", "--cached", "--no-color"],
                    capture_output=True,
                    text=True,
                    cwd=self.git.repo_path,
                    check=True,
                )
                
                diff_content = result.stdout
                lines = diff_content.split('\n')
                
                if len(lines) > MAX_DIFF_LINES:
                    # Truncate to MAX_DIFF_LINES and add truncation notice
                    truncated_lines = lines[:MAX_DIFF_LINES]
                    truncated_lines.append(f"\n... (diff truncated at {MAX_DIFF_LINES} lines)")
                    return '\n'.join(truncated_lines)
                
                return diff_content
            else:
                # Normal diff processing
                return self.git.get_staged_diff()
                
        except subprocess.CalledProcessError:
            return ""
    
    def _get_unstaged_diff_with_limits(self) -> str:
        """Get unstaged diff with size and line limits."""
        try:
            import subprocess
            
            # First, check the size of the diff
            size_result = subprocess.run(
                ["git", "diff", "--stat"],
                capture_output=True,
                text=True,
                cwd=self.git.repo_path,
                check=True,
            )
            
            # If diff is too large, get a truncated version
            if len(size_result.stdout) > MAX_DIFF_SIZE:
                # Get only the first part of the diff
                result = subprocess.run(
                    ["git", "diff", "--no-color"],
                    capture_output=True,
                    text=True,
                    cwd=self.git.repo_path,
                    check=True,
                )
                
                diff_content = result.stdout
                lines = diff_content.split('\n')
                
                if len(lines) > MAX_DIFF_LINES:
                    # Truncate to MAX_DIFF_LINES and add truncation notice
                    truncated_lines = lines[:MAX_DIFF_LINES]
                    truncated_lines.append(f"\n... (diff truncated at {MAX_DIFF_LINES} lines)")
                    return '\n'.join(truncated_lines)
                
                return diff_content
            else:
                # Normal diff processing
                return self.git.get_unstaged_diff()
                
        except subprocess.CalledProcessError:
            return ""
    
    def _get_unstaged_files(self) -> List[str]:
        """Get list of unstaged files."""
        try:
            import subprocess
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                cwd=self.git.repo_path,
                check=True,
            )
            
            unstaged_files = []
            for line in result.stdout.strip().split("\n"):
                if line and line[1] in "MDR":  # Modified, Deleted, Renamed (unstaged)
                    file_path = line[3:]  # Remove status prefix
                    unstaged_files.append(file_path)
            
            return unstaged_files
        except subprocess.CalledProcessError:
            return []
    
    def _extract_todos(self, diff: str) -> List[str]:
        """Extract TODO comments from diff with limits."""
        if not diff or len(diff) > MAX_DIFF_SIZE:
            return []
        
        todos = []
        patterns = [
            r"//\s*TODO[:\s]*(.+)",
            r"#\s*TODO[:\s]*(.+)",
            r"/\*\s*TODO[:\s]*(.+?)\*/",
            r"<!--\s*TODO[:\s]*(.+?)-->",
            r"TODO[:\s]*(.+)",  # Generic TODO
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, diff, re.IGNORECASE | re.MULTILINE)
            # Limit the number of matches to prevent memory issues
            limited_matches = matches[:MAX_PATTERN_MATCHES]
            todos.extend([match.strip() for match in limited_matches])
            
            # Stop if we've reached the limit
            if len(todos) >= MAX_PATTERN_MATCHES:
                break
        
        return todos[:MAX_PATTERN_MATCHES]
    
    def _extract_fixes(self, diff: str) -> List[str]:
        """Extract FIX comments from diff with limits."""
        if not diff or len(diff) > MAX_DIFF_SIZE:
            return []
        
        fixes = []
        patterns = [
            r"//\s*FIX[:\s]*(.+)",
            r"#\s*FIX[:\s]*(.+)",
            r"/\*\s*FIX[:\s]*(.+?)\*/",
            r"<!--\s*FIX[:\s]*(.+?)-->",
            r"FIX[:\s]*(.+)",  # Generic FIX
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, diff, re.IGNORECASE | re.MULTILINE)
            # Limit the number of matches
            limited_matches = matches[:MAX_PATTERN_MATCHES]
            fixes.extend([match.strip() for match in limited_matches])
            
            if len(fixes) >= MAX_PATTERN_MATCHES:
                break
        
        return fixes[:MAX_PATTERN_MATCHES]
    
    def _extract_bugs(self, diff: str) -> List[str]:
        """Extract BUG comments from diff with limits."""
        if not diff or len(diff) > MAX_DIFF_SIZE:
            return []
        
        bugs = []
        patterns = [
            r"//\s*BUG[:\s]*(.+)",
            r"#\s*BUG[:\s]*(.+)",
            r"/\*\s*BUG[:\s]*(.+?)\*/",
            r"<!--\s*BUG[:\s]*(.+?)-->",
            r"BUG[:\s]*(.+)",  # Generic BUG
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, diff, re.IGNORECASE | re.MULTILINE)
            # Limit the number of matches
            limited_matches = matches[:MAX_PATTERN_MATCHES]
            bugs.extend([match.strip() for match in limited_matches])
            
            if len(bugs) >= MAX_PATTERN_MATCHES:
                break
        
        return bugs[:MAX_PATTERN_MATCHES]
    
    def _extract_version_changes(self, diff: str) -> List[str]:
        """Extract version changes from diff with limits."""
        if not diff or len(diff) > MAX_DIFF_SIZE:
            return []
        
        version_changes = []
        patterns = [
            r'version\s*[=:]\s*["\']?(\d+\.\d+\.\d+)["\']?',
            r'__version__\s*=\s*["\']?(\d+\.\d+\.\d+)["\']?',
            r'"version":\s*"(\d+\.\d+\.\d+)"',
            r"'version':\s*'(\d+\.\d+\.\d+)'",
            r'version\s*=\s*["\']?(\d+\.\d+\.\d+)["\']?',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, diff, re.IGNORECASE | re.MULTILINE)
            # Limit the number of matches
            limited_matches = matches[:MAX_PATTERN_MATCHES]
            version_changes.extend(limited_matches)
            
            if len(version_changes) >= MAX_PATTERN_MATCHES:
                break
        
        return version_changes[:MAX_PATTERN_MATCHES]
    
    def _extract_function_changes(self, diff: str) -> List[str]:
        """Extract function and method changes from diff with limits."""
        if not diff or len(diff) > MAX_DIFF_SIZE:
            return []
        
        function_changes = []
        patterns = [
            r'def\s+(\w+)',  # Python
            r'function\s+(\w+)',  # JavaScript
            r'fn\s+(\w+)',  # Rust
            r'func\s+(\w+)',  # Go
            r'public\s+\w+\s+(\w+)\s*\(',  # Java/C#
            r'private\s+\w+\s+(\w+)\s*\(',  # Java/C#
            r'protected\s+\w+\s+(\w+)\s*\(',  # Java/C#
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, diff, re.MULTILINE)
            # Limit the number of matches
            limited_matches = matches[:MAX_PATTERN_MATCHES]
            function_changes.extend(limited_matches)
            
            if len(function_changes) >= MAX_PATTERN_MATCHES:
                break
        
        return function_changes[:MAX_PATTERN_MATCHES]
    
    def _extract_color_changes(self, diff: str) -> List[str]:
        """Extract color-related changes from diff with limits."""
        if not diff or len(diff) > MAX_DIFF_SIZE:
            return []
        
        color_changes = []
        patterns = [
            r'color\s*[=:]\s*["\']?([^"\']+)["\']?',
            r'background-color\s*[=:]\s*["\']?([^"\']+)["\']?',
            r'border-color\s*[=:]\s*["\']?([^"\']+)["\']?',
            r'#[0-9a-fA-F]{3,6}',  # Hex colors
            r'rgb\([^)]+\)',  # RGB colors
            r'rgba\([^)]+\)',  # RGBA colors
            r'hsl\([^)]+\)',  # HSL colors
            r'hsla\([^)]+\)',  # HSLA colors
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, diff, re.IGNORECASE | re.MULTILINE)
            # Limit the number of matches
            limited_matches = matches[:MAX_PATTERN_MATCHES]
            color_changes.extend(limited_matches)
            
            if len(color_changes) >= MAX_PATTERN_MATCHES:
                break
        
        return color_changes[:MAX_PATTERN_MATCHES]
    
    def _extract_config_changes(self, diff: str) -> List[str]:
        """Extract configuration changes from diff with limits."""
        if not diff or len(diff) > MAX_DIFF_SIZE:
            return []
        
        config_changes = []
        patterns = [
            r'config\s*[=:]\s*["\']?([^"\']+)["\']?',
            r'setting\s*[=:]\s*["\']?([^"\']+)["\']?',
            r'option\s*[=:]\s*["\']?([^"\']+)["\']?',
            r'parameter\s*[=:]\s*["\']?([^"\']+)["\']?',
            r'default\s*[=:]\s*["\']?([^"\']+)["\']?',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, diff, re.IGNORECASE | re.MULTILINE)
            # Limit the number of matches
            limited_matches = matches[:MAX_PATTERN_MATCHES]
            config_changes.extend(limited_matches)
            
            if len(config_changes) >= MAX_PATTERN_MATCHES:
                break
        
        return config_changes[:MAX_PATTERN_MATCHES]
    
    def _analyze_branch(self, branch_name: str) -> tuple[Optional[str], Optional[str]]:
        """Analyze branch name for type and scope."""
        # Common branch naming patterns
        patterns = [
            r"^(feat|feature)/(.+)$",
            r"^(fix|bugfix)/(.+)$",
            r"^(docs|documentation)/(.+)$",
            r"^(test|testing)/(.+)$",
            r"^(refactor|refactoring)/(.+)$",
            r"^(style|styling)/(.+)$",
            r"^(perf|performance)/(.+)$",
            r"^(chore|maintenance)/(.+)$",
            r"^(hotfix)/(.+)$",
            r"^(release)/(.+)$",
        ]
        
        for pattern in patterns:
            match = re.match(pattern, branch_name, re.IGNORECASE)
            if match:
                branch_type = match.group(1).lower()
                branch_scope = match.group(2).lower()
                return branch_type, branch_scope
        
        # Try alternative patterns
        if "/" in branch_name:
            parts = branch_name.split("/", 1)
            if len(parts) == 2:
                return parts[0].lower(), parts[1].lower()
        
        return None, None
    
    def _get_primary_file_type(self, file_types: Dict[str, List[str]]) -> Optional[str]:
        """Determine the primary file type being modified."""
        # Priority order for file types
        priority_order = ["code", "tests", "docs", "config", "assets", "other"]
        
        for file_type in priority_order:
            if file_types.get(file_type):
                return file_type
        
        return None
    
    def _generate_change_summary(self, staged_files: List[str], stats: Dict[str, int], file_types: Dict[str, List[str]]) -> str:
        """Generate a human-readable summary of changes."""
        if not staged_files:
            return "No changes"
        
        parts = []
        
        # File count
        file_count = len(staged_files)
        if file_count == 1:
            parts.append("1 file")
        else:
            parts.append(f"{file_count} files")
        
        # Statistics
        if stats.get("insertions", 0) > 0 or stats.get("deletions", 0) > 0:
            insertions = stats.get("insertions", 0)
            deletions = stats.get("deletions", 0)
            
            if insertions > 0 and deletions > 0:
                parts.append(f"{insertions} additions, {deletions} deletions")
            elif insertions > 0:
                parts.append(f"{insertions} additions")
            elif deletions > 0:
                parts.append(f"{deletions} deletions")
        
        # File types
        type_summary = []
        for file_type, files in file_types.items():
            if files:
                if file_type == "code":
                    type_summary.append("code")
                elif file_type == "tests":
                    type_summary.append("tests")
                elif file_type == "docs":
                    type_summary.append("documentation")
                elif file_type == "config":
                    type_summary.append("configuration")
                elif file_type == "assets":
                    type_summary.append("assets")
        
        if type_summary:
            parts.append(f"({', '.join(type_summary)})")
        
        return " ".join(parts)
    
    def _generate_scope_suggestions(self, staged_files: List[str], branch_scope: Optional[str], file_types: Dict[str, List[str]]) -> List[str]:
        """Generate scope suggestions for commit messages."""
        suggestions = set()
        
        # From branch scope
        if branch_scope:
            suggestions.add(branch_scope)
        
        # From file paths
        for file_path in staged_files:
            path = Path(file_path)
            
            # Directory-based scope
            if len(path.parts) > 1:
                # Use first directory as scope
                suggestions.add(path.parts[0])
            
            # File-based scope
            if path.stem:
                suggestions.add(path.stem)
        
        # From file types
        if file_types.get("code"):
            suggestions.add("core")
        if file_types.get("tests"):
            suggestions.add("test")
        if file_types.get("docs"):
            suggestions.add("docs")
        if file_types.get("config"):
            suggestions.add("config")
        
        # Common scopes based on file patterns
        for file_path in staged_files:
            path = Path(file_path)
            
            if "auth" in path.name.lower() or "login" in path.name.lower():
                suggestions.add("auth")
            elif "api" in path.name.lower():
                suggestions.add("api")
            elif "ui" in path.name.lower() or "component" in path.name.lower():
                suggestions.add("ui")
            elif "db" in path.name.lower() or "database" in path.name.lower():
                suggestions.add("db")
            elif "util" in path.name.lower() or "helper" in path.name.lower():
                suggestions.add("utils")
            elif "tui" in path.name.lower():
                suggestions.add("tui")
            elif "llm" in path.name.lower():
                suggestions.add("llm")
            elif "git" in path.name.lower():
                suggestions.add("git")
        
        return sorted(list(suggestions))
    
    def _analyze_change_context(self, staged_files: List[str], stats: Dict[str, int], file_types: Dict[str, List[str]], staged_diff: str) -> Dict[str, Any]:
        """Analyze the context and nature of changes."""
        context = {
            "is_documentation_update": bool(file_types.get("docs")),
            "is_test_update": bool(file_types.get("tests")),
            "is_config_update": bool(file_types.get("config")),
            "is_code_refactor": self._is_code_refactor(stats, staged_diff),
            "is_bug_fix": self._is_bug_fix(staged_diff),
            "is_feature_addition": self._is_feature_addition(stats, staged_diff),
            "is_performance_improvement": self._is_performance_improvement(staged_diff),
            "is_style_change": self._is_style_change(staged_diff),
            "has_version_bump": bool(self._extract_version_changes(staged_diff)),
            "has_color_changes": bool(self._extract_color_changes(staged_diff)),
            "has_function_changes": bool(self._extract_function_changes(staged_diff)),
            "file_count": len(staged_files),
            "insertions": stats.get("insertions", 0),
            "deletions": stats.get("deletions", 0),
        }
        
        return context
    
    def _is_code_refactor(self, stats: Dict[str, int], diff: str) -> bool:
        """Check if changes indicate a code refactor."""
        # Look for refactor-related keywords
        refactor_keywords = ["refactor", "cleanup", "restructure", "reorganize", "simplify", "extract"]
        diff_lower = diff.lower()
        
        if any(keyword in diff_lower for keyword in refactor_keywords):
            return True
        
        # Check if deletions are significant (refactoring often involves removing code)
        deletions = stats.get("deletions", 0)
        insertions = stats.get("insertions", 0)
        
        if deletions > 20 and abs(insertions - deletions) < deletions * 0.5:
            return True
        
        return False
    
    def _is_bug_fix(self, diff: str) -> bool:
        """Check if changes indicate a bug fix."""
        bug_keywords = ["fix", "bug", "issue", "error", "exception", "crash", "fail", "broken", "wrong"]
        diff_lower = diff.lower()
        
        return any(keyword in diff_lower for keyword in bug_keywords)
    
    def _is_feature_addition(self, stats: Dict[str, int], diff: str) -> bool:
        """Check if changes indicate a feature addition."""
        feature_keywords = ["add", "new", "implement", "create", "introduce", "feature", "functionality"]
        diff_lower = diff.lower()
        
        # Check for feature keywords
        if any(keyword in diff_lower for keyword in feature_keywords):
            return True
        
        # Check if additions are significant
        insertions = stats.get("insertions", 0)
        deletions = stats.get("deletions", 0)
        
        if insertions > deletions * 2 and insertions > 30:
            return True
        
        return False
    
    def _is_performance_improvement(self, diff: str) -> bool:
        """Check if changes indicate performance improvements."""
        perf_keywords = ["performance", "optimize", "speed", "fast", "efficient", "cache", "memory"]
        diff_lower = diff.lower()
        
        return any(keyword in diff_lower for keyword in perf_keywords)
    
    def _is_style_change(self, diff: str) -> bool:
        """Check if changes indicate style changes."""
        style_keywords = ["style", "format", "indent", "whitespace", "lint", "prettier", "beautify"]
        diff_lower = diff.lower()
        
        return any(keyword in diff_lower for keyword in style_keywords)
    
    def _determine_impact_level(self, stats: Dict[str, int], staged_files: List[str], file_types: Dict[str, List[str]]) -> str:
        """Determine the impact level of the changes."""
        insertions = stats.get("insertions", 0)
        deletions = stats.get("deletions", 0)
        file_count = len(staged_files)
        
        # High impact indicators
        if insertions + deletions > 500:
            return "high"
        if file_count > 10:
            return "high"
        if file_types.get("config") and file_count > 3:
            return "high"
        
        # Medium impact indicators
        if insertions + deletions > 100:
            return "medium"
        if file_count > 3:
            return "medium"
        if file_types.get("code") and insertions > 50:
            return "medium"
        
        # Low impact
        return "low"
    
    def get_analysis_summary(self, analysis: GitAnalysis) -> Dict[str, Any]:
        """Get a summary of the analysis for display."""
        return {
            "branch": analysis.branch_name,
            "files": len(analysis.staged_files),
            "file_types": list(analysis.file_types.keys()),
            "changes": analysis.change_summary,
            "todos": len(analysis.todos),
            "fixes": len(analysis.fixes),
            "bugs": len(analysis.bugs),
            "version_changes": len(analysis.version_changes),
            "function_changes": len(analysis.function_changes),
            "color_changes": len(analysis.color_changes),
            "config_changes": len(analysis.config_changes),
            "scope_suggestions": analysis.scope_suggestions[:3],  # Top 3 suggestions
            "impact_level": analysis.impact_level,
        } 