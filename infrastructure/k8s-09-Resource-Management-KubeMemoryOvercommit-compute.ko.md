---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/09-Resource-Management/KubeMemoryOvercommit-compute.md)'
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
- kubememoryovercommit
- management
- performance
- resource
- scaling
- sts
---

---
title: Kube Memory Overcommit - 메모리 오버커밋
weight: 20
aliases:
  - /kubememovercommit/
---

# KubeMemoryOvercommit

## 의미

클러스터가 Pod의 메모리 리소스 요청을 오버커밋하여 노드 장애를 견딜 수 없습니다(KubeMemoryOvercommit 알림 트리거). 모든 Pod의 총 메모리 요청이 가용 클러스터 용량을 초과하여 노드 장애 시 가용성을 유지할 수 없습니다.

## 영향

KubeMemoryOvercommit 알림 발생, 클러스터가 노드 장애를 견딜 수 없음, 노드 장애 시 일부 Pod가 Pending 상태, 새 워크로드 스케줄링 불가, InsufficientMemory 오류로 Pod 스케줄링 실패, 용량 제약으로 워크로드 배포 불가, 클러스터 복원력 저하. Pod 메모리 요청 할당이 총 노드 메모리 용량을 초과하며, 클러스터 오토스케일러가 노드 추가에 실패할 수 있습니다.

## 플레이북

1. 모든 노드를 describe하여 할당 가능한 메모리 리소스와 현재 메모리 요청 할당을 확인합니다.
2. 모든 namespace의 이벤트를 타임스탬프 순으로 조회하여 메모리 관련 스케줄링 실패와 리소스 제약 이벤트를 식별합니다.
3. 클러스터 전체의 Pod 리소스를 나열하고 메모리 요청 할당을 조회하여 총 노드 메모리 용량과 비교합니다.
4. 클러스터 오토스케일러 상태와 로그를 확인하여 노드 추가를 방해하는 문제를 검증합니다.
5. 노드 `<node-name>` 리소스를 조회하고 가용 클러스터 용량을 줄이는 cordon 또는 스케줄 불가 노드를 확인합니다.
6. 노드 `<node-name>` 메트릭을 조회하고 메모리 사용량과 메모리 요청을 비교하여 오버커밋 패턴을 식별합니다.
7. Namespace별 메모리 요청 분포를 분석하여 주요 소비자를 식별합니다.

## 진단

플레이북 섹션에서 수집한 노드 할당 가능 리소스, Pod 메모리 요청, 이벤트를 분석하는 것으로 시작합니다.

**이벤트에 Insufficient memory와 함께 FailedScheduling이 표시되는 경우:**
- 메모리 오버커밋으로 새 Pod를 스케줄링할 수 없습니다. 노드 추가, 기존 Pod의 메모리 요청 감소, 비핵심 워크로드 퇴거 중 하나를 수행합니다.

**노드 describe에서 높은 메모리 요청 할당 비율(100% 초과)이 표시되는 경우:**
- 총 메모리 요청이 노드 용량을 초과합니다. 플레이북의 Namespace 집계를 사용하여 가장 큰 메모리 요청을 가진 Pod를 식별합니다.

**클러스터 오토스케일러 로그에 "scale up needed but not possible"이 표시되는 경우:**
- 오토스케일러가 노드를 추가할 수 없습니다. 노드 풀 제한, 쿼터 제한, 클라우드 프로바이더 용량 문제를 확인합니다.

**특정 Namespace가 메모리 요청을 지배하는 경우:**
- 높은 소비 Namespace에 최적화를 집중합니다. 해당 Namespace의 Deployment에서 과도한 메모리 요청을 검토합니다.

**노드 cordon 또는 제거 후 오버커밋이 발생한 경우:**
- 용량 감소가 오버커밋을 유발했습니다. 노드가 정상이면 uncordon하거나, 대체 용량을 추가하거나, 나머지 노드로 워크로드를 재스케줄링합니다.

**명확한 원인이 식별되지 않는 경우:** Pod 전체의 메모리 요청과 실제 메모리 사용량을 비교합니다. 요청이 사용량을 크게 초과하는 Pod가 요청 감소 후보입니다. 요청 조정 전에 메트릭을 사용하여 기준 사용 패턴을 설정합니다.
