---
tags:
- techniques
- rubber-duck
- debugging
- explanation
- verbalization
---
# Rubber Duck Debugging — Explain-to-Debug Technique

## Concept

A debugging technique where explaining a problem line by line to a rubber duck
(or any other object) leads you to discover the issue yourself.
Popularized by "The Pragmatic Programmer" (1999).
The act of explaining itself organizes thinking and exposes implicit assumptions.

## Key Principles

- Verbalization effect: Expressing thoughts in words reveals logical gaps
- Forcing slow thinking: Explaining code line by line activates System 2 thinking instead of "skimming"
- Assumption exposure: Attempting to explain what you took for granted reveals hidden assumptions
- Zero cost: Can be done immediately, alone, without any tools or other people

## Prompt Template

```
Find the problem in the following code/system using rubber duck debugging.

**Problem:** [Bug/issue description]
**Expected behavior:** [How it should work]
**Actual behavior:** [How it actually works]

**Explaining line by line:**

"The purpose of this code is [purpose]."

"First, it does [step 1]..."
- Input: [Expected input]
- Processing: [What it does]
- Output: [Expected output]
→ Is this correct so far? [Verification]

"Then in [step 2]..."
- Input: [Output from previous step]
- Processing: [What it does]
- Output: [Expected output]
→ Wait, I have a question about [concern]...

"Ah, [discovered problem] was the cause!"

**Problem found:** [Specific problem]
**Why it was missed:** [Which assumption was wrong]
**Fix:** [Solution]
```

## Practical Example

**Scenario: "User list API returns an empty array"**

"This API queries users from the DB and returns them."
"First, it parses page and limit from query parameters... defaults are page=1, limit=20."
"Then it builds the SQL query... OFFSET = (page-1) * limit = 0, LIMIT = 20."
"Wait, it stores the query result in a variable... rows = cursor.fetchall()..."
"Ah, cursor.execute() was never called before fetchall()!"
→ A commit() slipped in between execute() and fetchall(), resetting the cursor

## Variations and Combinations

- **Rubber Duck + Feynman**: Explain as if to an elementary school student — even simpler
- **Rubber Duck + CoT**: Structure the explanation process as step-by-step reasoning
- **Rubber Duck + Pair Programming**: Explain to an actual colleague (most effective)

## Caveats

- Limited effectiveness when the problem lies in environment/configuration rather than code logic
- In very large codebases, deciding where to start explaining can be difficult
- If you already know the code well, the "explanation" becomes perfunctory and less effective
- Concurrency/async bugs may be hard to reproduce through sequential explanation

## Suitable Scenarios

Code debugging, finding logic errors, understanding complex code, code review, onboarding

## References

- Hunt & Thomas (1999) "The Pragmatic Programmer" (popularized rubber duck debugging)
- Begel & Simon (2008) "Novice Software Developers, All Over Again" (research on verbalization effects)
