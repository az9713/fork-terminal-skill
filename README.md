# Fork Terminal Skill

A Claude Code skill that enables spawning new terminal windows to run AI agents or CLI commands in parallel. Delegate tasks to forked agents that work independently while you continue in your main session.

## What It Does

Instead of handling everything in one Claude Code session, you can:

- **Fork Claude agents** to work on bugs, research, or tests in separate terminals
- **Run CLI commands** in new windows without blocking your session
- **Track tasks** across all forked agents
- **Pass context** so forked agents understand your current work
- **Use git worktrees** for isolated experimentation

## Quick Example

```
You: /fork claude "fix the authentication bug in src/auth.ts" --model sonnet
```

Result: A new terminal opens with Claude Code working on the bug independently.

## Installation

1. **Clone or download** this repository
2. **Ensure prerequisites**:
   - Claude Code installed (`claude` command works)
   - Python with UV (`pip install uv`)
   - Windows Terminal (recommended) or PowerShell

3. **Verify setup**:
   ```bash
   uv run .claude/skills/fork-terminal/tools/task_registry.py status
   ```

## Documentation

| Document | Description |
|----------|-------------|
| [Quick Start Guide](docs/QUICK_START.md) | 10 hands-on tutorials |
| [User Guide](docs/USER_GUIDE.md) | Complete reference |
| [Developer Guide](docs/DEVELOPER_GUIDE.md) | Technical documentation |
| [CLAUDE.md](CLAUDE.md) | Guidance for Claude Code |

## Commands

| Command | Description |
|---------|-------------|
| `/fork claude <task>` | Spawn Claude in new terminal |
| `/fork raw <command>` | Run CLI command in new terminal |
| `/fork status` | Show running/completed tasks |
| `/fork bugfix <desc>` | Preset for bug fixes |
| `/fork research <topic>` | Preset for exploration |
| `/fork tests` | Preset for running tests |

## Project Structure

```
agent_skill_dan/
├── .claude/skills/fork-terminal/    # The skill
│   ├── SKILL.md                     # Central pivot file
│   ├── tools/                       # Python scripts
│   ├── prompts/                     # Agent prompts
│   ├── cookbook/                    # Reference docs
│   ├── data/                        # Runtime data
│   └── logs/                        # Fork output logs
├── docs/                            # Documentation
├── CLAUDE.md                        # Claude Code guidance
└── README.md                        # This file
```

## Features

- **Context Handoff**: Pass context summary to forked agents
- **Task Registry**: Track all running and completed tasks
- **Output Capture**: Save forked agent output to log files
- **Model Selection**: Choose haiku/sonnet/opus per task
- **Git Worktree Integration**: Isolated workspaces
- **Presets**: Quick shortcuts for common patterns

## Philosophy

From IndyDevDan's agentic coding approach:

1. **Fresh context windows** - Forked agents start clean, focused
2. **In-loop vs Out-of-loop** - Complex work in-loop, routine tasks out-of-loop
3. **Simple solutions** - Don't over-engineer
4. **Parallel execution** - Multiple agents working simultaneously

## License

MIT

---

*Inspired by [IndyDevDan's](https://www.youtube.com/@indydevdan) agentic coding workflow. Built with [Claude Code](https://claude.ai/code).*
