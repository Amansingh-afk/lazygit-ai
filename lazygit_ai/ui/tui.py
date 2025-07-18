"""
Simple TUI for lazygit-ai.

Provides a clean, LazyGit-style interface for commit message editing.
"""

import pyperclip
import sys
import os
import threading
import time
import tty
import termios
from typing import Optional

from rich.console import Console, Group
from rich.text import Text
from rich.panel import Panel
from rich.prompt import Prompt

from ..core.analyzer import GitAnalysis
from ..utils.git import GitWrapper


class InPlaceEditor:
    """In-place text editor for terminal input."""
    
    def __init__(self, initial_text: str = "", max_width: int = 80):
        self.text = initial_text
        self.cursor_pos = len(initial_text)
        self.max_width = max_width
        self.editing = False
    
    def _get_cursor_position(self, text: str, target_pos: int) -> tuple[int, int]:
        """Calculate cursor position in terms of row and column."""
        lines = text.split('\n')
        row = 0
        col = 0
        pos = 0
        
        for line in lines:
            if pos + len(line) >= target_pos:
                col = target_pos - pos
                break
            pos += len(line) + 1  # +1 for newline
            row += 1
        
        return row, col
    
    def _move_cursor(self, row: int, col: int) -> None:
        """Move cursor to specific position."""
        print(f"\033[{row + 1};{col + 1}H", end='', flush=True)
    
    def _clear_line(self) -> None:
        """Clear current line."""
        print("\033[K", end='', flush=True)
    
    def _get_char(self) -> str:
        """Get a single character from stdin."""
        if 'pytest' in sys.modules or not sys.stdin.isatty():
            raise Exception("Not in interactive terminal")
            
        try:
            import tty
            import termios
        except ImportError:
            raise Exception("tty/termios not available")
            
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
            return ch
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    
    def _get_special_key(self) -> Optional[str]:
        """Get special keys like arrow keys."""
        ch = self._get_char()
        if ch == '\x1b':  # ESC
            next_ch = self._get_char()
            if next_ch == '[':
                third_ch = self._get_char()
                if third_ch == 'D':  # Left arrow
                    return 'LEFT'
                elif third_ch == 'C':  # Right arrow
                    return 'RIGHT'
                elif third_ch == 'H':  # Home
                    return 'HOME'
                elif third_ch == 'F':  # End
                    return 'END'
        elif ch == '\x7f':  # Backspace
            return 'BACKSPACE'
        elif ch == '\x04':  # Ctrl+D
            return 'CTRL_D'
        elif ch == '\x0d':  # Enter
            return 'ENTER'
        return ch
    
    def edit(self, start_row: int, start_col: int) -> str:
        """Edit text in-place starting at the given position."""
        self.editing = True
        
        # Move cursor to start position
        self._move_cursor(start_row, start_col)
        
        # Display initial text
        print(self.text, end='', flush=True)
        
        while self.editing:
            key = self._get_special_key()
            
            if key == 'LEFT':
                if self.cursor_pos > 0:
                    self.cursor_pos -= 1
                    row, col = self._get_cursor_position(self.text, self.cursor_pos)
                    self._move_cursor(start_row + row, start_col + col)
            
            elif key == 'RIGHT':
                if self.cursor_pos < len(self.text):
                    self.cursor_pos += 1
                    row, col = self._get_cursor_position(self.text, self.cursor_pos)
                    self._move_cursor(start_row + row, start_col + col)
            
            elif key == 'HOME':
                self.cursor_pos = 0
                self._move_cursor(start_row, start_col)
            
            elif key == 'END':
                self.cursor_pos = len(self.text)
                row, col = self._get_cursor_position(self.text, self.cursor_pos)
                self._move_cursor(start_row + row, start_col + col)
            
            elif key == 'BACKSPACE':
                if self.cursor_pos > 0:
                    self.text = self.text[:self.cursor_pos - 1] + self.text[self.cursor_pos:]
                    self.cursor_pos -= 1
                    # Redraw from cursor position
                    row, col = self._get_cursor_position(self.text, self.cursor_pos)
                    self._move_cursor(start_row + row, start_col + col)
                    self._clear_line()
                    print(self.text[self.cursor_pos:], end='', flush=True)
                    self._move_cursor(start_row + row, start_col + col)
            
            elif key == 'ENTER':
                self.editing = False
                break
            
            elif key == 'CTRL_D':
                self.editing = False
                self.text = ""
                break
            
            elif isinstance(key, str) and len(key) == 1 and ord(key) >= 32:
                # Insert character
                self.text = self.text[:self.cursor_pos] + key + self.text[self.cursor_pos:]
                self.cursor_pos += 1
                # Redraw from cursor position
                row, col = self._get_cursor_position(self.text, self.cursor_pos - 1)
                self._move_cursor(start_row + row, start_col + col - 1)
                self._clear_line()
                print(self.text[self.cursor_pos - 1:], end='', flush=True)
                self._move_cursor(start_row + row, start_col + col)
        
        return self.text


