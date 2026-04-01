---
category: coding
type: guide
tags:
- agent
- self-learning
- memory
- pattern
role: Developer
origin: custom
source: 'https://github.com/Equilateral-AI/equilateral-agents-open-core'
---
# 자기 학습 AI 에이전트 패턴 — Self-Learning Agent Patterns

> Designing AI agent memory systems that track execution history, recognize patterns, and improve over time.

---

## Prompt

```markdown
## Memory File Structure

memory/
  decisions.md     — Architecture decision log
  patterns.md      — Discovered code patterns
  errors.md        — Resolved errors and solutions
  preferences.md   — User preferences

## Error Learning Template

## Error: [Error Name]
- Cause: [Root cause]
- Fix: [Fix command or procedure]
- Frequency: N times (last 7 days)

### Example
## Error: ModuleNotFoundError
- Cause: Virtual environment not activated
- Fix: Run `source .venv/bin/activate` then retry
- Frequency: 3 times (last 7 days)

## Preferences Template

## User Preferences
- Test framework: [choice] (not [alternative])
- Package manager: [choice] (not [alternative])
- Error handling: [pattern] (not [alternative])

### Example
## User Preferences
- Test framework: pytest (not vitest)
- Package manager: pnpm (not npm)
- Error handling: Result pattern (not try-catch)

## Learning Cycle

1. Perform task
2. Evaluate result (success/failure)
3. Extract pattern
4. Save to memory
5. Apply to next task
```

---

## Background

AI agents are stateless by default and repeat the same mistakes. By maintaining memory files in the project, agents can load decisions and error resolutions from previous sessions as context. The key components are: (1) tracking recent execution history, (2) detecting recurring error patterns, (3) remembering effective solutions, and (4) learning project-specific idioms and user preferences.

## Usage

Create a `memory/` directory at the project root, and include those files in the agent's context at session start to reuse previous learnings.
