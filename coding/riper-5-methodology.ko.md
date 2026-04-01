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
# RIPER-5 — AI 에이전트 개발 방법론

> GoMall 프로젝트에서 사용된 AI 에이전트 개발 방법론. Research → Implement → Plan → Execute → Review 5단계 사이클로 에이전트의 작업을 구조화한다.

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

## 사용법

CLAUDE.md에 위 Prompt 블록 내용을 복사하고, 에이전트에게 작업 지시 시 현재 RIPER 단계를 명시적으로 지정하여 사용한다.

## 적용 확인

이 방법론이 작동하고 있다면:
- 에이전트가 요청을 받자마자 바로 코드를 작성하지 않고 Research 결과를 먼저 보고한다
- 각 단계가 완료된 후 사용자 확인을 요청한다
- Plan 단계에서 번호가 매겨진 실행 계획이 명시적으로 제시된다
- 변경의 영향 범위가 Execute 전에 파악된다
