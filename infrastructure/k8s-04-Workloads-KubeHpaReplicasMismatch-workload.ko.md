---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/04-Workloads/KubeHpaReplicasMismatch-workload.md)'
role: SRE / K8s Incident Response
origin: scoutflo
tags:
- autoscal
- capacity
- infrastructure
- k8s-namespace
- k8s-pod
- kubehpareplicasmismatch
- performance
- scaling
- workload
- workloads
---

---
title: Kube HPA  Replicas Mismatch
weight: 20
---

# HPA Replica 불일치 (KubeHpaReplicasMismatch)

## 의미

HPA(Horizontal Pod Autoscaler)가 15분 이상 원하는 Replica 수와 일치하지 않는 상태입니다(KubeHpaReplicasMismatch 알림 발생). 리소스 제약, Quota 제한 또는 스케줄링 실패로 HPA가 원하는 수의 Pod를 스케줄링할 수 없기 때문입니다.
kubectl에서 HPA의 Replica 수가 불일치하며, Pod가 Pending 상태로 남고, Pod 이벤트에 InsufficientCPU, InsufficientMemory 또는 Unschedulable 오류가 표시됩니다. 이는 워크로드 플레인에 영향을 미치며 HPA가 원하는 스케일링을 달성하지 못하게 하는 용량 또는 설정 문제를 나타냅니다. 주로 클러스터 용량 제한, 리소스 Quota 소진 또는 지속적인 스케줄링 제약이 원인이며, ResourceQuota 제한이 Pod 생성을 방해할 수 있습니다.

## 영향

KubeHpaReplicasMismatch 알림이 발생하며, HPA가 원하는 Replica 수를 달성할 수 없습니다. 애플리케이션이 부족한 용량으로 실행되고, 성능 저하 또는 사용 불가가 발생합니다. 원하는 Replica가 현재 Replica를 초과하며, Pod 스케줄링 실패가 발생합니다. 자동 스케일링이 수요를 충족할 수 없고, Pod가 Pending 상태로 남습니다.

## 플레이북

1. namespace <namespace>에서 HPA <hpa-name>을 describe하여 다음을 확인합니다:
   - 현재 Replica 대비 원하는 Replica
   - 현재 Metrics 대비 목표 Metrics
   - Replica 불일치 이유를 보여주는 Condition
   - 스케일링 제약 또는 실패를 보여주는 Event

2. namespace <namespace>에서 HPA <hpa-name>의 이벤트를 타임스탬프 순으로 조회하여 Replica 불일치 문제 순서를 확인합니다.

3. namespace <namespace>에서 label app=<app-label>로 HPA가 관리하는 Pod를 조회하고 Pending 상태의 Pod를 describe하여 스케줄링 차단 요인(InsufficientCPU, InsufficientMemory, Unschedulable)을 식별합니다.

4. namespace <namespace>에서 ResourceQuota를 describe하고 리소스 Quota 상태를 확인하여 Quota가 Pod 생성을 방해하는지 확인합니다.

5. Node를 describe하고 할당된 리소스를 확인하여 추가 Pod 스케줄링을 위한 클러스터 전체 가용성을 검증합니다.

6. PriorityClass 리소스를 조회하고 HPA 관리 Pod의 Preemption을 유발할 수 있는 Pod Priority Class 설정을 확인합니다.

## 진단

1. 플레이북의 HPA 및 Pod 이벤트를 분석하여 원하는 Replica를 달성할 수 없는 이유를 파악합니다. 이벤트에 스케줄링 실패, Quota 오류 또는 스케일링 제약이 표시되면, 이벤트 타임스탬프를 사용하여 불일치가 시작된 시점을 확인합니다.

2. 이벤트가 Pod 스케줄링 실패를 나타내면(InsufficientCPU, InsufficientMemory, Unschedulable), 플레이북 3단계의 Pending Pod를 검사합니다. 스케줄링 이벤트에 구체적인 리소스 제약이 표시되면 클러스터 용량이 제한 요인입니다.

3. 이벤트가 리소스 Quota 소진을 나타내면, 플레이북 4단계의 ResourceQuota 상태를 확인합니다. Quota 이벤트에 제한 도달이 표시되면 namespace Quota가 추가 Pod 생성을 방해하는 것입니다.

4. 이벤트가 Node 용량 문제를 나타내면, 플레이북 5단계의 Node 할당 가능 리소스를 분석합니다. 클러스터 전체에서 Node 용량이 소진되었으면 클러스터 리소스 부족이 스케일링을 방해하는 것입니다.

5. 이벤트가 Node Taint 또는 Cordon을 나타내면, Node 스케줄링 가용성을 확인합니다. 불일치가 시작된 시점에 Node 이벤트에 Cordon 또는 Taint가 표시되면 스케줄링 가능한 Node 감소가 문제를 유발한 것입니다.

6. 이벤트가 Cluster Autoscaler 활동을 나타내면, Autoscaler 응답을 확인합니다. HPA 스케일링 시점에 Autoscaler 이벤트에 대기 중인 스케일업 또는 실패가 표시되면 Cluster Autoscaler가 추가 Node를 프로비저닝할 수 없는 것입니다.

7. 이벤트가 PriorityClass 또는 Preemption 문제를 나타내면, 플레이북 6단계의 Pod Priority 설정을 확인합니다. 낮은 우선순위의 HPA Pod가 Preemption되고 있으면 우선순위 조정이 필요할 수 있습니다.

**상관관계를 찾을 수 없는 경우**: 용량 분석을 위해 시간 범위를 1시간으로 확장하고, HPA 목표 Metric 설정을 검토하고, 지속적인 리소스 제약을 확인하고, PodDisruptionBudget을 검증하고, 과거 HPA 스케일링 패턴을 검사합니다. HPA Replica 불일치는 즉각적인 변경이 아닌 클러스터 용량 제한, 잘못 설정된 리소스 Quota 또는 지속적인 스케줄링 제약으로 인해 발생할 수 있습니다.
