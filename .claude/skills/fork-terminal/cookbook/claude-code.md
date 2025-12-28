# Claude Code CLI Reference

Progressive disclosure documentation for Claude Code CLI usage in forks.

## Basic Usage

```bash
# Interactive mode (recommended for forks - no -p flag)
claude "your task here"

# Non-interactive/print mode (for automation scripts)
claude -p "your task here"

# With model selection
claude --model claude-sonnet-4-20250514 "task"
```

## Model Options

| Tier | Model ID | Best For |
|------|----------|----------|
| haiku | claude-3-5-haiku-20241022 | Fast, simple tasks, quick fixes |
| sonnet | claude-sonnet-4-20250514 | Balanced (default), most tasks |
| opus | claude-opus-4-20250514 | Complex reasoning, architecture |

### When to Use Each Model

**Haiku (fast)**
- Quick bug fixes
- Simple refactors
- Formatting changes
- Running tests
- Small chores

**Sonnet (balanced)**
- Feature implementation
- Code review
- Moderate complexity tasks
- Most general development

**Opus (powerful)**
- Complex architecture decisions
- Multi-file refactoring
- Difficult debugging
- Performance optimization
- Security analysis

## Useful Flags

```bash
# Model selection
claude --model claude-opus-4-20250514 "complex task"

# Skip permission prompts (for trusted automation)
claude --dangerously-skip-permissions "automated task"

# Output format
claude --output-format text "your task"
claude --output-format json "your task"
```

## Context Handoff Pattern

To pass context to a forked Claude:

1. **Build context summary** using `tools/context_builder.py`:
   ```bash
   uv run tools/context_builder.py --task "the task" --context "background"
   ```

2. **Read the context file** into the task prompt:
   - The fork_terminal.py script handles this automatically with `--with-context`

3. **Forked agent starts with context**:
   - Receives your summary as initial context
   - Has fresh context window beyond that

## Best Practices for Forks

### 1. Use Interactive Mode

Leave off the `-p` flag so the forked agent can interact:
```bash
# Good - interactive
claude "analyze this codebase"

# Avoid for forks - non-interactive
claude -p "analyze this codebase"
```

### 2. Be Specific

```bash
# Too vague
claude "fix bugs"

# Better - specific
claude "fix the null pointer exception in src/auth/validate.ts:42 where user.email.toLowerCase() fails"
```

### 3. Include Constraints

```bash
# Better with constraints
claude "add input validation to the login form. Use zod for validation. Don't modify the User type."
```

### 4. Set Expected Outcome

```bash
# With expected outcome
claude "add unit tests for the auth module. Aim for 80% coverage. Use jest."
```

## Common Fork Patterns

### Bug Fix
```bash
fork terminal claude "fix: <specific bug description>"
```

### Feature Addition
```bash
fork terminal claude "add: <feature description>" --model sonnet
```

### Research/Analysis
```bash
fork terminal claude "analyze: <what to analyze>" --model opus
```

### Test Writing
```bash
fork terminal claude "test: add tests for <component>"
```

### Refactoring
```bash
fork terminal claude "refactor: <what to refactor>" --worktree
```

## Fresh Context Advantage

Remember IndyDevDan's insight:

> "It's easy to know what your agent has seen when it's seen nothing."

Forked agents start with a clean slate. Use this to your advantage:
- Pass only relevant context, not everything
- Let the agent approach the problem fresh
- Avoid polluted context from long debugging sessions
