---
tags:
- techniques
- self-consistency
- voting
- ensemble
---
# Self-Consistency — Multi-Path Majority Voting

## Concept

A technique that generates multiple independent reasoning paths for the same problem,
then selects the most frequently reached answer as the final answer.
Proposed by Wang et al. (2022). Provides more stable and reliable results than single CoT.
It implements the idea of ensemble learning at the prompt level.

## Key Principles

- Robustness through diversity: When different reasoning paths converge on the same answer, confidence is high
- Bias reduction: Majority voting offsets accidental errors from any single path
- Temperature tuning: Use high temperature (0.7–1.0) to generate diverse paths
- +17.9% accuracy improvement over CoT on GSM8K

## Prompt Template

```
Solve the following problem independently from 3 different perspectives.
Each path should reason independently without referencing previous paths.

**Problem:** [Problem description]

**Path 1 (Perspective: [A]):**
[Reasoning process] → Conclusion: [X]

**Path 2 (Perspective: [B]):**
[Reasoning process] → Conclusion: [Y]

**Path 3 (Perspective: [C]):**
[Reasoning process] → Conclusion: [Z]

**Majority Vote:**
- Conclusion distribution: X=N times, Y=N times, Z=N times
- Final answer: [Most frequent conclusion]
- Agreement rate: [N/3]
- Disagreement analysis: [Why the paths diverged]
```

## Practical Example

**Scenario: "What's causing this API response latency?"**

Path 1 (Network perspective): DNS lookup delay → Conclusion: DNS cache miss
Path 2 (DB perspective): Slow query → Conclusion: Missing index
Path 3 (App perspective): N+1 query pattern → Conclusion: Missing index + N+1

Majority vote: "Missing index" mentioned in 2/3 paths → Confirmed as primary cause
Follow-up: N+1 pattern also needs investigation

## Variations and Combinations

- **Self-Consistency + CoT**: Reason each path with detailed CoT (the default combination)
- **Self-Consistency + Role**: Reason each path as a different expert persona
- **Self-Consistency + Temperature variation**: Use different temperatures per path

## Caveats

- Cost scales linearly with the number of paths (3–5 is practical)
- All paths can be wrong in the same direction (systematic bias)
- Majority voting may be meaningless for open-ended questions with no single correct answer
- Prompt design requires care to ensure paths are truly "independent"

## Suitable Scenarios

Problems with clear correct answers, numerical calculations, classification tasks, high-confidence diagnostics, pinpointing code bug causes

## References

- Wang et al. (2022) "Self-Consistency Improves Chain of Thought Reasoning in Language Models"
