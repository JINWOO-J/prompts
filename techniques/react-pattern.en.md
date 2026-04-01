---
tags:
- techniques
- react
- reasoning
- acting
- agent
- tool-use
---
# ReAct — Reasoning + Acting Pattern

## Concept

A technique that interleaves reasoning and acting in alternating cycles.
The LLM repeats a Think → Act → Observe → Think loop to solve problems.
Proposed by Yao et al. (2022). A core pattern behind modern AI agents (LangChain, AutoGPT, etc.)
that naturally integrates with tool use.

## Key Principles

- Synergy of reasoning and acting: Reasoning alone lacks information, acting alone lacks direction → interleaving is optimal
- Observation-based correction: Observe action results and feed them into the next reasoning step for adaptive problem-solving
- Interpretability: The Thought-Action-Observation trace provides an audit trail for easy debugging
- +6% over CoT and +14% over act-only approaches on HotpotQA

## Prompt Template

```
Solve the following problem using the ReAct pattern.

**Problem:** [Problem description]

**Thought 1:** [Analyze the current situation. What do you know, what don't you know? What should you do next?]
**Action 1:** [Action to perform — search, run command, API call, check file, etc.]
**Observation 1:** [Observed result — actual output, data, error messages, etc.]

**Thought 2:** [New reasoning based on the observation. Revise or confirm hypothesis]
**Action 2:** [Next action]
**Observation 2:** [Result]

**Thought 3:** [Is there enough information? Can a conclusion be drawn?]
**Action 3:** [Final action or further investigation]
**Observation 3:** [Result]

**Final Answer:** [Final conclusion and solution synthesized from all observations]
```

## Practical Example

**Scenario: "Production API response time suddenly increased to 5 seconds"**

Thought 1: Common causes for increased response time are DB, network, app logic. First, identify the bottleneck
Action 1: Run `kubectl top pods -n production`
Observation 1: api-server Pod CPU at 95%, other Pods normal

Thought 2: API server CPU is high. GC issue? Infinite loop? Traffic spike? Need to check logs
Action 2: Check `kubectl logs api-server-xxx --tail=100`
Observation 2: "Connection pool exhausted" error repeating

Thought 3: DB connection pool exhausted. Need to determine if it's a DB-side issue or app-side connection leak
Action 3: Query active DB connections → 500 (5x the max_connections: 100)
Observation 3: Confirmed app is not returning connections — a leak

Final Answer: Recent deployment missing a `finally` block in transaction handling → connections not returned → pool exhaustion → timeout

## Variations and Combinations

- **ReAct + CoT**: Elaborate the Thought portion with CoT
- **ReAct + Self-Refinement**: Self-critique and improve the final answer
- **ReAct + Role**: Perform ReAct "as a senior SRE"
- **ReAct + Tool Use**: Integrate with real tools (kubectl, SQL, etc.)

## Caveats

- Actions can have side effects (exercise caution in production environments)
- May fall into infinite loops when Observations differ from expectations (set a max iteration count)
- Without tool access, Actions may produce fabricated results
- Tokens accumulate with each cycle, so long chains increase cost

## Suitable Scenarios

Tasks requiring tool use, information retrieval, multi-step debugging, AI agent design, incident response

## References

- Yao et al. (2022) "ReAct: Synergizing Reasoning and Acting in Language Models"
- LangChain ReAct Agent implementation (practical reference)
