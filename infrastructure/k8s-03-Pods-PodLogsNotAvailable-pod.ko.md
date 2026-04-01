---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/03-Pods/PodLogsNotAvailable-pod.md)'
role: SRE / K8s Incident Response
origin: scoutflo
tags:
- alerting
- docker
- infrastructure
- k8s-namespace
- k8s-node
- k8s-pod
- kubernetes
- logging
- monitoring
- podlogsnotavailable
- pods
---

---
title: Pod Logs Not Available - Pod
weight: 267
categories:
  - kubernetes
  - pod
---

# PodLogsNotAvailable-pod — Pod 로그 불가용

## 의미

Pod 로그에 접근할 수 없습니다(일반적으로 monitoring gaps or log collection system failures rather than standard Prometheus alerts을 통해 감지)  container runtime (containerd, Docker) is not logging, log files are not being created on nodes, log collection systems are failing, or the logging driver is misconfigured. Pod logs cannot be retrieved kubectl logs, container runtime logs show logging errors, and log collection systems show gaps in log data. 이는 모니터링 및 문제 해결 능력에 영향을 미치며, 일반적으로 container runtime logging issues, disk space problems, or log collection system failures; application errors cannot be diagnosed.

## 영향

Pod logs are unavailable; troubleshooting is blocked; application debugging is impossible; log collection fails; monitoring systems cannot access logs; container runtime logging is broken; log-based alerting fails; `kubectl logs` commands return errors or empty results; centralized logging systems show gaps in log data; application errors cannot be diagnosed. Pod logs cannot be retrieved indefinitely; container runtime logs show logging errors; application errors cannot be diagnosed; troubleshooting is blocked and application debugging is impossible.

## 플레이북

1. Pod를 describe하고 <pod-name> Namespace <namespace> 확인합니다 its status and container states 확인합니다 if containers are running and should be producing logs.

2. Namespace에서 이벤트를 조회하고 <namespace> for pod <pod-name> 타임스탬프 순으로 정렬하여 파악합니다 pod-related events, focon events with reasons such as Failed or messages indicating log collection failures.

3. Attempt to retrieve logs from the pod <pod-name> Namespace <namespace> and check for errors indicating why logs are not available.

4. On the node where the pod is scheduled, check container runtime logging configuration Pod Exec tool or SSH if node access is available 확인합니다 if logging is enabled.

5. Check container runtime status on the node 확인합니다 if the runtime is functioning and can collect logs.

6. 확인합니다: log files exist on the node filesystem and check file permissions that may prevent log access.

## 진단

1. Pod 이벤트를 분석하여 플레이북 1-2 파악합니다 any container or logging-related failures. Events showing container failures or runtime errors may explain why logs are unavailable.

2. If kubectl logs returns "container not found" or similar error (플레이북 3), the container may have terminated and logs were garbage collected. For terminated containers, use `kubectl logs --previous` to retrieve logs from the previous container instance.

3. If kubectl logs returns empty results but the container is running (플레이북 1, 3), check:
   - Application is writing to stdout/stderr (not to files)
   - Container runtime is capturing stdout/stderr correctly
   - Log files exist on the node filesystem (플레이북 6)

4. If container runtime status shows errors (플레이북 5), the logging subsystem may be broken. Restart the container runtime service on the affected node.

5. If node disk is full or log directory has permission issues (플레이북 6), logs cannot be written:
   - Check disk usage with `df -h` on the node
   - Verify /var/log/containers and /var/log/pods directories are writable
   - Check for SELinux or AppArmor policies blocking log writes

6. If logging driver is misconfigured (플레이북 4), logs may be sent to an unsupported destination. Verify the container runtime is configured to use the json-file or journald logging driver.

7. If the pod was recently restarted multiple times, older logs may have been rotated out. Kubernetes only keeps logs from the current and previous container instances.

**복구를 위해 log availability**: Fix underlying storage or runtime issues, ensure the container writes to stdout/stderr, verify container runtime configuration, and consider implementing persistent logging to an external system for long-term retention.

