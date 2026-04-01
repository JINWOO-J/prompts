---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/03-Pods/KubePodPending-pod.md)'
role: SRE / K8s Incident Response
origin: scoutflo
tags:
- capacity
- infrastructure
- k8s-deployment
- k8s-namespace
- k8s-node
- k8s-pod
- k8s-service
- kubepodpending
- kubernetes
- pods
- scaling
- sts
---

---
title: Kube Pod Pending
weight: 27
categories: [kubernetes, pod]
---

# KubePodPending — Pod Pending 상태

## 의미

Pod가 Pending 상태에 고착되어 있습니다(KubePodPending 알림 발생). 리소스 제약, Node Selector, Taint/Toleration, Affinity 규칙 또는 클러스터 용량 부족으로 인해 Kubernetes 스케줄러가 Pod를 배치할 적합한 노드를 찾지 못합니다.
 Pod 상태에 스케줄링 실패 이벤트와 함께 Pending이 표시되고, 노드가 할당되지 않으며, Pod를 시작할 수 없습니다. 이는 워크로드 플레인에 영향을 미치며, 클러스터 용량 또는 스케줄링 구성 문제를 나타냅니다. Deployment 완료 불가, 스케일링 작업 실패, 서비스 용량 제한.

## 영향

KubePodPending 알림 발생; Pod 시작 불가; Deployment Replica 불가용; 스케일링 작업 차단; HPA 효과적 스케일 업 불가; Job 실행 불가; 서비스 용량 감소; 배치 처리 지연; 새 애플리케이션 버전 배포 불가; 중요 워크로드 차단 가능; Pod가 대기하는 동안 클러스터 사용률이 가득 찬 것으로 표시.

## 플레이북

1. Namespace `<namespace>`에서 Pod `<pod-name>`을 조회하고 노드가 할당되지 않은 Pending 상태인지 확인합니다.

2. Namespace `<namespace>`에서 Pod `<pod-name>`의 이벤트를 조회하고 'FailedScheduling', 'Unschedulable', 'Insufficient' 등 스케줄링 이벤트를 필터링하여 구체적인 스케줄링 실패를 파악합니다.

3. Pod 리소스 request(CPU, 메모리)를 조회하고 노드의 가용 용량과 비교하여 리소스 제약을 파악합니다.

4. Pod 사양의 Node Selector를 확인하고 클러스터 노드에 일치하는 레이블이 존재하는지 확인합니다.

5. 노드 Taint를 조회하고 Pod에 Taint된 노드에 스케줄링하기 위한 적절한 Toleration이 있는지 확인합니다.

6. Pod Affinity 및 Anti-Affinity 규칙을 확인하여 불가능한 스케줄링 제약을 생성하지 않는지 확인합니다.

7. 모든 노드와 할당 가능한 리소스, 현재 사용량, 조건을 조회하여 Pod를 수용할 수 있는 노드가 있는지 파악합니다.

## 진단

Pod 리소스 request를 노드 가용 용량과 비교하고, request가 단일 노드가 제공할 수 있는 양을 초과하는지 확인합니다. 노드 할당 가능 리소스와 현재 Pod 할당을 근거로 판단합니다.

FailedScheduling 이벤트에서 구체적인 사유(Insufficient cpu, Insufficient memory, node(s) didn't match node selector)를 분석하고 차단 제약을 확인합니다. 스케줄러 이벤트와 Pod 사양을 근거로 판단합니다.

Pending Pod를 클러스터 전체 리소스 사용률과 상관 분석하고, 클러스터에 더 많은 노드가 필요한지(용량 문제) 또는 Pod가 잘못 구성되었는지(구성 문제) 확인합니다. 클러스터 리소스 메트릭과 Pending Pod 사양을 근거로 판단합니다.

PriorityClass가 스케줄링에 영향을 미치는지 확인하고, 낮은 우선순위 Pod가 선점되고 있는지 또는 Pending Pod의 우선순위가 너무 낮은지 확인합니다. Pod 우선순위와 선점 이벤트를 근거로 판단합니다.

Pod가 참조하는 PersistentVolumeClaim이 바인딩되어 있는지 확인합니다. 바인딩되지 않은 PVC는 Pod 스케줄링을 차단합니다. PVC 상태와 StorageClass 가용성을 근거로 판단합니다.

지정된 시간 범위 내에서 상관관계를 찾지 못한 경우: Namespace의 ResourceQuota 제한 확인, LimitRange 제약 확인, 상세 결정에 대한 스케줄러 로그 검토, Cluster Autoscaler가 노드를 추가할 수 있는지 확인, 노드 Cordon 또는 Drain이 스케줄링을 차단하지 않는지 확인합니다.
