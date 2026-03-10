---
category: coding
tags:
- coding
- ai-agent
- behavior
- agents-md
- patterns
role: Developer
origin: custom
source: ''
---
# Agent Behavior Patterns — 실제로 에이전트 행동을 바꾸는 패턴

## 개요

AGENTS.md/CLAUDE.md에서 실제로 AI 에이전트의 행동을 변화시키는 패턴과
효과가 없는 패턴을 구분하는 실증적 가이드.

> 참고: [blakecrosley.com — What Actually Changes Agent Behavior](https://blakecrosley.com/blog/agents-md-patterns),
> [dair.ai — Does AGENTS.md Actually Help?](https://academy.dair.ai/blog/agents-md-evaluation)

## 효과적인 패턴

### 1. 구체적 명령어
```markdown
# ✅ 효과적
테스트: `pnpm vitest --run`
린트: `pnpm eslint . --fix`

# ❌ 비효과적
테스트와 린트를 실행하세요.
```

### 2. 명시적 금지
```markdown
# ✅ 효과적
- sed 사용 금지. sd를 사용하라.
- python -c 사용 금지. 임시 파일에 작성 후 실행.
- 기존 테스트 삭제 금지.

# ❌ 비효과적
- 좋은 코드를 작성하세요.
- 베스트 프랙티스를 따르세요.
```

### 3. 예시 코드
```markdown
# ✅ 효과적
에러 처리 패턴:
\`\`\`typescript
try {
  const result = await operation();
  return { ok: true, data: result };
} catch (e) {
  logger.error('operation failed', { error: e });
  return { ok: false, error: e.message };
}
\`\`\`

# ❌ 비효과적
에러를 적절히 처리하세요.
```

### 4. 디렉토리 구조 명시
```markdown
# ✅ 효과적
src/
  routes/     — API 라우트 핸들러
  services/   — 비즈니스 로직
  models/     — 데이터 모델
  utils/      — 유틸리티 함수
```

## 효과 없는 패턴

- 일반적인 코딩 조언 ("클린 코드를 작성하세요")
- 코드 스타일 규칙 (linter에 위임)
- 너무 긴 설명 (500줄 이상)
- 모호한 지시 ("적절히 처리하세요")

## DAIR.AI 연구 결과

- AGENTS.md가 있을 때 에이전트 성능이 향상되는 경우가 있지만
- 효과는 **구체성**에 비례
- 일반적 조언은 거의 효과 없음
- 명령어, 금지사항, 예시 코드가 가장 효과적
