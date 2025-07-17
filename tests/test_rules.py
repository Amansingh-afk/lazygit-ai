"""
Tests for the rule-based commit message generator.

Tests the RuleEngine class and its various methods for generating
commit messages based on git analysis.
"""

import pytest
from unittest.mock import Mock, patch

from lazygit_ai.core.rules import RuleEngine
from lazygit_ai.core.analyzer import GitAnalysis
from lazygit_ai.utils.config import ConfigManager


class TestRuleEngine:
    """Test cases for RuleEngine class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = ConfigManager()
        self.engine = RuleEngine(self.config)
    
    def test_determine_commit_type_from_branch(self):
        """Test commit type determination from branch name."""
        analysis = Mock(spec=GitAnalysis)
        analysis.branch_type = "feat"
        analysis.branch_scope = "auth"
        analysis.fixes = []
        analysis.bugs = []
        analysis.file_types = {}
        analysis.staged_files = []
        analysis.staged_diff = ""
        
        commit_type = self.engine._determine_commit_type(analysis)
        assert commit_type == "feat"
    
    def test_determine_commit_type_from_fixes(self):
        """Test commit type determination from fix comments."""
        analysis = Mock(spec=GitAnalysis)
        analysis.branch_type = None
        analysis.fixes = ["fix login issue"]
        analysis.bugs = []
        analysis.file_types = {}
        analysis.staged_files = []
        analysis.staged_diff = ""
        
        commit_type = self.engine._determine_commit_type(analysis)
        assert commit_type == "fix"
    
    def test_determine_commit_type_from_file_types(self):
        """Test commit type determination from file types."""
        analysis = Mock(spec=GitAnalysis)
        analysis.branch_type = None
        analysis.fixes = []
        analysis.bugs = []
        analysis.file_types = {"tests": ["test_auth.py"]}
        analysis.staged_files = ["test_auth.py"]
        analysis.staged_diff = ""
        
        commit_type = self.engine._determine_commit_type(analysis)
        assert commit_type == "test"
    
    def test_normalize_commit_type(self):
        """Test commit type normalization."""
        assert self.engine._normalize_commit_type("feat") == "feat"
        assert self.engine._normalize_commit_type("feature") == "feat"
        assert self.engine._normalize_commit_type("fix") == "fix"
        assert self.engine._normalize_commit_type("bugfix") == "fix"
        assert self.engine._normalize_commit_type("docs") == "docs"
        assert self.engine._normalize_commit_type("unknown") == "feat"
    
    def test_determine_scope_from_branch(self):
        """Test scope determination from branch scope."""
        analysis = Mock(spec=GitAnalysis)
        analysis.branch_scope = "auth"
        analysis.scope_suggestions = []
        analysis.staged_files = []
        
        scope = self.engine._determine_scope(analysis)
        assert scope == "auth"
    
    def test_determine_scope_from_suggestions(self):
        """Test scope determination from scope suggestions."""
        analysis = Mock(spec=GitAnalysis)
        analysis.branch_scope = None
        analysis.scope_suggestions = ["auth", "ui"]
        analysis.staged_files = []
        
        scope = self.engine._determine_scope(analysis)
        assert scope == "auth"
    
    def test_format_scope_lowercase(self):
        """Test scope formatting in lowercase style."""
        self.engine.commit_config["scope_style"] = "lowercase"
        
        assert self.engine._format_scope("Auth") == "auth"
        assert self.engine._format_scope("USER_AUTH") == "user_auth"
        assert self.engine._format_scope("Login Flow") == "login flow"
    
    def test_format_scope_kebab_case(self):
        """Test scope formatting in kebab-case style."""
        self.engine.commit_config["scope_style"] = "kebab-case"
        
        assert self.engine._format_scope("Auth") == "auth"
        assert self.engine._format_scope("USER_AUTH") == "user-auth"
        assert self.engine._format_scope("Login Flow") == "login-flow"
    
    def test_generate_description_from_todo(self):
        """Test description generation from TODO comments."""
        analysis = Mock(spec=GitAnalysis)
        analysis.todos = ["TODO: implement user authentication"]
        analysis.fixes = []
        analysis.bugs = []
        
        description = self.engine._generate_description(analysis)
        assert "implement user authentication" in description
    
    def test_generate_description_from_fix(self):
        """Test description generation from FIX comments."""
        analysis = Mock(spec=GitAnalysis)
        analysis.todos = []
        analysis.fixes = ["FIX: resolve login bug"]
        analysis.bugs = []
        
        description = self.engine._generate_description(analysis)
        assert "resolve login bug" in description
    
    def test_clean_description(self):
        """Test description cleaning and formatting."""
        dirty_text = "  TODO:   implement   user   auth   "
        cleaned = self.engine._clean_description(dirty_text)
        assert cleaned == "implement user auth"
    
    def test_ensure_verb_start(self):
        """Test ensuring description starts with a verb."""
        # Already starts with verb
        text = "add user authentication"
        result = self.engine._ensure_verb_start(text)
        assert result == text
        
        # Doesn't start with verb
        text = "user authentication feature"
        result = self.engine._ensure_verb_start(text)
        assert result.startswith("update")
    
    def test_format_conventional(self):
        """Test conventional commit formatting."""
        # With scope
        result = self.engine._format_conventional("feat", "auth", "add login")
        assert result == "feat(auth): add login"
        
        # Without scope
        result = self.engine._format_conventional("fix", None, "fix bug")
        assert result == "fix: fix bug"
    
    def test_validate_message(self):
        """Test commit message validation."""
        # Valid message
        assert self.engine.validate_message("feat: add new feature")
        
        # Empty message
        assert not self.engine.validate_message("")
        assert not self.engine.validate_message("   ")
        
        # Too long message
        long_message = "feat: " + "a" * 100
        assert not self.engine.validate_message(long_message)
    
    def test_suggest_improvements(self):
        """Test improvement suggestions."""
        # Message too long
        long_message = "feat: " + "a" * 100
        suggestions = self.engine.suggest_improvements(long_message)
        assert any("too long" in suggestion for suggestion in suggestions)
        
        # Message with "update"
        suggestions = self.engine.suggest_improvements("update something")
        assert any("specific verb" in suggestion for suggestion in suggestions)
        
        # Message ending with period
        suggestions = self.engine.suggest_improvements("feat: add feature.")
        assert any("period" in suggestion for suggestion in suggestions)
    
    def test_is_imperative(self):
        """Test imperative mood detection."""
        # Imperative verbs
        assert self.engine._is_imperative("feat: add feature")
        assert self.engine._is_imperative("fix: resolve bug")
        assert self.engine._is_imperative("docs: update readme")
        
        # Non-imperative
        assert not self.engine._is_imperative("feat: added feature")
        assert not self.engine._is_imperative("fix: fixing bug")
    
    def test_generate_message_integration(self):
        """Test full message generation integration."""
        analysis = Mock(spec=GitAnalysis)
        analysis.branch_type = "feat"
        analysis.branch_scope = "auth"
        analysis.todos = ["TODO: implement login validation"]
        analysis.fixes = []
        analysis.bugs = []
        analysis.file_types = {"code": ["auth.py"]}
        analysis.staged_files = ["auth.py"]
        analysis.staged_diff = ""
        
        message = self.engine.generate_message(analysis)
        assert message.startswith("feat(auth):")
        assert "login validation" in message
    
    def test_generate_message_without_scope(self):
        """Test message generation without scope."""
        self.engine.commit_config["include_scope"] = False
        
        analysis = Mock(spec=GitAnalysis)
        analysis.branch_type = "fix"
        analysis.branch_scope = "auth"
        analysis.todos = []
        analysis.fixes = ["FIX: resolve login issue"]
        analysis.bugs = []
        analysis.file_types = {}
        analysis.staged_files = []
        analysis.staged_diff = ""
        
        message = self.engine.generate_message(analysis)
        assert message.startswith("fix:")
        assert "(" not in message  # No scope
    
    def test_generate_message_non_conventional(self):
        """Test message generation without conventional format."""
        self.engine.commit_config["conventional"] = False
        
        analysis = Mock(spec=GitAnalysis)
        analysis.branch_type = "feat"
        analysis.branch_scope = "auth"
        analysis.todos = ["TODO: add login"]
        analysis.fixes = []
        analysis.bugs = []
        analysis.file_types = {}
        analysis.staged_files = []
        analysis.staged_diff = ""
        
        message = self.engine.generate_message(analysis)
        assert not message.startswith("feat(")
        assert "add login" in message 