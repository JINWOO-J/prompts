---
category: coding
type: guide
tags:
- spec-driven
- tdd
- methodology
role: Developer
origin: custom
source: 'http://smartscope.blog/en/ai-development/enforcing-spec-driven-development-claude-copilot-2025/'
---
# 스펙 기반 개발 — Spec-Driven Development for AI Agents

> A spec-first TDD methodology that technically enforces AI agents' tendency to treat instructions as suggestions.

---

## Prompt

```markdown
## Spec-Driven Development Workflow

1. Write specs (requirements.md)
2. Write design document (design.md)
3. Decompose tasks (tasks.md)
4. For each task:
   a. Write tests first
   b. Confirm test failure
   c. Write minimal implementation code
   d. Confirm tests pass
   e. Mark task as complete

## Key Principles

1. Specs Before Implementation
   - Clearly define what to build before writing code
   - Enforce the order: requirements → design → tasks

2. One Small Change at a Time
   - Small test, small implementation
   - Refactoring only after all tests pass

3. Verifiable Completion Criteria
   - Clear success criteria for each task
   - Verification through automated tests

4. Enforcing Agent Behavior
   - Always include spec files in the agent's context
   - Explicitly state the rule: "Do not add features not in the spec"

## Spec File Templates

### requirements.md
## Requirement 1: [Feature Name]
### User Stories
- As a [role], I want [feature] so that [reason]
### Acceptance Criteria
- [ ] [Verifiable criterion 1]
- [ ] [Verifiable criterion 2]

### tasks.md
## Task 1: [Task Name]
- [ ] 1.1 [Subtask] (Req 1.1)
- [ ] 1.2 [Subtask] (Req 1.2)
```

---

## Background

AI agents tend to interpret instructions as recommendations rather than mandatory constraints, often adding features beyond the spec scope or implementing things differently. By writing spec documents first and always including them in the agent's context, this tendency can be technically suppressed. When combined with a TDD cycle, any deviation from the spec is immediately caught by test failures.

## Usage

Before starting new feature development, write documents in the order `requirements.md` → `design.md` → `tasks.md`, instruct the agent to read the spec files first, then delegate implementation task by task.
