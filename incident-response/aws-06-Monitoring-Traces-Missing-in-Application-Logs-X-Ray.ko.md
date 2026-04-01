---
category: incident-response
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/AWS%20Playbooks/06-Monitoring/Traces-Missing-in-Application-Logs-X-Ray.md)'
role: SRE / AWS Incident Response
origin: scoutflo
extract_date: 2026-03-05
tags:
- cloudwatch
- iam
- incident-response
- k8s-service
- logs
- missing
- monitoring
- observability
- traces
---

# X-Ray Traces Missing in Application Logs - X-Ray 트레이스 애플리케이션 로그에서 누락

## 의미

X-Ray 트레이스가 애플리케이션 로그에서 누락되는 현상(분산 추적 격차 또는 XRayTracesMissing 경보 트리거)은 X-Ray 데몬이 실행되지 않거나, X-Ray SDK가 구성되지 않았거나, IAM 권한이 트레이스 제출에 불충분하거나, X-Ray 샘플링 규칙이 트레이스를 필터링하거나, X-Ray 서비스가 트레이스 수집 중 오류를 만나거나, X-Ray 트레이스 샘플링 비율이 너무 낮을 때 발생합니다.
 X-Ray 트레이스가 수집되지 않고, 분산 추적이 실패하며, 트레이스 기반 분석을 사용할 수 없습니다. 이는 관측성 및 분산 추적 계층에 영향을 미치며 애플리케이션 가시성을 감소시킵니다.

## 영향

X-Ray 트레이스가 수집되지 않습니다. 분산 추적이 실패합니다. 트레이스 기반 분석을 사용할 수 없습니다. 애플리케이션 트레이스 가시성이 상실됩니다. X-Ray 트레이스 샘플링이 효과가 없습니다. 트레이스 기반 디버깅이 실패합니다. 관측성이 손상됩니다.

## 플레이북

1. X-Ray 서비스 접근을 확인하고 리전 `<region>`의 X-Ray AWS 서비스 상태가 정상인지 확인합니다.
2. 애플리케이션 로그가 포함된 CloudWatch Logs에서 X-Ray 트레이스 ID 패턴이나 트레이스 제출 오류 메시지를 필터링합니다.
3. X-Ray 서비스의 CloudWatch 지표(TracesReceived, TracesProcessed)를 최근 24시간 동안 조회하여 트레이스 수집 패턴을 파악합니다.
4. 애플리케이션이 X-Ray 트레이스 제출에 사용하는 IAM 역할 `<role-name>`을 조회하여 PutTraceSegments를 포함한 X-Ray 작업에 대한 정책 권한을 점검합니다.
5. X-Ray 샘플링 규칙을 나열하고 샘플링 규칙 구성, 샘플링 비율, 애플리케이션 트레이스에 대한 규칙 적용 가능성을 확인합니다.
6. X-Ray 데몬 로그가 포함된 CloudWatch Logs에서 데몬 오류, 트레이스 제출 실패 또는 데몬 연결 문제를 필터링합니다.
7. X-Ray 서비스 샘플링 구성을 조회하여 샘플링 비율 설정을 확인하고, 샘플링 비율이 너무 낮아 트레이스 수집에 영향을 미치는지 점검합니다.
8. X-Ray 데몬의 CloudWatch 지표(가용한 경우)를 조회하여 데몬 상태를 확인합니다.
9. CloudTrail 이벤트가 포함된 CloudWatch Logs에서 최근 24시간 이내 X-Ray SDK 구성 또는 IAM 역할 정책 변경 이벤트를 필터링합니다.

## 진단

1. **4단계의 IAM 권한 먼저 확인**: 트레이스 제출에 IAM 권한이 필요한 경우 4단계의 IAM 역할에 `xray:PutTraceSegments` 및 `xray:PutTelemetryRecords` 권한이 있는지 확인합니다. 2단계의 애플리케이션 로그에서 "AccessDeniedException" 또는 권한 오류가 표시되면 불충분한 권한이 트레이스 제출을 차단하고 있는 것입니다.

2. **3단계의 CloudWatch 지표 분석**: X-Ray 트레이스 수집 지표를 검토합니다. CloudWatch 지표에서 TracesReceived가 0이면 트레이스가 X-Ray 서비스에 도달하지 않고 있는 것입니다. 일부 트레이스가 수신되지만 예상보다 적으면 샘플링이 트레이스를 필터링하고 있을 수 있습니다.

3. **6단계 및 8단계의 X-Ray 데몬 상태 확인**: 6단계의 데몬 로그에서 오류, 연결 문제가 표시되거나 데몬이 실행되지 않으면 트레이스를 X-Ray 서비스로 전달할 수 없습니다. 데몬이 실행 중이고 X-Ray 엔드포인트에 접근할 수 있는지 확인합니다.

4. **5단계 및 7단계의 샘플링 규칙 검토**: 5단계의 샘플링 규칙에서 매우 낮은 샘플링 비율(예: 0.01 = 1%)이거나 규칙이 애플리케이션의 트래픽 패턴을 제외하면 대부분의 트레이스가 설계상 삭제되고 있는 것입니다. 100%의 트레이스가 필요하면 샘플링 규칙을 조정합니다.

5. **9단계의 구성 변경과 상관 분석**: 9단계의 CloudTrail 이벤트에서 트레이스 사라짐 30분 이내에 X-Ray 구성 변경, IAM 역할 변경 또는 샘플링 규칙 업데이트가 표시되면 최근 변경이 문제를 유발한 것입니다.

**상관관계를 찾을 수 없는 경우**: 3단계의 트레이스 패턴을 사용하여 분석을 30일로 확장합니다. X-Ray SDK가 애플리케이션 코드에 올바르게 통합되어 있고 계측이 활성화되어 있는지 확인합니다. Lambda 함수의 경우 활성 추적이 활성화되어 있는지 확인합니다.