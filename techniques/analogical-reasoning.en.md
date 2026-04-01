---
tags:
- techniques
- analogy
- metaphor
- transfer
- cross-domain
---
# Analogical Reasoning — Reasoning by Analogy

## Concept

A technique that applies similar problems or solutions from other domains to the current problem.
Leverages structural similarity in the form of 'A:B = C:?'.
Theoretically grounded in Gentner's (1983) Structure Mapping Theory.
Innovative solutions often emerge from cross-domain analogies (e.g., Velcro = burdock burrs).

## Key Principles

- Structural similarity: The key is relational structure, not surface-level resemblance
- Knowledge transfer: Applying knowledge from a familiar domain to a new one
- Creative leaps: Discovering solutions that pure logical reasoning cannot reach
- Communication: Explaining complex concepts through familiar analogies improves comprehension

## Prompt Template

```
**Current Problem:** [Problem to solve]

**Analogy Exploration:**

**Analogy 1 — Similar problem in [Domain A]:**
- Original problem: [Problem in Domain A]
- Original solution: [Solution in Domain A]
- Structural similarity: [What structural parallels exist]
- Application to our problem: [Specific application plan]

**Analogy 2 — Similar problem in [Domain B]:**
- Original problem: [Problem in Domain B]
- Original solution: [Solution in Domain B]
- Structural similarity: [What structural parallels exist]
- Application to our problem: [Specific application plan]

**Structure Mapping Table:**
| Source Domain Element | Current Problem Element | Mapping Rationale |
|----------------------|------------------------|-------------------|
| [Element A] | [Corresponding element] | [...] |
| [Element B] | [Corresponding element] | [...] |
| [Solution mechanism] | [Application plan] | [...] |

**Limitations of the Analogy:**
- Breaking point: [Where does the analogy no longer hold]
- Constraints unique to the current problem: [Constraints absent in the source domain]
- Gaps to address: [What the analogy alone cannot cover]
```

## Practical Example

**Scenario: "Handling communication failures between microservices"**

Analogy 1 — Power Grid:
- Source: When one power plant goes down, others absorb the load
- Application: Circuit Breaker pattern — isolate the failing service and switch to a fallback

Analogy 2 — Immune System:
- Source: Detect virus → quarantine → produce antibodies → remember
- Application: Anomaly detection → service isolation → auto-recovery → pattern learning (AIOps)

Structure mapping: Power plant = Service, Power grid = Service mesh, Circuit breaker = Circuit Breaker

## Variations and Combinations

- **Analogy + First Principles**: Validate the analogy using first-principles reasoning
- **Analogy + Feynman**: Use analogies to explain concepts and verify understanding
- **Analogy + Lateral Thinking**: Deliberately search for analogies from distant domains

## Caveats

- Surface-level similarity can be misleading (always verify structural similarity)
- Failing to recognize where the analogy breaks down can lead to wrong conclusions
- Analogies from overly distant domains may lack practical applicability
- Analogies are hypothesis-generation tools, not proof tools — separate validation is required

## Suitable Scenarios

Innovative problem-solving, architecture design, explanation/education, cross-domain learning, brainstorming

## References

- Gentner, Dedre (1983) "Structure-Mapping: A Theoretical Framework for Analogy"
- Holyoak & Thagard (1995) "Mental Leaps: Analogy in Creative Thought"
