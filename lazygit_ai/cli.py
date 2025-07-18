"""
Main CLI entry point for lazygit-ai.

Provides commands for commit generation, LazyGit integration, and configuration.
"""

import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from .core.analyzer import GitAnalyzer
from .core.rules import RuleEngine
from .core.llm import LLMProvider
from .ui.tui import CommitTUI
from .ui.display import DisplayManager
from .utils.config import ConfigManager
from .utils.git import GitWrapper
from .utils.shortcuts import LazyGitShortcutManager

# Initialize Typer app
app = typer.Typer(
    name="lazygit-ai",
    help="AI-powered commit message generator for LazyGit",
    add_completion=False,
    rich_markup_mode="rich",
)

# Global console for consistent styling
console = Console()

# ASCII art banner
BANNER = """
[bold blue]██╗     █████╗ ███████╗██╗   ██╗ ██████╗ ██╗███████╗████████╗[/bold blue]
[bold blue]██║    ██╔══██╗╚══███╔╝╚██╗ ██╔╝██╔════╝ ██║██╔════╝╚══██╔══╝[/bold blue]
[bold blue]██║    ███████║  ███╔╝  ╚████╔╝ ██║  ███╗██║█████╗     ██║   [/bold blue]
[bold blue]██║    ██╔══██║ ███╔╝    ╚██╔╝  ██║   ██║██║██╔══╝     ██║   [/bold blue]
[bold blue]███████╗██║  ██║███████╗   ██║   ╚██████╔╝██║██║        ██║   [/bold blue]
[bold blue]╚══════╝╚═╝  ╚═╝╚══════╝   ╚═╝    ╚═════╝ ╚═╝╚═╝        ╚═╝   [/bold blue]

[dim]AI-powered commit message generator for LazyGit[/dim]
"""


def show_banner() -> None:
    """Display the lazygit-ai banner."""
    console.print(Panel(BANNER, border_style="blue"))


