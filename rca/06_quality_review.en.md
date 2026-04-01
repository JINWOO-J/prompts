---
기법: Chain-of-Verification (CoVe) + Self-Refinement / Critique Loop
난이도: 기본 (모든 RCA 보고서에 적용 권장)
적합 상황: 대외 공유 RCA 보고서, Post-mortem 문서 최종 검토, 규정 준수 감사 보고서
필수 입력: 완성된 RCA 초안 (01~05 프롬프트 중 하나의 출력 결과)
예상 출력: 검증 질문 목록 → 초안 비판 → 수정된 최종 RCA 보고서
tags:
- 06_quality_review
- rca
- security
---

# RCA Report Quality Review (CoVe + Self-Refinement)

## Usage
After running one of `01_basic_rca.md` through `05_security_rca.md` to obtain a draft,
paste that draft into `<DraftRCA>` and execute this prompt.

---

## Prompt Body (Step 1: Verification Question Generation)

```
<Role>
You are a senior SRE with 10 years of experience and a rigorous technical document reviewer.
Based on the RCA draft below, generate a specific list of verification questions
to validate the accuracy and completeness of this report.
</Role>

<DraftRCA>
[Paste the previous prompt output (RCA draft) here]
</DraftRCA>

<Task>
Generate a specific list of questions to verify the following aspects of this RCA draft:
1. Factual Accuracy (Do the conclusions match the log data?)
2. Logical Consistency (Are cause-effect relationships logically connected?)
3. Completeness (Are there missing causes or contributing factors?)
4. Actionability (Are the recurrence prevention recommendations realistically executable?)
5. Clarity (Can a non-expert understand this?)
</Task>

<OutputFormat>
## Verification Questions

### Factual Accuracy
- Q1: [Question]
- Q2: [Question]

### Logical Consistency
- Q3: [Question]
- Q4: [Question]

### Completeness
- Q5: [Question]
- Q6: [Question]

### Actionability
- Q7: [Question]
- Q8: [Question]

### Clarity
- Q9: [Question]
- Q10: [Question]
</OutputFormat>
```

---

## Prompt Body (Step 2: Critique and Improvement Identification)

> Paste the Step 1 verification questions into `<VerificationQuestions>` and execute

```
<Role>
You are a rigorous senior SRE reviewer.
Answer the verification questions below while identifying weaknesses and areas for improvement in the RCA draft.
</Role>

<DraftRCA>
[Paste the draft again]
</DraftRCA>

<VerificationQuestions>
[Paste the Step 1 verification questions here]
</VerificationQuestions>

<Task>
Answer each verification question and identify issues in the draft:
- If the answer is clear: ✅ [Answer]
- If unverifiable from the draft (insufficient data): ⚠️ [What is missing]
- If an error or logical flaw is found: ❌ [What the error is and how to fix it]
</Task>

<OutputFormat>
## Verification Results

| Question | Result | Notes |
|----------|--------|-------|
| Q1 | ✅ / ⚠️ / ❌ | |
| Q2 | | |
| ... | | |

## Summary of Key Issues Found
1. ❌ **[Issue Title]**: [Description and correction direction]
2. ⚠️ **[Insufficient Data Item]**: [What needs additional verification]

## Improvement Recommendations (by Priority)
1. [Most important correction]
2. [Second correction]
...
</OutputFormat>
```

---

## Prompt Body (Step 3: Final Revised Version)

> Paste the Step 2 results into `<CritiqueResult>` and execute

```
<Role>
You are a senior SRE. Produce the final version of the RCA report incorporating the critique review results.
Apply corrections while preserving the verified content from the original RCA.
</Role>

<DraftRCA>
[Paste the draft]
</DraftRCA>

<CritiqueResult>
[Paste the Step 2 critique results]
</CritiqueResult>

<Task>
Produce the final RCA report incorporating the critique review results:
- Fix items marked as errors (❌)
- Mark insufficient data items (⚠️) as "Further investigation required: [item]"
- Incorporate improvement recommendations into the report
- Improve overall document consistency and clarity
</Task>

<OutputFormat>
# Final RCA Report — [Service Name] Incident / [Date]

## Executive Summary
[2–3 sentence summary understandable by non-experts]

## Root Cause
> [Clear 1–2 sentences]

## Incident Timeline
[Timeline table]

## 5-Whys Analysis
[Revised 5-Whys]

## Recurrence Prevention Action Plan
[Revised action plan table]

## Items Requiring Further Investigation
- ⚠️ [Item 1]
- ⚠️ [Item 2]

## Report Metadata
- Date: [Date]
- Author: [Name/Team]
- Reviewer: [Name/Team]
- Version: v1.0
</OutputFormat>
```

---

## Tips

- **Always run as the final step**: Regardless of which RCA prompt was used, validate the final report through this prompt.
- **Step 2 is the most important**: The "critique loop" is the key step for catching AI hallucinations and logical leaps.
- **External-facing documents**: For post-mortems shared with executives or customers, always use the Step 3 final version.
