---
tags:
- techniques
- contrastive
- comparison
- contrast
- differentiation
---
# Contrastive Prompting — Comparative Analysis Technique

## Concept

A technique that explicitly compares and contrasts two or more subjects
to structurally analyze their differences and commonalities.
It clarifies tradeoffs between options to support decision-making.
Showing "good examples vs bad examples" is also a form of contrastive prompting.

## Key Principles

- Highlighting differences: Comparative analysis reveals distinctions more clearly than individual analysis
- Tradeoff visibility: Pros and cons of each option are displayed side by side for easy comparison
- Bias reduction: Analyzing only one option leads to confirmation bias; contrasting enables a balanced perspective
- Good/Bad examples: Showing the LLM "do this / don't do this" improves accuracy

## Prompt Template

```
Systematically compare and contrast the following subjects.

**Subject A:** [First option]
**Subject B:** [Second option]
**(Optional) Subject C:** [Third option]

**Comparative Analysis:**

| Criterion | A | B | (C) | Notes |
|-----------|---|---|-----|-------|
| [Criterion 1 — Performance] | [...] | [...] | [...] | [...] |
| [Criterion 2 — Cost] | [...] | [...] | [...] | [...] |
| [Criterion 3 — Complexity] | [...] | [...] | [...] | [...] |
| [Criterion 4 — Scalability] | [...] | [...] | [...] | [...] |
| [Criterion 5 — Ecosystem] | [...] | [...] | [...] | [...] |

**Commonalities:**
- [Characteristics shared by A and B]

**Key Differences:**
- [Most important difference 1]: [Explanation]
- [Most important difference 2]: [Explanation]

**Situational Recommendations:**
- For [Situation X], A is suitable: [Reason]
- For [Situation Y], B is suitable: [Reason]
- For [Situation Z], C is suitable: [Reason]

**Conclusion:** [Overall judgment]
```

## Practical Example

**Scenario: "PostgreSQL vs MySQL vs MongoDB"**

| Criterion | PostgreSQL | MySQL | MongoDB |
|-----------|-----------|-------|---------|
| Data model | Relational + JSON | Relational | Document |
| Complex queries | Excellent (CTE, window) | Moderate | Limited |
| Write performance | Moderate | Excellent | Excellent |
| Schema flexibility | Medium (JSONB) | Low | High |

Situational: OLAP → PostgreSQL, Simple CRUD → MySQL, Frequent schema changes → MongoDB

## Variations and Combinations

- **Contrastive + SWOT**: Analyze each subject with SWOT, then compare
- **Contrastive + Hypothesis**: Set "A is better than B" as a hypothesis and test it
- **Contrastive + Few-Shot**: Present good vs bad examples as contrasts

## Caveats

- The choice of comparison criteria drives the outcome — watch for biased criteria
- Tables become complex with more than 3 subjects (2-3 is optimal)
- Criteria that are hard to quantify (e.g., user experience) can be subjective
- The goal is not to pick a "winner" — it's to find the best fit for each situation

## Suitable Scenarios

Technology selection, architecture comparison, library evaluation, decision-making, vendor assessment

## References

- Yin et al. (2023) "Contrastive Chain-of-Thought Prompting"
- Mao et al. (2024) "Contrastive Prompting for LLM Reasoning"
