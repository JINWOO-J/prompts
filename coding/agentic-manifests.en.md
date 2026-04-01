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
# 에이전트 매니페스트 표준 — Agentic Coding Manifests

> Standards and patterns for configuration files (CLAUDE.md, AGENTS.md, etc.) that provide project context, identity, and operational rules to AI coding agents.

---

## Prompt

```markdown
## Manifest File Types

| Filename | Tool | Scope |
|----------|------|-------|
| CLAUDE.md | Claude Code | Claude only |
| AGENTS.md | Universal | Cursor, Copilot, Codex, etc. |
| .cursorrules | Cursor | Cursor only |
| copilot-instructions.md | GitHub Copilot | Copilot only |
| GEMINI.md | Gemini | Gemini only |

## AGENTS.md Required Section Template

# AGENTS.md

## Project Overview
[Project description]

## Commands
- build: `npm run build`
- test: `npm test`
- lint: `npm run lint`

## Architecture
[Directory structure and module relationships]

## Conventions
[Coding rules]

## Constraints
[Prohibited actions]

## Effective Manifest Writing Principles

- Specify concrete commands and prohibitions (general advice has limited effect)
- Maintain a shallow hierarchy with explicit section divisions
- Write concisely to enable quick context acquisition
- Structure the format to support reproducible workflow execution
```

---

## Background

As of January 2026, over 60,000 open-source projects on GitHub use this format. The Agentic AI Foundation under the Linux Foundation manages the AGENTS.md universal standard, aiming for a universal format that works across all AI coding tools. According to the arxiv study (2509.14744), manifests have a shallow hierarchy with explicit section divisions, and concrete commands and prohibitions are far more effective than general advice.

## Usage

When starting a new project or adopting an AI agent, create a manifest file at the project root based on the AGENTS.md template above.
