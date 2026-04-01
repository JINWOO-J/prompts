---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/04-Workloads/CannotScaleDeploymentBeyondNodeCapacity-workload.md)'
role: SRE / K8s Incident Response
origin: scoutflo
tags:
- cannotscaledeploymentbeyondnodecapacity
- capacity
- infrastructure
- k8s-deployment
- k8s-namespace
- k8s-node
- k8s-pod
- kubernetes
- performance
- scaling
- sts
- workload
- workloads
---

---
title: Cannot Scale Deployment Beyond Node Capacity - Workload
weight: 275
categories:
  - kubernetes
  - workload
---

# Node 용량 초과로 Deployment 스케일링 불가 (CannotScaleDeploymentBeyondNodeCapacity-workload)

## 의미

사용 가능한 Node 용량을 초과하여 Deployment를 스케일링할 수 없는 상태입니다(KubePodPending 알림 발생). 모든 Pod의 총 리소스 요청량이 사용 가능한 Node의 할당 가능 리소스를 초과하거나, Node 용량 제약으로 추가 Pod를 스케줄링할 수 없기 때문입니다. Pod가 Pending 상태를 보이고, Pod 이벤트에 InsufficientCPU 또는 InsufficientMemory 오류가 표시되며, Node 할당 가능 리소스가 용량 부족을 나타냅니다. 이는 워크로드 플레인에 영향을 미치며 Deployment 스케일링을 제한합니다. 주로 리소스 요청 소진 또는 Node 용량 제약이 원인이며, 애플리케이션이 증가된 부하를 처리할 수 없어 오류가 발생할 수 있습니다.

## 영향

Deployment를 스케일업할 수 없으며, 원하는 Replica 수를 달성할 수 없습니다. Pod가 Pending 상태로 남고, 애플리케이션이 증가된 부하를 처리할 수 없습니다. 용량 제약이 성장을 제한하고, KubePodPending 알림이 발생하며, 스케줄러가 Pod를 배치할 수 없습니다. Replica 수가 원하는 상태와 불일치하며, 스케일링을 위해 수동 Node 추가가 필요합니다. Pod가 무기한 Pending 상태를 보이고, InsufficientCPU 또는 InsufficientMemory 오류가 표시되며, 애플리케이션이 증가된 부하를 처리할 수 없어 오류나 성능 저하가 발생할 수 있습니다.

## 플레이북

1. namespace <namespace>에서 deployment <deployment-name>을 describe하여 다음을 확인합니다:
   - Replica 상태 (desired/current/ready/available)
   - 모든 컨테이너의 리소스 요청 및 제한
   - 스케일링 실패 이유를 보여주는 Condition
   - FailedCreate, FailedScheduling 또는 InsufficientCPU/InsufficientMemory 오류를 보여주는 Event

2. namespace <namespace>에서 deployment <deployment-name>의 이벤트를 타임스탬프 순으로 조회하여 스케일링 실패 순서를 확인합니다.

3. Node를 describe하고 할당된 리소스를 확인하여 Node 용량을 분석하고, Deployment 리소스 요청과 비교하여 용량 제약을 파악합니다.

4. namespace <namespace>에서 label app=<app-label>로 Pending 상태의 Pod를 조회하고 Pod를 describe하여 리소스 제약이 스케줄링을 방해하는지 확인합니다.

5. namespace <namespace>에서 ResourceQuota를 describe하고 현재 사용량과 제한을 비교하여 Quota가 스케일링을 차단하는지 확인합니다.

6. 모든 Node를 조회하고 Taint를 확인하여 Deployment에 대해 Node가 사용 가능하고 스케줄링 가능한지 검증합니다.

## 진단

1. 플레이북의 Deployment 및 Pod 이벤트를 분석하여 스케줄링 실패를 파악합니다. 이벤트에 InsufficientCPU, InsufficientMemory, Unschedulable 또는 FailedScheduling이 표시되면, 이벤트 타임스탬프와 오류 메시지를 사용하여 구체적인 용량 제약을 식별합니다.

2. 이벤트가 CPU 또는 메모리 부족을 나타내면, 플레이북 3단계의 Node 용량을 분석합니다. 모든 Node가 높은 할당 비율을 보이면 클러스터 전체 용량 소진이 스케줄링을 방해하는 것입니다.

3. 이벤트가 스케줄링 제약 또는 Node Affinity 문제를 나타내면, 플레이북 4단계의 Pending Pod를 검사합니다. Pod에 배치 옵션을 제한하는 Node Selector, Affinity 또는 Anti-Affinity가 있으면 제약 설정이 너무 제한적인 것입니다.

4. 이벤트가 리소스 Quota 소진을 나타내면, 플레이북 5단계의 ResourceQuota 상태를 확인합니다. namespace Quota에 도달했다면 Node 용량이 아닌 Quota 제한이 스케일링을 차단하는 것입니다.

5. 이벤트가 Node Taint 또는 Cordon을 나타내면, 플레이북 6단계의 Node 스케줄링 상태를 확인합니다. 실패 시점에 Node가 Taint되거나 Cordon되었다면, 스케줄링 가능한 Node 감소가 용량 제약을 유발한 것입니다.

6. 이벤트가 경쟁 워크로드를 나타내면, 리소스를 소비하는 다른 Deployment를 식별합니다. 이 Deployment의 실패 전에 다른 워크로드 스케일링 이벤트가 발생했다면, 리소스 경쟁이 사용 가능한 용량을 줄인 것입니다.

7. 이벤트가 리소스 요청 수정을 나타내면, Pod 리소스 요청이 증가했는지 확인합니다. 스케줄링 실패 전에 요청 증가 이벤트가 발생했다면, Pod당 더 높은 요청이 사용 가능한 Node 용량을 초과한 것입니다.

**상관관계를 찾을 수 없는 경우**: 검색 범위를 확장하고(30분→1시간, 1시간→2시간), Node 리소스 사용량 추세에서 점진적 소진을 검토하고, 여러 Deployment의 누적 리소스 요청을 확인하고, Node 용량이 항상 부족했지만 최근에야 적용되었는지 검사하고, 기존 Pod의 리소스 요청이 시간이 지남에 따라 증가했는지 확인하고, Node 용량을 초과한 점진적 워크로드 증가를 확인합니다. 용량 초과 스케일링은 즉각적인 변경이 아닌 누적 리소스 사용으로 인해 발생할 수 있습니다.
