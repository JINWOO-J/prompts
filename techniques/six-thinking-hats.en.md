---
tags:
- techniques
- six-hats
- de-bono
- perspectives
- parallel-thinking
---
# Six Thinking Hats — Six-Color Parallel Thinking

## Concept

Proposed by Edward de Bono (1985). Six colored hats each represent a different mode of thinking.
A technique for parallel thinking by focusing on only one perspective at a time.
When all meeting participants wear the same hat and think in the same direction,
multi-angle analysis becomes possible without conflict. An alternative to traditional adversarial debate.

## Key Principles

- Parallel thinking: All participants think in the same direction simultaneously → reduces confrontation
- Complete coverage: Going through all 6 perspectives prevents blind spots
- Legitimizing emotion: The Red Hat formally addresses intuition and feelings
- Time efficiency: Setting time limits per hat shortens meeting duration
- The 6 hats: White (facts), Red (emotions), Black (criticism), Yellow (optimism), Green (creativity), Blue (process)

## Prompt Template

```
**Topic:** [Topic to analyze]

**🤍 White Hat (Facts and Data):**
"Let's look at the objective facts only."
- Known facts: [...]
- Data needed but unavailable: [...]
- Numbers/statistics: [...]
- Sources and reliability: [...]

**🔴 Red Hat (Emotions and Intuition):**
"Share your feelings honestly. No justification needed."
- First impression/gut feeling: [...]
- Concerns: [...]
- Excitement: [...]
- Overall team sentiment: [...]

**⚫ Black Hat (Criticism and Risk):**
"Let's look at what could go wrong."
- Risk factors: [...]
- Likelihood of failure: [...]
- Weaknesses and flaws: [...]
- Causes of failure in similar past cases: [...]

**🟡 Yellow Hat (Optimism and Value):**
"Let's look at the value and benefits."
- Advantages and benefits: [...]
- Opportunities: [...]
- Best-case scenario: [...]
- Long-term value: [...]

**🟢 Green Hat (Creativity and Alternatives):**
"Let's freely generate new ideas."
- New ideas: [...]
- Alternative approaches: [...]
- Variations on existing methods: [...]
- "What if...?" scenarios: [...]

**🔵 Blue Hat (Summary and Process):**
"Let's organize the discussion so far."
- Key points from each hat: [...]
- Points of agreement: [...]
- Unresolved issues: [...]
- Next steps and action items: [...]
```

## Practical Example

**Scenario: "Should we adopt Kubernetes?"**

White: Current traffic 1M requests/month, 5 servers, deployments twice a week, 1 incident/month
Red: Team is excited about K8s but anxious about operational burden
Black: 6-month learning curve, 3x increase in operational complexity, may be overkill for a small team
Yellow: Auto-scaling, self-healing, deployment automation improve long-term operational efficiency
Green: ECS Fargate instead of K8s? Or managed K8s (EKS)?
Blue: Conclusion — Start with managed K8s (EKS), decide on full adoption after a 3-month pilot

## Variations and Combinations

- **Six Hats + SWOT**: Map Yellow/Black to SWOT's S/W/O/T
- **Six Hats + Devil's Advocate**: Strengthen the Black Hat with Devil's Advocate
- **Six Hats + Role**: Assign each hat to a different expert persona
- **Six Hats + Time-boxing**: 5-minute limit per hat for efficient meetings

## Caveats

- Hat order can influence results (Blue → White → Red → Black → Yellow → Green → Blue recommended)
- Effectiveness is limited in cultures uncomfortable with the Red Hat (emotions)
- Switching perspectives for each hat can be difficult when used solo
- Spending too much time on the Black Hat can create a negative atmosphere

## Suitable Scenarios

Team decision-making, project evaluation, strategy formulation, brainstorming, meeting facilitation

## References

- de Bono, Edward (1985) "Six Thinking Hats"
- de Bono, Edward (1992) "Serious Creativity"
