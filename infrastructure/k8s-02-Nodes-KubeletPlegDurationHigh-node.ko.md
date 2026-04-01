---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/02-Nodes/KubeletPlegDurationHigh-node.md)'
role: SRE / K8s Incident Response
origin: scoutflo
tags:
- infrastructure
- k8s-node
- k8s-pod
- kubeletplegdurationhigh
- node
- nodes
- performance
---

---
title: Kubelet Pod Lifecycle Event Generator Duration High — Kubelet PLEG 지속 시간 높음
weight: 20
---

# KubeletPlegDurationHigh

## 의미

Node에서 Kubelet Pod Lifecycle Event Generator(PLEG)의 99번째 백분위 지속 시간이 임계값을 초과하고 있습니다(KubeletPlegDurationHigh 알림 발생). PLEG가 Pod 라이프사이클 이벤트를 생성하는 데 너무 오래 걸리고 있으며, 이는 컨테이너 런타임 성능 문제, 높은 Pod 밀도 또는 Node 리소스 제약을 나타냅니다.
 Kubelet PLEG 지속 시간 메트릭이 임계값을 초과하는 높은 값을 보이고, Kubelet 로그에 PLEG 관련 성능 문제가 나타나며, Node 조건에 MemoryPressure 또는 DiskPressure가 표시될 수 있습니다. 이는 데이터 플레인에 영향을 미치며, Pod 상태 업데이트 및 라이프사이클 관리를 지연시킬 수 있는 Kubelet 성능 저하를 나타냅니다. 일반적으로 컨테이너 런타임 속도 저하, 높은 Pod 밀도 또는 리소스 압박이 원인이며, 영향받는 Node에서 실행 중인 애플리케이션의 Pod 상태 업데이트가 지연될 수 있습니다.

## 영향

KubeletPlegDurationHigh 알림이 발생하고, Kubelet Pod 라이프사이클 관리가 느려집니다. Pod 상태 업데이트가 지연되고, 컨테이너 런타임 작업이 느려질 수 있습니다. Pod 시작 및 종료가 지연될 수 있으며, Node 성능이 저하됩니다. 높은 Pod 밀도가 Node 운영에 영향을 줄 수 있고, Pod 라이프사이클 이벤트 생성이 지연됩니다. Kubelet PLEG 지속 시간 메트릭이 지속적으로 높은 값을 보이며, Pod 상태 업데이트가 지연되고, 컨테이너 런타임 작업이 느려집니다. 영향받는 Node에서 실행 중인 애플리케이션의 Pod 상태 업데이트가 지연되거나 성능이 저하될 수 있습니다.

## 플레이북

1. Node <node-name>을 describe하여 다음을 확인합니다:
   - Conditions 섹션에서 Ready 상태 및 압박 조건 (MemoryPressure, DiskPressure, PIDPressure) 확인
   - Events 섹션에서 PLEG 관련 또는 성능 문제 확인
   - 할당된 리소스 및 Pod 수 확인

2. Node <node-name>의 이벤트를 타임스탬프 순으로 조회하여 PLEG 성능과 관련될 수 있는 Node 문제의 순서를 확인합니다.

3. Node <node-name>의 Kubelet PLEG 지속 시간 메트릭을 조회하여 현재 PLEG 지속 시간 값을 확인하고 성능 저하를 파악합니다.

4. Pod Exec 도구 또는 SSH(Node 접근 가능 시)를 통해 Node <node-name>에서 Kubelet 로그를 조회하고, PLEG 관련 오류 패턴을 필터링하여 PLEG 문제를 파악합니다.

5. Node <node-name>에 스케줄링된 Pod를 조회하고 Node에 스케줄링된 Pod 수를 세어 높은 Pod 밀도를 확인합니다.

6. Node <node-name>의 컨테이너 런타임 상태 및 성능을 확인하여 컨테이너 런타임 문제를 파악합니다.

7. Node <node-name>의 메트릭을 조회하고 CPU, 메모리, 디스크 I/O를 포함한 Node 리소스 사용량을 확인하여 리소스 제약을 파악합니다.

## 진단

1. 플레이북 1-2단계의 Node 이벤트를 분석하여 성능 관련 문제를 파악합니다. 리소스 압박(MemoryPressure, DiskPressure, PIDPressure) 또는 컨테이너 런타임 문제를 나타내는 이벤트가 PLEG 성능 저하의 맥락을 제공합니다. 이벤트 타임스탬프를 기록하여 PLEG 지속 시간 스파이크와 대조합니다.

2. Node 이벤트가 높은 Pod 밀도 또는 빈번한 Pod 변동을 나타내는 경우, 플레이북 5단계에서 Pod 수를 확인합니다. PLEG는 각 Pod의 상태를 위해 컨테이너 런타임에 쿼리해야 하므로, 높은 Pod 밀도는 PLEG 지속 시간을 직접적으로 증가시킵니다.

3. Node 이벤트가 리소스 압박 조건을 나타내는 경우, 플레이북 1단계의 Node 조건과 플레이북 7단계의 리소스 메트릭을 확인합니다. 메모리 압박이나 디스크 I/O 제약은 PLEG가 의존하는 컨테이너 런타임 작업을 느리게 합니다.

4. 플레이북 4단계의 Kubelet 로그에서 PLEG 관련 오류나 경고("PLEG is not healthy", "relist exceeded threshold")가 나타나는 경우, PLEG 성능 문제가 확인되며 구체적인 병목 지점을 나타낼 수 있습니다.

5. 플레이북 6단계의 컨테이너 런타임 상태에서 저하가 나타나는 경우, 컨테이너 런타임 성능을 확인합니다. PLEG 지속 시간은 컨테이너 런타임 응답성에 직접적으로 연결되어 있으므로, 느린 런타임은 느린 PLEG를 유발합니다.

6. 플레이북 3단계의 PLEG 지속 시간 메트릭이 리소스 압박 없이 지속적으로 높은 값을 보이는 경우, 컨테이너 상태 쿼리에 영향을 미치는 컨테이너 런타임 구성 문제나 기반 스토리지 성능 문제를 확인합니다.

7. PLEG 지속 시간이 일관적이지 않고 간헐적인 경우, 높은 Pod 스케줄링 활동이나 컨테이너 라이프사이클 이벤트 기간과 대조합니다. 버스트 활동은 일시적으로 PLEG 처리 용량을 초과할 수 있습니다.

**이벤트에서 근본 원인을 파악할 수 없는 경우**: 컨테이너 런타임 로그에서 성능 문제를 검토하고, 디스크 I/O 메트릭에서 스토리지 병목을 확인하며, Node가 Pod 밀도에 충분한 리소스를 가지고 있는지 검증하고, 컨테이너 런타임 구성(예: 컨테이너 로그 로테이션)이 오버헤드를 유발하는지 확인합니다.
