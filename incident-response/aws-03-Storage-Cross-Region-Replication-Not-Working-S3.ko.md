---
category: incident-response
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/AWS%20Playbooks/03-Storage/Cross-Region-Replication-Not-Working-S3.md)'
role: SRE / AWS Incident Response
origin: scoutflo
extract_date: 2026-03-05
tags:
- backup
- cloudwatch
- cross
- iam
- incident-response
- k8s-service
- kms
- region
- replication
- s3
- storage
- sts
- working
---

# S3 Cross-Region Replication Not Working - S3 교차 리전 복제 미작동

## 의미

S3 교차 리전 복제가 작동하지 않는 현상(복제 실패 또는 S3ReplicationFailed 경보 트리거)은 복제 구성이 누락되었거나 잘못되었거나, IAM 역할 권한이 부족하거나, 소스 및 대상 버킷이 잘못 구성되었거나, 복제 상태가 실패를 표시하거나, 복제 규칙이 객체 필터와 일치하지 않거나, S3 버킷 버전 관리가 비활성화되어 복제가 불가능할 때 발생합니다.
 S3 객체가 대상 리전으로 복제되지 않고, 데이터 중복성이 상실되며, 교차 리전 백업이 실패합니다. 이는 스토리지 및 데이터 보호 계층에 영향을 미치며 재해 복구를 손상시킵니다. 일반적으로 복제 구성 문제, 권한 문제 또는 버킷 구성 오류가 원인이며, 암호화와 함께 S3 복제를 사용하는 경우 KMS 키 구성이 복제에 영향을 미칠 수 있고 애플리케이션이 교차 리전 중복성 누락의 영향을 받을 수 있습니다.

## 영향

S3 객체가 대상 리전으로 복제되지 않습니다. 데이터 중복성이 상실됩니다. 교차 리전 백업이 실패합니다. 복제 지연이 증가합니다. 복제 상태에 오류가 표시됩니다. 재해 복구 기능이 손상됩니다. 데이터 동기화가 실패합니다. 복제 자동화가 효과가 없습니다. S3ReplicationFailed 경보가 발생할 수 있으며, 암호화와 함께 S3 복제를 사용하는 경우 KMS 키 구성이 복제에 영향을 미칠 수 있습니다. 교차 리전 중복성 누락으로 애플리케이션이 영향을 받을 수 있으며, 재해 복구 기능이 손상될 수 있습니다.

## 플레이북

1. S3 소스 버킷 `<source-bucket-name>`이 존재하고 리전 `<region>`의 S3 AWS 서비스 상태가 정상인지 확인합니다.
2. 리전 `<region>`의 S3 버킷 `<source-bucket-name>`을 조회하여 복제 구성, 복제 규칙, 대상 버킷 설정, 복제 상태를 점검하고, 복제가 활성화되어 있는지 검증합니다.
3. S3 복제에 사용되는 IAM 역할 `<role-name>`을 조회하여 소스 및 대상 버킷에 대한 복제 작업 정책 권한을 점검하고, IAM 권한을 검증합니다.
4. S3 서버 접근 로그가 포함된 CloudWatch Logs 로그 그룹에서 버킷 `<source-bucket-name>` 관련 복제 실패 이벤트나 오류 패턴을 필터링하여 복제 오류 세부 정보를 확인합니다.
5. S3 버킷 `<source-bucket-name>`의 CloudWatch 지표(ReplicationLatency, ReplicationBytes)를 최근 24시간 동안 조회하여 복제 패턴을 파악하고, 복제 지표를 분석합니다.
6. 소스 버킷 `<source-bucket-name>`에서 복제되어야 할 S3 객체를 나열하고 복제 상태와 실패 사유를 확인하여 객체 복제 상태를 분석합니다.
7. S3 버킷 `<source-bucket-name>`의 버전 관리 구성을 조회하여 버전 관리가 활성화되어 있는지 확인하고, 버전 관리가 복제에 영향을 미치는지 점검합니다.
8. 대상 리전의 S3 버킷 `<destination-bucket-name>`을 조회하여 버킷이 존재하고 복제 권한이 있는지 확인하고, 대상 버킷 구성을 점검합니다.
9. CloudTrail 이벤트가 포함된 CloudWatch Logs 로그 그룹에서 최근 24시간 이내 소스 버킷 `<source-bucket-name>` 관련 S3 복제 구성 또는 IAM 역할 정책 변경 이벤트를 필터링하여 구성 변경 사항을 확인합니다.

