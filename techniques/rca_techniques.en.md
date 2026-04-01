---
tags:
- iam
- rca_techniques
- techniques
---
# RCA-Specific Prompt Techniques Reference

> A curated reference of techniques directly applicable to RCA (Root Cause Analysis), organized from `found.md`.

---

## 📌 Technique Selection Guide by RCA Process Stage

```
Incident occurs
    │
    ▼
[Stage 1] Initial scoping            →  Step-back prompting
    │
    ▼
[Stage 2] Cause exploration           →  5-Whys + CoT (simple incidents)
    │                                     ToT (complex/multi-cause incidents)
    ▼
[Stage 3] Hypothesis & validation     →  Hypothesis Testing
    │
    ▼
[Stage 4] Timeline reconstruction     →  Prompt Chaining (4-stage pipeline)
    │
    ▼
[Stage 5] (Security breach) Attack    →  Diamond Model + MITRE ATT&CK
    │       analysis
    ▼
[Stage 6] RCA report validation       →  CoVe + Self-Refinement
```

---

## 🔍 Technique Details

### 1. Step-back Prompting — Initial Scoping

| Item | Description |
|------|-------------|
| **Purpose** | Identify high-level principles/patterns before diving into detailed log analysis |
| **Suitable for** | When the cause category is unclear (Network? App? DB?) |
| **Core technique** | "Before analyzing this incident, what are the common cause patterns for this symptom in [system type]?" |
| **Prompt file** | `rca/02_hypothesis_stepback.md` |

---

### 2. 5-Whys + CoT (Chain-of-Thought) — Cause Exploration (Basic)

| Item | Description |
|------|-------------|
| **Purpose** | Dig beyond "human error" down to process/policy failures |
| **Suitable for** | Single-system incidents with relatively linear causality |
| **Core technique** | Step-by-step "Why?" × 5, with explicit reasoning at each step |
| **Prompt file** | `rca/01_basic_rca.md` |

---

### 3. ToT (Tree-of-Thoughts) — Cause Exploration (Advanced)

| Item | Description |
|------|-------------|
| **Purpose** | Explore 2–4 independent hypothesis paths simultaneously, scoring by risk and impact |
| **Suitable for** | Multi-system incidents with multiple candidate causes |
| **Core technique** | Guide the model to present probability, blast radius, and verification methods for each path in parallel |
| **Prompt file** | `rca/04_advanced_tot.md` |

---

### 4. Hypothesis Testing — Hypothesis Formulation & Validation

| Item | Description |
|------|-------------|
| **Purpose** | Preemptively formulate 2–3 hypotheses, then generate evidence checklists to prove/disprove each |
| **Suitable for** | Early stages with limited data, narrowing down multiple candidate causes |
| **Core technique** | "What logs/metrics need to be checked to prove each hypothesis?" |
| **Prompt file** | `rca/02_hypothesis_stepback.md` |

---

### 5. Prompt Chaining — Timeline Reconstruction

| Item | Description |
|------|-------------|
| **Purpose** | Break complex RCA into a staged pipeline |
| **Suitable for** | Multi-service incidents with diverse log sources |
| **Pipeline** | `Log classification → Event timeline → Root cause → Prevention actions` |
| **Prompt file** | `rca/03_timeline_chain.md` |

---

### 6. Diamond Model + MITRE ATT&CK — Security Breach Analysis

| Item | Description |
|------|-------------|
| **Purpose** | Analyze attack paths and IOCs using standardized frameworks |
| **Suitable for** | Security breaches, anomaly detection, APT analysis |
| **Output format** | Diamond Model 4-axis table + ATT&CK Tactic/Technique ID mapping |
| **Prompt file** | `rca/05_security_rca.md` |

---

### 7. CoVe + Self-Refinement — RCA Report Validation

| Item | Description |
|------|-------------|
| **Purpose** | Self-verify logical and factual errors in the draft, then produce the final version |
| **Suitable for** | Externally shared RCA reports, post-mortem documentation |
| **Core technique** | Draft → Generate verification questions → Critique → Revision loop |
| **Prompt file** | `rca/06_quality_review.md` |

---

### 8. Context Scaffolding — Context Injection (Universal)

| Item | Description |
|------|-------------|
| **Purpose** | Inject specific environment information to suppress hallucination |
| **Include in all prompts** | System architecture, tech stack, incident timestamp, blast radius |
| **Guardrail** | "Answer only from the attached log/runbook data; respond with 'insufficient data' if unknown" |

---

## 📊 Recommended Prompts by RCA Difficulty

| Difficulty | Scenario | Recommended prompt |
|------------|----------|--------------------|
| 🟢 Basic | Simple single-service incident | `01_basic_rca.md` |
| 🟡 Intermediate | Unclear cause, multiple hypotheses needed | `02_hypothesis_stepback.md` |
| 🟡 Intermediate | Multi-service, complex timeline | `03_timeline_chain.md` |
| 🔴 Advanced | Multiple candidate causes, cost/risk analysis needed | `04_advanced_tot.md` |
| 🔴 Advanced | Suspected security breach | `05_security_rca.md` |
| ⬜ Universal | Final review of RCA report | `06_quality_review.md` |
