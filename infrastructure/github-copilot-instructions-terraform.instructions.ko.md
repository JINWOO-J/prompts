---
category: infrastructure
source: '[shawnewallace/prompt-library](https://github.com/shawnewallace/prompt-library/blob/main/scenarios/devops-infrastructure/github-copilot/instructions/terraform.instructions.md)'
role: DevOps / Infrastructure Engineer
origin: shawnewallace
extract_date: 2026-03-05
tags:
- compute
- copilot
- database
- dynamodb
- github
- infrastructure
- k8s-deployment
- k8s-secret
- networking
- s3
- terraform
- terraform.instructions
---

---
applyTo: '**/*.tf'
---

# Terraform

## 모듈 구조

- 인프라를 재사용 가능한 모듈로 조직합니다. 각 모듈에는 `main.tf`, `variables.tf`, `outputs.tf`, `README.md`가 있어야 합니다.
- 루트 구성은 모듈을 호출합니다. 리소스 정의를 직접 포함하지 않습니다.
- 일관된 디렉토리 레이아웃을 사용합니다:

```
infrastructure/
  modules/
    networking/
    compute/
    database/
  environments/
    dev/
    staging/
    prod/
```

## 원격 상태

- 항상 원격 상태(S3 + DynamoDB 잠금, Azure Blob, GCS 또는 Terraform Cloud)를 사용합니다. `.tfstate` 파일을 절대 커밋하지 않습니다.
- 환경별 별도의 상태 파일을 사용합니다. 환경 간 상태를 절대 공유하지 않습니다.
- 저장 시 상태 암호화를 활성화합니다.

## 변수 및 값

- 환경별 값(계정 ID, 리전 이름, CIDR 블록, 시크릿)을 절대 하드코딩하지 않습니다. `variables.tf`를 사용합니다.
- 모든 변수에 설명과 타입을 제공합니다. 제한된 입력에 validation 블록을 사용합니다.
- 계산되거나 반복되는 값에 `locals`를 사용합니다. 표현식 중복을 피합니다.

```hcl
variable "environment" {
  type        = string
  description = "Deployment environment (dev, staging, prod)"
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod."
  }
}
```

## 태깅

- 모든 리소스에 일관된 태그를 적용합니다: 최소한 `environment`, `project`, `managed-by = terraform`, `owner`.
- 공통 태그 맵에 `locals` 블록을 사용하고 리소스별 태그와 병합합니다.

```hcl
locals {
  common_tags = {
    environment = var.environment
    project     = var.project_name
    managed-by  = "terraform"
  }
}
```

## 스타일

- 커밋 전에 `terraform fmt`를 사용합니다. CI에서 포맷되지 않은 코드를 거부해야 합니다.
- pre-commit 훅에서 `terraform validate`와 `tflint`를 사용합니다.
- 의미 있는 키가 있는 리소스에 `count` 대신 `for_each`를 선호합니다 (인덱스 기반 드리프트 방지).
- `required_providers`에서 프로바이더 버전을 고정하고 `required_version`으로 Terraform 자체를 고정합니다.
