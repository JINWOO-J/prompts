---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/13-Proactive/05-Observability/SLO-SLI-Monitoring-K8s.md)'
role: SRE / K8s Proactive Operations
origin: scoutflo
tags:
- compliance
- infrastructure
- k8s-deployment
- k8s-namespace
- k8s-pod
- k8s-service
- monitoring
- observability
- performance
---

# SLO/SLI Monitoring — SLO/SLI 모니터링

## 의미

SLO/SLI 모니터링은 Service Level Objective와 Service Level Indicator 모니터링을 수행할 수 없거나 SLO/SLI 위반이 감지되었음을 나타냅니다(SLOViolation 또는 SLIMonitoringFailed 같은 알림 발생).
 SLO/SLI 메트릭이 사용 불가하거나, SLO/SLI 모니터링 도구가 실패하거나, SLO/SLI 위반이 감지되거나, SLO/SLI 구성이 누락되거나, SLO/SLI 모니터링에서 문제가 감지되는 것이 원인입니다. SLO/SLI 모니터링에서 실패가 나타나고, SLO/SLI 메트릭이 사용 불가하며, SLO/SLI 위반이 감지되고, SLO/SLI 모니터링이 실패합니다. 이는 성능 모니터링 계층과 서비스 수준 관리에 영향을 미치며, 일반적으로 SLO/SLI 구성 실패, SLO/SLI 모니터링 도구 실패, SLO/SLI 메트릭 수집 문제, 또는 SLO/SLI 모니터링 격차로 인해 발생합니다. SLO/SLI 모니터링이 컨테이너 워크로드에 영향을 미치면 컨테이너 SLO/SLI가 사용 불가하고 애플리케이션에서 서비스 수준 관리 실패가 발생할 수 있습니다.

## 영향

SLOViolation 알림 발생, SLIMonitoringFailed 알림 발생, SLO/SLI 모니터링 수행 불가, SLO/SLI 위반 감지, 서비스 수준 관리 저하 가능, 서비스 수준 준수 위험 가능. SLO/SLI 모니터링에서 실패가 나타나며, SLO/SLI 모니터링이 컨테이너 워크로드에 영향을 미치면 컨테이너 SLO/SLI가 사용 불가하고, Pod 서비스 수준이 모니터링되지 않으며, 컨테이너 애플리케이션에서 서비스 수준 관리 실패가 발생할 수 있습니다. 애플리케이션에서 SLO/SLI 모니터링 격차 또는 서비스 수준 준수 위험이 발생할 수 있습니다.

## 플레이북

1. 네임스페이스 <namespace>에서 app=<service-name> 레이블의 Pod를 wide 출력으로 조회하여 서비스 Pod의 현재 상태, 준비 상태, 가용성 메트릭을 확인합니다.
2. 네임스페이스 <namespace>의 최근 이벤트를 타임스탬프 순으로 조회하여 서비스 가용성 문제, Pod 실패, 지연 시간 관련 경고를 확인합니다.
3. 네임스페이스 <namespace>의 Deployment <service-name>을 상세 조회하여 레플리카 상태, 리소스 제한, 상태 점검 설정을 포함한 배포 구성을 확인합니다.
4. 지난 30일 동안의 서비스 `<service-name>`에 대한 Prometheus 메트릭(availability, latency, error_rate 등 SLI 메트릭 포함)을 조회하여 SLO 준수를 계산합니다.
5. SLO/SLI 모니터링 Pod 로그를 조회하고 지난 7일 이내의 SLO 위반 패턴 또는 SLI 모니터링 실패를 필터링합니다.
6. SLO 위반 감지 타임스탬프와 SLI 메트릭 임계값 초과 타임스탬프를 5분 이내로 비교하고, Prometheus 메트릭을 보조 증거로 사용하여 메트릭 초과가 SLO 위반을 유발하는지 확인합니다.
7. SLO/SLI 모니터링 도구 실행 결과를 조회하고 도구 가용성 및 모니터링 완료 상태를 확인합니다.
8. 서비스 `<service-name>`의 SLO/SLI 준수 이력을 조회하고 SLO 준수 추세와 SLI 메트릭 정확도를 확인합니다.
9. 서비스 `<service-name>`의 Prometheus 알림을 조회하고 알림 SLO/SLI 구성을 확인하여 SLO/SLI 모니터링이 없는 알림을 식별합니다.

## 진단

1. 4단계의 SLI 메트릭(availability, latency, error_rate)을 검토합니다. 메트릭이 SLO 임계값 미만의 값을 보이면 실제 서비스 성능 문제가 SLO 위반을 유발하고 있습니다. 메트릭이 정상인데 위반이 보고되면 SLO 구성이 잘못되었을 수 있습니다.

2. 7단계의 SLO/SLI 모니터링 도구 상태를 분석합니다. 도구에서 실패 또는 불완전 상태가 나타나면 모니터링 인프라 문제가 잘못된 위반 또는 누락된 위반을 유발할 수 있습니다. 도구가 정상이면 SLO 구성 분석으로 진행합니다.

3. 5단계의 로그에서 위반 패턴이 나타나면 위반이 특정 시간대에 집중되는지(트래픽 패턴 시사) 또는 무작위로 발생하는지(간헐적 서비스 문제 시사) 확인합니다.

4. 8단계의 SLO 준수 이력을 검토합니다. 30일 동안 준수가 하향 추세이면 체계적인 서비스 저하가 발생하고 있습니다. 준수가 변동하면 특정 인시던트가 일시적 위반을 유발하고 있습니다.

5. 9단계의 알림 커버리지에서 SLO/SLI 모니터링이 없는 서비스가 있으면 사각지대가 존재합니다. SLO 추적이 없는 주요 서비스에 대한 모니터링 추가를 우선합니다.

분석이 결론에 도달하지 못하는 경우: 2단계의 이벤트에서 Pod 실패나 지연 시간 관련 경고를 확인합니다. SLO 위반이 특정 배포 이벤트나 트래픽 급증과 상관관계가 있는지 판단합니다. SLO 목표가 현실적인 서비스 성능 기대치에 맞게 적절히 보정되어 있는지 확인합니다.
