---
category: coding
type: concept
tags:
- context-engineering
- prompt-engineering
- llm
role: Developer
origin: custom
source: 'https://www.pixelmojo.io/blogs/context-engineering-ai-coding-agents-beyond-claude-md'
---
# Context Engineering — AI 코딩 에이전트 컨텍스트 엔지니어링

> AI 코딩 에이전트에게 올바른 컨텍스트를 체계적으로 제공하여 출력 품질을 극대화하는 기법.

---

## 핵심 원칙

- 모델은 현재 토큰 스트림에 있는 것만 안다 — 컨텍스트가 에이전트의 전부다
- 구체적 명령어가 일반적 조언보다 강력하다 ("pnpm test" > "테스트를 실행하세요")
- 예시가 설명보다 효과적이다 — 코드 예시를 규칙 설명 대신 사용하라
- 금지 표현이 권장 표현보다 강력하다 ("sed 사용 금지" > "sd를 사용하세요")
- 표, 목록, 코드 블록이 긴 산문보다 효과적이다
- CLAUDE.md는 200~500줄이 최적이다 — 자주 변하는 정보는 별도 파일로 분리하라
- @import 패턴으로 큰 문서를 참조 방식으로 연결하라
- 4-파일 워킹 메모리 시스템(PRD, CLAUDE.md, planning.md, tasks.md)으로 세션 간 컨텍스트를 유지하라

## 상세

2025년 Andrej Karpathy가 "vibe coding"을 제안한 이후, 업계는 "AI 제안을 그냥 수락"에서
컨텍스트 엔지니어링이라는 체계적 접근으로 전환했다.

### 컨텍스트의 4가지 레이어

| 레이어 | 설명 | 예시 |
|--------|------|------|
| 시스템 | 에이전트 기본 동작 | 시스템 프롬프트 |
| 프로젝트 | 코드베이스 규칙 | CLAUDE.md, AGENTS.md |
| 세션 | 현재 대화 | 대화 이력, 파일 읽기 |
| 작업 | 현재 태스크 | 사용자 프롬프트 |

### 효과적인 컨텍스트 전략

1. **구체적 명령어 > 일반적 조언**: "pnpm test" > "테스트를 실행하세요"
2. **예시 > 설명**: 코드 예시가 규칙 설명보다 효과적
3. **금지 > 권장**: "sed 사용 금지"가 "sd를 사용하세요"보다 강력
4. **구조 > 산문**: 표, 목록, 코드 블록이 긴 문장보다 효과적

### 실전 패턴

**4-파일 워킹 메모리 시스템**
```
PRD.md          — 제품 요구사항
CLAUDE.md       — 프로젝트 규칙
planning.md     — 아키텍처 결정
tasks.md        — 작업 추적
```

**@import 패턴**
CLAUDE.md에서 다른 파일을 참조:
```markdown
See @docs/architecture.md for system design
See @docs/api-spec.yaml for API contracts
```

**토큰 예산 관리**
- CLAUDE.md는 200~500줄이 최적
- 자주 변하는 정보는 별도 파일로 분리
- 서브디렉토리별 CLAUDE.md로 점진적 공개

## 참고

- [pixelmojo.io — Context Engineering for AI Coding Agents](https://www.pixelmojo.io/blogs/context-engineering-ai-coding-agents-beyond-claude-md)
