---
tags:
- techniques
- red-team
- blue-team
- security
- adversarial
---
# Red Team / Blue Team — Adversarial Analysis

## Concept

A technique that adopts both Red Team (attacker) and Blue Team (defender) perspectives
to find system vulnerabilities and develop defense strategies.
Originated in military/security domains. Now widely used for AI safety evaluation as well.

## Key Principles

- Adversarial thinking: Taking the attacker's perspective reveals vulnerabilities that defenders miss
- Balanced analysis: Considering both offense and defense leads to realistic countermeasures
- Naturally integrates with the MITRE ATT&CK framework
- Can be extended to Purple Team (offense + defense collaboration)

## Prompt Template

```
**Target system:** [System/service description]

**🔴 Red Team (Attacker perspective):**

**Attack vector 1:** [Attack method]
- Prerequisites: [What the attack requires]
- Attack path: [Step-by-step attack scenario]
- Difficulty: [High/Med/Low] | Impact: [High/Med/Low]
- MITRE ATT&CK: [Technique ID, if applicable]

**Attack vector 2:** [Attack method]
- Prerequisites: [...]
- Attack path: [...]
- Difficulty: [...] | Impact: [...]

**Attack vector 3:** [Attack method]
- [...]

**🔵 Blue Team (Defender perspective):**

| Attack vector | Current defense level | Detection capability | Improvement plan | Priority |
|---------------|----------------------|---------------------|-----------------|----------|
| 1 | [None/Partial/Full] | [High/Med/Low] | [...] | [P1/P2/P3] |
| 2 | [...] | [...] | [...] | [...] |
| 3 | [...] | [...] | [...] | [...] |

**🟣 Purple Team (Combined):**
- Most dangerous attack path: [...]
- Immediate action required: [...]
- Mid-term improvement plan: [...]
- Defense roadmap: [Prioritized execution plan]
```

## Practical Example

**Scenario: "Kubernetes cluster security assessment"**

Red Team:
1. Exposed API server → Attempt kubectl access without authentication (Difficulty: Low, Impact: High)
2. Container escape → Access host from privileged container (Difficulty: Med, Impact: High)
3. RBAC bypass → Exploit overly permissive ServiceAccount (Difficulty: Med, Impact: Med)

Blue Team:
1. API server → Apply Network Policy + OIDC authentication (P1)
2. Container → Enforce PodSecurityPolicy/Standards, prohibit privileged mode (P1)
3. RBAC → Apply least-privilege principle, conduct regular audits (P2)

## Variations and Combinations

- **Red/Blue + STRIDE**: Combine with the STRIDE threat modeling framework
- **Red/Blue + OODA**: Apply OODA loop to both attack and defense
- **Red/Blue + Pre-mortem**: Analyze successful attack scenarios using Pre-mortem

## Caveats

- "Imagining" attacks without actual simulation has limitations
- Attacker motivation and capabilities must be realistically assumed
- Defense cost-effectiveness must be considered (not every attack can be blocked)
- Insider threats require separate consideration

## Suitable Scenarios

Security audits, system reviews, failure scenario analysis, threat modeling, AI safety evaluation

## References

- MITRE ATT&CK Framework (https://attack.mitre.org/)
- Brumley et al. (2014) "Red Team vs Blue Team" (from military strategy to cybersecurity)
