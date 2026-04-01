---
category: coding
type: guide
tags:
- hooks
- automation
- ci-cd
role: Developer
origin: custom
source: ''
---
# AI 에이전트 훅과 자동화 패턴 — Hooks & Automation

> A hook system that automates AI agent behavior by reacting to events such as file changes, tool execution, and task completion.

---

## Prompt

```markdown
## Hook Type Reference

| Event | Trigger Timing | Use Case |
|-------|---------------|----------|
| fileEdited | On file save | Lint, format, test |
| fileCreated | On file creation | Boilerplate validation |
| preToolUse | Before tool execution | Permission check, validation |
| postToolUse | After tool execution | Result validation, logging |
| promptSubmit | On prompt submission | Context injection |
| postTaskExecution | After task completion | Test execution |

## Hook Templates

### Lint on Save
{
  "name": "Lint on Save",
  "version": "1.0.0",
  "when": {
    "type": "fileEdited",
    "patterns": ["*.ts", "*.tsx"]
  },
  "then": {
    "type": "runCommand",
    "command": "npm run lint"
  }
}

### Write Operation Validation
{
  "name": "Review Write Operations",
  "version": "1.0.0",
  "when": {
    "type": "preToolUse",
    "toolTypes": ["write"]
  },
  "then": {
    "type": "askAgent",
    "prompt": "Verify that this write operation follows coding standards"
  }
}

### Post-Task Testing
{
  "name": "Test After Task",
  "version": "1.0.0",
  "when": {
    "type": "postTaskExecution"
  },
  "then": {
    "type": "runCommand",
    "command": "npm test"
  }
}

## Design Principles

- Hooks must execute quickly (60-second timeout by default)
- If a preToolUse hook denies access, tool execution is blocked
- Watch out for circular dependencies (Hook A → Tool X → Hook A)
- Hooks are supplementary — do not put core logic in hooks
```

---

## Background

Since AI coding agents autonomously modify files and execute commands, event-driven automation is necessary to maintain quality without human intervention every time. The hook system attaches side effects to agent actions — think of it as an in-agent version of a CI/CD pipeline.

## Usage

Use the templates above when defining hooks in JSON format within agent configuration files (e.g., `.claude/hooks/`) or orchestrator settings.
