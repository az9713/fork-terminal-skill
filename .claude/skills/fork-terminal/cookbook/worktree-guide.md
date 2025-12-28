# Git Worktree Integration Guide

Use git worktrees for isolated fork environments.

## What Are Worktrees?

Git worktrees allow you to have multiple branches checked out simultaneously in separate directories. Each worktree is a separate working copy that shares the same `.git` repository.

## Why Use Worktrees with Forks?

### 1. Isolation

Forked agent can make changes without affecting your main workspace:
- Experimental changes stay separate
- Failed attempts don't pollute main branch
- Easy to discard or merge

### 2. Parallel Work

Multiple agents can work on different branches simultaneously:
- Main session continues on feature-A
- Forked agent works on bug-fix in worktree
- Another fork works on tests in another worktree

### 3. Safety

Easy to review before merging:
- Changes are on a separate branch
- Can review diff before merging
- Rollback is just deleting the worktree

### 4. Clean Merges

Work is done on proper branches:
- Standard git workflow applies
- PR-ready branches
- Clean history

## Creating a Worktree Fork

### Via Natural Language

Say: "Fork a Claude agent in a worktree to implement feature X"

This will:
1. Create a new branch: `fork/feature-x-{timestamp}`
2. Create worktree at `../{repo-name}-worktrees/fork-feature-x-{timestamp}`
3. Spawn Claude in the worktree directory

### Via Tool Directly

```bash
uv run tools/worktree_manager.py create --branch fork/my-feature --task "implement feature"
```

## Worktree Directory Structure

```
projects/
├── my-repo/                    # Your main repository
│   ├── .git/
│   ├── src/
│   └── ...
└── my-repo-worktrees/          # Worktrees directory (sibling)
    ├── fork-feature-a-20241227/
    ├── fork-bugfix-20241227/
    └── fork-tests-20241227/
```

Worktrees are created as siblings to your main repo for easy management.

## Managing Worktrees

### List All Worktrees

```bash
uv run tools/worktree_manager.py list
```

Or directly with git:
```bash
git worktree list
```

### Remove a Worktree

```bash
uv run tools/worktree_manager.py remove --path ../my-repo-worktrees/fork-feature-a
```

Or with force (uncommitted changes):
```bash
uv run tools/worktree_manager.py remove --path ../my-repo-worktrees/fork-feature-a --force
```

### Clean Up Stale Entries

```bash
uv run tools/worktree_manager.py prune
```

## After Fork Completes

### 1. Review Changes

Navigate to worktree and review:
```bash
cd ../my-repo-worktrees/fork-feature-a
git diff main
git log --oneline main..HEAD
```

### 2. Merge or Cherry-Pick

From your main repo:
```bash
# Merge the branch
git merge fork/feature-a

# Or cherry-pick specific commits
git cherry-pick <commit-hash>
```

### 3. Clean Up

```bash
# Remove the worktree
uv run tools/worktree_manager.py remove --path ../my-repo-worktrees/fork-feature-a

# Delete the branch
git branch -d fork/feature-a
```

## Best Practices

### 1. Use Descriptive Branch Names

Say: "Fork a Claude agent in a worktree to fix auth bug"
```
# Creates: fork/fix-auth-bug-{timestamp}
```

### 2. Clean Up After Merging

Don't leave worktrees lying around:
```bash
# List worktrees
git worktree list

# Remove merged ones
git worktree remove ../my-repo-worktrees/old-worktree
```

### 3. Limit Active Worktrees

Too many worktrees can be confusing:
- Keep only active work in worktrees
- Clean up completed forks
- Prune periodically

### 4. Disk Space

Worktrees are relatively light (share .git), but:
- node_modules, build artifacts are duplicated
- Consider .gitignore for heavy directories
- Clean up to save space

## Troubleshooting

### "Branch already exists"

The branch name was already used:
```bash
# Use existing branch
git worktree add ../worktree existing-branch

# Or create with different name
git worktree add -b new-branch-name ../worktree
```

### "Worktree already exists"

A worktree is already at that path:
```bash
# List worktrees to see what's there
git worktree list

# Remove if stale
git worktree remove path/to/worktree
```

### "Uncommitted changes"

Worktree has uncommitted work:
```bash
# Commit or stash first
cd ../worktree
git stash  # or git commit

# Or force remove (loses changes!)
git worktree remove --force path/to/worktree
```

## Example Workflow

```bash
# 1. Start a complex refactor in worktree
# Say: "Fork a Claude agent in a worktree to refactor auth module to use dependency injection"

# 2. Check status
# Say: "Show fork status"
# Shows: fork-refactor-auth-20241227 (running)

# 3. When complete, review
cd ../my-repo-worktrees/fork-refactor-auth-20241227
git log --oneline main..HEAD
git diff main

# 4. Merge if satisfied
cd ../my-repo
git merge fork/refactor-auth-20241227

# 5. Clean up
git worktree remove ../my-repo-worktrees/fork-refactor-auth-20241227
git branch -d fork/refactor-auth-20241227
```
