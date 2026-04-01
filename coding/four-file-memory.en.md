---
category: coding
type: concept
tags:
- working-memory
- session-management
- claude-code
role: Developer
origin: custom
source: 'https://www.implicator.ai/this-simple-four-file-system-gives-claude-code-a-working-memory/'
---
# 4-파일 워킹 메모리 — 4-File Working Memory System for AI Agents

> A framework that solves AI coding agents' cross-session memory loss using 4 files (PRD, CLAUDE.md, planning.md, tasks.md).

---

## Key Principles

- Persist project context by separating it into 4 files (PRD, CLAUDE.md, planning.md, tasks.md)
- Have the agent read all 4 files at the start of every session to understand the current state
- PRD holds goals and feature specs; CLAUDE.md holds project rules
- planning.md tracks architecture decisions and rationale; tasks.md tracks completed/in-progress/pending tasks
- Keeping tasks.md up to date prevents task duplication and omission

## Details

### The Problem

AI coding agents have no memory across sessions:
- Re-explaining project architecture every session
- Re-creating files that already exist
- Repeating completed tasks, missing new ones
- Inconsistent decisions

### The 4-File Structure

**1. PRD.md — Product Requirements**
```markdown
# Product Requirements Document
## Goals
[Core project goals]
## Feature List
- [Feature 1]: [Description]
- [Feature 2]: [Description]
## Tech Stack
- Backend: [Technology]
- Frontend: [Technology]
```

**2. CLAUDE.md — Project Rules**
```markdown
# Project Rules
## Build Commands
## Coding Rules
## Prohibitions
```

**3. planning.md — Architecture Decisions**
```markdown
# Architecture Decisions
## Decision 1: [Title]
- Choice: [Selected option]
- Reason: [Rationale]
- Alternatives: [Considered alternatives]
```

**4. tasks.md — Task Tracking**
```markdown
# Tasks
## Completed
- [x] [Task 1]
## In Progress
- [ ] [Task 2]
## Pending
- [ ] [Task 3]
```

### Session Start Prompt

```
Read this project's PRD.md, CLAUDE.md, planning.md, and tasks.md,
understand the current state, then proceed with the next task.
```

### Benefits

- 70% reduction in project management time
- Minimized context switching cost
- Consistent architecture decisions
- Prevention of task duplication/omission

## References

- [implicator.ai — Four-File System for Claude Code](https://www.implicator.ai/this-simple-four-file-system-gives-claude-code-a-working-memory/)
