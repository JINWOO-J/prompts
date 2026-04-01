---
category: coding
type: guide
tags:
- hooks
- automation
- ci-cd
role: Developer
origin: custom
source: ''
---
# Hooks & Automation — AI 에이전트 훅과 자동화 패턴

> 파일 변경·도구 실행·태스크 완료 등의 이벤트에 반응하여 AI 에이전트 동작을 자동화하는 훅 시스템.

---

## Prompt

```markdown
## 훅 유형 참조표

| 이벤트 | 트리거 시점 | 용도 |
|--------|------------|------|
| fileEdited | 파일 저장 시 | 린트, 포맷, 테스트 |
| fileCreated | 파일 생성 시 | 보일러플레이트 검증 |
| preToolUse | 도구 실행 전 | 권한 체크, 검증 |
| postToolUse | 도구 실행 후 | 결과 검증, 로깅 |
| promptSubmit | 프롬프트 전송 시 | 컨텍스트 주입 |
| postTaskExecution | 태스크 완료 후 | 테스트 실행 |

## 훅 템플릿

### 저장 시 린트
{
  "name": "Lint on Save",
  "version": "1.0.0",
  "when": {
    "type": "fileEdited",
    "patterns": ["*.ts", "*.tsx"]
  },
  "then": {
    "type": "runCommand",
    "command": "npm run lint"
  }
}

### 쓰기 작업 검증
{
  "name": "Review Write Operations",
  "version": "1.0.0",
  "when": {
    "type": "preToolUse",
    "toolTypes": ["write"]
  },
  "then": {
    "type": "askAgent",
    "prompt": "이 쓰기 작업이 코딩 표준을 따르는지 확인하라"
  }
}

### 태스크 후 테스트
{
  "name": "Test After Task",
  "version": "1.0.0",
  "when": {
    "type": "postTaskExecution"
  },
  "then": {
    "type": "runCommand",
    "command": "npm test"
  }
}

## 설계 원칙

- 훅은 빠르게 실행되어야 함 (60초 타임아웃 기본)
- preToolUse 훅이 접근을 거부하면 도구 실행 금지
- 순환 의존성 주의 (훅 A → 도구 X → 훅 A)
- 훅은 보조적 — 핵심 로직을 훅에 넣지 마라
```

---

## 배경

AI 코딩 에이전트는 자율적으로 파일을 수정하고 명령을 실행하기 때문에, 사람이 매번 개입하지 않아도 품질을 유지하려면 이벤트 기반 자동화가 필요하다. 훅 시스템은 에이전트의 행동에 사이드이펙트를 붙이는 방식으로, CI/CD 파이프라인의 에이전트 내부 버전이라고 볼 수 있다.

## 사용법

에이전트 설정 파일(예: `.claude/hooks/`) 또는 오케스트레이터 설정에서 JSON 형태로 훅을 정의할 때 위 템플릿을 사용하라.
