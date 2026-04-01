---
category: coding
type: prompt
tags:
- progressive-disclosure
- claude-md
- architecture
role: Developer
origin: custom
source: 'https://greeto.me/blog/claude-md-progressive-disclosure-for-fast-teams'
---
# Progressive Disclosure — CLAUDE.md 점진적 공개 패턴

> 대규모 프로젝트에서 AI 에이전트에게 컨텍스트를 계층적으로 제공하는 패턴. greeto.me 및 potapov.dev의 CLAUDE.md 가이드에서 추출.

---

## Prompt

```markdown
## CLAUDE.md Progressive Disclosure

Structure CLAUDE.md files in layers. Load only what is relevant to the current working directory.

### Layer Structure
project/
  CLAUDE.md                    ← L0: project-wide rules (100–200 lines)
  packages/
    api/
      CLAUDE.md                ← L1: package rules (50–100 lines)
      src/
        auth/
          CLAUDE.md            ← L2: domain/feature rules (20–50 lines)
    web/
      CLAUDE.md                ← L1: package rules

### What Goes Where
- L0 (root): build/test commands, overall architecture, global coding rules, forbidden patterns
- L1 (package): package-specific build commands, internal architecture, dependency rules
- L2 (feature/domain): domain-specific rules, security requirements, special test patterns

### Token Budget
- L0: 100–200 lines (loaded every session)
- L1: 50–100 lines (loaded when working in that package)
- L2: 20–50 lines (loaded when working in that module)
- Keep total under 500 lines across all active layers
```

---

## 사용법

프로젝트 루트, 패키지, 도메인 디렉토리 각각에 CLAUDE.md를 생성하고 위 레이어 원칙에 따라 내용을 분배한다. 토큰 예산 가이드를 지켜 각 파일의 크기를 제한한다.

## 적용 확인

이 패턴이 적용되고 있다면:
- 에이전트가 작업 중인 디렉토리와 관련 없는 규칙을 참조하지 않는다
- 각 CLAUDE.md 파일이 지정된 줄 수 제한 안에 들어온다
- 루트 CLAUDE.md에는 전역 규칙만 있고 패키지 세부 사항이 없다
- 컨텍스트 윈도우 사용량이 단일 대형 CLAUDE.md 대비 줄어든다
