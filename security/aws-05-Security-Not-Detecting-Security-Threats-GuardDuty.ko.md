---
category: security
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/AWS%20Playbooks/05-Security/Not-Detecting-Security-Threats-GuardDuty.md)'
role: SRE / AWS Incident Response
origin: scoutflo
extract_date: 2026-03-05
tags:
- cloudwatch
- detecting
- guardduty
- iam
- k8s-service
- monitoring
- security
- sts
- threats
---

# GuardDuty 보안 위협 미탐지 — GuardDuty Not Detecting Security Threats

## 의미

GuardDuty가 보안 위협을 탐지하지 못합니다(위협 탐지 실패 또는 GuardDutyThreatDetectionFailed 알람 발생). 원인으로는 GuardDuty 미활성화, GuardDuty 탐지기 비활성화, 데이터 소스 미구성, IAM 권한 부족, GuardDuty 서비스의 위협 분석 중 오류, GuardDuty 위협 인텔리전스 피드 미업데이트 등이 있습니다. GuardDuty 위협 탐지가 실패하고, 보안 위협이 식별되지 않으며, 위협 기반 알림이 발생하지 않습니다. 이는 보안 및 위협 탐지 계층에 영향을 미치며 보안 모니터링을 저해합니다. 일반적으로 GuardDuty 구성 문제, 데이터 소스 문제, 탐지기 상태 문제가 원인이며, 여러 계정이나 리전에서 GuardDuty를 사용하는 경우 탐지 동작이 다를 수 있고 애플리케이션에서 위협 탐지 실패가 발생할 수 있습니다.

## 영향

GuardDuty 위협 탐지 실패, 보안 위협 미식별, 위협 기반 알림 미발생, 보안 모니터링 저해, 위협 탐지 자동화 무효, 보안 사고 탐지 지연, GuardDuty 발견사항 미생성, 보안 태세 가시성 상실. GuardDutyThreatDetectionFailed 알람 발생 가능. 여러 계정이나 리전에서 GuardDuty를 사용하는 경우 탐지 동작이 다를 수 있음. 보안 모니터링 저하 발생 가능. 보안 위협 탐지가 무효화될 수 있습니다.

## 플레이북

1. GuardDuty 탐지기 `<detector-id>`의 존재를 확인하고 리전 `<region>`의 GuardDuty AWS 서비스 상태가 정상인지 확인합니다.
2. 리전 `<region>`의 GuardDuty 탐지기 `<detector-id>`를 조회하여 탐지기 상태, 활성화 상태, 데이터 소스 구성을 검사하고 탐지기가 활성화되었는지 확인합니다.
3. GuardDuty 이벤트가 포함된 CloudWatch Logs 로그 그룹을 조회하여 위협 탐지 실패 패턴이나 탐지기 오류 메시지를 필터링하고 탐지 오류 세부사항을 포함합니다.
4. FindingsGenerated를 포함한 GuardDuty 탐지기 `<detector-id>` CloudWatch 메트릭을 지난 7일 동안 조회하여 위협 탐지 패턴을 식별하고 탐지 메트릭을 분석합니다.
5. 탐지기 `<detector-id>`의 GuardDuty 발견사항을 나열하고 발견사항 생성 패턴, 위협 심각도, 탐지 타임스탬프를 확인하며 발견사항 생성을 검증합니다.
6. CloudTrail 이벤트가 포함된 CloudWatch Logs 로그 그룹을 조회하여 GuardDuty API 호출 실패나 탐지기 구성 오류를 필터링하고 API 오류를 확인합니다.
7. GuardDuty 탐지기 `<detector-id>`의 데이터 소스 활성화 상태를 조회하여 데이터 소스가 활성화되었는지 확인하고 데이터 소스 구성이 탐지에 영향을 미치는지 확인합니다.
8. 가용한 경우 DataSourcesProcessed를 포함한 GuardDuty 탐지기 `<detector-id>` CloudWatch 메트릭을 조회하여 데이터 소스 처리 패턴을 확인하고 데이터 소스가 처리되고 있는지 확인합니다.
9. CloudTrail 이벤트가 포함된 CloudWatch Logs 로그 그룹을 조회하여 지난 7일 동안 탐지기 `<detector-id>`와 관련된 GuardDuty 탐지기 활성화 또는 데이터 소스 구성 수정 이벤트를 필터링하고 구성 변경을 확인합니다.

## 진단

1. **4단계의 CloudWatch 메트릭 분석**: 탐지 활동에 대한 GuardDuty 메트릭을 검토합니다. CloudWatch 메트릭에서 7일간 FindingsGenerated가 0이면 위협이 없거나 탐지가 작동하지 않는 것입니다. 환경 위험 프로필에 기반한 예상 위협 활동과 비교합니다. 메트릭에서 일부 발견사항이 생성된 것으로 확인되면 탐지는 작동하지만 특정 위협 유형을 놓치고 있을 수 있습니다 - 2단계로 진행합니다.

2. **2단계의 탐지기 활성화 확인**: 2단계의 탐지기 구성에서 탐지기 상태가 "DISABLED"이거나 탐지기가 일시 중지된 것으로 확인되면 위협 탐지가 실행되지 않는 것입니다. 탐지기가 최근 비활성화되었는지 확인합니다. 탐지기가 활성화되어 있지만 상태에 문제가 있으면 3단계로 진행합니다.

3. **7단계의 데이터 소스 구성 확인**: 7단계의 데이터 소스에서 VPC Flow Logs, CloudTrail, DNS 로그가 활성화되지 않은 것으로 확인되면 GuardDuty가 네트워크 및 API 활동에 대한 가시성이 없는 것입니다. 포괄적인 위협 탐지를 위해 모든 관련 데이터 소스를 활성화합니다. 데이터 소스가 활성화되어 있지만 8단계의 메트릭에서 처리 활동이 없으면 데이터 소스 전달이 실패하는 것입니다.

4. **6단계의 CloudTrail 이벤트 검토**: 6단계의 CloudTrail 이벤트에서 GuardDuty API 호출 실패나 접근 거부 오류가 확인되면 권한 문제가 탐지에 영향을 미치는 것입니다. GuardDuty 서비스 연결 역할에 적절한 권한이 있는지 확인합니다. API 호출이 성공하고 있으면 5단계로 진행합니다.

5. **9단계의 구성 변경 상관관계 분석**: 9단계의 CloudTrail 이벤트에서 탐지 중단 5분 이내에 탐지기 활성화 변경, 데이터 소스 수정, 억제 규칙 추가가 확인되면 최근 변경이 위협 탐지에 영향을 미친 것입니다. 정상적인 위협을 필터링할 수 있는 발견사항 억제 규칙을 확인합니다.

**상관관계가 발견되지 않는 경우**: 5단계의 발견사항 패턴을 사용하여 분석을 90일로 확장합니다. 멀티 계정 설정의 경우 멤버 계정이 관리자 계정에 올바르게 연결되었는지 확인합니다. GuardDuty 위협 인텔리전스 피드 업데이트와 1단계의 서비스 상태를 검토합니다. 위협을 마스킹할 수 있는 IP 화이트리스트나 발견사항 억제 규칙을 확인합니다. 계정에 분석할 실제 네트워크 및 API 활동이 있는지 확인합니다.
