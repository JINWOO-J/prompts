---
category: coding
type: concept
tags:
- claude-md
- agents-md
- context-engineering
role: Developer
origin: custom
source: 'https://www.humanlayer.dev/blog/writing-a-good-claude-md'
---
# CLAUDE.md / AGENTS.md 작성 가이드 — CLAUDE.md / AGENTS.md Writing Guide

> How to write configuration files that deliver project context to AI coding agents.

---

## Key Principles

- CLAUDE.md is a shared resource in the context window — include only concise, essential information
- Include build/test commands, architecture overview, coding rules, prohibitions, and dependency info
- Delegate code style/formatting rules to linters/formatters — don't put them in CLAUDE.md
- Effectiveness decreases beyond 500 lines — separate frequently changing information into separate files
- For large projects, place CLAUDE.md files hierarchically per subdirectory (Progressive Disclosure)
- Leverage the 5-layer configuration system (CLAUDE.md, settings.json, hooks, agents, memory)

## Details

### What to Include

- **Build/test commands**: Exact commands like `npm run test`, `make lint`
- **Architecture overview**: Directory structure, key module relationships
- **Coding rules**: Naming, error handling, logging patterns
- **Prohibitions**: "Do not use sed", "Do not delete existing tests", etc.
- **Dependency info**: Package manager, runtime versions

### What Not to Include

- Code style/formatting rules (delegate to linters/formatters)
- Overly long descriptions (effectiveness decreases beyond 500 lines)
- Frequently changing information (separate into dedicated files)

### Structure Template

```markdown
# CLAUDE.md

## Project Overview
[One paragraph project description]

## Build & Test
- Install: `pnpm install`
- Test: `pnpm test`
- Lint: `pnpm lint`

## Architecture
- `src/` — Main source
- `tests/` — Tests
- `docs/` — Documentation

## Coding Rules
- [Rule 1]
- [Rule 2]

## Prohibitions
- [Prohibition 1]
- [Prohibition 2]
```

### 5-Layer Configuration System

| Layer | File | Purpose |
|-------|------|---------|
| 1 | CLAUDE.md | Project context (loaded every session) |
| 2 | .claude/settings.json | Tool permissions, allowed commands |
| 3 | .claude/hooks/ | Event-driven automation |
| 4 | .claude/agents/ | Sub-agent definitions |
| 5 | .claude/memory/ | Automatic memory |

### Progressive Disclosure Pattern

For large projects, place CLAUDE.md files hierarchically:
- Root `CLAUDE.md` — Project-wide rules
- `packages/api/CLAUDE.md` — API package rules
- `packages/web/CLAUDE.md` — Web package rules

When the agent works in a specific directory, the rules at that level are additionally loaded.

## References

- [humanlayer.dev — Writing a Good CLAUDE.md](https://www.humanlayer.dev/blog/writing-a-good-claude-md)
- [josix/awesome-claude-md](https://github.com/josix/awesome-claude-md)
