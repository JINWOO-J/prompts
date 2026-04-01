---
tags:
- techniques
- tot
- reasoning
- branching
- exploration
---
# Tree-of-Thoughts (ToT) — Branching Exploration Reasoning

## Concept

A technique that explores multiple thought branches simultaneously rather than following
a single reasoning path, evaluating each branch to select the most promising one.
Proposed by Yao et al. (2023). If CoT is a single path, ToT extends it into a tree structure.
Exploration can use BFS (breadth-first) or DFS (depth-first) strategies.

## Key Principles

- Expanded search space: Overcomes CoT's single-path limitation by considering multiple possibilities simultaneously
- Self-evaluation: The LLM evaluates the promise of each branch itself, enabling pruning
- Backtracking: Can return from dead-end paths to explore alternatives
- Significant performance improvement over CoT in Game of 24, creative writing, etc. (74% vs 4%)

## Prompt Template

```
Analyze the following problem using the Tree-of-Thoughts approach.

**Problem:** [Problem description]

**Step 1 — Generate Possible Approaches (Branch Generation):**
- Approach A: [Description]
- Approach B: [Description]
- Approach C: [Description]

**Step 2 — Evaluate Each Approach (Pruning):**
| Approach | Feasibility (1-5) | Effectiveness (1-5) | Risk (1-5) | Overall |
|----------|-------------------|---------------------|------------|---------|
| A | | | | |
| B | | | | |
| C | | | | |

**Step 3 — Select the Optimal Path and Go Deeper:**
Selection: [Approach X]
Reason: [Evaluation rationale]

**Step 4 — Sub-Branches Within the Selected Path:**
- Sub-plan X-1: [...]
- Sub-plan X-2: [...]
→ Final selection: [X-N] Reason: [...]
```

## Practical Example

**Scenario: Legacy monolith → microservices migration strategy**

Approach A: Big Bang migration → Evaluation: Risk 5, Effectiveness 4 → Eliminated
Approach B: Strangler Fig pattern → Evaluation: Risk 2, Effectiveness 4 → Promising
Approach C: MSA for new features only → Evaluation: Risk 1, Effectiveness 2 → Conservative

→ Selected B, then sub-branches:
B-1: API Gateway-based routing → Medium implementation complexity
B-2: Event-driven decomposition → Data consistency issues
→ Selected B-1 (suitable for incremental migration)

## Variations and Combinations

- **ToT + Self-Consistency**: Apply majority voting within each branch
- **ToT + SWOT**: Evaluate each branch using SWOT
- **ToT + Devil's Advocate**: Challenge promising branches with counterarguments
- **ToT + Decomposition**: Break each branch into sub-problems

## Caveats

- Excessive overhead for simple problems — CoT is often sufficient
- Too many branches can make evaluation itself inaccurate (3–5 is optimal)
- LLM self-evaluation is not always accurate — external verification is needed
- Token consumption is 3–5x or more compared to CoT

## Suitable Scenarios

Strategic decision-making, architecture design, complex trade-off analysis, creative problem solving, migration planning

## References

- Yao et al. (2023) "Tree of Thoughts: Deliberate Problem Solving with Large Language Models"
- Long (2023) "Large Language Model Guided Tree-of-Thought"
