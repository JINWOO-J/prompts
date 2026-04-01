---
tags:
- techniques
- fishbone
- ishikawa
- cause-effect
- rca
---
# Fishbone (Ishikawa) — Cause-and-Effect Diagram

## Concept

A diagram with the problem (effect) as the head and cause categories as the bones.
Proposed by Kaoru Ishikawa (1968). Systematically classifies causes using the 6M categories
(Man, Machine, Method, Material, Measurement, Mother Nature).
More effective than 5 Whys for analyzing compound causes.

## Key Principles

- Multi-dimensional analysis: Explore causes across multiple categories simultaneously, not just a single causal chain
- Visual structure: Grasp cause relationships at a glance through the diagram format
- Suited for team brainstorming: Multiple people can add causes to each category
- Natural fit with MECE: The 6M categories form a MECE structure

## Prompt Template

```
**Problem (Fish Head):** [Problem description]

**Cause Analysis (Fish Bones):**

**1. People (Team/Personnel):**
- [Cause 1-1]: [Details — skill level, communication, staffing gaps, etc.]
- [Cause 1-2]: [Details]

**2. Process (Methods/Procedures):**
- [Cause 2-1]: [Details — missing procedures, inefficient workflows, etc.]
- [Cause 2-2]: [Details]

**3. Technology (Tools/Systems):**
- [Cause 3-1]: [Details — software bugs, hardware limitations, missing tools, etc.]
- [Cause 3-2]: [Details]

**4. Environment (Infrastructure):**
- [Cause 4-1]: [Details — infrastructure, network, external services, etc.]

**5. Measurement (Monitoring):**
- [Cause 5-1]: [Details — missing metrics, unconfigured alerts, lack of visibility, etc.]

**6. Data/Material (Resources):**
- [Cause 6-1]: [Details — data quality, resource shortages, etc.]

**Cause Prioritization:**
| Rank | Cause | Category | Impact | Actionability |
|------|-------|----------|--------|---------------|
| 1 | [...] | [...] | High/Med/Low | High/Med/Low |
| 2 | [...] | [...] | | |
| 3 | [...] | [...] | | |

**Most likely root cause:** [Selection and rationale]
```

## Practical Example

**Scenario: "30% deployment failure rate"**

People: Insufficient training for deployers, poor on-call handoffs
Process: No deployment checklist, undefined rollback procedures
Technology: Unstable CI/CD pipeline, low test coverage
Environment: Discrepancies between staging and production environments
Measurement: Deployment success rate metrics not collected
Data: Configuration files not separated by environment

→ Priority 1: Stabilize CI/CD pipeline + strengthen testing

## Variations and Combinations

- **Fishbone + 5 Whys**: Apply 5 Whys to each bone's causes to reach root causes
- **Fishbone + MECE**: Validate categories using MECE
- **Fishbone + Prioritization Matrix**: Impact × Actionability matrix for each cause

## Caveats

- Fixed categories may not fit every domain (use custom categories)
- Difficult to represent interactions (cross-effects) between causes
- Working alone without brainstorming can lead to biased cause listing
- Merely listing causes without validation/prioritization is meaningless

## Suitable Scenarios

Compound cause analysis, incident RCA, quality issues, process improvement, team retrospectives

## References

- Ishikawa, Kaoru (1968) "Guide to Quality Control"
- ASQ (American Society for Quality) Fishbone Diagram Guide
