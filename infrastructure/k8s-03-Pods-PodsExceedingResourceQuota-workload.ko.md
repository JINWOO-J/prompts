---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/03-Pods/PodsExceedingResourceQuota-workload.md)'
role: SRE / K8s Incident Response
origin: scoutflo
tags:
- infrastructure
- k8s-deployment
- k8s-namespace
- k8s-pod
- k8s-service
- kubernetes
- performance
- pods
- podsexceedingresourcequota
- sts
- workload
---

---
title: Pods Exceeding Resource Quota - Workload
weight: 248
categories:
  - kubernetes
  - workload
---

# PodsExceedingResourceQuota-workload — Pod ResourceQuota 초과

## 의미

Pods cannot be created or updated (triggering KubePodPending alerts)  namespace ResourceQuota limits have been exceeded. ResourceQuota resources show current usage exceeding hard limits in kubectl, pod events show "exceeded quota" or "Forbidden" errors, and pod creation requests are rejected by the API server. 이는 워크로드 플레인에 영향을 미치며, new workloads from starting, 일반적으로 normal workload growth or inadequate quota sizing; applications cannot scale.

## 영향

New pods cannot be created; Deployment 스케일링 실패; pod creation requests are rejected; 애플리케이션을 배포할 수 없습니다 new replicas; 서비스가 새 Pod를 확보할 수 없음; Pod가 Pending state; KubePodPending 알림 발생; pod events show "exceeded quota" errors; namespace resource allocation is blocked. ResourceQuota resources show current usage exceeding hard limits indefinitely; pod events show "exceeded quota" or "Forbidden" errors; applications cannot scale and may experience errors or performance degradation.

## 플레이북

1. Describe deployment <deployment-name> Namespace <namespace> 확인합니다:
   - Resource requests and limits for all containers
   - Conditions showing why pod creation is failing
   - Events showing FailedCreate or quota exceeded errors

2. Retrieve events for deployment <deployment-name> Namespace <namespace> 타임스탬프 순으로 정렬하여 확인합니다 the sequence of quota-related errors.

3. Describe ResourceQuota objects Namespace <namespace> 파악합니다 which resource types have limits and compare used resources with hard limits.

4. List all pods Namespace <namespace> and analyse total resource requests 확인합니다 current namespace resource usage.

5. Pod를 describe하고 <pod-name> Namespace <namespace> and inspect its resource requests 확인합니다 which resources would exceed the quota.

6. 확인합니다: multiple deployments or workloads Namespace <namespace> are competing for the same quota limits by listing deployments, statefulsets, and daemonsets.

## 진단

1. Analyze deployment and pod events 플레이북 파악합니다 quota-related errors. 이벤트에서 "exceeded quota", "Forbidden", or "FailedCreate" errors, use event timestamps 판단합니다 when quota limits were first exceeded.

2. 이벤트에서 quota exceeded errors, examine ResourceQuota status 플레이북 3. If current usage equals or exceeds hard limits, identify which resource types (CPU, memory, pods, storage) are exhausted.

3. 이벤트에서 recent deployment scaling, correlate scaling timestamps with quota errors. If replica increase events occurred before quota errors, scaling requests pushed usage beyond quota limits.

4. 이벤트에서 resource request modifications, verify if per-pod requests were increased. If resource request events show increases before quota errors, higher per-pod allocation exceeded namespace quota.

5. 이벤트에서 new workload deployments, identify additional workloads consuming quota. If new deployment events occurred in the namespace before quota errors, competing workloads exhausted available quota.

6. 이벤트에서 ResourceQuota modifications, verify if limits were reduced. If quota modification events show reduced limits before errors, quota reduction caused existing workloads to exceed new limits.

7. 이벤트에서 PVC creation (for storage quotas), verify storage quota consumption. If PVC events occurred before quota errors and storage limits are reached, storage quota is the constraint.

**If no correlation is found**: Extend the search window (30 minutes to 1 hour, 1 hour to 2 hours), review namespace resource usage trends for gradual quota exhaustion, check for cumulative resource requests from multiple deployments, examine if quota limits were always too restrictive but only recently enforced, verify if resource requests in existing pods were increased over time, and check for gradual workload growth that exceeded quota capacity. Resource quota issues may result from cumulative resource usage rather than immediate changes.

