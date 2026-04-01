---
category: incident-response
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/AWS%20Playbooks/06-Monitoring/Logs-Not-Appearing-CloudWatch.md)'
role: SRE / AWS Incident Response
origin: scoutflo
extract_date: 2026-03-05
tags:
- appearing
- cloudwatch
- iam
- incident-response
- k8s-service
- logs
- monitoring
- observability
---

# CloudWatch Logs Not Appearing - CloudWatch Logs 미표시

## 의미

CloudWatch Logs가 표시되지 않는 현상(로그 가시성 격차 또는 CloudWatchLogsMissing 경보 트리거)은 로그 그룹이 존재하지 않거나, IAM 권한이 로그 생성에 불충분하거나, 로그 보존 기간이 만료되거나, 로그 스트림 생성이 실패하거나, CloudWatch Logs 서비스가 로그 수집 중 오류를 만나거나, CloudWatch Logs 로그 그룹 할당량 제한에 도달할 때 발생합니다.
 CloudWatch Logs가 누락되고, 로그 기반 디버깅이 실패하며, 로그 가시성이 손상됩니다. 이는 모니터링 및 관측성 계층에 영향을 미치며 문제 해결 기능을 감소시킵니다.

## 영향

CloudWatch Logs가 누락됩니다. 로그 기반 디버깅이 실패합니다. 로그 가시성이 손상됩니다. 로그 스트림이 생성되지 않습니다. 애플리케이션 로그가 수집되지 않습니다. 로그 기반 모니터링이 효과가 없습니다. 문제 해결 기능이 감소합니다.

## 플레이북

1. CloudWatch Logs 접근을 확인하고 리전 `<region>`의 CloudWatch Logs AWS 서비스 상태가 정상인지 확인합니다.
2. 예상 로그 그룹 패턴과 일치하는 CloudWatch Logs 로그 그룹을 쿼리하여 로그 그룹이 존재하고 접근 가능한지 확인합니다.
3. 로그 게시에 사용되는 IAM 역할 `<role-name>` 또는 IAM 사용자 `<user-name>`을 조회하여 CreateLogGroup, CreateLogStream, PutLogEvents를 포함한 CloudWatch Logs 작업에 대한 정책 권한을 점검합니다.
4. 애플리케이션 로그가 포함된 CloudWatch Logs에서 로그 게시 오류나 PutLogEvents API 호출 실패를 필터링합니다.
5. CloudWatch Logs의 CloudWatch 지표(IncomingLogEvents, IncomingBytes)를 최근 24시간 동안 조회하여 로그 수집 패턴을 파악합니다.
6. CloudWatch 로그 그룹을 나열하고 로그 그룹 구성, 보존 설정, 로그 스트림 생성 패턴을 확인합니다.
7. CloudWatch Logs 로그 그룹 할당량 제한을 조회하여 할당량 사용량을 확인합니다.
8. CloudWatch Logs의 CloudWatch 지표(가용한 경우 ThrottledLogEvents)를 조회하여 로그 스로틀링 패턴을 확인합니다.
9. CloudTrail 이벤트가 포함된 CloudWatch Logs에서 최근 24시간 이내 CloudWatch Logs 로그 그룹 또는 IAM 정책 변경 이벤트를 필터링합니다.

## 진단

1. **3단계의 IAM 권한 먼저 확인**: 로그 게시에 IAM 권한이 필요한 경우 3단계의 IAM 역할 또는 사용자에게 `logs:CreateLogGroup`, `logs:CreateLogStream`, `logs:PutLogEvents` 권한이 있는지 확인합니다. CloudTrail 이벤트에서 CloudWatch Logs API 호출에 대한 "AccessDenied"가 표시되면 권한 문제가 로그 전달을 차단하고 있는 것입니다.

2. **5단계의 CloudWatch 지표 분석**: 로그 수집 지표에서 전달 패턴을 검토합니다. CloudWatch 지표에서 예상 로그 그룹의 IncomingLogEvents가 0이면 로그가 수신되지 않고 있는 것입니다. 8단계의 지표에서 스로틀링이 표시되면 할당량 제한이 수집에 영향을 미치고 있는 것입니다.

3. **2단계 및 6단계의 로그 그룹 존재 확인**: 2단계의 로그 그룹이 존재하지 않으면 로그 그룹 생성이 실패했거나 로그 그룹이 삭제된 것입니다. 로그 그룹이 존재하지만 최근 스트림이 없으면 로그 스트림 생성이 실패하고 있는 것입니다.

4. **7단계의 할당량 제한 확인**: 7단계의 할당량 제한에서 로그 그룹 수 또는 PutLogEvents 속도 제한에 도달했으면 할당량 소진이 새 로그를 방해하고 있는 것입니다.

5. **9단계의 구성 변경과 상관 분석**: 9단계의 CloudTrail 이벤트에서 로그 사라짐 1시간 이내에 로그 그룹 삭제, IAM 정책 변경 또는 보존 정책 변경이 표시되면 최근 변경이 문제를 유발한 것입니다.

**상관관계를 찾을 수 없는 경우**: 로그 수집 패턴을 사용하여 분석을 30일로 확장합니다. 애플리케이션이 CloudWatch로 로그를 보내도록 올바르게 구성되어 있는지 확인합니다(에이전트 구성, SDK 설정). CloudWatch Logs VPC 엔드포인트 없이 VPC에서 실행되는 애플리케이션의 네트워크 연결 문제를 점검합니다.