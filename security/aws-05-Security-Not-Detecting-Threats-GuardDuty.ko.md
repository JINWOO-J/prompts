---
category: security
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/AWS%20Playbooks/05-Security/Not-Detecting-Threats-GuardDuty.md)'
role: SRE / AWS Incident Response
origin: scoutflo
extract_date: 2026-03-05
tags:
- cloudwatch
- compliance
- detecting
- dns
- guardduty
- iam
- k8s-service
- monitoring
- performance
- security
- sts
- threats
- vpc
---

# GuardDuty 위협 미탐지 — AWS GuardDuty Not Detecting Threats

## 의미

GuardDuty가 보안 위협을 탐지하지 못합니다(보안 모니터링 갭 또는 GuardDutyFindingMissing 알림 발생). 원인으로는 GuardDuty 미활성화, 위협 인텔리전스 피드 비활성화, CloudTrail/VPC Flow Logs/DNS 로그 미모니터링, GuardDuty 발견사항 필터링, IAM 권한으로 인한 GuardDuty의 필요 로그 접근 차단, GuardDuty 억제 규칙으로 인한 발견사항 숨김 등이 있습니다. GuardDuty 발견사항이 누락되거나 억제되고, 보안 모니터링에 갭이 발생하며, CloudWatch Logs에서 GuardDuty 데이터 소스 문제가 확인됩니다. 이는 보안 모니터링 계층에 영향을 미치며 위협 탐지를 저해합니다. 일반적으로 구성 문제, 데이터 소스 문제, 발견사항 억제가 원인이며, AWS Organizations를 사용하는 경우 멤버 계정 구성이 탐지에 영향을 줄 수 있고 Security Hub 통합에서 누락된 발견사항이 표시될 수 있습니다.

## 영향

보안 위협 미탐지, 보안 모니터링 무효, GuardDuty 발견사항 누락, 보안 알림 미발생, 위협 탐지 갭 발생, 보안 조사에서 위협 식별 불가, 컴플라이언스 모니터링 실패, 악의적 활동 미감지 가능, 보안 태세 저해. GuardDutyFindingMissing 알림 발생. Security Hub 발견사항 불완전. AWS Organizations를 사용하는 경우 조직 전체 위협 탐지 저해. 보안 컴플라이언스 요구사항 위반 가능. 미탐지 위협으로 인해 애플리케이션에서 보안 관련 오류나 성능 문제가 발생할 수 있습니다.

## 플레이북

1. GuardDuty 탐지기 `<detector-id>`의 존재를 확인하고 리전 `<region>`의 GuardDuty AWS 서비스 상태가 정상인지 확인합니다.
2. GuardDuty 탐지기 `<detector-id>` 구성을 조회하여 탐지기 상태를 확인하고 GuardDuty가 활성화되었는지 검증하며 탐지기가 "ENABLED" 상태인지 확인합니다.
3. GuardDuty 탐지기 `<detector-id>` 설정을 조회하여 위협 인텔리전스 피드가 활성화되었는지 확인하고 위협 인텔리전스 피드 상태를 검증합니다.
4. GuardDuty 탐지기 `<detector-id>` 데이터 소스 구성을 조회하여 CloudTrail, VPC Flow Logs, DNS 로그가 모니터링되고 있는지 확인하고 각 소스의 데이터 소스 상태를 확인합니다.
5. GuardDuty 탐지기 `<detector-id>` 억제 규칙을 조회하여 억제 규칙이 정상적인 위협 발견사항을 숨기고 있지 않은지 확인하고 규칙 기준과 범위를 확인합니다.
6. GuardDuty 서비스용 IAM 역할 `<role-name>`을 조회하여 GuardDuty가 필요한 로그에 접근할 수 있는 IAM 권한을 확인하고 서비스 연결 역할 권한을 검증합니다.
7. CloudTrail 이벤트가 포함된 CloudWatch Logs 로그 그룹을 조회하여 탐지기 `<detector-id>`와 관련된 GuardDuty API 호출 실패, Security Hub 통합 오류, 구성 오류를 필터링합니다.
8. GuardDuty 탐지기 `<detector-id>` 기능 활성화 상태를 조회하여 해당되는 경우 S3 Protection, EKS Protection, RDS Protection, Malware Protection 기능이 활성화되었는지 확인합니다.
9. AWS Organizations 사용 여부를 확인하고 GuardDuty 멤버 계정 구성을 확인하며 조직 전체 GuardDuty 설정을 검증합니다.

## 진단

1. 플레이북 1단계의 AWS 서비스 상태를 분석하여 해당 리전의 GuardDuty 서비스 가용성을 확인합니다. 서비스 상태에 문제가 있으면 탐지 갭은 구성 변경이 아닌 AWS 측 문제로 모니터링이 필요합니다.

2. 플레이북 2단계의 탐지기 상태에서 GuardDuty가 "ENABLED" 상태가 아니면 탐지기가 비활성화되어 상태 변경 타임스탬프에서 위협 탐지가 중단된 것입니다. 즉시 다시 활성화합니다.

3. 플레이북 3단계의 위협 인텔리전스 피드 상태에서 피드가 비활성화된 것으로 확인되면 비활성화 타임스탬프와 탐지 갭이 시작된 시점의 상관관계를 분석합니다. 비활성화된 피드는 알려진 악성 지표에 대한 탐지 범위를 줄입니다.

4. 플레이북 4단계의 데이터 소스 구성에서 CloudTrail, VPC Flow Logs, DNS 로그가 모니터링되지 않는 것으로 확인되면 플레이북 7단계의 CloudTrail 이벤트에서 데이터 소스 구성 변경을 조사합니다. 누락된 데이터 소스는 특정 탐지 카테고리에 사각지대를 만듭니다.

5. 플레이북 5단계의 억제 규칙에 지나치게 광범위한 기준이 포함되어 있으면 규칙 생성 타임스탬프를 검토하여 정상적인 발견사항이 억제되고 있는지 판단합니다. 넓은 IP 범위나 일반적인 이벤트 유형과 매칭되는 규칙은 실제 위협을 숨길 수 있습니다.

6. 플레이북 6단계의 IAM 권한에서 GuardDuty 서비스 연결 역할에 필요한 권한이 없는 것으로 확인되면 권한 변경과 탐지 실패의 상관관계를 분석합니다. 로그 접근 권한 누락은 GuardDuty가 보안 데이터를 분석하는 것을 방해합니다.

7. 플레이북 8단계의 기능 활성화에서 S3 Protection, EKS Protection, RDS Protection, Malware Protection이 비활성화된 것으로 확인되면 탐지가 활성화된 기능에만 제한됩니다.

8. AWS Organizations를 사용하는 경우(플레이북 9단계), 멤버 계정 GuardDuty 구성을 확인합니다. 잘못 구성된 멤버 계정은 관리자 계정에 발견사항을 전달하지 않습니다.

수집된 데이터에서 상관관계가 발견되지 않는 경우: CloudTrail 쿼리 기간을 7일로 확장하고, Security Hub 통합 상태를 검토하고, 데이터 소스의 로그 전달 실패를 확인하고, 탐지 빈도에 영향을 줄 수 있는 GuardDuty 비용 최적화 설정을 조사합니다. 탐지 실패는 로그 소스 전달 문제, 위협 인텔리전스 연결 문제, 조직 전체 구성 불일치로 인해 발생할 수 있습니다.