@app.command()
def commit(
    message: Optional[str] = typer.Option(None, "--message", "-m", help="Custom commit message"),
    no_ai: bool = typer.Option(False, "--no-ai", help="Skip AI enhancement"),
    copy_only: bool = typer.Option(False, "--copy", "-c", help="Copy to clipboard only"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be committed"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
) -> None:
    """
    Generate an intelligent commit message for staged changes.
    
    Analyzes git diff, branch name, and file types to create meaningful
    commit messages. Optionally enhances with AI when rules aren't sufficient.
    """
    try:
        # Initialize components
        config = ConfigManager()
        git_wrapper = GitWrapper()
        display = DisplayManager(console, verbose)
        
        # Check if we're in a git repository
        if not git_wrapper.is_git_repo():
            console.print("[red]❌ Not in a git repository[/red]")
            console.print("Please run this command from within a git repository.")
            raise typer.Exit(1)
        
        # Check commit readiness using the new method
        readiness = git_wrapper.check_commit_readiness()
        if not readiness["ready"]:
            console.print(f"[red]{readiness['message']}[/red]")
            console.print("\n[yellow]Please stage your files first, then run lazygit-ai again.[/yellow]")
            raise typer.Exit(1)
        
        # Get staged files for analysis
        staged_files = readiness["staged_files"]
        
        # Show analysis start
        display.show_analysis_start(staged_files)
        
        # Analyze git state
        analyzer = GitAnalyzer(git_wrapper)
        analysis = analyzer.analyze()
        
        # Generate commit message using rules
        rules_engine = RuleEngine(config)
        rule_message = rules_engine.generate_message(analysis)
        
        # Enhance with AI if enabled and needed
        final_message = rule_message
        if not no_ai and config.ai_enabled():
            llm_provider = LLMProvider(config)
            if llm_provider.is_available():
                display.show_ai_enhancement()
                ai_message = llm_provider.enhance_message(analysis, rule_message)
                if ai_message and ai_message != rule_message:
                    final_message = ai_message
                    display.show_ai_enhancement_success()
        
        # Use custom message if provided
        if message:
            final_message = message
        
        # Handle different output modes
        if copy_only:
            display.show_commit_message(final_message, analysis)
            display.copy_to_clipboard(final_message)
            console.print("[green]✅ Commit message copied to clipboard![/green]")
        elif dry_run:
            display.show_commit_message(final_message, analysis)
            display.show_dry_run(final_message, staged_files)
        else:
            # Launch interactive TUI (no need to display message first)
            tui = CommitTUI(final_message, analysis, git_wrapper)
            tui.run()
            
    except Exception as e:
        if verbose:
            console.print_exception()
        else:
            console.print(f"[red]❌ Error: {str(e)}[/red]")
        raise typer.Exit(1)


@app.command()
def help() -> None:
    """Show detailed help and information about lazygit-ai."""
    show_banner()
    
    help_text = """
[bold]🚀 lazygit-ai: AI-powered commit message generator for LazyGit[/bold]

[bold]Commands:[/bold]
  [cyan]lazygit-ai commit[/cyan]          - Generate commit message for staged changes
  [cyan]lazygit-ai install-shortcut[/cyan] - Install LazyGit integration
  [cyan]lazygit-ai config[/cyan]          - Manage configuration
  [cyan]lazygit-ai help[/cyan]            - Show this help

[bold]Commit Options:[/bold]
  [yellow]--no-ai[/yellow]                    - Skip AI enhancement (rule-based only)
  [yellow]--copy[/yellow]                     - Copy to clipboard only
  [yellow]--dry-run[/yellow]                  - Show what would be committed
  [yellow]--verbose[/yellow]                  - Show detailed output
  [yellow]--message[/yellow]                  - Use custom commit message

[bold]LazyGit Integration:[/bold]
  1. Install shortcut: [code]lazygit-ai install-shortcut[/code]
  2. In LazyGit, press [code]C[/code] in Files context
  3. Review and edit the generated message
  4. Accept to commit or copy to clipboard

[bold]Configuration:[/bold]
  Config file: [code]~/.config/lazygit-ai/config.toml[/code]
  Edit config: [code]lazygit-ai config --edit[/code]
  Show config: [code]lazygit-ai config --show[/code]

[bold]Examples:[/bold]
  [code]lazygit-ai commit[/code]              - Generate AI-enhanced commit message
  [code]lazygit-ai commit --no-ai[/code]      - Rule-based commit message only
  [code]lazygit-ai commit --copy[/code]       - Copy message to clipboard
  [code]lazygit-ai commit --dry-run[/code]    - Preview without committing

[dim]For more information, visit:[/dim]
[link=https://github.com/yourusername/lazygit-ai]https://github.com/yourusername/lazygit-ai[/link]
"""
    console.print(help_text)


@app.command()
def install_shortcut(
    key: str = typer.Option("C", "--key", "-k", help="Key binding for the shortcut"),
    context: str = typer.Option("files", "--context", "-c", help="LazyGit context for the shortcut"),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing shortcut"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
) -> None:
    """
    Install LazyGit shortcut for AI commit generation.
    
    Adds a custom command to your LazyGit configuration that allows you to
    generate AI-powered commit messages directly from within LazyGit.
    """
    try:
        show_banner()
        
        shortcut_manager = LazyGitShortcutManager()
        
        if not shortcut_manager.is_lazygit_installed():
            console.print("[red]❌ LazyGit not found[/red]")
            console.print("\n[dim]Please install LazyGit first:[/dim]")
            console.print("  [code]https://github.com/jesseduffield/lazygit#installation[/code]")
            raise typer.Exit(1)
        
        console.print(f"[blue]🔧 Installing LazyGit shortcut...[/blue]")
        console.print(f"  Key: [code]{key}[/code]")
        console.print(f"  Context: [code]{context}[/code]")
        
        success = shortcut_manager.install_shortcut(key, context, force)
        
        if success:
            console.print("[green]✅ Shortcut installed successfully![/green]")
            console.print("\n[dim]Usage in LazyGit:[/dim]")
            console.print(f"  1. Stage your changes")
            console.print(f"  2. Press [code]{key}[/code] in the {context} context")
            console.print(f"  3. Review and edit the generated commit message")
            console.print(f"  4. Accept to commit or copy to clipboard")
        else:
            console.print("[yellow]⚠️  Shortcut already exists[/yellow]")
            console.print("Use [code]--force[/code] to overwrite the existing shortcut.")
            raise typer.Exit(1)
            
    except Exception as e:
        if verbose:
            console.print_exception()
        else:
            console.print(f"[red]❌ Error: {str(e)}[/red]")
        raise typer.Exit(1)


@app.command()
def uninstall_shortcut(
    key: str = typer.Option("C", "--key", "-k", help="Key binding to remove"),
    context: str = typer.Option("files", "--context", "-c", help="LazyGit context"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
) -> None:
    """
    Remove LazyGit shortcut for AI commit generation.
    """
    try:
        show_banner()
        
        shortcut_manager = LazyGitShortcutManager()
        
        console.print(f"[blue]🔧 Removing LazyGit shortcut...[/blue]")
        console.print(f"  Key: [code]{key}[/code]")
        console.print(f"  Context: [code]{context}[/code]")
        
        success = shortcut_manager.uninstall_shortcut(key, context)
        
        if success:
            console.print("[green]✅ Shortcut removed successfully![/green]")
        else:
            console.print("[yellow]⚠️  Shortcut not found[/yellow]")
            
    except Exception as e:
        if verbose:
            console.print_exception()
        else:
            console.print(f"[red]❌ Error: {str(e)}[/red]")
        raise typer.Exit(1)


@app.command()
def config(
    show: bool = typer.Option(False, "--show", "-s", help="Show current configuration"),
    edit: bool = typer.Option(False, "--edit", "-e", help="Edit configuration file"),
    reset: bool = typer.Option(False, "--reset", help="Reset to default configuration"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
) -> None:
    """
    Manage lazygit-ai configuration.
    
    View, edit, or reset your configuration settings for AI providers,
    commit message format, and rule preferences.
    """
    try:
        show_banner()
        
        config_manager = ConfigManager()
        
        if show:
            config_manager.show_config(console)
        elif edit:
            config_manager.edit_config(console)
        elif reset:
            config_manager.reset_config(console)
        else:
            # Show help if no action specified
            console.print("[blue]📋 Configuration Management[/blue]")
            console.print("\n[dim]Available actions:[/dim]")
            console.print("  [code]lazygit-ai config --show[/code]   - Show current config")
            console.print("  [code]lazygit-ai config --edit[/code]   - Edit config file")
            console.print("  [code]lazygit-ai config --reset[/code]  - Reset to defaults")
            
    except Exception as e:
        if verbose:
            console.print_exception()
        else:
            console.print(f"[red]❌ Error: {str(e)}[/red]")
        raise typer.Exit(1)


@app.command()
def version() -> None:
    """Show lazygit-ai version information."""
    from . import __version__
    
    show_banner()
    console.print(f"[blue]Version:[/blue] {__version__}")
    console.print("[blue]Python:[/blue] " + sys.version.split()[0])


@app.callback()
def main(
    version: bool = typer.Option(False, "--version", help="Show version and exit"),
) -> None:
    """
    🚀 lazygit-ai: AI-powered commit message generator for LazyGit
    
    Transform your Git workflow with intelligent commit message generation.
    Combines rule-based analysis with optional AI enhancement to create
    meaningful, semantic commit messages.
    
    [dim]For more information, visit:[/dim]
    [link=https://github.com/yourusername/lazygit-ai]https://github.com/yourusername/lazygit-ai[/link]
    """
    if version:
        version()
        raise typer.Exit()


if __name__ == "__main__":
    app() 