---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/13-Proactive/05-Observability/Log-Coverage-Analysis-K8s.md)'
role: SRE / K8s Proactive Operations
origin: scoutflo
tags:
- analysis
- coverage
- infrastructure
- k8s-daemonset
- k8s-deployment
- k8s-namespace
- k8s-pod
- logging
- monitoring
- observability
---

# Log Coverage Analysis — 로그 커버리지 분석

## 의미

로그 커버리지 분석은 로그 수집 커버리지가 불완전하거나 로그 커버리지 격차가 감지되었음을 나타냅니다(LogCoverageIncomplete 또는 LogCollectionGapDetected 같은 알림 발생).
 Pod 로그가 구성되지 않았거나, 로그 수집 에이전트가 설치되지 않았거나, 로그 커버리지 분석 도구가 실패하거나, 로그 커버리지 모니터링에서 격차가 감지되거나, 로그 수집 커버리지가 불충분한 것이 원인입니다. 로그 커버리지 격차가 감지되고, Pod 로그가 구성되지 않았으며, 로그 수집 에이전트가 누락되고, 로그 커버리지 분석이 실패합니다. 이는 관측성 계층과 로그 모니터링 커버리지에 영향을 미치며, 일반적으로 로그 구성 실패, 로그 수집 에이전트 설치 문제, 로그 커버리지 분석 도구 실패, 또는 로그 커버리지 모니터링 격차로 인해 발생합니다. 로그 커버리지가 컨테이너 워크로드에 영향을 미치면 컨테이너 로그가 수집되지 않고 애플리케이션에서 로그 모니터링 사각지대가 발생할 수 있습니다.

## 영향

LogCoverageIncomplete 알림 발생, LogCollectionGapDetected 알림 발생, 로그 수집 커버리지 불완전, 로그 커버리지 격차 감지, 로그 모니터링 불충분 가능, 문제 해결 어려움 가능. 로그 커버리지 격차가 감지되며, 로그 커버리지가 컨테이너 워크로드에 영향을 미치면 컨테이너 로그가 수집되지 않고, Pod 로그가 누락되며, 컨테이너 애플리케이션에서 로그 모니터링 사각지대가 발생할 수 있습니다. 애플리케이션에서 로그 커버리지 격차 또는 로그 수집 실패가 발생할 수 있습니다.

## 플레이북

1. 네임스페이스 <namespace>의 Pod, Deployment, DaemonSet을 wide 출력으로 조회하고 <logging-namespace> 네임스페이스의 DaemonSet <log-collector-daemonset>을 상세 조회하여 로그 수집 인프라와 Pod 로깅 상태를 파악합니다.

2. 네임스페이스 <namespace>와 <logging-namespace>의 최근 이벤트를 타임스탬프 순으로 조회하여 로그 수집 실패나 문제를 확인합니다.

3. 네임스페이스 `<namespace>`의 Pod를 조회하고 Pod 로그 구성 및 로그 수집 에이전트 설치 상태를 확인하여 Pod 수준 로그 커버리지를 점검합니다.

4. 네임스페이스 `<namespace>`의 Deployment를 조회하고 Deployment 로그 구성 및 로그 수집 설정을 확인하여 Deployment 로그 커버리지를 점검합니다.

5. 네임스페이스 `<namespace>`의 Service를 조회하고 서비스 로그 구성 및 로그 수집 설정을 확인하여 서비스 로그 커버리지를 점검합니다.

6. 로그 수집 Pod 로그를 조회하고 지난 7일 동안의 로그 스트림 활동을 확인하여 비활성 로그 스트림이나 로그 수집 실패를 식별합니다.

7. 로그 커버리지 분석 결과와 Pod 배포 타임스탬프를 비교하고, Pod 구성 데이터를 보조 증거로 사용하여 새 Pod 배포 시 로그 수집이 구성되는지 확인합니다.

8. 네임스페이스 `<namespace>` Pod의 로그 수집 에이전트 상태를 조회하고 에이전트 상태 및 로그 수집 상태를 확인합니다.

9. 로그 수집 구성을 조회하고 Pod에 대한 로그 수집 커버리지를 확인하여 로그 수집이 없는 Pod를 식별합니다.

10. 지난 7일 동안의 로그 수집에 대한 Prometheus 메트릭(log_collection_success_rate, log_collection_latency 포함)을 조회하여 로그 수집 문제를 확인합니다.

## 진단

1. 3단계의 Pod 로그 구성 상태를 검토합니다. Pod에 로그 수집 구성이 없으면 이것이 주요 커버리지 격차입니다. 에이전트 사이드카 누락, 잘못된 로그 경로, 또는 어노테이션 누락 중 어떤 문제인지 확인합니다.

2. 8단계의 로그 수집 에이전트 상태를 분석합니다. 에이전트가 비정상 상태이거나 배포가 누락되면 인프라 수준 문제가 로그 수집을 방해하고 있습니다. 에이전트가 정상이면 Pod 수준 구성이 문제입니다.

3. 6단계의 로그 스트림 활동에서 비활성 스트림이 나타나면 로그 수집이 구성되었지만 작동하지 않는 것입니다. 스트림이 활성이지만 10단계의 메트릭에서 높은 수집 지연 또는 낮은 성공률이 나타나면 수집 성능 문제가 존재합니다.

4. 1단계의 DaemonSet 상태를 검토합니다. 로그 수집기 DaemonSet의 Pod가 모든 노드에서 실행되지 않으면 일부 워크로드에 로그 커버리지가 없습니다. 모든 DaemonSet Pod가 실행 중이면 구성 분석으로 진행합니다.

5. 7단계에서 새 Pod 배포 시 로그 수집이 구성되지 않으면 배포 템플릿이나 Admission Webhook을 업데이트하여 로그 수집 구성을 자동으로 포함해야 합니다.

분석이 결론에 도달하지 못하는 경우: 2단계의 이벤트에서 로그 수집 실패나 구성 문제를 확인합니다. 커버리지 격차가 특정 네임스페이스에 집중되어 있는지(네임스페이스 수준 구성 문제 시사) 또는 클러스터 전체에 분산되어 있는지(시스템적 문제 시사) 판단합니다. 로그 수집 자동화가 배포 파이프라인에 통합되어 있는지 확인합니다.
