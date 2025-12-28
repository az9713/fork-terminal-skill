#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""
Context Builder - Prepare context summaries for forked agents.

Builds context handoff files that contain the delegated task and relevant
background context from the parent agent session.

Usage:
    uv run tools/context_builder.py --task "<delegated task>" --context "<background>"
    uv run tools/context_builder.py --task "fix auth bug" --context "Working on login" --files src/auth.py src/login.py

Examples:
    # Basic context handoff
    uv run tools/context_builder.py --task "fix the null pointer in user.email" --context "We found a bug during auth refactor"

    # With important files
    uv run tools/context_builder.py --task "add validation" --context "Refactoring forms" --files src/forms.py src/validate.py

    # Load context from file
    uv run tools/context_builder.py --task "continue the work" --context-file context.md
"""

import os
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path

# Skill directory (parent of tools/)
SKILL_DIR = Path(__file__).parent.parent
PROMPTS_DIR = SKILL_DIR / "prompts"
DATA_DIR = SKILL_DIR / "data"

# Default template for context handoff
DEFAULT_TEMPLATE = """# Context Handoff for Forked Agent

You are a forked agent spawned by a parent agent to handle a delegated task.

## Delegated Task

{task}

## Working Directory

{cwd}

## Background Context

{context}

## Relevant Files

{files}

## Instructions

1. **Focus ONLY on the delegated task** - don't expand scope
2. Work independently but stay within the task boundaries
3. If blocked, clearly state what you need
4. When complete, summarize what was accomplished

## Completion Signal

When done, output:
```
FORK COMPLETE: [brief summary of what was done]
```

If blocked:
```
FORK BLOCKED: [what you need to continue]
```

---
Generated: {timestamp}
Parent CWD: {cwd}
"""


def load_template() -> str:
    """Load the fork-summary prompt template."""
    template_path = PROMPTS_DIR / "fork-summary.md"
    if template_path.exists():
        try:
            return template_path.read_text(encoding="utf-8")
        except IOError:
            pass
    return DEFAULT_TEMPLATE


def build_context_file(
    task: str,
    context: str = None,
    cwd: str = None,
    important_files: list = None,
    context_from_file: str = None,
    output_path: str = None
) -> dict:
    """
    Build a context file for the forked agent.

    Args:
        task: The delegated task (MOST IMPORTANT)
        context: Background context from parent session
        cwd: Working directory
        important_files: List of relevant file paths
        context_from_file: Path to file containing context
        output_path: Where to save the context file

    Returns:
        Dict with result info
    """
    if cwd is None:
        cwd = os.getcwd()

    # Load context from file if specified
    if context_from_file and os.path.exists(context_from_file):
        try:
            with open(context_from_file, 'r', encoding='utf-8') as f:
                context = f.read()
        except IOError as e:
            context = f"(Failed to load context from {context_from_file}: {e})"

    # Build file list string
    if important_files:
        files_str = "\n".join(f"- `{f}`" for f in important_files)
    else:
        files_str = "(No specific files mentioned)"

    # Load and fill template
    template = load_template()

    content = template.format(
        task=task,
        cwd=cwd,
        context=context or "(No additional context provided)",
        files=files_str,
        timestamp=datetime.now().isoformat()
    )

    # Generate output path if not specified
    if not output_path:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        output_path = str(DATA_DIR / f"context-{timestamp}.md")

    # Write context file
    try:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)

        return {
            "success": True,
            "context_file": output_path,
            "task": task,
            "cwd": cwd,
            "has_context": bool(context),
            "files_count": len(important_files) if important_files else 0,
            "content_length": len(content),
            "message": f"Context file created at {output_path}"
        }
    except IOError as e:
        return {
            "success": False,
            "error": str(e),
            "task": task
        }


def preview_context(
    task: str,
    context: str = None,
    cwd: str = None,
    important_files: list = None
) -> dict:
    """
    Preview the context that would be generated without saving.

    Args:
        task: The delegated task
        context: Background context
        cwd: Working directory
        important_files: List of relevant file paths

    Returns:
        Dict with preview content
    """
    if cwd is None:
        cwd = os.getcwd()

    # Build file list string
    if important_files:
        files_str = "\n".join(f"- `{f}`" for f in important_files)
    else:
        files_str = "(No specific files mentioned)"

    template = load_template()

    content = template.format(
        task=task,
        cwd=cwd,
        context=context or "(No additional context provided)",
        files=files_str,
        timestamp=datetime.now().isoformat()
    )

    return {
        "preview": True,
        "content": content,
        "length": len(content),
        "word_count": len(content.split())
    }


def main():
    parser = argparse.ArgumentParser(
        description="Context Builder - Prepare context summaries for forked agents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Build context with task and background
    uv run tools/context_builder.py --task "fix auth bug" --context "Found during login refactor"

    # Include important files
    uv run tools/context_builder.py --task "add tests" --files src/auth.py tests/test_auth.py

    # Preview without saving
    uv run tools/context_builder.py --task "review code" --preview
        """
    )

    parser.add_argument(
        "--task",
        required=True,
        help="The delegated task (MOST IMPORTANT)"
    )
    parser.add_argument(
        "--context",
        default="",
        help="Background context from parent session"
    )
    parser.add_argument(
        "--context-file",
        help="Load context from a file instead"
    )
    parser.add_argument(
        "--cwd",
        default=os.getcwd(),
        help="Working directory"
    )
    parser.add_argument(
        "--files",
        nargs="*",
        help="Important files to include"
    )
    parser.add_argument(
        "--output",
        help="Output file path (auto-generated if not specified)"
    )
    parser.add_argument(
        "--preview",
        action="store_true",
        help="Preview content without saving"
    )

    args = parser.parse_args()

    if args.preview:
        result = preview_context(
            task=args.task,
            context=args.context,
            cwd=args.cwd,
            important_files=args.files
        )
    else:
        result = build_context_file(
            task=args.task,
            context=args.context,
            cwd=args.cwd,
            important_files=args.files,
            context_from_file=args.context_file,
            output_path=args.output
        )

    # Pretty print JSON for agent consumption
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
