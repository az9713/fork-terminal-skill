# Gemini CLI Reference

Progressive disclosure documentation for Gemini CLI usage in forks.

## Prerequisites

Before using Gemini CLI:

### 1. Installation

```bash
# Via npm (recommended)
npm install -g @google/gemini-cli

# Or via pip
pip install google-generativeai
```

### 2. API Key Setup

```bash
# Windows (Command Prompt)
set GOOGLE_API_KEY=your-api-key-here

# Windows (PowerShell)
$env:GOOGLE_API_KEY = "your-api-key-here"

# Or add to environment variables permanently
```

### 3. Enable in Skill

In `SKILL.md`, set:
```yaml
enable_gemini_cli: true
```

## Basic Usage

```bash
# Interactive mode
gemini "your task here"

# With model selection
gemini --model gemini-2.0-flash "task"
```

## Model Options

| Model | Best For |
|-------|----------|
| gemini-2.0-flash | Fast responses, simple tasks |
| gemini-pro | Balanced capability |
| gemini-ultra | Complex reasoning (if available) |

## When to Use Gemini vs Claude

### Use Gemini When:
- You want a second opinion on a problem
- Claude is rate-limited
- You want to compare approaches
- Task aligns with Gemini's strengths

### Use Claude When:
- Deep codebase integration needed
- Using Claude Code specific features
- Task requires Claude's coding strengths

## Example Invocations

```bash
# Basic query
fork terminal gemini "explain this algorithm"

# Code review
fork terminal gemini "review this code for bugs"

# Alternative perspective
fork terminal gemini "suggest alternative approaches to this problem"
```

## Limitations

Gemini CLI has some differences from Claude Code:

1. **No native file editing** - May need manual file operations
2. **Different context handling** - Context windows work differently
3. **Different tool availability** - Not all Claude tools are available

## Notes

- This skill focuses primarily on Claude Code
- Gemini support is provided for flexibility
- Use based on your specific needs and preferences
