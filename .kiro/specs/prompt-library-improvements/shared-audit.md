# shared/ 폴더 파일 감사 결과

> **감사 일시**: 2025-07  
> **대상**: shared/ 내 17개 파일  
> **목적**: 인프라/보안 운영 프롬프트 라이브러리 정체성에 부합하는지 분류  
> **AC**: `req-1.ac-1`

---

## 분류 기준

| 분류 | 설명 |
|------|------|
| 🟢 인프라/보안 운영 관련 | 인프라 운영, 보안, SRE, 인시던트 대응 등 라이브러리 목적에 직접 부합 |
| 🔴 범용 개발 에이전트 | 일반적인 소프트웨어 개발 에이전트로, 인프라/보안 운영과 직접적 관련 없음 |
| 🟡 재분류 필요 | 인프라 요소를 포함하지만 현재 카테고리가 부적절하여 이동 검토 필요 |

---

## 분류 결과 요약

| 분류 | 파일 수 |
|------|---------|
| 🟢 인프라/보안 운영 관련 | 2 |
| 🔴 범용 개발 에이전트 | 14 |
| 🟡 재분류 필요 | 1 |

---

## 🟢 인프라/보안 운영 관련 (2개)

| 파일 | origin | 역할 | 판단 근거 |
|------|--------|------|-----------|
| `guardrails.md` | custom | 공통 가드레일 | 환각 방지, 보안 데이터 격리(`<AnalysisData>` 태그), HITL 규칙(호스트 격리·방화벽 변경 등 고위험 작업 승인), 보안 보고서 마스킹 규칙 등 운영 보안에 직접 기여 |
| `role-definitions.md` | custom | 공통 역할 정의 | SRE Engineer, Incident Responder, Security Engineer(SIRT), K8s Specialist, Terraform/IaC Engineer, DevOps/Platform Engineer 페르소나 정의. 라이브러리 전체 프롬프트가 참조하는 핵심 공유 자산 |

---

## 🔴 범용 개발 에이전트 (14개)

| 파일 | origin | 역할 | 판단 근거 |
|------|--------|------|-----------|
| `agent-installer.md` | extracted | Claude Code 에이전트 설치 도구 | GitHub에서 에이전트를 브라우징/설치하는 메타 도구. 인프라/보안 운영과 무관 |
| `api-architect.agent.md` | shawnewallace | API 아키텍트 | API 연결 코드 생성 (서비스/매니저/레질리언스 레이어). 범용 API 개발 에이전트 |
| `api-designer.md` | extracted | API 설계자 | REST/GraphQL API 설계 전문. 범용 API 설계 에이전트 |
| `api-documenter.md` | extracted | API 문서화 | OpenAPI 스펙, SDK 문서, 인터랙티브 포털. 범용 문서화 에이전트 |
| `architect.agent.md` | shawnewallace | 아키텍트/기술 리드 | 마크다운 기반 설계 계획 수립. 범용 아키텍처 계획 에이전트 |
| `backend-developer.md` | extracted | 백엔드 개발자 | Node.js/Python/Go 서버 개발. 범용 백엔드 개발 에이전트 |
| `check.agent.md` | shawnewallace | 코드 리뷰 | 코딩 표준 준수, 리팩토링 제안. 범용 코드 리뷰 에이전트 |
| `context-manager.md` | extracted | 컨텍스트 관리자 | 분산 에이전트 시스템의 상태/지식 관리. 범용 메타 오케스트레이션 |
| `documentation-engineer.md` | extracted | 문서화 엔지니어 | API 문서, 튜토리얼, 아키텍처 가이드. 범용 문서화 에이전트 |
| `fullstack-developer.md` | extracted | 풀스택 개발자 | DB~UI 전체 스택 개발. 범용 풀스택 개발 에이전트 |
| `graphql-architect.md` | extracted | GraphQL 아키텍트 | Apollo Federation, 스키마 설계. 범용 GraphQL 개발 에이전트 |
| `knowledge-synthesizer.md` | extracted | 지식 합성 | 멀티 에이전트 시스템의 패턴 인식/지식 관리. 범용 메타 오케스트레이션 |
| `plan.agent.md` | shawnewallace | 전략 계획 어시스턴트 | 코드베이스 분석, 요구사항 정리, 구현 전략 수립. 범용 계획 에이전트 |
| `websocket-engineer.md` | extracted | WebSocket 엔지니어 | 실시간 통신 시스템 구축. 범용 실시간 통신 개발 에이전트 |

---

## 🟡 재분류 필요 (1개)

| 파일 | origin | 역할 | 판단 근거 | 권장 이동 위치 |
|------|--------|------|-----------|---------------|
| `microservices-architect.md` | extracted | 마이크로서비스 아키텍트 | K8s 배포, 서비스 메시(Istio), 컨테이너 오케스트레이션, 관찰성 스택, zero-trust 네트워킹 등 인프라 운영 요소를 상당 부분 포함. 그러나 주 목적은 마이크로서비스 아키텍처 설계이므로 `infrastructure/` 카테고리가 더 적합 | `infrastructure/` |
