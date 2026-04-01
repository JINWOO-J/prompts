---
category: security
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/AWS%20Playbooks/05-Security/Not-Aggregating-Findings-Security-Hub.md)'
role: SRE / AWS Incident Response
origin: scoutflo
extract_date: 2026-03-05
tags:
- aggregating
- cloudwatch
- compliance
- findings
- iam
- k8s-service
- monitoring
- rds
- security
- sts
---

# Security Hub 발견사항 집계 실패 — AWS Security Hub Not Aggregating Findings

## 의미

AWS Security Hub가 발견사항을 집계하지 않습니다(보안 집계 실패 또는 SecurityHubFindingsNotAggregating 알람 발생). 원인으로는 Security Hub 미활성화, 보안 표준 미구독, 발견사항 집계 구성 오류, IAM 권한 부족, Security Hub 서비스의 집계 중 오류, Security Hub 발견사항 소스 통합 미구성 등이 있습니다. Security Hub 발견사항이 집계되지 않고, 보안 태세 가시성이 상실되며, 발견사항 기반 분석이 실패합니다. 이는 보안 및 컴플라이언스 계층에 영향을 미치며 보안 가시성을 저해합니다. 일반적으로 Security Hub 구성 문제, 통합 문제, 권한 실패가 원인이며, 여러 계정이나 리전에서 Security Hub를 사용하는 경우 집계 동작이 다를 수 있고 애플리케이션에서 보안 가시성 갭이 발생할 수 있습니다.

## 영향

Security Hub 발견사항 미집계, 보안 태세 가시성 상실, 발견사항 기반 분석 실패, 보안 표준 컴플라이언스 추적 실패, 발견사항 집계 자동화 무효, 보안 인사이트 이용 불가, 컴플라이언스 요구사항 미충족, 보안 모니터링 저해. SecurityHubFindingsNotAggregating 알람 발생 가능. 여러 계정이나 리전에서 Security Hub를 사용하는 경우 집계 동작이 다를 수 있음. 보안 가시성 저하 발생 가능. 보안 컴플라이언스 추적이 무효화될 수 있습니다.

## 플레이북

1. AWS Security Hub 구성의 존재를 확인하고 리전 `<region>`의 Security Hub AWS 서비스 상태가 정상인지 확인합니다.
2. 리전 `<region>`의 AWS Security Hub 구성을 조회하여 활성화 상태, 보안 표준 구독, 발견사항 집계 설정을 검사하고 Security Hub가 활성화되었는지 확인합니다.
3. Security Hub 이벤트가 포함된 CloudWatch Logs 로그 그룹을 조회하여 집계 실패 패턴이나 발견사항 처리 오류를 필터링하고 집계 오류 세부사항을 포함합니다.
4. FindingsImported 및 FindingsUpdated를 포함한 Security Hub CloudWatch 메트릭을 지난 24시간 동안 조회하여 발견사항 집계 패턴을 식별하고 집계 메트릭을 분석합니다.
5. Security Hub 발견사항을 나열하고 발견사항 집계 상태, 발견사항 소스, 발견사항 업데이트 타임스탬프를 확인하며 발견사항 집계를 검증합니다.
6. CloudTrail 이벤트가 포함된 CloudWatch Logs 로그 그룹을 조회하여 Security Hub API 호출 실패나 집계 오류를 필터링하고 API 오류를 확인합니다.
7. AWS Security Hub 발견사항 소스 통합을 조회하여 통합 구성을 확인하고 발견사항 소스가 통합되었는지 확인합니다.
8. AWS Security Hub 보안 표준 구독을 조회하여 표준이 구독되었는지 확인하고 표준이 집계에 영향을 미치는지 확인합니다.
9. CloudTrail 이벤트가 포함된 CloudWatch Logs 로그 그룹을 조회하여 지난 7일 동안 Security Hub 활성화 또는 보안 표준 구독 수정 이벤트를 필터링하고 구성 변경을 확인합니다.

## 진단

1. **4단계의 CloudWatch 메트릭 분석**: 발견사항 집계 패턴에 대한 Security Hub 메트릭을 검토합니다. CloudWatch 메트릭에서 FindingsImported가 0이면 통합된 소스에서 발견사항이 수신되지 않는 것입니다. FindingsUpdated가 0이지만 FindingsImported에 활동이 있으면 발견사항 처리가 실패하는 것입니다. 보안 도구에서 예상되는 발견사항 볼륨과 비교합니다. 메트릭에 일부 활동이 있으면 2단계로 진행합니다.

2. **2단계의 Security Hub 활성화 확인**: 2단계의 Security Hub 구성에서 Security Hub가 활성화되지 않았거나 최근 비활성화된 것으로 확인되면 활성화 부재가 근본 원인입니다. 8단계의 보안 표준 구독을 확인합니다 - 표준이 활성화되지 않았으면 컴플라이언스 발견사항이 생성되지 않습니다. Security Hub가 활성화되어 있으면 3단계로 진행합니다.

3. **7단계의 발견사항 소스 통합 확인**: 7단계의 발견사항 소스 통합에서 GuardDuty, Inspector, 서드파티 도구가 통합되지 않은 것으로 확인되면 해당 발견사항 소스가 데이터를 전송하지 않는 것입니다. 예상되는 각 통합이 활성화되고 올바르게 구성되었는지 확인합니다. 통합이 올바른 것으로 보이면 4단계로 진행합니다.

4. **6단계의 CloudTrail 이벤트 검토**: 6단계의 CloudTrail 이벤트에서 Security Hub API 호출 실패나 접근 거부 오류가 확인되면 권한 문제가 집계에 영향을 미치는 것입니다. 커스텀 통합을 사용하는 경우 `securityhub:BatchImportFindings` 권한 문제를 확인합니다. API 호출이 성공하고 있으면 5단계로 진행합니다.

5. **9단계의 구성 변경 상관관계 분석**: 9단계의 CloudTrail 이벤트에서 집계 실패 5분 이내에 Security Hub 활성화 변경, 보안 표준 수정, 통합 구성 변경이 확인되면 최근 변경이 문제를 유발한 것입니다. 구체적인 수정 사항을 검토하여 원인이 되는 변경을 식별합니다.

**상관관계가 발견되지 않는 경우**: 5단계의 발견사항 패턴을 사용하여 분석을 30일로 확장합니다. 멀티 계정 설정의 경우 집계 리전이 올바르게 구성되었는지 확인합니다. 멤버 계정이 관리자 계정에 올바르게 연결되었는지 확인합니다. 1단계의 Security Hub 서비스 상태를 검토하고 발견사항 소스 서비스(GuardDuty, Inspector)가 올바르게 활성화되어 발견사항을 생성하고 있는지 확인합니다.
