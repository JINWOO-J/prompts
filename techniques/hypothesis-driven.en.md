---
tags:
- techniques
- hypothesis
- scientific-method
- testing
- validation
---
# Hypothesis-Driven Analysis — Systematic Validation through Hypotheses

## Concept

Applying the scientific method to problem-solving. A systematic approach of forming hypotheses, designing validation methods, and confirming or refuting them with data. Theoretically grounded in Karl Popper's Falsificationism.
"Try to prove your hypothesis wrong. The hypothesis that survives is the strongest."

## Key Principles

- Efficient exploration: Narrow the search scope through hypotheses instead of random investigation
- Falsifiability: A good hypothesis is one that "can be proven wrong"
- Bias reduction: Attempting falsification instead of confirmation improves objectivity
- Prioritization: Order hypotheses by impact and ease of validation
- McKinsey methodology: "Day 1 Answer" — form and validate hypotheses from day one

## Prompt Template

```
**Observed Phenomenon:** [Problem/symptom description]

**Hypothesis Formation:**

| # | Hypothesis | Expected Rationale | Falsification Condition | Validation Method | Cost/Time | Priority |
|---|-----------|-------------------|------------------------|-------------------|-----------|----------|
| H1 | [Hypothesis 1] | [...] | [Reject if this is observed] | [...] | [...] | [1/2/3] |
| H2 | [Hypothesis 2] | [...] | [Reject if this is observed] | [...] | [...] | [1/2/3] |
| H3 | [Hypothesis 3] | [...] | [Reject if this is observed] | [...] | [...] | [1/2/3] |

**Validation Execution (in priority order):**

**H1 Validation:**
- Action: [Specific validation steps]
- Expected result (if hypothesis is correct): [...]
- Actual result: [Data/observation]
- Verdict: ✅ Confirmed / ❌ Falsified / ⚠️ Inconclusive

**H2 Validation:** (if H1 is falsified)
- Action: [...]
- Actual result: [...]
- Verdict: [...]

**Conclusion:**
- Confirmed hypotheses: [...]
- Falsified hypotheses: [...]
- Remaining uncertainties: [...]
- Next action: [Measures based on confirmed hypotheses]
```

## Practical Example

**Scenario: "API response time intermittently exceeds 10 seconds"**

H1: DB slow query (rationale: recent data growth) → Validation: Check slow query log
H2: GC pause (rationale: Java app, high heap usage) → Validation: Analyze GC logs
H3: External API timeout (rationale: third-party dependency) → Validation: External call latency metrics

H1 validation: No queries over 10s in slow query log → ❌ Falsified
H2 validation: Full GC of 8s found in GC log, timing matches → ✅ Confirmed
→ Conclusion: Switch to G1GC + adjust heap size

## Variations and Combinations

- **Hypothesis + CoT**: Use CoT for detailed reasoning through each hypothesis validation
- **Hypothesis + MECE**: Classify hypotheses using MECE to prevent omissions
- **Hypothesis + Bayesian**: Assign prior probabilities and update with evidence
- **Hypothesis + A/B Test**: Validate hypotheses through A/B testing

## Caveats

- Biased hypotheses lead to biased validation — generating diverse hypotheses is critical
- Confirmation bias: Try to "falsify" rather than "prove" your hypothesis
- If all hypotheses are falsified, new ones are needed — keep an open mind
- Deprioritize high-cost hypotheses, but make exceptions for high-impact ones

## Suitable Scenarios

Debugging, incident analysis, A/B testing, performance optimization, experiment design, consulting

## References

- Popper, Karl (1959) "The Logic of Scientific Discovery" (Falsificationism)
- Rasiel, Ethan (1999) "The McKinsey Way" (Hypothesis-driven problem solving)
