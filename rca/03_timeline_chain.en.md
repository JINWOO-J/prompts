---
기법: 프롬프트 체이닝 (Prompt Chaining) — 4단계 파이프라인
난이도: 중급
적합 상황: 멀티 서비스/시스템 장애, 로그 소스가 다양하고 타임라인 재구성이 필요한 경우
필수 입력: 각 시스템 로그 (최소 2개 이상 소스), 장애 발생 시각, 영향 시스템 목록
예상 출력: 시스템별 분류된 로그 → 정렬된 이벤트 타임라인 → 근본 원인 → 재발 방지 액션 플랜
tags:
- 03_timeline_chain
- rca
- redis
---

# Timeline Reconstruction (4-Step Prompt Chaining)

## Usage
Execute each step **in order**, using the output of the previous step as input for the next.

---

## STEP 1: Log Classification and Normalization

```
<Role>
You are a senior SRE. You classify and normalize raw logs collected from multiple systems.
</Role>

<Context>
- Incident Start Time: [YYYY-MM-DD HH:MM UTC]
- Affected Systems: [e.g., API server, DB, Cache (Redis), Load Balancer]
- Analysis Time Window: [30 minutes before incident ~ 10 minutes after recovery]
</Context>

<RawLogs>
[Paste raw logs collected from multiple systems here]
</RawLogs>

<Task>
Classify and normalize the logs above according to the following criteria:
1. Group by system (API server, DB, Cache, Network, etc.)
2. Standardize each log entry to the format: `[Timestamp] [System] [Level] [Message]`
3. Exclude logs outside the analysis window
4. Compress duplicate logs as "Repeated N times"
</Task>

<OutputFormat>
## Classified Logs by System

### [System A]
| Timestamp | Level | Message |
|-----------|-------|---------|
| | | |

### [System B]
(Same format)

## Notable Anomalies After Classification
- [System A]: [Anomaly summary]
- [System B]: [Anomaly summary]
</OutputFormat>
```

---

## STEP 2: Event Timeline Reconstruction

> **Paste the previous step's output into `<ClassifiedLogs>` and execute**

```
<Role>
You are a senior SRE. You reconstruct the chronological sequence of the incident based on classified logs.
</Role>

<ClassifiedLogs>
[Paste Step 1 output here]
</ClassifiedLogs>

<Task>
Based on the classified logs, create a chronological event timeline.
- Reconstruct the flow from normal state through incident occurrence, propagation, impact spread, and recovery
- Express cascading effects on other systems using arrows (→)
- Clearly mark the "first anomaly timestamp"
</Task>

<OutputFormat>
## Event Timeline

| Time | System | Event | Cascading Impact |
|------|--------|-------|-----------------|
| HH:MM | | | |
| HH:MM | ⚠️ **First Anomaly** | | |
| HH:MM | | | → Impact on [next system] |
| HH:MM | 🔴 Service Impact Begins | | |
| HH:MM | ✅ Recovery | | |

## Incident Propagation Summary
[Summarize in 2–3 sentences how the incident started and propagated across systems]
</OutputFormat>
```

---

## STEP 3: Root Cause Analysis

> **Paste the previous step's output into `<Timeline>` and execute**

```
<Role>
You are a senior SRE. You derive the root cause based on timeline analysis.
You must draw conclusions only from the provided timeline data, and mark uncertain items as "Insufficient data."
</Role>

<Timeline>
[Paste Step 2 output here]
</Timeline>

<Task>
Based on the timeline:
1. Trace the root cause using the 5-Whys technique (down to the process/policy level)
2. Identify contributing factors
3. Clearly distinguish between root cause and contributing factors
</Task>

<OutputFormat>
## Root Cause Analysis

### 5-Whys
- Why 1: →
- Why 2: →
- Why 3: →
- Why 4: →
- Why 5: →

### Root Cause
> [State clearly in 1–2 sentences]

### Contributing Factors
1.
2.
3.
</OutputFormat>
```

---

## STEP 4: Recurrence Prevention Action Plan

> **Paste the previous step's output into `<RCAResult>` and execute**

```
<Role>
You are a senior SRE. You create an actionable recurrence prevention plan based on the RCA results.
</Role>

<RCAResult>
[Paste Step 3 output here]
</RCAResult>

<Task>
Based on the root cause and contributing factors:
1. Immediate Actions (within 24–48 hours): Temporary measures to reduce immediate risk
2. Short-term Improvements (1–2 weeks): Technical improvements to prevent recurrence
3. Long-term Improvements (1–3 months): Address fundamental system vulnerabilities
Include the responsible team and expected deadline for each item.
</Task>

<OutputFormat>
## Recurrence Prevention Action Plan

### Immediate Actions (24–48 hours)
| Item | Description | Owner | Deadline |
|------|-------------|-------|----------|

### Short-term Improvements (1–2 weeks)
| Item | Description | Owner | Deadline |
|------|-------------|-------|----------|

### Long-term Improvements (1–3 months)
| Item | Description | Owner | Deadline |
|------|-------------|-------|----------|

### Post-mortem Report Schedule
- [ ] Draft: [Date]
- [ ] Team Review: [Date]
- [ ] Final Distribution: [Date]
</OutputFormat>
```

---

## Tips

- **Save each step's output** before pasting it into the next step.
- After completing Step 3, use **06_quality_review.md** to validate the final report.
- If logs are very large, prioritize selecting key anomaly logs in Step 1.
