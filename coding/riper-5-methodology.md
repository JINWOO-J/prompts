---
category: coding
tags:
- coding
- riper-5
- methodology
- ai-agent
- workflow
role: Developer
origin: custom
source: ''
---
# RIPER-5 — AI 에이전트 개발 방법론

## 개요

GoMall 프로젝트에서 사용된 AI 에이전트 개발 방법론.
Research → Implement → Plan → Execute → Review 5단계 사이클로
AI 에이전트의 작업을 구조화한다.

> 출처: [josix/awesome-claude-md — GoMall](https://github.com/josix/awesome-claude-md/blob/main/scenarios/developer-tooling/li0on3_GoMall/README.md)

## 5단계 사이클

### R — Research (조사)
- 기존 코드베이스 분석
- 관련 파일과 의존성 파악
- 기존 패턴과 규칙 이해
- **출력**: 현재 상태 요약

### I — Implement (구현 계획)
- 변경 사항의 영향 범위 분석
- 가능한 접근 방식 비교
- 트레이드오프 명시
- **출력**: 구현 방향 제안

### P — Plan (계획)
- 구체적인 단계별 실행 계획
- 각 단계의 검증 방법 정의
- 의존성 순서 결정
- **출력**: 번호가 매겨진 실행 계획

### E — Execute (실행)
- 계획에 따라 코드 변경
- 각 단계 후 검증
- 문제 발생 시 계획 수정
- **출력**: 변경된 코드

### R — Review (검토)
- 변경 사항 전체 검토
- 테스트 실행 및 확인
- 의도하지 않은 부수효과 확인
- **출력**: 검토 결과 및 개선 제안

## 적용 방법

에이전트에게 현재 단계를 명시적으로 지시:
```
현재 RIPER 단계: Research
[프로젝트]의 인증 모듈을 분석하고 현재 상태를 요약해줘.
```

## 장점

- 에이전트가 "바로 코딩"하는 것을 방지
- 각 단계에서 사용자 확인 가능
- 변경의 영향 범위를 사전에 파악
- 체계적인 검증 프로세스
