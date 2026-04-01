---
category: coding
type: guide
tags:
- agent
- sub-agent
- orchestration
- claude-code
role: Developer
origin: custom
source: 'https://github.com/hesreallyhim/awesome-claude-code-agents'
---
# 서브에이전트 아키텍처 — Sub-Agent Architecture for AI Coding

> An orchestration architecture that separates AI coding agents by role into specialized sub-agents.

---

## Prompt

```markdown
## Role-Based Agent Classification

| Agent | Role | Specialty |
|-------|------|-----------|
| ts-coder | TypeScript development | Type safety, functional patterns |
| react-coder | React development | Components, hooks, state management |
| backend-architect | Backend design | API, DB, scaling |
| code-reviewer | Code review | Security, performance, architecture |
| ui-engineer | UI development | Accessibility, responsive, components |

## Agent File Structure (Markdown frontmatter)

---
name: [agent-name]
description: [Role description]
model: opus | sonnet | haiku
color: [color]
---

[Agent system prompt]

## Orchestration Pattern

Main Agent (Orchestrator)
  ├── context-gatherer → Codebase analysis
  ├── ts-coder → TypeScript implementation
  ├── code-reviewer → Code review
  └── test-writer → Test writing

## Design Principles

1. Single Responsibility
   - Each agent performs one clear role only
   - Specialized agents are more effective than "full-stack agents"

2. Clear Interfaces
   - Communication between agents is defined with clear inputs/outputs
   - The main agent delegates specific tasks to sub-agents

3. Context Isolation
   - Each agent loads only the context needed for its role
   - Don't waste the context window with unnecessary information
```

---

## Background

A single general-purpose agent causes context pollution and role confusion in complex codebases. Sub-agent architecture applies software engineering's Single Responsibility Principle to agent design. When each agent focuses on a narrow specialty, it consistently produces higher-quality output. Reference: [blog.saurav.io — AI Coding Stack](https://blog.saurav.io/ai-coding-stack-explained/)

## Usage

When creating agent definition files (`.claude/agents/` or similar directories), use the frontmatter structure above and route each agent by task type in the orchestrator prompt.
