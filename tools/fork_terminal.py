#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""
Fork Terminal - Windows-compatible terminal spawner for Claude Code skills.

Spawns new terminal windows to run Claude Code, Gemini CLI, or raw CLI commands.
Supports Windows Terminal (wt.exe) with PowerShell fallback.

Usage:
    uv run tools/fork_terminal.py --type claude --task "your task" --cwd "C:\\path"
    uv run tools/fork_terminal.py --type gemini --task "your task" --model haiku
    uv run tools/fork_terminal.py --type raw --task "dir /s" --cwd "."
    uv run tools/fork_terminal.py --type claude --task "fix bug" --with-context context.md

Examples:
    # Spawn Claude Code with a task
    uv run tools/fork_terminal.py --type claude --task "list current directory files"

    # Spawn raw CLI command
    uv run tools/fork_terminal.py --type raw --task "ping google.com"

    # Spawn with specific model
    uv run tools/fork_terminal.py --type claude --task "complex analysis" --model opus
"""

import subprocess
import sys
import os
import json
import argparse
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
    Determine the best available terminal on Windows.

    Priority order:
    1. Windows Terminal (wt.exe) - modern, best UX, supports tabs
    2. PowerShell - universal fallback

    Returns:
        Tuple of (terminal_type, executable_path)
    """
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


def escape_for_cmd(text: str) -> str:
    """Escape special characters for cmd.exe."""
    # Escape quotes and special chars
    text = text.replace('"', '\\"')
    text = text.replace('%', '%%')
    return text


def escape_for_powershell(text: str) -> str:
    """Escape special characters for PowerShell."""
    # Escape single quotes by doubling them
    text = text.replace("'", "''")
    # Escape backticks
    text = text.replace("`", "``")
    return text


def spawn_terminal_windows(
    command: str,
    cwd: str,
    title: str = "Forked Agent",
    output_file: str = None
) -> dict:
    """
    Spawn a new terminal window on Windows with the given command.

    Args:
        command: The command to execute in the new terminal
        cwd: Working directory for the new terminal
        title: Title for the terminal window/tab
        output_file: Optional file to capture output (for logging)

    Returns:
        Dict with spawn result including success status
    """
    terminal_type, terminal_path = find_terminal_executable()

    # Add output redirection if output file specified
    if output_file:
        # Ensure logs directory exists
        LOGS_DIR.mkdir(parents=True, exist_ok=True)
        # Append output capture using tee-like behavior
        # Note: This captures what's visible in terminal
        command_with_log = f'{command} 2>&1 | Tee-Object -FilePath "{output_file}"'
    else:
        command_with_log = command

    try:
        if terminal_type == "wt":
            # Windows Terminal: new tab with title and command
            # Using cmd /k keeps the window open after command completes
            # This allows user to see the result
            spawn_cmd = [
                terminal_path,
                "new-tab",
                "-d", cwd,
                "--title", title[:50],  # Limit title length
                "powershell", "-NoExit", "-Command", command_with_log
            ]

            result = subprocess.run(
                spawn_cmd,
                capture_output=True,
                text=True,
                cwd=cwd
            )
        else:
            # PowerShell fallback: Start-Process opens new window
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
        # Read context and prepend to task
        try:
            with open(context_file, 'r', encoding='utf-8') as f:
                context = f.read()
            task = f"{context}\n\n---\n\nTask: {task}"
        except Exception:
            pass  # Silently continue without context if file read fails

    # Add the task as the prompt (interactive mode - no -p flag per Dan's guidance)
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
    # Sanitize task for filename
    safe_task = "".join(c if c.isalnum() or c in ('-', '_') else '-' for c in task[:30])
    safe_task = safe_task.strip('-').lower()
    return str(LOGS_DIR / f"{date_str}_{safe_task}_{task_id}.md")


def main():
    parser = argparse.ArgumentParser(
        description="Fork Terminal - Spawn new terminal windows for AI agents or CLI commands",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    uv run tools/fork_terminal.py --type claude --task "analyze this codebase"
    uv run tools/fork_terminal.py --type raw --task "npm test"
    uv run tools/fork_terminal.py --type claude --task "fix bug" --model opus --with-context summary.md
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

    # Spawn terminal
    result = spawn_terminal_windows(command, cwd, title, output_file)

    # Build output for agent consumption (agentic return values)
    output = {
        "timestamp": datetime.now().isoformat(),
        "task_id": task_id,
        "fork_type": args.type,
        "task": args.task,
        "model": args.model if args.type in ("claude", "gemini") else None,
        "cwd": cwd,
        "command_executed": command,
        "output_file": output_file,
        "spawn_result": result,
        "message": f"Forked {args.type} agent spawned successfully" if result.get("success") else f"Failed to spawn: {result.get('error', result.get('stderr', 'Unknown error'))}"
    }

    # Pretty print JSON for agent to parse
    print(json.dumps(output, indent=2))

    return 0 if result.get("success") else 1


if __name__ == "__main__":
    sys.exit(main())
