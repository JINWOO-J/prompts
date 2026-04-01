---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/03-Pods/PodStuckinPendingDuetoNodeAffinity-pod.md)'
role: SRE / K8s Incident Response
origin: scoutflo
tags:
- infrastructure
- k8s-deployment
- k8s-namespace
- k8s-node
- k8s-pod
- k8s-service
- kubernetes
- pods
- podstuckinpendingduetonodeaffinity
---

---
title: Pod Stuck in Pending Due to Node Affinity - Pod
weight: 291
categories:
  - kubernetes
  - pod
---

# PodStuckinPendingDuetoNodeAffinity-pod — Node Affinity로 인한 Pod Pending

## 의미

Pods remain stuck in Pending state (triggering KubePodPending alerts)  scheduler cannot find any node that satisfies the pod's affinity or anti-affinity rules. Pods show Pending state in kubectl, pod events show "0/X nodes are available" messages with affinity mismatch reasons, and node labels may not match pod affinity requirements. 이는 워크로드 플레인에 영향을 미치며, pod placement, 일반적으로 node label mismatches or restrictive affinity rules; 애플리케이션을 시작할 수 없습니다.

## 영향

Pods cannot be scheduled; Deployment 스케일링 실패; 애플리케이션 불가용 상태 유지; 서비스가 새 Pod를 확보할 수 없음; Pod가 Pending state indefinitely; 스케줄러가 Pod를 배치할 수 없음; Replica 수가 원하는 상태와 불일치; KubePodPending 알림 발생; pod events show "0/X nodes are available" messages with affinity mismatch reasons. Pods show Pending state indefinitely; pod events show affinity mismatch reasons; node labels may not match pod affinity requirements; 애플리케이션을 시작할 수 없습니다 and may show errors.

## 플레이북

1. Pod를 describe하고 <pod-name> Namespace <namespace> 확인합니다 spec.affinity.nodeAffinity 파악합니다 the required or preferred node affinity rules.

2. Namespace에서 이벤트를 조회하고 <namespace> for pod <pod-name> 타임스탬프 순으로 정렬하여 파악합니다 scheduler events, focon events with messages indicating affinity mismatches or "0/X nodes are available" with affinity reasons.

3. 모든 노드를 나열하고 and retrieve their labels to compare with the pod's affinity requirements and identify which labels are missing or mismatched.

4.  Deployment <deployment-name> Namespace <namespace> and review the pod template's affinity configuration 확인합니다 the affinity rules are correctly specified.

5. 확인합니다: anti-affinity rules are too restrictive by verifying if any nodes satisfy the requirements or if the rules conflict with each other.

6. 확인합니다: node labels were recently removed or changed that may have caused previously schedulable pods to become unschedulable.

## 진단

1. Pod 이벤트를 분석하여 플레이북 1-2 파악합니다 the affinity constraint cascheduling failure. Events showing "0/X nodes are available" with affinity-related reasons indicate which constraint cannot be satisfied.

2. 이벤트에서 nodeAffinity mismatch (플레이북 2):
   - requiredDuringSchedulingIgnoredDuringExecution cannot be satisfied
   - Check pod affinity rules (플레이북 1) against node labels (플레이북 3)
   - Identify which label selector expression is not matched

3. 이벤트에서 podAntiAffinity conflict:
   - Pod cannot be placed without violating anti-affinity with existing pods
   - 확인합니다: topologyKey is too restrictive (e.g., kubernetes.io/hostname)
   - Consider preferredDuringSchedulingIgnoredDuringExecution for soft rules

4. 이벤트에서 podAffinity cannot be satisfied:
   - No nodes have pods matching the affinity selector
   - The required pod may be on an unschedulable node
   - 확인합니다: affinity target pods exist and are running

5. If deployment affinity rules (플레이북 4) conflict with available nodes:
   - requiredDuringScheduling rules are hard constraints
   - preferredDuringScheduling rules should allow scheduling with lower score
   - Convert hard constraints to soft preferences if flexibility is acceptable

6. If anti-affinity rules are too restrictive (플레이북 5):
   - Each replica needs a unique node but not enough nodes exist
   - Relax topologyKey from hostname to zone or region
   - Reduce replica count or add more nodes

7. If nodes with matching labels exist but are not schedulable (플레이북 6):
   - Node is cordoned or tainted
   - Node resources are exhausted
   - Other scheduling constraints block placement

**해결을 위해 affinity scheduling issues**: Either add/update node labels to match affinity requirements, add nodes with required labels, relax affinity rules (convert required to preferred), or remove conflicting anti-affinity constraints. Use `kubectl describe pod` 확인합니다 the exact scheduling failure reason.

