---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/03-Pods/PodsOverloadedDuetoMissingHPA-workload.md)'
role: SRE / K8s Incident Response
origin: scoutflo
tags:
- autoscal
- infrastructure
- k8s-deployment
- k8s-namespace
- k8s-pod
- k8s-service
- kubernetes
- monitoring
- performance
- pods
- podsoverloadedduetomissinghpa
- sts
- workload
---

---
title: Pods Overloaded Due to Missing HPA - Workload
weight: 300
categories:
  - kubernetes
  - workload
---

# PodsOverloadedDuetoMissingHPA-workload — HPA 미설정으로 인한 Pod 과부하

## 의미

Pods are experiencing high load and performance degradation (triggering KubePodCPUHigh, KubePodMemoryHigh, or KubePodNotReady alerts)  no Horizontal Pod Autoscaler (HPA) is configured to scale the deployment based on CPU or memory metrics from metrics-server. Pods show high CPU or memory usage exceeding resource limits, pod metrics indicate resource utilization approaching thresholds, and application performance degrades. 이는 워크로드 플레인에 영향을 미치며, that deployments maintain a fixed replica count regardless of load, 일반적으로 missing HPA configuration; application errors may appear in application monitoring.

## 영향

Pods become overloaded with CPU or memory usage exceeding resource limits; application performance degrades; response times increase; pods may become unresponsive or crash under load; services experience high latency; pods may be terminated due to resource pressure; resource usage approaches or exceeds limits; KubePodCPUHigh alerts fire when pod CPU usage exceeds thresholds; KubePodMemoryHigh alerts fire when pod memory usage exceeds thresholds; KubePodNotReady alerts fire when pods become unresponsive; applications cannot handle traffic spikes; user-facing services are slow or unavailable; deployments cannot automatically scale to handle increased load. Pods show high CPU or memory usage indefinitely; application errors may appear in application monitoring; applications cannot handle traffic spikes and may experience errors or performance degradation; user-facing services are slow or unavailable.

## 플레이북

1. Describe deployment <deployment-name> Namespace <namespace> 확인합니다:
   - Current replica count versus expected load requirements
   - Resource requests and limits for all containers
   - Conditions showing pod health issues
   - Events showing resource pressure or performance issues

2. Retrieve events for deployment <deployment-name> Namespace <namespace> 타임스탬프 순으로 정렬하여 확인합니다 the sequence of resource-related events.

3. List HorizontalPodAutoscaler objects Namespace <namespace> and verify if an HPA exists for the deployment.

4. 확인합니다: the metrics-server is running in the kube-system namespace by listing pods with label k8s-app=metrics-server and verify metrics-server pod status.

5. Retrieve resource usage metrics for pods Namespace <namespace> with label app=<app-label> 확인합니다 if pods are approaching resource limits.

6. Pod를 describe하고 <pod-name> Namespace <namespace> and check resource usage 확인합니다 if pods are overloaded.

## 진단

1. Analyze deployment and pod events 플레이북 파악합니다 resource pressure indicators. 이벤트에서 OOMKilled, CPU throttling, or pod restarts due to resource limits, use event timestamps 판단합니다 when overload began.

2. 이벤트에서 high resource usage, verify whether HPA exists 플레이북 3. If no HPA is configured for the deployment, missing autoscaling is confirmed as the root cause allowing pods to become overloaded.

3. 이벤트에서 HPA exists but is not scaling, verify metrics-server status 플레이북 4. If metrics-server events show failures or unavailability at overload timestamps, metrics collection issues prevented HPA from functioning.

4. 이벤트에서 replica count changes, correlate changes with overload onset. If replica count was reduced before overload events, manual scaling down caused insufficient capacity.

5. 이벤트에서 deployment updates or rollouts, verify if new application version has different resource requirements. If deployment events occurred before overload, the new version may require more resources than allocated.

6. 이벤트에서 resource request modifications, verify if requests were reduced. If resource request events show decreases before overload, pods became less capable of handling existing load.

7. If events are inconclusive, analyze pod resource metrics 플레이북 5. If resource usage consistently approaches limits without overload events, gradual load increase has exceeded static capacity.

**If no correlation is found**: Extend the search window (30 minutes to 1 hour, 1 hour to 2 hours), review resource usage trends for gradual load increase, check for intermittent traffic spikes, examine if HPA was never configured and load gradually increased over time, verify if metrics-server experienced gradual performance degradation, and check for external factors like database slowdowns that may have increased application resource usage. Pod overload may result from gradual load growth rather than immediate changes.

