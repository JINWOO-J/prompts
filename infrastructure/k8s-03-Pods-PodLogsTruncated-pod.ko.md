---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/03-Pods/PodLogsTruncated-pod.md)'
role: SRE / K8s Incident Response
origin: scoutflo
tags:
- infrastructure
- k8s-namespace
- k8s-node
- k8s-pod
- kubernetes
- logging
- monitoring
- podlogstruncated
- pods
- storage
---

---
title: Pod Logs Truncated - Pod
weight: 282
categories:
  - kubernetes
  - pod
---

# PodLogsTruncated-pod — Pod 로그 잘림

## 의미

Pod 로그가 잘리고 있습니다(일반적으로 log analysis or monitoring gaps rather than standard Prometheus alerts을 통해 감지)  container runtime log rotation settings limit log size, log buffers are too small, or log retention policies are too aggressive. Pod logs show truncated entries, container runtime log rotation configuration shows aggressive limits, and log files on nodes are rotated before collection. 이는 모니터링 및 문제 해결 능력에 영향을 미치며, 일반적으로 log rotation settings or disk space constraints; important log information is lost.

## 영향

Pod logs are incomplete; log entries are truncated; troubleshooting is impaired; important log information is lost; log analysis is incomplete; container runtime log rotation is too aggressive; historical log data is unavailable; `kubectl logs` commands return partial log output; log files on nodes are rotated before collection; critical error messages may be lost in truncated logs. Pod logs show truncated entries indefinitely; container runtime log rotation configuration shows aggressive limits; important log information is lost; troubleshooting is impaired and critical error messages may be lost.

## 플레이북

1. Pod를 describe하고 <pod-name> Namespace <namespace> 확인합니다 pod status and container states 파악합니다 the pod configuration and logging context.

2. Namespace에서 이벤트를 조회하고 <namespace> for pod <pod-name> 타임스탬프 순으로 정렬하여 파악합니다 pod-related events that may indicate logging or storage issues.

3. Pod의 로그를 조회하고 <pod-name> Namespace <namespace> and verify if logs are truncated by checking for cut-off entries or missing log lines.

4. On the node where the pod is scheduled, check container runtime log rotation configuration Pod Exec tool or SSH if node access is available 확인합니다 log size limits and rotation settings.

5. Check container runtime log buffer settings 확인합니다 if buffers are too small and catruncation.

6. Verify log file sizes on the node filesystem 확인합니다 if log files are being rotated or truncated.

7. Check cluster logging system configuration if centralized logging is used 확인합니다 if log collection is truncating logs.

8. Review container runtime documentation for default log size limits and rotation policies.

## 진단

1. Pod 이벤트를 분석하여 플레이북 1-2 파악합니다 any storage or logging-related issues. Events showing disk pressure or container runtime errors may indicate the cause of log truncation.

2. If pod logs show cut-off entries or missing lines (플레이북 3), verify container runtime log rotation settings (플레이북 4):
   - Docker: Check --log-opt max-size and --log-opt max-file settings
   - Containerd: Check max-size and max-file in config.toml

3. If log files on the node are small despite heavy log output (플레이북 6), the container runtime is rotating logs aggressively. Common default limits:
   - Docker: 10MB per log file, 1 file (no rotation)
   - Containerd: configurable, often 10-100MB

4. If node shows DiskPressure condition or low disk space, the runtime may be truncating logs to free space. Clear disk space or increase node storage capacity.

5. If container runtime log buffer is too small (플레이북 5), individual log lines may be truncated. This typically affects very long log lines (>16KB).

6. If centralized logging is configured (플레이북 7), check if the log shipper (Fluentd, Filebeat, etc.) is failing to collect logs before rotation. Common issues include:
   - Log shipper pod not running
   - Log shipper falling behind on high-volume logs
   - Network issues preventing log delivery

7. If application produces excessive logs, consider implementing application-level log rate limiting or adjusting log verbosity to reduce output volume.

**방지를 위해 log truncation**: Increase container runtime log size limits, ensure adequate node disk space, configure centralized logging with sufficient collection capacity, and review application logging patterns to reduce unnecessary verbose output.

