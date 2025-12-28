#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""
Fork Terminal - Cross-platform terminal spawner for Claude Code skills.

Spawns new terminal windows to run Claude Code, Gemini CLI, or raw CLI commands.
Supports Windows, macOS, and Linux.

Platform Support:
    - Windows: Windows Terminal (wt.exe) or PowerShell fallback
    - macOS: Terminal.app via osascript (AppleScript)
    - Linux: gnome-terminal, konsole, xfce4-terminal, or xterm

Usage:
    uv run tools/fork_terminal.py --type claude --task "your task" --cwd "C:\\path"
    uv run tools/fork_terminal.py --type gemini --task "your task" --model haiku
    uv run tools/fork_terminal.py --type raw --task "dir /s" --cwd "."
    uv run tools/fork_terminal.py --type claude --task "fix bug" --with-context context.md
    uv run tools/fork_terminal.py --type raw --task "echo hello" --new-window

Examples:
    # Spawn Claude Code with a task
    uv run tools/fork_terminal.py --type claude --task "list current directory files"

    # Spawn raw CLI command
    uv run tools/fork_terminal.py --type raw --task "ping google.com"

    # Spawn with specific model
    uv run tools/fork_terminal.py --type claude --task "complex analysis" --model opus

    # Force new window instead of tab (Windows Terminal only)
    uv run tools/fork_terminal.py --type raw --task "echo hello" --new-window
