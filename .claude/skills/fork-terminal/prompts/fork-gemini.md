# Fork Gemini CLI Agent

Spawn a new Gemini CLI instance in a separate terminal window.

## Prerequisites

Before using Gemini CLI forks:

1. **Install Gemini CLI:**
   ```bash
   npm install -g @google/gemini-cli
   ```

2. **Set API key:**
   ```bash
   set GOOGLE_API_KEY=your-key-here
   ```

3. **Enable in SKILL.md:**
   Set `enable_gemini_cli: true` in the Variables section.

## Purpose

Gemini CLI agents can be used for:
- Alternative perspective on code problems
- Cross-checking Claude's suggestions
- Tasks where Gemini models excel
- Parallel exploration with different models

## Task

{task}

## Configuration

- **Model**: {model}
- **Working Directory**: {cwd}

## Behavior

The forked Gemini instance will:
1. Start with the specified task
2. Work independently
3. Report results when done

## Example Invocations

```bash
# Basic Gemini fork
fork terminal gemini "analyze this codebase"

# With model selection
fork terminal gemini "explain this algorithm" --model gemini-pro
```

## Notes

- Gemini CLI has different capabilities than Claude Code
- Not all Claude Code features are available in Gemini CLI
- Consider task requirements when choosing between CLI tools

## Output

- New terminal window opens with Gemini CLI
- Task registered in data/forked-tasks.json
- Output captured to logs/forks/ (unless --no-output)
