---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/13-Proactive/05-Observability/Metric-Coverage-Gaps-K8s.md)'
role: SRE / K8s Proactive Operations
origin: scoutflo
tags:
- coverage
- gaps
- infrastructure
- k8s-namespace
- k8s-pod
- k8s-service
- metric
- monitoring
- observability
- performance
---

# Metric Coverage Gaps — 메트릭 커버리지 격차

## 의미

메트릭 커버리지 격차는 Prometheus 메트릭 수집 커버리지가 불완전하거나 메트릭 커버리지 격차가 감지되었음을 나타냅니다(MetricCoverageIncomplete 또는 MetricCollectionGapDetected 같은 알림 발생).
 Pod에 대한 Prometheus 메트릭이 수집되지 않거나, 커스텀 메트릭이 누락되거나, 메트릭 익스포터가 설치되지 않거나, 메트릭 커버리지 분석 도구가 실패하거나, 메트릭 커버리지 모니터링에서 격차가 감지되는 것이 원인입니다. 메트릭 커버리지 격차가 감지되고, Prometheus 메트릭이 수집되지 않으며, 커스텀 메트릭이 누락되고, 메트릭 커버리지 분석이 실패합니다. 이는 관측성 계층과 메트릭 모니터링 커버리지에 영향을 미치며, 일반적으로 메트릭 구성 실패, 메트릭 익스포터 설치 문제, 메트릭 커버리지 분석 도구 실패, 또는 메트릭 커버리지 모니터링 격차로 인해 발생합니다. 메트릭 커버리지가 컨테이너 워크로드에 영향을 미치면 컨테이너 메트릭이 수집되지 않고 애플리케이션에서 메트릭 모니터링 사각지대가 발생할 수 있습니다.

## 영향

MetricCoverageIncomplete 알림 발생, MetricCollectionGapDetected 알림 발생, 메트릭 수집 커버리지 불완전, 메트릭 커버리지 격차 감지, 메트릭 모니터링 불충분 가능, 성능 분석 어려움 가능. 메트릭 커버리지 격차가 감지되며, 메트릭 커버리지가 컨테이너 워크로드에 영향을 미치면 컨테이너 메트릭이 수집되지 않고, Pod 메트릭이 누락되며, 컨테이너 애플리케이션에서 메트릭 모니터링 사각지대가 발생할 수 있습니다. 애플리케이션에서 메트릭 커버리지 격차 또는 메트릭 수집 실패가 발생할 수 있습니다.

## 플레이북

1. 네임스페이스 <namespace>의 Pod, Service, ServiceMonitor를 wide 출력으로 조회하고 ServiceMonitor <servicemonitor-name>을 상세 조회하여 메트릭 수집 구성과 커버리지를 파악합니다.

2. 네임스페이스 <namespace>와 <monitoring-namespace>의 최근 이벤트를 타임스탬프 순으로 조회하여 메트릭 수집 실패나 구성 문제를 확인합니다.

3. 네임스페이스 `<namespace>` 서비스의 Prometheus 메트릭 네임스페이스 커버리지를 조회하고 메트릭 수집 커버리지를 확인하여 메트릭이 없는 서비스를 식별합니다.

4. 네임스페이스 `<namespace>`의 Pod를 조회하고 Prometheus 메트릭 익스포터 설치 상태 및 메트릭 수집 구성을 확인하여 Pod 수준 메트릭 커버리지를 점검합니다.

5. 네임스페이스 `<namespace>`의 Deployment를 조회하고 Deployment 메트릭 구성 및 메트릭 익스포터 연결을 확인하여 Deployment 메트릭 커버리지를 점검합니다.

6. 네임스페이스 `<namespace>`의 Service를 조회하고 Prometheus ServiceMonitor 구성 및 서비스 메트릭 수집 설정을 확인하여 서비스 메트릭 커버리지를 점검합니다.

7. 서비스 네임스페이스의 Prometheus 메트릭을 조회하고 지난 7일 동안의 메트릭 가용성을 확인하여 누락된 메트릭이나 메트릭 수집 실패를 식별합니다.

8. 메트릭 커버리지 분석 결과와 Pod 배포 타임스탬프를 비교하고, Pod 구성 데이터를 보조 증거로 사용하여 새 Pod 배포 시 메트릭이 구성되는지 확인합니다.

9. 네임스페이스 `<namespace>` Pod의 Prometheus 메트릭 익스포터 상태를 조회하고 익스포터 상태 및 메트릭 수집 상태를 확인합니다.

10. Prometheus 커스텀 메트릭을 조회하고 서비스에 대한 커스텀 메트릭 커버리지를 확인하여 커스텀 메트릭이 없는 서비스를 식별합니다.

## 진단

1. 3단계의 메트릭 네임스페이스 커버리지를 검토합니다. 서비스에 Prometheus 메트릭이 없으면 이것이 주요 커버리지 격차입니다. ServiceMonitor 누락, 잘못된 레이블 셀렉터, 또는 메트릭 엔드포인트 누락 중 어떤 문제인지 확인합니다.

2. 4단계의 Pod 수준 메트릭 익스포터 상태를 분석합니다. 익스포터가 설치되지 않았거나 잘못 구성되면 Pod가 수집을 위한 메트릭을 노출할 수 없습니다. 익스포터가 있지만 9단계에서 비정상 상태가 나타나면 익스포터 유지보수가 필요합니다.

3. 6단계의 ServiceMonitor 구성이 존재하지만 7단계의 메트릭 가용성에서 격차가 나타나면 레이블 매칭이나 포트 구성이 잘못되었을 수 있습니다. ServiceMonitor가 완전히 누락되면 메트릭 수집 인프라를 배포해야 합니다.

4. 10단계의 커스텀 메트릭 커버리지를 검토합니다. 서비스에 기본 리소스 메트릭 외에 커스텀 메트릭이 없으면 비즈니스 모니터링 요구에 대한 애플리케이션별 관측성이 불충분할 수 있습니다.

5. 8단계에서 새 Pod 배포 시 메트릭이 없으면 배포 자동화에 메트릭 구성을 포함해야 합니다. 기존 Pod가 시간이 지나면서 메트릭을 잃으면 구성 드리프트 또는 익스포터 실패가 발생하고 있는 것입니다.

분석이 결론에 도달하지 못하는 경우: 2단계의 이벤트에서 메트릭 수집 실패나 Prometheus 스크레이프 오류를 확인합니다. 커버리지 격차가 특정 서비스 유형에 집중되어 있는지(템플릿 문제 시사) 또는 무작위로 분산되어 있는지(표준 없는 비표준 배포 시사) 판단합니다. Prometheus 서비스 가용성과 용량이 워크로드에 충분한지 확인합니다.