"""

import subprocess
import sys
import os
import json
import argparse
import platform
from datetime import datetime
from pathlib import Path
import uuid
import shutil

# Model tier mapping to actual model IDs
MODEL_MAP = {
    "haiku": "claude-3-5-haiku-20241022",
    "sonnet": "claude-sonnet-4-20250514",
    "opus": "claude-opus-4-20250514"
}

# Skill directory (parent of tools/)
SKILL_DIR = Path(__file__).parent.parent
DATA_DIR = SKILL_DIR / "data"
LOGS_DIR = SKILL_DIR / "logs" / "forks"


def find_terminal_executable() -> tuple[str, str]:
    """
    Determine the best available terminal for the current platform.

    Returns:
        Tuple of (terminal_type, executable_path)

    Platform behavior:
        - Windows: Windows Terminal (wt.exe) > PowerShell
        - macOS: osascript (for Terminal.app)
        - Linux: gnome-terminal > konsole > xfce4-terminal > xterm
    """
    system = platform.system()

    if system == "Windows":
        # Check for Windows Terminal in standard location
        wt_path = os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\WindowsApps\wt.exe")
        if os.path.exists(wt_path):
            return "wt", wt_path

        # Check if wt is in PATH
        wt_in_path = shutil.which("wt")
        if wt_in_path:
            return "wt", "wt"

        # Fall back to PowerShell (always available on Windows)
        return "powershell", "powershell"

    elif system == "Darwin":  # macOS
        # Use osascript to control Terminal.app
        return "osascript", "osascript"

    elif system == "Linux":
        # Try common Linux terminal emulators in order of preference
        terminals = [
            ("gnome-terminal", "gnome-terminal"),
            ("konsole", "konsole"),
            ("xfce4-terminal", "xfce4-terminal"),
            ("xterm", "xterm"),
        ]
        for term_type, term_cmd in terminals:
            if shutil.which(term_cmd):
                return term_type, term_cmd
        # Ultimate fallback
        return "xterm", "xterm"

    else:
        raise OSError(f"Unsupported platform: {system}")


def escape_for_cmd(text: str) -> str:
    """Escape special characters for cmd.exe."""
    text = text.replace('"', '\\"')
    text = text.replace('%', '%%')
    return text


def escape_for_powershell(text: str) -> str:
    """Escape special characters for PowerShell."""
    text = text.replace("'", "''")
    text = text.replace("`", "``")
    return text


def escape_for_bash(text: str) -> str:
    """Escape special characters for bash."""
    text = text.replace("'", "'\\''")
    text = text.replace('"', '\\"')
    return text


def escape_for_applescript(text: str) -> str:
    """Escape special characters for AppleScript strings."""
    text = text.replace('\\', '\\\\')
    text = text.replace('"', '\\"')
    return text


def spawn_terminal_windows(
    command: str,
    cwd: str,
    title: str = "Forked Agent",
    output_file: str = None,
    new_window: bool = False
) -> dict:
    """
    Spawn a new terminal window on Windows with the given command.

    Args:
        command: The command to execute in the new terminal
        cwd: Working directory for the new terminal
        title: Title for the terminal window/tab
        output_file: Optional file to capture output (for logging)
        new_window: If True, force a new window instead of a tab (Windows Terminal only)

    Returns:
        Dict with spawn result including success status
    """
    terminal_type, terminal_path = find_terminal_executable()

    # Add output redirection if output file specified
    if output_file:
        LOGS_DIR.mkdir(parents=True, exist_ok=True)
        command_with_log = f'{command} 2>&1 | Tee-Object -FilePath "{output_file}"'
    else:
        command_with_log = command

    try:
        if terminal_type == "wt":
            # Windows Terminal: use -w -1 to force new window, otherwise new-tab
            if new_window:
                # -w -1 means "create a new window" in Windows Terminal
                spawn_cmd = [
                    terminal_path,
                    "-w", "-1",
                    "new-tab",
                    "-d", cwd,
                    "--title", title[:50],
                    "powershell", "-NoExit", "-Command", command_with_log
                ]
            else:
                spawn_cmd = [
                    terminal_path,
                    "new-tab",
                    "-d", cwd,
                    "--title", title[:50],
                    "powershell", "-NoExit", "-Command", command_with_log
                ]

            result = subprocess.run(
                spawn_cmd,
                capture_output=True,
                text=True,
                cwd=cwd
            )
        else:
            # PowerShell fallback: Start-Process always opens new window
            escaped_cwd = escape_for_powershell(cwd)
            escaped_cmd = escape_for_powershell(command_with_log)

            ps_script = f"Set-Location '{escaped_cwd}'; {escaped_cmd}"

            spawn_cmd = [
                "powershell",
                "-Command",
                f"Start-Process powershell -ArgumentList '-NoExit', '-Command', '{escape_for_powershell(ps_script)}'"
            ]

            result = subprocess.run(
                spawn_cmd,
                capture_output=True,
                text=True,
                shell=True,
                cwd=cwd
            )

        return {
            "success": result.returncode == 0,
            "terminal_type": terminal_type,
            "command": command,
            "cwd": cwd,
            "title": title,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
            "output_file": output_file,
            "new_window": new_window
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "terminal_type": terminal_type,
            "command": command,
            "cwd": cwd
        }


def spawn_terminal_macos(
    command: str,
    cwd: str,
    title: str = "Forked Agent",
    output_file: str = None
) -> dict:
    """
    Spawn a new terminal window on macOS using AppleScript.

    Args:
        command: The command to execute in the new terminal
        cwd: Working directory for the new terminal
        title: Title for the terminal window
        output_file: Optional file to capture output (for logging)

    Returns:
        Dict with spawn result including success status
    """
    # Add output redirection if output file specified
    if output_file:
        LOGS_DIR.mkdir(parents=True, exist_ok=True)
        command_with_log = f'{command} 2>&1 | tee "{output_file}"'
    else:
        command_with_log = command

    # Escape for AppleScript
    escaped_cwd = escape_for_applescript(cwd)
    escaped_cmd = escape_for_applescript(command_with_log)

    # AppleScript to open Terminal.app and run command
    applescript = f'''
        tell application "Terminal"
            activate
            do script "cd \\"{escaped_cwd}\\" && {escaped_cmd}"
        end tell
    '''

    try:
        spawn_cmd = ["osascript", "-e", applescript]

        result = subprocess.run(
            spawn_cmd,
            capture_output=True,
            text=True
        )

        return {
            "success": result.returncode == 0,
            "terminal_type": "Terminal.app",
            "command": command,
            "cwd": cwd,
            "title": title,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
            "output_file": output_file
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "terminal_type": "Terminal.app",
            "command": command,
            "cwd": cwd
        }


def spawn_terminal_linux(
    command: str,
    cwd: str,
    title: str = "Forked Agent",
    output_file: str = None
) -> dict:
    """
    Spawn a new terminal window on Linux.

    Args:
        command: The command to execute in the new terminal
        cwd: Working directory for the new terminal
        title: Title for the terminal window
        output_file: Optional file to capture output (for logging)

    Returns:
        Dict with spawn result including success status
    """
    terminal_type, terminal_path = find_terminal_executable()

    # Add output redirection if output file specified
    if output_file:
        LOGS_DIR.mkdir(parents=True, exist_ok=True)
        command_with_log = f'{command} 2>&1 | tee "{output_file}"'
    else:
        command_with_log = command

    # Escape command for bash
    escaped_cmd = escape_for_bash(command_with_log)

    try:
        if terminal_type == "gnome-terminal":
            # gnome-terminal uses -- to separate terminal args from command
            spawn_cmd = [
                terminal_path,
                "--working-directory", cwd,
                "--title", title[:50],
                "--",
                "bash", "-c", f'{command_with_log}; exec bash'
            ]
        elif terminal_type == "konsole":
            # konsole uses --workdir and -e
            spawn_cmd = [
                terminal_path,
                "--workdir", cwd,
                "-e",
                "bash", "-c", f'{command_with_log}; exec bash'
            ]
        elif terminal_type == "xfce4-terminal":
            # xfce4-terminal uses --working-directory and -e
            spawn_cmd = [
                terminal_path,
                "--working-directory", cwd,
                "--title", title[:50],
                "-e",
                f'bash -c "{escaped_cmd}; exec bash"'
            ]
        else:
            # xterm fallback
            spawn_cmd = [
                terminal_path,
                "-T", title[:50],
                "-e",
                f'bash -c "cd {cwd} && {command_with_log}; exec bash"'
            ]

        result = subprocess.run(
            spawn_cmd,
            capture_output=True,
            text=True,
            cwd=cwd
        )

        return {
            "success": result.returncode == 0,
            "terminal_type": terminal_type,
            "command": command,
            "cwd": cwd,
            "title": title,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
            "output_file": output_file
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "terminal_type": terminal_type,
            "command": command,
            "cwd": cwd
        }


def spawn_terminal(
    command: str,
    cwd: str,
    title: str = "Forked Agent",
    output_file: str = None,
    new_window: bool = False
) -> dict:
    """
    Cross-platform terminal spawner - dispatches to platform-specific implementation.

    Args:
        command: The command to execute in the new terminal
        cwd: Working directory for the new terminal
        title: Title for the terminal window/tab
        output_file: Optional file to capture output (for logging)
        new_window: If True, force new window instead of tab (Windows only)

    Returns:
        Dict with spawn result including success status
    """
    system = platform.system()

    if system == "Windows":
        return spawn_terminal_windows(command, cwd, title, output_file, new_window)
    elif system == "Darwin":
        return spawn_terminal_macos(command, cwd, title, output_file)
    elif system == "Linux":
        return spawn_terminal_linux(command, cwd, title, output_file)
    else:
        return {
            "success": False,
            "error": f"Unsupported platform: {system}",
            "command": command,
            "cwd": cwd
        }


def build_claude_command(
    task: str,
    model: str = "sonnet",
    context_file: str = None,
    dangerously_skip_permissions: bool = False
) -> str:
    """
    Build Claude Code CLI command.

    Args:
        task: The task/prompt for Claude
        model: Model tier (haiku, sonnet, opus)
        context_file: Optional path to context file for handoff
        dangerously_skip_permissions: Skip permission prompts (for automation)

    Returns:
        Command string to run Claude Code
    """
    cmd_parts = ["claude"]

    # Add model selection if specified
    if model in MODEL_MAP:
        cmd_parts.extend(["--model", MODEL_MAP[model]])

    # Add permission skip if requested (for trusted automation)
    if dangerously_skip_permissions:
        cmd_parts.append("--dangerously-skip-permissions")

    # Add context file if provided (for context handoff)
    if context_file and os.path.exists(context_file):
        try:
            with open(context_file, 'r', encoding='utf-8') as f:
                context = f.read()
            task = f"{context}\n\n---\n\nTask: {task}"
        except Exception:
            pass

    # Escape quotes in task for shell
    escaped_task = task.replace('"', '\\"').replace("'", "''")
    cmd_parts.append(f'"{escaped_task}"')

    return " ".join(cmd_parts)


def build_gemini_command(task: str, model: str = None) -> str:
    """
    Build Gemini CLI command.

    Args:
        task: The task/prompt for Gemini
        model: Optional model selection

    Returns:
        Command string to run Gemini CLI
    """
    cmd_parts = ["gemini"]

    if model:
        cmd_parts.extend(["--model", model])

    escaped_task = task.replace('"', '\\"').replace("'", "''")
    cmd_parts.append(f'"{escaped_task}"')

    return " ".join(cmd_parts)


def generate_task_id() -> str:
    """Generate a short unique task ID."""
    return uuid.uuid4().hex[:8]


def generate_output_filename(task: str, task_id: str) -> str:
    """Generate output log filename."""
    date_str = datetime.now().strftime("%Y-%m-%d")
    safe_task = "".join(c if c.isalnum() or c in ('-', '_') else '-' for c in task[:30])
    safe_task = safe_task.strip('-').lower()
    return str(LOGS_DIR / f"{date_str}_{safe_task}_{task_id}.md")


def main():
    parser = argparse.ArgumentParser(
        description="Fork Terminal - Cross-platform terminal spawner for AI agents or CLI commands",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    uv run tools/fork_terminal.py --type claude --task "analyze this codebase"
    uv run tools/fork_terminal.py --type raw --task "npm test"
    uv run tools/fork_terminal.py --type claude --task "fix bug" --model opus --with-context summary.md
    uv run tools/fork_terminal.py --type raw --task "echo hello" --new-window

Platform Support:
    Windows: Windows Terminal (wt.exe) or PowerShell
    macOS:   Terminal.app via osascript
    Linux:   gnome-terminal, konsole, xfce4-terminal, or xterm
        """
    )

    parser.add_argument(
        "--type",
        choices=["claude", "gemini", "raw"],
        required=True,
        help="Type of fork: claude (Claude Code), gemini (Gemini CLI), or raw (CLI command)"
    )
    parser.add_argument(
        "--task",
        required=True,
        help="Task description or command to execute"
    )
    parser.add_argument(
        "--model",
        default="sonnet",
        choices=["haiku", "sonnet", "opus"],
        help="Model tier for AI agents (default: sonnet)"
    )
    parser.add_argument(
        "--cwd",
        default=os.getcwd(),
        help="Working directory for the forked terminal"
    )
    parser.add_argument(
        "--with-context",
        dest="context_file",
        help="Path to context summary file for handoff"
    )
    parser.add_argument(
        "--no-output",
        action="store_true",
        help="Disable output capture to logs"
    )
    parser.add_argument(
        "--skip-permissions",
        action="store_true",
        help="Add --dangerously-skip-permissions flag (for trusted automation)"
    )
    parser.add_argument(
        "--task-id",
        help="Specific task ID (auto-generated if not provided)"
    )
    parser.add_argument(
        "--new-window",
        action="store_true",
        help="Force opening a new window instead of a tab (Windows Terminal only)"
    )

    args = parser.parse_args()

    # Resolve working directory to absolute path
    cwd = os.path.abspath(args.cwd)

    # Generate task ID
    task_id = args.task_id or generate_task_id()

    # Generate output filename if output capture enabled
    output_file = None
    if not args.no_output:
        output_file = generate_output_filename(args.task, task_id)

    # Build command based on type
    if args.type == "claude":
        command = build_claude_command(
            args.task,
            args.model,
            args.context_file,
            args.skip_permissions
        )
        title = f"Claude: {args.task[:40]}..."
    elif args.type == "gemini":
        command = build_gemini_command(args.task, args.model)
        title = f"Gemini: {args.task[:40]}..."
    else:  # raw
        command = args.task
        title = f"CLI: {args.task[:40]}..."

    # Spawn terminal (cross-platform)
    result = spawn_terminal(command, cwd, title, output_file, args.new_window)

    # Build output for agent consumption (agentic return values)
    output = {
        "timestamp": datetime.now().isoformat(),
        "task_id": task_id,
        "fork_type": args.type,
        "task": args.task,
        "model": args.model if args.type in ("claude", "gemini") else None,
        "cwd": cwd,
        "platform": platform.system(),
        "command_executed": command,
        "output_file": output_file,
        "new_window": args.new_window,
        "spawn_result": result,
        "message": f"Forked {args.type} agent spawned successfully on {platform.system()}" if result.get("success") else f"Failed to spawn: {result.get('error', result.get('stderr', 'Unknown error'))}"
    }

    # Pretty print JSON for agent to parse
    print(json.dumps(output, indent=2))

    return 0 if result.get("success") else 1


if __name__ == "__main__":
    sys.exit(main())
