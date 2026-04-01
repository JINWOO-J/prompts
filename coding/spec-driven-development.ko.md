---
category: coding
type: guide
tags:
- spec-driven
- tdd
- methodology
role: Developer
origin: custom
source: 'http://smartscope.blog/en/ai-development/enforcing-spec-driven-development-claude-copilot-2025/'
---
# Spec-Driven Development — AI 에이전트 스펙 기반 개발

> AI 에이전트의 "지시를 권장사항으로 취급"하는 경향을 기술적으로 강제하는 스펙 우선 TDD 방법론.

---

## Prompt

```markdown
## 스펙 기반 개발 워크플로우

1. 스펙 작성 (requirements.md)
2. 설계 문서 작성 (design.md)
3. 태스크 분해 (tasks.md)
4. 각 태스크마다:
   a. 테스트 먼저 작성
   b. 테스트 실패 확인
   c. 최소 구현 코드 작성
   d. 테스트 통과 확인
   e. 태스크 완료 마킹

## 핵심 원칙

1. 구현 전에 스펙
   - 코드를 쓰기 전에 무엇을 만들지 명확히 정의
   - 요구사항 → 설계 → 태스크 순서를 강제

2. 한 번에 하나의 작은 변경
   - 작은 테스트, 작은 구현
   - 리팩터링은 모든 테스트 통과 후에만

3. 검증 가능한 완료 기준
   - 각 태스크에 명확한 성공 기준
   - 자동화된 테스트로 검증

4. 에이전트 행동 강제
   - 스펙 파일을 에이전트 컨텍스트에 항상 포함
   - "스펙에 없는 기능 추가 금지" 규칙 명시

## 스펙 파일 템플릿

### requirements.md
## Requirement 1: [기능명]
### User Stories
- As a [역할], I want [기능] so that [이유]
### Acceptance Criteria
- [ ] [검증 가능한 기준 1]
- [ ] [검증 가능한 기준 2]

### tasks.md
## Task 1: [태스크명]
- [ ] 1.1 [서브태스크] (Req 1.1)
- [ ] 1.2 [서브태스크] (Req 1.2)
```

---

## 배경

AI 에이전트는 지시를 강제적 제약이 아닌 권장사항으로 해석하는 경향이 있어, 스펙 범위를 넘어 기능을 추가하거나 다른 방식으로 구현하는 경우가 많다. 스펙 문서를 먼저 작성하고 에이전트 컨텍스트에 항상 포함시킴으로써 이 경향을 기술적으로 억제할 수 있다. TDD 사이클과 결합하면 구현이 스펙에서 벗어나는 즉시 테스트 실패로 감지된다.

## 사용법

새 기능 개발 시작 전 `requirements.md` → `design.md` → `tasks.md` 순서로 작성하고, 에이전트에게 스펙 파일을 먼저 읽도록 지시한 뒤 태스크 단위로 구현을 위임하라.
