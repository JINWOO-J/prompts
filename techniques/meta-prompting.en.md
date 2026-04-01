---
tags:
- techniques
- meta
- prompt-generation
- self-improving
---
# Meta-Prompting — Prompts that Generate Prompts

## Concept

A technique that asks an LLM to generate or improve prompts themselves.
Automation of prompt engineering — the LLM designs better prompts on its own.
Systematized in Suzgun & Kalai (2024) "Meta-Prompting" paper.

## Key Principles

- Automated prompt optimization: The LLM searches for optimal prompts instead of manual trial and error
- No expert knowledge required: Good prompts can be generated without prompt engineering experience
- Iterative improvement: A loop of testing generated prompts and refining them with feedback
- Domain adaptation: Automatically generate prompts tailored to specific domains

## Prompt Template

```
You are a prompt engineering expert.

**Goal:** [What you want to achieve]
**Target LLM:** [Model to use — GPT-4, Claude, etc.]
**Input data:** [Type of data that will go into the prompt]
**Output requirements:** [Desired output format, length, tone]
**Constraints:** [Elements that must be included/excluded]

Write an optimal prompt to achieve the above goal.

Elements to include in the prompt:
1. Clear role definition (Role)
2. Specific instructions (Task)
3. Output format specification (Format)
4. Examples (Few-Shot, if needed)
5. Constraints
6. Explanation of techniques used

---
**Generated Prompt:**
[Write the prompt here]

**Design Rationale:**
- Techniques used: [CoT, Role, Few-Shot, etc.]
- Why this structure was chosen: [...]
- Expected effectiveness: [...]
- Areas for improvement: [...]
```

## Practical Example

**Scenario: "Create a code review prompt for me"**

Goal: A prompt that reviews PR code to find bugs, performance, and security issues
Target: Claude Sonnet
Output: Issue list (severity, location, description, fix suggestion)

→ Generated prompt includes Role (senior reviewer) + checklist (OWASP Top 10) +
output format (table) + Few-Shot (good review examples)

## Variations and Combinations

- **Meta + Self-Refinement**: Self-critique the generated prompt, then improve it
- **Meta + A/B Testing**: Generate multiple prompts and run comparison tests
- **Meta + Domain Expert**: Incorporate domain expert feedback and regenerate

## Caveats

- Generated prompts are not always optimal — manual review is necessary
- The quality of the meta-prompt itself determines the results
- May generate overly complex prompts (explicit simplification instructions needed)
- A prompt optimized for one model may be inefficient on another

## Suitable Scenarios

Prompt optimization, repetitive task automation, prompt template creation, domain-specific prompt design

## References

- Suzgun & Kalai (2024) "Meta-Prompting: Enhancing Language Models with Task-Agnostic Scaffolding"
- Zhou et al. (2022) "Large Language Models Are Human-Level Prompt Engineers" (APE)
