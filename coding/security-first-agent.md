---
category: coding
tags:
- coding
- security
- ai-agent
- defi
- rules
role: Security Engineer
origin: custom
source: ''
---
# Security-First Agent Rules — 보안 우선 AI 에이전트 규칙

## 개요

보안이 최우선인 프로젝트(DeFi, 금융, 인프라 등)에서 AI 코딩 에이전트가 따라야 할 규칙.
Citadel Protocol 등 보안 크리티컬 프로젝트의 CLAUDE.md 패턴에서 추출.

> 참고: [josix/awesome-claude-md — Citadel Protocol](https://github.com/josix/awesome-claude-md/blob/main/scenarios/complex-projects/Citadel-Protocol_contracts/analysis.md)

## 핵심 규칙

### 1. 보안 검토 필수
- 모든 외부 입력에 대한 유효성 검사
- SQL 인젝션, XSS, CSRF 등 OWASP Top 10 체크
- 인증/인가 로직 변경 시 반드시 수동 리뷰

### 2. 비밀 정보 관리
- 하드코딩된 시크릿 절대 금지
- 환경 변수 또는 시크릿 매니저 사용
- 로그에 민감 정보 출력 금지
- 코드 예시에서 PII는 플레이스홀더 사용

### 3. 의존성 보안
- 새 의존성 추가 시 보안 감사 필요
- 알려진 취약점이 있는 버전 사용 금지
- 최소 권한 원칙 적용

### 4. 에러 처리
- 내부 에러 상세를 외부에 노출 금지
- 스택 트레이스를 사용자에게 보여주지 않음
- 에러 로깅은 내부 시스템에만

### 5. 코드 변경 제한
- 보안 관련 파일 변경 시 명시적 승인 필요
- 인증 미들웨어, 권한 체크 로직은 자동 변경 금지
- 암호화 관련 코드는 검증된 라이브러리만 사용

## CLAUDE.md 보안 섹션 템플릿

```markdown
## Security Rules
- NEVER hardcode secrets, API keys, or credentials
- NEVER log sensitive data (PII, tokens, passwords)
- ALWAYS validate external input before processing
- ALWAYS use parameterized queries for database access
- NEVER modify auth middleware without explicit approval
- NEVER disable security headers or CORS restrictions
```

## 보안 체크리스트

- [ ] 입력 유효성 검사
- [ ] 출력 인코딩
- [ ] 인증/인가 확인
- [ ] 세션 관리
- [ ] 에러 처리 (정보 누출 방지)
- [ ] 로깅 (민감 정보 제외)
- [ ] 의존성 취약점 스캔
