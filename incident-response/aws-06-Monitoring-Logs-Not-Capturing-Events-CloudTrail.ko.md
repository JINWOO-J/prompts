---
category: incident-response
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/AWS%20Playbooks/06-Monitoring/Logs-Not-Capturing-Events-CloudTrail.md)'
role: SRE / AWS Incident Response
origin: scoutflo
extract_date: 2026-03-05
tags:
- capturing
- cloudtrail
- cloudwatch
- compliance
- events
- iam
- incident-response
- k8s-service
- kms
- logging
- logs
- monitoring
- performance
- s3
- security
- sts
---

# AWS CloudTrail Logs Not Capturing Events - AWS CloudTrail 로그 이벤트 미캡처

## 의미

CloudTrail 로그가 API 이벤트를 캡처하지 못하는 현상(로깅 격차 또는 CloudTrailEventMissing 경보 트리거)은 CloudTrail이 활성화되지 않았거나, 로깅이 꺼져 있거나, S3 버킷 정책이 CloudTrail 쓰기를 차단하거나, IAM 권한이 CloudTrail 작업에 불충분하거나, CloudTrail 이벤트 선택기가 이벤트를 필터링하거나, KMS 키 접근이 암호화된 트레일 쓰기를 방해할 때 발생합니다.
 API 활동이 로깅되지 않고, 감사 추적이 불완전하며, CloudTrail 로그 파일에 격차가 표시됩니다. 이는 보안 및 컴플라이언스 계층에 영향을 미치며 감사 기능을 손상시킵니다.

## 영향

API 활동이 로깅되지 않습니다. 감사 추적이 불완전합니다. 보안 모니터링이 실패합니다. 컴플라이언스 요구사항을 위반할 수 있습니다. CloudTrail 로그 격차가 발생합니다. 이벤트 이력이 누락됩니다. 보안 조사를 진행할 수 없습니다. API 호출 추적이 상실됩니다.

## 플레이북

1. CloudTrail 트레일 `<trail-name>`이 존재하고 리전 `<region>`의 CloudTrail AWS 서비스 상태가 정상인지 확인합니다.
2. CloudTrail 트레일 `<trail-name>`을 조회하여 CloudTrail이 활성화되어 있고 로깅이 켜져 있는지 트레일 상태와 IsLogging 상태를 확인합니다.
4. S3 버킷 `<bucket-name>`의 버킷 정책을 조회하여 정책이 CloudTrail의 로그 쓰기를 허용하는지 확인합니다.
5. CloudTrail 서비스의 IAM 권한을 조회하여 IAM 권한에 cloudtrail:PutEventSelectors 및 cloudtrail:UpdateTrail이 포함되어 있는지 검증합니다.
6. 트레일 `<trail-name>`의 CloudTrail 이벤트가 포함된 CloudWatch Logs를 쿼리하여 이벤트 캡처의 잠재적 격차나 문제를 파악합니다.
7. CloudTrail 트레일 `<trail-name>`의 이벤트 선택기를 조회하여 이벤트 선택기가 필요한 이벤트를 필터링하고 있지 않은지 확인합니다.
8. CloudTrail 트레일 `<trail-name>`의 데이터 이벤트 구성을 조회하여 필요한 경우 데이터 이벤트(S3, Lambda)가 활성화되어 있는지 확인합니다.
9. 트레일이 암호화된 경우 CloudTrail 트레일 `<trail-name>`의 KMS 키 구성을 조회하여 KMS 키 정책이 CloudTrail의 키 사용을 허용하는지 확인합니다.
10. AWS Organizations를 사용하는 경우 CloudTrail 트레일 `<trail-name>`의 조직 트레일 구성을 조회하여 조직 트레일 설정을 확인합니다.

## 진단

1. 플레이북 1단계의 AWS 서비스 상태를 분석하여 리전의 CloudTrail 서비스 가용성을 확인합니다.

2. 플레이북 2단계의 트레일 상태에서 IsLogging이 false이거나 트레일이 "ACTIVE" 상태가 아니면 로깅이 비활성화된 것입니다.

3. 플레이북 4단계의 S3 버킷 정책이 CloudTrail의 로그 쓰기를 허용하지 않으면(CloudTrail 서비스 주체에 대한 s3:PutObject 권한 필요) 로그 전달이 조용히 실패합니다.

4. 플레이북 5단계의 IAM 권한에서 CloudTrail 서비스 연결 역할에 필요한 권한이 없으면 트레일 작업이 실패할 수 있습니다.

5. 플레이북 6단계의 CloudWatch Logs에서 이벤트 전달 격차가 표시되면 격차 타임스탬프를 파악하고 구성 변경이나 S3 전달 실패와 상관 분석합니다.

6. 플레이북 7단계의 이벤트 선택기가 관리 이벤트를 필터링하거나 특정 이벤트 소스를 제외하면 일치하는 이벤트만 캡처됩니다.

7. 플레이북 8단계의 데이터 이벤트가 S3 또는 Lambda에 대해 활성화되지 않으면 데이터 플레인 이벤트가 캡처되지 않습니다.

8. 플레이북 9단계의 KMS 키 구성에서 트레일이 암호화를 사용하지만 키 정책이 CloudTrail의 키 사용을 허용하지 않으면 암호화된 로그 전달이 실패합니다.

상관관계를 찾을 수 없는 경우: 쿼리 기간을 24시간으로 확장하고, S3 버킷에 충분한 용량이 있는지 확인하고, 로그 파일을 삭제하거나 전환할 수 있는 S3 수명 주기 정책을 점검합니다.