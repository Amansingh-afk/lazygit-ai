"""
Git analysis module for lazygit-ai.

Analyzes git state including staged changes, branch information, and file types
to provide context for commit message generation.
"""

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Set

from ..utils.git import GitWrapper


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


class GitAnalyzer:
    """Analyzes git state for commit message generation."""
    
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
        
        # Get diffs
        staged_diff = self.git.get_staged_diff()
        unstaged_diff = self.git.get_unstaged_diff()
        
        # Get statistics
        stats = self.git.get_commit_stats()
        
        # Analyze patterns in diffs
        todos = self._extract_todos(staged_diff)
        fixes = self._extract_fixes(staged_diff)
        bugs = self._extract_bugs(staged_diff)
        
        # Analyze branch
        branch_type, branch_scope = self._analyze_branch(branch_name)
        
        # Get context
        recent_commits = self.git.get_recent_commits(5)
        remote_url = self.git.get_remote_url()
        
        # Derive additional information
        primary_file_type = self._get_primary_file_type(file_types)
        change_summary = self._generate_change_summary(staged_files, stats, file_types)
        scope_suggestions = self._generate_scope_suggestions(staged_files, branch_scope, file_types)
        
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
            branch_type=branch_type,
            branch_scope=branch_scope,
            recent_commits=recent_commits,
            remote_url=remote_url,
            primary_file_type=primary_file_type,
            change_summary=change_summary,
            scope_suggestions=scope_suggestions,
        )
    
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
        """Extract TODO comments from diff."""
        todos = []
        patterns = [
            r"//\s*TODO[:\s]*(.+)",
            r"#\s*TODO[:\s]*(.+)",
            r"/\*\s*TODO[:\s]*(.+?)\*/",
            r"<!--\s*TODO[:\s]*(.+?)-->",
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, diff, re.IGNORECASE | re.MULTILINE)
            todos.extend([match.strip() for match in matches])
        
        return todos
    
    def _extract_fixes(self, diff: str) -> List[str]:
        """Extract FIX comments from diff."""
        fixes = []
        patterns = [
            r"//\s*FIX[:\s]*(.+)",
            r"#\s*FIX[:\s]*(.+)",
            r"/\*\s*FIX[:\s]*(.+?)\*/",
            r"<!--\s*FIX[:\s]*(.+?)-->",
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, diff, re.IGNORECASE | re.MULTILINE)
            fixes.extend([match.strip() for match in matches])
        
        return fixes
    
    def _extract_bugs(self, diff: str) -> List[str]:
        """Extract BUG comments from diff."""
        bugs = []
        patterns = [
            r"//\s*BUG[:\s]*(.+)",
            r"#\s*BUG[:\s]*(.+)",
            r"/\*\s*BUG[:\s]*(.+?)\*/",
            r"<!--\s*BUG[:\s]*(.+?)-->",
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, diff, re.IGNORECASE | re.MULTILINE)
            bugs.extend([match.strip() for match in matches])
        
        return bugs
    
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
        
        return sorted(list(suggestions))
    
    def get_analysis_summary(self, analysis: GitAnalysis) -> Dict[str, any]:
        """Get a summary of the analysis for display."""
        return {
            "branch": analysis.branch_name,
            "files": len(analysis.staged_files),
            "file_types": list(analysis.file_types.keys()),
            "changes": analysis.change_summary,
            "todos": len(analysis.todos),
            "fixes": len(analysis.fixes),
            "bugs": len(analysis.bugs),
            "scope_suggestions": analysis.scope_suggestions[:3],  # Top 3 suggestions
        } # BUG: handle edge case when no staged files
