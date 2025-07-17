"""
Display management for lazygit-ai.

Handles rich terminal output, user interface elements, and clipboard operations.
"""

import pyperclip
from typing import List

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn

from ..core.analyzer import GitAnalysis
from ..utils.config import ConfigManager


class DisplayManager:
    """Manages display output for lazygit-ai."""
    
    def __init__(self, console: Console, verbose: bool = False) -> None:
        """Initialize display manager."""
        self.console = console
        self.verbose = verbose
        self.config = ConfigManager()
    
    def show_analysis_start(self, staged_files: List[str]) -> None:
        """Show analysis start message."""
        self.console.print("\n[blue]🔍 Analyzing staged files...[/blue]")
        
        if self.verbose:
            self.console.print(f"[dim]Found {len(staged_files)} staged files[/dim]")
    
    def show_ai_enhancement(self) -> None:
        """Show AI enhancement start message."""
        self.console.print("[yellow]🤖 Enhancing with AI...[/yellow]")
    
    def show_ai_enhancement_success(self) -> None:
        """Show AI enhancement success message."""
        self.console.print("[green]✨ AI enhancement applied![/green]")
    
    def show_commit_message(self, message: str, analysis: GitAnalysis) -> None:
        """Display the generated commit message."""
        self.console.print("\n[bold blue]💡 Suggested commit message:[/bold blue]")
        
        # Create a panel for the commit message
        panel = Panel(
            message,
            border_style="green",
            padding=(1, 2),
            title="[bold]Commit Message[/bold]",
            title_align="left"
        )
        self.console.print(panel)
        
        # Show analysis summary
        self._show_analysis_summary(analysis)
    
    def _show_analysis_summary(self, analysis: GitAnalysis) -> None:
        """Show analysis summary."""
        if not self.verbose:
            return
        
        table = Table(title="[bold]Analysis Summary[/bold]", show_header=False)
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="white")
        
        table.add_row("Branch", analysis.branch_name)
        table.add_row("Files", str(len(analysis.staged_files)))
        table.add_row("Changes", analysis.change_summary)
        
        if analysis.file_types:
            file_types_str = ", ".join([f"{k}: {len(v)}" for k, v in analysis.file_types.items() if v])
            table.add_row("File Types", file_types_str)
        
        if analysis.todos:
            table.add_row("TODOs", str(len(analysis.todos)))
        
        if analysis.fixes:
            table.add_row("Fixes", str(len(analysis.fixes)))
        
        if analysis.bugs:
            table.add_row("Bugs", str(len(analysis.bugs)))
        
        if analysis.scope_suggestions:
            scope_str = ", ".join(analysis.scope_suggestions[:3])
            table.add_row("Scope Suggestions", scope_str)
        
        self.console.print(table)
    
    def show_dry_run(self, message: str, staged_files: List[str]) -> None:
        """Show dry run information."""
        self.console.print("\n[bold yellow]🔍 Dry Run Mode[/bold yellow]")
        self.console.print(f"[dim]Would commit with message:[/dim]")
        
        panel = Panel(
            message,
            border_style="yellow",
            padding=(1, 2),
            title="[bold]Commit Message[/bold]",
            title_align="left"
        )
        self.console.print(panel)
        
        self.console.print(f"\n[dim]Files that would be committed:[/dim]")
        for file_path in staged_files:
            self.console.print(f"  [code]{file_path}[/code]")
    
    def copy_to_clipboard(self, message: str) -> bool:
        """Copy message to clipboard."""
        try:
            pyperclip.copy(message)
            return True
        except Exception as e:
            if self.verbose:
                self.console.print(f"[red]Failed to copy to clipboard: {e}[/red]")
            return False
    
    def show_interactive_prompt(self) -> None:
        """Show interactive prompt for user action."""
        self.console.print("\n[bold]Choose an action:[/bold]")
        self.console.print("  [green][✔] Accept[/green]     [yellow][e] Edit[/yellow]     [blue][c] Copy[/blue]     [red][q] Quit[/red]")
    
    def show_edit_prompt(self) -> str:
        """Show edit prompt and get user input."""
        self.console.print("\n[bold yellow]📝 Edit commit message:[/bold yellow]")
        self.console.print("[dim]Enter your commit message (or press Enter to keep current):[/dim]")
        
        try:
            return input("> ").strip()
        except KeyboardInterrupt:
            return ""
    
    def show_error(self, message: str) -> None:
        """Show error message."""
        self.console.print(f"\n[red]❌ Error: {message}[/red]")
    
    def show_warning(self, message: str) -> None:
        """Show warning message."""
        self.console.print(f"\n[yellow]⚠️  Warning: {message}[/yellow]")
    
    def show_success(self, message: str) -> None:
        """Show success message."""
        self.console.print(f"\n[green]✅ {message}[/green]")
    
    def show_info(self, message: str) -> None:
        """Show info message."""
        self.console.print(f"\n[blue]ℹ️  {message}[/blue]")
    
    def show_loading(self, message: str) -> None:
        """Show loading spinner."""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
            transient=True,
        ) as progress:
            task = progress.add_task(message, total=None)
            progress.update(task, advance=0)
    
    def show_diff_preview(self, diff: str, max_lines: int = 20) -> None:
        """Show a preview of the git diff."""
        if not diff or not self.verbose:
            return
        
        self.console.print("\n[bold]📄 Diff Preview:[/bold]")
        
        lines = diff.split("\n")
        if len(lines) > max_lines:
            lines = lines[:max_lines]
            lines.append("... (truncated)")
        
        # Create a code block
        diff_text = "\n".join(lines)
        panel = Panel(
            diff_text,
            border_style="dim",
            padding=(0, 1),
            title="[dim]Git Diff[/dim]",
            title_align="left"
        )
        self.console.print(panel)
    
    def show_file_analysis(self, analysis: GitAnalysis) -> None:
        """Show detailed file analysis."""
        if not self.verbose:
            return
        
        self.console.print("\n[bold]📂 File Analysis:[/bold]")
        
        table = Table(title="[bold]Staged Files[/bold]")
        table.add_column("File", style="cyan")
        table.add_column("Type", style="green")
        table.add_column("Status", style="yellow")
        
        for file_path in analysis.staged_files:
            # Determine file type
            file_type = "other"
            for type_name, files in analysis.file_types.items():
                if file_path in files:
                    file_type = type_name
                    break
            
            # Determine status (simplified)
            status = "modified"
            if file_path in analysis.staged_files:
                status = "staged"
            
            table.add_row(file_path, file_type, status)
        
        self.console.print(table)
    
    def show_branch_info(self, analysis: GitAnalysis) -> None:
        """Show branch information."""
        self.console.print(f"\n[blue]🌿 Branch:[/blue] {analysis.branch_name}")
        
        if analysis.branch_type and analysis.branch_scope:
            self.console.print(f"[dim]Type: {analysis.branch_type}, Scope: {analysis.branch_scope}[/dim]")
    
    def show_patterns_found(self, analysis: GitAnalysis) -> None:
        """Show patterns found in the diff."""
        if not self.verbose:
            return
        
        patterns = []
        
        if analysis.todos:
            patterns.append(f"TODOs: {len(analysis.todos)}")
        
        if analysis.fixes:
            patterns.append(f"Fixes: {len(analysis.fixes)}")
        
        if analysis.bugs:
            patterns.append(f"Bugs: {len(analysis.bugs)}")
        
        if patterns:
            self.console.print(f"\n[bold]🔍 Patterns Found:[/bold] {', '.join(patterns)}")
            
            # Show first few patterns
            if analysis.todos:
                self.console.print(f"[dim]First TODO: {analysis.todos[0][:50]}...[/dim]")
    
    def show_commit_stats(self, analysis: GitAnalysis) -> None:
        """Show commit statistics."""
        if not self.verbose:
            return
        
        stats = analysis.stats
        if stats:
            self.console.print(f"\n[bold]📊 Statistics:[/bold]")
            self.console.print(f"[dim]Files: {stats.get('files', 0)}, "
                             f"Insertions: {stats.get('insertions', 0)}, "
                             f"Deletions: {stats.get('deletions', 0)}[/dim]")
    
    def show_help_text(self) -> None:
        """Show help text for the tool."""
        help_text = """
[bold]lazygit-ai Help[/bold]

[bold]Commands:[/bold]
  lazygit-ai commit          - Generate commit message for staged changes
  lazygit-ai install-shortcut - Install LazyGit integration
  lazygit-ai config          - Manage configuration
  lazygit-ai --help          - Show this help

[bold]Options:[/bold]
  --no-ai                    - Skip AI enhancement
  --copy                     - Copy to clipboard only
  --dry-run                  - Show what would be committed
  --verbose                  - Show detailed output

[bold]LazyGit Integration:[/bold]
  1. Install shortcut: lazygit-ai install-shortcut
  2. In LazyGit, press 'C' in Files context
  3. Review and edit the generated message
  4. Accept to commit or copy to clipboard

[bold]Configuration:[/bold]
  Config file: ~/.config/lazygit-ai/config.toml
  Edit config: lazygit-ai config --edit
  Show config: lazygit-ai config --show
"""
        self.console.print(help_text)
    
    def show_version_info(self) -> None:
        """Show version information."""
        from .. import __version__
        
        version_text = f"""
[bold blue]lazygit-ai v{__version__}[/bold blue]

[dim]AI-powered commit message generator for LazyGit[/dim]

[bold]Features:[/bold]
  • Rule-based commit message generation
  • AI enhancement with OpenAI/Claude/Ollama
  • LazyGit integration
  • Conventional commit support
  • Offline-first design

[bold]Links:[/bold]
  • GitHub: https://github.com/yourusername/lazygit-ai
  • Documentation: https://github.com/yourusername/lazygit-ai#readme
"""
        self.console.print(version_text) 