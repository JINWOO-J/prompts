---
tags:
- techniques
- react
- reasoning
- acting
- agent
- tool-use
---
# ReAct — Reasoning + Acting 패턴

## 개념

추론(Reasoning)과 행동(Acting)을 교차 반복하는 기법.
LLM이 생각 → 행동 → 관찰 → 생각 사이클을 반복하며 문제를 해결한다.
Yao et al. (2022) 제안. 현대 AI 에이전트(LangChain, AutoGPT 등)의 핵심 패턴이며,
도구 사용(tool use)과 자연스럽게 결합된다.

## 핵심 원리

- 추론과 행동의 시너지: 추론만으로는 정보 부족, 행동만으로는 방향 상실 → 교차가 최적
- 관찰 기반 수정: 행동 결과를 관찰하고 다음 추론에 반영하여 적응적 문제 해결
- 해석 가능성: Thought-Action-Observation 트레이스가 남아 디버깅 용이
- HotpotQA에서 CoT 대비 +6%, 행동만 하는 방식 대비 +14% 성능 향상

## 프롬프트 템플릿

```
다음 문제를 ReAct 패턴으로 해결하세요.

**문제:** [문제 설명]

**Thought 1:** [현재 상황 분석. 무엇을 알고 있고, 무엇을 모르는가? 다음에 무엇을 해야 하는가?]
**Action 1:** [수행할 행동 — 검색, 명령 실행, API 호출, 파일 확인 등]
**Observation 1:** [행동 결과 관찰 — 실제 출력, 데이터, 에러 메시지 등]

**Thought 2:** [관찰 결과를 바탕으로 새로운 추론. 가설 수정 또는 확인]
**Action 2:** [다음 행동]
**Observation 2:** [결과]

**Thought 3:** [충분한 정보가 모였는가? 결론을 내릴 수 있는가?]
**Action 3:** [최종 행동 또는 추가 조사]
**Observation 3:** [결과]

**Final Answer:** [모든 관찰을 종합한 최종 결론과 해결책]
```

## 실전 예시

**시나리오: "프로덕션 API 응답 시간이 갑자기 5초로 증가"**

Thought 1: 응답 시간 증가의 일반적 원인은 DB, 네트워크, 앱 로직. 먼저 어디서 병목인지 확인
Action 1: `kubectl top pods -n production` 실행
Observation 1: api-server Pod CPU 95%, 다른 Pod는 정상

Thought 2: API 서버 CPU가 높다. GC 문제? 무한 루프? 트래픽 급증? 로그 확인 필요
Action 2: `kubectl logs api-server-xxx --tail=100` 확인
Observation 2: "Connection pool exhausted" 에러 반복 발생

Thought 3: DB 커넥션 풀 고갈. DB 쪽 문제인지 앱 쪽 커넥션 누수인지 확인
Action 3: DB 활성 커넥션 수 조회 → 500개 (max_connections: 100의 5배)
Observation 3: 앱에서 커넥션을 반환하지 않는 누수 확인

Final Answer: 최근 배포에서 트랜잭션 finally 블록 누락 → 커넥션 미반환 → 풀 고갈 → 타임아웃

## 변형 및 조합

- **ReAct + CoT**: Thought 부분을 CoT로 상세화
- **ReAct + Self-Refinement**: 최종 답변을 자기 비평 후 개선
- **ReAct + Role**: "시니어 SRE로서" ReAct 수행
- **ReAct + Tool Use**: 실제 도구(kubectl, SQL 등)와 연동

## 주의사항

- 행동이 부작용을 가질 수 있음 (프로덕션 환경에서 주의)
- Observation이 예상과 다를 때 무한 루프에 빠질 수 있음 (최대 반복 횟수 설정)
- 도구 접근 권한이 없으면 Action이 가상의 결과를 만들어낼 수 있음
- 각 사이클마다 토큰이 누적되므로 긴 체인은 비용 증가

## 적합한 상황

도구 사용이 필요한 작업, 정보 검색, 멀티스텝 디버깅, AI 에이전트 설계, 인시던트 대응

## 참고 자료

- Yao et al. (2022) "ReAct: Synergizing Reasoning and Acting in Language Models"
- LangChain ReAct Agent 구현 (실용적 참고)
