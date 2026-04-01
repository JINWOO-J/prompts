---
category: infrastructure
source: '[shawnewallace/prompt-library](https://github.com/shawnewallace/prompt-library/blob/main/scenarios/devops-infrastructure/claude-code/commands/scaffold-pipeline.md)'
role: DevOps / Infrastructure Engineer
origin: shawnewallace
extract_date: 2026-03-05
tags:
- ci-cd
- claude
- code
- commands
- infrastructure
- k8s-deployment
- k8s-node
- k8s-secret
- pipeline
- scaffold
- security
- terraform
---

# 파이프라인 스캐폴딩

`$ARGUMENTS`에 대한 CI/CD 파이프라인을 스캐폴딩합니다.

필요한 경우 명확한 질문을 합니다:
- 어떤 플랫폼? (GitHub Actions, Azure Pipelines, GitLab CI)
- 어떤 스택? (Node.js, Python, .NET, 컨테이너, Terraform 등)
- 어떤 환경? (예: dev → staging → prod)
- 따라야 할 기존 규칙이 있나요?

그런 다음 다음 단계로 파이프라인을 생성합니다:

1. **린트 및 검증** — 언어에 적합한 린팅 및 해당되는 경우 IaC 검증
2. **테스트** — 커버리지 출력과 함께 테스트 스위트 실행
3. **빌드** — 아티팩트 컴파일 또는 컨테이너화
4. **보안 스캔** — 의존성 감사 + 스택에 적합한 컨테이너 또는 SAST 스캔
5. **배포: 스테이징** — 스테이징에 배포 (main 브랜치에서 자동)
6. **배포: 프로덕션** — 프로덕션에 배포 (수동 승인 필요)

`ci-cd.instructions.md` 및 `security.instructions.md`의 규칙을 따릅니다:
- 플랫폼의 시크릿 저장소에서 시크릿 — 절대 하드코딩하지 않음
- 잠금 파일 해시에 키가 지정된 의존성 캐시
- 작업 간 명시적 `needs:`
- 모든 작업에 타임아웃
- 커밋 SHA로 프로덕션 배포 태깅

각 섹션을 설명하는 주석이 포함된 완전한 파이프라인 파일을 출력합니다.
