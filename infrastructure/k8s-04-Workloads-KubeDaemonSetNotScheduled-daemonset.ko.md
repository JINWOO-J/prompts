---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/04-Workloads/KubeDaemonSetNotScheduled-daemonset.md)'
role: SRE / K8s Incident Response
origin: scoutflo
tags:
- daemonset
- infrastructure
- k8s-daemonset
- k8s-namespace
- k8s-node
- k8s-pod
- k8s-service
- kubedaemonsetnotscheduled
- workloads
---

---
title: Kube DaemonSet Not Scheduled
weight: 20
---

# DaemonSet이 스케줄링되지 않음 (KubeDaemonSetNotScheduled)

## 의미

DaemonSet Pod가 실행되어야 하는 Node에 스케줄링되지 않는 상태입니다(DaemonSet 스케줄링 관련 알림 발생). Node Selector, Toleration 또는 Affinity 규칙이 스케줄링을 방해하거나, Node에 필요한 리소스가 부족하거나, Node Taint가 DaemonSet Toleration과 호환되지 않기 때문입니다.
kubectl에서 DaemonSet의 스케줄된 수가 불일치하며, Pod가 Pending 상태로 남고, Pod 이벤트에 FailedScheduling, InsufficientCPU, InsufficientMemory 또는 Unschedulable 오류가 표시됩니다. 이는 워크로드 플레인에 영향을 미치며 DaemonSet이 원하는 상태를 달성하지 못하게 하는 스케줄링 제약을 나타냅니다. 주로 설정 불일치, 지속적인 리소스 제약 또는 Node Pool 변경이 원인이며, Node Taint/Toleration 불일치가 스케줄링을 방해할 수 있습니다.

## 영향

DaemonSet 스케줄링 알림이 발생하며, 서비스 저하 또는 사용 불가가 발생합니다. DaemonSet이 원하는 상태를 달성할 수 없고, Pod가 Pending 상태로 남습니다. DaemonSet의 원하는 스케줄 수가 불일치하며, 필요한 Node에서 시스템 구성 요소가 누락될 수 있습니다. DaemonSet Pod에 의존하는 기능이 실패하며, DaemonSet 원하는 상태를 달성할 수 없습니다.

## 플레이북

1. namespace <namespace>에서 DaemonSet <daemonset-name>을 describe하여 다음을 확인합니다:
   - 스케줄된 수 대비 원하는 스케줄 수
   - Node Selector, Toleration 및 Affinity 규칙 설정
   - Pod가 스케줄링되지 않는 이유를 보여주는 Condition
   - FailedScheduling, InsufficientCPU, InsufficientMemory 또는 Unschedulable 오류를 보여주는 Event

2. namespace <namespace>에서 DaemonSet <daemonset-name>의 이벤트를 타임스탬프 순으로 조회하여 스케줄링 실패 순서를 확인합니다.

3. namespace <namespace>에서 label app=<daemonset-label>로 DaemonSet에 속한 Pod를 조회하고 Pod를 describe하여 Pending 상태의 Pod와 스케줄링 차단 요인을 식별합니다.

4. node <node-name>을 describe하여 Node 가용성, Condition, Taint 및 DaemonSet Toleration과의 호환성을 확인합니다.

5. DaemonSet Pod가 스케줄링되어야 하는 Node의 리소스 사용량 메트릭을 조회하여 리소스 가용성을 확인합니다.

## 진단

1. 플레이북의 DaemonSet 및 Pod 이벤트를 분석하여 스케줄링 차단 요인을 파악합니다. 구체적인 이유가 포함된 "FailedScheduling" 이벤트(InsufficientCPU, InsufficientMemory, node(s) had taint)는 Pod 배치를 방해하는 정확한 제약을 나타냅니다.

2. 이벤트가 Taint 관련 실패를 나타내면(node(s) had taint that the pod didn't tolerate), 플레이북의 Node Taint와 DaemonSet Toleration을 비교합니다. DaemonSet은 Node Taint에 대한 명시적 Toleration이 필요합니다. 일반적으로 누락되는 Toleration에는 node-role.kubernetes.io/master, node-role.kubernetes.io/control-plane 또는 사용자 정의 Taint가 포함됩니다.

3. 이벤트가 리소스 제약을 나타내면(InsufficientCPU, InsufficientMemory), DaemonSet Pod 리소스 요청과 Node 할당 가능 리소스를 비교합니다. DaemonSet Pod는 Node 리소스를 다른 Pod와 경쟁합니다. 기존 Pod가 DaemonSet Pod에 필요한 리소스를 소비하는지 확인합니다.

4. 이벤트가 Node Selector 불일치를 나타내면(node(s) didn't match Pod's node affinity/selector), DaemonSet의 nodeSelector 또는 nodeAffinity가 대상 Node의 Label과 일치하는지 확인합니다. 플레이북의 Node 설명을 사용하여 예상 Node Label이 존재하는지 확인합니다.

5. 이벤트가 Node가 스케줄링 불가임을 나타내면(node(s) were unschedulable), Cordon된 Node 또는 스케줄링이 비활성화된 Node의 Node Condition을 확인합니다. Cordon된 Node는 DaemonSet Pod를 포함한 새 Pod 스케줄링을 방해합니다.

6. Pod가 Pending이지만 명확한 스케줄링 실패 이벤트가 없으면, Node가 NotReady 상태인지 확인합니다. DaemonSet Pod는 기본적으로 NotReady Node에 스케줄링되지 않습니다. 플레이북의 Node Condition을 확인합니다.

7. DaemonSet이 requiredDuringSchedulingIgnoredDuringExecution이 포함된 nodeAffinity를 사용하면, Affinity 규칙과 일치하는 Node가 없으면 Pod가 스케줄링되지 않습니다. 클러스터에서 최소한 일부 Node가 지정된 Node Affinity 표현식과 일치하는지 확인합니다.
