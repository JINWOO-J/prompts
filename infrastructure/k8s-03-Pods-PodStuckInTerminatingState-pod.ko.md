---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/03-Pods/PodStuckInTerminatingState-pod.md)'
role: SRE / K8s Incident Response
origin: scoutflo
tags:
- infrastructure
- k8s-deployment
- k8s-namespace
- k8s-pod
- k8s-service
- kubernetes
- pods
- podstuckinterminatingstate
---

---
title: Pod Stuck In Terminating State - Pod
weight: 206
categories:
  - kubernetes
  - pod
---

# PodStuckInTerminatingState-pod — Pod Terminating 상태 고착

## 의미

Pod가 Terminating 단계에 고착되어 있습니다(KubePodNotReady 알림이 발생할 수 있음)  shutdown cannot complete cleanly, often due to hanging processes, blocking finalizers, or attached volumes and endpoints that cannot be detached. Pods show Terminating state indefinitely in kubectl, pod finalizers prevent deletion, and pod events may show deletion-related errors. 이는 pod deletion failures, finalizer issues, or resource dependency problems preventing graceful pod termination; PersistentVolumeClaim detachments may fail.

## 영향

Pods cannot be deleted; Deployment 업데이트 불가; 롤링 업데이트 중단; resources remain in terminating state; cluster state becomes inconsistent; new pods may not start if resources are blocked; KubePodNotReady 알림이 발생할 수 있음; Pod가 Terminating state; finalizers prevent deletion; volume detachments fail. Pods show Terminating state indefinitely; pod finalizers prevent deletion; PersistentVolumeClaim detachments may fail; applications may experience resource allocation issues.

## 플레이북

1. Pod를 describe하고 <pod-name> Namespace <namespace> 확인합니다 pod details and reason for termination delay.

2. Namespace에서 이벤트를 조회하고 <namespace> for pod <pod-name> 타임스탬프 순으로 정렬하여 파악합니다 deletion-related events.

3. Retrieve pod <pod-name> Namespace <namespace> and check finalizers preventing deletion.

4. Check dependent resources like persistent volume claims, services, or other pods.

5. Retrieve deployment <deployment-name> Namespace <namespace> and verify terminationGracePeriodSeconds setting.

6. Retrieve pod <pod-name> Namespace <namespace> and check for volume mount issues.

## 진단

1. Pod 이벤트를 분석하여 플레이북 1-2 파악합니다 why the pod is stuck in Terminating state. Events showing deletion-related errors, volume detachment failures, or finalizer issues indicate the specific blocker.

2. If pod metadata shows finalizers (플레이북 3), identify which finalizer is preventing deletion:
   - "kubernetes.io/pvc-protection": PersistentVolumeClaim is still bound
   - "foregroundDeletion": Child resources still exist
   - Custom finalizers: Check the owning controller/operator status

3. 이벤트에서 volume mount issues (플레이북 6), PersistentVolumeClaims cannot be detached. Check dependent resources (플레이북 4) 확인합니다 PVC status and storage provider health.

4. If no events indicate the blocker, check if the node where the pod was running is healthy. A NotReady node cannot complete pod termination cleanup.

5. If terminationGracePeriodSeconds (플레이북 5) is very long, the pod may still be in its grace period. Kubernetes waits for containers to terminate gracefully before force-killing them.

6. 이벤트에서 no errors but pod remains Terminating, check for hanging processes in the container that are not responding to SIGTERM. The container may need to handle shutdown signals properly.

**조사 후에도 Pod가 고착된 경우**: Consider force-deleting with `kubectl delete pod --force --grace-period=0` if the underlying resources are confirmed cleaned up. For stuck finalizers, manually patch the pod to remove finalizers only after verifying dependent resources are properly cleaned.
