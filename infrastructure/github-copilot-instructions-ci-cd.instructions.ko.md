---
category: infrastructure
source: '[shawnewallace/prompt-library](https://github.com/shawnewallace/prompt-library/blob/main/scenarios/devops-infrastructure/github-copilot/instructions/ci-cd.instructions.md)'
role: DevOps / Infrastructure Engineer
origin: shawnewallace
extract_date: 2026-03-05
tags:
- cd.instructions
- ci-cd
- copilot
- github
- infrastructure
- k8s-deployment
- k8s-node
- k8s-secret
- pipeline
- rds
- security
- sts
---

---
applyTo: '**/.github/workflows/*.yml,**/pipelines/*.yml,**/pipelines/*.yaml'
---

# CI/CD 파이프라인

## 파이프라인 구조

모든 파이프라인은 순서대로 실행되는 명확히 분리된 단계를 가져야 합니다:

1. **린트 및 검증** — 정적 분석, 포맷 검사, IaC 검증
2. **테스트** — 커버리지 보고와 함께 단위 및 통합 테스트
3. **빌드** — 아티팩트 컴파일, 패키징 또는 컨테이너화
4. **보안 스캔** — 의존성 감사, 컨테이너 스캐닝, SAST
5. **배포 (환경별)** — 스테이징 및 프로덕션에 대한 환경 승인이 포함된 게이트 배포

## 시크릿 관리

- 파이프라인 파일에 시크릿, 토큰 또는 비밀번호를 절대 하드코딩하지 않습니다.
- 플랫폼의 네이티브 시크릿 저장소(GitHub Secrets, Azure Key Vault, AWS Secrets Manager)를 사용합니다.
- 시크릿을 정기적으로 로테이션하고 접근 로그를 감사합니다.
- 로그에서 시크릿 값을 마스킹합니다. 자격 증명이 포함된 로그 출력은 보안 인시던트로 처리합니다.

## 캐싱

- 잠금 파일 해시에 키가 지정된 의존성 설치(node_modules, pip 패키지, Maven/Gradle 캐시)를 캐시합니다.
- 안전한 경우 빌드 출력을 캐시합니다 — 소스가 변경되면 무효화합니다.
- 시크릿 또는 환경별 구성이 포함된 아티팩트는 캐시하지 않습니다.

## 작업 설계

- 작업을 집중적으로 유지합니다: 하나의 작업 = 하나의 관심사.
- 순차적 순서에 의존하지 않고 작업 간 명시적 `needs:` 의존성을 사용합니다.
- 중단된 러너가 할당량을 소비하는 것을 방지하기 위해 모든 작업에 타임아웃을 설정합니다.
- `finally`/`always` 단계에서 항상 임시 자격 증명과 임시 리소스를 정리합니다.

## 환경 게이트

- 프로덕션 배포에는 수동 승인 단계가 필요합니다.
- 환경 보호 규칙을 사용하여 배포를 승인할 수 있는 사람을 제한합니다.
- 추적성을 위해 모든 프로덕션 배포에 커밋 SHA와 타임스탬프를 태깅합니다.

## 알림

- 모든 브랜치에서 실패 시 알림; main/release 브랜치에서만 성공 시 알림.
- 알림에 실패한 단계, 브랜치 이름, 실행에 대한 직접 링크를 포함합니다.
