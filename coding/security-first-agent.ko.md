---
category: coding
type: prompt
tags:
- agent
- security
- defi
- rule
role: Security Engineer
origin: custom
source: 'https://github.com/josix/awesome-claude-md/blob/main/scenarios/complex-projects/Citadel-Protocol_contracts/analysis.md'
---
# Security-First Agent Rules — 보안 우선 AI 에이전트 규칙

> 보안 크리티컬 프로젝트(DeFi, 금융, 인프라 등)에서 AI 코딩 에이전트가 따라야 할 규칙. Citadel Protocol 등의 CLAUDE.md 패턴에서 추출.

---

## Prompt

```markdown
## Security Rules

- NEVER hardcode secrets, API keys, or credentials
- NEVER log sensitive data (PII, tokens, passwords)
- ALWAYS validate external input before processing
- ALWAYS use parameterized queries for database access
- NEVER modify auth middleware without explicit approval
- NEVER disable security headers or CORS restrictions
- NEVER expose internal error details to external callers
- ALWAYS use vetted libraries for cryptographic operations
- ALWAYS apply least-privilege principle to new dependencies
- Flag any change to authentication, authorization, or session logic for manual review
```

---

## 사용법

CLAUDE.md의 Security 섹션에 위 Prompt 블록 내용을 복사하여 사용한다. DeFi, 금융, 인프라 등 보안이 최우선인 프로젝트의 에이전트 규칙으로 적합하다.

## 적용 확인

이 규칙이 작동하고 있다면:
- 하드코딩된 시크릿이 커밋에 포함되지 않는다
- 인증/인가 로직 변경 시 에이전트가 명시적으로 수동 리뷰를 요청한다
- 로그 출력에 토큰, 비밀번호, PII가 나타나지 않는다
- 새 의존성 추가 시 에이전트가 보안 감사 필요성을 언급한다
