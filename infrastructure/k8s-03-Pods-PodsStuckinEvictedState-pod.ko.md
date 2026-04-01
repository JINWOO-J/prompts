---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/03-Pods/PodsStuckinEvictedState-pod.md)'
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
- podsstuckinevictedstate
---

---
title: Pods Stuck in Evicted State - Pod
weight: 283
categories:
  - kubernetes
  - pod
---

# PodsStuckinEvictedState-pod — Pod Evicted 상태 고착

## 의미

Pods remain in Evicted state (triggering KubePodNotReady alerts) y were evicted by kubelet due to node resource pressure (MemoryPressure, DiskPressure, PIDPressure) but were not automatically cleaned up. Pods show Evicted state in kubectl, pod status reason shows Evicted with resource pressure type, and node conditions may show MemoryPressure, DiskPressure, or PIDPressure. This affects the workload plane and blocks cleanup, 일반적으로 node resource exhaustion; applications cannot run on affected nodes.

## 영향

Evicted Pod가 the cluster; pod resources are not released; deployments cannot achieve desired replica count; new pods may fail to schedule due to resource constraints; namespace cleanup is blocked; pod status shows Evicted state; KubePodNotReady 알림 발생; node resources remain allocated to evicted pods; cluster resource management is impaired. Pods show Evicted state indefinitely; pod status reason shows Evicted with resource pressure type; node conditions show MemoryPressure, DiskPressure, or PIDPressure; applications cannot run on affected nodes and may show errors.

## 플레이북

1. Pod를 describe하고 <pod-name> Namespace <namespace> 확인합니다 status.reason and status.message 확인합니다 eviction reason and identify which resource pressure caused the eviction.

2. Namespace에서 이벤트를 조회하고 <namespace> for pod <pod-name> 타임스탬프 순으로 정렬하여 파악합니다 eviction events, focon events with reasons such as Evicted and messages indicating the resource pressure type (memory, disk, PID).

3. Pod를 나열하고 namespace <namespace> and filter for pods with status Evicted 파악합니다 all evicted pods.

4. Check the node where the pod was evicted and verify its resource pressure conditions (MemoryPressure, DiskPressure, PIDPressure) 파악합니다 current node state.

5.  Deployment <deployment-name> Namespace <namespace> and review resource requests 확인합니다 if requests are reasonable relative to node capacity.

6. Check node resource usage metrics 확인합니다 current available resources and identify if node-level resource pressure persists.

## 진단

1. Pod 이벤트를 분석하여 플레이북 1-2 파악합니다 the eviction reason. The status.reason field shows "Evicted" and status.message indicates the specific resource pressure (memory, disk, PID) that triggered the eviction.

2. If eviction message indicates MemoryPressure (플레이북 1), the node ran out of memory. Check node conditions (플레이북 4) 확인합니다 MemoryPressure and review node memory usage metrics (플레이북 6) 파악합니다 memory-hungry pods.

3. If eviction message indicates DiskPressure, the node ran out of disk space. 일반적인 원인:
   - Container logs consuming too much space
   - Container images filling the disk
   - emptyDir volumes growing unbounded
   - Application writing excessive data to ephemeral storage

4. If eviction message indicates PIDPressure, the node has too many running processes. Check for runaway process spawning in containers.

5. If multiple pods were evicted simultaneously (플레이북 3), there was a significant resource pressure event on the node. Lower-priority pods are evicted first based on QoS class (BestEffort, then Burstable, then Guaranteed).

6. If deployment resource requests (플레이북 5) are too low relative to actual usage, pods may be scheduled on nodes with insufficient capacity. Increase resource requests to ensure proper scheduling.

7. Evicted Pod가 Evicted state until manually deleted or garbage collected. They do not automatically restart; the deployment controller creates new pods on other nodes.

**방지를 위해 future evictions**: Set appropriate resource requests and limits, configure pod priority classes for critical workloads, implement horizontal pod autoscaling, add more nodes to the cluster, or reduce resource consumption in applications.

