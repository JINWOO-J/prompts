---
tags:
- techniques
- cot
- reasoning
- step-by-step
---
# Chain-of-Thought (CoT) — Step-by-Step Reasoning

## Concept

A technique for solving complex problems by explicitly working through intermediate reasoning steps.
Even a single sentence — "Let's think step by step" — can significantly improve LLM reasoning accuracy.
Proposed by Wei et al. (2022), it is one of the most fundamental and powerful prompt engineering techniques.

## Key Principles

- Mimics human thought processes: Breaking complex problems into intermediate steps reduces errors
- Working memory aid: The LLM "records" intermediate results as text, reducing context loss
- Zero-shot CoT ("Let's think step by step") alone improved accuracy on the GSM8K math benchmark from 17.7% to 78.7%
- Few-shot CoT (with examples) achieves even higher accuracy, especially effective for arithmetic and commonsense reasoning

## Prompt Template

```
Please solve the following problem by thinking through it step by step.

**Problem:** [Problem description]

**Solution Process:**
Step 1: [First reasoning — identify the core elements of the problem]
Step 2: [Second reasoning — organize relevant information]
Step 3: [Third reasoning — make logical connections]
...
Final Answer: [Conclusion]

At each step, explicitly state the rationale behind your judgment.
```

## Practical Example

**Scenario: Analyzing the cause of K8s Pod OOMKilled**

> "A Pod is repeatedly restarting with OOMKilled. Analyze the cause step by step."

Step 1: OOMKilled means the container exceeded its memory limit
Step 2: Check the last termination status with `kubectl describe pod` → exitCode: 137
Step 3: The container memory limit is 256Mi, but actual usage grew to 300Mi
Step 4: The application heap setting (-Xmx) is set to 512m, which exceeds the limit
Step 5: JVM heap + metaspace + native memory exceeds the limit
→ Conclusion: Lower JVM -Xmx to 200m or increase the Pod memory limit to 512Mi

## Variations and Combinations

- **CoT + Self-Consistency**: Generate multiple CoT paths and select the final answer by majority vote
- **CoT + Few-Shot**: Include reasoning processes in examples to guide pattern learning
- **CoT + Role Prompting**: "As a senior SRE, analyze step by step"
- **CoT + CoVe**: Self-verify each step after reasoning

## Caveats

- Unnecessary overhead for simple factual questions (e.g., "What is the capital of France?")
- Errors can accumulate as reasoning chains grow longer (error propagation)
- LLMs may produce plausible-sounding reasoning that is actually incorrect (faithful reasoning problem)
- Higher token consumption means cost/speed tradeoffs to consider

## Suitable Scenarios

Math/logic problems, code debugging, incident root cause analysis, complex decision-making, multi-step analysis, technical interview problem-solving

## References

- Wei et al. (2022) "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models"
- Kojima et al. (2022) "Large Language Models are Zero-Shot Reasoners" (Zero-shot CoT)
