---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/03-Pods/PodsStuckinContainerCreatingState-pod.md)'
role: SRE / K8s Incident Response
origin: scoutflo
tags:
- infrastructure
- k8s-configmap
- k8s-deployment
- k8s-namespace
- k8s-pod
- k8s-secret
- k8s-service
- kubernetes
- pods
- podsstuckincontainercreatingstate
---

---
title: Pods Stuck in ContainerCreating State - Pod
weight: 222
categories:
  - kubernetes
  - pod
---

# PodsStuckinContainerCreatingState-pod — Pod ContainerCreating 상태 고착

## 의미

Pods remain stuck in ContainerCreating state (triggering KubePodPending alerts)  container image pull is failing, volumes cannot be mounted, container runtime is experiencing issues, or resource constraints prevent container creation. Pods show ContainerCreating state in kubectl, container waiting state reason shows ImagePullBackOff, ErrImagePull, or CreateContainerConfigError, and pod events show Failed, ErrImagePull, or FailedMount errors. 이는 워크로드 플레인에 영향을 미치며, pods from transitioning to Running state, 일반적으로 image pull failures, PersistentVolumeClaim binding failures, or container runtime issues; missing ConfigMap, Secret, or PersistentVolumeClaim dependencies may block container creation.

## 영향

Pods cannot start; containers never begin running; deployments remain at 0 ready replicas; services have no endpoints; applications are unavailable; Pod가 ContainerCreating state indefinitely; KubePodPending 알림 발생; pod status shows container creation failures; application startup is blocked. Pods show ContainerCreating state indefinitely; container waiting state reason shows ImagePullBackOff, ErrImagePull, or CreateContainerConfigError; missing ConfigMap, Secret, or PersistentVolumeClaim dependencies may prevent container creation; 애플리케이션을 시작할 수 없습니다 and may show errors.

## 플레이북

1. Pod를 describe하고 <pod-name> Namespace <namespace> 확인합니다 the container waiting reason in the Status section and check Events for FailedMount, ErrImagePull, or CreateContainerConfigError with specific details.

2. Pod의 이벤트를 조회하고 <pod-name> Namespace <namespace> 타임스탬프 순으로 정렬하여 확인합니다 the sequence of failures (image pull, volume mount, config errors).

3.  container waiting state for pod <pod-name> Namespace <namespace> 확인합니다 exactly why container creation is stuck.

4. If volume mount issue, list PersistentVolumeClaims Namespace <namespace> and describe PVC <pvc-name> 확인합니다 if PVC is bound and volume is available.

5. If ConfigMap/Secret issue, verify they exist: check ConfigMap <name> and Secret <name> Namespace <namespace>.

6. Describe Deployment <deployment-name> Namespace <namespace> 확인합니다 image references, volume mounts, and imagePullSecrets configuration.

7. Describe node <node-name> where pod is scheduled to look for disk pressure, container runtime issues, or resource constraints.

8. Check container runtime on the node (SSH required) 확인합니다 container creation attempts and runtime logs for errors.

## 진단

1. Pod 이벤트를 분석하여 플레이북 1-2 파악합니다 why container creation is stuck. Events showing the container waiting reason provide the specific blocker. Order diagnosis by most common causes:

2. 이벤트에서 "ImagePullBackOff" or "ErrImagePull" (플레이북 2):
   - Image does not exist or tag is incorrect
   - Private registry requires imagePullSecrets not configured
   - Network connectivity to registry failed
   - Registry rate limiting or authentication issues
   - Check deployment image configuration (플레이북 6)

3. 이벤트에서 "FailedMount" for volumes (플레이북 2):
   - PVC is not bound (플레이북 4) - check storage class and provisioner
   - PV cannot attach to node - check cloud provider volume limits
   - Volume already attached to another node - multi-attach not supported
   - NFS or network storage unreachable

4. 이벤트에서 "CreateContainerConfigError" (플레이북 3):
   - ConfigMap or Secret does not exist (플레이북 5)
   - Key referenced in envFrom or volumeMount missing
   - Syntax error in container command or args

5. If node shows resource issues (플레이북 7):
   - DiskPressure: Node disk full, cannot pull images
   - Container runtime overloaded or unresponsive
   - Too many containers on node

6. If container runtime logs show errors (플레이북 8):
   - Runtime cannot create container sandbox
   - Image format incompatible with runtime
   - Security policy blocking container creation

**해결을 위해 ContainerCreating issues**: Fix image references for pull errors, create missing ConfigMaps/Secrets, ensure PVCs are bound and volumes can attach, free node disk space if needed, and verify container runtime is healthy.

