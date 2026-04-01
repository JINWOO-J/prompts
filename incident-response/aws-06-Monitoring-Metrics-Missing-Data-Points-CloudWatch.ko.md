---
category: incident-response
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/AWS%20Playbooks/06-Monitoring/Metrics-Missing-Data-Points-CloudWatch.md)'
role: SRE / AWS Incident Response
origin: scoutflo
extract_date: 2026-03-05
tags:
- cloudwatch
- data
- incident-response
- k8s-namespace
- k8s-service
- metrics
- missing
- monitoring
- observability
- performance
- points
- sts
---

# CloudWatch Metrics Missing Data Points - CloudWatch 지표 데이터 포인트 누락

## 의미

CloudWatch 지표에 데이터 포인트가 누락되는 현상(모니터링 격차 또는 CloudWatchMetricsMissing 경보 트리거)은 지표 네임스페이스가 잘못되었거나, 지표 차원이 일치하지 않거나, 지표 게시가 실패하거나, 지표 보존 기간이 만료되거나, CloudWatch Metrics 서비스가 데이터 수집 중 오류를 만나거나, 지표 게시 애플리케이션 오류가 데이터 제출을 방해할 때 발생합니다.
 CloudWatch 지표에 데이터 포인트가 누락되고, 모니터링 데이터가 불완전하며, 지표 기반 경보가 평가할 수 없습니다. 이는 모니터링 및 관측성 계층에 영향을 미치며 모니터링 가시성을 감소시킵니다.

## 영향

CloudWatch 지표에 데이터 포인트가 누락됩니다. 모니터링 데이터가 불완전합니다. 지표 기반 경보가 평가할 수 없습니다. 지표 그래프에 격차가 표시됩니다. 모니터링 가시성이 감소합니다. 지표 보존으로 데이터 손실이 발생합니다. 지표 게시가 실패합니다. 관측성이 손상됩니다.

## 플레이북

1. 지표 네임스페이스 `<namespace>`가 존재하고 리전 `<region>`의 CloudWatch Metrics AWS 서비스 상태가 정상인지 확인합니다.
2. 지표 네임스페이스 `<namespace>` 및 지표 이름 `<metric-name>`의 CloudWatch 지표를 최근 24시간 동안 조회하여 누락된 데이터 포인트 패턴과 격차를 파악합니다.
3. 애플리케이션 로그가 포함된 CloudWatch Logs에서 CloudWatch 지표 게시 오류나 PutMetricData API 호출 실패를 필터링합니다.
4. 지표 네임스페이스 `<namespace>` 및 지표 이름 `<metric-name>`의 CloudWatch 지표 메타데이터를 조회하여 가용한 차원, 지표 속성, 지표 통계를 점검합니다.
5. 네임스페이스 `<namespace>`의 CloudWatch 지표를 나열하고 여러 지표에 걸친 데이터 포인트 가용성을 비교하여 문제가 지표 고유의 것인지 판단합니다.
6. CloudTrail 이벤트가 포함된 CloudWatch Logs에서 CloudWatch PutMetricData API 호출 실패나 지표 게시 오류를 필터링합니다.
7. CloudWatch Metrics 서비스의 CloudWatch 지표(가용한 경우 PutMetricData 오류)를 조회하여 서비스 상태를 확인합니다.
8. 지표 네임스페이스 `<namespace>`의 CloudWatch 지표 보존 설정을 조회하여 보존 기간을 확인합니다.
9. CloudTrail 이벤트가 포함된 CloudWatch Logs에서 최근 7일 이내 지표 네임스페이스 또는 차원 변경 이벤트를 필터링합니다.

## 진단

1. CloudWatch 지표 데이터(플레이북 2단계)를 분석하여 최근 24시간 동안의 누락된 데이터 포인트 패턴을 파악합니다. 데이터 포인트가 정기적 간격으로 지속적으로 누락되면 지표 게시 애플리케이션이 중지되었거나 주기적으로 실패하고 있을 수 있습니다.

2. 지표 게시 오류에 대한 CloudWatch Logs(플레이북 3단계 및 6단계)를 검토하여 PutMetricData API 호출 실패를 파악합니다. "AccessDenied" 오류가 표시되면 게시 애플리케이션의 IAM 권한을 확인합니다.

3. 지표 메타데이터 및 차원(플레이북 4단계)을 확인하여 차원 구성이 예상 값과 일치하는지 검증합니다. 지표 차원이 변경되었거나 일관되지 않으면 데이터 포인트가 다른 지표 조합으로 게시되어 예상 지표에서 데이터 격차가 나타날 수 있습니다.

4. 동일 네임스페이스의 여러 지표에 걸친 지표 가용성(플레이북 5단계)을 비교합니다. 네임스페이스의 모든 지표에 데이터가 누락되면 게시 애플리케이션 또는 서비스가 중지된 것입니다.

5. 지표 보존 설정(플레이북 8단계)을 확인하여 이전 데이터 포인트가 보존 정책에 따라 만료되었는지 판단합니다. 고해상도 지표(1초)는 3시간, 60초 지표는 15일 동안 보존됩니다.

6. CloudTrail 이벤트(플레이북 9단계)와 누락된 데이터 포인트 타임스탬프를 5분 이내로 상관 분석합니다.

상관관계를 찾을 수 없는 경우: 기간을 30일로 확장하고, 지표 게시 애플리케이션 코드 및 CloudWatch 서비스 상태를 포함한 대안적 증거 소스를 검토합니다.