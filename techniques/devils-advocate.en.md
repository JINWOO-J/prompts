---
tags:
- techniques
- devils-advocate
- counter-argument
- critical-thinking
---
# Devil's Advocate — Counter-Argument Technique

## Concept

A technique that deliberately takes the opposing position to uncover weaknesses in an argument.
Originated from the 13th-century Catholic canonization process (Advocatus Diaboli).
Prevents groupthink and strengthens the robustness of decisions.

## Key Principles

- Overcoming confirmation bias: Consciously breaking the tendency to seek only evidence that supports your position
- Early weakness detection: Finding and addressing weaknesses before execution
- Improved decision quality: Arguments that survive counter-arguments are more robust
- Psychological safety: Critiquing as a "role" makes it constructive criticism rather than personal attack

## Prompt Template

```
**Original Claim/Proposal:** [Description of the claim]

**Devil's Advocate Analysis:**

**1. Core Weaknesses (Top 3):**
1. [Weakness]: [Why it's a problem, specific scenario]
2. [Weakness]: [Why it's a problem, specific scenario]
3. [Weakness]: [Why it's a problem, specific scenario]

**2. Hidden Assumptions:**
- [Assumption 1]: What if this is wrong? → [Consequence]
- [Assumption 2]: What if this is wrong? → [Consequence]

**3. Alternatives from the Opposing Perspective:**
- Alternative A: [Description] — Pros: [...], Cons: [...]
- Alternative B: [Description] — Pros: [...], Cons: [...]

**4. Failure Scenarios:**
- Worst case: [Scenario and impact]
- Most likely failure: [Scenario and impact]

**5. Final Judgment:**
Should the original claim be maintained / modified / abandoned?
- Judgment: [Maintain/Modify/Abandon]
- Rationale: [...]
- If modifying: [Specific remediation plan]
```

## Practical Example

**Scenario: "Let's use Redis as our session store"**

Weakness 1: If Redis goes down, all users are logged out → single point of failure
Weakness 2: Memory cost is 10x that of a DB → costs explode as users grow
Weakness 3: Session data persistence is not guaranteed → data loss on restart

Hidden assumption: "Sessions require fast reads" → Is session lookup actually the bottleneck?

Alternatives: JWT tokens (no server state needed) / DB + cache layer

Judgment: Modify — Redis Sentinel + AOF persistence + JWT hybrid

## Variations and Combinations

- **Devil's Advocate + Six Hats**: Strengthen the Black Hat with Devil's Advocate
- **Devil's Advocate + Red Team**: Add attack scenarios from a security perspective
- **Devil's Advocate + Pre-mortem**: Systematize failure scenarios more thoroughly

## Caveats

- Excessive counter-arguments can paralyze decision-making (analysis paralysis)
- Counter-arguments must be constructive — propose alternatives, not just negation
- When used in teams, make it clear it's a "role" to prevent personal conflict
- Applying it to every decision is inefficient — reserve for important decisions only

## Suitable Scenarios

Decision validation, architecture reviews, proposal evaluation, risk assessment, investment decisions

## References

- Janis, Irving (1972) "Victims of Groupthink" (groupthink research)
- Nemeth et al. (2001) "Devil's Advocate versus Authentic Dissent"
