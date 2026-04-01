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
# Progressive Disclosure — Layered Context Pattern for CLAUDE.md

> A pattern for providing context to AI agents hierarchically in large-scale projects. Extracted from CLAUDE.md guides on greeto.me and potapov.dev.

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

## Usage

Create a CLAUDE.md in the project root, each package directory, and each domain directory, and distribute content according to the layer principles above. Follow the token budget guidelines to keep each file within its size limit.

## Verification

If this pattern is applied correctly:
- The agent does not reference rules unrelated to the current working directory.
- Each CLAUDE.md file stays within its designated line count limit.
- The root CLAUDE.md contains only global rules, with no package-specific details.
- Context window usage is reduced compared to a single large CLAUDE.md.
