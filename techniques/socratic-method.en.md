---
tags:
- techniques
- socratic
- questioning
- critical-thinking
- dialogue
---
# Socratic Method — Systematic Questioning for Deep Understanding

## Concept

A technique that guides the other party (or oneself) to reach deep understanding
through systematic questioning, rather than providing answers directly. Derived from
Socrates' method of dialogue. Richard Paul's 6 types of Socratic questions are widely
used as a systematic framework.

## Key Principles

- Active learning: Discovering answers through questions leads to deeper understanding than being given answers
- Exposing assumptions: Questions reveal hidden assumptions and biases
- Critical thinking training: Improves the ability to filter out unsupported claims
- Richard Paul's 6 types: Clarification, probing assumptions, probing reasons/evidence, questioning viewpoints, probing implications, meta-questions

## Prompt Template

```
Explore the following topic using the Socratic method.

**Topic:** [Topic to explore]

**Step 1 — Clarification Questions:**
- What exactly does this mean?
- Can you define the core concept in one sentence?
- Can you give a concrete example?

**Step 2 — Probing Assumptions:**
- What assumptions are being made?
- How would the conclusion change if that assumption were wrong?
- Does this assumption always hold?

**Step 3 — Probing Reasons/Evidence:**
- What is the basis for thinking so?
- How reliable is this evidence?
- Is there any counter-evidence?

**Step 4 — Questioning Viewpoints:**
- How does this look from a different perspective?
- How would [the opposing side] counter this?
- How do different stakeholders view this differently?

**Step 5 — Probing Implications:**
- What are the implications of this conclusion?
- What consequences follow?
- What is the worst-case scenario?

**Step 6 — Meta-Questions (Questions about the Question):**
- Why is this question important?
- What are we missing?
- What would be a better question to ask?
```

## Practical Example

**Scenario: "Should we migrate to microservices?"**

Clarification: What exactly does "microservices" mean? Independent deployment? Independent DB?
Probing assumptions: Is the assumption "monoliths can't scale" actually true? → Shopify handles billions of requests with a monolith
Evidence: What's the basis for needing the migration? → "The team is growing" → What's the correlation between team size and architecture?
Viewpoint shift: From a junior developer's perspective? → Increased complexity triples onboarding time
Implications: If we migrate? → Increased operational complexity, distributed transaction issues, network latency
Meta: Is the real problem the architecture, or the team structure?

## Variations and Combinations

- **Socratic + Devil's Advocate**: Use questions to elicit counterarguments
- **Socratic + First Principles**: Use questions to drill down to fundamental assumptions
- **Socratic + CoT**: Reason through each question's answer step by step

## Caveats

- Time-consuming — not suitable for urgent decisions
- Questions that are too abstract make it hard to reach practical conclusions
- The other party (or LLM) may misunderstand the intent of the questions
- Inefficient when the answer is already known

## Suitable Scenarios

Deep analysis, decision validation, team discussions, requirements elicitation, code review, architecture decisions, education

## References

- Plato, "Meno", "Theaetetus" (original Socratic dialogues)
- Richard Paul & Linda Elder (2006) "The Art of Socratic Questioning"
- Paul & Elder's 6 Socratic Question Types Framework
