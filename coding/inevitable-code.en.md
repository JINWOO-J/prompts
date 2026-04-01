---
category: coding
type: concept
tags:
- typescript
- simplicity
- design
role: Developer
origin: custom
source: 'https://github.com/giselles-ai/giselle/blob/main/.claude/agents/ts-coder.md'
---
# 필연적 코드 철학 — Inevitable Code Philosophy

> A philosophy of writing code where every design choice feels like the only reasonable option.

---

## Key Principles

- Hide internal complexity behind simple interfaces — the goal is to eliminate external cognitive load
- Reduce API choices forced on the user — leverage JavaScript's natural patterns
- Choose names and patterns that leverage existing mental models — recognition, not recall
- Prefer functions over classes, composition over inheritance
- Use TypeScript's type system to prevent mistakes, but don't create unnecessary ceremony
- Eliminate over-abstraction, configuration explosion, premature generalization, and unnecessary service layers
- Before shipping code, ask yourself: Is it as simple as possible? Does it feel natural? Does it solve a real problem?

## Details

The coding philosophy followed by the Giselle AI team's ts-coder agent.
The goal is to make developers feel "Of course it should be this way. What other way could there be?" when they encounter the code.

### Core Principle: Surface Simplicity, Internal Sophistication

Simple interfaces can hide sophisticated implementations.
Willingly accept internal complexity to eliminate external cognitive load.

```typescript
// Inevitable: direct and obvious
const user = await getUser(id);
if (!user) return null;

// Over-engineered: unnecessary abstraction layer
const userService = createUserService(dependencies);
const result = await userService.getUser(id);
if (!result.success) handleError(result.error);
```

### Design Principles

**1. Minimize Decision Points**
Every API choice forced on the user creates cognitive load.
Leverage JavaScript's natural patterns to reduce decisions.

**2. Hide Complexity Behind Purpose**
Internal complexity is acceptable — when it eliminates complexity elsewhere.
Concentrate complexity in one place to simplify everything else.

**3. Design for Recognition, Not Recall**
Choose patterns and names that leverage existing mental models.
Code should be recognizable for what it does without memorizing arbitrary rules.

**4. Functions Over Classes, Composition Over Inheritance**
Classes introduce accidental complexity through state management, lifecycle, and inheritance hierarchies.
Functions compose naturally.

**5. Make Errors Impossible, Not Detectable**
Use TypeScript's type system to prevent obvious mistakes, but don't create ceremony.

### Anti-Pattern Removal Checklist

- **Over-abstraction**: Creating complex patterns when a simple function would suffice
- **Configuration explosion**: Pushing decisions onto users that could be resolved with good defaults
- **Type ceremony**: Using complex types when simple types communicate sufficiently
- **Premature generalization**: Building abstractions before knowing what's needed
- **Service layers**: Adding indirection that doesn't solve a real problem

### Litmus Test

Before shipping code, ask yourself:
1. Is this as simple as possible?
2. Does it feel natural?
3. Does it solve a real problem?
4. What happens when it breaks?

## References

- [giselles-ai/giselle ts-coder agent](https://github.com/giselles-ai/giselle/blob/main/.claude/agents/ts-coder.md)
