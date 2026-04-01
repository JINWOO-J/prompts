---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/02-Nodes/NodeCannotJoinCluster-node.md)'
role: SRE / K8s Incident Response
origin: scoutflo
tags:
- capacity
- infrastructure
- k8s-node
- kubernetes
- node
- nodecannotjoincluster
- nodes
- scaling
- sts
---

---
title: Node Cannot Join Cluster — Node 클러스터 조인 실패
weight: 262
categories:
  - kubernetes
  - node
---

# NodeCannotJoinCluster-node

## 의미

Node가 Kubernetes 클러스터에 조인할 수 없습니다(Node 관련 알림 발생). 조인 토큰이 만료되었거나 유효하지 않거나, Control Plane으로의 네트워크 연결이 차단되었거나, 필요한 포트가 열려 있지 않거나, Kubelet 구성이 잘못되었습니다.
 새 Node가 미조인 상태로 표시되고, Kubelet 로그에 조인 오류나 인증 실패가 나타나며, API 서버 엔드포인트로의 네트워크 연결 테스트가 실패할 수 있습니다. 이는 데이터 플레인에 영향을 미치며, 클러스터 스케일링 및 용량 확장을 방해합니다. 불충분한 Node 용량으로 인해 애플리케이션이 스케일링할 수 없을 수 있습니다.

## 영향

Node가 클러스터에 조인할 수 없고, 클러스터 스케일링이 실패합니다. 새 Node가 미조인 상태로 남으며, 클러스터 용량을 늘릴 수 없습니다. KubeNodeNotReady 알림이 발생하고, Node 등록이 실패합니다. Kubelet이 인증할 수 없으며, 클러스터 확장이 차단됩니다. Node 추가를 위해 수동 개입이 필요합니다. 새 Node가 무기한 미조인 상태로 표시되고, Kubelet 로그에 조인 오류나 인증 실패가 나타나며, 클러스터 용량을 늘릴 수 없습니다. 불충분한 Node 용량으로 인해 애플리케이션이 스케일링할 수 없을 수 있습니다.

## 플레이북

1. Node <node-name>을 describe하여(Node가 클러스터에 나타나는 경우) 다음을 확인합니다:
   - Conditions 섹션에서 등록 상태 확인
   - Events 섹션에서 조인 또는 등록 실패 확인
   - System Info 및 Kubelet 버전 세부 정보 확인

2. Node 이벤트를 타임스탬프 순으로 조회하여 Node 등록 이벤트 및 조인 실패의 순서를 확인합니다.

3. 조인 토큰을 조회하고 토큰 만료 시간 및 클러스터 조인에 토큰이 여전히 유효한지 확인합니다.

4. 새 Node와 Control Plane Node 간의 네트워크 연결을 확인하고, API 서버 엔드포인트 및 필요한 포트로의 연결을 테스트합니다.

5. 새 Node에서 Kubelet 구성을 확인하고, Kubelet이 올바른 클러스터 엔드포인트 및 인증 자격 증명으로 구성되어 있는지 검증합니다.

6. Pod Exec 도구 또는 SSH(Node 접근 가능 시)를 사용하여 새 Node의 Kubelet 로그를 확인하고, 조인 오류, 인증 실패 또는 연결 문제를 필터링합니다.

7. Kubelet 인증을 위해 새 Node에서 인증 기관(CA) 인증서의 가용성 및 유효성을 확인합니다.

## 진단

1. 플레이북 1-2단계의 Node 이벤트를 분석하여(Node가 클러스터에 나타나는 경우) 등록 실패를 파악합니다. "RegisteredNode" 실패, 인증 오류 또는 TLS 핸드셰이크 실패를 보여주는 이벤트가 구체적인 조인 문제를 나타냅니다. 이벤트 타임스탬프와 오류 메시지를 기록합니다.

2. Node 이벤트 또는 Kubelet 로그에서 토큰 관련 오류("token expired", "invalid token")가 나타나는 경우, 플레이북 3단계에서 조인 토큰 유효성을 확인합니다. Bootstrap 토큰에는 만료 시간이 있으며 조인 시도 전에 만료되었을 수 있습니다.

3. 플레이북 6단계의 Kubelet 로그에서 네트워크 연결 오류("connection refused", "no route to host", "timeout")가 나타나는 경우, 플레이북 4단계에서 네트워크 연결을 확인합니다. Node는 포트 6443의 API 서버 및 기타 필요한 Control Plane 포트에 도달할 수 있어야 합니다.

4. 네트워크 연결 테스트가 실패하는 경우, 방화벽 규칙 및 네트워크 정책을 확인합니다. 필요한 포트(API 서버용 6443, Kubelet용 10250, 해당되는 경우 etcd용 2379-2380)가 새 Node와 Control Plane 사이에 열려 있어야 합니다.

5. Kubelet 로그에서 인증 또는 인증서 오류가 나타나는 경우, 플레이북 7단계에서 CA 인증서 가용성을 확인합니다. 새 Node는 TLS 연결을 설정하기 위해 클러스터 CA 인증서를 신뢰해야 합니다.

6. 플레이북 5단계의 Kubelet 구성에서 잘못된 API 서버 엔드포인트 또는 클러스터 설정이 나타나는 경우, 구성을 수정합니다. 잘못 구성된 클러스터 엔드포인트는 Kubelet이 Control Plane을 찾는 것을 방해합니다.

7. Kubelet 로그에서 API 서버 접근 불가 오류가 나타나는 경우, API 서버 가용성 및 상태를 확인합니다. Control Plane 문제는 올바른 구성에도 불구하고 새 Node의 조인을 방해합니다.

**이벤트에서 근본 원인을 파악할 수 없는 경우**: 조인 명령 구문 및 매개변수가 올바른지 확인하고, 클러스터가 Node 등록을 거부할 수 있는 커스텀 Admission Controller를 사용하는지 확인하며, Control Plane 로그에서 Node 등록 오류를 검토하고, Node가 클러스터 요구 사항(Kubernetes 버전 호환성, 필수 레이블 등)을 충족하는지 검증합니다.
