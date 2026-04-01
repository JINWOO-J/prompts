---
category: infrastructure
source: '[shawnewallace/prompt-library](https://github.com/shawnewallace/prompt-library/blob/main/scenarios/devops-infrastructure/claude-code/commands/review-iac.md)'
role: DevOps / Infrastructure Engineer
origin: shawnewallace
extract_date: 2026-03-05
tags:
- claude
- code
- commands
- database
- iam
- infrastructure
- k8s-deployment
- k8s-ingress
- k8s-secret
- pipeline
- rds
- review
- security
- storage
- terraform
---

# Infrastructure as Code 리뷰

`$ARGUMENTS`의 인프라 코드를 프로젝트의 DevOps 표준에 따라 리뷰합니다.

확인 항목:

**보안**
- [ ] 하드코딩된 시크릿, 비밀번호 또는 API 키 없음
- [ ] IAM 역할 및 정책이 최소 권한 원칙 준수 (프로덕션에서 와일드카드 리소스 ARN 없음)
- [ ] 민감한 포트에 대한 네트워크 인그레스 규칙이 `0.0.0.0/0`으로 열려 있지 않음
- [ ] 스토리지 및 데이터베이스에 저장 시 및 전송 중 암호화 활성화
- [ ] 컨테이너 이미지가 `latest`가 아닌 특정 다이제스트에 고정

**Terraform**
- [ ] 잠금이 포함된 원격 상태 구성
- [ ] 프로바이더 및 Terraform 버전 고정
- [ ] 모든 변수에 설명 및 타입 포함
- [ ] 키가 있는 리소스에 `count` 대신 `for_each` 사용
- [ ] 모든 리소스에 공통 태그 적용
- [ ] `.tf` 파일에 환경별 값 하드코딩 없음

**CI/CD**
- [ ] 파이프라인 변수가 아닌 시크릿 매니저에서 시크릿 소싱
- [ ] 잠금 파일 해시에 키가 지정된 의존성 캐시
- [ ] 프로덕션 배포에 수동 승인 필요
- [ ] 모든 작업에 타임아웃 설정
- [ ] 배포 단계 전에 보안 스캔 실행

**일반**
- [ ] `terraform fmt` / `terraform validate` 통과
- [ ] 코드에 주석 처리된 리소스 블록 없음
- [ ] 복사-붙여넣기 대신 반복 패턴에 모듈 사용

실패한 각 검사에 대해 위험을 설명하고 수정된 예시를 제공합니다.
