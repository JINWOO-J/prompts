---
tags:
- techniques
- few-shot
- examples
- in-context-learning
---
# Few-Shot Prompting — Example-Based Learning

## Concept

A technique that includes 2–5 input-output examples in the prompt so the LLM can learn the pattern.
Systematized by Brown et al. (2020, GPT-3 paper). The core of In-Context Learning (ICL).
Enables the model to perform new tasks using only examples, without fine-tuning.

## Key Principles

- Pattern recognition: The LLM infers input-output mapping rules from the examples
- Format consistency: Showing the desired output format through examples produces consistently formatted responses
- Example selection is critical: Relevant and diverse examples drive performance
- Example order matters: The model tends to follow patterns closer to the last example (recency bias)

## Prompt Template

```
Refer to the following examples and respond in the same format.

**Example 1:**
Input: [Input 1]
Output: [Output 1]

**Example 2:**
Input: [Input 2]
Output: [Output 2]

**Example 3:**
Input: [Input 3]
Output: [Output 3]

---
**Actual Input:**
Input: [Actual input]
Output:
```

## Practical Example

**Scenario: Error log → Cause classification**

Example 1:
Input: "java.lang.OutOfMemoryError: Java heap space"
Output: Category: Memory | Severity: Critical | Action: Increase JVM heap size or check for memory leaks

Example 2:
Input: "Connection refused: connect to [db-host]:5432"
Output: Category: Network | Severity: High | Action: Check DB server status and firewall rules

Actual input: "disk usage exceeded 95% on /var/log"
→ LLM output: Category: Storage | Severity: High | Action: Configure log rotation and clean up old logs

## Variations and Combinations

- **Few-Shot + CoT**: Include reasoning processes in examples (Few-Shot CoT)
- **Few-Shot + Role**: Set a role first, then provide examples
- **Few-Shot + Self-Consistency**: Generate multiple paths based on examples

## Caveats

- Biased examples produce biased outputs (diverse examples are essential)
- Too many examples consume the context window (2–5 is optimal)
- Effectiveness drops when examples and actual input are from different domains
- Results can vary depending on example order (experiment with ordering)

## Suitable Scenarios

Output format standardization, classification tasks, transformation tasks, maintaining consistent style, defining new tasks

## References

- Brown et al. (2020) "Language Models are Few-Shot Learners" (GPT-3)
- Liu et al. (2022) "What Makes Good In-Context Examples for GPT-3?"
