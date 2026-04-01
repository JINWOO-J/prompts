---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/03-Pods/PodsRestartingFrequently-pod.md)'
role: SRE / K8s Incident Response
origin: scoutflo
tags:
- infrastructure
- k8s-deployment
- k8s-namespace
- k8s-pod
- k8s-service
- kubernetes
- monitoring
- pods
- podsrestartingfrequently
---

---
title: Pods Restarting Frequently - Pod
weight: 269
categories:
  - kubernetes
  - pod
---

# PodsRestartingFrequently-pod — Pod 빈번한 재시작

## 의미

Pods are restarting frequently (triggering KubePodCrashLooping alerts)  applications are crashing due to errors, out-of-memory conditions, liveness probe failures, container runtime issues, or resource constraints. Pods show high restart counts in kubectl, pods enter CrashLoopBackOff state, and application logs show fatal errors, panic messages, or exceptions. 이는 워크로드 플레인에 영향을 미치며, unstable applications that cannot maintain running state, 일반적으로 application errors, OOM kills, or liveness probe failures; application crashes and exceptions may appear in application monitoring.

## 영향

Pods enter CrashLoopBackOff state; applications cannot maintain stable state; services experience frequent disruptions; pods consume resources but provide intermittent service; restart counts increase rapidly; application data may be lost on each restart; KubePodCrashLooping 알림 발생; deployments cannot achieve desired replica count; user-facing services are unreliable. Pods show high restart counts indefinitely; Pod가 CrashLoopBackOff state; application logs show fatal errors, panic messages, or exceptions; application crashes and exceptions may appear in application monitoring; applications cannot maintain stable state.

## 플레이북

1. Pod를 describe하고 <pod-name> Namespace <namespace> 확인합니다 restart count, last termination reason (OOMKilled, Error, Completed), exit code, and recent events showing why the pod is restarting.

2.  last termination state for pod <pod-name> Namespace <namespace> - if reason is OOMKilled, this is the root cause.

3. Pod의 이벤트를 조회하고 <pod-name> Namespace <namespace> 타임스탬프 순으로 정렬하여 확인합니다 OOMKill events, liveness probe failures, or container runtime errors.

4. Retrieve logs from the previous container instance for pod <pod-name> Namespace <namespace> 확인합니다 error messages and stack traces from before the crash.

5. Describe Deployment <deployment-name> Namespace <namespace> 확인합니다 resource requests/limits, liveness probe settings (timeoutSeconds, failureThreshold), and readiness probe configuration.

6. Retrieve resource usage metrics for pod <pod-name> Namespace <namespace> 확인합니다 if memory or CPU is approaching limits.

7. If OOMKilled, describe node <node-name> and check Conditions section 확인합니다 if node-level memory pressure is contributing.

## 진단

1. Pod 이벤트를 분석하여 플레이북 1-3 파악합니다 the primary restart reason. Order diagnosis by most common causes:

2. If termination reason shows "OOMKilled" (플레이북 1-2):
   - Container exceeded memory limits
   - Check memory usage metrics (플레이북 6) vs limits
   - Increase memory limits or fix memory leaks
   - Exit code 137 confirms OOM kill

3. If termination reason shows "Error" with non-zero exit code (플레이북 1):
   - Application crashed with error
   - Check previous container logs (플레이북 4) for stack traces
   - Common exit codes: 1 (general error), 139 (segfault), 143 (SIGTERM not handled)

4. 이벤트에서 liveness probe failures before restarts (플레이북 3):
   - Application became unresponsive
   - Check probe configuration (플레이북 5)
   - Verify probe timeouts are appropriate for application
   - Review if resource limits are caslow responses

5. 이벤트에서 "BackOff" indicating CrashLoopBackOff:
   - Container is crashing immediately after start
   - Check container command/args configuration
   - Verify required dependencies (ConfigMap, Secret, volumes) exist
   - Review application startup logs

6. If node shows resource pressure (플레이북 7):
   - Node-level issues affecting pod stability
   - Consider moving pod to a healthier node
   - 확인합니다: eviction is carestarts

7. If restarts correlate with deployment changes (플레이북 5):
   - New application version has bugs
   - Configuration changes broke the application
   - Consider rolling back to previous version

**To reduce restart frequency**: Fix the underlying cause identified in termination reason and logs. For OOMKilled, increase memory or fix leaks. For application errors, fix bugs or configuration. For probe failures, adjust probe timing or fix application responsiveness.

