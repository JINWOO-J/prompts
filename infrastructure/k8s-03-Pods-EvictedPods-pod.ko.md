---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/03-Pods/EvictedPods-pod.md)'
role: SRE / K8s Incident Response
origin: scoutflo
tags:
- capacity
- evictedpods
- infrastructure
- k8s-deployment
- k8s-namespace
- k8s-node
- k8s-pod
- k8s-service
- kubernetes
- pods
- sts
---

---
title: Evicted Pods - Pod
weight: 205
categories:
  - kubernetes
  - pod
---

# EvictedPods-pod — Pod 축출(Eviction)

## 의미

리소스 압박 임계값(MemoryPressure, DiskPressure 조건으로 KubeNodeMemoryPressure 또는 KubeNodeDiskPressure 알림 발생)이 초과되어 kubelet이 노드에서 Pod를 강제 축출하고 있습니다.
 kubectl에서 Pod가 Evicted 상태로 표시되고, Pod 상태 사유에 리소스 압박 유형과 함께 Evicted가 표시되며, 노드 조건에 MemoryPressure 또는 DiskPressure가 표시됩니다. 이는 워크로드 플레인에 영향을 미치며, 일반적으로 메모리 또는 디스크 압박으로 인한 노드 리소스 고갈을 나타냅니다. 애플리케이션이 예기치 않은 재시작을 경험하고 오류가 발생할 수 있습니다.

## 영향

Pod가 강제 종료됨; 애플리케이션이 예기치 않은 재시작을 경험; Deployment가 Replica를 잃음; 서비스 불가용 가능; 애플리케이션이 메모리 내 상태를 잃을 수 있음; Pod 축출 이벤트 발생; 노드 압박 조건이 알림을 트리거; Pod 상태가 Evicted로 변경; 리소스 제약으로 Pod 스케줄링 불가. Pod가 무기한 Evicted 상태로 유지; 애플리케이션이 예기치 않은 재시작을 경험하고 오류가 발생할 수 있음; 메모리 내 상태 손실 가능.

## 플레이북

1. Namespace `<namespace>`에서 축출된 Pod 목록과 축출 사유를 조회하여 어떤 Pod가 왜 축출되었는지 파악합니다.

2. Namespace `<namespace>`에서 Evicted 사유로 필터링된 이벤트를 타임스탬프 순으로 조회하여 축출 시점과 어떤 노드가 축출을 트리거했는지 확인합니다.

3. Pod를 축출한 노드 `<node-name>`을 describe하고 다음을 확인합니다:
   - Conditions 섹션에서 MemoryPressure, DiskPressure, PIDPressure
   - Allocated resources 섹션에서 리소스 소비량
   - Events 섹션에서 타임스탬프가 포함된 축출 이벤트

4. 노드 `<node-name>`의 활성 조건을 조회하여 어떤 리소스 압박이 축출을 유발했는지 파악합니다.

5. Namespace `<namespace>`에서 Deployment `<deployment-name>`을 describe하여 리소스 request와 limit을 확인하고, 노드 용량과 비교하여 request가 너무 높은지 확인합니다.

6. 노드 `<node-name>`의 리소스 사용량 메트릭을 조회하여 현재 CPU 및 메모리 소비량을 확인합니다.

7. 디스크 압박의 경우, 노드에 SSH 접속하여 디스크 사용량을 확인하고 무엇이 디스크 공간을 소비하는지 파악합니다.

## 진단

1. 플레이북 1-2단계의 Pod 이벤트를 분석하여 축출 사유를 파악합니다. "Evicted"를 포함하는 이벤트에는 축출을 트리거한 특정 리소스 압박(메모리, 디스크, PID)이 포함됩니다.

2. 이벤트에서 MemoryPressure 축출이 확인된 경우(플레이북 2단계):
   - 노드 메모리 사용량이 축출 임계값을 초과
   - 노드 조건(플레이북 3-4단계)에서 MemoryPressure=True 확인
   - 노드 메트릭(플레이북 6단계)을 사용하여 메모리 다소비 Pod 파악
   - Pod는 QoS 순서로 축출: BestEffort 먼저, 그 다음 Burstable, 마지막으로 Guaranteed

3. 이벤트에서 DiskPressure 축출이 확인된 경우:
   - 노드 디스크 사용량이 축출 임계값을 초과
   - 노드의 디스크 사용량 확인(플레이북 7단계)
   - 일반적인 원인: Container 로그, 풀링된 이미지, emptyDir 볼륨
   - 노드에서 미사용 이미지와 오래된 로그 정리

4. 이벤트에서 PIDPressure 축출이 확인된 경우:
   - 노드에 실행 중인 프로세스가 너무 많음
   - Container에서 폭주하는 프로세스 생성 확인
   - 많은 자식 프로세스를 포크하는 애플리케이션 검토

5. Deployment 리소스 request가 낮은 경우(플레이북 5단계):
   - BestEffort Pod(request 없음)가 먼저 축출됨
   - Burstable Pod(requests < limits)가 다음으로 축출됨
   - 축출 우선순위를 개선하기 위해 적절한 request 설정

6. 노드 리소스 사용량이 지속적인 압박을 보이는 경우(플레이북 6단계):
   - 노드가 지속적으로 오버커밋 상태
   - 노드 추가 또는 워크로드 감소 고려
   - 정확한 스케줄링을 위한 Pod 리소스 request 검토

7. 축출된 Pod는 삭제될 때까지 Evicted 상태로 유지됩니다. Deployment 컨트롤러가 다른 노드에 대체 Pod를 생성합니다.

**향후 축출 방지를 위해**: 적절한 리소스 request와 limit 설정, 중요 Pod에 Guaranteed QoS 클래스 사용, 리소스 모니터링 및 알림 구현, 워크로드 피크에 대한 충분한 클러스터 용량 확보를 수행합니다.
