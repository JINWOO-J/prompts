---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/03-Pods/PodsNotBeingScheduled-pod.md)'
role: SRE / K8s Incident Response
origin: scoutflo
tags:
- capacity
- infrastructure
- k8s-deployment
- k8s-namespace
- k8s-node
- k8s-pod
- k8s-service
- kubernetes
- pods
- podsnotbeingscheduled
- sts
---

---
title: Pods Not Being Scheduled - Pod
weight: 233
categories:
  - kubernetes
  - pod
---

# PodsNotBeingScheduled-pod — Pod 스케줄링 불가

## 의미

Pods remain stuck in Pending state (triggering KubePodPending alerts)  scheduler cannot find any suitable node due to resource constraints, node taints without matching tolerations, affinity/anti-affinity rules, or other placement restrictions. Pods show Pending state in kubectl, pod events show "0/X nodes are available" messages with InsufficientCPU, InsufficientMemory, or Unschedulable errors, and ResourceQuota resources may show exceeded limits. 이는 워크로드 플레인에 영향을 미치며, pod placement, 일반적으로 resource constraints, node taint/toleration mismatches, or ResourceQuota limits; 애플리케이션을 시작할 수 없습니다.

## 영향

Pods cannot be scheduled; Deployment 스케일링 실패; 애플리케이션 불가용 상태 유지; 서비스가 새 Pod를 확보할 수 없음; Pod가 Pending state indefinitely; 스케줄러가 Pod를 배치할 수 없음; Replica 수가 원하는 상태와 불일치; KubePodPending 알림 발생; pod events show "0/X nodes are available" messages with specific scheduling failure reasons. Pods show Pending state indefinitely; pod events show InsufficientCPU, InsufficientMemory, or Unschedulable errors; ResourceQuota limits may prevent pod creation; 애플리케이션을 시작할 수 없습니다 and may show errors.

## 플레이북

1. Pod를 describe하고 <pod-name> Namespace <namespace> 확인합니다 its status and see scheduler messages explaining why it remains Pending.

2. Namespace에서 이벤트를 조회하고 <namespace> for pod <pod-name> 타임스탬프 순으로 정렬하여 파악합니다 scheduler events and scheduling failure reasons.

3. 모든 노드를 나열하고 and retrieve resource usage metrics to compare available CPU and memory on each node with the pod's requested resources.

4.  Deployment <deployment-name> Namespace <namespace> and review container resource requests and limits to ensure they are reasonable relative to node capacity.

5. Inspect the pod <pod-name> spec for node selectors, affinity, or anti-affinity rules that may restrict which nodes it can schedule onto.

6. 모든 노드를 나열하고 and examine their taints, then compare with the pod's tolerations 판단합니다 whether taints are preventing scheduling.

7. Retrieve ResourceQuota objects Namespace <namespace> and compare current usage against limits 확인합니다 whether quotas are blocking new pod creation.

## 진단

1. Pod 이벤트를 분석하여 플레이북 1-2 파악합니다 the scheduling failure reason. The scheduler provides detailed messages like "0/X nodes are available" followed by specific reasons for each node rejection.

2. 이벤트에서 "Insufficient cpu" or "Insufficient memory" (플레이북 2), compare pod resource requests (플레이북 4) with node available capacity (플레이북 3). Either reduce resource requests or add more nodes to the cluster.

3. 이벤트에서 "node(s) had taint that pod didn't tolerate" (플레이북 6), the pod needs tolerations for the node taints. Add appropriate tolerations to the pod spec or remove unnecessary taints from nodes.

4. 이벤트에서 node selector or affinity mismatches (플레이북 5), verify that nodes with matching labels exist. Either update node labels or adjust pod placement constraints.

5. If ResourceQuota shows exceeded limits (플레이북 7), the namespace has reached its resource quota. Either increase the quota or reduce resource usage in the namespace.

6. 이벤트에서 PodDisruptionBudget constraints, too many pods are already unavailable. Wait for existing disruptions to resolve or adjust PDB settings.

7. 이벤트에서 inter-pod anti-affinity conflicts, there are not enough nodes to satisfy the spreading requirements. Add more nodes or relax anti-affinity rules.

8. If cluster autoscaler is enabled but not scaling up (플레이북 8), check autoscaler events for errors. Common issues include cloud provider API limits, insufficient quota, or autoscaler configuration problems.

**If scheduling failure persists**: Review the complete scheduler message which lists all nodes and why each was rejected. Address the most common rejection reason first. Consider `kubectl describe nodes` 확인합니다 current resource allocation on each node.

