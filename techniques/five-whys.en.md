---
tags:
- techniques
- five-whys
- root-cause
- rca
- toyota
---
# 5 Whys — Asking "Why?" Five Times

## Concept

A technique for reaching the root cause by repeatedly asking "Why?" about the surface-level cause of a problem. Developed by Taiichi Ohno, the creator of the Toyota Production System (TPS). Typically, five iterations are enough to reach the root cause, though it may take three or seven.

## Key Principles

- Simplicity: No special tools needed — just keep asking "Why?"
- Causal chain tracing: Follow the chain of causation from surface symptoms to root cause
- Preventing premature stops: Continuing to ask "Why?" avoids stopping at superficial causes
- Reaching actionable causes: The root cause must be at a level where action can be taken

## Prompt Template

```
**Problem:** [Observed problem/symptom]

**Why 1:** Why did [problem] occur?
→ Cause 1: [Direct cause]

**Why 2:** Why did [Cause 1] occur?
→ Cause 2: [One level deeper]

**Why 3:** Why did [Cause 2] occur?
→ Cause 3: [Deeper cause]

**Why 4:** Why did [Cause 3] occur?
→ Cause 4: [Structural/process cause]

**Why 5:** Why did [Cause 4] occur?
→ Root Cause: [Actionable root cause]

**Validation:** Would fixing the root cause resolve the original problem? [Yes/No]
**Backtrace:** Root Cause → ... → Original Problem (Is the causal chain logical?)

**Countermeasures:**
- Immediate action: [Fix the root cause]
- Recurrence prevention: [Process/system improvement]
- Monitoring: [How to detect recurrence]
```

## Practical Example

**Scenario: "Spike in 500 errors after production deployment"**

Why 1: Why did 500 errors occur? → NullPointerException in the new API endpoint
Why 2: Why did the NPE occur? → Null return from user profile lookup was not handled
Why 3: Why was null handling missing? → Not caught during code review
Why 4: Why was it missed in code review? → No null safety checklist exists
Why 5: Why is there no checklist? → No standard guidelines for the code review process

Root cause: Lack of code review guidelines
Countermeasures: Create a code review checklist including null safety + add lint rules

## Variations and Combinations

- **5 Whys + Fishbone**: When multiple causes emerge at each Why, classify them with Fishbone
- **5 Whys + CoT**: Use CoT for detailed reasoning at each Why step
- **5 Whys + Hypothesis**: Form and validate hypotheses at each step
- **5 Whys + MECE**: Classify possible causes at each step using MECE

## Caveats

- Tracks only a single causal chain — may miss compound causes (supplement with Fishbone)
- When a "Why?" has multiple answers, judgment is needed on which to follow
- Five iterations aren't always the right number — three may suffice, or seven may be needed
- Focus on system/process causes, not blame

## Suitable Scenarios

Incident analysis (RCA), bug root cause tracing, process improvement, quality management, postmortems

## References

- Ohno, Taiichi (1988) "Toyota Production System: Beyond Large-Scale Production"
- Serrat (2017) "The Five Whys Technique" (Asian Development Bank)
