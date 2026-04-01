---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/02-Nodes/NodeNotReady-node.md)'
role: SRE / K8s Incident Response
origin: scoutflo
tags:
- capacity
- infrastructure
- k8s-node
- k8s-pod
- k8s-service
- kubernetes
- networking
- node
- nodenotready
- nodes
---

---
title: Node Not Ready — Node 준비 안 됨
weight: 204
categories:
  - kubernetes
  - node
---

# NodeNotReady-node

## 의미

Node의 Ready 조건이 False 또는 Unknown으로 표시되어 KubeNodeNotReady 또는 KubeNodeUnreachable과 같은 알림이 발생합니다. Kubelet 헬스 체크가 실패하거나, Node가 리소스 압박(MemoryPressure, DiskPressure, PIDPressure) 상태이거나, Kubelet이 Control Plane과 안정적으로 통신할 수 없기 때문입니다.
 이는 Pod 스케줄링 및 가용성에 영향을 미치는 Node 수준 장애를 나타냅니다.

## 영향

Node가 스케줄링 불가능해지고, Node의 Pod가 사용 불가능해지거나 재시작될 수 있습니다. 워크로드를 해당 Node에 스케줄링할 수 없으며, 서비스가 엔드포인트를 잃습니다. 애플리케이션이 용량 감소를 경험하고, KubeNodeNotReady 알림이 발생합니다. Node 상태가 NotReady로 전환되며, Kubelet 통신 장애가 발생합니다.

## 플레이북

1. Node <node-name>을 describe하여 다음을 확인합니다:
   - Conditions 섹션에서 Ready 상태 및 기타 압박 조건 확인
   - Events 섹션에서 NodeNotReady, KubeletNotReady 이벤트와 타임스탬프 확인
   - 레이블, Taint 및 할당된 리소스 확인

2. Node <node-name>의 이벤트를 타임스탬프 순으로 조회하여 Node 문제의 순서를 확인합니다.

3. Node <node-name>의 조건을 확인하여 Ready, MemoryPressure, DiskPressure, PIDPressure, NetworkUnavailable 상태와 lastTransitionTime을 확인합니다.

4. 영향받는 Node에서 Kubelet 서비스 로그(예: 마지막 100-500줄)를 확인하여 등록, 헬스 체크, 리소스 압박 또는 런타임 문제에 대한 오류를 확인합니다.

5. 영향받는 Node의 Pod(또는 클러스터의 테스트 Pod)에서 주요 클러스터 엔드포인트로의 네트워크 연결을 확인하여 Node 네트워킹이 작동하는지 확인합니다.

6. 영향받는 Node에서 컨테이너 런타임의 health 또는 info 명령을 사용하여 런타임 상태를 확인하고, 올바르게 실행되며 컨테이너를 시작할 수 있는지 확인합니다.

7. 영향받는 Node에서 Kubelet 클라이언트 인증서 유효성 및 만료를 확인하여 Kubelet이 API 서버에 인증할 수 있는지 확인합니다.

## 진단

1. 플레이북 1-2단계의 Node 이벤트를 분석하여 NotReady의 주요 원인을 파악합니다. "KubeletNotReady" 사유의 "NodeNotReady" 이벤트는 Kubelet 문제를 나타냅니다. "NodeHasDiskPressure", "NodeHasMemoryPressure" 또는 "NodeHasPIDPressure" 이벤트는 리소스 고갈 문제를 나타냅니다. "NodeNotSchedulable" 이벤트는 수동 cordon을 나타냅니다.

2. Node 이벤트가 Kubelet 문제(KubeletNotReady, KubeletStopped)를 나타내는 경우, 플레이북 4단계에서 Kubelet 서비스 상태를 확인하여 Kubelet이 실행되지 않거나 비정상인지 확인합니다. Kubelet 로그에서 크래시 원인, OOM Kill 또는 시작 실패를 확인합니다.

3. Node 이벤트가 리소스 압박(MemoryPressure, DiskPressure, PIDPressure)을 나타내는 경우, 플레이북 3단계의 Node 조건과 대조하여 어떤 리소스가 고갈되었는지 파악합니다. 압박 조건의 lastTransitionTime을 NotReady 전환 시간과 비교합니다.

4. Node 이벤트에서 네트워크 관련 오류가 나타나거나 최근 하트비트 업데이트가 없는 경우, 플레이북 5단계의 네트워크 연결 결과를 확인하여 Node-API 서버 통신을 방해하는 네트워크 문제를 파악합니다.

5. Node 이벤트에서 인증서 관련 오류나 인증 실패가 나타나는 경우, 플레이북 7단계에서 Node 인증서 유효성을 확인하고 인증서 만료 타임스탬프를 NotReady 전환 시간과 비교합니다.

6. Node 이벤트에서 컨테이너 런타임 오류(ContainerRuntimeDown, RuntimeUnhealthy)가 나타나는 경우, 플레이북 6단계에서 컨테이너 런타임 상태를 확인하여 Kubelet의 컨테이너 관리를 방해하는 런타임 문제를 확인합니다.

7. Node 이벤트가 결론을 내리기 어려운 경우, Node 조건 lastTransitionTime 타임스탬프를 Kubelet 로그 타임스탬프와 비교하여 Kubelet 크래시, 리소스 고갈 또는 외부 요인이 NotReady 상태를 트리거했는지 파악합니다.

**이벤트에서 근본 원인을 파악할 수 없는 경우**: NotReady 전환 이전의 Kubelet 로그에서 경고를 검토하고, Node 수준 시스템 문제(커널 패닉, 하드웨어 장애)를 확인하며, 여러 Node가 유사한 패턴을 보이는지 확인하여 클러스터 전체 문제를 파악하고, 최근 수정 사항에 대한 인프라 변경 기록을 검토합니다.
