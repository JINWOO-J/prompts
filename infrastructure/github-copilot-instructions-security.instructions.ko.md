---
category: infrastructure
source: '[shawnewallace/prompt-library](https://github.com/shawnewallace/prompt-library/blob/main/scenarios/devops-infrastructure/github-copilot/instructions/security.instructions.md)'
role: DevOps / Infrastructure Engineer
origin: shawnewallace
extract_date: 2026-03-05
tags:
- copilot
- docker
- github
- iam
- infrastructure
- k8s-ingress
- k8s-secret
- k8s-service
- kubernetes
- logging
- pipeline
- rds
- security
- security.instructions
- terraform
---

---
applyTo: '**/*.tf,**/*.yml,**/*.yaml,**/Dockerfile'
---

# 보안

## 시크릿

- 소스 코드나 파이프라인 파일에 시크릿, API 키, 비밀번호 또는 토큰을 절대 넣지 않습니다.
- 시크릿 매니저(HashiCorp Vault, AWS Secrets Manager, Azure Key Vault, GCP Secret Manager)를 사용하고 런타임에 주입합니다.
- 자격 증명을 정기적으로 로테이션합니다. 커밋된 시크릿은 즉시 손상된 것으로 처리합니다: PR을 닫기 전에 로테이션합니다.
- 실수로 커밋하는 것을 방지하기 위해 pre-commit 훅에서 `git-secrets` 또는 `trufflehog`를 실행합니다.

## IAM 및 권한

- 모든 IAM 역할, 서비스 계정, 정책에 최소 권한을 적용합니다. 필요한 권한만 부여합니다.
- 프로덕션 IAM 정책에서 와일드카드 리소스 ARN(`*`)을 절대 사용하지 않습니다.
- 워크로드별 별도의 서비스 계정을 사용합니다 — 서비스 간 자격 증명을 절대 공유하지 않습니다.
- IAM 정책을 수정하는 모든 PR에서 IAM 정책을 감사합니다.

## 네트워크

- 기본적으로 모든 인그레스를 거부하고 필요한 포트만 허용합니다.
- 관리 포트(SSH, RDP)를 알려진 CIDR 범위 또는 배스천 호스트로 제한합니다. `0.0.0.0/0`에 절대 노출하지 않습니다.
- TLS 1.2+로 전송 중인 모든 트래픽을 암호화합니다. HTTPS 리다이렉트를 적용합니다.
- 가능한 경우 클라우드 서비스에 프라이빗 엔드포인트를 사용합니다.

## 인프라 스캐닝

- CI에서 모든 Terraform 변경에 `tfsec` 또는 `checkov`를 실행합니다. HIGH/CRITICAL 발견 시 머지를 차단합니다.
- 레지스트리에 푸시하기 전에 컨테이너 이미지에 `trivy` 또는 `grype`를 실행합니다.
- 애플리케이션 의존성에 `npm audit` / `pip audit` / 동등한 도구를 실행합니다.

## 컨테이너

- 최소 베이스 이미지(distroless, alpine)를 사용합니다. `latest` 태그를 피합니다 — 특정 다이제스트에 고정합니다.
- 컨테이너를 비루트로 실행합니다. Dockerfile에 `USER`를 설정합니다.
- CI에서 CVE에 대해 이미지를 스캔합니다. 심각한 취약점 시 차단합니다.
- 절대적으로 필요한 경우가 아니면 컨테이너에 Docker 소켓을 마운트하지 않습니다.

## 로깅 및 감사

- 모든 클라우드 계정과 Kubernetes 클러스터에 감사 로깅을 활성화합니다.
- 로그를 중앙화하고 보존 정책을 설정합니다.
- 의심스러운 활동에 대해 알림합니다: 반복된 인증 실패, 권한 상승, 예상치 못한 API 호출.
