---
category: incident-response
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/AWS%20Playbooks/06-Monitoring/Alarm-Not-Triggering-as-Expected-CloudWatch.md)'
role: SRE / AWS Incident Response
origin: scoutflo
extract_date: 2026-03-05
tags:
- alarm
- alerting
- cloudwatch
- expected
- incident-response
- k8s-service
- monitoring
- performance
- sts
- triggering
---

# CloudWatch Alarm Not Triggering as Expected - CloudWatch 경보 예상대로 미트리거

## 의미

CloudWatch 경보가 예상대로 트리거되지 않는 현상(경고 실패 또는 CloudWatchAlarmNotTriggering 경보 트리거)은 경보 임계값이 잘못되었거나, 경보 평가 기간이 너무 길거나, 경보 지표를 사용할 수 없거나, 경보 상태 전환 조건이 충족되지 않거나, 경보가 비활성화되었거나 INSUFFICIENT_DATA 상태이거나, 경보 작업 구성이 알림을 방해할 때 발생합니다.
 CloudWatch 경보가 트리거되지 않고, 경고가 실패하며, 임계값 위반이 감지되지 않습니다. 이는 모니터링 및 경고 계층에 영향을 미치며 인시던트 감지를 손상시킵니다.

## 영향

CloudWatch 경보가 트리거되지 않습니다. 경고가 실패합니다. 모니터링 자동화가 효과가 없습니다. 경보 상태 전환이 발생하지 않습니다. 임계값 위반이 감지되지 않습니다. 경보 알림이 전송되지 않습니다. 경고 안정성이 손상됩니다. 인시던트 감지가 지연됩니다.

## 플레이북

1. CloudWatch 경보 `<alarm-name>`이 존재하고 리전 `<region>`의 CloudWatch AWS 서비스 상태가 정상인지 확인합니다.
2. 리전 `<region>`의 CloudWatch 경보 `<alarm-name>`을 조회하여 경보 구성, 임계값 설정, 평가 기간, 지표 구성, 경보 상태를 점검하고, 경보가 활성화되어 있는지 검증합니다.
3. 경보 `<alarm-name>`이 사용하는 지표의 CloudWatch 지표를 최근 24시간 동안 조회하여 지표 데이터 가용성과 값을 확인하고, 지표 데이터 격차를 분석합니다.
4. 경보 `<alarm-name>`의 CloudWatch 경보 이력을 최근 7일 동안 조회하여 경보 상태 전환과 평가 패턴을 파악하고, 평가 이력을 분석합니다.
5. CloudWatch 경보 이벤트가 포함된 CloudWatch Logs에서 경보 `<alarm-name>` 관련 경보 평가 패턴이나 상태 전환 이벤트를 필터링합니다.
6. 경보 `<alarm-name>`의 CloudWatch 경보 작업을 나열하고 SNS 주제 구성, 작업 활성화, 알림 설정을 확인합니다.
7. 해당되는 경우 CloudWatch 경보 `<alarm-name>`의 지표 수학 또는 복합 경보 구성을 조회하여 경보 평가 로직을 검증합니다.
8. 경보 `<alarm-name>`의 CloudWatch 경보 이력(상태 변경 이력 포함)을 조회하여 경보 상태 전환을 확인하고, 경보 전환은 발생했지만 작업이 실패했는지 점검합니다.
9. CloudTrail 이벤트가 포함된 CloudWatch Logs에서 최근 7일 이내 경보 `<alarm-name>` 관련 CloudWatch 경보 구성 변경 이벤트를 필터링합니다.

## 진단

1. 경보 `<alarm-name>`에 대해 수집된 CloudWatch 지표(플레이북 3단계)를 분석하여 지표 데이터 가용성을 확인하고 데이터 격차를 파악합니다. 지표 데이터에 지속적인 격차나 INSUFFICIENT_DATA 패턴이 표시되면 경보가 올바르게 평가할 수 없습니다.

2. CloudWatch 경보 이력(플레이북 4단계)을 검토하여 최근 7일 동안의 경보 상태 전환과 평가 패턴을 확인합니다. 경보 이력에서 경보가 INSUFFICIENT_DATA 상태로 유지되면 지표 가용성 타임스탬프와 상관 분석합니다. 예상 임계값 위반에도 불구하고 OK 상태를 보이면 임계값 구성이 잘못되었을 가능성이 높습니다.

3. 경보 구성 세부 정보(플레이북 2단계)를 확인하여 임계값 설정, 평가 기간, 비교 연산자를 점검합니다. 임계값이 지표 데이터 분석 기반의 예상 지표 범위와 일치하지 않으면 임계값 잘못된 구성이 근본 원인입니다.

4. 경보 구성이 올바르지만 경보가 여전히 트리거되지 않으면 경보 작업 구성(플레이북 6단계)을 확인하여 SNS 주제가 올바르게 구성되어 있고 작업이 활성화되어 있는지 검증합니다.

5. 복합 경보의 경우 지표 수학 또는 복합 경보 구성(플레이북 7단계)을 분석하여 평가 로직을 검증합니다.

6. CloudTrail 이벤트(플레이북 9단계)와 경보 미트리거 타임스탬프를 30분 이내로 상관 분석하여 경보 동작에 영향을 미쳤을 수 있는 최근 구성 변경을 파악합니다.

상관관계를 찾을 수 없는 경우: 기간을 30일로 확장하고, 경보 작업 구성 및 SNS 주제 전달 상태를 포함한 대안적 증거 소스를 검토합니다.