---
tags:
- techniques
- feynman
- simplification
- teaching
- understanding
---
# Feynman Technique — The Feynman Learning Method

## Concept

Richard Feynman's learning method. The principle that explaining a complex concept
so that even an elementary school student can understand it leads to true comprehension.
"If you can't explain it, you don't understand it."
4 steps: Choose a concept → Explain as if teaching → Identify gaps → Simplify.

## Key Principles

- Shattering the Illusion of Knowledge: Discovering parts you thought you understood but cannot explain
- Active learning: Explaining has a 90% retention rate compared to passive reading (Learning Pyramid)
- Gap identification: The exact points where you get stuck while explaining are precisely where understanding is lacking
- The power of simplification: The process of making complex things simple reveals the essence

## Prompt Template

```
**Topic:** [Concept to explain]

**Step 1 — Explain to an elementary school student:**
"[Topic] in simple terms is..."
[Explain without jargon, using everyday analogies and examples]

**Step 2 — Identify where you get stuck:**
Parts where the explanation stalled:
- ❓ [Gap 1]: Why I got stuck → [...]
- ❓ [Gap 2]: Why I got stuck → [...]

**Step 3 — Re-study and re-explain:**
[Re-explain from the beginning, filling in the gaps]

**Step 4 — Simplify and create analogies:**
- Core idea in one sentence: [...]
- Best analogy: "[Topic] is like [analogy]. Because..."
- If explaining to a 5-year-old: [...]

**Self-Assessment Checklist:**
- Can I answer if someone asks "Why?"? [Yes/No]
- Can I explain edge cases? [Yes/No]
- Can I explain the differences from related concepts? [Yes/No]
```

## Practical Example

**Scenario: "What is a Kubernetes Pod?"**

Step 1: "A Pod is like a shipping box. It's a box that carries your app as cargo.
You can put just one item in a box, or pack several related items together."

Step 2: Gap — "Why wrap containers in a Pod instead of running them directly?"
→ Need to study further: network namespace sharing, sidecar pattern, etc.

Step 3: "A Pod is like roommates living in the same apartment. They share the same address (IP),
use the same fridge (volumes), and always move together (scheduling)."

Step 4: "Pod = the smallest unit of a group of containers that are deployed and scheduled together"

## Variations and Combinations

- **Feynman + Socratic**: After explaining, verify understanding with Socratic questions
- **Feynman + Analogy**: Search for analogies across multiple domains
- **Feynman + Rubber Duck**: Debug by explaining to a rubber duck

## Caveats

- Unnecessary overhead for concepts you already know well
- Important nuances may be lost during simplification
- A bad analogy can cause misunderstanding (always state the analogy's limitations)
- Simplification has limits in fields where formal definitions matter (e.g., math, physics)

## Suitable Scenarios

Concept learning, technical documentation, team training, onboarding materials, explaining complex systems, interview preparation

## References

- Feynman, Richard (1985) "Surely You're Joking, Mr. Feynman!"
- Gleick, James (1992) "Genius: The Life and Science of Richard Feynman"
