---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/03-Pods/PodSchedulingIgnoredNodeSelector-pod.md)'
role: SRE / K8s Incident Response
origin: scoutflo
tags:
- infrastructure
- k8s-deployment
- k8s-namespace
- k8s-node
- k8s-pod
- kubernetes
- pods
- podschedulingignorednodeselector
---

---
title: Pod Scheduling Ignored Node Selector - Pod
weight: 278
categories:
  - kubernetes
  - pod
---

# PodSchedulingIgnoredNodeSelector-pod — Pod 스케줄링 NodeSelector 무시

## 의미

Pod가 Node Selector와 일치하는 노드에 스케줄링되지 않습니다(KubePodPending 알림 발생)  node selector specified in the pod does not match any node labels, node labels were removed or changed, or the node selector configuration is incorrect. Pods show Pending state in kubectl, pod events show "0/X nodes are available" messages with node selector mismatch reasons, and node labels may not match pod selector requirements. 이는 워크로드 플레인에 영향을 미치며, pod placement, 일반적으로 node label mismatches or incorrect selector configuration; 애플리케이션을 시작할 수 없습니다.

## 영향

Pods cannot be scheduled; Deployment 스케일링 실패; 애플리케이션 불가용 상태 유지; Pod가 Pending state indefinitely; 스케줄러가 Pod를 배치할 수 없음; Replica 수가 원하는 상태와 불일치; KubePodPending 알림 발생; pod events show "0/X nodes are available" messages with node selector mismatch reasons. Pods show Pending state indefinitely; pod events show node selector mismatch reasons; node labels may not match pod selector requirements; 애플리케이션을 시작할 수 없습니다 and may show errors.

## 플레이북

1. Pod를 describe하고 <pod-name> Namespace <namespace> 확인합니다 pod node selector configuration 파악합니다 which node selector is specified.

2. Namespace에서 이벤트를 조회하고 <namespace> for pod <pod-name> 타임스탬프 순으로 정렬하여 파악합니다 scheduler events, focon events with messages indicating node selector mismatches or "0/X nodes are available" with selector reasons.

3. 모든 노드를 나열하고 and retrieve their labels to compare with the pod's node selector and identify which labels are missing or mismatched.

4.  Deployment <deployment-name> Namespace <namespace> and review the pod template's node selector configuration 확인합니다 the selector is correctly specified.

5. 확인합니다: node labels were recently removed or changed that may have caused previously schedulable pods to become unschedulable.

6. 확인합니다: the node selector requirements are too restrictive or if they conflict with other scheduling constraints (affinity, taints, tolerations).

## 진단

1. Pod 이벤트를 분석하여 플레이북 1-2 파악합니다 the node selector mismatch. Events showing "0/X nodes are available" with "node(s) didn't match Pod's node affinity/selector" confirm the selector is not matching any nodes.

2. If pod node selector (플레이북 1) requires specific labels, compare with actual node labels (플레이북 3). 일반적인 불일치:
   - Typos in label keys or values
   - Labels that were removed from nodes
   - Labels that exist only on cordoned or NotReady nodes
   - Case sensitivity issues in label values

3. If deployment node selector (플레이북 4) was recently changed, verify the new selector matches available nodes. Roll back the change if the selector is incorrect.

4. If nodes exist with matching labels but are unschedulable (플레이북 5), check for:
   - Node cordoned for maintenance
   - Node taints that the pod does not tolerate
   - Node resource exhaustion preventing new pod placement

5. If node selector uses labels for specific node pools (e.g., GPU nodes, high-memory nodes), verify those node pools are provisioned and healthy.

6. If the node selector conflicts with other scheduling constraints (플레이북 6), such as affinity rules or tolerations, the combined constraints may be unsatisfiable. Simplify scheduling requirements.

**해결을 위해 node selector issues**: Either add the required labels to existing nodes `kubectl label node <node-name> <key>=<value>`, or update the pod specification to use labels that exist on available nodes. For dynamic node provisioning (cloud environments), ensure autoscaler is configured to provision nodes with the required labels.

