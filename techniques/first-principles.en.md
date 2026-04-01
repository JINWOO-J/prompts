---
tags:
- techniques
- first-principles
- elon-musk
- decomposition
- fundamental
---
# First Principles Thinking — Reasoning from Fundamentals

## Concept

A thinking method that strips away all existing assumptions and conventions, then rebuilds from the most fundamental truths (laws of physics, mathematical facts, etc.). Famously used by Elon Musk to reduce SpaceX rocket costs. Originates from Aristotle's "First Principles."
"Why does a battery pack cost $600/kWh?" → Raw material cost is $80 → Source it directly.

## Key Principles

- Overcoming the limits of Reasoning by Analogy: Rebuild from fundamentals instead of "because everyone else does it"
- The source of innovation: Most breakthroughs start by breaking existing assumptions
- Cost structure decomposition: Breaking complex costs into raw materials/labor/time reveals optimization points
- Removing cognitive biases: Consciously eliminate anchoring, status quo bias, bandwagon effect, etc.

## Prompt Template

```
Analyze the following problem using First Principles Thinking.

**Problem/Situation:** [Describe the current situation]

**Step 1 — List existing assumptions:**
"What are we taking for granted?"
- Assumption 1: [...]
- Assumption 2: [...]
- Assumption 3: [...]

**Step 2 — Validate each assumption:**
| Assumption | Classification | Rationale |
|------------|---------------|-----------|
| Assumption 1 | Fact / Convention / Bias | [...] |
| Assumption 2 | Fact / Convention / Bias | [...] |
| Assumption 3 | Fact / Convention / Bias | [...] |

**Step 3 — Extract only fundamental truths:**
Confirmed immutable truths:
1. [Physical/logical constraints]
2. [Mathematical facts]

**Step 4 — Rebuild from fundamental truths:**
If we redesign the problem from scratch using only these truths:
[New solution]

**Step 5 — Compare:**
| Aspect | Conventional Approach | First Principles Approach | Difference |
|--------|----------------------|--------------------------|------------|
| Cost | | | |
| Complexity | | | |
| Risk | | | |
```

## Practical Example

**Scenario: "Why does our CI/CD pipeline take 30 minutes?"**

Existing assumptions: "Builds inherently take a long time", "We need to run all tests to be safe"

Validation:
- "Builds inherently take a long time" → Convention. Actual compilation is 2 min; the rest is dependency downloads
- "We need to run all tests" → Bias. Running only tests for changed modules covers 95%

Fundamental truths: Only changed code needs to be built/tested; dependencies can be cached

Rebuild: Incremental build + dependency cache + impact-scoped testing → 30 min → 4 min

## Variations and Combinations

- **First Principles + 5 Whys**: Repeatedly ask "Why?" when validating assumptions
- **First Principles + Inversion**: "What happens if this assumption is wrong?"
- **First Principles + Decomposition**: Break the problem down to atomic units
- **First Principles + MECE**: Classify fundamental truths using MECE

## Caveats

- Time-intensive — applying it to every problem is inefficient
- What you believe to be a "fundamental truth" may actually be an assumption (meta-validation needed)
- Ignoring compatibility with existing systems can produce impractical solutions
- Team/organizational constraints (politics, culture) should be included as "fundamental truths"

## Suitable Scenarios

Cost optimization, architecture redesign, situations requiring innovative approaches, technical debt resolution, process improvement

## References

- Aristotle, "Metaphysics" (the original source of the First Principles concept)
- Elon Musk, TED Talk (2013) — Battery cost analysis case study
- Tim Urban, "Wait But Why: The Cook and the Chef" (First Principles thinking explained)
