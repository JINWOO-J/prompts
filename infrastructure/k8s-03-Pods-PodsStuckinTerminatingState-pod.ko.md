---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/03-Pods/PodsStuckinTerminatingState-pod.md)'
role: SRE / K8s Incident Response
origin: scoutflo
tags:
- infrastructure
- k8s-namespace
- k8s-node
- k8s-pod
- kubernetes
- pods
- podsstuckinterminatingstate
---

---
title: Pods Stuck in Terminating State - Pod
weight: 293
categories:
  - kubernetes
  - pod
---

# PodsStuckinTerminatingState-pod — Pod Terminating 상태 고착 (다수)

## 의미

Pods remain stuck in Terminating state (triggering KubePodNotReady alerts)  finalizers cannot complete, persistent volumes cannot be unmounted, the kubelet on the node cannot communicate with the control plane, or the node itself is unreachable. Pods show Terminating state indefinitely in kubectl, pod finalizers prevent deletion, and PersistentVolumeClaim resources may show stuck binding. This affects the workload plane and blocks resource cleanup, 일반적으로 finalizer processing failures, PersistentVolume unmount issues, or node communication problems; PersistentVolumeClaim binding failures may prevent pod termination.

## 영향

Pods cannot be deleted; namespace cleanup is blocked; resources remain allocated; new pods may fail to schedule due to resource constraints; finalizers prevent resource deletion; volumes remain attached; pod IPs remain allocated; KubePodNotReady 알림 발생; pod status shows Terminating indefinitely; cluster resource management is impaired. Pods show Terminating state indefinitely; pod finalizers prevent deletion; PersistentVolumeClaim binding failures may prevent pod termination; applications may experience resource allocation issues.

## 플레이북

1. Pod를 describe하고 <pod-name> Namespace <namespace> 확인합니다 pod deletion timestamp and finalizers 확인합니다 the pod is in Terminating state and identify which finalizers are present.

2. Namespace에서 이벤트를 조회하고 <namespace> for pod <pod-name> 타임스탬프 순으로 정렬하여 파악합니다 events related to volume unmount failures, finalizer errors, or node communication issues.

3. Check the node where the pod was scheduled and verify its Ready condition and communication status with the control plane by checking node status conditions 판단합니다 if the node is reachable.

4. Verify node-to-control-plane connectivity by checking if kubelet on the node can communicate with the API server.

5.  PersistentVolumeClaim objects referenced by the pod and check their status 확인합니다 if volumes are stuck in use or cannot be released.

6.  pod <pod-name> and inspect pod volume configuration 파악합니다 all volume types and their mount points, then verify if any volumes have unmount issues.

7. List all finalizers on the pod and check if any custom resource controllers or operators are responsible for those finalizers and verify their status by checking controller pod logs.

## 진단

1. Pod 이벤트를 분석하여 플레이북 1-2 파악합니다 why termination is blocked. Events showing volume unmount failures, finalizer errors, or node communication issues indicate the specific blocker preventing pod deletion.

2. If pod metadata shows finalizers (플레이북 1), identify which finalizer is blocking deletion:
   - "kubernetes.io/pvc-protection": PersistentVolumeClaim cannot be released
   - "foregroundDeletion": Dependent resources still exist
   - Custom finalizers: Operator or controller responsible for cleanup is failing

3. If node status shows NotReady condition (플레이북 3), the kubelet cannot complete pod cleanup. The pod will remain Terminating until the node recovers or is removed from the cluster.

4. 이벤트에서 volume unmount failures (플레이북 2), check PersistentVolumeClaim status (플레이북 5). 일반적인 원인:
   - Storage provider issues preventing volume detachment
   - Volume still in use by another pod
   - Node cannot communicate with storage backend

5. If kubelet connectivity check fails (플레이북 4), the node cannot report pod termination completion to the API server. Verify network connectivity between the node and control plane.

6. If finalizer controller pods are failing or restarting (플레이북 7), the finalizer cannot be processed. Check controller logs for errors and restart the controller if necessary.

7. If no specific blocker is identified in events, check if the terminationGracePeriodSeconds has been exceeded. Kubernetes will force-kill the pod after this period, but cleanup may still be blocked by finalizers or volumes.

**조사 후에도 Pod가 고착된 경우**: Consider force-deleting the pod with `kubectl delete pod --force --grace-period=0` (use with caution as this may leave orphaned resources). For stuck finalizers, manually remove them only after verifying the underlying resource is cleaned up.

