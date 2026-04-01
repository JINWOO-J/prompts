---
category: coding
type: guide
tags:
- agent
- manifest
- agents-md
- claude-md
role: Developer
origin: custom
source: 'https://arxiv.org/html/2509.14744v1'
---
# Agentic Coding Manifests — 에이전트 매니페스트 표준

> AI 코딩 에이전트에게 프로젝트 컨텍스트·정체성·운영 규칙을 제공하는 설정 파일(CLAUDE.md, AGENTS.md 등)의 표준과 패턴.

---

## Prompt

```markdown
## 매니페스트 파일 유형

| 파일명 | 도구 | 범위 |
|--------|------|------|
| CLAUDE.md | Claude Code | Claude 전용 |
| AGENTS.md | 범용 | Cursor, Copilot, Codex 등 |
| .cursorrules | Cursor | Cursor 전용 |
| copilot-instructions.md | GitHub Copilot | Copilot 전용 |
| GEMINI.md | Gemini | Gemini 전용 |

## AGENTS.md 필수 섹션 템플릿

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

## 효과적인 매니페스트 작성 원칙

- 구체적 명령어와 금지사항을 명시하라 (일반적 조언은 효과가 제한적)
- 얕은 계층 구조와 명시적 섹션 분할을 유지하라
- 빠른 컨텍스트 획득이 가능하도록 간결하게 작성하라
- 재현 가능한 워크플로우 실행을 지원하는 형식으로 구성하라
```

---

## 배경

2026년 1월 기준 GitHub에서 60,000개 이상의 오픈소스 프로젝트가 이 형식을 사용한다. Linux Foundation 산하 Agentic AI Foundation이 AGENTS.md 범용 표준을 관리하며, 모든 AI 코딩 도구에서 작동하는 범용 형식을 목표로 한다. arxiv 연구(2509.14744)에 따르면 매니페스트는 얕은 계층 구조와 명시적 섹션 분할을 가지며, 구체적 명령어와 금지사항이 일반적 조언보다 훨씬 효과적이다.

## 사용법

새 프로젝트 시작 시 또는 AI 에이전트 도입 시 위 AGENTS.md 템플릿을 기반으로 프로젝트 루트에 매니페스트 파일을 작성하라.
