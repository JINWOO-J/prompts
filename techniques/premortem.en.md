---
tags:
- techniques
- premortem
- risk
- failure-analysis
- gary-klein
---
# Pre-mortem Analysis — Prospective Failure Analysis

## Concept

A technique where you assume "this project has failed" before it even starts,
then trace back the causes of failure. Proposed by Gary Klein (2007).
A preemptive version of the post-mortem.
"Prospective Hindsight" — research shows that describing future failure in past tense
improves failure-cause prediction accuracy by 30%.

## Key Principles

- Psychological safety: Assuming "it has failed" makes it easier to voice negative opinions
- Overcoming optimism bias: Adjusts excessive optimism during the planning phase to be more realistic
- Concrete risk identification: Specific failure scenarios rather than abstract "risks"
- Mitchell et al. (1989): Imagining the future in past tense improves causal reasoning by 30%

## Prompt Template

```
**Project:** [Project/plan description]
**Goal:** [Success criteria]
**Timeline:** [Expected duration]

---
**Point in time: After [timeline], this project has completely failed.**
**"What went wrong?"**

**Technical failure causes:**
1. [Cause]: [Why it happened] → [What impact it had]
2. [Cause]: [Why it happened] → [What impact it had]
3. [Cause]: [Why it happened] → [What impact it had]

**Organizational/process failure causes:**
1. [Cause]: [Why it happened] → [What impact it had]
2. [Cause]: [Why it happened] → [What impact it had]

**External factors:**
1. [Cause]: [Why it happened] → [What impact it had]

**Failure probability assessment:**
| Failure cause | Probability | Impact | Risk score |
|---------------|-------------|--------|------------|
| [...] | [High/Med/Low] | [High/Med/Low] | [High/Med/Low] |
| [...] | [...] | [...] | [...] |

**Preventive measures (what can be done now):**
| Failure cause | Preventive measure | Owner | Deadline | Cost |
|---------------|--------------------|-------|----------|------|
| [...] | [...] | [...] | [...] | [...] |

**Kill switch:** [Under what conditions should the project be stopped?]
```

## Practical Example

**Scenario: "K8s migration failure within 3 months"**

Technical: Stateful workload migration failure (DB, cache), security incident due to missing network policies
Organizational: Team lacks K8s experience causing 2x schedule overrun, burnout from running parallel operations
External: Cloud costs 3x over estimate, vendor lock-in

Prevention: K8s training upfront (2 weeks), migrate only stateless workloads first,
run cost simulation beforehand, establish rollback plan
Kill switch: Abort if pilot fails at the 1-month mark

## Variations and Combinations

- **Pre-mortem + Inversion**: Combine with inversion thinking for richer failure factors
- **Pre-mortem + 5 Whys**: Apply 5 Whys to each failure cause
- **Pre-mortem + MECE**: Classify failure causes using MECE framework
- **Pre-mortem + Red Team**: Analyze failure scenarios from an attacker's perspective

## Caveats

- Can drift into an overly negative atmosphere — facilitation is important
- Not all failure causes can be prevented — prioritization is needed
- If the team treats failures as "prophecies," it can become a self-fulfilling prophecy
- Cost of preventive measures may exceed the project itself — consider cost-effectiveness

## Suitable Scenarios

Project kickoff, risk management, migration planning, pre-launch review, sprint planning

## References

- Klein, Gary (2007) "Performing a Project Premortem" (Harvard Business Review)
- Mitchell et al. (1989) "Back to the Future: Temporal Perspective in the Explanation of Events"
