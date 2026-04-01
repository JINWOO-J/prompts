---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/03-Pods/PodFailsReadinessProbe-pod.md)'
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
- podfailsreadinessprobe
- pods
---

---
title: Pod Fails Readiness Probe - Pod
weight: 212
categories:
  - kubernetes
  - pod
---

# PodFailsReadinessProbe-pod — Readiness Probe 실패

## 의미

Pod가 Readiness Probe 검사에 실패하고 있습니다(KubePodNotReady 알림 발생)  application is not responding on the probe endpoint, the probe configuration is incorrect, the application startup time exceeds probe delays, or network issues prevent probe execution. Pods show NotReady state in kubectl, pod events show Unhealthy events with "readiness probe failed" messages, and readiness probe checks fail repeatedly. 이는 워크로드 플레인에 영향을 미치며, pods from transitioning to Ready state, 일반적으로 application startup delays, probe configuration issues, or application errors; applications may show errors in application monitoring.

## 영향

Pods remain in NotReady state; services have no endpoints; 트래픽이 도달할 수 없음 application pods; 로드 밸런서가 Pod를 로테이션에서 제외; applications appear unavailable even if running; 롤링 업데이트 실패; deployments cannot achieve desired replica count; KubePodNotReady 알림 발생; pod status shows readiness probe failures. Pods show NotReady state indefinitely; pod events show Unhealthy events with "readiness probe failed" messages; applications may show errors in application monitoring; services have no endpoints and applications appear unavailable.

## 플레이북

1. Pod를 describe하고 <pod-name> Namespace <namespace> 확인합니다 Ready condition status and Events showing "Readiness probe failed" with the specific failure (HTTP error, connection refused, timeout).

2. Pod의 이벤트를 조회하고 <pod-name> Namespace <namespace> 사유로 필터링하여 Unhealthy 확인합니다 probe failure timestamps and messages.

3.  readiness probe configuration for pod <pod-name> Namespace <namespace> 확인합니다 path, port, initialDelaySeconds, periodSeconds, timeoutSeconds.

4. Execute a request to the readiness endpoint from inside pod <pod-name> 확인합니다 the endpoint is responding.

5. Pod의 로그를 조회하고 <pod-name> Namespace <namespace> 파악합니다 errors during initialization or dependency connection failures.

6. List endpoints for service <service-name> Namespace <namespace> 확인합니다 if pod is registered - if pod is not listed, readiness probe is failing.

7. Describe Deployment <deployment-name> Namespace <namespace> 확인합니다 if initialDelaySeconds is sufficient for application startup time.

8. Retrieve resource usage metrics for pod <pod-name> Namespace <namespace> 확인합니다 if resource constraints are caslow responses.

## 진단

1. Pod 이벤트를 분석하여 플레이북 1-2 파악합니다 readiness probe failures. Events showing "Unhealthy" with "Readiness probe failed" include the specific failure reason (HTTP status code, connection refused, timeout).

2. 이벤트에서 "connection refused" for HTTP/TCP probes (플레이북 2):
   - Application is not listening on the configured port
   - Verify application logs (플레이북 5) for startup errors
   - 확인합니다: application binds to correct interface (0.0.0.0 vs 127.0.0.1)
   - Verify the probe port matches application's listening port

3. 이벤트에서 HTTP error codes (4xx, 5xx) for HTTP probes:
   - 404: Probe path does not exist - verify httpGet.path is correct
   - 401/403: Authentication required - probe endpoint should not require auth
   - 500/503: Application error - check application logs for errors

4. 이벤트에서 "timeout" for probes:
   - Application is slow to respond - increase timeoutSeconds
   - Application startup is slow - increase initialDelaySeconds
   - Resource constraints caslow responses - check CPU/memory usage (플레이북 8)

5. If endpoint responds when tested manually (플레이북 4) but probe still fails:
   - Probe configuration mismatch (wrong port, path, or scheme)
   - Intermittent application issues under load
   - Network policy blocking kubelet probe traffic

6. If pod is not registered in service endpoints (플레이북 6), readiness probe is failing. The pod will not receive traffic until it passes readiness checks.

7. If initialDelaySeconds is too short (플레이북 7), probes fail before the application is ready. Set initialDelaySeconds to exceed typical application startup time.

**해결을 위해 readiness probe failures**: Fix application startup issues, adjust probe timing (initialDelaySeconds, timeoutSeconds, periodSeconds), verify probe endpoint configuration matches application, and ensure the endpoint returns HTTP 2xx or 3xx for success.

