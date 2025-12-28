# Fork Presets

Quick shortcuts for common fork patterns. Presets define model tier, context settings, and task templates.

## Available Presets

---

### bugfix

Fork a specialized bug-fixing agent.

```yaml
preset: bugfix
type: claude
model: sonnet
context: true
task_template: |
  Fix the following bug: {description}

  Steps:
  1. Identify the root cause
  2. Implement minimal fix
  3. Add regression test if appropriate
  4. Commit with descriptive message starting with "fix:"
```

**Usage:**
```bash
/fork bugfix "null pointer in user.email at src/auth.ts:42"
/fork bugfix "login fails when email contains plus sign"
```

**Best for:**
- Known bugs with clear symptoms
- Issues that can be isolated
- Quick fixes that shouldn't expand scope

---

### research

Fork a research and exploration agent.

```yaml
preset: research
type: claude
model: opus
context: true
task_template: |
  Research the following topic: {description}

  Deliverables:
  1. Summary of findings
  2. Key insights
  3. Recommendations
  4. Relevant code locations or files

  Save findings to research/{date}_{topic}.md
```

**Usage:**
```bash
/fork research "how authentication flows work in this codebase"
/fork research "performance optimization opportunities"
/fork research "security vulnerabilities in input handling"
```

**Best for:**
- Understanding new codebases
- Exploring options before implementation
- Finding patterns across the codebase
- Security or performance audits

---

### tests

Fork a test runner and fixer agent.

```yaml
preset: tests
type: claude
model: haiku
context: false
task_template: |
  Run the test suite and fix any failures:

  Steps:
  1. Run full test suite
  2. Identify failing tests
  3. Analyze failure causes
  4. Fix issues causing failures
  5. Re-run to verify
  6. Report results

  Do NOT skip or delete failing tests unless they are genuinely obsolete.
```

**Usage:**
```bash
/fork tests
/fork tests "focus on auth module tests"
```

**Best for:**
- CI/CD preparation
- Catching regressions
- Routine test maintenance
- Post-refactor verification

---

### review

Fork a code review agent.

```yaml
preset: review
type: claude
model: sonnet
context: true
task_template: |
  Review recent changes and provide feedback:

  Focus areas:
  1. Code quality and readability
  2. Potential bugs or edge cases
  3. Performance issues
  4. Security concerns
  5. Suggestions for improvement

  Be specific and actionable in feedback.
  Reference line numbers when possible.
```

**Usage:**
```bash
/fork review
/fork review "review the auth module changes"
```

**Best for:**
- Pre-commit review
- Learning from your own code
- Catching issues before PR

---

### refactor

Fork a refactoring agent.

```yaml
preset: refactor
type: claude
model: sonnet
worktree: true
context: true
task_template: |
  Refactor the following: {description}

  Constraints:
  1. Maintain existing behavior (no functional changes)
  2. Improve code quality and maintainability
  3. Add/update tests if behavior is unclear
  4. Document significant structural changes

  Commit with message starting with "refactor:"
```

**Usage:**
```bash
/fork refactor "extract auth logic into separate service"
/fork refactor "convert callbacks to async/await"
```

**Best for:**
- Structural improvements
- Code modernization
- Extracting reusable components
- Technical debt reduction

---

### docs

Fork a documentation agent.

```yaml
preset: docs
type: claude
model: sonnet
context: false
task_template: |
  Update documentation for: {description}

  Tasks:
  1. Review existing documentation
  2. Update outdated information
  3. Add missing sections
  4. Ensure examples work

  Documentation should be clear, concise, and accurate.
```

**Usage:**
```bash
/fork docs "update README with new setup instructions"
/fork docs "add API documentation for auth endpoints"
```

**Best for:**
- README updates
- API documentation
- Usage examples
- Architecture documentation

---

## Custom Presets

You can define your own presets by adding new sections to this file following the same format:

```yaml
preset: my-custom-preset
type: claude | gemini | raw
model: haiku | sonnet | opus
context: true | false
worktree: true | false
task_template: |
  Your template with {description} placeholder
```

## Preset Selection Logic

When a preset is invoked:

1. Load preset configuration from this file
2. Apply model, context, and worktree settings
3. Fill task_template with user's description
4. Execute fork with configured options

## Combining Presets with Flags

Presets can be combined with flags:

```bash
# Override model
/fork bugfix "fix null pointer" --model opus

# Add worktree to preset that doesn't have it
/fork bugfix "risky fix" --worktree

# Disable context on preset that has it
/fork research "quick lookup" --no-context
```

Flags override preset defaults.
