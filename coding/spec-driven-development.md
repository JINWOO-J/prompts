---
category: coding
tags:
- coding
- spec-driven
- tdd
- ai-agent
- methodology
role: Developer
origin: custom
source: ''
---
# Spec-Driven Development — AI 에이전트 스펙 기반 개발

## 개요

AI 에이전트가 "지시를 권장사항으로 취급"하는 경향을 기술적으로 강제하는 방법론.
스펙 문서를 먼저 작성하고, 에이전트가 스펙에 따라 TDD 사이클로 구현하도록 한다.

> 참고: [smartscope.blog — Enforcing Spec-Driven on AI Agents](http://smartscope.blog/en/ai-development/enforcing-spec-driven-development-claude-copilot-2025/)

## 워크플로우

```
1. 스펙 작성 (requirements.md)
2. 설계 문서 작성 (design.md)
3. 태스크 분해 (tasks.md)
4. 각 태스크마다:
   a. 테스트 먼저 작성
   b. 테스트 실패 확인
   c. 최소 구현 코드 작성
   d. 테스트 통과 확인
   e. 태스크 완료 마킹
```

## 핵심 원칙

### 1. 구현 전에 스펙
- 코드를 쓰기 전에 무엇을 만들지 명확히 정의
- 요구사항 → 설계 → 태스크 순서를 강제

### 2. 한 번에 하나의 작은 변경
- 작은 테스트, 작은 구현
- 리팩터링은 모든 테스트 통과 후에만

### 3. 검증 가능한 완료 기준
- 각 태스크에 명확한 성공 기준
- 자동화된 테스트로 검증

### 4. 에이전트 행동 강제
- 스펙 파일을 에이전트 컨텍스트에 항상 포함
- "스펙에 없는 기능 추가 금지" 규칙 명시

## 스펙 파일 구조

### requirements.md
```markdown
## Requirement 1: [기능명]
### User Stories
- As a [역할], I want [기능] so that [이유]
### Acceptance Criteria
- [ ] [검증 가능한 기준 1]
- [ ] [검증 가능한 기준 2]
```

### tasks.md
```markdown
## Task 1: [태스크명]
- [ ] 1.1 [서브태스크] (Req 1.1)
- [ ] 1.2 [서브태스크] (Req 1.2)
```
