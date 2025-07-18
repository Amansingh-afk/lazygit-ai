"""
Git wrapper utilities for lazygit-ai.

Provides a clean interface for Git operations including diff analysis,
branch information, and staged file management.
"""

import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import git
from git import Repo


class GitWrapper:
    """Wrapper for Git operations used by lazygit-ai."""
    
    def __init__(self, repo_path: Optional[Path] = None) -> None:
        """
        Initialize Git wrapper.
        
        Args:
            repo_path: Path to git repository. If None, uses current directory.
        """
        self.repo_path = repo_path or Path.cwd()
        self._repo: Optional[Repo] = None
    
    @property
    def repo(self) -> Repo:
        """Get GitPython Repo object, initializing if needed."""
        if self._repo is None:
            self._repo = Repo(self.repo_path)
        return self._repo
    
    def is_git_repo(self) -> bool:
        """Check if current directory is a git repository."""
        try:
            return self.repo.git_dir is not None
        except git.InvalidGitRepositoryError:
            return False
    
    def get_current_branch(self) -> str:
        """Get the name of the current branch."""
        try:
            return self.repo.active_branch.name
        except (TypeError, AttributeError):
            # Handle detached HEAD state
            return self.repo.head.object.hexsha[:8]
    
    def get_staged_files(self) -> List[str]:
        """Get list of staged files."""
        try:
            # Get staged files using git status
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                cwd=self.repo_path,
                check=True,
            )
            
            staged_files = []
            for line in result.stdout.split("\n"):
                if line and len(line) >= 2:
                    # Check if file is staged: first char is A/M/D/R (not space)
                    # Second char can be anything (unstaged status)
                    if line[0] in "AMDR":
                        # Handle different prefix lengths:
                        # "M README.md" -> prefix is 2 chars ("M ")
                        # "M  README.md" -> prefix is 3 chars ("M  ")
                        if len(line) >= 3 and line[1] == " " and line[2] == " ":
                            file_path = line[3:].strip()  # Remove 3-char prefix
                        else:
                            file_path = line[2:].strip()  # Remove 2-char prefix
                        staged_files.append(file_path)
            
            return staged_files
        except subprocess.CalledProcessError:
            return []
    
    def get_staged_diff(self) -> str:
        """Get the diff of staged changes."""
        try:
            result = subprocess.run(
                ["git", "diff", "--cached", "--no-color"],
                capture_output=True,
                text=True,
                cwd=self.repo_path,
                check=True,
            )
            return result.stdout
        except subprocess.CalledProcessError:
            return ""
    
    def get_unstaged_diff(self) -> str:
        """Get the diff of unstaged changes."""
        try:
            result = subprocess.run(
                ["git", "diff", "--no-color"],
                capture_output=True,
                text=True,
                cwd=self.repo_path,
                check=True,
            )
            return result.stdout
        except subprocess.CalledProcessError:
            return ""
    
    def get_file_extensions(self, files: List[str]) -> List[str]:
        """Get unique file extensions from a list of files."""
        extensions = set()
        for file_path in files:
            path = Path(file_path)
            if path.suffix:
                extensions.add(path.suffix.lower())
        return sorted(list(extensions))
    
    def get_file_types(self, files: List[str]) -> Dict[str, List[str]]:
        """Categorize files by type."""
        categories = {
            "code": [],
            "docs": [],
            "tests": [],
            "config": [],
            "assets": [],
            "other": [],
        }
        
        for file_path in files:
            path = Path(file_path)
            suffix = path.suffix.lower()
            
            # Code files
            if suffix in {".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".c", ".cpp", ".h", ".hpp", ".go", ".rs", ".php", ".rb", ".swift", ".kt", ".scala"}:
                categories["code"].append(file_path)
            # Documentation
            elif suffix in {".md", ".txt", ".rst", ".adoc", ".tex"}:
                categories["docs"].append(file_path)
            elif "test" in path.name.lower() or suffix in {".test.js", ".test.ts", ".spec.js", ".spec.ts", "_test.py", "test_"}:
                categories["tests"].append(file_path)
            elif suffix in {".json", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".conf", ".env"}:
                categories["config"].append(file_path)
            # Assets
            elif suffix in {".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".css", ".scss", ".sass", ".less"}:
                categories["assets"].append(file_path)
            else:
                categories["other"].append(file_path)
        
        return categories
    
    def get_commit_stats(self) -> Dict[str, int]:
        """Get statistics about staged changes."""
        try:
            result = subprocess.run(
                ["git", "diff", "--cached", "--stat"],
                capture_output=True,
                text=True,
                cwd=self.repo_path,
                check=True,
            )
            
            # Parse the last line which contains summary
            lines = result.stdout.strip().split("\n")
            if not lines:
                return {"files": 0, "insertions": 0, "deletions": 0}
            
            # Find the summary line (usually the last line)
            summary_line = lines[-1]
            
            # Extract numbers using regex-like parsing
            import re
            pattern = r"(\d+) files? changed(?:, (\d+) insertions?\(\+\))?(?:, (\d+) deletions?\(-\))?"
            match = re.search(pattern, summary_line)
            
            if match:
                files = int(match.group(1))
                insertions = int(match.group(2)) if match.group(2) else 0
                deletions = int(match.group(3)) if match.group(3) else 0
                return {
                    "files": files,
                    "insertions": insertions,
                    "deletions": deletions,
                }
            
            return {"files": 0, "insertions": 0, "deletions": 0}
            
        except subprocess.CalledProcessError:
            return {"files": 0, "insertions": 0, "deletions": 0}
    
    def get_recent_commits(self, count: int = 5) -> List[Dict[str, str]]:
        """Get recent commit history."""
        try:
            result = subprocess.run(
                ["git", "log", f"-{count}", "--oneline", "--no-merges"],
                capture_output=True,
                text=True,
                cwd=self.repo_path,
                check=True,
            )
            
            commits = []
            for line in result.stdout.strip().split("\n"):
                if line:
                    parts = line.split(" ", 1)
                    if len(parts) == 2:
                        commits.append({
                            "hash": parts[0],
                            "message": parts[1]
                        })
            
            return commits
        except subprocess.CalledProcessError:
            return []
    
    def get_remote_url(self) -> Optional[str]:
        """Get the remote URL of the repository."""
        try:
            result = subprocess.run(
                ["git", "config", "--get", "remote.origin.url"],
                capture_output=True,
                text=True,
                cwd=self.repo_path,
                check=True,
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return None
    
    def is_clean_working_directory(self) -> bool:
        """Check if working directory is clean (no unstaged changes)."""
        try:
            result = subprocess.run(
                ["git", "diff", "--quiet"],
                capture_output=True,
                cwd=self.repo_path,
                check=False,
            )
            return result.returncode == 0
        except subprocess.CalledProcessError:
            return False
    
    def commit(self, message: str) -> bool:
        """Create a commit with the given message."""
        try:
            staged_files = self.get_staged_files()
            if not staged_files:
                return False
            
            result = subprocess.run(
                ["git", "commit", "-m", message],
                capture_output=True,
                text=True,
                cwd=self.repo_path,
                check=False,
            )
            
            if result.returncode == 0:
                return True
            else:
                return False
                
        except Exception as e:
            return False
    
    def get_branch_info(self) -> Dict[str, str]:
        """Get comprehensive branch information."""
        try:
            current_branch = self.get_current_branch()
            remote_url = self.get_remote_url()
            
            # Check if branch exists on remote
            has_remote = False
            if remote_url:
                try:
                    result = subprocess.run(
                        ["git", "ls-remote", "--heads", "origin", current_branch],
                        capture_output=True,
                        text=True,
                        cwd=self.repo_path,
                        check=True,
                    )
                    has_remote = bool(result.stdout.strip())
                except subprocess.CalledProcessError:
                    pass
            
            return {
                "name": current_branch,
                "remote_url": remote_url or "",
                "has_remote": has_remote,
            }
        except Exception:
            return {
                "name": "unknown",
                "remote_url": "",
                "has_remote": False,
            } 

    def check_commit_readiness(self) -> Dict[str, any]:
        """Check if the repository is ready for committing and provide guidance."""
        staged_files = self.get_staged_files()
        unstaged_changes = not self.is_clean_working_directory()
        
        status = {
            "ready": len(staged_files) > 0,
            "staged_files": staged_files,
            "unstaged_changes": unstaged_changes,
            "message": ""
        }
        
        if not staged_files:
            if unstaged_changes:
                status["message"] = "❌ No staged files to commit. You have unstaged changes.\n   Use: git add .  or  git add <specific-files>"
            else:
                status["message"] = "❌ No staged files to commit.\n   Use: git add .  or  git add <specific-files>"
        elif unstaged_changes:
            status["message"] = "⚠️  Ready to commit staged files. You also have unstaged changes."
        else:
            status["message"] = "✅ Ready to commit staged files."
            
        return status 