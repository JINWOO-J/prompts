---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/03-Pods/PodsStuckinInitState-pod.md)'
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
- podsstuckininitstate
---

---
title: Pods Stuck in Init State - Pod
weight: 229
categories:
  - kubernetes
  - pod
---

# PodsStuckinInitState-pod — Pod Init 상태 고착

## 의미

Pods remain stuck in Init state (triggering KubePodPending alerts)  init containers are failing to complete, hanging, or experiencing errors. Pods show Init container status indicating failures or hanging, init container logs show errors or timeout messages, and pod events show init container failure events. 이는 워크로드 플레인에 영향을 미치며, pods from transitioning from Init to Running state, 일반적으로 init container command failures, missing dependencies, or timeout issues; 애플리케이션을 시작할 수 없습니다.

## 영향

Pods cannot start; main application containers never begin; deployments remain at 0 ready replicas; services have no endpoints; applications are unavailable; Pod가 Init state indefinitely; KubePodPending 알림 발생; pod status shows init container failures; application startup is blocked. Pods show Init container status indicating failures indefinitely; init container logs show errors or timeout messages; 애플리케이션을 시작할 수 없습니다 and may show errors; deployments remain at 0 ready replicas.

## 플레이북

1. Pod를 describe하고 <pod-name> Namespace <namespace> 확인합니다 which init container is failing - look at Init Containers section for state (Waiting/Running/Terminated) and the reason/message.

2. Pod의 이벤트를 조회하고 <pod-name> Namespace <namespace> 타임스탬프 순으로 정렬하여 확인합니다 init container errors with timestamps.

3.  init container statuses for pod <pod-name> Namespace <namespace> 확인합니다 exactly which init container is stuck and why.

4. Retrieve logs from the failing init container <init-container-name> in pod <pod-name> Namespace <namespace> 확인합니다 what the init container is doing or where it is stuck.

5. Describe Deployment <deployment-name> Namespace <namespace> 확인합니다 init container configuration - command, args, image, and any dependencies.

6. If init container is waiting for a service, list services Namespace <namespace> and check endpoints for service <service-name> 확인합니다 the service exists.

7. If init container is waiting for a database or external resource, test connectivity to <host> on <port> from a debug pod.

8. 확인합니다: init container has enough resources by comparing requested resources with node availability node resource metrics.

## 진단

1. Pod 이벤트를 분석하여 플레이북 1-2 파악합니다 which init container is failing and why. The pod status shows init container states in order, and events provide specific failure reasons.

2. If init container status shows "Waiting" (플레이북 1), check the reason:
   - "ImagePullBackOff": Init container image cannot be pulled
   - "CreateContainerConfigError": Missing ConfigMap or Secret
   - "PodInitializing": Init container is still running (may be stuck)

3. If init container status shows "Running" for extended time (플레이북 3), check init container logs (플레이북 4) 파악합니다 what it is waiting for:
   - Waiting for a service to become available
   - Waiting for database connectivity
   - Waiting for external resource
   - Infinite loop or hang in init script

4. If init container logs show connection errors or timeouts (플레이북 4), verify the dependency is available:
   - 확인합니다: target service exists (플레이북 6)
   - Test connectivity to external resources (플레이북 7)
   - Verify network policies allow init container traffic

5. If init container status shows "Terminated" with non-zero exit code (플레이북 3):
   - Exit code 1: Command failed - check logs for error
   - Exit code 126: Command not found or not executable
   - Exit code 127: Shell or binary missing in image
   - Exit code 137: OOMKilled or SIGKILL

6. If init container needs resources not available (플레이북 5, 8), it may fail or hang:
   - Database not ready or credentials incorrect
   - Required files not present in mounted volumes
   - Schema migration failing

**해결을 위해 init container issues**: Fix the specific error shown in logs, ensure dependencies are available before pod starts, add timeout and retry logic to init scripts, and consider startup probes instead of init containers for dependency checks.

