# Quick Start Guide

Welcome to Fork Terminal! This guide will get you up and running with 10 hands-on tutorials that progressively teach you the skill's features.

## What is Fork Terminal?

Fork Terminal lets you **spawn new terminal windows** to run AI agents or commands **in parallel**. Instead of handling everything in one Claude Code session, you can delegate tasks to separate agents that work independently.

Think of it like having multiple assistants working on different tasks simultaneously, each with their own fresh perspective.

## Prerequisites

Before starting, make sure you have:

1. **Claude Code installed and working**
   - You should be able to run `claude` in your terminal
   - If not, visit: https://claude.ai/code

2. **Windows Terminal** (recommended but optional)
   - Modern Windows 10/11 should have this
   - The skill falls back to PowerShell if not available

3. **Python with UV** (for running tool scripts)
   - Install UV: `pip install uv`
   - Or: `curl -LsSf https://astral.sh/uv/install.sh | sh`

4. **This project cloned/downloaded**
   - You should be in the `agent_skill_dan` directory

## Verify Your Setup

Open a terminal in the `agent_skill_dan` directory and run:

```bash
uv run .claude/skills/fork-terminal/tools/task_registry.py status
```

You should see:
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

If this works, you're ready to go!

---

# 10 Hands-On Tutorials

## Tutorial 1: Your First Fork (Hello World)

**Goal:** Learn to spawn a simple terminal window.

**What you'll do:** Open a new terminal that displays a message.

### Steps

1. Open your terminal in the `agent_skill_dan` directory

2. Run this command:
   ```bash
   uv run .claude/skills/fork-terminal/tools/fork_terminal.py --type raw --task "echo Hello from Fork Terminal!" --no-output
   ```

3. **What happens:**
   - A new terminal window/tab opens
   - It displays "Hello from Fork Terminal!"
   - The window stays open so you can see the result

4. **What you learned:**
   - `--type raw` means run a raw CLI command
   - `--task` is the command to execute
   - `--no-output` skips logging the output to a file

### Try It Yourself

Change the message:
```bash
uv run .claude/skills/fork-terminal/tools/fork_terminal.py --type raw --task "echo My name is [YOUR NAME]" --no-output
```

---

## Tutorial 2: Track Your Tasks

**Goal:** Learn to use the task registry.

**What you'll do:** Add tasks, check status, and update them.

### Steps

1. **Add a task to the registry:**
   ```bash
   uv run .claude/skills/fork-terminal/tools/task_registry.py add --task "Fix login bug" --type claude --model sonnet
   ```

   You'll see a JSON response with a task ID (like `abc12345`).

2. **Check the status:**
   ```bash
   uv run .claude/skills/fork-terminal/tools/task_registry.py status
   ```

   You'll see your task listed as "running".

3. **List all tasks:**
   ```bash
   uv run .claude/skills/fork-terminal/tools/task_registry.py list
   ```

4. **Mark the task as completed** (use your actual task ID):
   ```bash
   uv run .claude/skills/fork-terminal/tools/task_registry.py update --id YOUR_TASK_ID --status completed
   ```

5. **Check status again:**
   ```bash
   uv run .claude/skills/fork-terminal/tools/task_registry.py status
   ```

   Now it shows 1 completed task.

### What You Learned

- Tasks are tracked in `data/forked-tasks.json`
- You can see what's running, completed, or failed
- This helps manage multiple forked agents

---

## Tutorial 3: Run Multiple Commands in Parallel

**Goal:** Experience the power of parallel execution.

**What you'll do:** Open three terminals at once, each doing something different.

### Steps

1. **Open Terminal 1 - Show date:**
   ```bash
   uv run .claude/skills/fork-terminal/tools/fork_terminal.py --type raw --task "date /t && echo Terminal 1 done" --no-output
   ```

2. **Immediately open Terminal 2 - Show time:**
   ```bash
   uv run .claude/skills/fork-terminal/tools/fork_terminal.py --type raw --task "time /t && echo Terminal 2 done" --no-output
   ```

3. **Immediately open Terminal 3 - Show directory:**
   ```bash
   uv run .claude/skills/fork-terminal/tools/fork_terminal.py --type raw --task "dir && echo Terminal 3 done" --no-output
   ```

4. **Observe:**
   - All three terminals opened nearly instantly
   - They ran in parallel, not one after another
   - Each has its own independent window

### What You Learned

