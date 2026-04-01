---
category: coding
type: prompt
tags:
- agent
- monorepo
- architecture
- turborepo
role: Developer
origin: custom
source: 'https://github.com/josix/awesome-claude-md/blob/main/scenarios/developer-tooling/cloudflare_workers-sdk/README.md'
---
# Monorepo Agent Rules — 모노레포 AI 에이전트 규칙

> 모노레포 환경에서 AI 코딩 에이전트가 효과적으로 작업하기 위한 규칙. Cloudflare Workers SDK 등 대규모 모노레포 프로젝트의 패턴에서 추출.

---

## Prompt

```markdown
## Monorepo Rules

### Package Boundaries
- Never access another package's internal implementation directly; use its public API only
- Never create circular dependencies between packages
- When changing a shared package, run tests for all consumers

### Change Scope
- Limit each change to one package when possible
- When making cross-package changes, explicitly state the impact scope
- Generate a changeset for any user-facing change; skip for internal-only changes

### Build Commands
- Full build: `turbo build`
- Single package: `turbo build --filter=@scope/package`
- Test: `turbo test --filter=@scope/package`
- Dependency graph: `turbo graph`

### Structure
root/
  CLAUDE.md              ← project-wide rules
  packages/
    api/CLAUDE.md        ← API package rules
    web/CLAUDE.md        ← web package rules
    shared/CLAUDE.md     ← shared package rules
```

---

## 사용법

모노레포 루트의 CLAUDE.md에 위 Prompt 블록 내용을 복사하고, 각 패키지 디렉토리에 패키지별 CLAUDE.md를 추가하여 계층적으로 규칙을 관리한다.

## 적용 확인

이 규칙이 작동하고 있다면:
- 패키지 내부 구현에 직접 접근하는 코드가 생성되지 않는다
- 공유 패키지 변경 시 에이전트가 영향받는 소비자 패키지를 명시한다
- 크로스 패키지 변경 시 changeset 생성 여부를 에이전트가 판단해 알려준다
- 빌드/테스트 명령에 올바른 `--filter` 옵션이 사용된다
