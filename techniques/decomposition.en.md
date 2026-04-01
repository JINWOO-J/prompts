---
tags:
- techniques
- decomposition
- divide-conquer
- breakdown
- modular
---
# Decomposition — Problem Decomposition Technique

## Concept

A technique for breaking down complex problems into smaller, manageable sub-problems.
A generalization of Divide and Conquer.
Each sub-problem is solved independently, then the solutions are combined.
A fundamental problem-solving principle systematized in Polya's (1945) "How to Solve It."

## Key Principles

- Reduced cognitive load: Focus on one small problem at a time
- Parallelization: Independent sub-problems can be solved simultaneously
- Reusability: Sub-problem solutions can be reused elsewhere
- Easier testing: Smaller units are easier to test
- Progress tracking: Overall progress can be gauged by sub-problem completion rate

## Prompt Template

```
**Complex Problem:** [Full problem description]

**Decomposition Strategy:** [Criteria for decomposition — by function, layer, chronological order, etc.]

**Decomposition Tree:**
```
[Full Problem]
├── [Sub-problem 1] — [Difficulty: High/Med/Low] [Dependency: None/Depends on 2]
│   ├── [Detail 1-1]
│   └── [Detail 1-2]
├── [Sub-problem 2] — [Difficulty] [Dependency]
│   ├── [Detail 2-1]
│   └── [Detail 2-2]
└── [Sub-problem 3] — [Difficulty] [Dependency]
    └── [Detail 3-1]
```

**Dependency Graph:**
[Which sub-problems depend on others]

**Resolution Order (based on dependencies + priority):**
1. [Sub-problem X] → Verify: [Completion criteria]
2. [Sub-problem Y] → Verify: [Completion criteria]
3. [Sub-problem Z] → Verify: [Completion criteria]

**Combination:** [How to merge the sub-solutions]
**Integration Verification:** [How to confirm the full problem is solved]
```

## Practical Example

**Scenario: "Introducing an API Gateway to a legacy monolith"**

Decomposition:
├── 1. Create an inventory of current API endpoints (Dependency: None)
├── 2. Decide on authentication/authorization integration approach (Dependency: 1)
├── 3. Design routing rules (Dependency: 1)
├── 4. Establish rate limiting policies (Dependency: 1)
├── 5. Build gateway infrastructure (Dependency: 2, 3, 4)
└── 6. Incremental migration (Dependency: 5)

Resolution order: 1 → 2, 3, 4 (parallel) → 5 → 6

## Variations and Combinations

- **Decomposition + MECE**: Classify sub-problems using MECE to prevent gaps and overlaps
- **Decomposition + CoT**: Solve each sub-problem using CoT
- **Decomposition + Estimation**: Estimate time/cost for each sub-problem
- **Decomposition + Delegation**: Distribute sub-problems across team members

## Caveats

- Poor decomposition criteria lead to complex inter-dependencies between sub-problems
- Over-decomposition increases overhead (combination cost)
- Interfaces between sub-problems must be clearly defined
- Risk of losing sight of the whole while focusing on parts (forest vs trees)

## Suitable Scenarios

Large-scale project planning, complex bug analysis, system design, task distribution, estimation

## References

- Polya, George (1945) "How to Solve It" (a classic on problem decomposition)
- Cormen et al. "Introduction to Algorithms" (divide and conquer algorithms)
