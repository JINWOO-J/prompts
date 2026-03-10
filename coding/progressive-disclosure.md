---
category: coding
tags:
- coding
- progressive-disclosure
- claude-md
- architecture
- ai-agent
role: Developer
origin: custom
source: ''
---
# Progressive Disclosure — CLAUDE.md 점진적 공개 패턴

## 개요

대규모 프로젝트에서 AI 에이전트에게 컨텍스트를 계층적으로 제공하는 패턴.
에이전트가 작업하는 디렉토리에 따라 관련 규칙만 로드하여 컨텍스트 윈도우를 효율적으로 사용한다.

> 참고: [greeto.me — CLAUDE.md Progressive Disclosure](https://greeto.me/blog/claude-md-progressive-disclosure-for-fast-teams),
> [potapov.dev — The Definitive Guide to CLAUDE.md](https://potapov.dev/blog/claude-md-guide)

## 계층 구조

```
project/
  CLAUDE.md                    ← L0: 전체 프로젝트 규칙
  packages/
    api/
      CLAUDE.md                ← L1: API 패키지 규칙
      src/
        auth/
          CLAUDE.md            ← L2: 인증 모듈 규칙
    web/
      CLAUDE.md                ← L1: 웹 패키지 규칙
```

## 각 레벨의 역할

### L0 — 프로젝트 루트
- 빌드/테스트 명령어
- 전체 아키텍처 개요
- 공통 코딩 규칙
- 금지 사항

### L1 — 패키지/모듈
- 패키지별 빌드 명령어
- 패키지 내부 아키텍처
- 패키지별 의존성 규칙

### L2 — 기능/도메인
- 도메인 특화 규칙
- 보안 요구사항
- 특수한 테스트 패턴

## 규칙 배치 원칙

| 규칙 유형 | 배치 레벨 | 예시 |
|-----------|----------|------|
| 빌드 명령어 | L0 | `pnpm test` |
| 패키지 매니저 | L0 | "pnpm만 사용" |
| API 규칙 | L1 | "REST 규칙 준수" |
| 인증 규칙 | L2 | "JWT 검증 필수" |

## 토큰 예산 가이드

- L0: 100~200줄 (매 세션 로드)
- L1: 50~100줄 (해당 패키지 작업 시)
- L2: 20~50줄 (해당 모듈 작업 시)
- 총합이 500줄을 넘지 않도록 관리
