---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/03-Pods/PendingPods-pod.md)'
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
- kubernetes
- pendingpods
- pods
- sts
---

---
title: Pending Pods - Pod
weight: 203
categories:
  - kubernetes
  - pod
---

# PendingPods-pod — Pod Pending 상태 지속

## 의미

Pod가 Pending 단계에 고착되어 있습니다(KubePodPending 알림 발생). 스케줄러가 리소스 요구사항, Affinity 규칙, Taint, Node Selector 또는 기타 배치 제약을 충족하는 노드를 찾지 못합니다.
 kubectl에서 Pod가 Pending 상태를 보이고, Pod 이벤트에 InsufficientCPU, InsufficientMemory 또는 Unschedulable 오류와 함께 "0/X nodes are available" 메시지가 표시되며, ResourceQuota 리소스에 초과된 제한이 표시될 수 있습니다. 이는 워크로드 플레인에 영향을 미치며, 리소스 제약, 노드 Taint/Toleration 불일치 또는 ResourceQuota 제한으로 인해 Pod 배치를 방해합니다. 애플리케이션을 시작할 수 없습니다.

## 영향

새 워크로드 시작 불가; Deployment 스케일링 실패; 애플리케이션 불가용 상태 유지; 서비스가 새 Pod를 확보할 수 없음; 용량 제약으로 워크로드 배포 불가; KubePodPending 알림 발생; Pod가 Pending 상태로 유지; 스케줄러가 Pod를 배치할 수 없음; Replica 수가 원하는 상태와 불일치.

## 플레이북

1. Namespace `<namespace>`에서 Pod `<pod-name>`을 describe하고 Events 섹션을 확인합니다. 스케줄러가 Pod를 스케줄링할 수 없는 정확한 이유를 설명합니다(예: "0/5 nodes are available: 3 Insufficient cpu, 2 node(s) had taint that the pod didn't tolerate").

2. Namespace `<namespace>`에서 Pod `<pod-name>`의 이벤트를 FailedScheduling 사유로 필터링하여 스케줄링 실패 사유를 확인합니다.

3. Namespace `<namespace>`에서 Pod `<pod-name>`의 리소스 request를 조회하고 노드 리소스 메트릭을 사용하여 가용 노드 용량과 비교합니다.

4. 모든 노드의 Taint를 나열하고 Namespace `<namespace>`에서 Pod `<pod-name>`에 구성된 Toleration과 비교합니다.

5. Namespace `<namespace>`에서 Pod `<pod-name>`의 Node Selector와 Affinity 규칙을 조회하여 배치 제약을 파악합니다.

6. Namespace `<namespace>`의 ResourceQuota 리소스를 describe하여 CPU/메모리/Pod 수 할당량이 소진되었는지 확인합니다.

7. Namespace `<namespace>`의 PodDisruptionBudget을 나열하여 PDB가 Pod 스케줄링을 차단하는지 확인합니다.

8. Cluster Autoscaler 상태를 확인합니다(활성화된 경우). kube-system Namespace에서 ScaleUp 사유로 필터링된 이벤트를 조회하여 새 노드가 프로비저닝되고 있는지 확인합니다.

## 진단

1. 플레이북 1-2단계의 Pod 이벤트를 분석하여 스케줄링 실패 사유를 파악합니다. 스케줄러가 "0/X nodes are available: ..." 형태의 상세 메시지와 각 노드가 거부된 이유를 제공합니다.

2. 이벤트에서 리소스 문제가 확인된 경우(플레이북 2단계):
   - "Insufficient cpu": Pod CPU request가 가용 용량을 초과
   - "Insufficient memory": Pod 메모리 request가 가용 용량을 초과
   - Pod request(플레이북 3단계)를 노드 용량과 비교하고 request를 줄이거나 노드를 추가

3. 이벤트에서 Taint 문제가 확인된 경우(플레이북 4단계):
   - "node(s) had taint {key=value:effect} that pod didn't tolerate"
   - Pod 사양에 Toleration을 추가하거나 노드에서 Taint를 제거
   - 유지보수를 위해 최근 노드에 Taint가 적용되었는지 확인

4. 이벤트에서 Affinity/Selector 문제가 확인된 경우(플레이북 5단계):
   - "node(s) didn't match Pod's node affinity/selector"
   - 필요한 레이블이 있는 노드가 존재하고 스케줄 가능한지 확인
   - 배치 제약이 너무 제한적이면 완화

5. ResourceQuota가 초과된 경우(플레이북 6단계):
   - Namespace가 CPU, 메모리 또는 Pod 수 제한에 도달
   - 할당량을 증가시키거나 Namespace의 리소스 사용량을 줄임

6. PodDisruptionBudget이 스케줄링을 차단하는 경우(플레이북 7단계):
   - 이미 너무 많은 Pod가 중단됨
   - 기존 중단이 해결될 때까지 대기

7. Cluster Autoscaler가 스케일 업하지 않는 경우(플레이북 8단계):
   - Autoscaler 로그에서 오류 확인
   - 클라우드 제공자 할당량이 새 노드를 허용하는지 확인
   - 노드 풀 구성이 Pod 요구사항과 일치하는지 확인

**Pending Pod 해결을 위해**: 스케줄러 메시지에서 파악된 구체적인 스케줄링 제약을 해결합니다. 일반적인 해결책으로는 노드 추가, 리소스 request 조정, Toleration 추가 또는 배치 제약 완화가 있습니다.
