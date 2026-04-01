---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/04-Workloads/DaemonSetPodsNotRunningonSpecificNode-daemonset.md)'
role: SRE / K8s Incident Response
origin: scoutflo
tags:
- daemonset
- daemonsetpodsnotrunningonspecificnode
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
title: DaemonSet Pods Not Running on Specific Node - DaemonSet
weight: 264
categories:
  - kubernetes
  - daemonset
---

# DaemonSet Pod가 특정 Node에서 실행되지 않음 (DaemonSetPodsNotRunningonSpecificNode-daemonset)

## 의미

DaemonSet Pod가 특정 Node에서 실행되지 않는 상태입니다(DaemonSet 관련 알림 발생). 해당 Node에 DaemonSet의 매칭되는 Toleration 없이 Taint가 설정되어 있거나, Node Selector가 해당 Node의 Label과 일치하지 않거나, 리소스 부족으로 Pod 생성이 불가능하거나, Node가 스케줄링 불가 상태이기 때문입니다.
해당 Node에서 DaemonSet의 스케줄된 수가 불일치하며, Pod가 Pending 상태로 남고, Pod 이벤트에 FailedCreate 또는 스케줄링 오류가 표시됩니다. 이는 워크로드 플레인에 영향을 미치며 특정 Node에 DaemonSet Pod가 생성되지 않게 합니다. 주로 Node Taint/Toleration 불일치 또는 리소스 제약이 원인이며, 해당 Node에서 Node 수준 기능을 사용할 수 없습니다.

## 영향

특정 Node에서 DaemonSet Pod가 누락되어 해당 Node의 Node 수준 기능을 사용할 수 없습니다. 모니터링, 로깅 또는 네트워킹 구성 요소가 누락되고, DaemonSet의 원하는 Node 수와 준비된 수가 일치하지 않습니다. KubeDaemonSetNotReady 알림이 발생할 수 있고, 영향받는 Node에서 Node별 서비스가 실행되지 않으며, 클러스터 기능이 일관되지 않습니다. 해당 Node에서 DaemonSet의 스케줄된 수 불일치가 무기한 지속되고, Pod가 Pending 상태로 남으며, 해당 Node에서 Node 수준 기능을 사용할 수 없어 오류가 발생할 수 있습니다.

## 플레이북

1. namespace <namespace>에서 DaemonSet <daemonset-name>을 describe하여 다음을 확인합니다:
   - 원하는 Pod 수 대비 준비된 수
   - Node Selector, Toleration 및 Affinity 규칙 설정
   - 특정 Node에서 Pod가 실행되지 않는 이유를 보여주는 Condition
   - FailedCreate 또는 스케줄링 오류를 보여주는 Event

2. namespace <namespace>에서 DaemonSet <daemonset-name>의 이벤트를 타임스탬프 순으로 조회하여 배포 실패 순서를 확인합니다.

3. kube-system namespace에서 kube-controller-manager Pod를 조회하여 DaemonSet 컨트롤러가 실행 중인지 확인합니다.

4. node <node-name>을 describe하여 Label, Taint, 스케줄링 상태를 검사하고 DaemonSet 요구사항과 일치하는지 확인합니다.

5. node <node-name>의 리소스 사용량 메트릭을 조회하여 CPU, 메모리 또는 기타 리소스 부족이 DaemonSet Pod 생성을 방해하는지 확인합니다.

6. namespace <namespace>에서 PodDisruptionBudget 리소스를 조회하여 특정 Node에서 DaemonSet Pod 생성을 방해하는 충돌이 있는지 확인합니다.

## 진단

1. 플레이북의 DaemonSet 및 Pod 이벤트를 분석하여 특정 Node에서 Pod가 실행되지 않는 이유를 파악합니다. Node 이름이 포함된 "FailedScheduling" 이벤트는 해당 Node에 특정한 스케줄링 제약을 나타냅니다. "FailedCreate" 이벤트는 Pod 생성 차단 요인을 나타냅니다.

2. 이벤트가 특정 Node의 Taint 관련 실패를 나타내면, 해당 Node의 Taint와 DaemonSet Toleration을 비교합니다. 특정 Node에 사용자 정의 워크로드 격리 Taint 또는 유지보수 Taint와 같이 다른 Node에는 없는 Taint가 있을 수 있습니다.

3. 이벤트가 특정 Node의 리소스 제약을 나타내면(InsufficientCPU, InsufficientMemory), 해당 Node의 사용 가능한 리소스와 DaemonSet Pod가 실행 중인 다른 Node를 비교합니다. 특정 Node에 다른 워크로드로 인한 더 높은 사용률이 있을 수 있습니다.

4. 특정 Node의 Label이 DaemonSet nodeSelector와 일치하지 않으면, 이 Node에 필요한 Label이 있어야 하는지 확인합니다. 해당 Node에 다른 Node가 가진 Label이 누락되었거나 다른 Node Pool에 추가되었을 수 있습니다.

5. Node가 Cordon되었거나 spec.unschedulable=true이면 DaemonSet Pod를 스케줄링할 수 없습니다. 플레이북에서 Node 상태를 확인하여 유지보수를 위해 의도적으로 스케줄링 불가로 표시되었는지 파악합니다.

6. Node가 NotReady 상태이거나 리소스 압박 Condition(MemoryPressure, DiskPressure, PIDPressure)이 있으면 kubelet이 새 Pod를 수락하지 않을 수 있습니다. Node Condition과 특정 Node의 kubelet 상태를 확인합니다.

7. 스케줄링 이벤트가 없고 해당 Node에 Pod가 단순히 존재하지 않으면, Node가 nodeSelector, nodeAffinity, Toleration을 포함한 모든 DaemonSet 스케줄링 요구사항을 충족하는지 확인합니다. 또한 PodDisruptionBudget이 필요한 Eviction을 차단하여 Pod 생성을 방해하는지 확인합니다.
