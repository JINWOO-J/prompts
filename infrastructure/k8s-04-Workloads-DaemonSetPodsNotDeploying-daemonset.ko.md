---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/04-Workloads/DaemonSetPodsNotDeploying-daemonset.md)'
role: SRE / K8s Incident Response
origin: scoutflo
tags:
- daemonset
- daemonsetpodsnotdeploying
- infrastructure
- k8s-daemonset
- k8s-deployment
- k8s-namespace
- k8s-node
- k8s-pod
- k8s-service
- kubernetes
- logging
- monitoring
- networking
- workloads
---

---
title: DaemonSet Pods Not Deploying - DaemonSet
weight: 239
categories:
  - kubernetes
  - daemonset
---

# DaemonSet Pod가 배포되지 않음 (DaemonSetPodsNotDeploying-daemonset)

## 의미

DaemonSet Pod가 Node에 배포되지 않는 상태입니다(DaemonSet 관련 알림 발생). Node Selector가 사용 가능한 Node와 일치하지 않거나, Toleration이 Node Taint와 일치하지 않거나, 리소스 제약으로 Pod 생성이 불가능하거나, DaemonSet 컨트롤러가 작동하지 않기 때문입니다. kubectl에서 DaemonSet의 스케줄된 수가 불일치하며, Pod가 Pending 상태로 남고, Pod 이벤트에 FailedCreate 또는 스케줄링 오류가 표시됩니다. 이는 워크로드 플레인에 영향을 미치며 DaemonSet Pod가 생성되지 않게 합니다. 주로 Node Selector/Toleration 불일치, 리소스 제약 또는 DaemonSet 컨트롤러 문제가 원인이며, Node 수준 기능을 사용할 수 없습니다.

## 영향

DaemonSet Pod가 생성되지 않으며, Node 수준 기능을 사용할 수 없습니다. 모니터링, 로깅 또는 네트워킹 구성 요소가 누락되고, DaemonSet의 원하는 Node 수와 준비된 수가 일치하지 않습니다. KubeDaemonSetNotReady 알림이 발생할 수 있으며, 클러스터 기능이 저하되고, Node별 서비스가 실행되지 않습니다. DaemonSet의 스케줄된 수 불일치가 무기한 지속되고, Pod가 Pending 상태로 남으며, Node 수준 기능을 사용할 수 없어 오류가 발생할 수 있습니다.

## 플레이북

1. namespace <namespace>에서 DaemonSet <daemonset-name>을 describe하여 다음을 확인합니다:
   - 원하는 Node 수 대비 현재/준비 수
   - Node Selector, Toleration 및 Affinity 규칙 설정
   - Pod가 배포되지 않는 이유를 보여주는 Condition
   - FailedCreate 또는 스케줄링 오류를 보여주는 Event

2. namespace <namespace>에서 DaemonSet <daemonset-name>의 이벤트를 타임스탬프 순으로 조회하여 배포 실패 순서를 확인합니다.

3. kube-system namespace에서 kube-controller-manager Pod를 조회하고 컨트롤러 로그를 확인하여 DaemonSet 컨트롤러가 실행 중인지 검증합니다.

4. 모든 Node를 조회하고 Node를 describe하여 Label, Taint, 스케줄링 상태를 확인하고 DaemonSet의 요구사항과 일치하는 Node가 있는지 검증합니다.

5. Node 리소스 사용량 메트릭을 조회하여 CPU, 메모리 또는 기타 리소스 부족이 DaemonSet Pod 생성을 방해하는지 확인합니다.

6. namespace <namespace>에서 PodDisruptionBudget 리소스를 조회하여 DaemonSet Pod 생성을 방해하는 충돌이 있는지 확인합니다.

## 진단

1. 플레이북의 DaemonSet 이벤트를 분석하여 Pod가 배포되지 않는 이유를 파악합니다. "FailedCreate" 이벤트는 컨트롤러가 Pod를 생성할 수 없음을 나타냅니다. 여러 Node에서 "FailedScheduling" 이벤트는 클러스터 전체 스케줄링 제약을 나타냅니다.

2. 이벤트가 컨트롤러 문제를 나타내면(이벤트가 생성되지 않거나 오래된 이벤트만 있는 경우), 플레이북에서 kube-controller-manager 상태를 확인합니다. DaemonSet 컨트롤러는 kube-controller-manager 내에서 실행되며 Pod를 생성하려면 정상이어야 합니다.

3. 이벤트가 모든 Node에서 Node Selector 불일치를 나타내면, DaemonSet의 nodeSelector가 어떤 Node에도 없는 Label을 지정하고 있을 수 있습니다. 클러스터에서 최소한 일부 Node에 필요한 Label이 있는지 확인합니다. 이는 DaemonSet 설정 변경 또는 Node Pool 마이그레이션 후에 흔히 발생합니다.

4. 이벤트가 모든 Node에서 Taint 관련 실패를 나타내면, 클러스터 전체 Node Taint와 DaemonSet Toleration을 비교합니다. 단일 Node 클러스터의 Control Plane Taint처럼 모든 Node에 DaemonSet이 허용하지 않는 Taint가 있을 수 있습니다.

5. 이벤트가 클러스터 전체 리소스 제약을 나타내면(모든 Node에서 InsufficientCPU, InsufficientMemory), DaemonSet의 리소스 요청이 모든 Node의 사용 가능한 용량을 초과하는 것입니다. Pod 리소스 요청과 Node 할당 가능 리소스를 비교하여 확인합니다.

6. Pod가 존재하지 않고 스케줄링 이벤트도 없으면, DaemonSet의 원하는 스케줄 수가 0보다 큰지 확인합니다. nodeSelector 또는 nodeAffinity 규칙이 클러스터의 모든 Node를 제외하는지 확인합니다.

7. DaemonSet 컨트롤러가 실행 중이지만 Pod가 생성되지 않으면, DaemonSet namespace의 리소스 Quota 제한이 Pod 생성을 방해하는지 확인합니다. 또한 namespace에 DaemonSet Pod 스펙과 충돌하는 LimitRange가 있는지 확인합니다.
