---
category: coding
type: concept
tags:
- readability
- cognitive-load
- clean-code
role: Developer
origin: custom
source: ''
---
# 인지 가독성 우선 코딩 — Cognitive Readability First

> Coding principles that optimize for human understanding, not rule compliance.

---

## Key Principles

- Keep the number of simultaneously tracked concepts in a function/block to 3–4 or fewer
- Aim for code that is read by pattern recognition (System 1), not step-by-step analysis (System 2)
- Names and structure must make the next behavior predictable
- The problem's own complexity is acceptable. Complexity caused by representation is not
- If understanding requires jumping across functions/files more than twice, reconsider the split
- Maintain linear flow with guard clauses and early returns
- Side effects (DB, network, events, cache) must be visible in names or structure
- Do not hide decision logic behind globals or environment flags
- Do not mechanically split functions, extract tiny one-off helpers, or refactor solely to reduce metrics

## Details

### 10 Practical Rules

**1. Minimize Active Context**
- Split when the flow is not obvious at a glance
- Split when logic can be tested or reused independently
- Keep very small (≈3 lines) simple logic inline
- Do not mechanically split just because "4 contexts are exceeded"

**2. Guard Against Jump Cost**
- If understanding requires jumping across functions/files more than twice, reconsider the split
- If behavior cannot be predicted from the call site, reconsider
- Split only when context reduction outweighs navigation cost

**3. Prefer Idiomatic Patterns**
- Follow language, framework, and team conventions
- Avoid clever tricks, double negatives, and unnecessary abstractions

**4. Keep a Linear Flow**
- Prefer guard clauses and early returns
- Main logic should read top-to-bottom

**5. Name = Behavior**
- A name must match what the code actually does
- Side effects (DB, network, events, cache, etc.) must be visible in names or structure

**6. Visual Structure**
- Group related logic with blank lines
- Keep similar responsibilities in similar shapes

**7. Locality**
- Core flow should be readable in a single file, preferably a single screen
- Place helpers close to their usage

**8. Symmetry**
- Keep paired operations (parse/serialize, encode/decode, CRUD, etc.) symmetric in naming, signatures, and error handling

**9. No Hidden Policies**
- Do not hide decision logic behind globals, environment flags, or singletons
- Expose policies through parameters or explicit policy objects

**10. Make Exceptions Structural**
- Important exception rules should be expressed through types, result objects, or dedicated functions — comments alone are not enough

### Do Not

- Mechanically split functions
- Extract tiny one-off helpers
- Break existing team conventions
- Refactor solely to reduce metrics

## References

