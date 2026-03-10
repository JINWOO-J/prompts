---
category: coding
tags:
- coding
- monorepo
- ai-agent
- architecture
- turborepo
role: Developer
origin: custom
source: ''
---
# Monorepo Agent Rules — 모노레포 AI 에이전트 규칙

## 개요

모노레포 환경에서 AI 코딩 에이전트가 효과적으로 작업하기 위한 규칙.
Cloudflare Workers SDK 등 대규모 모노레포 프로젝트의 패턴에서 추출.

> 참고: [josix/awesome-claude-md — Cloudflare Workers SDK](https://github.com/josix/awesome-claude-md/blob/main/scenarios/developer-tooling/cloudflare_workers-sdk/README.md)

## 핵심 규칙

### 1. 패키지 경계 존중
- 다른 패키지의 내부 구현에 직접 접근 금지
- 공개 API를 통해서만 패키지 간 소통
- 순환 의존성 생성 금지

### 2. 변경 범위 제한
- 한 번에 하나의 패키지만 변경 (가능한 경우)
- 크로스 패키지 변경 시 영향 범위 명시
- 공유 패키지 변경 시 모든 소비자 테스트 실행

### 3. 빌드 시스템 이해
```markdown
## Build Commands
- 전체 빌드: `turbo build`
- 단일 패키지: `turbo build --filter=@scope/package`
- 테스트: `turbo test --filter=@scope/package`
- 의존성 그래프: `turbo graph`
```

### 4. Progressive Disclosure
```
root/
  CLAUDE.md              ← 전체 프로젝트 규칙
  packages/
    api/CLAUDE.md        ← API 패키지 규칙
    web/CLAUDE.md        ← 웹 패키지 규칙
    shared/CLAUDE.md     ← 공유 패키지 규칙
```

### 5. 변경 로그
- 사용자 영향이 있는 변경은 changeset 생성
- 내부 변경은 changeset 불필요
- 버전 범프는 자동화 도구에 위임

## 모노레포 CLAUDE.md 템플릿

```markdown
# CLAUDE.md

## Monorepo Structure
- `packages/api` — REST API 서버
- `packages/web` — 프론트엔드 앱
- `packages/shared` — 공유 유틸리티

## Rules
- 패키지 간 직접 import 금지 (공개 API만 사용)
- 변경 시 해당 패키지의 테스트만 실행
- 공유 패키지 변경 시 전체 테스트 실행
```
