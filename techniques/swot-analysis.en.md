---
tags:
- techniques
- swot
- strategy
- analysis
- planning
---
# SWOT Analysis — Strengths, Weaknesses, Opportunities, and Threats

## Concept

A strategic framework that analyzes a situation along four axes:
Strengths, Weaknesses, Opportunities, and Threats.
Systematized by Albert Humphrey (1960s, Stanford Research Institute).
Strategies are derived by distinguishing internal factors (S/W) from external factors (O/T).

## Key Principles

- Structured analysis: Systematically organizes the situation along 4 axes
- Internal/external distinction: Separates what you can control (internal) from what you cannot (external)
- Strategy derivation: The TOWS matrix generates 4 cross-strategies
- Communication: Conveys the situation concisely to executives and stakeholders

## Prompt Template

```
**Subject:** [Description of system/project/technology/team]

**SWOT Matrix:**

| | Helpful | Harmful |
|---|--------|--------|
| **Internal** | **S — Strengths** | **W — Weaknesses** |
| | 1. [...] | 1. [...] |
| | 2. [...] | 2. [...] |
| | 3. [...] | 3. [...] |
| **External** | **O — Opportunities** | **T — Threats** |
| | 1. [...] | 1. [...] |
| | 2. [...] | 2. [...] |
| | 3. [...] | 3. [...] |

**TOWS Strategy Derivation:**

| Strategy | Description | Specific Actions |
|----------|-------------|-----------------|
| **SO (Strengths × Opportunities)** | Leverage strengths to maximize opportunities | [...] |
| **WO (Weaknesses × Opportunities)** | Address weaknesses to capitalize on opportunities | [...] |
| **ST (Strengths × Threats)** | Use strengths to counter threats | [...] |
| **WT (Weaknesses × Threats)** | Minimize weaknesses and threats (defensive) | [...] |

**Priorities:**
1. [Most important strategy]: [Reason]
2. [Second strategy]: [Reason]
```

## Practical Example

**Scenario: "SWOT of the team's monitoring system"**

S: Prometheus+Grafana expertise, in-house alert rule library
W: No distributed tracing, insufficient log centralization, dashboards not standardized
O: OpenTelemetry maturing, managed services (Datadog, Grafana Cloud) costs declining
T: Microservices migration increasing observability targets 10x, compliance requirements tightening

SO: Prometheus expertise + OTel adoption → Build a unified observability platform
WO: Use managed services to address distributed tracing/logging weaknesses
ST: Leverage in-house alert rules to maintain monitoring coverage during MSA migration
WT: Prioritize building minimum compliance dashboards first

## Variations and Combinations

- **SWOT + MECE**: Validate each axis's items for MECE completeness
- **SWOT + Six Hats**: Map Yellow=S/O, Black=W/T, Green=strategy derivation
- **SWOT + Hypothesis**: Frame each strategy as a hypothesis and plan validation
- **SWOT + OKR**: Convert TOWS strategies into OKRs

## Caveats

- Meaningless if you only list items without deriving strategies
- The internal/external distinction can be ambiguous (e.g., is tech debt internal or external?)
- As a static analysis, it struggles to reflect changes over time
- Highly subjective — multiple perspectives should be aggregated

## Suitable Scenarios

Technology selection, project evaluation, competitive analysis, migration decisions, team capability assessment, strategy formulation

## References

- Humphrey, Albert (1960s) Stanford Research Institute project
- Weihrich, Heinz (1982) "The TOWS Matrix" (framework for deriving strategies from SWOT)
