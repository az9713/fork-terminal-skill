# Developer Guide

Complete technical reference for developers who want to understand, modify, or extend the Fork Terminal skill. This guide assumes you have basic programming experience (C, C++, Java, or similar) but may be new to Python, Claude Code skills, or modern tooling.

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Technology Stack](#2-technology-stack)
3. [Development Environment Setup](#3-development-environment-setup)
4. [Code Structure Deep Dive](#4-code-structure-deep-dive)
5. [How Skills Work](#5-how-skills-work)
6. [Tool Scripts Explained](#6-tool-scripts-explained)
7. [Adding New Features](#7-adding-new-features)
8. [Testing Guide](#8-testing-guide)
9. [Debugging Guide](#9-debugging-guide)
10. [Code Patterns & Conventions](#10-code-patterns--conventions)
11. [Common Modifications](#11-common-modifications)
12. [Deployment](#12-deployment)
13. [Contributing](#13-contributing)

---

## 1. Architecture Overview

### 1.1 Big Picture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Claude Code Session                       │
│                                                                 │
│  User: "fork a claude agent to fix the auth bug"                │
│                           │                                     │
│                           ▼                                     │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                       SKILL.md                              ││
│  │  - Parses user intent                                       ││
│  │  - Routes to appropriate cookbook                           ││
│  │  - Executes tool scripts                                    ││
│  └─────────────────────────────────────────────────────────────┘│
│                           │                                     │
│           ┌───────────────┼───────────────┐                     │
│           ▼               ▼               ▼                     │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐               │
│  │ cookbook/   │ │ prompts/    │ │ tools/      │               │
│  │             │ │             │ │             │               │
│  │ Reference   │ │ Templates   │ │ Python      │               │
│  │ docs loaded │ │ for output  │ │ scripts     │               │
│  │ on demand   │ │             │ │ that do     │               │
│  │             │ │             │ │ the work    │               │
│  └─────────────┘ └─────────────┘ └──────┬──────┘               │
│                                         │                       │
└─────────────────────────────────────────│───────────────────────┘
                                          │
                                          ▼
                              ┌───────────────────┐
                              │  NEW TERMINAL     │
                              │                   │
                              │  Windows:         │
                              │   wt.exe/PS       │
                              │                   │
                              │  macOS:           │
                              │   Terminal.app    │
                              │                   │
                              │  Linux:           │
                              │   gnome-terminal  │
                              │   konsole, xterm  │
                              │                   │
                              │  Running:         │
                              │  - Claude Code    │
                              │  - Gemini CLI     │
                              │  - Raw command    │
                              └───────────────────┘
```

### 1.2 Data Flow

1. **User Request** → Claude Code receives natural language or slash command
2. **Skill Activation** → Claude reads SKILL.md and understands the skill
3. **Intent Parsing** → Skill determines fork type, flags, presets
4. **Progressive Disclosure** → Loads relevant cookbook files as needed
5. **Tool Execution** → Runs Python scripts to spawn terminals, track tasks
6. **Response** → Returns structured JSON for Claude to interpret

### 1.3 Key Design Principles

| Principle | Explanation |
|-----------|-------------|
| **Pivot File** | SKILL.md is the single source of truth |
| **Progressive Disclosure** | Don't load all docs upfront; load on demand |
| **Agentic Returns** | Tools return JSON for agent consumption |
| **Fresh Context** | Forked agents start with clean context windows |
| **Minimal Dependencies** | Use UV inline dependencies, no requirements.txt |

---

## 2. Technology Stack

### 2.1 Core Technologies

| Technology | Purpose | Why It's Used |
|------------|---------|---------------|
| **Python 3.10+** | Tool scripts | Universal, good subprocess support |
| **UV** | Script runner | Fast, handles inline dependencies |
| **Markdown** | Documentation | Human and agent readable |
| **JSON** | Data interchange | Structured, parseable by agents |
| **Git** | Version control | Worktree support |

### 2.2 What is UV?

UV is a fast Python package runner from Astral (makers of Ruff). Instead of:
```
pip install package
python script.py
```

You write dependencies in the script and run:
```
uv run script.py
```

UV handles the virtual environment automatically.

### 2.3 UV Inline Dependencies

At the top of each Python script, you'll see:

```python
#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
```

This tells UV:
- Minimum Python version required
- Packages to install (empty = standard library only)

To add a dependency:
```python
# /// script
# requires-python = ">=3.10"
# dependencies = ["requests", "pyyaml"]
# ///
```

### 2.4 Cross-Platform Terminal Support

The skill supports multiple platforms with automatic terminal detection:

| Platform | Primary Terminal | Fallback | Method |
|----------|-----------------|----------|--------|
| **Windows** | Windows Terminal (wt.exe) | PowerShell | `subprocess.run()` |
| **macOS** | Terminal.app | - | AppleScript via `osascript` |
| **Linux** | gnome-terminal, konsole, xfce4-terminal | xterm | `subprocess.run()` |

**Windows Terminal features:**
- Modern terminal with tabs
- Better rendering than cmd.exe
- `--new-window` flag to force separate window

**macOS Terminal.app:**
- Controlled via AppleScript
- Always opens new windows

**Linux terminals:**
- Detected in priority order
- Different CLI flags per terminal

---

## 3. Development Environment Setup

### 3.1 Prerequisites

#### Python 3.10+

**Check:**
```bash
python --version
```

**Install:** Download from https://python.org

#### UV

**Check:**
```bash
uv --version
```

**Install:**
```bash
pip install uv
```

Or (Unix/Mac):
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### Git

**Check:**
```bash
git --version
```

**Install:** Download from https://git-scm.com

#### Claude Code

**Check:**
```bash
claude --version
```

**Install:** Visit https://claude.ai/code

#### A Code Editor

Recommended:
- **VS Code** - Free, excellent Python support
- **Cursor** - AI-enhanced editor (Dan's preference)
- **PyCharm** - Full Python IDE

### 3.2 Clone the Project

```bash
git clone <repository-url>
cd agent_skill_dan
```

### 3.3 Verify Setup

Run all tools to verify:

```bash
# Task registry
uv run .claude/skills/fork-terminal/tools/task_registry.py status

# Context builder
uv run .claude/skills/fork-terminal/tools/context_builder.py --task "test" --preview

# Worktree manager
uv run .claude/skills/fork-terminal/tools/worktree_manager.py list

# Fork terminal
uv run .claude/skills/fork-terminal/tools/fork_terminal.py --type raw --task "echo test" --no-output
```

All should execute without errors.

### 3.4 IDE Setup

#### VS Code

Install extensions:
- Python (Microsoft)
- Pylance (Microsoft)
- Markdown All in One

Settings to add (.vscode/settings.json):
```json
{
  "python.defaultInterpreterPath": "python",
  "editor.formatOnSave": true,
  "python.formatting.provider": "black"
}
```

---

## 4. Code Structure Deep Dive

### 4.1 Directory Layout

```
.claude/skills/fork-terminal/
│
├── SKILL.md                        # THE CENTRAL FILE
│   │
│   │   This is the "pivot file" that:
│   │   - Defines when the skill activates
│   │   - Contains variables (feature flags)
│   │   - Lists available commands
│   │   - Provides step-by-step instructions
│   │   - Routes to cookbook files
│   │
├── tools/                          # PYTHON SCRIPTS
│   │
│   ├── fork_terminal.py            # Core terminal spawning
│   │   │
│   │   │   Main responsibilities:
│   │   │   - Detect Windows Terminal vs PowerShell
│   │   │   - Build Claude/Gemini/raw commands
│   │   │   - Spawn new terminal windows
│   │   │   - Return structured JSON
│   │   │
│   ├── task_registry.py            # Task tracking
│   │   │
│   │   │   Main responsibilities:
│   │   │   - Add/update/remove tasks
│   │   │   - Query task status
│   │   │   - Persist to JSON file
│   │   │
│   ├── context_builder.py          # Context handoff
│   │   │
│   │   │   Main responsibilities:
│   │   │   - Load template from prompts/
│   │   │   - Fill in task, context, files
│   │   │   - Save context file
│   │   │
│   └── worktree_manager.py         # Git worktrees
│       │
│       │   Main responsibilities:
│       │   - Create/list/remove worktrees
│       │   - Generate branch names
│       │   - Handle git commands
│
├── prompts/                        # TEMPLATES
│   │
│   ├── fork_summary_user_prompt.md # How parent generates summary
│   ├── fork-summary.md             # What forked agent receives
│   ├── fork-claude.md              # Claude-specific instructions
│   ├── fork-gemini.md              # Gemini-specific instructions
│   └── fork-raw.md                 # Raw CLI instructions
│
├── cookbook/                       # REFERENCE DOCS
│   │
│   │   These are loaded on-demand (progressive disclosure)
│   │
│   ├── claude-code.md              # Claude CLI reference
│   ├── gemini-cli.md               # Gemini CLI reference
│   ├── presets.md                  # Preset definitions
│   └── worktree-guide.md           # Worktree patterns
│
├── data/                           # RUNTIME DATA
│   │
│   └── forked-tasks.json           # Task registry (auto-created)
│
└── logs/
    └── forks/                      # OUTPUT LOGS
        └── *.md                    # One file per fork
```

### 4.2 File Relationships

```
User Request
     │
     ▼
 SKILL.md ────────────────────────────────────┐
     │                                        │
     │ reads variables                        │ routes to
     │ parses intent                          │
     ▼                                        ▼
┌─────────┐    ┌─────────┐    ┌─────────┐   cookbook/
│ tools/  │    │ tools/  │    │ tools/  │     │
│ fork_   │    │ task_   │    │ context_│     ├── claude-code.md
│terminal │    │registry │    │builder  │     ├── presets.md
│   .py   │    │   .py   │    │   .py   │     └── ...
└────┬────┘    └────┬────┘    └────┬────┘
     │              │              │
     ▼              ▼              ▼
 Spawns         Reads/Writes   Uses template
 Terminal       data/forked-   from prompts/
                tasks.json     fork-summary.md
```

---

## 5. How Skills Work

### 5.1 Claude Code Skill System

Claude Code has a built-in skill system. Skills are defined in:
```
.claude/skills/{skill-name}/SKILL.md
```

When Claude Code starts in a directory with `.claude/skills/`, it:
1. Scans for SKILL.md files
2. Reads skill names and descriptions
3. Activates skills based on user requests

### 5.2 SKILL.md Anatomy

```markdown
---
name: fork-terminal                    # Unique identifier
description: Spawn new terminals...    # When to activate
---

# Title

Introduction text...

## Variables                           # Configuration flags

```yaml
enable_feature: true
default_value: "something"
```

## When to Use                         # Trigger phrases

Activate when user says...

## Instructions                        # Step-by-step guide

### Step 1: Parse Request
...

### Step 2: Execute
...

## Progressive Disclosure             # Conditional loading

If X, read cookbook/x.md
If Y, read cookbook/y.md
```

### 5.3 Progressive Disclosure

Instead of loading all documentation upfront:

```markdown
## Progressive Disclosure

### If fork type is Claude Code:
Read `cookbook/claude-code.md` for Claude CLI flags and patterns.

### If using a preset:
Read `cookbook/presets.md` and apply the matching preset.
```

This keeps context windows focused on relevant information.

---

## 6. Tool Scripts Explained

### 6.1 fork_terminal.py

**Purpose:** Cross-platform terminal spawning

**Key Functions:**

```python
def find_terminal_executable():
    """
    Detects the best available terminal for current platform.
    Returns: ("wt", "path/to/wt.exe") on Windows
             ("osascript", "osascript") on macOS
             ("gnome-terminal", "gnome-terminal") on Linux
    """

def spawn_terminal(command, cwd, title, output_file, new_window=False, use_cmd=False):
    """
    Cross-platform dispatcher - calls platform-specific function.
    use_cmd: If True, use cmd.exe instead of PowerShell on Windows.
    """

def spawn_terminal_windows(command, cwd, title, output_file, new_window=False, use_cmd=False):
    """
    Windows: Uses wt.exe (new-tab or new-window) or PowerShell fallback.
    use_cmd: If True, spawns cmd.exe (for raw commands with && syntax).
             If False, spawns PowerShell (for Claude/Gemini with Tee-Object logging).
    """

def spawn_terminal_macos(command, cwd, title, output_file):
    """
    macOS: Uses AppleScript via osascript to open Terminal.app.
    """

def spawn_terminal_linux(command, cwd, title, output_file):
    """
    Linux: Supports gnome-terminal, konsole, xfce4-terminal, xterm.
    """

def build_claude_command(task, model, context_file, skip_permissions):
    """
    Constructs: claude --model X "task"
    """
```

**Escape Helpers:**
```python
def escape_for_cmd(text):           # Windows cmd.exe
def escape_for_powershell(text):    # Windows PowerShell
def escape_for_bash(text):          # macOS/Linux
def escape_for_applescript(text):   # macOS AppleScript
```

**Input:** Command-line arguments
```bash
--type claude|gemini|raw   # Fork type
--task "..."               # What to do
--model haiku|sonnet|opus  # Model tier
--cwd "path"               # Working directory
--with-context "file"      # Context file
--no-output                # Skip logging
--new-window               # Force new window (Windows only)
```

**Output:** JSON
```json
{
  "success": true,
  "task_id": "abc123",
  "fork_type": "claude",
  "platform": "Windows",
  "new_window": false,
  "command_executed": "claude --model ... \"...\"",
  "output_file": "logs/forks/...",
  "message": "Forked claude agent spawned successfully on Windows"
}
```

### 6.2 task_registry.py

**Purpose:** Track forked tasks

**Data Structure (forked-tasks.json):**
```json
{
  "tasks": [
    {
      "id": "abc123",
      "task": "fix auth bug",
      "type": "claude",
      "model": "sonnet",
      "status": "running",
      "started_at": "2024-12-27T10:00:00",
      "completed_at": null
    }
  ],
  "metadata": {
    "created": "2024-12-27T09:00:00",
    "updated": "2024-12-27T10:00:00"
  }
}
```

**Commands:**
```bash
task_registry.py add --task "..." --type claude
task_registry.py status
task_registry.py list --filter running
task_registry.py update --id X --status completed
task_registry.py remove --id X
task_registry.py clear --status completed
```

### 6.3 context_builder.py

**Purpose:** Create context handoff files

**Template (prompts/fork-summary.md):**
```markdown
# Context Handoff for Forked Agent

## Delegated Task
{task}

## Background Context
{context}

## Relevant Files
{files}

...
```

**Usage:**
```bash
# Preview
context_builder.py --task "..." --context "..." --preview

# Create file
context_builder.py --task "..." --context "..." --files a.py b.py
```

### 6.4 worktree_manager.py

**Purpose:** Manage git worktrees

**Key Functions:**
```python
def get_git_root(cwd):
    """Find the root of the git repository."""

def create_worktree(branch_name, task_description, cwd):
    """Create a new worktree with a branch."""

def list_worktrees(cwd):
    """List all worktrees."""

def remove_worktree(worktree_path, force, cwd):
    """Remove a worktree."""
```

---

## 7. Adding New Features

### 7.1 Adding a New Preset

1. **Edit cookbook/presets.md:**

```markdown
### my-preset

Description of what this preset does.

```yaml
preset: my-preset
type: claude
model: sonnet
context: true
task_template: |
  Your template here: {description}
```

**Usage:** Say "Fork my-preset agent for description"

2. **Update SKILL.md** if needed (usually not required for presets)

3. **Test:** Say "Fork my-preset agent for test description"

### 7.2 Adding a New Flag

1. **Add to fork_terminal.py:**

```python
# In argparse section
parser.add_argument(
    "--my-flag",
    action="store_true",
    help="Description of flag"
)

# In main() logic
if args.my_flag:
    # Handle the flag
```

2. **Update SKILL.md:**

```markdown
## Flags

| Flag | Purpose |
|------|---------|
| `--my-flag` | Description |
```

3. **Update documentation** (USER_GUIDE.md, etc.)

### 7.3 Adding a New Fork Type

1. **Add to fork_terminal.py:**

```python
def build_mytype_command(task, options):
    """Build command for my new type."""
    return f"mycommand {task}"

# In main()
elif args.type == "mytype":
    command = build_mytype_command(args.task, ...)
    title = f"MyType: {args.task[:40]}..."
```

2. **Update argparse choices:**
```python
parser.add_argument("--type", choices=["claude", "gemini", "raw", "mytype"])
```

3. **Add cookbook file:**
Create `.claude/skills/fork-terminal/cookbook/mytype.md`

4. **Update SKILL.md routing:**
```markdown
### If fork type is MyType:
Read `cookbook/mytype.md` for reference.
```

### 7.4 Adding a New Tool Script

1. **Create the script:**

```python
#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""
My Tool - Does something useful.

Usage:
    uv run tools/my_tool.py --option value
"""

import json
import argparse

def main():
    parser = argparse.ArgumentParser(description="My Tool")
    parser.add_argument("--option", required=True)
    args = parser.parse_args()

    result = {"success": True, "message": "Done"}
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
```

2. **Reference in SKILL.md:**
```markdown
### Step X: My New Step
```bash
uv run tools/my_tool.py --option value
```
```

---

## 8. Testing Guide

### 8.1 Manual Testing

**Test each tool individually:**

```bash
# Fork terminal
uv run .claude/skills/fork-terminal/tools/fork_terminal.py \
  --type raw --task "echo hello" --no-output

# Task registry
uv run .claude/skills/fork-terminal/tools/task_registry.py add \
  --task "test" --type claude
uv run .claude/skills/fork-terminal/tools/task_registry.py status

# Context builder
uv run .claude/skills/fork-terminal/tools/context_builder.py \
  --task "test" --preview

# Worktree manager
uv run .claude/skills/fork-terminal/tools/worktree_manager.py list
```

### 8.2 Integration Testing

**Test the full flow:**

1. Create context:
   ```bash
   uv run .claude/skills/fork-terminal/tools/context_builder.py \
     --task "fix bug" --context "testing"
   ```

2. Fork with context:
   ```bash
   uv run .claude/skills/fork-terminal/tools/fork_terminal.py \
     --type claude --task "fix bug" --with-context PATH
   ```

3. Check registry:
   ```bash
   uv run .claude/skills/fork-terminal/tools/task_registry.py status
   ```

### 8.3 Testing in Claude Code

1. Start Claude Code in the project directory:
   ```bash
   cd agent_skill_dan
   claude
   ```

2. Test natural language in Claude Code:
   ```
   "Fork a terminal to run echo hello"
   "Spawn a Claude agent to list files"
   "Show fork status"
   ```

### 8.4 Test Checklist

Before committing changes:

- [ ] fork_terminal.py spawns terminals correctly
- [ ] task_registry.py add/status/update/remove work
- [ ] context_builder.py creates valid files
- [ ] worktree_manager.py works in git repos
- [ ] SKILL.md syntax is valid
- [ ] All cookbook files are readable
- [ ] Documentation is updated

---

## 9. Debugging Guide

### 9.1 Common Issues

#### "Command not found: uv"

**Cause:** UV not installed
**Fix:** `pip install uv`

#### JSON parse error in tool output

**Cause:** Tool printed non-JSON output
**Fix:** Ensure all print statements output valid JSON

#### Terminal doesn't open

**Windows:**
```bash
# Check Windows Terminal
where wt

# Test PowerShell
powershell -Command "echo test"

# Check execution policy
powershell -Command "Get-ExecutionPolicy"
```

**macOS:**
```bash
# Test osascript
osascript -e 'tell application "Terminal" to activate'

# Check for automation permissions in System Preferences
```

**Linux:**
```bash
# Check available terminals
which gnome-terminal konsole xfce4-terminal xterm

# Check display is available
echo $DISPLAY
```

#### "Not in git repository" for worktrees

**Cause:** Not in a git repo
**Fix:** Run `git init` or use repo without worktrees

### 9.2 Debugging Techniques

#### Add Debug Logging

```python
import sys

def debug(msg):
    print(f"DEBUG: {msg}", file=sys.stderr)

# Use it
debug(f"Variable value: {variable}")
```

#### Test Functions Individually

```python
# At bottom of script
if __name__ == "__main__":
    # Test a specific function
    result = my_function("test input")
    print(json.dumps(result, indent=2))
```

#### Check JSON Output

```bash
uv run tools/my_tool.py --args 2>&1 | python -m json.tool
```

### 9.3 Log Files

Check these for issues:

1. **Task registry:** `.claude/skills/fork-terminal/data/forked-tasks.json`
2. **Fork logs:** `.claude/skills/fork-terminal/logs/forks/`

---

## 10. Code Patterns & Conventions

### 10.1 Python Style

**Use these patterns:**

```python
# UV script header (required)
#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

# Docstring for module
"""
Module description.

Usage:
    uv run tools/script.py --option value
"""

# Imports grouped: stdlib, third-party, local
import json
import os
import sys
import argparse

# Type hints
def my_function(input: str, count: int = 0) -> dict:
    """Function description."""
    return {"result": input}

# Main guard
if __name__ == "__main__":
    main()
```

### 10.2 Return Values

**Always return structured JSON:**

```python
# Success
{
    "success": True,
    "data": {...},
    "message": "Human-readable message"
}

# Failure
{
    "success": False,
    "error": "Error description",
    "details": {...}
}
```

### 10.3 Argparse Pattern

```python
def main():
    parser = argparse.ArgumentParser(
        description="Tool description",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Examples:\n  uv run script.py --option value"
    )

    parser.add_argument("--required-arg", required=True, help="Description")
    parser.add_argument("--optional-arg", default="default", help="Description")
    parser.add_argument("--flag", action="store_true", help="Description")

    args = parser.parse_args()

    result = do_work(args)
    print(json.dumps(result, indent=2))
```

### 10.4 File Paths

**Always use pathlib:**

```python
from pathlib import Path

# Get script directory
SCRIPT_DIR = Path(__file__).parent

# Get skill directory (parent of tools/)
SKILL_DIR = Path(__file__).parent.parent

# Build paths
DATA_FILE = SKILL_DIR / "data" / "tasks.json"
```

---

## 11. Common Modifications

### 11.1 Changing Default Model

In SKILL.md:
```yaml
default_model: opus  # Change from sonnet
```

In fork_terminal.py:
```python
parser.add_argument("--model", default="opus", ...)  # Change default
```

### 11.2 Adding External Dependencies

In the script's UV header:
```python
# /// script
# requires-python = ">=3.10"
# dependencies = ["requests", "pyyaml"]
# ///
```

UV will install these automatically when running.

### 11.3 Changing Terminal Behavior

**Windows** - In `spawn_terminal_windows()`:
```python
# Shell selection (use_cmd parameter)
if use_cmd:
    shell_args = ["cmd", "/k", command]      # For raw commands (supports &&)
else:
    shell_args = ["powershell", "-NoExit", "-Command", command]  # For Claude/Gemini

# Keep terminal open
"powershell", "-NoExit", "-Command", command   # PowerShell
"cmd", "/k", command                           # cmd.exe

# Close terminal after command
"powershell", "-Command", command              # PowerShell (remove -NoExit)
"cmd", "/c", command                           # cmd.exe (use /c instead of /k)

# Force new window instead of tab (use -w -1)
[terminal_path, "-w", "-1", "new-tab", ...]   # Opens in new window
```

**macOS** - In `spawn_terminal_macos()`:
```python
# Terminal always stays open after "do script"
# To close, you'd need to add: do script "cmd; exit"
```

**Linux** - In `spawn_terminal_linux()`:
```python
# Keep terminal open (current)
f'{command}; exec bash'

# Close terminal after command
command  # Without "; exec bash"
```

### 11.4 Adding Environment Variables

```python
import os

# Set before spawning
my_env = os.environ.copy()
my_env["MY_VAR"] = "value"

subprocess.run(cmd, env=my_env, ...)
```

---

## 12. Deployment

### 12.1 To Your Own Projects

Copy the skill:
```bash
cp -r .claude/ /path/to/your/project/
```

### 12.2 To Global Claude Config

Make available everywhere:
```bash
cp -r .claude/skills/fork-terminal ~/.claude/skills/
```

### 12.3 Packaging for Distribution

1. Ensure all paths are relative
2. Remove any local data (forked-tasks.json, logs)
3. Create a zip or tar:
   ```bash
   zip -r fork-terminal-skill.zip .claude/skills/fork-terminal
   ```

---

## 13. Contributing

### 13.1 Before Making Changes

1. Understand the architecture (read this guide)
2. Test existing functionality
3. Identify what you want to change
4. Consider backwards compatibility

### 13.2 Making Changes

1. Create a branch:
   ```bash
   git checkout -b feature/my-feature
   ```

2. Make changes

3. Test thoroughly

4. Update documentation

5. Commit with clear messages:
   ```bash
   git commit -m "feat: add my new feature"
   ```

### 13.3 Commit Message Convention

```
type: short description

Longer explanation if needed.

Types:
- feat: new feature
- fix: bug fix
- docs: documentation
- refactor: code restructuring
- test: adding tests
- chore: maintenance
```

### 13.4 Pull Request Checklist

- [ ] Code works as expected
- [ ] All tools return valid JSON
- [ ] SKILL.md updated if needed
- [ ] Cookbook updated if needed
- [ ] USER_GUIDE.md updated
- [ ] DEVELOPER_GUIDE.md updated
- [ ] QUICK_START.md updated if relevant
- [ ] No debug print statements left
- [ ] No hardcoded paths

---

## Appendix A: Full File Reference

| File | Lines | Purpose |
|------|-------|---------|
| SKILL.md | ~270 | Central skill definition |
| tools/fork_terminal.py | ~650 | Cross-platform terminal spawning |
| tools/task_registry.py | ~390 | Task tracking |
| tools/context_builder.py | ~300 | Context handoff |
| tools/worktree_manager.py | ~330 | Git worktrees |
| prompts/fork_summary_user_prompt.md | ~100 | How to generate context |
| prompts/fork-summary.md | ~50 | Template for forked agent |
| cookbook/claude-code.md | ~150 | Claude CLI reference |
| cookbook/presets.md | ~200 | Preset definitions |
| cookbook/worktree-guide.md | ~200 | Worktree patterns |

### Platform-Specific Functions in fork_terminal.py

| Function | Lines | Platform |
|----------|-------|----------|
| `find_terminal_executable()` | 62-109 | All |
| `spawn_terminal_windows()` | 140-244 | Windows |
| `spawn_terminal_macos()` | 247-312 | macOS |
| `spawn_terminal_linux()` | 315-407 | Linux |
| `spawn_terminal()` | 410-446 | Dispatcher |

## Appendix B: Technology Links

- **Python:** https://python.org
- **UV:** https://astral.sh/uv
- **Claude Code:** https://claude.ai/code
- **Git Worktrees:** https://git-scm.com/docs/git-worktree
- **Windows Terminal:** https://aka.ms/terminal
