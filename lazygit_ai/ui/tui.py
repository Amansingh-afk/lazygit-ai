"""
Simple TUI for lazygit-ai.

Provides a clean, LazyGit-style interface for commit message editing.
"""

import pyperclip
import sys
import os
from typing import Optional

from rich.console import Console, Group
from rich.text import Text
from rich.panel import Panel
from rich.prompt import Prompt
from rich.columns import Columns

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
    
    def _clear_terminal(self) -> None:
        """Clear the terminal screen."""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def _get_main_panel(self) -> Panel:
        """Create the main panel that wraps the entire interface as a Group of Rich objects."""
        # Suggested commit message panel
        message_panel = Panel(
            self.message,
            title="[bold cyan]Suggested commit message[/bold cyan]",
            border_style="cyan",
            padding=(1, 2)
        )
        # Git info
        info_lines = [
            f"[yellow]Branch:[/yellow] [white]{self.analysis.branch_name}[/white]",
            f"[yellow]Files:[/yellow] [white]{len(self.analysis.staged_files)}[/white]",
            f"[yellow]Changes:[/yellow] [white]{self.analysis.change_summary}[/white]",
            ""
        ]
        info_group = Group(*(Text.from_markup(line) for line in info_lines))
        # Actions
        actions = [
            ("[bold green]✓ Accept[/bold green]", "a"),
            ("[bold yellow]✎ Edit[/bold yellow]", "e"), 
            ("[bold blue]📋 Copy[/bold blue]", "c"),
            ("[bold red]✗ Quit[/bold red]", "q")
        ]
        action_texts = [f"  {action_text}" for action_text, key in actions]
        # Shortcuts
        shortcuts_text = "[dim]a to accept, e to edit, c to copy, q to quit[/dim]"
        # Compose all content as a Group
        group = Group(
            message_panel,
            info_group,
            Text.from_markup(shortcuts_text),
            Text("")
        )
        return Panel(
            group,
            title="[bold blue]🚀 lazygit-ai - Commit Message Editor[/bold blue]",
            border_style="blue",
            padding=(1, 2),
            expand=True
        )
    
    def run(self) -> None:
        """Run the simple TUI."""
        self._clear_terminal()
        self.console.print(self._get_main_panel())
        
        while True:
            try:
                choice = Prompt.ask(
                    "[bold cyan]Action[/bold cyan]",
                    choices=["a", "e", "c", "q"],
                    default="e",  # Default to edit
                    show_choices=False  # Don't show choices since we display them above
                )
                
                if choice == "a":
                    success = self.git_wrapper.commit(self.message)
                    if success:
                        self._clear_terminal()
                        self.console.print("[bold green]✅ Commit created successfully![/bold green]")
                        sys.exit(0)
                    else:
                        self.console.print("[bold red]❌ Failed to create commit[/bold red]")
                
                elif choice == "e":
                    self._clear_terminal()
                    self.console.print(self._get_main_panel())
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
                    self._clear_terminal()
                    self.console.print(self._get_main_panel())
                
                elif choice == "c":
                    try:
                        pyperclip.copy(self.message)
                        self.console.print("[bold green]📋 Message copied to clipboard![/bold green]")
                    except Exception as e:
                        self.console.print(f"[bold red]❌ Failed to copy to clipboard: {e}[/bold red]")
                
                elif choice == "q":
                    self._clear_terminal()
                    self.console.print("[yellow]👋 Exiting without committing[/yellow]")
                    sys.exit(1)
                    
            except KeyboardInterrupt:
                self._clear_terminal()
                self.console.print("[yellow]👋 Exiting without committing[/yellow]")
                sys.exit(1)
            except EOFError:
                self._clear_terminal()
                self.console.print("[yellow]👋 Exiting without committing[/yellow]")
                sys.exit(1)


class CommitTUI(SimpleCommitTUI):
    """Alias for backward compatibility."""
    pass 