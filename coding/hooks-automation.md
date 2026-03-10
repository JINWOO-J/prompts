---
category: coding
tags:
- coding
- hooks
- automation
- ai-agent
- ci-cd
role: Developer
origin: custom
source: ''
---
# Hooks & Automation — AI 에이전트 훅과 자동화 패턴

## 개요

AI 코딩 에이전트의 동작을 이벤트 기반으로 자동화하는 훅(Hook) 시스템.
파일 변경, 도구 실행, 태스크 완료 등의 이벤트에 반응하여 자동으로 작업을 수행한다.

## 훅 유형

| 이벤트 | 트리거 시점 | 용도 |
|--------|------------|------|
| fileEdited | 파일 저장 시 | 린트, 포맷, 테스트 |
| fileCreated | 파일 생성 시 | 보일러플레이트 검증 |
| preToolUse | 도구 실행 전 | 권한 체크, 검증 |
| postToolUse | 도구 실행 후 | 결과 검증, 로깅 |
| promptSubmit | 프롬프트 전송 시 | 컨텍스트 주입 |
| postTaskExecution | 태스크 완료 후 | 테스트 실행 |

## 실전 패턴

### 1. 저장 시 린트
```json
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
```

### 2. 쓰기 작업 검증
```json
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
```

### 3. 태스크 후 테스트
```json
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
```

## 설계 원칙

- 훅은 빠르게 실행되어야 함 (60초 타임아웃 기본)
- preToolUse 훅이 접근을 거부하면 도구 실행 금지
- 순환 의존성 주의 (훅 A → 도구 X → 훅 A)
- 훅은 보조적 — 핵심 로직을 훅에 넣지 마라
