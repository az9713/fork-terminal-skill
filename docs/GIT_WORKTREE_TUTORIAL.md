# Git Worktree Tutorial

A beginner-friendly guide to understanding and using Git worktrees, especially in the context of forking AI agents for parallel development.

## What is a Git Worktree?

A **worktree** is a separate working directory linked to the same Git repository. Think of it as having **multiple checkouts** of your repo at the same time.

```
Normal Git:
+----------------------------------+
|  my-project/                     |  <-- You can only be on ONE branch
|    .git/                         |
|    src/                          |
|    README.md                     |
|                                  |
|    Currently on: main            |
+----------------------------------+

With Worktrees:
+----------------------------------+     +----------------------------------+
|  my-project/                     |     |  my-project-feature/             |
|    .git/                         |     |    .git (link) ---------------+  |
|    src/                          |     |    src/                       |  |
|    README.md                     |     |    README.md                  |  |
|                                  |     |                               |  |
|    Currently on: main            |     |    Currently on: feature      |  |
+----------------------------------+     +-------------------------------+--+
                                                                         |
                                         Both share the same .git <------+
```

## Why Use Worktrees?

| Problem | Without Worktrees | With Worktrees |
|---------|-------------------|----------------|
| Work on 2 branches at once | `git stash`, switch, work, switch back, `git stash pop` | Just open the other folder |
| Run tests on main while coding on feature | Cannot - only one branch checked out | Each worktree has its own branch |
| Let an AI agent work on a fix | Agent changes might conflict with your work | Agent works in isolated worktree |
| Compare two versions side-by-side | Painful switching back and forth | Open both folders in editor |

## Basic Git Worktree Commands

```bash
# List all worktrees
git worktree list

# Create a new worktree with a new branch
git worktree add ../my-feature-worktree -b feature/my-feature

# Create a worktree for an existing branch
git worktree add ../hotfix-worktree hotfix/urgent-fix

# Remove a worktree (when done)
git worktree remove ../my-feature-worktree

# Force remove (if there are changes)
git worktree remove --force ../my-feature-worktree
```

## Real-World Example

```bash
# You are working on main
$ pwd
/projects/my-app

$ git branch
* main

# Create a worktree for a bugfix
$ git worktree add ../my-app-bugfix -b fix/login-bug
Preparing worktree (new branch 'fix/login-bug')
HEAD is now at abc1234 Latest commit

# Now you have TWO directories
$ ls ../
my-app/           # main branch
my-app-bugfix/    # fix/login-bug branch

# Work on bugfix WITHOUT leaving main
$ cd ../my-app-bugfix
$ # make changes, commit, push

# When done, remove worktree
$ cd ../my-app
$ git worktree remove ../my-app-bugfix
```

## How Fork Terminal Uses Worktrees

When you say **"Fork a Claude agent in a worktree"**:

```
+---------------------------------------------------------------------+
|  YOUR TERMINAL (main branch)                                        |
|                                                                     |
|  You: "Fork a Claude agent in a worktree to fix the login bug"     |
|                                                                     |
|  1. Skill creates worktree: ../project-fork-fix-login-abc123        |
|  2. New branch: fork/fix-login-abc123                               |
|  3. Spawns Claude in NEW terminal, working in the worktree          |
|                                                                     |
|  You continue working on main...                                    |
+---------------------------------------------------------------------+
                              |
                              v
+---------------------------------------------------------------------+
|  FORKED TERMINAL (worktree - separate branch)                       |
|                                                                     |
|  Claude works on fix/login-abc123 branch                            |
|  Makes changes, commits                                             |
|  Your main branch is UNTOUCHED                                      |
|                                                                     |
+---------------------------------------------------------------------+
                              |
                              v
                    When ready, you review and merge
```

## Benefits for AI Agents

| Benefit | Explanation |
|---------|-------------|
| **Isolation** | Agent cannot accidentally break your working code |
| **Safe experimentation** | If agent messes up, just delete the worktree |
| **Easy review** | Compare worktree changes before merging |
| **Parallel work** | Agent works on fix while you continue on main |

## Using Worktrees with Fork Terminal

### List Current Worktrees

```bash
uv run .claude/skills/fork-terminal/tools/worktree_manager.py list
```

### Create a Worktree

```bash
uv run .claude/skills/fork-terminal/tools/worktree_manager.py create \
  --branch fork/my-feature \
  --task "Description of what you are working on"
```

### Fork an Agent into a Worktree

Using natural language in Claude Code:
```
"Fork a Claude agent in a worktree to fix the authentication bug"
```

Or directly with the tool:
```bash
uv run .claude/skills/fork-terminal/tools/fork_terminal.py \
  --type claude \
  --task "Fix the authentication bug" \
  --model sonnet \
  --cwd /path/to/worktree
```

### Remove a Worktree

```bash
uv run .claude/skills/fork-terminal/tools/worktree_manager.py remove \
  --path /path/to/worktree
```

## Hands-On Example

Try this complete workflow:

### Step 1: Check Current Worktrees

```bash
uv run .claude/skills/fork-terminal/tools/worktree_manager.py list
```

You should see only your main worktree.

### Step 2: Create a Test Worktree

```bash
uv run .claude/skills/fork-terminal/tools/worktree_manager.py create \
  --branch fork/test-worktree \
  --task "Testing worktree functionality"
```

Note the worktree path in the output.

### Step 3: Verify the Worktree Exists

```bash
uv run .claude/skills/fork-terminal/tools/worktree_manager.py list
```

Now you should see two worktrees.

### Step 4: Fork an Agent to Work in the Worktree

```bash
uv run .claude/skills/fork-terminal/tools/fork_terminal.py \
  --type raw \
  --task "echo Hello from worktree > TEST.txt && dir" \
  --cwd <WORKTREE_PATH>
```

### Step 5: Clean Up

```bash
uv run .claude/skills/fork-terminal/tools/worktree_manager.py remove \
  --path <WORKTREE_PATH>
```

## Common Use Cases

### 1. Risky Refactoring

```bash
# Create isolated worktree for risky changes
uv run .claude/skills/fork-terminal/tools/worktree_manager.py create \
  --branch fork/risky-refactor \
  --task "Refactor authentication system"

# If it goes wrong, just delete the worktree
# Your main branch is safe
```

### 2. Parallel Bug Fixes

```bash
# Multiple agents can work on different bugs simultaneously
# Each in their own worktree, no conflicts
```

### 3. Code Review

```bash
# Create worktree to review someone's PR
git worktree add ../review-pr-123 origin/feature/pr-123

# Review, test, then remove
git worktree remove ../review-pr-123
```

## Key Points to Remember

1. **Worktrees share the same `.git` history** - commits in one are visible in all
2. **Each worktree must be on a different branch** - you cannot have two worktrees on `main`
3. **Worktrees are cheap** - they only duplicate working files, not the entire repo
4. **Clean up when done** - use `git worktree remove` to avoid clutter
5. **Perfect for AI agents** - isolates their work from your active development

## Further Reading

- [Git Worktree Documentation](https://git-scm.com/docs/git-worktree)
- [Fork Terminal Worktree Guide](../.claude/skills/fork-terminal/cookbook/worktree-guide.md)

---

*This tutorial is part of the Fork Terminal Skill project.*
