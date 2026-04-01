---
tags:
- techniques
- few-shot
- examples
- in-context-learning
---
# Few-Shot Prompting — 예시 기반 학습

## 개념

프롬프트에 2~5개의 입출력 예시를 포함하여 LLM이 패턴을 학습하도록 하는 기법.
Brown et al. (2020, GPT-3 논문)에서 체계화. In-Context Learning(ICL)의 핵심.
모델을 파인튜닝하지 않고도 예시만으로 새로운 태스크를 수행할 수 있게 한다.

## 핵심 원리

- 패턴 인식: LLM이 예시에서 입출력 매핑 규칙을 추론
- 형식 통일: 출력 형식을 예시로 보여주면 일관된 형식으로 답변
- 예시 선택이 핵심: 관련성 높고 다양한 예시가 성능을 좌우
- 예시 순서도 영향: 마지막 예시에 가까운 패턴을 따르는 경향 (recency bias)

## 프롬프트 템플릿

```
다음 예시를 참고하여 동일한 형식으로 답변하세요.

**예시 1:**
입력: [입력 1]
출력: [출력 1]

**예시 2:**
입력: [입력 2]
출력: [출력 2]

**예시 3:**
입력: [입력 3]
출력: [출력 3]

---
**실제 입력:**
입력: [실제 입력]
출력:
```

## 실전 예시

**시나리오: 에러 로그 → 원인 분류**

예시 1:
입력: "java.lang.OutOfMemoryError: Java heap space"
출력: 카테고리: 메모리 | 심각도: Critical | 조치: JVM 힙 크기 증가 또는 메모리 누수 확인

예시 2:
입력: "Connection refused: connect to [db-host]:5432"
출력: 카테고리: 네트워크 | 심각도: High | 조치: DB 서버 상태 및 방화벽 규칙 확인

실제 입력: "disk usage exceeded 95% on /var/log"
→ LLM 출력: 카테고리: 스토리지 | 심각도: High | 조치: 로그 로테이션 설정 및 오래된 로그 정리

## 변형 및 조합

- **Few-Shot + CoT**: 예시에 추론 과정을 포함 (Few-Shot CoT)
- **Few-Shot + Role**: 역할 설정 후 예시 제공
- **Few-Shot + Self-Consistency**: 예시 기반 다중 경로 생성

## 주의사항

- 예시가 편향되면 출력도 편향됨 (다양한 예시 필요)
- 예시가 너무 많으면 컨텍스트 윈도우 소비 (2-5개가 적정)
- 예시와 실제 입력의 도메인이 다르면 효과 감소
- 예시 순서에 따라 결과가 달라질 수 있음 (순서 실험 권장)

## 적합한 상황

출력 형식 통일, 분류 작업, 변환 작업, 일관된 스타일 유지, 새로운 태스크 정의

## 참고 자료

- Brown et al. (2020) "Language Models are Few-Shot Learners" (GPT-3)
- Liu et al. (2022) "What Makes Good In-Context Examples for GPT-3?" 
