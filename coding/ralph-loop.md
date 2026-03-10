---
category: coding
tags:
- coding
- ralph-loop
- autonomous
- ai-agent
- testing
role: Developer
origin: custom
source: ''
---
# Ralph Loop — AI 에이전트 자율 반복 실행 패턴

## 개요

Geoffrey Huntley가 만든 "Ralph Wiggum 기법". AI 코딩 에이전트를 스펙에 대해
자율적으로 반복 실행하여 기대 결과가 충족될 때까지 돌리는 방법론.
2026년 초 AI 코딩 커뮤니티에서 가장 많이 논의된 개발 방법론이다.

> 참고: [learndevrel.com — The Ralph Loop](https://learndevrel.com/blog/ralph-loop-ai-coding)

## 핵심 개념

```bash
while ! tests_pass; do
  ai_agent fix_failing_tests
done
```

스펙(테스트)을 먼저 작성하고, AI 에이전트가 모든 테스트를 통과할 때까지
자율적으로 코드를 수정하게 한다.

## 워크플로우

### 1. 스펙 정의
- 기대 동작을 테스트로 작성
- 엣지 케이스 포함
- 성능 기준 포함 (필요시)

### 2. 에이전트 실행
- 에이전트에게 테스트 통과를 목표로 지시
- 실패 시 자동으로 수정 시도
- 성공할 때까지 반복

### 3. 검증
- 모든 테스트 통과 확인
- 코드 리뷰 (사람)
- 의도하지 않은 부수효과 확인

## 전제 조건

- 명확하고 포괄적인 테스트 스위트
- 에이전트의 파일 시스템 접근 권한
- 테스트 실행 명령어가 CLAUDE.md에 명시
- 적절한 타임아웃 설정

## 주의사항

- 테스트가 불완전하면 "테스트만 통과하는" 나쁜 코드가 생길 수 있음
- 무한 루프 방지를 위한 최대 반복 횟수 설정 필요
- 보안 관련 코드에는 부적합 — 수동 리뷰 필수
