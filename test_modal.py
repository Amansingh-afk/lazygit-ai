#!/usr/bin/env python3
"""
Test script for the new terminal-based modal TUI.

This demonstrates the modal interface that appears within the current terminal
instead of opening a new window.
"""

import sys
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

from lazygit_ai.ui.modal_tui import TerminalModal
from lazygit_ai.core.analyzer import GitAnalysis


def create_test_analysis():
    """Create a test GitAnalysis."""
    return GitAnalysis(
        branch_name="feature/terminal-modal",
        staged_files=["src/modal.py", "tests/test_modal.py", "README.md"],
        file_extensions=[".py", ".md"],
        commit_patterns=["feat:", "fix:", "docs:"],
        diff_summary="Added terminal-based modal interface",
        total_changes=8,
        additions=6,
        deletions=2
    )


def main():
    """Test the terminal modal."""
    print("Testing Terminal Modal TUI")
    print("=" * 30)
    print("This will show a modal overlay in the current terminal.")
    print("Press Ctrl+S to accept, Ctrl+Q to quit, Ctrl+C to copy")
    print("=" * 30)
    
    # Create test data
    test_message = "feat: add terminal-based modal interface\n\n- Appears within current terminal\n- No new window opened\n- True modal overlay experience\n- Keyboard shortcuts work"
    test_analysis = create_test_analysis()
    
    # Create a mock git wrapper
    class MockGitWrapper:
        def commit(self, message):
            print(f"\n🎉 Would commit: {message}")
    
    git_wrapper = MockGitWrapper()
    
    # Create and run the modal
    modal = TerminalModal(test_message, test_analysis, git_wrapper)
    result = modal.run()
    
    if result:
        print(f"\n✅ Modal completed successfully!")
        print(f"Final message: {result}")
    else:
        print(f"\n❌ Modal was cancelled.")


if __name__ == "__main__":
    main() 