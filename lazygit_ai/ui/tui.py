"""
Simple TUI for lazygit-ai.

Provides a clean, LazyGit-style interface for commit message editing.
"""

import pyperclip
import sys
from typing import Optional

from rich.console import Console
from rich.text import Text
from rich.panel import Panel
from rich.prompt import Prompt

from ..core.analyzer import GitAnalysis
from ..utils.git import GitWrapper


class SimpleCommitTUI:
    """Simple, LazyGit-style TUI for commit message editing."""
    
    def __init__(self, message: str, analysis: GitAnalysis, git_wrapper: GitWrapper) -> None:
        """Initialize simple TUI."""
        self.message = message
        self.analysis = analysis
        self.git_wrapper = git_wrapper
        self.console = Console()
    
    def _display_suggested_message(self) -> None:
        """Display the suggested commit message with colors."""
        message_panel = Panel(
            self.message,
            title="[bold cyan]Suggested commit message[/bold cyan]",
            border_style="cyan",
            padding=(1, 2)
        )
        self.console.print(message_panel)
        self.console.print()
    
    def _display_git_info(self) -> None:
        """Display git information with colors."""
        self.console.print(f"[yellow]Branch:[/yellow] [white]{self.analysis.branch_name}[/white]")
        self.console.print(f"[yellow]Files:[/yellow] [white]{len(self.analysis.staged_files)}[/white]")
        self.console.print(f"[yellow]Changes:[/yellow] [white]{self.analysis.change_summary}[/white]")
        self.console.print()
    
    def _display_actions(self) -> None:
        """Display action choices with colors."""
        self.console.print("[bold yellow]Actions:[/bold yellow]")
        self.console.print("  [cyan][a][/cyan] Accept and commit")
        self.console.print("  [cyan][e][/cyan] Edit message")
        self.console.print("  [cyan][c][/cyan] Copy to clipboard")
        self.console.print("  [cyan][q][/cyan] Quit")
        self.console.print()
    
    def run(self) -> None:
        """Run the simple TUI."""
        self._display_suggested_message()
        self._display_git_info()
        
        while True:
            self._display_actions()
            
            try:
                choice = Prompt.ask(
                    "[bold cyan]Enter choice[/bold cyan]",
                    choices=["a", "e", "c", "q"],
                    default="e"  # Default to edit
                )
                
                if choice == "a":
                    success = self.git_wrapper.commit(self.message)
                    if success:
                        self.console.print("[bold green]✅ Commit created successfully![/bold green]")
                        sys.exit(0)
                    else:
                        self.console.print("[bold red]❌ Failed to create commit[/bold red]")
                
                elif choice == "e":
                    # Clear screen and show editor
                    self.console.clear()
                    self._display_suggested_message()
                    self._display_git_info()
                    
                    self.console.print("[bold cyan]Editing commit message:[/bold cyan]")
                    self.console.print("[dim]Press Enter to keep current message[/dim]")
                    
                    new_message = Prompt.ask(
                        "[bold yellow]Commit message[/bold yellow]",
                        default=self.message
                    )
                    
                    if new_message.strip():
                        self.message = new_message.strip()
                        self.console.print("[bold green]✅ Message updated![/bold green]")
                    else:
                        self.console.print("[yellow]⚠️  Message unchanged[/yellow]")
                    
                    # Clear and redisplay
                    self.console.clear()
                    self._display_suggested_message()
                    self._display_git_info()
                
                elif choice == "c":
                    try:
                        pyperclip.copy(self.message)
                        self.console.print("[bold green]📋 Message copied to clipboard![/bold green]")
                    except Exception as e:
                        self.console.print(f"[bold red]❌ Failed to copy to clipboard: {e}[/bold red]")
                
                elif choice == "q":
                    self.console.print("[yellow]👋 Exiting without committing[/yellow]")
                    sys.exit(1)
                    
            except KeyboardInterrupt:
                self.console.print("\n[yellow]👋 Exiting without committing[/yellow]")
                sys.exit(1)
            except EOFError:
                self.console.print("\n[yellow]👋 Exiting without committing[/yellow]")
                sys.exit(1)


class CommitTUI(SimpleCommitTUI):
    """Alias for backward compatibility."""
    pass 