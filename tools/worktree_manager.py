#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""
Git Worktree Manager - Create isolated worktrees for forked agents.

Manages git worktrees for isolated agent work environments.
Worktrees allow multiple branches to be checked out simultaneously
in separate directories.

Usage:
    uv run tools/worktree_manager.py create --branch <name> [--task "<task>"]
    uv run tools/worktree_manager.py list
    uv run tools/worktree_manager.py remove --path <worktree-path> [--force]
    uv run tools/worktree_manager.py prune

Examples:
    # Create worktree for a new feature branch
    uv run tools/worktree_manager.py create --branch fork/fix-auth --task "fix auth bug"

    # List all worktrees
    uv run tools/worktree_manager.py list

    # Remove a worktree
    uv run tools/worktree_manager.py remove --path ../myrepo-worktrees/fork-fix-auth

    # Clean up stale worktree entries
    uv run tools/worktree_manager.py prune
"""

import subprocess
import os
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path


def run_git_command(args: list, cwd: str = None) -> tuple[bool, str, str]:
    """
    Run a git command and return results.

    Args:
        args: Git command arguments (without 'git' prefix)
        cwd: Working directory

    Returns:
        Tuple of (success, stdout, stderr)
    """
    try:
        result = subprocess.run(
            ["git"] + args,
            capture_output=True,
            text=True,
            cwd=cwd or os.getcwd()
        )
        return (
            result.returncode == 0,
            result.stdout.strip(),
            result.stderr.strip()
        )
    except Exception as e:
        return False, "", str(e)


def get_git_root(cwd: str = None) -> str | None:
    """
    Get the root of the current git repository.

    Args:
        cwd: Directory to check from

    Returns:
        Git root path or None if not in a git repo
    """
    success, stdout, _ = run_git_command(
        ["rev-parse", "--show-toplevel"],
        cwd=cwd
    )
    return stdout if success else None


def get_current_branch(cwd: str = None) -> str | None:
    """Get the current branch name."""
    success, stdout, _ = run_git_command(
        ["rev-parse", "--abbrev-ref", "HEAD"],
        cwd=cwd
    )
    return stdout if success else None


def get_worktrees_dir(git_root: str) -> Path:
    """
    Get the directory for storing worktrees (sibling to repo).

    Creates worktrees in a directory named {repo-name}-worktrees
    next to the main repository.
    """
    repo_name = Path(git_root).name
    worktrees_base = Path(git_root).parent / f"{repo_name}-worktrees"
    return worktrees_base


def branch_exists(branch_name: str, cwd: str = None) -> bool:
    """Check if a branch exists."""
    success, _, _ = run_git_command(
        ["show-ref", "--verify", f"refs/heads/{branch_name}"],
        cwd=cwd
    )
    return success


def create_worktree(
    branch_name: str,
    task_description: str = "",
    cwd: str = None
) -> dict:
    """
    Create a new git worktree for isolated work.

    Args:
        branch_name: Name for the new branch
        task_description: Optional task description
        cwd: Working directory (must be in a git repo)

    Returns:
        Dict with worktree info or error
    """
    git_root = get_git_root(cwd)
    if not git_root:
        return {"success": False, "error": "Not in a git repository"}

    worktrees_dir = get_worktrees_dir(git_root)
    worktrees_dir.mkdir(parents=True, exist_ok=True)

    # Generate worktree name from branch
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    safe_branch = branch_name.replace("/", "-").replace(" ", "-")
    worktree_path = worktrees_dir / f"{safe_branch}-{timestamp}"

    # Check if branch already exists
    if branch_exists(branch_name, git_root):
        # Use existing branch
        cmd = ["worktree", "add", str(worktree_path), branch_name]
    else:
        # Create new branch
        cmd = ["worktree", "add", "-b", branch_name, str(worktree_path)]

    success, stdout, stderr = run_git_command(cmd, git_root)

    if success:
        return {
            "success": True,
            "worktree_path": str(worktree_path),
            "branch": branch_name,
            "task": task_description,
            "git_root": git_root,
            "created_at": datetime.now().isoformat(),
            "message": f"Worktree created at {worktree_path}"
        }
    else:
        return {
            "success": False,
            "error": stderr or "Failed to create worktree",
            "command": " ".join(["git"] + cmd)
        }


def list_worktrees(cwd: str = None) -> dict:
    """
    List all git worktrees.

    Args:
        cwd: Working directory

    Returns:
        Dict with worktrees list
    """
    git_root = get_git_root(cwd)
    if not git_root:
        return {"success": False, "error": "Not in a git repository"}

    success, stdout, stderr = run_git_command(
        ["worktree", "list", "--porcelain"],
        git_root
    )

    if not success:
        return {"success": False, "error": stderr}

    worktrees = []
    current = {}

    for line in stdout.split("\n"):
        if line.startswith("worktree "):
            if current:
                worktrees.append(current)
            current = {"path": line[9:]}
        elif line.startswith("HEAD "):
            current["head"] = line[5:]
        elif line.startswith("branch "):
            current["branch"] = line[7:].replace("refs/heads/", "")
        elif line == "bare":
            current["bare"] = True
        elif line == "detached":
            current["detached"] = True

    if current:
        worktrees.append(current)

    return {
        "success": True,
        "count": len(worktrees),
        "worktrees": worktrees,
        "git_root": git_root
    }


def remove_worktree(worktree_path: str, force: bool = False, cwd: str = None) -> dict:
    """
    Remove a git worktree.

    Args:
        worktree_path: Path to the worktree
        force: Force removal even with uncommitted changes
        cwd: Working directory

    Returns:
        Result dict
    """
    git_root = get_git_root(cwd)
    if not git_root:
        return {"success": False, "error": "Not in a git repository"}

    cmd = ["worktree", "remove"]
    if force:
        cmd.append("--force")
    cmd.append(worktree_path)

    success, stdout, stderr = run_git_command(cmd, git_root)

    if success:
        return {
            "success": True,
            "removed": worktree_path,
            "message": f"Worktree {worktree_path} removed"
        }
    else:
        return {
            "success": False,
            "error": stderr or "Failed to remove worktree",
            "hint": "Use --force to remove worktrees with uncommitted changes"
        }


def prune_worktrees(cwd: str = None) -> dict:
    """
    Clean up stale worktree entries.

    Removes worktree metadata for worktrees that no longer exist on disk.
    """
    git_root = get_git_root(cwd)
    if not git_root:
        return {"success": False, "error": "Not in a git repository"}

    success, stdout, stderr = run_git_command(["worktree", "prune"], git_root)

    if success:
        return {
            "success": True,
            "message": "Stale worktree entries pruned"
        }
    else:
        return {
            "success": False,
            "error": stderr or "Failed to prune worktrees"
        }


def main():
    parser = argparse.ArgumentParser(
        description="Git Worktree Manager - Create isolated worktrees for forked agents",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Create command
    create_parser = subparsers.add_parser("create", help="Create a new worktree")
    create_parser.add_argument("--branch", required=True, help="Branch name")
    create_parser.add_argument("--task", default="", help="Task description")
    create_parser.add_argument("--cwd", help="Working directory")

    # List command
    list_parser = subparsers.add_parser("list", help="List worktrees")
    list_parser.add_argument("--cwd", help="Working directory")

    # Remove command
    remove_parser = subparsers.add_parser("remove", help="Remove a worktree")
    remove_parser.add_argument("--path", required=True, help="Worktree path")
    remove_parser.add_argument("--force", action="store_true", help="Force removal")
    remove_parser.add_argument("--cwd", help="Working directory")

    # Prune command
    prune_parser = subparsers.add_parser("prune", help="Prune stale entries")
    prune_parser.add_argument("--cwd", help="Working directory")

    args = parser.parse_args()

    if args.command == "create":
        result = create_worktree(args.branch, args.task, args.cwd)
    elif args.command == "list":
        result = list_worktrees(args.cwd)
    elif args.command == "remove":
        result = remove_worktree(args.path, args.force, args.cwd)
    elif args.command == "prune":
        result = prune_worktrees(args.cwd)
    else:
        result = {"error": f"Unknown command: {args.command}"}

    # Pretty print JSON for agent consumption
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
