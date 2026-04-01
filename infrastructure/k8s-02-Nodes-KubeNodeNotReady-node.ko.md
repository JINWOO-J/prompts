---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/02-Nodes/KubeNodeNotReady-node.md)'
role: SRE / K8s Incident Response
origin: scoutflo
tags:
- capacity
- infrastructure
- k8s-deployment
- k8s-node
- k8s-pod
- k8s-service
- kubenodenotready
- node
- nodes
- performance
- rds
---

---
title: Kube Node Not Ready — Node 준비 안 됨
weight: 20
---

# KubeNodeNotReady

## 의미

Node의 Ready 조건이 False 또는 Unknown으로 표시되어 KubeNodeNotReady 또는 KubeNodeUnreachable과 같은 알림이 발생합니다. 이는 Kubelet 헬스 체크가 실패하거나, Node가 리소스 압박(MemoryPressure, DiskPressure, PIDPressure) 상태이거나, Kubelet이 Control Plane과 안정적으로 통신할 수 없기 때문입니다. 클러스터 대시보드에서 Node가 NotReady 상태로 표시되고, Kubelet 로그에 연결 타임아웃 오류나 헬스 체크 실패가 기록되며, Node 메트릭에서 리소스 압박이나 연결 문제가 나타납니다. 이는 데이터 플레인에 영향을 미쳐 해당 Node에서 새로운 Pod 스케줄링이 불가능하고 기존 워크로드 유지도 어려워집니다. 일반적으로 Kubelet 장애, 리소스 고갈, 네트워크 연결 문제 또는 Node 하드웨어 문제가 원인이며, 영향받는 Node에서 실행 중인 애플리케이션에 오류가 발생하거나 접근이 불가능해질 수 있습니다.

## 영향

KubeNodeNotReady 알림이 발생하고, 해당 Node에 새로운 Pod를 호스팅할 수 없으며, 기존 Pod에 접근이 불가능해질 수 있습니다. 워크로드가 다른 Node로 재스케줄링될 수 있고, Node 상태가 NotReady로 전환됩니다. 해당 Node에 대한 Pod 스케줄링이 실패하고, Node 용량을 사용할 수 없게 됩니다. 영향받는 Node의 Pod가 접근 불가능해지거나 축출될 수 있으며, 해당 Node의 Pod에 대한 서비스 저하 또는 중단이 발생합니다. Pod가 Node 리소스를 기다리며 Pending 상태로 남고, kubectl에서 Node가 무기한 NotReady 상태로 표시됩니다. 클러스터 용량이 감소하고, Deployment에서 레플리카 수 불일치가 나타날 수 있으며, 영향받는 Node에서 실행 중인 애플리케이션에 오류나 성능 저하가 발생할 수 있습니다.

## 플레이북

1. Node <node-name>을 describe하여 다음을 확인합니다:
   - Conditions 섹션에서 Ready 상태 및 기타 압박 조건 확인
   - Events 섹션에서 NodeNotReady, KubeletNotReady 이벤트와 타임스탬프 확인
   - 할당된 리소스에서 현재 사용량 확인

2. 관련 오브젝트 이름 <node-name>과 종류 Node로 필터링된 이벤트를 마지막 타임스탬프 순으로 조회하여 Node 문제의 순서를 파악합니다.

3. Node <node-name>의 조건을 조회하여 Ready, MemoryPressure, DiskPressure, PIDPressure, NetworkUnavailable 상태와 lastTransitionTime을 확인합니다.

4. Node <node-name>의 리소스 사용량 메트릭을 조회하여 현재 CPU 및 메모리 사용률을 확인합니다.

5. SSH로 Node에 접속하여 Kubelet 상태를 확인합니다:
   - Kubelet 서비스가 실행 중인지 확인
   - 최근 10분간의 Kubelet 로그 조회
   - Kubelet 로그에서 오류 메시지 확인

6. Node의 디스크 및 메모리를 확인합니다 (SSH 필요):
   - 디스크 공간 사용량 확인
   - 메모리 가용량 확인
   - 프로세스 리소스 사용량 분석

7. 컨테이너 런타임 상태를 확인합니다 (SSH 필요):
   - containerd 또는 docker 서비스 상태 확인
   - 런타임이 응답하는지 확인

8. Node에서 API 서버 연결을 확인합니다 (SSH 필요): API 서버 헬스 엔드포인트를 테스트하여 Control Plane으로의 네트워크 경로를 확인합니다.

## 진단

1. 플레이북 1-2단계의 Node 이벤트를 분석하여 NotReady의 주요 원인을 파악합니다. "KubeletNotReady" 또는 "KubeletStopped" 사유의 이벤트는 Kubelet 서비스 문제를 나타냅니다. "NodeHasDiskPressure", "NodeHasMemoryPressure" 또는 "NodeHasPIDPressure" 사유의 이벤트는 리소스 고갈을 나타냅니다.

2. Node 이벤트가 Kubelet 문제(KubeletNotReady)를 나타내는 경우, 플레이북 5단계에서 Kubelet 서비스 상태를 확인합니다. Kubelet이 실행 중인지, 중지되었는지, 또는 크래시 루프 상태인지 확인합니다. Kubelet 로그에서 장애 원인을 설명하는 오류 메시지를 검토합니다.

3. Node 이벤트가 리소스 압박 조건을 나타내는 경우, 플레이북 3단계의 Node 조건과 대조하여 어떤 리소스가 고갈되었는지 파악합니다. 플레이북 6단계의 디스크 및 메모리 확인을 통해 구체적인 리소스 제약을 확인합니다.

4. Node 이벤트에서 Kubelet이나 리소스 문제가 나타나지 않는 경우, 플레이북 8단계의 API 서버 연결 결과를 확인합니다. 네트워크 연결 실패는 Kubelet이 Node 상태를 보고하지 못하게 하여 NotReady 상태를 유발합니다.

5. Node 이벤트가 컨테이너 런타임 문제(ContainerRuntimeDown)를 나타내는 경우, 플레이북 7단계에서 컨테이너 런타임 상태를 확인합니다. Kubelet은 컨테이너 런타임에 의존하므로 런타임이 비정상이면 기능할 수 없습니다.

6. Node 이벤트가 결론을 내리기 어려운 경우, 플레이북 4단계의 리소스 사용량 메트릭을 Node 용량과 비교하여 CPU 또는 메모리 고갈이 Kubelet 헬스 체크에 영향을 미치는지 확인합니다.

7. 플레이북 3단계의 Node 조건 lastTransitionTime을 분석하여 NotReady가 지속적인지(일관된 타임스탬프) 또는 간헐적인지(최근 전환) 판단합니다. 이를 통해 Node 장애와 네트워크 불안정을 구분할 수 있습니다.

**이벤트에서 근본 원인을 파악할 수 없는 경우**: Node 시스템 로그로 분석을 확장하고, 하드웨어 장애나 커널 문제를 확인하며, 여러 Node가 영향받는지 확인합니다(클러스터 전체 문제 가능성). 또한 Node 상태에 영향을 줄 수 있는 최근 변경 사항에 대한 인프라 변경 기록을 검토합니다.
