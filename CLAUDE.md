# CLAUDE.md

This file provides guidance to Claude Code when working with the Fork Terminal Skill project.

## Project Overview

Fork Terminal is a Claude Code skill that enables spawning new terminal windows to run AI agents (Claude Code, Gemini CLI) or raw CLI commands in parallel. This enables "out-of-loop" agentic coding where routine tasks are delegated to forked agents.

**Key Concept:** Instead of context-switching or handling everything in one session, you can fork agents to work on independent tasks simultaneously.

## Project Structure

```
agent_skill_dan/
├── .claude/
│   └── skills/
│       └── fork-terminal/           # THE SKILL LIVES HERE
│           ├── SKILL.md             # Central pivot file (READ THIS FIRST)
│           ├── tools/               # Python scripts
│           │   ├── fork_terminal.py     # Core terminal spawning
│           │   ├── task_registry.py     # Track running/completed tasks
│           │   ├── context_builder.py   # Build context handoff files
│           │   └── worktree_manager.py  # Git worktree integration
│           ├── prompts/             # User prompts
│           │   ├── fork_summary_user_prompt.md  # How to generate context summary
│           │   ├── fork-summary.md              # Template forked agent receives
│           │   ├── fork-claude.md               # Claude fork instructions
│           │   ├── fork-gemini.md               # Gemini fork instructions
│           │   └── fork-raw.md                  # Raw CLI fork instructions
│           ├── cookbook/            # Progressive disclosure docs
│           │   ├── claude-code.md       # Claude CLI reference
│           │   ├── gemini-cli.md        # Gemini CLI reference
│           │   ├── presets.md           # Preset definitions
│           │   └── worktree-guide.md    # Git worktree patterns
│           ├── data/                # Runtime data
│           │   └── forked-tasks.json    # Task registry (auto-created)
│           └── logs/
│               └── forks/           # Output logs from forked agents
├── docs/                            # Documentation
│   ├── QUICK_START.md              # 10 hands-on tutorials
│   ├── USER_GUIDE.md               # Complete user reference
│   └── DEVELOPER_GUIDE.md          # Developer documentation
├── CLAUDE.md                        # This file
└── README.md                        # Project overview
```

## How the Skill Works

### The Pivot File Pattern

`SKILL.md` is the central organizing document. When Claude Code activates this skill:

1. Claude reads `SKILL.md` first
2. Based on user request, Claude routes to appropriate cookbook files
3. Claude executes the appropriate tool scripts
4. Results are returned to user

### Progressive Disclosure

The skill doesn't load all documentation upfront. Instead:
- If user wants Claude fork → read `cookbook/claude-code.md`
- If user wants preset → read `cookbook/presets.md`
- If user wants worktree → read `cookbook/worktree-guide.md`

This keeps context windows focused.

## Commands Reference

### User-Facing Commands

| Command | Purpose |
|---------|---------|
| `/fork claude <task>` | Spawn Claude Code in new terminal |
| `/fork raw <command>` | Run CLI command in new terminal |
| `/fork status` | Show running/completed tasks |
| `/fork list` | List all tracked forks |
| `/fork bugfix <desc>` | Preset: spawn bugfix agent |
| `/fork research <topic>` | Preset: spawn research agent |
| `/fork tests` | Preset: run and fix tests |

### Tool Scripts

All tools are in `.claude/skills/fork-terminal/tools/` and run with `uv run`:

```bash
# Spawn a terminal
uv run .claude/skills/fork-terminal/tools/fork_terminal.py --type claude --task "fix bug" --model sonnet

# Check task status
uv run .claude/skills/fork-terminal/tools/task_registry.py status

# Build context handoff
uv run .claude/skills/fork-terminal/tools/context_builder.py --task "the task" --context "background"

# Manage worktrees
uv run .claude/skills/fork-terminal/tools/worktree_manager.py list
```

## Key Technical Details

### Windows Terminal Spawning

The skill uses Windows Terminal (wt.exe) as the primary method:
```python
["wt", "new-tab", "-d", cwd, "--title", title, "powershell", "-NoExit", "-Command", command]
```

Falls back to PowerShell if Windows Terminal not available.

### Model Tier Mapping

```python
model_map = {
    "haiku": "claude-3-5-haiku-20241022",
    "sonnet": "claude-sonnet-4-20250514",
    "opus": "claude-opus-4-20250514"
}
```

### Agentic Return Values

All tools output JSON for agent consumption:
```json
{
  "success": true,
  "task_id": "abc123",
  "message": "Forked agent spawned successfully"
}
```

## Development Guidelines

### Adding New Features

1. **New tool script**: Add to `tools/` directory with UV script header
2. **New preset**: Add to `cookbook/presets.md`
3. **New fork type**: Update `SKILL.md` routing logic
4. **Update documentation**: Update all relevant docs

### Testing Changes

```bash
# Test fork terminal
uv run .claude/skills/fork-terminal/tools/fork_terminal.py --type raw --task "echo test" --no-output

# Test task registry
uv run .claude/skills/fork-terminal/tools/task_registry.py status

# Test context builder
uv run .claude/skills/fork-terminal/tools/context_builder.py --task "test" --preview
```

### Code Style

- Python scripts use UV inline dependencies (no requirements.txt needed)
- All tools return JSON for agent parsing
- Use argparse for CLI argument handling
- Include comprehensive docstrings

## Common Tasks

### When User Says "fork terminal" or "spawn agent"

1. Read `SKILL.md` to understand the skill
2. Parse the user's request to determine fork type
3. Check for flags (--model, --with-context, --worktree)
4. Execute appropriate tool
5. Register task in registry
6. Confirm to user

### When User Says "/fork status"

```bash
uv run .claude/skills/fork-terminal/tools/task_registry.py status
```

### When User Wants Context Handoff

1. Read `prompts/fork_summary_user_prompt.md`
2. Generate context summary following the instructions
3. Save with `context_builder.py`
4. Pass context file to fork_terminal.py

## Error Handling

| Error | Resolution |
|-------|------------|
| Windows Terminal not found | Automatic fallback to PowerShell |
| Not in git repo (worktree) | Inform user, skip worktree creation |
| Task spawn fails | Report error, don't register task |

## Files to Read for Context

When working on this project, read in this order:

1. `SKILL.md` - The central skill definition
2. `docs/DEVELOPER_GUIDE.md` - Full developer documentation
3. `tools/fork_terminal.py` - Core spawning logic
4. `cookbook/presets.md` - Preset definitions

## Key Principles

From IndyDevDan's agentic coding philosophy:

1. **Fresh context windows** - Forked agents start clean
2. **In-loop vs Out-of-loop** - Complex work in-loop, routine tasks out-of-loop
3. **Simple solutions** - Don't over-engineer
4. **Eliminate confusion** - Be specific about what the forked agent should do
