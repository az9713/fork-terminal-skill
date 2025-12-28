# Fork Claude Code Agent

Spawn a new Claude Code instance in a separate terminal window.

## Purpose

Claude Code agents are best for:
- Code modifications and bug fixes
- Refactoring and improvements
- Adding features
- Writing tests
- Code review and analysis
- Complex multi-step development tasks

## Task

{task}

## Configuration

- **Model**: {model}
- **Working Directory**: {cwd}
- **Context File**: {context_file}

## Behavior

The forked Claude Code instance will:
1. Start in interactive mode (not -p mode)
2. Have access to the same codebase
3. Work on the delegated task independently
4. Complete or report blockers when done

## Best Practices

1. **Be specific about the task** - vague tasks lead to scope creep
2. **Include relevant file paths** - helps agent focus
3. **Mention constraints** - things the agent should NOT change
4. **Set expectations** - what "done" looks like

## Example Invocations

```bash
# Simple bug fix
fork terminal claude "fix the null pointer at src/auth.ts:42"

# With model selection
fork terminal claude "analyze this codebase architecture" --model opus

# With context handoff
fork terminal claude "continue the auth refactor" --with-context

# With worktree isolation
fork terminal claude "implement experimental feature" --worktree
```

## Output

- New terminal window opens with Claude Code
- Task registered in data/forked-tasks.json
- Output captured to logs/forks/ (unless --no-output)
