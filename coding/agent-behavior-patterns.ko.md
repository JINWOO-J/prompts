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
# Agent Behavior Patterns — 실제로 에이전트 행동을 바꾸는 패턴

> AGENTS.md/CLAUDE.md에서 실제로 AI 에이전트의 행동을 변화시키는 패턴과 효과가 없는 패턴을 구분하는 실증적 가이드. blakecrosley.com 및 DAIR.AI 연구 기반.

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

## 사용법

CLAUDE.md 또는 AGENTS.md를 작성할 때 위 패턴을 참고하여 구체적 명령어, 명시적 금지사항, 예시 코드, 디렉토리 구조 형태로 규칙을 작성한다.

## 적용 확인

이 패턴이 작동하고 있다면:
- 에이전트가 금지된 도구(`sed`, `python -c` 등) 대신 지정된 대안을 사용한다
- 에러 처리 코드가 지정된 패턴 구조를 따른다
- 일반적인 조언("좋은 코드 작성") 대신 구체적이고 검증 가능한 행동이 나온다
- 명령어 실행 시 정확한 CLI 인수가 사용된다
