---
category: incident-response
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/AWS%20Playbooks/03-Storage/Failing-Due-to-S3-Permissions-CodePipeline.md)'
role: SRE / AWS Incident Response
origin: scoutflo
extract_date: 2026-03-05
tags:
- cloudformation
- cloudwatch
- codepipeline
- failing
- iam
- incident-response
- k8s-deployment
- k8s-service
- kms
- performance
- permissions
- pipeline
- s3
- storage
- sts
---

# CodePipeline Failing Due to S3 Permissions - S3 권한으로 인한 CodePipeline 실패

## 의미

AWS CodePipeline이 실행 중 실패하는 현상(파이프라인 실행 실패 또는 CodePipelineExecutionFailed 경보 트리거)은 파이프라인 실행 이력에 스테이지 실패가 표시되거나, CodeBuild 로그에 오류가 표시되거나, IAM 역할 권한이 부족하거나, 파이프라인 역할에 필요한 정책이 없거나, S3 버킷 권한이 파이프라인 작업을 차단하거나, KMS 키 정책이 아티팩트 암호화를 방해할 때 발생합니다.
 파이프라인 실행 이력에 실패한 스테이지가 표시되고, CodeBuild 로그에 권한 거부 오류가 표시되며, S3 접근 로그에 접근 실패가 표시됩니다. 이는 CI/CD 계층에 영향을 미치며 배포를 차단합니다. 일반적으로 IAM 권한 문제, S3 버킷 정책 제한, KMS 키 접근 문제 또는 교차 계정 접근 구성이 원인이며, 파이프라인이 인프라를 관리하는 경우 CloudFormation 스택 배포가 실패할 수 있고 애플리케이션에서 배포 지연이 발생할 수 있습니다.

## 영향

CodePipeline 실행이 실패합니다. CI/CD 워크플로우가 중단됩니다. 파이프라인 스테이지를 완료할 수 없습니다. CodeBuild 오류가 발생합니다. 배포 파이프라인이 실패합니다. 애플리케이션 배포가 차단됩니다. 파이프라인 실행 이력에 실패가 표시됩니다. 빌드 아티팩트를 저장할 수 없습니다. 릴리스 프로세스가 중단됩니다. CodePipelineExecutionFailed 경보가 발생합니다. 빌드 아티팩트를 S3에 업로드할 수 없습니다. 배포 스테이지가 타임아웃됩니다. 파이프라인이 인프라를 관리하는 경우 CloudFormation 스택 배포가 실패하고 인프라 변경을 적용할 수 없습니다. 실패한 배포로 인해 애플리케이션에서 오류나 성능 저하가 발생할 수 있습니다.

## 플레이북

1. 파이프라인 `<pipeline-name>`이 존재하고 리전 `<region>`의 CodePipeline AWS 서비스 상태가 정상인지 확인합니다.
2. CodePipeline `<pipeline-name>`을 조회하고 실행 이력을 확인하여 문제를 유발하는 스테이지(Source, Build, Deploy)를 파악합니다.
3. CodeBuild 로그가 포함된 CloudWatch Logs 로그 그룹에서 빌드 오류, 권한 실패 또는 실행 실패를 필터링하여 S3 접근 거부 오류를 확인합니다.
4. CodePipeline 서비스 역할 및 실행 역할의 IAM 역할 `<role-name>`을 조회하여 서비스 역할 권한에 Pipeline Role(AWSCodePipelineServiceRole)에 필요한 정책이 포함되어 있는지, 실행 역할에 아티팩트 버킷 접근 및 배포 작업 권한이 있는지 검증합니다.
5. S3 버킷 `<bucket-name>`의 버킷 정책을 조회하여 CodePipeline 접근을 위한 S3 버킷 권한을 확인하고, 버킷 정책이 파이프라인 서비스 역할과 실행 역할을 허용하는지 검증하며, 충돌하는 Deny 문을 점검합니다.
6. S3 버킷이 암호화를 사용하는 경우 KMS 키 `<key-id>` 키 정책을 조회하여 KMS 키 정책이 CodePipeline 서비스 역할과 실행 역할이 암호화/복호화에 키를 사용할 수 있도록 허용하는지 검증합니다.
7. CodePipeline `<pipeline-name>`의 실행 상태를 조회하여 현재 실행 상태와 실패한 스테이지 세부 정보를 확인하고, 아티팩트 위치 및 암호화 설정을 점검합니다.
8. 파이프라인 `<pipeline-name>`이 교차 계정 S3 접근을 사용하는지 확인하기 위해 버킷 정책의 교차 계정 역할 가정 및 신뢰 관계를 점검합니다.

## 진단

1. 플레이북 1단계의 AWS 서비스 상태를 분석하여 리전의 CodePipeline 서비스 가용성을 확인합니다. 서비스 상태에 문제가 있으면 파이프라인 실패는 구성 변경이 아닌 모니터링이 필요한 AWS 측 문제일 수 있습니다.

2. 플레이북 2단계의 실행 이력에서 어떤 특정 스테이지가 실패했는지(Source, Build, Deploy) 표시되면 해당 스테이지에 조사를 집중합니다. 초기 실패 타임스탬프에 대한 실행 세부 정보의 실패 사유를 확인합니다.

3. 플레이북 3단계의 CodeBuild 로그에서 S3 작업에 대한 "Access Denied" 또는 "AccessDenied" 오류가 표시되면 실행 역할에 S3 권한이 부족한 것입니다. 실패한 구체적인 S3 작업(GetObject, PutObject, ListBucket)을 파악합니다.

4. 플레이북 4단계의 IAM 역할 정책에 아티팩트 버킷에 필요한 S3 권한이 포함되어 있지 않으면 서비스 역할이 파이프라인 아티팩트에 접근할 수 없습니다. 파이프라인 서비스 역할과 실행 역할 모두 적절한 S3 권한이 있는지 확인합니다.

5. 플레이북 5단계의 S3 버킷 정책에 명시적 Deny 문이 포함되어 있거나 파이프라인 역할을 Allow하지 않으면 버킷 정책이 접근을 차단하고 있는 것입니다. IAM 권한을 재정의하는 충돌하는 Deny 문을 확인합니다.

6. 플레이북 6단계의 KMS 키 정책이 파이프라인 역할에 kms:Encrypt, kms:Decrypt, kms:GenerateDataKey 사용을 허용하지 않으면 암호화된 아티팩트를 처리할 수 없습니다. KMS 키 부여에 실행 역할이 포함되어 있는지 확인합니다.

7. 플레이북 7단계의 실행 상태에서 파이프라인이 아티팩트 위치에서 멈춰 있으면 S3 경로가 존재하고 파이프라인 구성과 버킷 간 암호화 설정이 일치하는지 확인합니다.

8. 플레이북 8단계의 교차 계정 구성에서 교차 계정 S3 접근이 표시되면 버킷 정책이 교차 계정 접근을 허용하고 가정하는 역할에 적절한 신뢰 관계가 있는지 모두 확인합니다.

상관관계를 찾을 수 없는 경우: CodeBuild 로그 쿼리 기간을 24시간으로 확장하고, 소스 리포지토리(CodeCommit, GitHub) 연결을 확인하고, 아티팩트 조회에 영향을 미칠 수 있는 S3 버킷 버전 관리를 점검하고, 아티팩트를 조기에 삭제할 수 있는 버킷 수명 주기 정책을 확인합니다. 파이프라인 실패는 소스 제어 웹훅 문제, CodeBuild 타임아웃 설정 또는 S3 접근을 제한하는 VPC 엔드포인트 정책으로 인해 발생할 수 있습니다.