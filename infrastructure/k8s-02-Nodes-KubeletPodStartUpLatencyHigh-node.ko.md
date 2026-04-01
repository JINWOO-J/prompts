---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/02-Nodes/KubeletPodStartUpLatencyHigh-node.md)'
role: SRE / K8s Incident Response
origin: scoutflo
tags:
- infrastructure
- k8s-node
- k8s-pod
- kubeletpodstartuplatencyhigh
- node
- nodes
- performance
- storage
---

---
title: Kubelet Pod Start Up Latency High — Kubelet Pod 시작 지연 높음
weight: 20
---

# KubeletPodStartUpLatencyHigh

## 의미

Node에서 Kubelet Pod 시작 99번째 백분위 지연 시간이 임계값을 초과하고 있습니다(KubeletPodStartUpLatencyHigh 알림 발생). Pod 시작에 너무 오래 걸리고 있으며, 일반적으로 Node 스토리지의 IOPS(초당 I/O 작업 수) 고갈, 컨테이너 이미지 풀 지연 또는 리소스 제약이 원인입니다.
 Kubelet Pod 시작 지연 메트릭이 임계값을 초과하는 높은 값을 보이고, Node 스토리지 I/O 메트릭이 IOPS 고갈을 나타내며, Node 조건에 DiskPressure가 표시될 수 있습니다. 이는 데이터 플레인에 영향을 미치며, Pod 시작 및 워크로드 가용성을 지연시키는 Node 성능 문제를 나타냅니다. 일반적으로 스토리지 성능 저하, 느린 이미지 풀 또는 디스크 압박이 원인이며, 애플리케이션이 사용 가능해지는 데 더 오래 걸립니다.

## 영향

KubeletPodStartUpLatencyHigh 알림이 발생하고, Pod 시작이 느려집니다. Pod 시작 지연이 임계값을 초과하며, 애플리케이션이 사용 가능해지는 데 더 오래 걸립니다. Pod 스케줄링에서 준비 완료까지의 시간이 연장되고, Node 성능이 저하됩니다. 컨테이너 런타임 작업이 느려지며, Pod 시작 작업이 예상보다 훨씬 오래 걸립니다. Kubelet Pod 시작 지연 메트릭이 지속적으로 높은 값을 보이고, Node 스토리지 I/O 메트릭이 IOPS 고갈을 나타냅니다. 애플리케이션이 사용 가능해지는 데 상당히 더 오래 걸리며, Pod 스케줄링에서 준비 완료까지의 시간이 연장됩니다. 애플리케이션의 시작이 지연되거나 성능이 저하될 수 있습니다.

## 플레이북

1. Node <node-name>을 describe하여 다음을 확인합니다:
   - Conditions 섹션에서 Ready 상태 및 DiskPressure 조건 확인
   - Events 섹션에서 Pod 시작 또는 성능 문제 확인
   - 할당된 리소스 및 현재 사용량 확인

2. Node <node-name>의 이벤트를 타임스탬프 순으로 조회하여 Pod 시작 지연과 관련될 수 있는 Node 문제의 순서를 확인합니다.

3. Node <node-name>의 Kubelet Pod 시작 지연 메트릭을 조회하여 현재 지연 값을 확인하고 성능 문제를 파악합니다.

4. Pod Exec 도구 또는 SSH(Node 접근 가능 시)를 통해 Node <node-name>에서 Kubelet 로그를 조회하고, Pod 시작 관련 패턴을 필터링하여 시작 지연을 파악합니다.

5. Node <node-name>의 메트릭을 조회하고 IOPS, 처리량, 지연을 포함한 Node 스토리지 I/O 메트릭을 확인하여 스토리지 성능 문제를 파악합니다.

6. Node <node-name>의 컨테이너 이미지 풀 시간 및 이미지 풀 성능을 확인하여 이미지 풀 지연을 파악합니다.

7. Node <node-name>의 메트릭을 조회하고 CPU, 메모리, 디스크를 포함한 Node 리소스 사용량을 확인하여 리소스 제약을 파악합니다.

## 진단

1. 플레이북 1-2단계의 Node 이벤트를 분석하여 Pod 시작 문제를 파악합니다. "FailedCreatePodSandBox", "ImagePullBackOff" 또는 "ContainerCreating" 지연을 보여주는 이벤트가 구체적인 시작 병목을 나타냅니다. 이벤트 타임스탬프와 영향받는 Pod를 기록합니다.

2. Node 이벤트가 DiskPressure 조건을 나타내는 경우, 플레이북 1단계의 Node 조건과 플레이북 5단계의 스토리지 I/O 메트릭을 대조합니다. 디스크 압박과 IOPS 고갈은 컨테이너 파일시스템 작업이 지연되어 Pod 시작을 직접적으로 느리게 합니다.

3. Node 이벤트에서 이미지 풀 지연("Pulling image" 이벤트의 긴 지속 시간)이 나타나는 경우, 플레이북 6단계에서 이미지 풀 성능을 확인합니다. 레지스트리에서의 느린 이미지 풀, 큰 이미지 크기 또는 네트워크 대역폭 제약이 시작 지연을 유발합니다.

4. Node 이벤트가 컨테이너 런타임 문제를 나타내는 경우, 플레이북 4단계의 Kubelet 로그에서 컨테이너 런타임 오류나 느린 작업을 확인합니다. 컨테이너 런타임 성능 저하는 모든 Pod 라이프사이클 작업에 영향을 미칩니다.

5. 플레이북 3단계의 Pod 시작 지연 메트릭이 일관되게 높은 값을 보이는 경우, 플레이북 7단계에서 Node 리소스 사용량을 확인합니다. CPU 또는 메모리 제약이 컨테이너 초기화 및 시작을 느리게 할 수 있습니다.

6. 시작 지연이 높은 Pod 밀도와 상관관계가 있는 경우, 현재 Pod 수를 정상 수준과 비교합니다. 높은 Pod 밀도는 컨테이너 런타임 오버헤드와 PLEG 처리 시간을 증가시켜 간접적으로 시작 지연에 영향을 줍니다.

7. 시작 지연이 일관적이지 않고 간헐적인 경우, 피크 사용 기간이나 많은 Pod가 동시에 시작되는 시점(배포 또는 Node 복구 중)의 리소스 경합 패턴을 확인합니다.

**이벤트에서 근본 원인을 파악할 수 없는 경우**: 컨테이너 런타임 로그에서 성능 문제를 검토하고, 스토리지 서브시스템 상태 및 IOPS 제한을 확인하며, 컨테이너 레지스트리로의 네트워크 연결을 검증하고, Node 하드웨어(디스크, 메모리)가 워크로드에 비해 저하되었거나 부족한지 확인합니다.
