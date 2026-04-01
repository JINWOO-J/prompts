---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/03-Pods/PodTerminatedWithExitCode137-pod.md)'
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
- monitoring
- pods
- podterminatedwithexitcode137
- sg
---

---
title: Pod Terminated With Exit Code 137 - Pod
weight: 242
categories:
  - kubernetes
  - pod
---

# PodTerminatedWithExitCode137-pod — Pod 종료 코드 137로 종료

## 의미

Pods are being terminated with exit code 137 (triggering KubePodCrashLooping or KubePodNotReady alerts)  container was killed by the kernel due to out-of-memory (OOM) conditions. Pods show exit code 137 in container termination status, pod events show OOMKilled events, and node conditions may show MemoryPressure. 이는 워크로드 플레인에 영향을 미치며, memory limit violations, 일반적으로 memory limits being too restrictive or node memory exhaustion; application errors may appear in application monitoring.

## 영향

Pods are terminated unexpectedly; containers are killed by OOM; applications lose in-memory state; pods enter CrashLoopBackOff state; deployments cannot maintain desired replica count; services lose endpoints; KubePodCrashLooping 알림 발생; pod status shows exit code 137; restart counts increase; application data may be lost on termination. Pods show exit code 137 in container termination status; pod events show OOMKilled events; application errors may appear in application monitoring; applications lose in-memory state and may show errors.

## 플레이북

1. Pod를 describe하고 <pod-name> Namespace <namespace> 확인합니다 container termination exit code 확인합니다 exit code 137 and container termination reason 확인합니다 OOM kill.

2. Namespace에서 이벤트를 조회하고 <namespace> for pod <pod-name> 타임스탬프 순으로 정렬하여 파악합니다 OOM kill events associated with the pod, focon events with reasons such as OOMKilled or messages containing "out of memory".

3. Check the node where the pod was scheduled for node-level memory pressure conditions (MemoryPressure) and system OOM kill events by checking node status conditions and system logs (dmesg) Pod Exec tool or SSH if node access is available.

4.  Deployment <deployment-name> Namespace <namespace> and review resource limits, specifically resources.limits.memory, 확인합니다 if memory limits are too restrictive.

5. Check the pod <pod-name> resource usage metrics 확인합니다 actual memory consumption compared to configured limits and identify if memory usage is approaching or exceeding limits.

6. Pod의 로그를 조회하고 <pod-name> Namespace <namespace> and filter for memory-related errors, allocation failures, or application memory issues that may indicate memory leaks or excessive usage.

## 진단

1. Pod 이벤트를 분석하여 플레이북 1-2 확인합니다 the OOMKilled termination reason. Events showing "OOMKilled" in the termination reason field confirm memory exhaustion as the root cause. Exit code 137 indicates SIGKILL (128 + 9).

2. If container termination reason shows "OOMKilled" (플레이북 1), there are two possible scenarios:
   - Container memory limit exceeded: The container used more memory than its configured limit (resources.limits.memory)
   - Node-level OOM: The node ran out of memory and the kernel killed the container

3. Pod 이벤트에서 OOMKilled without node MemoryPressure condition (플레이북 3), the issue is container-level memory limits being too restrictive. Compare actual memory usage (플레이북 5) with configured limits (플레이북 4) 판단합니다 appropriate limit increases.

4. If node conditions show MemoryPressure (플레이북 3), the issue is node-level memory exhaustion. Check system logs (dmesg) for kernel OOM killer messages and identify which processes consumed excessive memory.

5. If pod logs (플레이북 6) show memory allocation failures, OutOfMemoryError, or similar errors before termination, the application has a memory leak or insufficient heap configuration. Review application memory settings (e.g., JVM heap size, Node.js max-old-space-size).

6. 이벤트에서 recent deployment changes, correlate OOM kill onset with deployment rollout timestamps 파악합니다 if new application versions have higher memory requirements or memory leaks.

7. If memory usage metrics show gradual increase over time before OOMKill, investigate memory leaks in the application code or unbounded caching.

**명확한 근본 원인을 파악하지 못한 경우 from pod events**: Review application-specific memory configurations, check for memory-intensive operations that may cause spikes, verify if memory requests are set appropriately for scheduling, examine if other pods on the same node are consuming excessive memory, and consider implementing memory profiling 파악합니다 leak sources.

