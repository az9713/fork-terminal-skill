#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""
Task Registry - Track forked agent tasks.

Manages the forked-tasks.json registry for tracking running and completed tasks.
Supports add, status, list, update, and remove operations.

Usage:
    uv run tools/task_registry.py add --task "<task>" --type <type> --cwd "<dir>"
    uv run tools/task_registry.py status
    uv run tools/task_registry.py list [--filter running|completed|failed]
    uv run tools/task_registry.py update --id <id> --status completed
    uv run tools/task_registry.py remove --id <id>
    uv run tools/task_registry.py clear [--status completed|failed|all]

Examples:
    # Add a new task
    uv run tools/task_registry.py add --task "fix auth bug" --type claude --cwd "C:\\project"

    # Check status summary
    uv run tools/task_registry.py status

    # List running tasks
    uv run tools/task_registry.py list --filter running

    # Mark task as completed
    uv run tools/task_registry.py update --id abc123 --status completed

    # Clear old completed tasks
    uv run tools/task_registry.py clear --status completed
"""

import json
import os
import sys
import argparse
from datetime import datetime
from pathlib import Path
import uuid

# Skill directory (parent of tools/)
SKILL_DIR = Path(__file__).parent.parent
DATA_DIR = SKILL_DIR / "data"
REGISTRY_FILE = DATA_DIR / "forked-tasks.json"


def ensure_data_dir():
    """Create data directory if it doesn't exist."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def load_registry() -> dict:
    """Load the task registry from disk."""
    ensure_data_dir()
    if not REGISTRY_FILE.exists():
        return {
            "tasks": [],
            "metadata": {
                "created": datetime.now().isoformat(),
                "version": "1.0"
            }
        }
    try:
        with open(REGISTRY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        # Return fresh registry if file is corrupted
        return {
            "tasks": [],
            "metadata": {
                "created": datetime.now().isoformat(),
                "version": "1.0"
            }
        }


def save_registry(registry: dict):
    """Save the task registry to disk."""
    ensure_data_dir()
    registry["metadata"]["updated"] = datetime.now().isoformat()
    with open(REGISTRY_FILE, "w", encoding="utf-8") as f:
        json.dump(registry, f, indent=2)


def generate_task_id() -> str:
    """Generate a short unique task ID."""
    return uuid.uuid4().hex[:8]


def add_task(
    task: str,
    fork_type: str,
    cwd: str,
    task_id: str = None,
    model: str = None,
    output_file: str = None,
    context_file: str = None,
    preset: str = None
) -> dict:
    """
    Add a new task to the registry.

    Args:
        task: Task description
        fork_type: Type of fork (claude, gemini, raw)
        cwd: Working directory
        task_id: Optional specific task ID
        model: Model used (for AI agents)
        output_file: Path to output log file
        context_file: Path to context handoff file
        preset: Preset name if using a preset

    Returns:
        The created task entry
    """
    registry = load_registry()

    new_task = {
        "id": task_id or generate_task_id(),
        "task": task,
        "type": fork_type,
        "model": model,
        "cwd": cwd,
        "output_file": output_file,
        "context_file": context_file,
        "preset": preset,
        "status": "running",
        "started_at": datetime.now().isoformat(),
        "completed_at": None,
        "exit_code": None,
        "notes": None
    }

    registry["tasks"].append(new_task)
    save_registry(registry)

    return new_task


def update_task(
    task_id: str,
    status: str = None,
    exit_code: int = None,
    notes: str = None
) -> dict:
    """
    Update a task's status.

    Args:
        task_id: ID of the task to update
        status: New status (running, completed, failed)
        exit_code: Exit code if completed/failed
        notes: Optional notes

    Returns:
        Updated task entry or error dict
    """
    registry = load_registry()

    for task in registry["tasks"]:
        if task["id"] == task_id:
            if status:
                task["status"] = status
            if exit_code is not None:
                task["exit_code"] = exit_code
            if notes:
                task["notes"] = notes
            if status in ("completed", "failed"):
                task["completed_at"] = datetime.now().isoformat()

            save_registry(registry)
            return {"success": True, "task": task}

    return {"success": False, "error": f"Task {task_id} not found"}


def get_status() -> dict:
    """
    Get summary status of all tasks.

    Returns:
        Dict with counts and recent tasks
    """
    registry = load_registry()
    tasks = registry.get("tasks", [])

    running = [t for t in tasks if t["status"] == "running"]
    completed = [t for t in tasks if t["status"] == "completed"]
    failed = [t for t in tasks if t["status"] == "failed"]

    # Sort by start time (most recent first)
    running.sort(key=lambda t: t.get("started_at", ""), reverse=True)
    completed.sort(key=lambda t: t.get("completed_at", ""), reverse=True)
    failed.sort(key=lambda t: t.get("completed_at", ""), reverse=True)

    return {
        "summary": {
            "total": len(tasks),
            "running": len(running),
            "completed": len(completed),
            "failed": len(failed)
        },
        "running_tasks": running[:10],  # Show up to 10 most recent
        "recent_completed": completed[:5],  # Show 5 most recent completed
        "recent_failed": failed[:5] if failed else []
    }


def list_tasks(filter_status: str = None, limit: int = 50) -> dict:
    """
    List all tasks, optionally filtered by status.

    Args:
        filter_status: Optional status filter
        limit: Maximum number of tasks to return

    Returns:
        Dict with tasks list
    """
    registry = load_registry()
    tasks = registry.get("tasks", [])

    if filter_status:
        tasks = [t for t in tasks if t["status"] == filter_status]

    # Sort by start time (most recent first)
    tasks.sort(key=lambda t: t.get("started_at", ""), reverse=True)

    return {
        "count": len(tasks),
        "tasks": tasks[:limit],
        "filter": filter_status
    }


def get_task(task_id: str) -> dict:
    """
    Get a specific task by ID.

    Args:
        task_id: Task ID to find

    Returns:
        Task entry or error dict
    """
    registry = load_registry()

    for task in registry.get("tasks", []):
        if task["id"] == task_id:
            return {"success": True, "task": task}

    return {"success": False, "error": f"Task {task_id} not found"}


def remove_task(task_id: str) -> dict:
    """
    Remove a task from the registry.

    Args:
        task_id: Task ID to remove

    Returns:
        Success/failure result
    """
    registry = load_registry()
    original_count = len(registry["tasks"])
    registry["tasks"] = [t for t in registry["tasks"] if t["id"] != task_id]

    if len(registry["tasks"]) < original_count:
        save_registry(registry)
        return {"success": True, "id": task_id, "message": f"Task {task_id} removed"}

    return {"success": False, "error": f"Task {task_id} not found"}


def clear_tasks(status: str = None) -> dict:
    """
    Clear tasks from registry.

    Args:
        status: Status to clear (completed, failed, or all)

    Returns:
        Result with count of removed tasks
    """
    registry = load_registry()
    original_count = len(registry["tasks"])

    if status == "all":
        registry["tasks"] = []
    elif status:
        registry["tasks"] = [t for t in registry["tasks"] if t["status"] != status]
    else:
        # Default: clear completed tasks
        registry["tasks"] = [t for t in registry["tasks"] if t["status"] != "completed"]

    removed_count = original_count - len(registry["tasks"])
    save_registry(registry)

    return {
        "success": True,
        "removed_count": removed_count,
        "remaining_count": len(registry["tasks"]),
        "cleared_status": status or "completed"
    }


def main():
    parser = argparse.ArgumentParser(
        description="Task Registry - Track forked agent tasks",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Add command
    add_parser = subparsers.add_parser("add", help="Add a new task")
    add_parser.add_argument("--id", help="Task ID (auto-generated if not provided)")
    add_parser.add_argument("--task", required=True, help="Task description")
    add_parser.add_argument("--type", required=True, choices=["claude", "gemini", "raw"])
    add_parser.add_argument("--cwd", default=os.getcwd(), help="Working directory")
    add_parser.add_argument("--model", help="Model used")
    add_parser.add_argument("--output-file", help="Output log file path")
    add_parser.add_argument("--context-file", help="Context handoff file path")
    add_parser.add_argument("--preset", help="Preset name")

    # Status command
    subparsers.add_parser("status", help="Show status summary")

    # List command
    list_parser = subparsers.add_parser("list", help="List tasks")
    list_parser.add_argument("--filter", choices=["running", "completed", "failed"])
    list_parser.add_argument("--limit", type=int, default=50)

    # Get command
    get_parser = subparsers.add_parser("get", help="Get specific task")
    get_parser.add_argument("--id", required=True, help="Task ID")

    # Update command
    update_parser = subparsers.add_parser("update", help="Update task status")
    update_parser.add_argument("--id", required=True, help="Task ID")
    update_parser.add_argument("--status", choices=["running", "completed", "failed"])
    update_parser.add_argument("--exit-code", type=int)
    update_parser.add_argument("--notes", help="Optional notes")

    # Remove command
    remove_parser = subparsers.add_parser("remove", help="Remove a task")
    remove_parser.add_argument("--id", required=True, help="Task ID")

    # Clear command
    clear_parser = subparsers.add_parser("clear", help="Clear tasks")
    clear_parser.add_argument("--status", choices=["completed", "failed", "all"],
                              help="Status to clear (default: completed)")

    args = parser.parse_args()

    # Execute command
    if args.command == "add":
        result = add_task(
            task=args.task,
            fork_type=args.type,
            cwd=args.cwd,
            task_id=args.id,
            model=args.model,
            output_file=args.output_file,
            context_file=args.context_file,
            preset=args.preset
        )
    elif args.command == "status":
        result = get_status()
    elif args.command == "list":
        result = list_tasks(args.filter, args.limit)
    elif args.command == "get":
        result = get_task(args.id)
    elif args.command == "update":
        result = update_task(args.id, args.status, args.exit_code, args.notes)
    elif args.command == "remove":
        result = remove_task(args.id)
    elif args.command == "clear":
        result = clear_tasks(args.status)
    else:
        result = {"error": f"Unknown command: {args.command}"}

    # Pretty print JSON for agent consumption
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
