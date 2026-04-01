---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/09-Resource-Management/HighCPUUsage-compute.md)'
role: Kubernetes SRE
origin: scoutflo
extract_date: 2026-03-05
tags:
- compute
- highcpuusage
- infrastructure
- k8s-namespace
- k8s-node
- k8s-pod
- kubernetes
- management
- performance
- resource
---

---
title: High CPU Usage - 높은 CPU 사용량
weight: 290
categories:
  - kubernetes
  - compute
---

# HighCPUUsage-compute

## 의미

하나 이상의 노드 또는 컨트롤 플레인 컴포넌트가 지속적으로 높은 CPU 사용률로 실행되고 있습니다(API 서버에 영향을 미치는 경우 KubeCPUOvercommit 또는 KubeAPILatencyHigh 알림 트리거 가능). 정상 운영이나 새 워크로드 트래픽을 위한 여유가 거의 없습니다.

## 영향

컨트롤 플레인 컴포넌트 느려짐, API 서버 응답 시간 증가, 클러스터 작업 지연, 노드 응답 불가 가능, 애플리케이션 성능 저하, CPU 스로틀링 발생, KubeAPILatencyHigh 알림 발생 가능, API 요청 처리 느려짐, 컨트롤러 조정 지연, 노드 리소스 압력 증가.

## 플레이북

1. 모든 노드를 나열하고 상태를 확인하여 높은 CPU 사용률의 노드를 식별합니다.

2. 모든 namespace의 이벤트를 타임스탬프 순으로 조회하고 CPU 관련 리소스 압력 이벤트를 필터링합니다.

3. 모든 노드의 CPU 사용량 메트릭을 조회하고 지속적으로 높은 사용률 임계값에서 실행되는 노드를 식별합니다.

4. `kube-system` namespace의 컨트롤 플레인 Pod(API 서버, controller-manager, scheduler, etcd)의 CPU 사용량 메트릭을 조회하고 핫스팟을 식별합니다.

5. 모든 namespace의 Pod를 CPU 사용량 메트릭과 함께 나열하고 비정상적으로 높은 CPU를 소비하는 특정 워크로드를 식별합니다.

6. `kube-system` namespace의 API 서버 Pod 로그를 조회하고 관찰된 CPU 스파이크와 상관될 수 있는 높은 요청 비율 또는 스로틀링 이벤트를 필터링합니다.

## 진단

플레이북 섹션에서 수집한 노드 상태, 이벤트, CPU 메트릭을 분석하는 것으로 시작합니다. 노드 조건, Pod CPU 소비 순위, 컨트롤 플레인 상태가 주요 진단 신호를 제공합니다.

**이벤트에 특정 노드의 CPU 압력 또는 EvictionThresholdMet이 표시되는 경우:**
- 해당 노드가 심각한 CPU 압력 상태입니다. 영향받는 노드에서 CPU 소비 상위 Pod를 식별합니다. 비핵심 워크로드의 퇴거 또는 재스케줄링을 고려합니다. 압력이 클러스터 전체인 경우 노드 용량을 추가합니다.

**컨트롤 플레인 Pod(API 서버, controller-manager, scheduler)가 높은 CPU를 보이는 경우:**
- 컨트롤 플레인이 과부하 상태입니다. API 서버 로그에서 스로틀링 메시지에 대한 요청 비율을 확인합니다. 최근 변경이 API 호출 빈도를 증가시켰는지 검토합니다(새 컨트롤러, Operator, CI/CD 파이프라인).

**특정 워크로드 Pod가 CPU 소비를 지배하는 경우:**
- 애플리케이션 수준 문제입니다. 해당 Pod에 CPU limit이 설정되어 있는지 확인합니다. 처리 루프 또는 비효율적인 코드에 대한 애플리케이션 로그를 검토합니다. 부하 분산을 위한 수평 스케일링을 고려합니다.

**CPU 스파이크가 예약된 CronJob과 일치하는 경우:**
- 배치 작업이 실행 시간 동안 CPU를 소비하고 있습니다. CronJob 스케줄에서 겹치는 실행 시간을 검토합니다. 작업 스케줄 분산 또는 배치 워크로드 전용 노드 풀 추가를 고려합니다.

**Deployment 롤아웃 후 CPU 사용량이 증가한 경우:**
- 새 애플리케이션 버전에 성능 회귀가 있을 수 있습니다. 메트릭 타임스탬프를 사용하여 롤아웃 전후의 CPU 사용량을 비교합니다. 회귀가 심각한 경우 롤백을 고려합니다.

**노드 CPU는 높지만 Pod CPU 요청이 낮은 경우:**
- 시스템 프로세스 또는 DaemonSet이 CPU를 소비하고 있을 수 있습니다. kubelet, 컨테이너 런타임, 로깅 에이전트의 CPU 사용량을 확인합니다. 영향받는 노드의 DaemonSet 리소스 소비를 검토합니다.

**이벤트가 불확실한 경우 타임스탬프를 상관 분석합니다:**
1. 레플리카 수를 증가시킨 HPA 스케일링 이벤트 후 CPU 스파이크가 시작되었는지 확인합니다.
2. 워크로드를 집중시킨 노드 제거와 CPU 증가가 일치하는지 확인합니다.
3. 클러스터 업그레이드가 성능 변화를 도입했는지 확인합니다.

**명확한 원인이 식별되지 않는 경우:** 애플리케이션이 지원하는 경우 높은 소비 Pod에서 CPU 프로파일링을 활성화합니다. CPU 요청 대비 실제 사용량을 검토하여 더 높은 limit 또는 최적화가 필요한 Pod를 식별합니다.
