---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/04-Workloads/KubeHpaMaxedOut-workload.md)'
role: SRE / K8s Incident Response
origin: scoutflo
tags:
- autoscal
- capacity
- infrastructure
- k8s-namespace
- k8s-pod
- kubehpamaxedout
- performance
- scaling
- sts
- workload
- workloads
---

---
title: Kube HPA Maxed Out
weight: 20
---

# HPA 최대 Replica 도달 (KubeHpaMaxedOut)

## 의미

HPA(Horizontal Pod Autoscaler)가 15분 이상 최대 Replica로 실행되고 있는 상태입니다(KubeHpaMaxedOut 알림 발생). 지속적인 높은 리소스 수요에도 불구하고 설정된 최대 Replica 제한을 초과하여 스케일링할 수 없기 때문입니다.
HPA에 현재 Replica가 최대 Replica와 일치하는 것이 표시되고, HPA 목표 Metrics에 높은 리소스 사용률이 표시되며, Pod 리소스 사용량 Metrics에 지속적인 높은 수요가 표시됩니다. 이는 워크로드 플레인에 영향을 미치며 최대 Replica 제한이 너무 낮거나, 리소스 요청이 잘못 설정되었거나, 애플리케이션이 현재 할당된 것보다 더 많은 용량을 필요로 함을 나타냅니다. 주로 지속적인 높은 부하, 부적절한 최대 Replica 설정 또는 리소스 Quota 제약이 원인이며, ResourceQuota 제한이 추가 스케일링을 방해할 수 있습니다.

## 영향

KubeHpaMaxedOut 알림이 발생하며, HPA가 증가된 부하를 처리하기 위해 새 Pod를 추가할 수 없습니다. 애플리케이션 성능이 저하될 수 있고, 자동 스케일링이 효과가 없습니다. 원하는 Replica 수가 최대 Replica와 일치하며, 지속적인 높은 부하에서 애플리케이션이 사용 불가능해질 수 있습니다. 스케일링 작업이 차단되고, HPA 목표 Metrics가 지속적으로 더 많은 Replica가 필요함을 나타냅니다.

## 플레이북

1. namespace <namespace>에서 HPA <hpa-name>을 describe하여 다음을 확인합니다:
   - 현재 Replica, 원하는 Replica 및 최대 Replica
   - 현재 Metrics 대비 목표 Metrics
   - HPA가 최대에 도달했음을 보여주는 Condition
   - 스케일링 제약 또는 높은 사용률을 보여주는 Event

2. namespace <namespace>에서 HPA <hpa-name>의 이벤트를 타임스탬프 순으로 조회하여 스케일링 이벤트와 제약 순서를 확인합니다.

3. namespace <namespace>에서 label app=<app-label>로 Pod의 리소스 사용량 Metrics를 조회하여 높은 리소스 수요를 확인합니다.

4. namespace <namespace>에서 pod <pod-name>을 describe하여 리소스 요청 및 제한을 확인하고 실제 사용량과 비교하여 잘못된 설정을 식별합니다.

5. namespace <namespace>에서 ResourceQuota를 describe하고 현재 수준을 초과한 스케일링을 방해하는 리소스 Quota 제한을 확인합니다.

6. Node를 describe하고 할당된 리소스를 확인하여 HPA가 추가로 스케일링할 수 있는 경우 추가 Pod Replica를 지원할 수 있는지 검증합니다.

## 진단

1. 플레이북의 HPA 이벤트를 분석하여 HPA가 최대 Replica에 도달한 시점을 파악합니다. 이벤트에 최대 제한에 도달한 스케일링 시도가 표시되면, 이벤트 타임스탬프를 사용하여 최대 도달 상태의 지속 시간을 확인합니다.

2. 이벤트가 지속적인 높은 리소스 사용률을 나타내면, 플레이북 3단계의 Pod 리소스 Metrics를 확인합니다. 최대 Replica에서 목표 Metrics가 지속적으로 임계값을 초과하면 현재 수요에 비해 최대 Replica 제한이 너무 낮은 것입니다.

3. 이벤트가 리소스 Quota 제약을 나타내면, 플레이북 5단계의 ResourceQuota 상태를 확인합니다. HPA 최대를 늘려도 Quota 제한이 추가 Pod 생성을 방해하면 먼저 Quota 조정이 필요합니다.

4. 이벤트가 Node 용량 소진을 나타내면, 플레이북 6단계의 Node 용량을 분석합니다. 클러스터에 추가 Pod를 위한 용량이 없으면 클러스터 용량이 확장될 때까지 HPA 최대를 늘려도 도움이 되지 않습니다.

5. 이벤트가 잘못 설정된 리소스 요청을 나타내면, 플레이북 4단계의 Pod 리소스 요청과 실제 사용량을 비교합니다. Pod가 사용하는 것보다 더 많은 리소스를 요청하면 요청을 줄여 같은 용량 내에서 더 많은 Replica를 허용할 수 있습니다.

6. 이벤트에서 HPA가 예측 가능한 시간에 정기적으로 최대에 도달하면, 과거 패턴을 분석합니다. 최대 도달 기간이 트래픽 패턴(예: 업무 시간)과 일치하면 피크 수요에 맞게 최대 제한을 조정해야 합니다.

7. 이벤트가 애플리케이션 성능 문제를 나타내면, 높은 리소스 사용이 비효율적인 애플리케이션 동작 때문인지 확인합니다. 워크로드 대비 리소스 사용이 예상보다 높으면 애플리케이션 최적화가 스케일링 필요를 줄일 수 있습니다.

**상관관계를 찾을 수 없는 경우**: 용량 분석을 위해 시간 범위를 7일로 확장하고, HPA 목표 Metric 설정을 검토하고, 높은 리소스 사용을 유발하는 애플리케이션 성능 문제를 확인하고, Cluster Autoscaler 효과를 검증하고, 과거 스케일링 패턴을 검사합니다. HPA 최대 도달은 즉각적인 설정 문제가 아닌 지속적인 높은 부하, 부적절한 최대 Replica 제한 또는 애플리케이션 비효율성으로 인해 발생할 수 있습니다.
