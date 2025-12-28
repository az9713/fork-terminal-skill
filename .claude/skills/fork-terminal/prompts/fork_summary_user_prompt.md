# Fork Summary User Prompt

Generate a condensed context summary to pass to a forked agent.

## Purpose

When forking an agent with `--with-context`, you need to generate a summary that gives the forked agent enough background to work effectively WITHOUT loading your entire conversation history.

## What to Include (in priority order)

### 1. The Delegated Task (MOST IMPORTANT)

State clearly what the forked agent should do:
- Specific objective/outcome expected
- Any constraints or requirements
- Definition of "done"

**Example:**
```
TASK: Fix the null pointer exception in user.email validation at src/auth/validate.ts:42
```

### 2. Background Context

What you've been working on that's relevant:
- Current task/objective (1-2 sentences)
- Why this fork is needed
- Any failed approaches already tried

**Example:**
```
CONTEXT: Refactoring auth module. Found this bug while testing login flow.
Tried adding null check at line 40 but validation still fails.
```

### 3. Key Files

Paths to files the forked agent will likely need:
- Files directly related to the task
- Related test files
- Configuration files if relevant

**Example:**
```
FILES:
- src/auth/validate.ts (the bug location)
- src/auth/user.ts (User type definition)
- tests/auth/validate.test.ts (existing tests)
```

### 4. Important Decisions Already Made

Things the forked agent shouldn't undo or reconsider:
- Architecture decisions
- Library choices
- Patterns established

**Example:**
```
DECISIONS:
- Using zod for validation (don't switch libraries)
- User.email is optional in database but required for login
```

### 5. Current State

Where things stand right now:
- What's working
- What's broken
- Blockers if any

**Example:**
```
STATE: Login works with hardcoded data but fails with real users.
Error: "Cannot read property 'toLowerCase' of undefined"
```

## What to EXCLUDE

- Irrelevant conversation tangents
- Already-resolved issues
- Exploration that led nowhere
- Your reasoning process (just give conclusions)
- Code that's working fine
- Unrelated files

## Format Requirements

- Maximum ~500 words
- Use markdown structure
- Be actionable, not narrative
- Bullet points over paragraphs
- Include file paths, not just descriptions

## Output Template

```markdown
# Context for Forked Agent

## Task
[Clear, specific task description]

## Background
[1-2 sentences of relevant context]

## Key Files
- [file paths]

## Decisions Made
- [Important constraints]

## Current State
[What's working/broken]

## Notes
[Any other critical info]
```

## Example Summary

```markdown
# Context for Forked Agent

## Task
Fix null pointer in email validation: user.email.toLowerCase() fails when email is undefined.

## Background
Refactoring auth module to use stricter typing. Found this bug during login flow testing.

## Key Files
- src/auth/validate.ts:42 (bug location)
- src/auth/user.ts (User type)
- tests/auth/validate.test.ts

## Decisions Made
- Using zod for validation
- Email optional in DB but required for login
- Don't modify User type (breaking change)

## Current State
Login works with test data, fails with real users.
Error: "Cannot read property 'toLowerCase' of undefined"

## Notes
Fix should add null check before toLowerCase. Update tests.
```
