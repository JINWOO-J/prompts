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
# Monorepo Agent Rules — AI Agent Rules for Monorepos

> Rules for AI coding agents to work effectively in a monorepo environment. Extracted from patterns used in large-scale monorepo projects such as the Cloudflare Workers SDK.

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

## Usage

Copy the content of the Prompt block above into the root CLAUDE.md of your monorepo, and add a package-specific CLAUDE.md to each package directory to manage rules hierarchically.

## Verification

If these rules are working:
- The agent does not generate code that directly accesses another package's internal implementation.
- When modifying a shared package, the agent explicitly names the affected consumer packages.
- For cross-package changes, the agent determines and reports whether a changeset should be generated.
- The correct `--filter` option is used in build and test commands.
