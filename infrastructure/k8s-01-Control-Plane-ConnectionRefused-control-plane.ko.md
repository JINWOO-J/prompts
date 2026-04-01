---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/01-Control-Plane/ConnectionRefused-control-plane.md)'
role: SRE / K8s Incident Response
origin: scoutflo
tags:
- connectionrefused
- control
- infrastructure
- k8s-namespace
- k8s-node
- k8s-pod
- k8s-service
- kubernetes
- plane
---

---
title: Connection Refused - 연결 거부 - Control Plane
weight: 221
categories:
  - kubernetes
  - control-plane
---

# ConnectionRefused-control-plane

## 의미

Kubernetes API Server 주소와 포트에 대한 TCP 연결이 적극적으로 거부되고 있으며(KubeAPIDown 또는 KubeletDown 알림 트리거 가능), 이는 API Server 프로세스가 수신 대기하지 않거나, 정상이 아니거나, 크래시했거나, 예상 인터페이스에서 접근할 수 없음을 나타냅니다. 연결 거부 오류는 API Server 프로세스 실패 또는 네트워크 바인딩 문제를 나타냅니다.

## 영향

모든 kubectl 명령이 연결 거부로 실패합니다. 클러스터 관리 작업을 수행할 수 없으며, Controller가 상태를 조정할 수 없고, 클러스터가 관리 불가능해집니다. 기존 워크로드는 계속 실행될 수 있지만 업데이트할 수 없습니다. KubeAPIDown 알림이 발생하고, API Server 프로세스가 실행되지 않으며, 연결 거부 오류가 발생합니다. Control Plane 컴포넌트가 통신할 수 없습니다.

## 플레이북

1. kube-system 네임스페이스에서 component=kube-apiserver 레이블을 가진 API Server Pod를 describe하여 상태, 재시작 횟수 및 컨테이너 상태를 포함한 상세 정보를 확인하고 연결 거부 원인을 식별합니다.

2. kube-system 네임스페이스에서 타임스탬프 순으로 이벤트를 조회하여 API Server 실패 또는 연결 오류를 필터링합니다.

3. 클러스터 구성을 조회하여 클라이언트와 Controller가 사용하는 API Server 엔드포인트, IP 및 포트를 확인합니다.

4. 각 Control Plane 노드에서 kubelet 서비스 상태와 로그를 확인하여 kubelet이 실행 중이고 정상이며 API Server Pod 또는 Static Pod를 시작하거나 관리할 수 있는지 확인합니다.

## 진단

1. 플레이북의 API Server Pod 이벤트를 분석하여 API Server Pod가 크래시하거나, 시작에 실패하거나, 종료되고 있는지 식별합니다. 이벤트에서 CrashLoopBackOff, Failed 또는 Pod 종료가 나타나면, API Server 프로세스 실패가 근본 원인입니다.

2. 이벤트에서 API Server Pod 재시작이 나타나면, 재시작 이벤트 타임스탬프와 연결 거부 오류 시작을 연관시킵니다. 연결 실패 시작 직전 또는 시작 시점에 재시작이 발생했다면, Pod 불안정성이 연결 문제를 유발하고 있습니다.

3. 이벤트에서 컨테이너 시작 실패 또는 구성 오류가 나타나면, API Server 컨테이너 상태와 로그를 검토합니다. 이벤트에서 이미지 풀 실패, 프로브 실패 또는 구성 검증 오류가 나타나면, 컨테이너 수준 문제가 API Server 시작을 방해하고 있습니다.

4. 이벤트에서 Control Plane 노드의 kubelet 문제가 나타나면, 플레이북 4단계의 kubelet 상태를 검증합니다. 연결 오류 이전 타임스탬프에서 kubelet 이벤트가 재시작 또는 실패를 보이면, kubelet 문제가 API Server Pod 관리를 방해하고 있습니다.

5. 이벤트에서 인증서 관련 오류가 나타나면, 플레이북의 인증서 만료 상태를 검증합니다. 연결 거부 오류 근처 타임스탬프에서 인증서 이벤트 또는 TLS 오류가 나타나면, 만료된 인증서가 API Server 실패를 유발했을 수 있습니다.

6. 이벤트에서 구성 변경(Static Pod 매니페스트, Deployment, ConfigMap)이 나타나면, 변경 타임스탬프와 오류 시작을 연관시킵니다. 연결 거부 오류 시작 전에 구성 수정이 발생했다면, 최근 변경이 API Server 구성을 손상시켰을 수 있습니다.

7. 이벤트에서 노드 수준 문제 또는 유지보수 활동이 나타나면, 노드 조건 변경과 연결 오류 타임스탬프를 연관시킵니다. 노드 이벤트에서 NotReady, MemoryPressure 또는 유지보수 Cordon이 나타나면, 노드 수준 문제가 API Server 가용성에 영향을 미치고 있습니다.

**연관 관계를 찾을 수 없는 경우**: 이전 API Server 연결 시도에 대해 kubelet 로그를 검토하고, 인증서 만료를 확인하며, Control Plane 노드 시스템 로그에서 프로세스 실패를 검토하고, 기록된 변경 외에 Static Pod 매니페스트가 수정되었는지 확인합니다. 연결 거부 오류는 점진적으로 발전한 API Server 프로세스 문제를 나타낼 수 있습니다.
