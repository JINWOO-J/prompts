---
category: coding
tags:
- coding
- working-memory
- ai-agent
- session-management
- claude-code
role: Developer
origin: custom
source: ''
---
# 4-File Working Memory — AI 에이전트 워킹 메모리 시스템

## 개요

AI 코딩 에이전트의 세션 간 기억 상실 문제를 해결하는 4파일 프레임워크.
PRD, CLAUDE.md, planning.md, tasks.md 4개 파일로 프로젝트 컨텍스트를 영속화한다.

> 참고: [implicator.ai — Four-File System for Claude Code](https://www.implicator.ai/this-simple-four-file-system-gives-claude-code-a-working-memory/)

## 문제

AI 코딩 에이전트는 세션 간 기억이 없다:
- 매 세션마다 프로젝트 아키텍처를 다시 설명
- 이미 존재하는 파일을 다시 생성
- 완료된 작업을 반복, 새 작업은 누락
- 일관성 없는 결정

## 4파일 구조

### 1. PRD.md — 제품 요구사항
```markdown
# Product Requirements Document
## 목표
[프로젝트의 핵심 목표]
## 기능 목록
- [기능 1]: [설명]
- [기능 2]: [설명]
## 기술 스택
- Backend: [기술]
- Frontend: [기술]
```

### 2. CLAUDE.md — 프로젝트 규칙
```markdown
# Project Rules
## 빌드 명령어
## 코딩 규칙
## 금지 사항
```

### 3. planning.md — 아키텍처 결정
```markdown
# Architecture Decisions
## 결정 1: [제목]
- 선택: [선택한 옵션]
- 이유: [근거]
- 대안: [고려한 대안]
```

### 4. tasks.md — 작업 추적
```markdown
# Tasks
## 완료
- [x] [작업 1]
## 진행 중
- [ ] [작업 2]
## 대기
- [ ] [작업 3]
```

## 세션 시작 프롬프트

```
이 프로젝트의 PRD.md, CLAUDE.md, planning.md, tasks.md를 읽고
현재 상태를 파악한 후, 다음 작업을 진행해줘.
```

## 효과

- 프로젝트 관리 시간 70% 감소
- 컨텍스트 전환 비용 최소화
- 일관된 아키텍처 결정
- 작업 중복/누락 방지
