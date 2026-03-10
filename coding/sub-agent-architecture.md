---
category: coding
tags:
- coding
- sub-agent
- ai-agent
- architecture
- claude-code
role: Developer
origin: custom
source: ''
---
# Sub-Agent Architecture — AI 코딩 서브에이전트 설계

## 개요

AI 코딩 에이전트를 역할별로 분리하여 전문화된 서브에이전트로 구성하는 아키텍처.
각 서브에이전트는 고유한 시스템 프롬프트, 도구 접근 권한, 전문 영역을 가진다.

> 참고: [hesreallyhim/awesome-claude-code-agents](https://github.com/hesreallyhim/awesome-claude-code-agents),
> [blog.saurav.io — AI Coding Stack](https://blog.saurav.io/ai-coding-stack-explained/)

## 서브에이전트 유형

### 역할 기반 분류

| 에이전트 | 역할 | 전문 영역 |
|----------|------|-----------|
| ts-coder | TypeScript 개발 | 타입 안전성, 함수형 패턴 |
| react-coder | React 개발 | 컴포넌트, 훅, 상태 관리 |
| backend-architect | 백엔드 설계 | API, DB, 스케일링 |
| code-reviewer | 코드 리뷰 | 보안, 성능, 아키텍처 |
| ui-engineer | UI 개발 | 접근성, 반응형, 컴포넌트 |

### 에이전트 파일 구조

```markdown
---
name: ts-coder
description: TypeScript 코드 작성 및 리팩터링
model: opus
color: green
---

[에이전트 시스템 프롬프트]
```

## 설계 원칙

### 1. 단일 책임
각 에이전트는 하나의 명확한 역할만 수행.
"풀스택 에이전트"보다 전문화된 에이전트가 효과적.

### 2. 명확한 인터페이스
에이전트 간 소통은 명확한 입출력으로 정의.
메인 에이전트가 서브에이전트에게 구체적 태스크를 위임.

### 3. 컨텍스트 격리
각 에이전트는 자신의 역할에 필요한 컨텍스트만 로드.
불필요한 정보로 컨텍스트 윈도우를 낭비하지 않음.

## 오케스트레이션 패턴

```
메인 에이전트 (오케스트레이터)
  ├── context-gatherer → 코드베이스 분석
  ├── ts-coder → TypeScript 구현
  ├── code-reviewer → 코드 리뷰
  └── test-writer → 테스트 작성
```