class SimpleCommitTUI:
    """Simple, LazyGit-style TUI for commit message editing."""
    
    def __init__(self, message: str, analysis: GitAnalysis, git_wrapper: GitWrapper) -> None:
        """Initialize simple TUI."""
        self.message = message
        self.analysis = analysis
        self.git_wrapper = git_wrapper
        self.console = Console()
        self.running = True
        self.editor = InPlaceEditor(message)
    
    def _clear_terminal(self) -> None:
        """Clear the terminal screen."""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def _get_main_panel(self) -> Panel:
        """Create the main panel that shows the edit interface directly."""
        message_panel = Panel(
            f"[bold yellow]✎[/bold yellow] {self.message}",
            title="[bold yellow]✎ Edit commit message[/bold yellow]",
            border_style="yellow",
            padding=(1, 2)
        )
        
        info_lines = [
            f"[yellow]Branch:[/yellow] [white]{self.analysis.branch_name}[/white]",
            f"[yellow]Files:[/yellow] [white]{len(self.analysis.staged_files)}[/white]",
            f"[yellow]Changes:[/yellow] [white]{self.analysis.change_summary}[/white]",
            ""
        ]
        
        readiness = self.git_wrapper.check_commit_readiness()
        if readiness["unstaged_changes"]:
            info_lines.append(f"[yellow]⚠️  You also have unstaged changes. Only staged changes will be committed.[/yellow]")
        
        info_lines.append("")
        
        info_group = Group(*(Text.from_markup(line) for line in info_lines))
        
        actions_text = "[dim]Press Enter to finish editing, a to accept, c to copy, q to quit[/dim]"
        
        group = Group(
            message_panel,
            info_group,
            Text.from_markup(actions_text),
            Text("")
        )
        return Panel(
            group,
            title="[bold blue]🚀 lazygit-ai - Commit Message Editor[/bold blue]",
            border_style="blue",
            padding=(1, 2),
            expand=True
        )
    
    def _handle_key_press(self, key: str) -> None:
        """Handle key press events."""
        key = key.lower()
        
        if key == "a":
            self._handle_accept()
        elif key == "c":
            self._handle_copy()
        elif key == "q":
            self._handle_quit()
    
    def _handle_accept(self) -> None:
        """Handle accept action."""
        success = self.git_wrapper.commit(self.message)
        if success:
            self._clear_terminal()
            self.console.print("[bold green]✅ Commit created successfully![/bold green]")
            self.running = False
            sys.exit(0)
        else:
            self.console.print("[bold red]❌ Failed to create commit[/bold red]")
    
    def _handle_copy(self) -> None:
        """Handle copy action."""
        try:
            pyperclip.copy(self.message)
            self.console.print("[bold green]📋 Message copied to clipboard![/bold green]")
        except Exception as e:
            self.console.print(f"[bold red]❌ Failed to copy to clipboard: {e}[/bold red]")
    
    def _handle_quit(self) -> None:
        """Handle quit action."""
        self._clear_terminal()
        self.console.print("[yellow]👋 Exiting without committing[/yellow]")
        self.running = False
        sys.exit(1)
    
    def _keyboard_listener(self) -> None:
        """Listen for keyboard input in a separate thread."""
        try:
            import keyboard
            
            def on_key_press(event):
                if not self.running:
                    return
                if event.name in ['a', 'c', 'q']:
                    self._handle_key_press(event.name)
            
            try:
                keyboard.on_press(on_key_press)
                
                while self.running:
                    time.sleep(0.1)
                    
            except (PermissionError, OSError) as e:
                self._alternative_keyboard_listener()
                
        except ImportError:
            self._alternative_keyboard_listener()
        except Exception as e:
            self._alternative_keyboard_listener()
    
    def _fallback_input(self) -> None:
        """Fallback to traditional input method."""
        while self.running:
            try:
                choice = Prompt.ask(
                    "[bold cyan]Action[/bold cyan]",
                    choices=["a", "c", "q"],
                    default="a",
                    show_choices=False
                )
                self._handle_key_press(choice)
            except KeyboardInterrupt:
                self._handle_quit()
            except EOFError:
                self._handle_quit()
    
    def _get_key_press(self) -> Optional[str]:
        """Get a single key press without requiring Enter."""
        if 'pytest' in sys.modules or not sys.stdin.isatty():
            return None
            
        try:
            if os.name == 'nt':  # Windows
                import msvcrt
                key = msvcrt.getch().decode('utf-8').lower()
                return key if key in ['a', 'c', 'q'] else None
            else:  # Unix-like systems
                try:
                    import tty
                    import termios
                except ImportError:
                    return None
                
                fd = sys.stdin.fileno()
                old_settings = termios.tcgetattr(fd)
                try:
                    tty.setraw(sys.stdin.fileno())
                    ch = sys.stdin.read(1).lower()
                    return ch if ch in ['a', 'c', 'q'] else None
                finally:
                    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        except Exception:
            return None
    
    def _alternative_keyboard_listener(self) -> None:
        """Alternative keyboard listener using platform-specific methods."""
        if 'pytest' in sys.modules or not sys.stdin.isatty():
            self._fallback_input()
            return
            
        try:
            while self.running:
                key = self._get_key_press()
                if key:
                    self._handle_key_press(key)
                time.sleep(0.01)
        except Exception as e:
            self._fallback_input()
    
    def run(self) -> None:
        """Run the simple TUI with direct edit mode."""
        readiness = self.git_wrapper.check_commit_readiness()
        
        if not readiness["ready"]:
            self._clear_terminal()
            self.console.print(f"[bold red]{readiness['message']}[/bold red]")
            self.console.print("\n[yellow]Please stage your files first, then run lazygit-ai again.[/yellow]")
            self.running = False
            sys.exit(1)
        
        self._clear_terminal()
        self.console.print(self._get_main_panel())
        
        self._handle_edit()
        
        self._clear_terminal()
        self.console.print(self._get_main_panel())
        
        listener_thread = threading.Thread(target=self._keyboard_listener, daemon=True)
        listener_thread.start()
        
        try:
            while self.running:
                time.sleep(0.1)
        except KeyboardInterrupt:
            self._handle_quit()
    
    def _handle_edit(self) -> None:
        """Handle edit action with in-place editing."""
        if not sys.stdin.isatty() or 'pytest' in sys.modules:
            self._fallback_edit()
            return
            
        try:
            message_start_col = 4
            panel_start_row = 3
            panel_start_col = 4
            
            cursor_row = panel_start_row + 1
            cursor_col = panel_start_col + message_start_col
            
            editor = InPlaceEditor(self.message)
            
            new_message = editor.edit(cursor_row, cursor_col)
            
            if new_message.strip():
                self.message = new_message.strip()
                self._clear_terminal()
                self.console.print(self._get_main_panel())
                self.console.print("[bold green]✅ Message updated![/bold green]")
            
        except Exception as e:
            self._fallback_edit()
    
    def _fallback_edit(self) -> None:
        """Fallback editing method."""
        try:
            self.console.print(f"\n[bold cyan]✎ Editing commit message:[/bold cyan]")
            
            import readline
            
            readline.set_startup_hook(lambda: readline.insert_text(self.message))
            
            new_message = input("[bold yellow]Message: [/bold yellow]")
            
            readline.set_startup_hook()
            
            if new_message.strip():
                self.message = new_message.strip()
                self._clear_terminal()
                self.console.print(self._get_main_panel())
                self.console.print("[bold green]✅ Message updated![/bold green]")
            
        except ImportError:
            self.console.print(f"\n[bold cyan]✎ Editing commit message:[/bold cyan]")
            new_message = Prompt.ask(
                "[bold yellow]Message[/bold yellow]",
                default=self.message,
                show_default=False
            )
            if new_message.strip():
                self.message = new_message.strip()
                self._clear_terminal()
                self.console.print(self._get_main_panel())
                self.console.print("[bold green]✅ Message updated![/bold green]")
        except KeyboardInterrupt:
            pass
        except EOFError:
            pass


class CommitTUI(SimpleCommitTUI):
    """Alias for backward compatibility."""
    pass 