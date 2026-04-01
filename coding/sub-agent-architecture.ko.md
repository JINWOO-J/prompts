---
category: coding
type: guide
tags:
- agent
- sub-agent
- orchestration
- claude-code
role: Developer
origin: custom
source: 'https://github.com/hesreallyhim/awesome-claude-code-agents'
---
# Sub-Agent Architecture — AI 코딩 서브에이전트 설계

> AI 코딩 에이전트를 역할별로 분리하여 전문화된 서브에이전트로 구성하는 오케스트레이션 아키텍처.

---

## Prompt

```markdown
## 역할 기반 에이전트 분류

| 에이전트 | 역할 | 전문 영역 |
|----------|------|-----------|
| ts-coder | TypeScript 개발 | 타입 안전성, 함수형 패턴 |
| react-coder | React 개발 | 컴포넌트, 훅, 상태 관리 |
| backend-architect | 백엔드 설계 | API, DB, 스케일링 |
| code-reviewer | 코드 리뷰 | 보안, 성능, 아키텍처 |
| ui-engineer | UI 개발 | 접근성, 반응형, 컴포넌트 |

## 에이전트 파일 구조 (마크다운 frontmatter)

---
name: [agent-name]
description: [역할 설명]
model: opus | sonnet | haiku
color: [색상]
---

[에이전트 시스템 프롬프트]

## 오케스트레이션 패턴

메인 에이전트 (오케스트레이터)
  ├── context-gatherer → 코드베이스 분석
  ├── ts-coder → TypeScript 구현
  ├── code-reviewer → 코드 리뷰
  └── test-writer → 테스트 작성

## 설계 원칙

1. 단일 책임
   - 각 에이전트는 하나의 명확한 역할만 수행
   - "풀스택 에이전트"보다 전문화된 에이전트가 효과적

2. 명확한 인터페이스
   - 에이전트 간 소통은 명확한 입출력으로 정의
   - 메인 에이전트가 서브에이전트에게 구체적 태스크를 위임

3. 컨텍스트 격리
   - 각 에이전트는 자신의 역할에 필요한 컨텍스트만 로드
   - 불필요한 정보로 컨텍스트 윈도우를 낭비하지 않음
```

---

## 배경

단일 범용 에이전트는 복잡한 코드베이스에서 컨텍스트 오염과 역할 혼란 문제를 야기한다. 서브에이전트 아키텍처는 소프트웨어 공학의 단일 책임 원칙을 에이전트 설계에 적용한 것이다. 각 에이전트가 좁은 전문 영역에 집중하면 더 높은 품질의 출력을 일관되게 생성한다. 참고: [blog.saurav.io — AI Coding Stack](https://blog.saurav.io/ai-coding-stack-explained/)

## 사용법

에이전트 정의 파일(`.claude/agents/` 또는 유사 디렉토리)을 만들 때 위 frontmatter 구조를 사용하고, 오케스트레이터 프롬프트에서 각 에이전트를 태스크 유형에 따라 라우팅하라.
