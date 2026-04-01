---
tags:
- techniques
- ooda
- decision-loop
- military
- agile
- incident-response
---
# OODA Loop — Observe-Orient-Decide-Act

## Concept

A repeating loop of Observe → Orient → Decide → Act.
Developed by Colonel John Boyd for air combat decision-making.
The key to winning is cycling through the OODA loop faster than your opponent.
Widely applied to incident response, agile operations, and competitive strategy.

## Key Principles

- Speed advantage: Cycling through the loop faster than the opponent (or problem) secures initiative
- Orient is the core: Contextual interpretation, not mere observation, determines decision quality
- Implicit guidance: Through repetition, Orient → Act becomes automatic, allowing the Decide step to be skipped (intuition)
- Feedback loop: The result of Act feeds into the next Observe, enabling continuous adaptation

## Prompt Template

```
**Situation:** [Describe the current situation]

**🔍 Observe — "What do you see?"**
- Current data/metrics: [Metrics, logs, alerts, etc.]
- Changes detected: [What has changed compared to before]
- External signals: [User reports, dependent service status, etc.]
- Information gaps: [What is still unknown]

**🧭 Orient — "What does this mean?"**
- Data interpretation: [Meaning of the observations]
- Comparison with past experience: [Has a similar situation occurred before?]
- Mental model application: [Which pattern does this match?]
- Cultural/organizational context: [Team/organizational constraints to consider]
- Hypothesis: [Most likely explanation]

**🎯 Decide — "What will you do?"**
- Options: [A / B / C]
- Expected outcome for each option: [...]
- Choice: [X]
- Rationale: [Based on the Orient assessment]
- Reversibility: [Reversible / Irreversible]

**⚡ Act — "Execute and observe"**
- Immediate action: [Specific action]
- Monitoring execution results: [Which metrics to watch]
- Next OODA cycle trigger: [Under what conditions to start observing again]
- Timebox: [Maximum wait time until next assessment]
```

## Practical Example

**Scenario: "Production latency spike incident"**

Observe: P99 latency 200ms → 5s, error rate 0.1% → 15%, last deployment 10 minutes ago
Orient: Occurred right after deployment → new code is likely the cause. Similar pattern seen before
Decide: Immediate rollback (reversible, low risk) vs hotfix (time-consuming, high risk) → Choose rollback
Act: Execute rollback → Confirm latency normalized → Next OODA: analyze root cause then redeploy fix

→ Total loop time: 5 minutes (fast OODA reduces MTTR)

## Variations and Combinations

- **OODA + ReAct**: Map Observe-Orient to Thought, Act to Action
- **OODA + 5 Whys**: Use 5 Whys in the Orient phase to identify root cause
- **OODA + Hypothesis**: Formulate hypotheses in Orient, validate in Act

## Caveats

- Skipping the Orient phase leads to misguided actions
- Decisions often must be made with incomplete information (decide with 70% of the data)
- Cycling too fast may result in action without sufficient analysis
- Team OODA is slower than individual OODA — communication overhead

## Suitable Scenarios

Incident response, real-time decision-making, competitive strategy, agile operations, on-call response, crisis management

## References

- Boyd, John (1976) "Destruction and Creation" (original OODA loop paper)
- Richards, Chet (2004) "Certain to Win: The Strategy of John Boyd, Applied to Business"
