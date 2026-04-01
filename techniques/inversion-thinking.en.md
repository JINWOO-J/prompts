---
tags:
- techniques
- inversion
- reverse
- charlie-munger
- premortem
- failure-avoidance
---
# Inversion Thinking — Reasoning in Reverse

## Concept

Instead of asking "How do I succeed?", first ask "How would I guarantee failure?"
A favorite technique of Charlie Munger: "Tell me where I'm going to die, so I'll never go there."
Derived from Carl Jacobi's mathematical inversion principle: "Invert, always invert."
By eliminating causes of failure in advance, you increase the probability of success.

## Key Principles

- Failure avoidance > pursuing success: Avoiding major failures is more effective than accumulating small wins
- Overcoming cognitive biases: Inversion counteracts optimism bias toward success
- Deriving concrete actions: "How to succeed" is vague, but "How to fail" is specific
- Core of risk management: Eliminate the downside first, and the upside follows naturally

## Prompt Template

```
**Goal:** [What you want to achieve]

**Inversion question: "How would I guarantee this goal fails?"**

**Top 5 guaranteed ways to fail:**
1. [Do this and failure is certain]: [Specific description and mechanism]
2. [Do this and failure is certain]: [Specific description and mechanism]
3. [Do this and failure is certain]: [Specific description and mechanism]
4. [Do this and failure is certain]: [Specific description and mechanism]
5. [Do this and failure is certain]: [Specific description and mechanism]

**Re-inversion — How to avoid the above failure factors?**
| Failure Factor | Avoidance Strategy | Concrete Action | Verification Method |
|----------------|-------------------|-----------------|---------------------|
| 1 | [...] | [...] | [...] |
| 2 | [...] | [...] | [...] |
| 3 | [...] | [...] | [...] |
| 4 | [...] | [...] | [...] |
| 5 | [...] | [...] | [...] |

**Key Insight:**
Most important insight from the inversion: [...]
What needs to change in the existing plan: [...]
```

## Practical Example

**Scenario: "How to guarantee an SRE team's on-call system fails?"**

1. Don't document anything → New on-callers fumble from scratch every time
2. Don't define escalation paths → Chaos during severe incidents
3. Turn on every alert → Alert fatigue causes real incidents to be missed
4. Skip postmortems → The same incidents keep recurring
5. Pile all on-call shifts onto one person → Burnout

Re-inversion: Write runbooks, create escalation matrix, tune alerts, build postmortem culture, fair rotation

## Variations and Combinations

- **Inversion + Pre-mortem**: Analyze failure scenarios more systematically
- **Inversion + First Principles**: Dig to the root of failure causes
- **Inversion + Devil's Advocate**: Challenge the inversion results with counterarguments
- **Inversion + Checklist**: Turn failure avoidance strategies into a checklist

## Caveats

- Can lead to excessively negative thinking — balance is needed
- Listing every failure factor can cause analysis paralysis
- Failure avoidance alone cannot drive innovative success
- When used in teams, facilitation is needed to prevent a negative atmosphere

## Suitable Scenarios

Risk management, project planning, incident prevention, strategy validation, investment decisions, checklist creation

## References

- Munger, Charlie (2005) "Poor Charlie's Almanack" (numerous inversion thinking examples)
- Jacobi, Carl (19th century) "Invert, always invert" (mathematical inversion principle)
