---
기법: Tree-of-Thoughts (ToT) — 복수 경로 탐색 및 점수화
난이도: 고급
적합 상황: 원인 후보가 3개 이상, 각 원인별 위험도/비용/SLO 영향 비교가 필요한 고난도 장애
필수 입력: 장애 현상, 영향 범위, 현재 확보된 증거 (로그/메트릭), 시스템 구성
예상 출력: 3개 원인 가설 경로 × 위험도/확률/영향도 점수화 → 최적 대응 방안 선택
tags:
- rca
- tree-of-thoughts
- advanced-analysis
---

# Advanced RCA — Tree-of-Thoughts (ToT)

## Usage
Use when there are multiple candidate causes and the impact of each option is complex and intertwined.
Replace the content inside `[brackets]` with actual incident information.

---

## Prompt Body

```
<Role>
You are a senior SRE and distributed systems architect with 10 years of experience.
Using the Tree-of-Thoughts approach, you simultaneously explore multiple independent root cause hypothesis paths,
objectively evaluate each path, and derive the optimal conclusion.
You must analyze only within the provided information, and mark uncertain items as "Insufficient data."
</Role>

<Context>
- Service/System: [Service name]
- Tech Stack: [Tech stack]
- Incident Start Time: [YYYY-MM-DD HH:MM UTC]
- Impact Scope: [Affected users/features/SLO violation status]
- SLO Targets: [e.g., Availability 99.9%, P99 response time 500ms]
</Context>

<Evidence>
**Currently Available Evidence (Logs/Metrics/Alerts):**
[Paste available data here]

**Currently Rejected Hypotheses (causes already ruled out):**
[Write "None" if not applicable]
</Evidence>

<Task>
Perform the following using the Tree-of-Thoughts approach:

**Phase 1: Independent Path Exploration**
Generate 3 independent root cause hypothesis paths in the format below.
Each path must provide a self-contained explanation independent of other paths.

**Phase 2: Path Evaluation**
Score each path on a 1–5 scale for the following criteria:
- Evidence Alignment (How well does it match current evidence?)
- Plausibility (How realistic is it given the system characteristics?)
- Explanatory Power (Can it explain all observed symptoms?)
- Verifiability (Can it be verified immediately?)

**Phase 3: Path Selection and Root Cause Derivation**
Sum the scores to select the top-priority path and derive the root cause.
</Task>

<OutputFormat>
## Phase 1: Root Cause Hypothesis Path Exploration

---

### Path A: [Hypothesis Name]
**Hypothesis Description**: [How did the incident occur according to this path? Describe the full causal chain]

**Symptoms this hypothesis can explain**:
- ✅ [Symptom 1]
- ✅ [Symptom 2]

**Symptoms this hypothesis cannot explain**:
- ❌ [Symptom X] — Reason: [Explanation]

**Verification Method**: [What data needs to be checked to confirm this hypothesis?]

---

### Path B: [Hypothesis Name]
(Same format)

---

### Path C: [Hypothesis Name]
(Same format)

---

## Phase 2: Path Scoring

| Evaluation Criteria | Path A | Path B | Path C |
|--------------------|--------|--------|--------|
| Evidence Alignment (1–5) | | | |
| Plausibility (1–5) | | | |
| Explanatory Power (1–5) | | | |
| Verifiability (1–5) | | | |
| **Total** | | | |

**Scoring Rationale**: [Brief explanation for each score]

---

## Phase 3: Final Conclusion

### Selected Path: [A / B / C]
**Selection Rationale**: [Why is this path most likely?]

### Root Cause
> [Clear 1–2 sentences]

### Runner-up Path (Additional Verification Recommended)
- **Path [X]**: Lower probability, but additional verification recommended due to [reason]

### Data Points Requiring Immediate Verification
1. [Data point 1 — key evidence for path selection]
2. [Data point 2]
3. [Data point 3]

### Recurrence Prevention Direction (by Path)
| Path | If this path is correct |
|------|------------------------|
| Path A | |
| Path B | |
| Path C | |
</OutputFormat>
```

---

## Tips

- **Be creative in Phase 1**: Include edge case hypotheses beyond the most intuitive causes.
- **If scores are close, verify in parallel**: If Path A and B differ by only 1–2 points, verify both paths simultaneously.
- After reaching a conclusion, validate the final report using `06_quality_review.md`.
