---
tags:
- techniques
- self-refinement
- iteration
- improvement
- feedback
---
# Self-Refinement — Iterative Self-Improvement

## Concept

A technique where an LLM critiques its own output and iteratively improves it
based on that feedback. Systematized in Madaan et al. (2023) "Self-Refine" paper.
The Generate → Critique → Refine cycle repeats until convergence.

## Key Principles

- Iterative improvement: Since producing a perfect answer in one shot is difficult, quality improves incrementally
- Self-critique capability: GPT-4-class models have a remarkably strong ability to critique their own output
- Convergence: Quality typically converges after 2–3 iterations (further iterations yield diminishing returns)
- 5–20% performance improvement across diverse tasks including code generation, math, and reasoning

## Prompt Template

```
**Initial Output (Generate):**
First answer to [question/task]:
[Initial answer]

**Self-Critique (Critique):**
Evaluate the above answer against these criteria:
1. Accuracy: [Is it correct? Any errors?]
2. Completeness: [Is anything missing?]
3. Clarity: [Is it easy to understand?]
4. Practicality: [Is it actually applicable?]

Specific issues:
- [Issue 1]: [Why it's a problem, how to improve]
- [Issue 2]: [Why it's a problem, how to improve]

**Improved Output (Refine):**
[Revised answer incorporating the critique]

**Second Critique (if needed):**
[Are there remaining issues?]
- If yes: [Issues and improvement direction]
- If no: "Quality sufficient — finalized"

**Final Output:**
[Final answer]
```

## Practical Example

**Scenario: Dockerfile Optimization**

Initial: No multi-stage build, all build tools included in the final image (800MB)

Critique:
1. Image size excessive — build tools unnecessary
2. Layer cache inefficient — COPY . . runs too early
3. Security — running as root user

Improvement: Multi-stage build + COPY dependencies first + non-root USER → 120MB

Second critique: Missing .dockerignore → Added → Finalized

## Variations and Combinations

- **Self-Refinement + CoVe**: Include fact verification during critique
- **Self-Refinement + Role**: "Critique as a senior reviewer"
- **Self-Refinement + Rubric**: Provide an explicit scoring rubric for systematic critique
- **Self-Refinement + Few-Shot**: Provide examples of good critiques and improvements

## Caveats

- Weaker models may lack self-critique ability, potentially degrading quality
- More than 3 iterations can lead to "overfitting" — unnecessary modifications may creep in
- Vague critique criteria produce subjective and inconsistent feedback
- Unnecessary overhead when the original answer is already good

## Suitable Scenarios

Writing, code authoring, prompt improvement, documentation, any task where quality matters

## References

- Madaan et al. (2023) "Self-Refine: Iterative Refinement with Self-Feedback"
