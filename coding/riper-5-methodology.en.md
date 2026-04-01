---
category: coding
type: prompt
tags:
- riper-5
- methodology
- workflow
role: Developer
origin: custom
source: 'https://github.com/josix/awesome-claude-md/blob/main/scenarios/developer-tooling/li0on3_GoMall/README.md'
---
# RIPER-5 — AI Agent Development Methodology

> An AI agent development methodology used in the GoMall project. Structures agent work through a five-stage cycle: Research → Implement → Plan → Execute → Review.

---

## Prompt

```markdown
## RIPER-5 Development Methodology

Follow the RIPER-5 cycle for all non-trivial tasks. Do not skip stages or jump to coding without completing the prior stage.

### R — Research
- Analyze the existing codebase
- Identify related files and dependencies
- Understand existing patterns and rules
- Output: summary of current state

### I — Implement (planning)
- Analyze the impact scope of the proposed change
- Compare possible approaches
- State trade-offs explicitly
- Output: recommended implementation direction

### P — Plan
- Write a concrete, numbered step-by-step execution plan
- Define a verification method for each step
- Determine dependency ordering
- Output: numbered execution plan

### E — Execute
- Make code changes according to the plan
- Verify after each step
- Update the plan if a problem arises
- Output: changed code

### R — Review
- Review all changes as a whole
- Run tests and confirm results
- Check for unintended side effects
- Output: review result and improvement suggestions

### Usage
Specify the current stage explicitly when directing the agent:
  "Current RIPER stage: Research — analyze the auth module and summarize current state."
```

---

## Usage

Copy the content of the Prompt block above into your CLAUDE.md and explicitly specify the current RIPER stage when giving instructions to the agent.

## Verification

If this methodology is working:
- The agent reports Research findings before writing any code.
- The agent requests user confirmation after completing each stage.
- During the Plan stage, a numbered execution plan is presented explicitly.
- The impact scope of changes is understood before the Execute stage begins.
