---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/10-Monitoring-Autoscaling/AutoscalerNotAddingNodes-autoscaler.md)'
role: Kubernetes SRE
origin: scoutflo
extract_date: 2026-03-05
tags:
- autoscal
- autoscaler
- autoscalernotaddingnodes
- autoscaling
- capacity
- infrastructure
- k8s-configmap
- k8s-deployment
- k8s-namespace
- k8s-node
- k8s-pod
- k8s-rbac
- k8s-service
- kubernetes
- monitoring
- scaling
- sts
---

---
title: Autoscaler Not Adding Nodes - 오토스케일러 노드 추가 실패
weight: 236
categories:
  - kubernetes
  - autoscaler
---

# AutoscalerNotAddingNodes-autoscaler

## 의미

스케줄 불가하거나 리소스가 부족한 Pod가 있음에도 클러스터 오토스케일러가 추가 워커 노드를 프로비저닝하지 못하고 있습니다(KubePodPending 또는 KubeNodeUnschedulable 알림 트리거 가능). 일반적으로 오토스케일러 구성 문제, 노드 그룹 제한, 클라우드 프로바이더 통합 문제, 불충분한 RBAC 권한이 원인입니다.

## 영향

새 워크로드 시작 불가, Pending Pod가 스케줄링되지 않은 상태 유지, Deployment 스케일링 실패, 서비스가 용량 제약과 잠재적 불가용 경험, KubePodPending 알림 발생, Pod가 Pending 상태 유지, 클러스터 용량 확장 불가, 오토스케일러가 노드 프로비저닝 실패, 노드 그룹 제한 도달 가능, 오토스케일러 로그에 오류 표시.

## 플레이북

1. `kube-system` namespace에서 클러스터 오토스케일러 Deployment를 describe하여 상태, 구성, 이벤트를 확인합니다.
2. `kube-system` namespace의 이벤트를 타임스탬프 순으로 조회하여 오토스케일러 관련 이벤트와 스케일링 실패를 식별합니다.
3. `kube-system` namespace에서 클러스터 오토스케일러 ConfigMap을 조회하고 scale-down-delay-after-add, max-node-provision-time, min-nodes, max-nodes, 노드 그룹 설정 등 구성 파라미터를 확인합니다.
4. 모든 노드를 나열하고 현재 노드 수 대비 최대 노드 제한을 포함한 노드 풀 구성과 제한을 확인합니다.
5. `kube-system` namespace의 클러스터 오토스케일러 Pod 로그를 조회하고 "failed to scale", "node group limit reached", "insufficient permissions", "API rate limit exceeded" 등의 오류 패턴을 필터링합니다.
6. 모든 namespace에서 Pending 상태의 Pod를 나열하고 리소스 요청 기반으로 스케일링이 필요한 Pod를 필터링합니다.
7. `kube-system` namespace에서 클러스터 오토스케일러 서비스 계정과 역할 바인딩을 조회하여 RBAC 권한을 확인합니다.
8. 모든 namespace에서 PodDisruptionBudget 리소스를 나열하여 PDB가 스케일링에 필요한 퇴거를 방해하는지 확인합니다.

## 진단

1. 플레이북의 클러스터 오토스케일러 이벤트와 로그를 분석하여 노드가 추가되지 않는 이유를 식별합니다. "ScaleUpFailed"를 보여주는 이벤트나 오류 메시지가 특정 차단 요인을 나타냅니다. 일반적인 메시지: "node group limit reached", "failed to create node", "no available node groups".

2. 이벤트가 노드 그룹 제한 도달을 나타내면, 플레이북의 현재 노드 수와 최대 노드 제한을 비교합니다. 오토스케일러는 각 노드 그룹의 구성된 최대값을 초과하여 노드를 추가할 수 없습니다. 이는 실패가 아닌 구성 제한입니다.

3. 이벤트가 클라우드 프로바이더 오류(API 실패, 쿼터 초과, 인스턴스 유형 사용 불가)를 나타내면, 오토스케일러가 노드 추가를 시도하지만 클라우드 프로바이더가 요청을 거부하고 있습니다. 클라우드 프로바이더 쿼터, 리전 용량, 인스턴스 유형 가용성을 확인합니다.

4. 이벤트가 스케줄 가능한 노드 그룹이 없음을 나타내면, Pending Pod의 요구사항(노드 셀렉터, toleration, 리소스 요청)이 최소 하나의 노드 그룹에서 충족될 수 있는지 확인합니다.

5. 오토스케일러 로그에 권한 오류(forbidden, access denied)가 표시되면, 플레이북의 RBAC 권한을 확인합니다. 오토스케일러 서비스 계정에 노드 생성, 노드 그룹 읽기, 클라우드 프로바이더 API 상호작용 권한이 필요합니다.

6. Pending Pod가 존재하지만 오토스케일러에 스케일업 활동이 없으면, Pod에 모든 노드 그룹을 제외하는 스케줄링 제약이 있는지 확인합니다. 또한 Pending Pod가 DaemonSet 소유가 아닌지 확인합니다(DaemonSet은 오토스케일링을 트리거하지 않음).

7. 오토스케일러 Pod가 실행되지 않거나 재시작 중이면, 오토스케일러 Deployment 상태와 Pod 로그를 확인합니다. 오토스케일러 컨트롤러 자체가 비정상이면 노드를 추가할 수 없습니다.
