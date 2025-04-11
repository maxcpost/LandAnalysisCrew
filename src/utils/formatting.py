#!/usr/bin/env python3
"""
Formatting utilities for terminal output.
Provides functions for displaying headers, agent messages, and other formatted output.
"""

import os
import textwrap

class Colors:
    """Terminal colors for text formatting."""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    GRAY = '\033[90m'

def supports_color():
    """Check if the terminal supports colors."""
    try:
        import curses
        curses.setupterm()
        return curses.tigetnum("colors") > 2
    except Exception:
        # If there's any error, assume no color support
        return False

def get_terminal_width():
    """Get terminal width safely, defaulting to 80 if it can't be determined."""
    try:
        return min(os.get_terminal_size().columns, 80)
    except (OSError, AttributeError):
        return 80

def print_header(text):
    """Print a formatted header."""
    if not supports_color():
        print(f"\n===== {text} =====")
        return
        
    width = get_terminal_width()
    print("\n" + "=" * width)
    print(f"{Colors.BOLD}{Colors.HEADER}{text.center(width)}{Colors.ENDC}")
    print("=" * width)

def print_subheader(text):
    """Print a formatted subheader."""
    if not supports_color():
        print(f"\n----- {text} -----")
        return
        
    width = get_terminal_width()
    print("\n" + "-" * width)
    print(f"{Colors.BOLD}{text.center(width)}{Colors.ENDC}")
    print("-" * width)

def print_agent(role, message, color=None):
    """
    Print an agent message with proper formatting.
    
    Args:
        role: The role/name of the agent
        message: The message to display
        color: Optional color override (defaults to bold)
    """
    if not supports_color():
        print(f"\n[{role}]: {message}")
        return
        
    if color is None:
        color = Colors.BOLD
        
    width = get_terminal_width()
    wrapped_text = textwrap.fill(
        message, 
        width=width - 4,
        initial_indent=f"{color}💬 {role}: {Colors.ENDC}",
        subsequent_indent="   "
    )
    print(wrapped_text)
    print("")  # Add a blank line for readability

def print_success(message):
    """Print a success message."""
    if not supports_color():
        print(f"\n[SUCCESS] {message}")
        return
        
    print(f"\n{Colors.GREEN}✓ {message}{Colors.ENDC}")

def print_error(message):
    """Print an error message."""
    if not supports_color():
        print(f"\n[ERROR] {message}")
        return
        
    print(f"\n{Colors.RED}✗ {message}{Colors.ENDC}")

def print_warning(message):
    """Print a warning message."""
    if not supports_color():
        print(f"\n[WARNING] {message}")
        return
        
    print(f"\n{Colors.YELLOW}⚠ {message}{Colors.ENDC}")

def print_info(message):
    """Print an information message."""
    if not supports_color():
        print(f"\n[INFO] {message}")
        return
        
    print(f"\n{Colors.BLUE}ℹ {message}{Colors.ENDC}")

def print_step(step_num, description):
    """Print a step in a process."""
    if not supports_color():
        print(f"\nStep {step_num}: {description}")
        return
        
    print(f"\n{Colors.CYAN}Step {step_num}: {Colors.BOLD}{description}{Colors.ENDC}")

def print_progress(percentage, prefix="", suffix=""):
    """
    Print a progress bar.
    
    Args:
        percentage: Progress percentage (0-100)
        prefix: Text to display before the progress bar
        suffix: Text to display after the progress bar
    """
    if not supports_color():
        print(f"{prefix} {percentage}% {suffix}")
        return
        
    width = get_terminal_width() - len(prefix) - len(suffix) - 10
    filled = int(width * percentage / 100)
    bar = "█" * filled + "-" * (width - filled)
    print(f"\r{prefix} [{Colors.GREEN}{bar}{Colors.ENDC}] {percentage:>3}% {suffix}", end="\r")
    if percentage == 100:
        print()  # New line after 100% 