---
category: coding
tags:
- coding
- manifest
- agents-md
- claude-md
- convention
role: Developer
origin: custom
source: ''
---
# Agentic Coding Manifests — 에이전트 매니페스트 표준

## 개요

AI 코딩 에이전트에게 프로젝트 컨텍스트, 정체성, 운영 규칙을 제공하는
설정 파일(CLAUDE.md, AGENTS.md 등)의 표준과 패턴.
2026년 1월 기준 GitHub에서 60,000개 이상의 오픈소스 프로젝트가 이 형식을 사용한다.

> 참고: [arxiv.org — On the Use of Agentic Coding Manifests](https://arxiv.org/html/2509.14744v1),
> [emergentmind.com — Agentic Coding Manifests](https://www.emergentmind.com/topics/agentic-coding-manifests)

## 매니페스트 유형

| 파일명 | 도구 | 범위 |
|--------|------|------|
| CLAUDE.md | Claude Code | Claude 전용 |
| AGENTS.md | 범용 | Cursor, Copilot, Codex 등 |
| .cursorrules | Cursor | Cursor 전용 |
| copilot-instructions.md | GitHub Copilot | Copilot 전용 |
| GEMINI.md | Gemini | Gemini 전용 |

## AGENTS.md — 범용 표준

Linux Foundation 산하 Agentic AI Foundation이 관리.
모든 AI 코딩 도구에서 작동하는 범용 형식.

### 필수 섹션

```markdown
# AGENTS.md

## Project Overview
[프로젝트 설명]

## Commands
- build: `npm run build`
- test: `npm test`
- lint: `npm run lint`

## Architecture
[디렉토리 구조 및 모듈 관계]

## Conventions
[코딩 규칙]

## Constraints
[금지 사항]
```

## 연구 결과 (arxiv)

- 매니페스트는 얕은 계층 구조와 명시적 섹션 분할을 가짐
- 빠른 컨텍스트 획득과 재현 가능한 워크플로우 실행을 지원
- 구체적 명령어와 금지사항이 가장 효과적
- 일반적 조언은 효과가 제한적
