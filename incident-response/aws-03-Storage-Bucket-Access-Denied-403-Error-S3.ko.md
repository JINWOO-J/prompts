---
category: incident-response
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/AWS%20Playbooks/03-Storage/Bucket-Access-Denied-403-Error-S3.md)'
role: SRE / AWS Incident Response
origin: scoutflo
extract_date: 2026-03-05
tags:
- access
- backup
- bucket
- cloudfront
- cloudwatch
- denied
- iam
- incident-response
- k8s-service
- performance
- s3
- storage
- sts
---

# S3 Bucket Access Denied (403 Error) - S3 버킷 접근 거부 (403 오류)

## 의미

S3 버킷 접근 요청이 403 Forbidden 오류를 반환하는 현상(접근 거부 이벤트 또는 S3BucketAccessDenied 경보 트리거)은 버킷 정책에 Deny 문이 포함되어 있거나, IAM 사용자 또는 역할 권한이 부족하거나, 버킷 퍼블릭 접근 설정이 접근을 차단하거나, 잘못된 AWS 리전이 사용되거나, 리소스 기반 정책이 자격 증명 기반 정책과 충돌하거나, S3 객체 소유권 설정이 접근을 제한하거나, AWS Organizations SCP가 권한을 재정의할 때 발생합니다.
 S3 객체 조회가 실패하고, 애플리케이션이 저장된 데이터에 접근할 수 없으며, CloudWatch Logs에 403 오류가 표시됩니다. 이는 스토리지 및 접근 제어 계층에 영향을 미치며 데이터 접근을 차단합니다. 일반적으로 정책 구성 문제, 퍼블릭 접근 차단 설정 또는 SCP 제한이 원인이며, CloudFront와 함께 S3를 사용하는 경우 OAI/OAC 구성이 접근에 영향을 미칠 수 있고 애플리케이션에서 데이터 접근 실패가 발생할 수 있습니다.

## 영향

S3 객체 조회가 실패합니다. 애플리케이션이 저장된 데이터에 접근할 수 없습니다. 파일 업로드가 차단됩니다. 버킷 작업이 실패합니다. 애플리케이션 로그에 403 Forbidden 오류가 나타납니다. 접근 거부 이벤트가 발생합니다. 데이터 접근이 완전히 차단됩니다. 사용자 대면 기능이 실패합니다. 백업 및 복원 작업을 완료할 수 없습니다. S3BucketAccessDenied 경보가 발생합니다. CloudFront와 함께 S3를 사용하는 경우 OAI/OAC 구성이 접근에 영향을 미칠 수 있습니다. 데이터 접근 실패로 인해 애플리케이션에서 오류나 성능 저하가 발생할 수 있으며, 서비스 간 데이터 접근이 차단될 수 있습니다.

## 플레이북

1. S3 버킷 `<bucket-name>`과 IAM 사용자 `<user-name>` 또는 역할 `<role-name>`이 존재하고, 리전 `<region>`의 S3 AWS 서비스 상태가 정상인지 확인합니다.
2. S3 버킷 `<bucket-name>`의 버킷 정책과 사용자 `<user-name>` 또는 역할 `<role-name>`에 연결된 IAM 정책 `<policy-name>`을 조회하여 버킷 정책의 Deny 문을 점검하고, IAM 정책에 s3:GetObject 및 s3:ListBucket 권한이 있는지 확인하며, IAM 정책 대 버킷 정책 평가 순서를 검증합니다.
5. S3 버킷 `<bucket-name>`의 퍼블릭 접근 차단 구성을 조회하여 퍼블릭 접근 설정을 확인합니다.
6. S3 버킷 `<bucket-name>`의 객체 소유권 구성을 조회하여 객체 소유권 설정(BucketOwnerEnforced vs BucketOwnerPreferred)을 확인하고, 소유권 제한을 점검합니다.
7. 버킷 `<bucket-name>`의 버킷 리전 구성을 조회하여 올바른 AWS 리전 `<region>`이 사용되고 있는지 확인하고, 리전 불일치를 점검합니다.
8. Organizations를 사용하는 경우 AWS Organizations 서비스 제어 정책(SCP)을 조회하여 SCP가 S3 접근 권한을 재정의하고 있지 않은지 확인합니다.
9. S3 버킷 `<bucket-name>`의 암호화 구성을 조회하여 암호화를 사용하는 경우 KMS 키 권한을 확인합니다.
10. CloudFront를 사용하는 경우 CloudFront 로그가 포함된 CloudWatch Logs 로그 그룹에서 S3 버킷 `<bucket-name>` 관련 403 오류를 필터링하여 CloudFront 오리진 접근 로그를 확인합니다.

## 진단

1. 플레이북 1단계의 AWS 서비스 상태를 분석하여 리전의 S3 서비스 가용성을 확인합니다. 서비스 상태에 문제가 있으면 403 오류는 구성 변경이 아닌 모니터링이 필요한 AWS 측 문제일 수 있습니다.

2. 플레이북 2단계의 버킷 정책에 요청 주체와 일치하는 명시적 Deny 문이 포함되어 있으면 버킷 정책이 접근을 차단하고 있는 것입니다. 구체적인 Deny 문과 생성 타임스탬프를 파악합니다.

3. 플레이북 2단계의 IAM 정책에 버킷 리소스에 대한 s3:GetObject 또는 s3:ListBucket 권한이 없으면 자격 증명 기반 정책이 부족한 것입니다. 정책 연결 상태와 권한 범위를 확인합니다.

4. 플레이북 5단계의 퍼블릭 접근 차단 구성에서 BlockPublicAccess가 활성화되어 있으면 접근 패턴이 퍼블릭 접근을 필요로 하는지 확인합니다. 퍼블릭 접근 차단은 퍼블릭 접근을 허용하는 버킷 정책을 재정의합니다.

5. 플레이북 6단계의 객체 소유권 구성에서 BucketOwnerEnforced가 표시되면 ACL 기반 접근이 비활성화됩니다. 교차 계정 접근에 ACL을 사용하는 애플리케이션은 403 오류를 받게 됩니다.

6. 플레이북 7단계의 버킷 리전이 요청에 사용된 리전과 다르면 리전 불일치로 접근 실패가 발생합니다. S3 요청은 올바른 리전 엔드포인트를 대상으로 해야 합니다.

7. 플레이북 8단계의 SCP에 S3 Deny 문이 포함되어 있으면 조직 정책이 IAM 권한을 재정의합니다. 접근을 차단하는 구체적인 SCP를 파악합니다.

8. 플레이북 9단계의 암호화 구성에서 KMS 암호화가 표시되고 요청 주체에 키에 대한 kms:Decrypt 권한이 없으면 암호화된 객체에 접근할 수 없습니다.

9. 플레이북 10단계의 CloudFront 로그에서 403 오류가 표시되면 OAI/OAC 구성을 확인합니다. 잘못 구성된 오리진 접근 설정으로 인해 CloudFront가 S3에서 403을 받습니다.

상관관계를 찾을 수 없는 경우: 기간을 1시간으로 확장하고, 교차 계정 접근 구성을 검토하고, S3 버킷 MFA 삭제 요구사항을 확인하고, 객체 가용성에 영향을 미칠 수 있는 버킷 수명 주기 정책을 점검합니다. 403 오류는 VPC 엔드포인트 정책, 교차 계정 신뢰 문제 또는 임시 자격 증명 만료로 인해 발생할 수 있습니다.