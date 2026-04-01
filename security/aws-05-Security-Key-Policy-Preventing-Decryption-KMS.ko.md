---
category: security
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/AWS%20Playbooks/05-Security/Key-Policy-Preventing-Decryption-KMS.md)'
role: SRE / AWS Incident Response
origin: scoutflo
extract_date: 2026-03-05
tags:
- cloudwatch
- decryption
- iam
- k8s-service
- kms
- performance
- policy
- preventing
- rds
- s3
- security
- sts
---

# KMS 키 정책으로 인한 복호화 차단 — AWS KMS Key Policy Preventing Decryption

## 의미

KMS 키 복호화 작업이 실패합니다(복호화 오류 또는 KMSAccessDenied 예외 발생). 원인으로는 KMS 키 정책이 접근을 차단하거나, IAM 역할 또는 사용자에게 kms:Decrypt 및 kms:Encrypt 권한이 없거나, 키를 사용하는 주체가 키 정책에 나열되지 않았거나, 키가 비활성화되었거나, 리소스 정책에서 교차 계정 접근이 허용되지 않거나, 키 별칭이 잘못된 키를 가리키는 경우입니다. KMS API 호출이 "AccessDenied" 또는 "InvalidKeyUsageException" 오류를 반환하고, CloudWatch Logs에서 KMS 권한 오류가 확인되며, 암호화된 리소스에 접근할 수 없습니다. 이는 보안 및 암호화 계층에 영향을 미치며 데이터 접근을 차단합니다. 일반적으로 키 정책 제한, IAM 권한 문제, 키 별칭 설정 오류, 교차 계정 접근 문제가 원인이며, 멀티 리전 키를 사용하는 경우 키 복제 문제가 복호화에 영향을 줄 수 있고 애플리케이션에서 암호화 관련 오류가 발생할 수 있습니다.

## 영향

KMS 복호화 작업 실패, 암호화된 데이터 접근 불가, kms:Decrypt 권한 오류 발생, 암호화 및 복호화 작업 오류, 데이터 접근 차단, 암호화된 리소스 접근 불가, KMS 키 정책 오류 발생, 교차 계정 접근 실패, 암호화 워크플로우 중단. 암호화된 S3 객체 조회 불가, 암호화된 RDS 스냅샷 복원 불가, 암호화된 EBS 볼륨 연결 불가. 암호화 실패로 인해 애플리케이션 오류나 성능 저하 발생 가능. 멀티 리전 키를 사용하는 경우 교차 리전 복호화가 실패할 수 있습니다.

## 플레이북

1. KMS 키 `<key-id>`의 존재를 확인하고 삭제 예약 상태가 아닌지 확인하며, 리전 `<region>`의 KMS AWS 서비스 상태가 정상인지 확인합니다.
2. KMS 키 `<key-id>`의 키 정책을 조회하여 접근 제한을 확인하고 주체 ARN 및 액션 권한(kms:Decrypt, kms:Encrypt, kms:ReEncrypt)을 확인합니다.
3. KMS 키 `<key-id>`의 별칭 구성을 조회하여 키 별칭이 올바른 키 ID를 가리키는지 확인하고 별칭 설정 오류를 확인합니다.
4. IAM 역할 `<role-name>` 또는 사용자 `<user-name>`을 조회하여 IAM 역할 또는 사용자가 IAM 정책에서 kms:Decrypt 및 kms:Encrypt 권한을 가지고 있는지 확인하고 정책 평가 순서 문제를 확인합니다.
5. KMS 키 `<key-id>`의 키 정책을 조회하여 키를 사용하는 주체가 키 정책에 나열되어 있는지 확인하고 주체 ARN 형식 불일치를 확인합니다.
6. KMS 키 `<key-id>`의 상태를 조회하여 키가 활성화되어 있는지 확인하고 키 상태가 "Disabled" 또는 "PendingDeletion"이 아닌지 확인합니다.
7. KMS 키 `<key-id>`의 리소스 정책, 그랜트, 키 교체 상태를 조회하여 리소스 정책에 교차 계정 접근이 구성되어 있는지 확인하고, 그랜트 기반 접근 권한을 확인하고, 키 교체가 키 정책이나 키 ID에 영향을 미쳤는지 확인합니다. 교차 계정 주체 ARN, 신뢰 관계, 그랜트가 키 정책 제한을 오버라이드하는지, 교체 관련 정책 변경을 확인합니다.
8. CloudTrail 이벤트가 포함된 CloudWatch Logs 로그 그룹을 조회하여 키 `<key-id>`와 관련된 KMS API 호출 실패를 필터링하고 AccessDenied 오류를 포함합니다.

## 진단

1. 플레이북 1단계의 AWS 서비스 상태를 분석하여 해당 리전의 KMS 서비스 가용성을 확인합니다. 서비스 상태에 문제가 있으면 복호화 실패는 구성 변경이 아닌 AWS 측 문제로 모니터링이 필요합니다.

2. 플레이북 6단계의 키 상태가 "Disabled" 또는 "PendingDeletion"이면 키를 어떤 작업에도 사용할 수 없습니다. 키를 다시 활성화하거나 삭제를 취소하여 접근을 복원합니다.

3. 플레이북 2단계의 키 정책에 요청 주체(IAM 사용자, 역할, 서비스)가 허용된 주체에 포함되지 않으면 키 접근이 거부됩니다. 주체 ARN 형식이 정확히 일치하는지 확인합니다(계정 ID, 역할/사용자 이름).

4. 플레이북 2단계의 키 정책이 요청에서 충족되지 않는 특정 조건(예: kms:ViaService, kms:CallerAccount)을 통해서만 접근을 허용하는 경우, 조건부 접근이 작업을 차단하고 있습니다.

5. 플레이북 4단계의 IAM 정책에 특정 키 ARN에 대한 kms:Decrypt 및 kms:Encrypt 권한이 포함되지 않으면, 키 정책이 평가되기 전에 IAM이 작업을 거부합니다.

6. 플레이북 3단계의 키 별칭이 예상과 다른 키 ID를 가리키면, 별칭을 사용하는 애플리케이션이 잘못된 키에 접근하고 있습니다. 별칭 대상이 의도한 키와 일치하는지 확인합니다.

7. 플레이북 7단계의 키 정책, 그랜트, 교체 상태에서 교차 계정 접근 요구사항이 확인되면, 키 정책이 외부 계정을 허용하고 외부 계정의 IAM 정책이 KMS 접근을 허용하는지 모두 확인합니다. 그랜트의 경우 그랜트 토큰이 올바르게 사용되고 있는지 확인합니다.

8. 플레이북 8단계의 CloudTrail 이벤트에서 특정 AccessDenied 오류 코드가 확인되면, 오류 컨텍스트가 거부가 키 정책, IAM 정책, VPC 엔드포인트 정책 중 어디에서 발생했는지 나타냅니다.

수집된 데이터에서 상관관계가 발견되지 않는 경우: CloudTrail 쿼리 기간을 1시간으로 확장하고, 키 교체가 예기치 않게 키 자료를 변경하지 않았는지 확인하고, KMS 접근을 제한하는 VPC 엔드포인트 정책을 확인하고, 멀티 리전 키 복제 상태를 조사합니다. 복호화 실패는 키 정책 크기 제한(32 KB), 그랜트 제한, 교차 계정 STS 세션 정책 제한으로 인해 발생할 수 있습니다.
