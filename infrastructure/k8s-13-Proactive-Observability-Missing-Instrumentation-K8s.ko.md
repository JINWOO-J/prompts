---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/13-Proactive/05-Observability/Missing-Instrumentation-K8s.md)'
role: SRE / K8s Proactive Operations
origin: scoutflo
tags:
- infrastructure
- instrumentation
- k8s-deployment
- k8s-namespace
- k8s-pod
- k8s-service
- missing
- monitoring
- observability
---

# Missing Instrumentation — 누락된 계측

## 의미

누락된 계측은 Pod 또는 서비스가 관측성을 위해 적절히 계측되지 않았거나 계측 격차가 감지되었음을 나타냅니다(InstrumentationMissing 또는 ObservabilityGapDetected 같은 알림 발생).
 Prometheus 메트릭이 수집되지 않거나, Pod 로그가 구성되지 않거나, 분산 트레이싱이 활성화되지 않거나, 커스텀 메트릭이 누락되거나, 계측 커버리지가 불완전한 것이 원인입니다. 계측 격차가 감지되고, Prometheus 메트릭이 누락되며, Pod 로그가 구성되지 않고, 계측 커버리지가 불완전합니다. 이는 관측성 계층과 모니터링 커버리지에 영향을 미치며, 일반적으로 계측 구성 실패, 모니터링 도구 비가용, 계측 배포 문제, 또는 계측 커버리지 격차로 인해 발생합니다. 누락된 계측이 컨테이너 워크로드에 영향을 미치면 컨테이너 관측성이 불완전하고 애플리케이션에서 모니터링 사각지대가 발생할 수 있습니다.

## 영향

InstrumentationMissing 알림 발생, ObservabilityGapDetected 알림 발생, Pod가 적절히 계측되지 않음, 모니터링 커버리지 불완전, 관측성 격차 존재, 문제 해결 어려움 가능. 계측 격차가 감지되며, 누락된 계측이 컨테이너 워크로드에 영향을 미치면 컨테이너 관측성이 불완전하고, Pod 메트릭이 누락되며, 컨테이너 애플리케이션에서 모니터링 사각지대가 발생할 수 있습니다. 애플리케이션에서 관측성 격차 또는 모니터링 실패가 발생할 수 있습니다.

## 플레이북

1. 네임스페이스 <namespace>의 Pod, Deployment, Service를 wide 출력으로 조회하고 Deployment <deployment-name>을 상세 조회하여 계측 구성을 파악하고 적절한 관측성 설정이 없는 Pod를 식별합니다.

2. 네임스페이스 <namespace>의 최근 이벤트를 타임스탬프 순으로 조회하여 Pod 시작 중 계측 관련 실패나 구성 문제를 확인합니다.

3. 네임스페이스 `<namespace>`의 Pod를 조회하고 Prometheus 메트릭 수집 상태 및 메트릭 익스포터 구성을 확인하여 Pod 수준 계측을 점검합니다.

4. 네임스페이스 `<namespace>`의 Deployment를 조회하고 Pod 로그 구성 및 분산 트레이싱 활성화 상태를 확인하여 Deployment 계측을 점검합니다.

5. 네임스페이스 `<namespace>`의 Service를 조회하고 서비스 모니터링 구성 및 메트릭 수집 설정을 확인하여 서비스 계측을 점검합니다.

6. 네임스페이스 `<namespace>` 서비스의 Prometheus 메트릭 네임스페이스 커버리지를 조회하고 메트릭 수집 커버리지를 확인하여 메트릭이 없는 서비스를 식별합니다.

7. 지난 7일 동안의 Pod 메트릭에 대한 Prometheus 메트릭(pod_metrics_available, pod_logs_configured 포함)을 조회하여 누락된 메트릭이나 메트릭 수집 실패를 식별합니다.

8. 계측 커버리지 분석 결과와 Pod 배포 타임스탬프를 비교하고, Pod 구성 데이터를 보조 증거로 사용하여 새 Pod 배포 시 계측이 적용되는지 확인합니다.

9. 네임스페이스 `<namespace>` Pod의 Prometheus 익스포터 상태를 조회하고 익스포터 상태 및 메트릭 수집 상태를 확인합니다.

10. Prometheus ServiceMonitor를 조회하고 서비스에 대한 ServiceMonitor 커버리지를 확인하여 ServiceMonitor가 없는 서비스를 식별합니다.

## 진단

1. 3~5단계의 Pod 수준 계측 상태를 검토합니다. Pod에 Prometheus 메트릭 수집, 로그 구성, 또는 분산 트레이싱 활성화가 없으면 운영 중요도에 따라 각 격차 해결의 우선순위를 정합니다.

2. 6~7단계의 메트릭 계측을 분석합니다. 서비스에 Prometheus 메트릭이 없거나 메트릭 수집 상태에서 실패가 나타나면 메트릭 관측성이 저하된 것입니다. 익스포터 설치와 ServiceMonitor 구성에 집중합니다.

3. 9단계의 익스포터 상태에서 비정상 익스포터가 나타나면 기존 계측이 실패하고 있습니다. 익스포터가 정상이지만 10단계의 ServiceMonitor 커버리지에서 격차가 나타나면 수집 구성이 문제입니다.

4. 4단계의 Deployment 계측을 검토합니다. Deployment에 로그 구성이나 분산 트레이싱이 없으면 디버깅 및 성능 분석을 위한 애플리케이션 수준 관측성이 제한됩니다.

5. 8단계에서 새 Pod 배포 시 계측이 없으면 배포 템플릿과 자동화 파이프라인을 업데이트하여 관측성 구성을 표준 관행으로 포함해야 합니다.

분석이 결론에 도달하지 못하는 경우: 2단계의 이벤트에서 Pod 시작 중 계측 관련 실패를 확인합니다. 계측 격차가 모든 관측성 축(메트릭, 로그, 트레이스)에 영향을 미치는지 또는 특정 축에만 영향을 미치는지 판단합니다. 운영 요구에 따라 우선순위를 정하고 계측 자동화가 CI/CD 파이프라인에 통합되어 있는지 확인합니다.