## 진단

1. S3 복제의 CloudWatch 지표(플레이북 5단계)를 분석하여 ReplicationLatency 및 ReplicationBytes를 포함한 복제 패턴을 파악합니다. 지표에서 ReplicationBytes가 0이면 복제가 전혀 발생하지 않고 있는 것입니다. ReplicationLatency가 증가하면 복제 대기 중인 객체 백로그가 있을 수 있습니다.

2. S3 서버 접근 로그와 CloudTrail 이벤트가 포함된 CloudWatch Logs(플레이북 4단계 및 6단계)를 검토하여 구체적인 복제 실패 오류를 파악합니다. 오류가 "AccessDenied"를 나타내면 즉시 IAM 권한 검증으로 진행합니다. 오류가 대상 버킷 문제를 나타내면 대상 버킷 구성을 확인합니다.

3. 접근 거부 오류의 경우, S3 복제에 사용되는 IAM 역할 권한(플레이북 3단계)을 검증합니다. 복제 역할에는 소스 및 대상 버킷 모두에 대해 s3:GetObjectVersionForReplication, s3:ReplicateObject, s3:ReplicateDelete 권한이 필요합니다. KMS 암호화를 사용하는 경우 역할에 소스에 대한 kms:Decrypt와 대상에 대한 kms:Encrypt도 필요합니다.

4. 소스 버킷 버전 관리 구성(플레이북 7단계)을 확인하여 버전 관리가 활성화되어 있는지 확인합니다. S3 교차 리전 복제는 소스 및 대상 버킷 모두에서 버전 관리가 활성화되어야 합니다. 버전 관리가 비활성화되거나 일시 중지되면 복제가 작동할 수 없습니다.

5. 복제 구성(플레이북 2단계)을 확인하여 대상 버킷, 규칙 상태, 필터 기준을 포함한 복제 규칙이 올바르게 정의되어 있는지 검증합니다. 규칙이 접두사 또는 태그 필터를 사용하는 경우 객체가 필터 기준과 일치하는지 확인합니다.

6. 대상 버킷 구성(플레이북 8단계)을 확인하여 대상 버킷이 존재하고 접근 가능한지 검증합니다. 대상 버킷이 존재하지 않거나, 삭제되었거나, 복제 역할에 쓰기 권한이 없으면 복제가 실패합니다.

7. 복제되어야 할 특정 객체의 객체 복제 상태(플레이북 6단계)를 검토합니다. 복제 상태가 "FAILED"이면 실패 사유를 확인합니다. 상태가 "PENDING"이면 백로그나 일시적 지연이 있을 수 있습니다.

8. CloudTrail 이벤트(플레이북 9단계)와 복제 실패 타임스탬프를 30분 이내로 상관 분석하여 IAM 역할 정책 또는 복제 구성 변경을 파악합니다. 권한 변경이 복제가 중단된 시점과 일치하면 해당 변경이 원인일 가능성이 높습니다.

상관관계를 찾을 수 없는 경우: 기간을 30일로 확장하고, 복제 규칙 상태 및 대상 버킷 구성을 포함한 대안적 증거 소스를 검토하고, 대상 버킷 접근 문제나 복제 역할 권한 드리프트와 같은 점진적 문제를 확인하고, 교차 리전 네트워크 연결이나 대상 버킷 권한과 같은 외부 종속성을 검증하고, 복제 실패의 과거 패턴을 점검하고, S3 버킷 버전 관리 요구사항을 확인하고, KMS 암호화 키 구성과 함께 S3 복제를 검증합니다.