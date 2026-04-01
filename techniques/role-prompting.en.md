---
tags:
- techniques
- role
- persona
- expert
- character
---
# Role Prompting — Persona Assignment Technique

## Concept

A technique that assigns a specific expert role to an LLM so it responds from that perspective.
The role activates relevant domain knowledge, tone, and viewpoint, improving response quality.
The most fundamental use of system prompts and the starting point for nearly every prompt.

## Key Principles

- Knowledge activation: Assigning a specific role prioritizes related knowledge
- Perspective anchoring: Consistent viewpoint reduces context-switching cost
- Tone/style control: Adjustable from expert-level to beginner-friendly explanations
- Specificity is key: "A 10-year K8s-specialized SRE" is far more effective than just "an engineer"

## Prompt Template

```
You are [role/expert description].

**Specialization:** [Specific domain of expertise]
**Experience:** [Experience level and key background]
**Perspective:** [From which viewpoint to answer]
**Communication style:** [Technical/non-technical, detailed/concise]

Answer the following question from this role's perspective:

[Question]

Include the following in your response:
- Rationale behind your expert judgment
- Advice grounded in practical experience
- Caveats and risks
- Additional items to verify
```

## Practical Example

**Scenario: Security audit**

"You are a cloud security architect with 15 years of experience. From the perspective of
reporting to the CISO, assess the security vulnerabilities of this AWS infrastructure."

→ Because the role is specific: the response comes in CISO report format, with risk matrix,
compliance perspective, and business-impact focus

vs "Assess as a security expert" → generic, technically-focused response

## Variations and Combinations

- **Role + CoT**: "As a senior SRE, analyze step by step"
- **Role + Six Hats**: Assign a different role to each hat
- **Role + Devil's Advocate**: "As a security auditor, raise objections"
- **Multi-Role**: Format where multiple roles debate

## Caveats

- Overly specific roles may narrow the response scope
- The LLM may "act" the role and produce factually incorrect answers (over-immersion)
- Residual perspective from a previous role may carry over during role switches
- Sensitive roles (doctor, lawyer) require disclaimers

## Suitable Scenarios

Domain expert consultation, code review, security audits, gathering diverse perspectives, adjusting document tone

## References

- Shanahan et al. (2023) "Role-Play with Large Language Models"
- Zheng et al. (2023) "Is ChatGPT a Good NLG Evaluator?" (impact of roles on evaluation quality)
