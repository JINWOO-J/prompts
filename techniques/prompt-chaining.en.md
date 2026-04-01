---
tags:
- techniques
- chaining
- pipeline
- sequential
- workflow
---
# Prompt Chaining — Sequential Prompt Linking

## Concept

A technique that breaks complex tasks into multiple prompt stages,
connecting the output of one stage as the input to the next.
Each stage becomes simpler, improving accuracy and enabling intermediate result verification.
A core concept in frameworks like LangChain and Semantic Kernel.

## Key Principles

- Distributed complexity: Multiple small prompts are more accurate than one massive prompt
- Intermediate verification: Outputs at each stage can be reviewed and corrected as needed
- Reusability: Each chain can be independently tested and reused
- Easier debugging: Pinpoint exactly which stage caused the problem

## Prompt Template

```
**Overall task:** [Complex task description]

**Chain 1 — [Stage name] (e.g., Information Gathering):**
Input: [Raw data/question]
Instructions: [What to do in this stage]
Output format: [Structured format usable by the next stage]
→ Output: [Result]

**Chain 2 — [Stage name] (e.g., Analysis):**
Input: Output from Chain 1
Instructions: [What to do in this stage]
Output format: [Structured format]
→ Output: [Result]

**Chain 3 — [Stage name] (e.g., Conclusion):**
Input: Output from Chain 2
Instructions: [Final processing]
→ Final output: [Result]

**Verification:** Does the final output meet the original task requirements?
```

## Practical Example

**Scenario: Automated incident report generation**

Chain 1 (Log parsing): Raw logs → Structured event timeline
Chain 2 (Root cause analysis): Timeline → 5-Whys analysis → Root cause
Chain 3 (Impact assessment): Root cause → Blast radius, SLA violation status
Chain 4 (Report generation): Analysis results → Executive incident report

Since each stage is independent, you can swap out just Chain 2 to apply a different analysis technique

## Variations and Combinations

- **Chaining + CoT**: Apply CoT within each chain
- **Chaining + Gate**: Add conditional branching mid-chain (if-else chains)
- **Chaining + Parallel**: Run independent chains in parallel, then merge
- **Chaining + Human-in-the-Loop**: Human verification at intermediate stages

## Caveats

- Longer chains risk error propagation (upstream errors cascade downstream)
- Interfaces (output formats) between stages must be clearly defined
- Overall latency increases proportionally with the number of chains
- Error handling is needed when intermediate outputs differ from expectations

## Suitable Scenarios

Complex analysis, document generation, data transformation pipelines, multi-step workflows, automation

## References

- Wu et al. (2022) "AI Chains: Transparent and Controllable Human-AI Interaction by Chaining LLM Steps"
- LangChain, Semantic Kernel framework documentation
