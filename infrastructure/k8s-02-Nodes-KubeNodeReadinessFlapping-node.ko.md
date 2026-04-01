---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/02-Nodes/KubeNodeReadinessFlapping-node.md)'
role: SRE / K8s Incident Response
origin: scoutflo
tags:
- capacity
- infrastructure
- k8s-deployment
- k8s-node
- k8s-pod
- k8s-service
- kubenodereadinessflapping
- node
- nodes
- performance
- rds
---

---
title: Kube Node Readiness Flapping — Node Readiness 상태 불안정
weight: 20
---

# KubeNodeReadinessFlapping

## 의미

Node의 Readiness 상태가 최근 15분 동안 여러 번 변경되어 KubeNodeReadinessFlapping 알림이 발생합니다. Node의 Ready 조건이 True와 False 사이를 반복적으로 전환하고 있으며, 이는 불안정한 Node 상태, 간헐적 연결 문제 또는 리소스 압박으로 인한 반복적인 헬스 체크 실패를 나타냅니다. 클러스터 대시보드에서 Node의 Ready 조건이 반복적으로 전환되고, Node 이벤트에 NodeNotReady와 NodeReady 전환이 표시되며, Node 조건에 간헐적인 MemoryPressure, DiskPressure 또는 NetworkUnavailable이 나타날 수 있습니다. 이는 데이터 플레인에 영향을 미치며 Pod 스케줄링 및 워크로드 중단을 유발할 수 있는 Node 불안정을 나타냅니다. 일반적으로 네트워크 불안정, 리소스 압박 변동 또는 Kubelet 헬스 체크 문제가 원인이며, 영향받는 Node에서 실행 중인 애플리케이션에 중단이 발생할 수 있습니다.

## 영향

KubeNodeReadinessFlapping 알림이 발생하고, 클러스터 배포 성능에 영향을 미칩니다. Node 상태가 Ready와 NotReady 사이를 반복적으로 전환하며, Pod가 반복적으로 재스케줄링될 수 있습니다. 워크로드에 중단이 발생하고, Node 용량 가용성이 변동합니다. 서비스 엔드포인트가 반복적으로 추가 및 제거될 수 있으며, Node 불안정으로 인해 Pod 스케줄링 및 워크로드 중단이 발생합니다. Node에서 반복적인 Ready 조건 전환이 나타나고, Pod가 반복적으로 재스케줄링될 수 있으며, 영향받는 Node에서 실행 중인 애플리케이션에 중단이나 성능 저하가 발생할 수 있습니다.

## 플레이북

1. Node <node-name>을 describe하여 다음을 확인합니다:
   - Conditions 섹션에서 Ready 상태, 전환 이력 및 타임스탬프 확인
   - Events 섹션에서 NodeNotReady 및 NodeReady 전환 확인
   - 압박 조건 (MemoryPressure, DiskPressure, PIDPressure, NetworkUnavailable)

2. Node <node-name>의 이벤트를 타임스탬프 순으로 조회하여 'NodeNotReady', 'NodeReady', 'KubeletNotReady'를 포함한 조건 전환 순서를 확인합니다.

3. Node <node-name>의 조건을 확인하여 Ready, MemoryPressure, DiskPressure, PIDPressure, NetworkUnavailable 상태와 lastTransitionTime을 확인합니다.

4. Pod Exec 도구 또는 SSH(Node 접근 가능 시)를 통해 Node <node-name>의 Kubelet 상태 및 헬스를 확인하여 Kubelet 불안정을 검증합니다.

5. Node <node-name>과 API 서버 엔드포인트 간의 네트워크 연결 안정성을 확인하여 간헐적 연결 문제를 파악합니다.

6. Node <node-name>의 리소스 사용량 메트릭을 조회하여 CPU 및 메모리 사용률을 확인하고 리소스 압박 패턴을 파악합니다.

## 진단

1. 플레이북 1-2단계의 Node 이벤트를 분석하여 Readiness 전환 패턴을 파악합니다. "NodeNotReady"와 "NodeReady" 전환을 보여주는 이벤트 수를 세고 타임스탬프를 기록하여 플래핑 빈도와 패턴을 이해합니다.

2. Node 이벤트가 빠른 전환(수분 내 여러 번)을 보이는 경우, 이는 일반적으로 Kubelet과 API 서버 간의 네트워크 연결 불안정을 나타냅니다. 플레이북 5단계에서 네트워크 연결 안정성을 확인하고 네트워크 테스트 결과를 이벤트 타임스탬프와 대조합니다.

3. Node 이벤트가 리소스 압박 조건(NodeHasMemoryPressure, NodeHasDiskPressure, NodeHasPIDPressure)과 함께 느린 전환을 보이는 경우, 플레이북 3단계의 Node 조건을 확인합니다. 임계값 근처에서 변동하는 리소스 압박은 조건이 토글되면서 Readiness 플래핑을 유발합니다.

4. Node 이벤트가 Kubelet 헬스 체크 실패(KubeletNotReady 후 KubeletReady)를 나타내는 경우, 플레이북 4단계에서 Kubelet 상태 및 헬스를 확인합니다. Kubelet 불안정이나 리소스 제약이 간헐적 헬스 체크 실패를 유발할 수 있습니다.

5. Node 이벤트가 리소스 메트릭과 상관관계가 있는 플래핑을 보이는 경우, 플레이북 6단계에서 CPU 및 메모리 사용률을 확인합니다. 용량 근처의 지속적인 높은 리소스 사용은 간헐적 헬스 체크 타임아웃을 유발합니다.

6. Node 이벤트가 여러 Node에서 동시에 Readiness 플래핑을 보이는 경우, 이는 개별 Node 문제가 아닌 API 서버 성능 문제, 네트워크 인프라 불안정 또는 Control Plane 리소스 제약과 같은 클러스터 전체 문제를 나타냅니다.

7. 플레이북 3단계의 Node 조건 lastTransitionTime 빈도를 분석하여 플래핑이 진행 중인지 또는 안정화되었는지 판단합니다. 이를 통해 문제가 현재 발생 중인지 또는 해결되었는지 평가할 수 있습니다.

**이벤트에서 근본 원인을 파악할 수 없는 경우**: 플래핑 전환 사이의 Kubelet 로그에서 경고를 검토하고, 간헐적 하드웨어 문제(디스크 I/O 스파이크, 메모리 압박)를 확인하며, 네트워크 인프라 안정성을 검증하고, Node 오토스케일링이나 Pod 스케줄링 패턴이 리소스 변동을 유발하는지 확인합니다.
