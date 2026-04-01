---
category: incident-response
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/AWS%20Playbooks/03-Storage/Public-Access-Block-Preventing-Access-S3.md)'
role: SRE / AWS Incident Response
origin: scoutflo
extract_date: 2026-03-05
tags:
- access
- block
- cloudfront
- cloudwatch
- iam
- incident-response
- k8s-service
- performance
- preventing
- public
- s3
- storage
- sts
---

# S3 Public Access Block Preventing Access - S3 퍼블릭 접근 차단으로 인한 접근 불가

## 의미

S3 버킷 접근이 차단되는 현상(접근 거부 오류 또는 S3PublicAccessBlocked 경보 트리거)은 Block Public Access 설정이 퍼블릭 접근을 방지하거나, 버킷 ACL이 퍼블릭 접근을 거부하거나, 버킷 정책이 접근을 제한하거나, IAM 정책이 버킷 작업에 필요한 권한을 부여하지 않거나, AWS Organizations 서비스 제어 정책이 버킷 권한을 재정의할 때 발생합니다.
 S3 버킷에 대한 퍼블릭 접근이 거부되고, 애플리케이션이 퍼블릭 객체에 접근할 수 없으며, 403 Access Denied 오류가 발생합니다. 이는 스토리지 및 접근 제어 계층에 영향을 미치며 퍼블릭 데이터 접근을 차단합니다. 일반적으로 Block Public Access 구성, 버킷 정책 제한 또는 SCP 재정의가 원인이며, CloudFront와 함께 S3를 사용하는 경우 OAI/OAC 구성이 접근에 영향을 미칠 수 있고 애플리케이션에서 데이터 접근 실패가 발생할 수 있습니다.

## 영향

S3 버킷에 대한 퍼블릭 접근이 거부됩니다. 애플리케이션이 퍼블릭 객체에 접근할 수 없습니다. 버킷 정책이 실패합니다. 403 Access Denied 오류가 발생합니다. 퍼블릭 웹사이트 호스팅이 실패합니다. 버킷 ACL 작업이 차단됩니다. 교차 계정 접근이 제한될 수 있습니다. 퍼블릭 리소스에 대한 객체 조회가 실패합니다. S3PublicAccessBlocked 경보가 발생할 수 있으며, CloudFront와 함께 S3를 사용하는 경우 OAI/OAC 구성이 접근에 영향을 미칠 수 있습니다. 차단된 퍼블릭 접근으로 인해 애플리케이션에서 오류나 성능 저하가 발생할 수 있으며, 퍼블릭 웹사이트 호스팅이 실패할 수 있습니다.

## 플레이북

1. S3 버킷 `<bucket-name>`이 존재하고 리전 `<region>`의 S3 AWS 서비스 상태가 정상인지 확인합니다.
2. 리전 `<region>`의 S3 버킷 `<bucket-name>`을 조회하여 Block Public Access 설정, 퍼블릭 접근 구성, 버킷 정책을 점검하고, 네 가지 Block Public Access 설정을 모두 검증합니다.
3. 버킷 `<bucket-name>`의 S3 버킷 정책을 조회하여 정책 문, 주체 구성, 작업 권한을 점검하고, 정책 평가 순서를 검증합니다.
4. CloudTrail 이벤트가 포함된 CloudWatch Logs 로그 그룹에서 버킷 `<bucket-name>` 관련 S3 접근 거부 이벤트를 필터링하여 퍼블릭 접근 시도 패턴을 확인합니다.
5. 버킷 `<bucket-name>`에 접근하려는 IAM 역할 `<role-name>` 또는 IAM 사용자 `<user-name>`을 조회하여 S3 작업에 대한 정책 권한을 점검하고, IAM 정책 대 버킷 정책 평가를 검증합니다.
6. Organizations를 사용하는 경우 AWS Organizations 서비스 제어 정책(SCP)을 조회하여 SCP가 S3 퍼블릭 접근 권한을 재정의하고 있지 않은지 확인합니다.
7. S3 버킷 `<bucket-name>`의 버킷 ACL 구성을 조회하여 버킷 ACL 설정을 확인하고, ACL이 퍼블릭 접근을 제한하는지 점검합니다.
8. CloudFront를 사용하는 경우 CloudFront 로그가 포함된 CloudWatch Logs 로그 그룹에서 S3 버킷 `<bucket-name>` 관련 403 오류를 필터링하여 CloudFront 오리진 접근 로그를 확인합니다.
9. 버킷 `<bucket-name>`의 S3 버킷 접근 시도를 나열하고 접근 거부 패턴이나 권한 관련 오류를 확인하여 접근 시도 패턴을 분석합니다.

## 진단

1. CloudTrail 이벤트(플레이북 4단계)를 분석하여 S3 접근 거부 이벤트가 처음 나타난 시점을 파악합니다. 이 타임스탬프가 접근 차단이 시작된 시점을 확립하고 상관관계 기준선이 됩니다.

2. 버킷 Block Public Access 설정(플레이북 2단계)에서 네 가지 설정이 모두 활성화되어 있고, 이 설정이 활성화된 후 접근 거부가 시작되었다면(플레이북 4단계의 CloudTrail 확인) Block Public Access가 의도된 접근을 직접 방해하고 있는 것입니다.

3. Block Public Access가 원인이 아닌 경우 버킷 정책(플레이북 3단계)을 확인합니다. Deny 효과가 있는 정책 문이나 요청 주체에 대한 필요한 Allow 문 누락이 접근 거부를 유발합니다.

4. 접근 거부 패턴(플레이북 4단계)이 여러 버킷에 동시에 영향을 미치면 AWS Organizations SCP(플레이북 6단계)를 확인합니다. 계정 수준 또는 조직 수준 제한이 버킷 수준 권한을 재정의할 수 있습니다.

5. IAM 정책 분석(플레이북 5단계)에서 요청하는 역할이나 사용자에게 s3:GetObject 또는 필요한 권한이 없으면 버킷 구성이 아닌 IAM 수준 제한이 근본 원인입니다.

6. CloudFront를 사용하는 경우(플레이북 8단계) OAI/OAC 구성을 확인합니다. CloudFront 403 오류는 Origin Access Identity 또는 Origin Access Control 잘못된 구성으로 인해 CloudFront가 S3에 접근하지 못하는 것을 나타냅니다.

7. 버킷 ACL 구성(플레이북 7단계)이 퍼블릭 접근을 제한하고 애플리케이션이 퍼블릭 접근을 기대하면 ACL이 접근을 차단하고 있는 것입니다. Block Public Access가 ACL 권한을 재정의한다는 점에 유의합니다.

상관관계를 찾을 수 없는 경우: 분석 기간을 2시간으로 확장하고, VPC에서 접근하는 경우 VPC 엔드포인트 정책을 검토하고, 교차 계정 접근을 위한 S3 버킷 암호화 KMS 키 정책을 확인하고, IAM 주체의 권한 경계를 검증하고, IAM 정책 평가 순서를 점검합니다.