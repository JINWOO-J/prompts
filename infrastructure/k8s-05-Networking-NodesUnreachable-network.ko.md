---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/05-Networking/NodesUnreachable-network.md)'
role: Kubernetes SRE
origin: scoutflo
extract_date: 2026-03-05
tags:
- capacity
- infrastructure
- k8s-daemonset
- k8s-namespace
- k8s-node
- k8s-pod
- k8s-service
- kubernetes
- network
- networking
- nodesunreachable
- sts
---

---
title: Nodes Unreachable - Network
weight: 270
categories:
  - kubernetes
  - network
---

# NodesUnreachable-network - 노드 접근 불가

## 의미

하나 이상의 노드가 접근 불가로 표시되었으며(KubeNodeUnreachable 알림 발생), Control Plane이 클러스터 네트워크를 통해 해당 노드의 kubelet과 안정적으로 통신할 수 없는 것이 원인입니다. 노드 접근 불가는 네트워크 파티션, kubelet 장애 또는 노드-Control Plane 간 통신을 방해하는 연결 문제를 나타냅니다.

## 영향

노드 간 통신 불가, Pod 간 통신 실패, 접근 불가 노드의 Pod에 Service가 접근 불가, 클러스터 네트워킹 중단, 애플리케이션 연결 문제 발생, KubeNodeUnreachable 알림 발생, 노드 Ready 상태가 Unknown으로 변경, kubelet 통신 실패, 접근 불가 노드에서 Pod 스케줄링 실패.

## 플레이북

1. 접근 불가 노드 `<node-name>`을 상세 조회하여 상태, 주소, 용량, 이벤트를 포함한 상세 정보를 확인합니다.

2. 노드 `<node-name>`의 이벤트를 타임스탬프 순으로 조회하여 노드에 영향을 미치는 최근 문제를 파악합니다.

3. 모든 노드와 상태를 조회하여 NotReady 또는 접근 불가로 표시된 노드를 파악하고 Ready 상태 전환을 확인합니다.

4. `kube-system`에서 Pod를 조회하고 CNI 플러그인 Pod(예: DaemonSet Pod)를 필터링하여 영향받는 노드에서 실행 중이고 과도하게 재시작하지 않는지 확인합니다.

5. 정상 노드의 Pod에서 접근 불가 노드 IP에 ping 또는 유사한 네트워크 테스트를 실행하여 노드 간 연결을 확인합니다.

6. `kube-system` 및 기타 관련 Namespace에서 NetworkPolicy 리소스를 조회하고 규칙을 검토하여 노드 간 노드 또는 Pod 트래픽을 차단할 수 있는 정책이 있는지 확인합니다.

## 진단

1. 플레이북에서 노드 이벤트를 분석하여 노드가 NotReady 또는 Unknown 상태로 전환된 시점을 파악합니다. 이벤트에서 특정 타임스탬프와 함께 NodeNotReady가 표시되면, 전환 시간과 관련 오류 메시지를 확인합니다.

2. 노드 이벤트에서 접근 불가가 표시되면, 플레이북에서 노드 상태의 Ready 조건 상태와 LastHeartbeatTime을 확인합니다. LastHeartbeatTime이 오래되었으면, kubelet이 API Server와 통신하지 않고 있습니다.

3. kubelet 통신이 실패하면, 플레이북에서 영향받는 노드의 CNI 플러그인 Pod 상태를 확인합니다. CNI Pod가 실행되지 않거나 장애를 보이면, 노드와 Control Plane 간 네트워크 연결이 끊어진 것입니다.

4. CNI Pod가 정상이면, 플레이북에서 네트워크 연결 테스트 결과(노드 간 ping 테스트)를 확인합니다. 노드 간 연결이 실패하면, 노드 통신에 영향을 미치는 네트워크 인프라 문제를 확인합니다.

5. 노드 연결이 작동하면, 플레이북에서 kubelet으로의 Control Plane 트래픽(포트 10250)을 차단할 수 있는 NetworkPolicy 리소스를 확인합니다. 정책이 kube-system 또는 노드 통신을 제한하면, API Server가 kubelet에 접근할 수 없습니다.

6. NetworkPolicy가 차단하지 않으면, 노드 네트워크 인터페이스와 라우트 설정을 검토합니다. API Server 또는 클러스터 네트워크로의 라우트가 누락되었거나 올바르지 않으면, kubelet이 상태를 보고할 수 없습니다.

**네트워크 설정 문제가 발견되지 않는 경우**: 클라우드 프로바이더 네트워킹(VPC, 서브넷, 보안 그룹)을 확인하고, 노드가 연결 문제가 있는 서로 다른 가용 영역에 있는지 확인하고, kubelet 로그에서 인증 또는 인증서 오류를 검토하고, 최근 인프라 유지보수가 노드 네트워킹에 영향을 미쳤는지 검사합니다.