- You can spawn multiple terminals quickly
- Each runs independently
- This is the foundation of parallel agent workflows

---

## Tutorial 4: Fork a Claude Code Agent

**Goal:** Spawn a Claude Code instance in a new terminal.

**What you'll do:** Create a new Claude session with a specific task.

### Steps

1. **Spawn Claude with a simple task:**
   ```bash
   uv run .claude/skills/fork-terminal/tools/fork_terminal.py --type claude --task "List the files in the current directory and tell me what each one does" --model haiku
   ```

2. **What happens:**
   - A new terminal opens
   - Claude Code starts with your task
   - It begins working on listing files

3. **Check your task registry:**
   ```bash
   uv run .claude/skills/fork-terminal/tools/task_registry.py status
   ```

### What You Learned

- `--type claude` spawns Claude Code
- `--model haiku` uses the fast Haiku model
- The forked Claude has a fresh context window

### Model Selection Guide

| Model | When to Use |
|-------|-------------|
| haiku | Quick tasks, simple fixes, fast responses |
| sonnet | Balanced tasks, most development work |
| opus | Complex reasoning, architecture decisions |

---

## Tutorial 5: Context Handoff

**Goal:** Learn to pass context to a forked agent.

**What you'll do:** Create a context file and pass it to a fork.

### Steps

1. **Preview what a context file looks like:**
   ```bash
   uv run .claude/skills/fork-terminal/tools/context_builder.py --task "Fix the authentication bug" --context "We found a null pointer in user.email validation" --preview
   ```

   This shows you the formatted context without saving it.

2. **Create an actual context file:**
   ```bash
   uv run .claude/skills/fork-terminal/tools/context_builder.py --task "Fix the authentication bug" --context "We found a null pointer in user.email validation" --files src/auth.ts src/user.ts
   ```

   Note the `context_file` path in the output.

3. **Use the context file with a fork:**
   ```bash
   uv run .claude/skills/fork-terminal/tools/fork_terminal.py --type claude --task "Fix the bug described in context" --with-context PATH_TO_CONTEXT_FILE --model sonnet
   ```

### What You Learned

- Context handoff passes information to forked agents
- The forked agent knows what you were working on
- This prevents starting from zero

---

## Tutorial 6: Git Worktree Integration

**Goal:** Create an isolated workspace for a forked agent.

**What you'll do:** Create a git worktree for safe experimentation.

### Steps

1. **Make sure you're in a git repository** (this project is one):
   ```bash
   git status
   ```

2. **List current worktrees:**
   ```bash
   uv run .claude/skills/fork-terminal/tools/worktree_manager.py list
   ```

   You'll see just the main worktree.

3. **Create a new worktree for experimentation:**
   ```bash
   uv run .claude/skills/fork-terminal/tools/worktree_manager.py create --branch fork/experiment --task "Test a risky change"
   ```

4. **List worktrees again:**
   ```bash
   uv run .claude/skills/fork-terminal/tools/worktree_manager.py list
   ```

   Now you see two worktrees!

5. **Clean up** (remove the worktree):
   ```bash
   uv run .claude/skills/fork-terminal/tools/worktree_manager.py remove --path PATH_FROM_STEP_3
   ```

### What You Learned

- Worktrees let forked agents work in isolation
- Changes don't affect your main workspace
- You can review and merge when ready

---

## Tutorial 7: Using Presets

**Goal:** Understand the built-in presets for common tasks.

**What you'll do:** Learn about the preset configurations.

### Steps

1. **Read the presets documentation:**

   Open `.claude/skills/fork-terminal/cookbook/presets.md` and look at:
   - `bugfix` - For quick bug fixes
   - `research` - For exploration tasks
   - `tests` - For running and fixing tests
   - `review` - For code review

2. **In a Claude Code session, you would use:**
   ```
   /fork bugfix "null pointer in line 42"
   /fork research "how does authentication work here"
   /fork tests
   /fork review
   ```

3. **Presets automatically set:**
   - Model tier (haiku for tests, opus for research)
   - Context handoff (on/off)
   - Task template

### What You Learned

- Presets are shortcuts for common patterns
- They encode best practices
- You can add your own presets

---

## Tutorial 8: Capture Output to Logs

**Goal:** Save forked agent output for later review.

**What you'll do:** Fork with output capture enabled.

### Steps

1. **Fork WITHOUT --no-output (output capture enabled by default):**
   ```bash
   uv run .claude/skills/fork-terminal/tools/fork_terminal.py --type raw --task "echo This will be logged"
   ```

