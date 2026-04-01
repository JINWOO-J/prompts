---
tags:
- techniques
- mece
- framework
- classification
- mckinsey
---
# MECE Framework — Mutually Exclusive, Collectively Exhaustive

## Concept

Mutually Exclusive, Collectively Exhaustive.
A classification technique ensuring all items are non-overlapping (ME) and cover the entire space without gaps (CE). Systematized by Barbara Minto of McKinsey Consulting. The gold standard for structuring problems.

## Key Principles

- Preventing omissions (CE): Cover all possibilities so nothing is missed
- Preventing overlaps (ME): No overlap between categories, avoiding double counting/analysis
- Communication clarity: MECE structures are easy for the audience to understand
- Foundation of the Pyramid Principle: The core of logical document/presentation structure

## Prompt Template

```
Classify the following topic using the MECE principle.

**Topic:** [Subject to classify]

**MECE Classification:**

| # | Category | Included Items | Excluded Items (ME Validation) |
|---|----------|---------------|-------------------------------|
| 1 | [Category name] | [...] | [...] |
| 2 | [Category name] | [...] | [...] |
| 3 | [Category name] | [...] | [...] |
| 4 | [Category name] | [...] | [...] |

**CE Validation (Collectively Exhaustive):**
- Do the above categories cover everything? [Yes/No]
- Missing items: [List if any, otherwise "None"]
- Coverage rate: [Estimated %]

**ME Validation (Mutually Exclusive):**
- Overlapping items between categories: [List if any, otherwise "None"]
- Overlap resolution: [Reclassification approach]

**Final MECE Structure:**
[Finalized classification after validation]
```

## Practical Example

**Scenario: "Classifying API response delay causes"**

MECE Classification:
1. Network layer: DNS, TCP, TLS, routing
2. Application layer: Code logic, memory, GC, threads
3. Data layer: DB queries, cache misses, connection pool
4. External dependencies: Third-party APIs, CDN, external services

CE Validation: All request paths covered ✅
ME Validation: "DB connection pool" could fall under both Network and Data → Assigned to Data layer

## Variations and Combinations

- **MECE + 5 Whys**: Apply 5 Whys within each category
- **MECE + Fishbone**: Use MECE categories as Fishbone bones
- **MECE + Decomposition**: Recursively decompose each category into sub-MECE structures
- **MECE + Prioritization**: Prioritize after MECE classification

## Caveats

- Perfect MECE is hard to achieve in practice (approximate MECE is sufficient)
- Over-classification hurts practicality (3–7 categories is optimal)
- The choice of classification axis determines the outcome — try multiple axes
- MECE can break down for dynamically changing subjects

## Suitable Scenarios

Problem structuring, cause classification, requirements organization, strategy formulation, report structuring, issue triage

## References

- Barbara Minto (1987) "The Pyramid Principle"
- McKinsey & Company problem-solving framework
