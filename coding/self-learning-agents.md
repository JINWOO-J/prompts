---
category: coding
tags:
- coding
- self-learning
- ai-agent
- memory
- patterns
role: Developer
origin: custom
source: ''
---
# Self-Learning Agents — 자기 학습 AI 에이전트 패턴

## 개요

AI 코딩 에이전트가 실행 이력을 추적하고 패턴을 인식하여
시간이 지남에 따라 개선되는 자기 학습 시스템 설계.

> 참고: [Equilateral Agents Open Core](https://github.com/Equilateral-AI/equilateral-agents-open-core)

## 핵심 구성요소

### 1. 에이전트 메모리
- 최근 100회 실행 이력 추적
- 성공/실패 패턴 기록
- 자주 사용되는 명령어 학습

### 2. 패턴 인식
- 반복되는 에러 패턴 감지
- 효과적인 해결 방법 기억
- 프로젝트별 관용구 학습

### 3. 워크플로우 최적화
- 자주 수행하는 작업 순서 최적화
- 불필요한 단계 제거
- 병렬 실행 가능한 작업 식별

## 메모리 시스템 설계

```
memory/
  decisions.md     — 아키텍처 결정 기록
  patterns.md      — 발견된 코드 패턴
  errors.md        — 해결된 에러와 해결법
  preferences.md   — 사용자 선호도
```

## 학습 사이클

```
1. 작업 수행
2. 결과 평가 (성공/실패)
3. 패턴 추출
4. 메모리에 저장
5. 다음 작업에 적용
```

## 실전 적용

### 에러 학습
```markdown
## Error: ModuleNotFoundError
- 원인: 가상환경 미활성화
- 해결: `source .venv/bin/activate` 후 재실행
- 빈도: 3회 (최근 7일)
```

### 선호도 학습
```markdown
## User Preferences
- 테스트 프레임워크: pytest (vitest 아님)
- 패키지 매니저: pnpm (npm 아님)
- 에러 처리: Result 패턴 (try-catch 아님)
```
