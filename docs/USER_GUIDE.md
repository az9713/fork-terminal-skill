# User Guide

Complete reference for using the Fork Terminal skill. This guide assumes no prior experience with AI coding assistants or advanced terminal operations.

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Core Concepts](#2-core-concepts)
3. [Installation & Setup](#3-installation--setup)
4. [Basic Usage](#4-basic-usage)
5. [Commands Reference](#5-commands-reference)
6. [Flags & Options](#6-flags--options)
7. [Presets](#7-presets)
8. [Context Handoff](#8-context-handoff)
9. [Git Worktrees](#9-git-worktrees)
10. [Task Management](#10-task-management)
11. [Output & Logging](#11-output--logging)
12. [Best Practices](#12-best-practices)
13. [Troubleshooting](#13-troubleshooting)
14. [Glossary](#14-glossary)

---

## 1. Introduction

### What is Fork Terminal?

Fork Terminal is a **Claude Code skill** that lets you spawn new terminal windows to run AI agents or commands in parallel with your main session.

### Why Use It?

**Without Fork Terminal:**
- You work on a feature in Claude Code
- You find a bug that needs fixing
- You stop your feature work to fix the bug
- You lose focus and context
- When done, you have to remember where you were

**With Fork Terminal:**
- You work on a feature in Claude Code
- You find a bug that needs fixing
- You say: "fork a claude agent to fix this bug"
- A new terminal opens with a fresh Claude working on the bug
- You continue your feature work uninterrupted
- The forked agent fixes the bug independently

### Key Benefits

| Benefit | Description |
|---------|-------------|
| **Parallel Work** | Multiple agents work simultaneously |
| **Fresh Context** | Forked agents start clean, without your session's history |
| **Focus** | Delegate routine tasks, stay focused on complex work |
| **Organization** | Track what's running, completed, or failed |
| **Isolation** | Use worktrees to safely experiment |

---

## 2. Core Concepts

### 2.1 What is a "Fork"?

A **fork** is a new terminal window running either:
- **Claude Code** - An AI coding assistant
- **Gemini CLI** - Google's AI assistant (if enabled)
- **Raw CLI** - Any command-line command

When you fork, you're creating an independent session that works separately from your main session.

### 2.2 In-Loop vs Out-of-Loop

This terminology comes from IndyDevDan's agentic coding philosophy:

**In-Loop Coding:**
- High presence, high effort
- You're actively working with the agent
- Complex, new development work
- Requires your attention and decisions

**Out-of-Loop Coding:**
- Low presence, automated
- Forked agents handle tasks independently
- Routine fixes, tests, small chores
- You check results later

**Rule of Thumb:** Fork things that don't need your active attention.

### 2.3 Fresh Context Windows

Every forked agent starts with a **fresh context window**. This means:

- It hasn't seen your conversation history
- It approaches problems with fresh eyes
- It won't be confused by earlier debugging attempts
- You control exactly what context it receives

IndyDevDan says:
> "It's easy to know what your agent has seen when it's seen nothing."

### 2.4 The Skill Structure

```
.claude/skills/fork-terminal/
├── SKILL.md              # Central definition (Claude reads this first)
├── tools/                # Python scripts that do the actual work
├── prompts/              # Templates for different scenarios
├── cookbook/             # Reference documentation (loaded on demand)
├── data/                 # Runtime data (task registry)
└── logs/                 # Output logs from forked agents
```

---

## 3. Installation & Setup

### 3.1 Prerequisites

Before using Fork Terminal, you need:

#### Claude Code
Claude Code must be installed and working on your system.

**To check:** Open a terminal and type:
```bash
claude --version
```

If this shows a version number, you're good. If not, visit https://claude.ai/code to install.

#### Python with UV

UV is a fast Python package runner that executes the tool scripts.

**To check:** Type:
```bash
uv --version
```

**To install UV:**
```bash
pip install uv
```

Or on Unix/Mac:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### Terminal (Platform-Specific)

The skill automatically detects and uses the best available terminal:

| Platform | Primary | Fallback |
|----------|---------|----------|
| **Windows** | Windows Terminal (wt.exe) | PowerShell |
| **macOS** | Terminal.app (via osascript) | - |
| **Linux** | gnome-terminal, konsole, xfce4-terminal | xterm |

**Windows Shell Selection:**
- **Raw commands** (`--type raw`): Uses **cmd.exe** - supports `&&`, `||`, and other cmd operators
- **Claude/Gemini commands**: Uses **PowerShell** - supports output logging with `Tee-Object`

**Windows - Check Windows Terminal:**
```bash
wt --version
```

**macOS - Check osascript:**
```bash
osascript -e 'return "ok"'
```

**Linux - Check available terminals:**
```bash
which gnome-terminal konsole xfce4-terminal xterm
```

If the primary terminal is not available, the skill automatically falls back to alternatives.

### 3.2 Project Setup

The skill is located in `.claude/skills/fork-terminal/` within this project.

**To use in this project:** Just start Claude Code in this directory. The skill will be automatically available.

**To use in other projects:** Copy the `.claude/` folder to your other projects:
```bash
cp -r .claude/ /path/to/your/project/
```

### 3.3 Verify Installation

Run this command to verify everything works:

```bash
uv run .claude/skills/fork-terminal/tools/task_registry.py status
```

Expected output:
```json
{
  "summary": {
    "total": 0,
    "running": 0,
    "completed": 0,
    "failed": 0
  },
  ...
}
```

---

## 4. Basic Usage

### 4.1 In Claude Code Sessions

When you're in a Claude Code session, you can use natural language:

```
"Fork a new terminal to run npm test"

"Spawn a claude agent to fix the bug in auth.ts"

"Delegate this task to a new agent: update the README"
```

Or use slash commands:

```
/fork claude "fix the login bug"

/fork raw "npm run build"

/fork raw "echo Hello && pause"   # Windows: && works because raw uses cmd.exe

/fork status
```

### 4.2 Direct Tool Usage

You can also run the tools directly from the command line:

```bash
# Spawn a terminal
uv run .claude/skills/fork-terminal/tools/fork_terminal.py --type raw --task "echo hello"

# Check status
uv run .claude/skills/fork-terminal/tools/task_registry.py status
```

### 4.3 Understanding the Response

When you fork, you get a JSON response like:

```json
{
  "success": true,
  "task_id": "abc12345",
  "fork_type": "claude",
  "task": "fix the login bug",
  "model": "sonnet",
  "platform": "Windows",
  "new_window": false,
  "message": "Forked claude agent spawned successfully on Windows"
}
```

Key fields:
- `success`: Whether the fork worked
- `task_id`: Unique ID to track this task
- `platform`: Operating system (Windows, Darwin, Linux)
- `new_window`: Whether `--new-window` flag was used
- `message`: Human-readable status

---

## 5. Commands Reference

### 5.1 Fork Commands

| Command | Description |
|---------|-------------|
| `/fork claude <task>` | Spawn Claude Code with a task |
| `/fork gemini <task>` | Spawn Gemini CLI (if enabled) |
| `/fork raw <command>` | Run a CLI command |

### 5.2 Management Commands

| Command | Description |
|---------|-------------|
| `/fork status` | Show summary of all tasks |
| `/fork list` | List all tracked forks |
| `/fork kill <id>` | Mark a task as failed/killed |
| `/fork kill all` | Mark all running tasks as failed |

### 5.3 Preset Commands

| Command | Description |
|---------|-------------|
| `/fork bugfix <description>` | Quick bug fix agent (haiku model) |
| `/fork research <topic>` | Deep research agent (opus model) |
| `/fork tests` | Run and fix tests (haiku model) |
| `/fork review` | Code review agent (sonnet model) |

---

## 6. Flags & Options

Flags modify how forks behave. Add them after the task description.

### 6.1 Model Selection

```
/fork claude "complex task" --model opus
/fork claude "quick fix" --model haiku
```

| Model | Speed | Capability | Best For |
|-------|-------|------------|----------|
| haiku | Fast | Basic | Quick fixes, simple tasks |
| sonnet | Medium | Balanced | Most development work |
| opus | Slow | Advanced | Complex reasoning, architecture |

### 6.2 Context Handoff

```
/fork claude "continue this work" --with-context
```

Passes a summary of your current work to the forked agent.

### 6.3 Worktree Isolation

```
/fork claude "experimental feature" --worktree
```

Creates a git worktree so changes are isolated from your main branch.

### 6.4 Skip Output Logging

```
/fork raw "quick command" --no-output
```

Doesn't save output to log files. Good for quick, throwaway commands.

### 6.5 Trusted Automation

```
/fork claude "automated task" --skip-permissions
```

Adds `--dangerously-skip-permissions` to Claude. Only use for fully trusted automation.

### 6.6 New Window (Windows Only)

```
/fork raw "my command" --new-window
```

Forces Windows Terminal to open a **new window** instead of a new **tab**.

| Flag | Behavior |
|------|----------|
| (default) | Opens as a new tab in existing Windows Terminal |
| `--new-window` | Opens as a separate window |

**Note:** This flag only affects Windows Terminal. On macOS and Linux, terminals always open as new windows.

---

## 7. Presets

Presets are pre-configured fork patterns for common scenarios.

### 7.1 Bugfix Preset

**Purpose:** Quick bug fixes
**Model:** Sonnet (balanced)
**Context:** Enabled

```
/fork bugfix "null pointer in user.email at line 42"
```

The agent will:
1. Find the root cause
2. Implement a minimal fix
3. Add a regression test if appropriate
4. Commit with a "fix:" message

### 7.2 Research Preset

**Purpose:** Deep exploration
**Model:** Opus (powerful)
**Context:** Enabled

```
/fork research "how does authentication work in this codebase"
```

The agent will:
1. Explore the codebase
2. Document findings
3. Provide insights and recommendations

### 7.3 Tests Preset

**Purpose:** Run and fix tests
**Model:** Haiku (fast)
**Context:** Disabled (fresh perspective)

```
/fork tests
```

The agent will:
1. Run the test suite
2. Identify failures
3. Fix issues
4. Re-run to verify

### 7.4 Review Preset

**Purpose:** Code review
**Model:** Sonnet (balanced)
**Context:** Enabled

```
/fork review
```

The agent will:
1. Review recent changes
2. Check for bugs, security issues
3. Suggest improvements

### 7.5 Custom Presets

You can add your own presets by editing:
`.claude/skills/fork-terminal/cookbook/presets.md`

---

## 8. Context Handoff

Context handoff passes information from your current session to a forked agent.

### 8.1 Why Use Context Handoff?

Without context, the forked agent knows nothing about:
- What you were working on
- What files are relevant
- What decisions you've made
- What approaches you've tried

With context, the agent has relevant background to work more effectively.

### 8.2 What Gets Passed

When you use `--with-context`, the summary includes:

1. **The Delegated Task** - What the agent should do
2. **Background Context** - What you were working on
3. **Key Files** - Relevant file paths
4. **Decisions Made** - Things not to undo
5. **Current State** - What's working/broken

### 8.3 How to Use

**In Claude Code:**
```
/fork claude "fix the auth bug" --with-context
```

**Direct tool usage:**
```bash
# Create context file
uv run .claude/skills/fork-terminal/tools/context_builder.py \
  --task "fix the auth bug" \
  --context "Found during login refactor" \
  --files src/auth.ts tests/auth.test.ts

# Use it with fork
uv run .claude/skills/fork-terminal/tools/fork_terminal.py \
  --type claude \
  --task "fix the auth bug" \
  --with-context path/to/context/file.md
```

### 8.4 Best Practices

**DO:**
- Include specific file paths
- Mention constraints (things not to change)
- Describe current state clearly

**DON'T:**
- Include irrelevant history
- Pass entire conversation logs
- Over-explain (keep it under 500 words)

---

## 9. Git Worktrees

Worktrees let forked agents work in isolated copies of your repository.

### 9.1 What is a Worktree?

A git worktree is a separate working directory that shares the same git repository. It's like having multiple checkouts of your repo at once.

```
projects/
├── my-repo/                    # Your main work
└── my-repo-worktrees/          # Worktrees created by forks
    ├── fork-fix-auth/
    └── fork-new-feature/
```

### 9.2 Why Use Worktrees?

| Reason | Explanation |
|--------|-------------|
| **Safety** | Forked agent changes don't affect your main work |
| **Parallel branches** | Multiple agents can work on different features |
| **Easy review** | Review changes before merging |
| **Easy rollback** | Just delete the worktree if it fails |

### 9.3 How to Use

**In Claude Code:**
```
/fork claude "experimental refactor" --worktree
```

**Direct tool usage:**
```bash
# Create worktree
uv run .claude/skills/fork-terminal/tools/worktree_manager.py create \
  --branch fork/my-feature \
  --task "implement feature X"

# List worktrees
uv run .claude/skills/fork-terminal/tools/worktree_manager.py list

# Remove worktree
uv run .claude/skills/fork-terminal/tools/worktree_manager.py remove \
  --path path/to/worktree
```

### 9.4 After Fork Completes

1. Review the changes in the worktree
2. If good, merge to your main branch:
   ```bash
   git merge fork/my-feature
   ```
3. Clean up:
   ```bash
   uv run .claude/skills/fork-terminal/tools/worktree_manager.py remove --path path/to/worktree
   git branch -d fork/my-feature
   ```

---

## 10. Task Management

### 10.1 Task States

| State | Meaning |
|-------|---------|
| `running` | Task is currently in progress |
| `completed` | Task finished successfully |
| `failed` | Task failed or was killed |

### 10.2 Checking Status

**Summary view:**
```bash
uv run .claude/skills/fork-terminal/tools/task_registry.py status
```

**List all tasks:**
```bash
uv run .claude/skills/fork-terminal/tools/task_registry.py list
```

**Filter by status:**
```bash
uv run .claude/skills/fork-terminal/tools/task_registry.py list --filter running
```

### 10.3 Updating Tasks

**Mark as completed:**
```bash
uv run .claude/skills/fork-terminal/tools/task_registry.py update \
  --id TASK_ID \
  --status completed \
  --notes "Bug fixed, tests passing"
```

**Mark as failed:**
```bash
uv run .claude/skills/fork-terminal/tools/task_registry.py update \
  --id TASK_ID \
  --status failed \
  --notes "Couldn't reproduce the issue"
```

### 10.4 Cleaning Up

**Remove one task:**
```bash
uv run .claude/skills/fork-terminal/tools/task_registry.py remove --id TASK_ID
```

**Clear completed:**
```bash
uv run .claude/skills/fork-terminal/tools/task_registry.py clear --status completed
```

**Clear all:**
```bash
uv run .claude/skills/fork-terminal/tools/task_registry.py clear --status all
```

---

## 11. Output & Logging

### 11.1 Where Logs Go

Output from forked agents is saved to:
```
.claude/skills/fork-terminal/logs/forks/
```

Files are named:
```
YYYY-MM-DD_task-description_taskid.md
```

### 11.2 Enabling/Disabling Logging

Logging is **enabled by default**.

To disable for a specific fork:
```
/fork raw "quick command" --no-output
```

### 11.3 Viewing Logs

```bash
# List log files
ls .claude/skills/fork-terminal/logs/forks/

# View a specific log
cat .claude/skills/fork-terminal/logs/forks/2024-12-27_fix-bug_abc123.md
```

---

## 12. Best Practices

### 12.1 When to Fork

**Good candidates for forking:**
- Bug fixes (especially ones you find while doing other work)
- Running tests
- Documentation updates
- Small refactors
- Research and exploration
- Code review

**Keep in your main session:**
- Complex new features
- Architecture decisions
- Anything requiring back-and-forth discussion

### 12.2 Be Specific

**Bad:** "Fix the bugs"
**Good:** "Fix the null pointer in src/auth.ts:42 where user.email is undefined"

### 12.3 Use Appropriate Models

- **Haiku** for quick, simple tasks
- **Sonnet** for most development work
- **Opus** for complex reasoning

### 12.4 Review Before Merging

Always review what forked agents did before merging:
- Check the changes make sense
- Verify tests pass
- Look for unintended side effects

### 12.5 Clean Up Regularly

Don't let your task registry grow forever:
```bash
uv run .claude/skills/fork-terminal/tools/task_registry.py clear --status completed
```

---

## 13. Troubleshooting

### Problem: "Command not found: uv"

**Solution:** Install UV:
```bash
pip install uv
```

### Problem: No new terminal opens

**Possible causes (by platform):**

**Windows:**
1. Windows Terminal not installed
2. PowerShell execution policy restricted

**macOS:**
1. Terminal.app permissions not granted
2. osascript blocked by security settings

**Linux:**
1. No supported terminal emulator installed
2. Display server not running (for headless systems)

**Solutions:**

**Windows:**
- Install Windows Terminal from Microsoft Store
- The skill should fall back to PowerShell automatically
- Check execution policy: `Get-ExecutionPolicy`

**macOS:**
- Grant Terminal access in System Preferences > Security & Privacy > Privacy > Automation
- Test manually: `osascript -e 'tell application "Terminal" to activate'`

**Linux:**
- Install a terminal: `sudo apt install gnome-terminal` (Ubuntu/Debian)
- Ensure X11/Wayland is running
- Check which terminal is available: `which gnome-terminal konsole xterm`

### Problem: "Not in a git repository" when using --worktree

**Solution:** Worktrees require a git repository. Either:
- Run `git init` to create one
- Don't use the `--worktree` flag

### Problem: Fork fails to spawn

**Check:**
1. Is Claude Code installed? (`claude --version`)
2. Is the path correct?
3. Are there special characters in the task that need escaping?

### Problem: Task registry shows wrong status

**Solution:** Manually update the status:
```bash
uv run .claude/skills/fork-terminal/tools/task_registry.py update \
  --id TASK_ID \
  --status completed
```

### Problem: Output file not created

**Check:**
- Did you use `--no-output`?
- Does the logs directory exist?
- Do you have write permissions?

---

## 14. Glossary

| Term | Definition |
|------|------------|
| **Fork** | Spawning a new terminal/agent session |
| **Claude Code** | Anthropic's AI coding assistant CLI |
| **Context Window** | The "memory" an AI agent has of the conversation |
| **Context Handoff** | Passing information from one agent to another |
| **Worktree** | A separate working directory linked to the same git repo |
| **Pivot File** | The central SKILL.md that organizes the skill |
| **Cookbook** | Reference documentation loaded on demand |
| **Preset** | Pre-configured fork pattern for common tasks |
| **Task Registry** | JSON file tracking all forked tasks |
| **In-Loop** | Active, high-attention work with an agent |
| **Out-of-Loop** | Delegated work that runs independently |
| **UV** | Fast Python package runner |
| **Model Tier** | Quality level of AI model (haiku < sonnet < opus) |

---

## Need More Help?

- **Quick Start:** See `docs/QUICK_START.md` for hands-on tutorials
- **Developer Guide:** See `docs/DEVELOPER_GUIDE.md` if you want to modify the skill
- **SKILL.md:** Read `.claude/skills/fork-terminal/SKILL.md` for the full skill definition