2. **Check the response** - note the `output_file` path

3. **Look at the logs directory:**
   ```bash
   ls .claude/skills/fork-terminal/logs/forks/
   ```

   You'll see log files named like `2024-12-27_this-will-be-logged_abc123.md`

4. **View the log:**
   ```bash
   cat .claude/skills/fork-terminal/logs/forks/YOUR_LOG_FILE.md
   ```

### What You Learned

- Output is automatically captured to log files
- Logs help you review what forked agents did
- Use `--no-output` to skip logging for quick tasks

---

## Tutorial 9: Clean Up Completed Tasks

**Goal:** Manage your task registry.

**What you'll do:** Clear old tasks from the registry.

### Steps

1. **Check current status:**
   ```bash
   uv run .claude/skills/fork-terminal/tools/task_registry.py status
   ```

2. **Clear completed tasks:**
   ```bash
   uv run .claude/skills/fork-terminal/tools/task_registry.py clear --status completed
   ```

3. **Clear failed tasks:**
   ```bash
   uv run .claude/skills/fork-terminal/tools/task_registry.py clear --status failed
   ```

4. **Clear everything (use with caution!):**
   ```bash
   uv run .claude/skills/fork-terminal/tools/task_registry.py clear --status all
   ```

5. **Verify it's clean:**
   ```bash
   uv run .claude/skills/fork-terminal/tools/task_registry.py status
   ```

### What You Learned

- Task registry can grow over time
- Cleaning up keeps things manageable
- You can selectively clear by status

---

## Tutorial 10: Complete Workflow

**Goal:** Put it all together in a realistic scenario.

**Scenario:** You're working on a bug and want to delegate the fix to a forked agent while you continue with other work.

### Steps

1. **Create context for the forked agent:**
   ```bash
   uv run .claude/skills/fork-terminal/tools/context_builder.py \
     --task "Fix the login timeout bug - users are getting logged out after 5 minutes instead of 30" \
     --context "Working on auth module refactor. Found this bug during testing. The session timeout is set in config.ts but something is overriding it." \
     --files config.ts auth/session.ts
   ```

   Note the `context_file` path from the output.

2. **Spawn a forked Claude to fix the bug:**
   ```bash
   uv run .claude/skills/fork-terminal/tools/fork_terminal.py \
     --type claude \
     --task "Fix the login timeout bug" \
     --model sonnet \
     --with-context PATH_TO_CONTEXT_FILE
   ```

3. **Register the task:**
   ```bash
   uv run .claude/skills/fork-terminal/tools/task_registry.py add \
     --task "Fix login timeout bug" \
     --type claude \
     --model sonnet
   ```

4. **Check status periodically:**
   ```bash
   uv run .claude/skills/fork-terminal/tools/task_registry.py status
   ```

5. **When the forked agent completes, mark it done:**
   ```bash
   uv run .claude/skills/fork-terminal/tools/task_registry.py update \
     --id YOUR_TASK_ID \
     --status completed \
     --notes "Bug fixed - timeout was being overridden in middleware"
   ```

### What You Learned

- Context handoff + forking creates powerful delegation
- Task tracking keeps you organized
- You can continue working while forked agents handle tasks

---

## Next Steps

Now that you've completed all 10 tutorials, you can:

1. **Read the full User Guide:** `docs/USER_GUIDE.md`
2. **Explore the skill definition:** `.claude/skills/fork-terminal/SKILL.md`
3. **Customize presets:** Edit `.claude/skills/fork-terminal/cookbook/presets.md`
4. **Use in real projects:** Copy `.claude/` to your own projects

## Troubleshooting

### "Command not found: uv"
Install UV: `pip install uv` or visit https://astral.sh/uv

### No new terminal opens
- Make sure Windows Terminal is installed
- The skill falls back to PowerShell if not found

### "Not in a git repository" for worktrees
- Worktrees require a git repo
- Run `git init` if you want to use worktrees

### JSON parsing errors
- Check your command syntax
- Make sure quotes are properly escaped

---

## Congratulations!

You've completed the Fork Terminal Quick Start Guide. You now understand:

- How to spawn terminals with raw commands
- How to fork Claude Code agents
- How to track tasks
- How to pass context between agents
- How to use git worktrees for isolation
- How to use presets
- How to capture and review output

Happy forking! 🚀
