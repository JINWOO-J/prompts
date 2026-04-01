---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/04-Workloads/DaemonSetNotDeployingPodsonAllNodes-daemonset.md)'
role: SRE / K8s Incident Response
origin: scoutflo
tags:
- daemonset
- daemonsetnotdeployingpodsonallnodes
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
title: DaemonSet Not Deploying Pods on All Nodes - DaemonSet
weight: 220
categories:
  - kubernetes
  - daemonset
---

# DaemonSet이 모든 Node에 Pod를 배포하지 않음 (DaemonSetNotDeployingPodsonAllNodes-daemonset)

## 의미

DaemonSet Pod가 모든 Node에 배포되지 않는 상태입니다(DaemonSet 관련 알림 발생). Node Selector 또는 Affinity 규칙이 Pod를 실행할 수 있는 Node를 제한하거나, Node Taint가 매칭되는 Toleration 없이 스케줄링을 차단하거나, Node의 리소스 부족으로 Pod 생성이 불가능하거나, Node가 스케줄링 불가 상태이기 때문입니다. kubectl에서 DaemonSet의 스케줄된 수가 불일치하며, 일부 Node에서 Pod가 Pending 상태로 남고, Pod 이벤트에 FailedCreate 또는 스케줄링 오류가 표시됩니다. 이는 워크로드 플레인에 영향을 미치며 모든 Node에 DaemonSet Pod가 생성되지 않게 합니다. 주로 Node Selector/Toleration 불일치 또는 리소스 제약이 원인이며, 영향받는 Node에서 Node 수준 기능을 사용할 수 없습니다.

## 영향

일부 Node에서 DaemonSet Pod가 누락되어 해당 Node의 Node 수준 기능을 사용할 수 없습니다. 모니터링, 로깅 또는 네트워킹 구성 요소가 누락될 수 있으며, DaemonSet의 원하는 Node 수와 준비된 수가 일치하지 않습니다. KubeDaemonSetNotReady 알림이 발생할 수 있고, Node별 서비스가 실행되지 않으며, 클러스터 기능이 Node 간에 일관되지 않습니다. DaemonSet의 스케줄된 수 불일치가 무기한 지속되고, 일부 Node에서 Pod가 Pending 상태로 남으며, 영향받는 Node에서 Node 수준 기능을 사용할 수 없어 오류가 발생할 수 있습니다.

## 플레이북

1. namespace <namespace>에서 DaemonSet <daemonset-name>을 describe하여 다음을 확인합니다:
   - 원하는 Node 수 대비 준비/가용 수
   - Node Selector 및 Toleration 설정
   - Pod가 배포되지 않는 이유를 보여주는 Condition
   - FailedCreate, FailedScheduling 또는 스케줄링 오류를 보여주는 Event

2. namespace <namespace>에서 DaemonSet <daemonset-name>의 이벤트를 타임스탬프 순으로 조회하여 배포 실패 순서를 확인합니다.

3. 모든 Node를 조회하고 namespace <namespace>에서 label app=<daemonset-label>로 Pod를 조회하여 DaemonSet Pod 분포와 비교하고, 어떤 Node에서 DaemonSet Pod가 누락되었는지 확인합니다.

4. kube-system namespace에서 kube-controller-manager Pod를 조회하여 DaemonSet 컨트롤러가 실행 중인지 확인합니다.

5. DaemonSet Pod가 누락된 Node에 대해 node <node-name>을 describe하여 Label, Taint, 스케줄링 상태를 확인하고 DaemonSet 요구사항과 일치하는지 검증합니다.

6. DaemonSet Pod가 누락된 Node의 리소스 사용량 메트릭을 조회하여 리소스 부족이 Pod 생성을 방해하는지 확인합니다.

7. namespace <namespace>에서 PodDisruptionBudget 리소스를 조회하여 Node에서 DaemonSet Pod 생성을 방해하는 충돌이 있는지 확인합니다.

## 진단

1. 플레이북의 DaemonSet 이벤트와 Pod 분포를 분석하여 어떤 Node에서 DaemonSet Pod가 누락되었는지 확인합니다. Pod가 실행 중인 Node와 실행되지 않는 Node를 비교하여 차이점(Label, Taint, 리소스 또는 Condition)을 파악합니다.

2. 이벤트가 특정 Node에서 스케줄링 실패를 나타내면 해당 Node를 개별적으로 검사합니다. 실패 원인별로 Node를 그룹화합니다 — 일부는 Taint 문제이고 다른 일부는 리소스 제약일 수 있습니다. Node마다 다른 차단 요인이 있을 수 있습니다.

3. 누락된 Pod가 특정 Node Pool 또는 Node 그룹과 관련이 있으면, 해당 Node에 DaemonSet의 nodeSelector와 일치하는 Label이 있는지 확인합니다. Node Pool 설정 변경으로 필요한 Label 없이 Node가 추가되었을 수 있습니다.

4. 누락된 Pod가 특정 Taint가 있는 Node와 관련이 있으면, DaemonSet Toleration이 모든 Taint 키와 Effect를 포함하는지 확인합니다. 일반적으로 누락되는 Toleration에는 특수 워크로드, GPU Node 또는 Spot/Preemptible 인스턴스에 대한 NoSchedule Taint가 포함됩니다.

5. 일부 Node에 리소스가 부족한 경우, DaemonSet Pod의 리소스 요청량과 영향받는 Node의 사용 가능한 할당 가능 리소스를 비교합니다. 기존 워크로드가 많은 Node는 DaemonSet Pod를 위한 용량이 부족할 수 있습니다.

6. 영향받는 Node가 Cordon 또는 스케줄링 불가 상태이면 해당 Node에 DaemonSet Pod를 생성할 수 없습니다. 플레이북에서 Node 설명의 spec.unschedulable 또는 Cordon 상태를 확인합니다.

7. 영향받는 Node가 NotReady 상태이거나 kubelet 문제가 있으면 해당 Node가 Pod 스케줄링을 수락하지 않을 수 있습니다. Node Condition을 확인하고 스케줄링을 방해하는 MemoryPressure, DiskPressure 또는 PIDPressure Condition이 있는지 확인합니다.

8. 명확한 패턴이 나타나지 않으면, 전체 스케줄링 요구사항(nodeSelector, nodeAffinity, Toleration)을 각 영향받는 Node의 설정과 비교합니다. 여러 제약 조건의 교집합이 개별 검사를 통과하는 Node를 제외할 수 있습니다.
