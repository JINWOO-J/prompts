---
category: coding
tags:
- coding
- claude-md
- agents-md
- context-engineering
- ai-agent
role: Developer
origin: custom
source: ''
---
# CLAUDE.md / AGENTS.md 작성 가이드

## 개요

AI 코딩 에이전트에게 프로젝트 컨텍스트를 전달하는 CLAUDE.md(또는 AGENTS.md) 파일 작성법.
매 세션마다 반복 설명 없이 에이전트가 프로젝트를 이해하도록 하는 핵심 설정 파일이다.

> 참고: [humanlayer.dev/blog/writing-a-good-claude-md](https://www.humanlayer.dev/blog/writing-a-good-claude-md),
> [josix/awesome-claude-md](https://github.com/josix/awesome-claude-md)

## 핵심 원칙

### 1. 컨텍스트 윈도우는 공유 자원
CLAUDE.md는 시스템 프롬프트, 대화 이력, 기타 컨텍스트와 경쟁한다.
간결하고 핵심적인 정보만 포함하라.

### 2. 포함해야 할 것
- **빌드/테스트 명령어**: `npm run test`, `make lint` 등 정확한 명령어
- **아키텍처 개요**: 디렉토리 구조, 주요 모듈 관계
- **코딩 규칙**: 네이밍, 에러 처리, 로깅 패턴
- **금지 사항**: "sed 사용 금지", "기존 테스트 삭제 금지" 등
- **의존성 정보**: 패키지 매니저, 런타임 버전

### 3. 포함하지 말 것
- 코드 스타일/포매팅 규칙 (linter/formatter에 위임)
- 너무 긴 설명 (500줄 이상은 효과 감소)
- 자주 변하는 정보 (별도 파일로 분리)

## 구조 템플릿

```markdown
# CLAUDE.md

## 프로젝트 개요
[한 문단으로 프로젝트 설명]

## 빌드 & 테스트
- 설치: `pnpm install`
- 테스트: `pnpm test`
- 린트: `pnpm lint`

## 아키텍처
- `src/` — 메인 소스
- `tests/` — 테스트
- `docs/` — 문서

## 코딩 규칙
- [규칙 1]
- [규칙 2]

## 금지 사항
- [금지 1]
- [금지 2]
```

## 5계층 설정 시스템

| 계층 | 파일 | 용도 |
|------|------|------|
| 1 | CLAUDE.md | 프로젝트 컨텍스트 (매 세션 로드) |
| 2 | .claude/settings.json | 도구 권한, 허용 명령어 |
| 3 | .claude/hooks/ | 이벤트 기반 자동화 |
| 4 | .claude/agents/ | 서브에이전트 정의 |
| 5 | .claude/memory/ | 자동 메모리 |

## Progressive Disclosure 패턴

큰 프로젝트에서는 계층적으로 CLAUDE.md를 배치:
- 루트 `CLAUDE.md` — 전체 프로젝트 규칙
- `packages/api/CLAUDE.md` — API 패키지 규칙
- `packages/web/CLAUDE.md` — 웹 패키지 규칙

에이전트가 특정 디렉토리에서 작업할 때 해당 레벨의 규칙이 추가 로드된다.
