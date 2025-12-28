# Fork Raw CLI Command

Execute a CLI command in a new terminal window.

## Purpose

Raw CLI forks are useful for:
- Running long-running commands (builds, tests, servers)
- Commands that need their own terminal (watchers, dev servers)
- Parallel execution of independent commands
- Commands that produce lots of output

## Command

{task}

## Configuration

- **Working Directory**: {cwd}

## Behavior

The new terminal will:
1. Open in the specified working directory
2. Execute the command
3. Stay open to show results (uses `cmd /k` on Windows)

## Safety Considerations

Raw CLI commands run with your user permissions. Review commands before spawning if you have any security concerns.

The skill does NOT:
- Validate commands for safety
- Sandbox execution
- Limit network access

## Example Invocations

```bash
# Run tests in background
fork terminal raw "npm test"

# Start a dev server
fork terminal raw "npm run dev"

# Run a build
fork terminal raw "npm run build"

# Git operations
fork terminal raw "git status"

# Multiple commands
fork terminal raw "npm install && npm run build"

# With specific directory
fork terminal raw "python manage.py runserver" --cwd "C:\projects\django-app"
```

## Common Use Cases

| Use Case | Command |
|----------|---------|
| Run tests | `npm test`, `pytest`, `cargo test` |
| Build project | `npm run build`, `cargo build` |
| Start server | `npm run dev`, `python -m http.server` |
| Watch files | `npm run watch`, `cargo watch` |
| Git operations | `git pull`, `git status` |

## Output

- New terminal window opens with command running
- Task registered in data/forked-tasks.json
- Output visible in terminal (and captured to logs if enabled)
