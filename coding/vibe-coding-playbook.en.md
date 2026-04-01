---
category: coding
type: guide
origin: custom
role: Developer
source: 'https://royfactory.net/posts/ai/202512/vibe-coding-playbook/'
tags:
- vibe-coding
- methodology
- karpathy-rules
---
# 바이브 코딩 실전 가이드 — Vibe Coding Playbook

> A practical methodology for delegating implementation to AI while ensuring quality through prompts, tests, and guardrails.

---

## Prompt

```markdown
## Vibe Coding Practical Principles

### 1. Prompts Are Design
- Clear, specific prompts = good design documents
- Vague prompts → vague code

### 2. Tests Are Specs
- The correctness of AI-generated code can only be verified through tests
- Write tests first, then let AI handle the implementation

### 3. Set Up Guardrails
- Define behavioral rules with CLAUDE.md/AGENTS.md
- Automate verification with linters, formatters, and type checkers
- Verify before deployment with CI/CD pipelines

### 4. Incremental Complexity
- Start small and expand gradually
- Multiple small changes over one large change

### 5. Context Management
- Context quality degrades as sessions get longer
- Periodically start new sessions
- Record important decisions in files

## Workflow

1. Clarify intent (write prompt)
2. Write tests (define success criteria)
3. Delegate implementation to AI
4. Run tests (automated verification)
5. Code review (manual verification)
6. Iterate

## Caveats

- Do not blindly trust AI output
- Security-related code requires manual review
- Verify complex business logic step by step
- Performance-critical code requires benchmarking
```

---

## Background

Originating from the "vibe coding" concept proposed by Andrej Karpathy in February 2025. The approach is to "surrender to the vibes, embrace exponential growth, and forget whether the code even works" — but in production, guardrails are essential. The key is balancing delegation of output to AI while humans maintain a verification layer.

## Usage

Refer to these principles when starting a new AI coding session or writing a project's CLAUDE.md/AGENTS.md.
