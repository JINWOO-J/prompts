---
기법: 5-Whys + Chain-of-Thought (CoT)
난이도: 기본
적합 상황: 단일 서비스/시스템 장애, 인과 관계가 비교적 선형적인 경우
필수 입력: 장애 현상 요약, 발생 시각, 영향 받은 시스템, 관련 로그 또는 에러 메시지
예상 출력: 단계별 5-Whys 분석, 근본 원인 도출, 재발 방지 권고안
tags:
- 01_basic_rca
- k8s-node
- kubernetes
- postgres
- rca
---

# Basic RCA (5-Whys + CoT)

## Usage
Replace the content inside `[brackets]` with actual incident information, then paste into an LLM.

---

## Prompt Body

```
<Role>
You are a senior SRE (Site Reliability Engineer) with 10 years of experience.
As an expert in infrastructure failure analysis and root cause identification, you perform systematic RCA.
You must analyze only within the provided information, and mark uncertain items as "Insufficient data — further investigation required."
</Role>

<Context>
- Service/System: [Service name or system name]
- Tech Stack: [e.g., Kubernetes on GCP, Node.js API, PostgreSQL]
- Incident Start Time: [YYYY-MM-DD HH:MM UTC]
- Incident End/Recovery Time: [YYYY-MM-DD HH:MM UTC] (write "Ongoing" if not yet recovered)
- Impact Scope: [Number of affected users, features, regions, etc.]
</Context>

<Task>
Using the 5-Whys technique and Chain-of-Thought approach, perform a step-by-step root cause analysis based on the following incident description and logs.

**Incident Description:**
[Describe the incident in detail. e.g., "Payment API response time increased from an average of 200ms to 8000ms, with 5xx error rate reaching 35%"]

**Related Logs/Error Messages:**
[Paste logs here. If unavailable, write "Logs not provided"]
</Task>

<OutputFormat>
Produce output in the following format:

## 1. Incident Summary
- Symptom:
- Impact:
- Occurrence Time:

## 2. 5-Whys Analysis
**Why 1:** [Why did the observed symptom occur?]
→ Answer:

**Why 2:** [Why did the answer to Why 1 occur?]
→ Answer:

**Why 3:** [Why did the answer to Why 2 occur?]
→ Answer:

**Why 4:** [Why did the answer to Why 3 occur?]
→ Answer:

**Why 5:** [Why did the answer to Why 4 occur?]
→ Answer:

## 3. Root Cause
[State the identified root cause in 1–2 sentences]

## 4. Contributing Factors
- [Factors that worsened the incident beyond the root cause]

## 5. Recurrence Prevention Recommendations
| Priority | Action | Owner | Deadline |
|----------|--------|-------|----------|
| High | | | |
| Medium | | | |
| Low | | | |

## 6. Uncertain Items (Further Investigation Required)
- [Items that could not be analyzed due to insufficient data]
</OutputFormat>
```

---

## Tips

- **If 5 Whys are not enough**: Continue with "Why 6", "Why 7", etc. The goal is to reach the process/policy failure level.
- **If no logs are available**: Add the following to the `<Task>` section: "Since no logs are currently available, propose possible root cause hypotheses and list the logs/metrics needed to verify each hypothesis."
- **Next step**: If the cause remains unclear, proceed to `02_hypothesis_stepback.md`.
