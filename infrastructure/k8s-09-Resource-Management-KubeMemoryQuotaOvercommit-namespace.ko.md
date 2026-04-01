---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/09-Resource-Management/KubeMemoryQuotaOvercommit-namespace.md)'
role: Kubernetes SRE
origin: scoutflo
extract_date: 2026-03-05
tags:
- autoscal
- capacity
- compute
- infrastructure
- k8s-deployment
- k8s-namespace
- k8s-node
- k8s-pod
- kubememoryquotaovercommit
- management
- namespace
- performance
- resource
- scaling
- sts
---

---
title: Kube Memory Quota Overcommit - 메모리 Quota 오버커밋
weight: 20
aliases:
  - /kubememquotaovercommit/
---

# KubeMemoryQuotaOvercommit

## 의미

클러스터가 Namespace의 메모리 리소스 요청을 오버커밋했습니다(KubeMemoryQuotaOvercommit 알림 트리거). 모든 Pod의 총 메모리 요청이 가용 클러스터 용량을 초과하여 노드 장애를 견딜 수 없습니다.

## 영향

KubeMemoryQuotaOvercommit 알림 발생, 노드 장애 시 불충분한 메모리 리소스로 Pod가 Pending 상태, 새 워크로드 스케줄링 불가, Deployment 스케일링 실패, 클러스터가 노드 장애를 견딜 수 없음, InsufficientMemory 오류로 Pod 스케줄링 실패. ResourceQuota 리소스에 메모리 요청 사용량이 가용 클러스터 용량을 초과하는 것으로 표시됩니다.

## 플레이북

1. namespace `<namespace>`에서 ResourceQuota `<quota-name>`을 describe하여 상태를 확인하고 메모리 요청 사용량 대비 쿼터 제한을 확인합니다.
2. namespace `<namespace>`의 이벤트를 타임스탬프 순으로 조회하여 쿼터 관련 이벤트와 리소스 할당 문제를 식별합니다.
3. namespace `<namespace>`의 Pod 리소스를 나열하고 메모리 요청을 집계하여 Namespace 쿼터와 비교합니다.
4. 노드 `<node-name>` 리소스를 조회하고 모든 노드의 할당 가능한 메모리 리소스와 현재 메모리 요청 할당을 확인합니다.
5. 클러스터 오토스케일러 상태와 로그를 확인하여 노드 추가를 방해하는 문제를 검증합니다.
6. 노드 `<node-name>` 리소스를 조회하고 가용 클러스터 용량을 줄이는 cordon 또는 스케줄 불가 노드를 확인합니다.
7. 노드 `<node-name>` 메트릭을 조회하고 메모리 사용량과 메모리 요청을 비교하여 오버커밋 패턴을 식별합니다.

## 진단

1. 플레이북의 이벤트를 분석하여 메모리 관련 스케줄링 실패를 식별합니다. "InsufficientMemory" 또는 "FailedScheduling"을 보여주는 이벤트는 메모리 제약으로 배치할 수 없는 Pod를 나타냅니다.

2. 이벤트가 불충분한 메모리로 인한 Pod Pending을 나타내면, 모든 Pod의 총 메모리 요청을 플레이북의 총 노드 할당 가능 메모리와 비교합니다.

3. 오버커밋이 노드 제거 또는 cordon 이벤트와 상관되면, 용량 감소가 오버커밋 조건을 유발한 것입니다.

4. 오버커밋이 최근 스케일링 또는 배포 이벤트와 상관되면, 해당 작업이 가용 용량을 초과하여 메모리 요청을 증가시킨 것입니다.

5. 클러스터 오토스케일러 이벤트에 스케일링 실패가 표시되거나 Pending Pod에도 불구하고 스케일링 활동이 없으면, 플레이북의 오토스케일러 상태를 확인합니다.

6. 오버커밋이 존재하지만 현재 Pending Pod가 없으면, 노드 장애가 발생할 때까지 클러스터가 이 조건을 견딜 수 있습니다.

7. Namespace 전체의 메모리 요청이 실제 메모리 사용량을 크게 초과하면, Pod 메모리 요청의 적정 크기 조정을 고려합니다.
