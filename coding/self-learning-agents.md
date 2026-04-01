---
category: coding
type: guide
tags:
- agent
- self-learning
- memory
- pattern
role: Developer
origin: custom
source: 'https://github.com/Equilateral-AI/equilateral-agents-open-core'
---
# Self-Learning Agents — 자기 학습 AI 에이전트 패턴

> 실행 이력을 추적하고 패턴을 인식하여 시간이 지남에 따라 개선되는 AI 에이전트 메모리 시스템 설계.

---

## Prompt

```markdown
## 메모리 파일 구조

memory/
  decisions.md     — 아키텍처 결정 기록
  patterns.md      — 발견된 코드 패턴
  errors.md        — 해결된 에러와 해결법
  preferences.md   — 사용자 선호도

## 에러 학습 템플릿

## Error: [에러명]
- 원인: [근본 원인]
- 해결: [해결 명령어 또는 절차]
- 빈도: N회 (최근 7일)

### 예시
## Error: ModuleNotFoundError
- 원인: 가상환경 미활성화
- 해결: `source .venv/bin/activate` 후 재실행
- 빈도: 3회 (최근 7일)

## 선호도 템플릿

## User Preferences
- 테스트 프레임워크: [선택] (대안 아님)
- 패키지 매니저: [선택] (대안 아님)
- 에러 처리: [패턴] (대안 아님)

### 예시
## User Preferences
- 테스트 프레임워크: pytest (vitest 아님)
- 패키지 매니저: pnpm (npm 아님)
- 에러 처리: Result 패턴 (try-catch 아님)

## 학습 사이클

1. 작업 수행
2. 결과 평가 (성공/실패)
3. 패턴 추출
4. 메모리에 저장
5. 다음 작업에 적용
```

---

## 배경

AI 에이전트는 기본적으로 상태가 없어 같은 실수를 반복한다. 메모리 파일을 프로젝트에 유지하면 에이전트가 이전 세션의 결정과 오류 해결법을 컨텍스트로 로드할 수 있다. 핵심 구성요소는 (1) 최근 실행 이력 추적, (2) 반복 에러 패턴 감지, (3) 효과적인 해결 방법 기억, (4) 프로젝트별 관용구와 사용자 선호도 학습이다.

## 사용법

프로젝트 루트에 `memory/` 디렉토리를 만들고, 에이전트 세션 시작 시 해당 파일들을 컨텍스트에 포함하여 이전 학습 내용을 재활용하라.
