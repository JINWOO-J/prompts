---
category: infrastructure
source: '[shawnewallace/prompt-library](https://github.com/shawnewallace/prompt-library/blob/main/scenarios/devops-infrastructure/github-copilot/instructions.md)'
role: DevOps / Infrastructure Engineer
origin: shawnewallace
extract_date: 2026-03-05
tags:
- ci-cd
- copilot
- github
- iam
- infrastructure
- k8s-secret
- pipeline
- security
- terraform
---

# Copilot 지침 — DevOps 및 인프라

## 언어 정책

기여자를 위한 모든 지침, 프롬프트, 코드 주석은 영어로 작성해야 합니다.

## 개발 워크플로우

**중요:** 인프라 변경을 구현할 때 항상 다음 단계를 따르세요:

1. 아래의 관련 지침 파일을 참조하고 구현을 안내한 파일을 명시합니다 (예: `Instructions used: [terraform.instructions.md, security.instructions.md]`).

2. 인프라 변경을 커밋하기 전에 `terraform validate`와 `terraform plan` (또는 동등한 도구)을 실행합니다. 플랜 출력을 주의 깊게 검토합니다 — diff를 검토하지 않고 절대 적용하지 않습니다.

3. 보안 스캐닝 도구(`tfsec`, `checkov`, `trivy`)를 실행하고 커밋 전에 모든 HIGH 및 CRITICAL 발견 사항을 해결합니다.

4. 자격 증명, 시크릿 또는 환경별 값을 절대 하드코딩하지 않습니다. 모든 민감한 값은 시크릿 매니저 또는 환경 변수에서 가져와야 합니다.

## 지침 파일

| 파일 | 목적 |
|------|------|
| [terraform.instructions.md](./instructions/terraform.instructions.md) | 모듈 구조, 원격 상태, 변수 규칙 |
| [ci-cd.instructions.md](./instructions/ci-cd.instructions.md) | 파이프라인 단계, 시크릿, 캐싱, 환경 게이트 |
| [security.instructions.md](./instructions/security.instructions.md) | 최소 권한 IAM, 스캐닝, 시크릿 관리 |
