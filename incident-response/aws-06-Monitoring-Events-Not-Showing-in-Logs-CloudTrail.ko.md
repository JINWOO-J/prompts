---
category: incident-response
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/AWS%20Playbooks/06-Monitoring/Events-Not-Showing-in-Logs-CloudTrail.md)'
role: SRE / AWS Incident Response
origin: scoutflo
extract_date: 2026-03-05
tags:
- cloudtrail
- cloudwatch
- compliance
- events
- iam
- incident-response
- k8s-service
- logging
- logs
- monitoring
- s3
- security
- showing
- sts
---

# CloudTrail Events Not Showing in Logs - CloudTrail 이벤트 로그에 미표시

## 의미

CloudTrail 이벤트가 로그에 표시되지 않는 현상(감사 추적 격차 또는 CloudTrailEventsMissing 경보 트리거)은 CloudTrail 로깅이 중지되었거나, S3 또는 CloudWatch Logs로의 로그 전달이 실패하거나, IAM 권한이 로그 전달에 불충분하거나, 로그 파일 전달 오류가 발생하거나, CloudTrail 트레일 구성이 잘못되었거나, CloudTrail 로그 파일 무결성 검증이 실패할 때 발생합니다.
 CloudTrail 이벤트가 로그에서 누락되고, 감사 추적이 불완전하며, 컴플라이언스 요구사항이 충족되지 않습니다. 이는 보안 및 감사 계층에 영향을 미치며 감사 추적 완전성을 손상시킵니다.

## 영향

CloudTrail 이벤트가 로그에서 누락됩니다. 감사 추적이 불완전합니다. 컴플라이언스 요구사항이 충족되지 않습니다. 보안 이벤트 가시성이 상실됩니다. 로그 기반 분석이 실패합니다. CloudTrail 로그 전달이 실패합니다. 감사 추적 격차가 발생합니다. 보안 모니터링이 손상됩니다.

## 플레이북

1. CloudTrail 트레일 `<trail-name>`이 존재하고 리전 `<region>`의 CloudTrail AWS 서비스 상태가 정상인지 확인합니다.
2. 리전 `<region>`의 CloudTrail 트레일 `<trail-name>`을 조회하여 트레일 상태, 로깅 상태, S3 버킷 구성, CloudWatch Logs 로그 그룹 구성을 점검하고, 트레일이 로깅 중인지 검증합니다.
3. CloudTrail 이벤트가 포함된 CloudWatch Logs에서 트레일 `<trail-name>` 관련 로그 전달 실패 패턴이나 누락된 이벤트 패턴을 필터링합니다.
4. CloudTrail 트레일 `<trail-name>`에 구성된 S3 버킷 `<bucket-name>`을 조회하여 버킷 정책, 로그 파일 전달 상태, 버킷 접근 권한을 점검합니다.
5. CloudTrail이 로그 전달에 사용하는 IAM 역할 `<role-name>`을 조회하여 S3 및 CloudWatch Logs 작업에 대한 정책 권한을 점검합니다.
6. S3 버킷 `<bucket-name>`의 CloudTrail 로그 파일을 나열하고 로그 파일 전달 타임스탬프, 파일 크기, 전달 패턴을 확인합니다.
7. CloudTrail 트레일 `<trail-name>`의 CloudWatch Logs 로그 그룹 구성을 조회하여 로그 그룹 구성을 확인합니다.
8. CloudTrail의 CloudWatch 지표(가용한 경우 로그 파일 전달)를 조회하여 로그 전달 패턴을 확인합니다.
9. CloudTrail 이벤트가 포함된 CloudWatch Logs에서 최근 7일 이내 트레일 `<trail-name>` 관련 CloudTrail 트레일 구성 또는 S3 버킷 정책 변경 이벤트를 필터링합니다.

## 진단

1. **3단계 및 2단계의 CloudWatch Logs 및 트레일 상태 분석**: CloudTrail 이벤트 전달 패턴을 검토합니다. 3단계의 CloudWatch Logs에서 최근 이벤트가 없으면 2단계의 트레일 상태를 확인합니다. 트레일 상태에서 "Logging: false"이거나 트레일이 중지되었으면 로깅이 비활성화된 것입니다.

2. **5단계의 IAM 권한 확인**: 로그 전달에 S3 또는 CloudWatch Logs가 관련된 경우 5단계의 IAM 역할에 대상 버킷에 대한 `s3:PutObject` 권한과 CloudWatch Logs 통합을 위한 `logs:PutLogEvents` 권한이 있는지 확인합니다.

3. **4단계의 S3 버킷 구성 확인**: 4단계의 S3 버킷 정책이 CloudTrail 서비스(`cloudtrail.amazonaws.com`)의 객체 쓰기를 허용하지 않으면 버킷 정책이 전달을 차단하고 있는 것입니다.

4. **6단계의 로그 파일 전달 검토**: 6단계의 S3 로그 파일에서 전달 타임스탬프 격차가 표시되면 간헐적 전달 실패가 발생한 것입니다. 가장 최근 로그 파일 타임스탬프를 확인합니다. 활성 트레일의 경우 CloudTrail은 약 5분마다 전달합니다.

5. **9단계의 구성 변경과 상관 분석**: 9단계의 CloudTrail 이벤트에서 로그 전달 중지 5분 이내에 트레일 구성 변경, S3 버킷 정책 변경 또는 IAM 역할 변경이 표시되면 최근 변경이 전달을 중단시킨 것입니다.

**상관관계를 찾을 수 없는 경우**: S3 접근 로그 및 CloudWatch Logs 패턴을 사용하여 분석을 30일로 확장합니다. 7단계의 CloudWatch Logs 로그 그룹이 적절한 보존으로 올바르게 구성되어 있는지 확인합니다.