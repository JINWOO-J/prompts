---
category: coding
type: concept
tags:
- ralph-loop
- autonomous
- tdd
role: Developer
origin: custom
source: 'https://learndevrel.com/blog/ralph-loop-ai-coding'
---
# AI 에이전트 자율 반복 실행 패턴 — Ralph Loop

> A methodology where you write specs (tests) first, then let the AI agent autonomously iterate until all tests pass.

---

## Key Principles

- Write specs (tests) first and instruct the agent to aim for passing them
- If tests are incomplete, you get bad code that "just passes the tests" — a comprehensive test suite is a prerequisite
- Set a maximum iteration count to prevent infinite loops
- Not suitable for security-related code — manual review is mandatory
- Specify the test execution command in CLAUDE.md
- After the agent generates code, human code review and side-effect verification are required

## Details

The "Ralph Wiggum technique" created by Geoffrey Huntley. It was the most discussed development methodology in the AI coding community in early 2026.

### Core Concept

```bash
while ! tests_pass; do
  ai_agent fix_failing_tests
done
```

Write specs (tests) first, then let the AI agent autonomously modify code
until all tests pass.

### Workflow

**1. Define Specs**
- Write expected behavior as tests
- Include edge cases
- Include performance criteria (if needed)

**2. Run the Agent**
- Instruct the agent to aim for passing tests
- Automatically retry on failure
- Iterate until success

**3. Verification**
- Confirm all tests pass
- Code review (human)
- Check for unintended side effects

### Prerequisites

- Clear and comprehensive test suite
- Agent's file system access permissions
- Test execution command specified in CLAUDE.md
- Appropriate timeout settings

### Caveats

- If tests are incomplete, you may get bad code that "just passes the tests"
- Maximum iteration count needed to prevent infinite loops
- Not suitable for security-related code — manual review is mandatory

## References

- [learndevrel.com — The Ralph Loop](https://learndevrel.com/blog/ralph-loop-ai-coding)
