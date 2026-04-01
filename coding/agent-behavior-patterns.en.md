---
category: coding
type: prompt
tags:
- agent
- behavior-pattern
- agents-md
- context-engineering
role: Developer
origin: custom
source: 'https://blakecrosley.com/blog/agents-md-patterns'
---
# Agent Behavior Patterns — Patterns That Actually Change Agent Behavior

> An evidence-based guide distinguishing patterns in AGENTS.md/CLAUDE.md that genuinely change AI agent behavior from those that do not. Based on research from blakecrosley.com and DAIR.AI.

---

## Prompt

```markdown
## Agent Behavior Rules

### Explicit Commands (use exact tool invocations)
Test: `pnpm vitest --run`
Lint: `pnpm eslint . --fix`

### Explicit Prohibitions
- Do NOT use `sed`. Use `sd` instead.
- Do NOT use `python -c`. Write to a temp file and execute it.
- Do NOT delete existing tests.

### Error Handling Pattern
\```typescript
try {
  const result = await operation();
  return { ok: true, data: result };
} catch (e) {
  logger.error('operation failed', { error: e });
  return { ok: false, error: e.message };
}
\```

### Directory Structure
src/
  routes/     — API route handlers
  services/   — business logic
  models/     — data models
  utils/      — utility functions

### What Does NOT Work
- Generic advice ("write clean code", "follow best practices")
- Style rules — delegate to linter
- Instructions longer than 500 lines
- Vague directives ("handle it appropriately")
```

---

## Usage

When writing your CLAUDE.md or AGENTS.md, use the patterns above as a reference: write rules as concrete commands, explicit prohibitions, code examples, and directory structure definitions.

## Verification

If these patterns are working:
- The agent uses the specified alternatives instead of prohibited tools (`sed`, `python -c`, etc.).
- Error handling code follows the specified pattern structure.
- Output consists of concrete, verifiable actions rather than generic advice like "write good code."
- Exact CLI arguments are used when running commands.
