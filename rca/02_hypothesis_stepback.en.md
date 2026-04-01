---
기법: Step-back 프롬프팅 + 가설 검증 (Hypothesis Testing)
난이도: 중급
적합 상황: 원인이 불명확한 장애, 데이터 부족, 초기 원인 범주 좁히기
필수 입력: 장애 현상 요약, 발생 시각, 시스템 구성, 관찰된 증상 목록
예상 출력: 상위 원인 패턴 분석, 2~3개 가설 + 각 가설 검증에 필요한 데이터 목록
tags:
- 02_hypothesis_stepback
- ecs
- rca
- rds
- redis
---

# Hypothesis Building + Step-back Analysis

## Usage
Replace the content inside `[brackets]` with actual incident information.
Use this **when 01_basic_rca.md analysis yields unclear results**, or **when you need to establish direction in the early stages**.

---

## Prompt Body (Step 1: Step-back)

```
<Role>
You are a senior SRE and distributed systems expert with 10 years of experience.
You take a Step-back approach, first identifying the higher-level context and common patterns before diving into detailed log analysis.
</Role>

<Context>
- Service/System: [Service name or system name]
- Tech Stack: [e.g., MSA on AWS, Redis + RDS + ECS]
- Incident Start Time: [YYYY-MM-DD HH:MM UTC]
- Observed Symptoms: [e.g., Specific API timeouts, DB connection pool exhaustion warnings, memory usage spike]
</Context>

<Task>
**[Step 1 — Step-back Questions]**
Before diving into detailed log analysis, answer the following questions first:

"For [tech stack or system type], when [observed symptoms] appear, what are the common root cause pattern categories?
Describe the typical leading indicators for each category."

Use the results of this Step-back analysis to proceed with Step 2.
</Task>

<OutputFormat>
## Step 1: High-Level Cause Pattern Analysis
| Cause Category | Description | Common Indicators |
|---------------|-------------|-------------------|
| | | |
| | | |
| | | |
</OutputFormat>
```

---

## Prompt Body (Step 2: Hypothesis Building and Verification Plan)

> Paste the Step 1 output into `<StepbackResult>` below and execute.

```
<Role>
You are a senior SRE with 10 years of experience. Based on the Step-back analysis results,
you formulate specific hypotheses for this incident and create a verification plan for each.
You must analyze only within the provided information, and mark uncertain items as "Insufficient data."
</Role>

<StepbackResult>
[Paste Step 1 output here]
</StepbackResult>

<ObservedData>
**Currently Available Data:**
[Paste available logs, metrics, alert details, etc. Write "None" if unavailable]
</ObservedData>

<Task>
Based on the Step-back analysis and currently available data:

1. Formulate 2–3 specific root cause hypotheses.
2. For each hypothesis:
   - If the hypothesis is correct, what patterns should appear in which data/metrics/logs?
   - If the hypothesis is wrong, what patterns should appear in which data/metrics/logs?
3. Assign verification priorities.
</Task>

<OutputFormat>
## Step 2: Hypothesis Building and Verification Plan

### Hypothesis 1: [Hypothesis Title]
- **Description**: [Hypothesis explanation]
- **Likelihood**: High / Medium / Low
- **Supporting Evidence (if hypothesis is correct)**:
  - Target: [Log/Metric/Indicator]
  - Expected Pattern: [What value or pattern should be observed]
- **Contradicting Evidence (if hypothesis is wrong)**:
  - Target: [Log/Metric/Indicator]
  - Expected Pattern: [What value or pattern should be observed]

### Hypothesis 2: [Hypothesis Title]
(Same format as above)

### Hypothesis 3: [Hypothesis Title]
(Same format as above)

---

## Verification Priority and Action Plan
| Order | Item to Verify | Method | Owner |
|-------|---------------|--------|-------|
| 1 | | | |
| 2 | | | |
| 3 | | | |
</OutputFormat>
```

---

## Tips

- Running Step 1 and Step 2 separately is more effective.
- If Step 1 results clarify the direction, return to `01_basic_rca.md` for detailed analysis.
- If all hypotheses are rejected, expand the hypothesis list or proceed to `04_advanced_tot.md`.
