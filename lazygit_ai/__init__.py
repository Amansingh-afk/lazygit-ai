"""
lazygit-ai: AI-powered commit message generator for LazyGit

A Python CLI tool that generates intelligent commit messages using rule-based
analysis and optional AI enhancement, designed to integrate seamlessly with LazyGit.
"""

__version__ = "0.1.0"
__author__ = "lazygit-ai contributors"
__email__ = "hello@lazygit-ai.dev"

from .cli import app

__all__ = ["app"] 