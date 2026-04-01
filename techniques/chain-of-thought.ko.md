---
tags:
- techniques
- cot
- reasoning
- step-by-step
---
# Chain-of-Thought (CoT) — 단계별 추론

## 개념

복잡한 문제를 중간 추론 단계를 명시적으로 거치며 풀어가는 기법.
"Let's think step by step"이라는 한 문장만으로도 LLM의 추론 정확도가 크게 향상된다.
Wei et al. (2022) 논문에서 제안되었으며, 프롬프트 엔지니어링의 가장 기본적이고 강력한 기법이다.

## 핵심 원리

- 인간의 사고 과정을 모방: 복잡한 문제를 한 번에 풀지 않고 중간 단계를 거치면 오류가 줄어든다
- 작업 기억(Working Memory) 보조: LLM이 중간 결과를 텍스트로 "기록"하면서 진행하므로 맥락 유실이 줄어든다
- Zero-shot CoT("Let's think step by step")만으로도 GSM8K 수학 벤치마크에서 정확도가 17.7% → 78.7%로 향상
- Few-shot CoT(예시 포함)는 더 높은 정확도를 보이며, 특히 산술·상식 추론에서 효과적

## 프롬프트 템플릿

```
다음 문제를 단계별로 사고하며 풀어주세요.

**문제:** [문제 설명]

**풀이 과정:**
1단계: [첫 번째 추론 — 문제의 핵심 요소 파악]
2단계: [두 번째 추론 — 관련 정보 정리]
3단계: [세 번째 추론 — 논리적 연결]
...
최종 답: [결론]

각 단계에서 왜 그렇게 판단했는지 근거를 명시하세요.
```

## 실전 예시

**시나리오: K8s Pod OOMKilled 원인 분석**

> "Pod가 OOMKilled로 반복 재시작됩니다. 단계별로 원인을 분석하세요."

1단계: OOMKilled는 컨테이너가 메모리 limit을 초과했다는 의미
2단계: `kubectl describe pod`로 마지막 종료 상태 확인 → exitCode: 137
3단계: 컨테이너 메모리 limit이 256Mi인데, 실제 사용량이 300Mi까지 증가
4단계: 애플리케이션 힙 설정(-Xmx)이 limit보다 큰 512m으로 설정됨
5단계: JVM 힙 + 메타스페이스 + 네이티브 메모리가 limit을 초과
→ 결론: JVM -Xmx를 200m으로 낮추거나 Pod 메모리 limit을 512Mi로 상향

## 변형 및 조합

- **CoT + Self-Consistency**: 여러 CoT 경로를 생성하고 다수결로 최종 답 선택
- **CoT + Few-Shot**: 예시에 추론 과정을 포함하여 패턴 학습 유도
- **CoT + Role Prompting**: "시니어 SRE로서 단계별로 분석하세요"
- **CoT + CoVe**: 추론 후 각 단계를 자기 검증

## 주의사항

- 단순한 사실 질문에는 오히려 불필요한 오버헤드 (예: "서울의 수도는?")
- 추론 단계가 길어지면 중간에 오류가 누적될 수 있음 (error propagation)
- LLM이 "그럴듯한 추론"을 만들어내지만 실제로는 틀린 경우 주의 (faithful reasoning 문제)
- 토큰 소비가 많아지므로 비용/속도 트레이드오프 고려

## 적합한 상황

수학/논리 문제, 코드 디버깅, 장애 원인 분석, 복잡한 의사결정, 다단계 분석, 기술 면접 풀이

## 참고 자료

- Wei et al. (2022) "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models"
- Kojima et al. (2022) "Large Language Models are Zero-Shot Reasoners" (Zero-shot CoT)
