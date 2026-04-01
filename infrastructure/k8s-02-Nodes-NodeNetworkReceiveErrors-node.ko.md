---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/02-Nodes/NodeNetworkReceiveErrors-node.md)'
role: SRE / K8s Incident Response
origin: scoutflo
tags:
- database
- dns
- infrastructure
- k8s-ingress
- k8s-node
- k8s-pod
- k8s-service
- kubernetes
- networking
- node
- nodenetworkreceiveerrors
- nodes
---

---
title: Node Network Receive Errors — Node 네트워크 수신 오류
weight: 34
categories: [kubernetes, node]
---

# NodeNetworkReceiveErrors

## 의미

Node에서 네트워크 수신 오류가 발생하고 있습니다(NodeNetworkReceiveErrors, NodeNetworkReceiveErrs 알림 발생). 네트워크 패킷이 수신 경로에서 드롭되거나, 손상되거나, 처리에 실패하고 있습니다.
 Node 메트릭에서 네트워크 인터페이스의 rx_errors, 드롭된 패킷 또는 프레임 오류가 증가하고 있으며, 네트워크 통신이 저하됩니다. 이는 Node의 모든 워크로드와 네트워크 연결에 영향을 미칩니다. 서비스 간 통신이 간헐적으로 실패하고, 외부 연결이 끊기며, 패킷 손실로 인해 재전송 및 지연이 발생합니다.

## 영향

NodeNetworkReceiveErrors 알림이 발생하고, 네트워크 연결이 불안정해집니다. TCP 재전송이 증가하며, 애플리케이션 타임아웃이 발생합니다. 서비스 디스커버리가 실패할 수 있고, 헬스 체크가 간헐적으로 실패합니다. 동서 트래픽이 영향받으며, 인그레스 트래픽이 드롭됩니다. Pod 네트워킹이 불안정해지고, DNS 조회가 실패할 수 있습니다. 데이터베이스 연결이 타임아웃되며, API 호출이 무작위로 실패합니다.

## 플레이북

1. Node `<node-name>`을 조회하고 rx_errors, rx_dropped, rx_frame_errors를 포함한 네트워크 인터페이스 통계를 확인합니다.

2. 어떤 네트워크 인터페이스에서 오류가 발생하는지 파악합니다 (eth0, ens5, 컨테이너 인터페이스).

3. 인터페이스 오류 카운터 및 링크 상태를 검사하여 하드웨어 수준 문제를 확인합니다.

4. MTU 설정이 클러스터 전체에서 일치하는지 포함하여 Node 네트워크 구성을 확인합니다.

5. 링 버퍼 설정 및 netdev_budget를 검사하여 네트워크 버퍼 고갈을 확인합니다.

6. 네트워크 플러그인(CNI)이 올바르게 작동하고 패킷을 드롭하지 않는지 확인합니다.

7. 인프라 수준에서 스로틀링이나 패킷 드롭에 대한 클라우드 제공자 네트워크 메트릭을 확인합니다.

## 진단

오류 유형을 분석하고 잠재적 원인과 대조합니다: 프레임 오류는 물리적/드라이버 문제를, 드롭된 패킷은 버퍼 고갈을, CRC 오류는 케이블/하드웨어 문제를 시사합니다. 상세 네트워크 통계를 근거로 사용합니다.

Node와 Pod 간의 MTU 설정을 비교하고, 패킷 단편화 또는 과대 프레임이 오류를 유발하는지 확인합니다. 인터페이스 MTU 구성 및 패킷 크기 분포를 근거로 사용합니다.

네트워크 오류를 트래픽 볼륨과 대조하고, 용량 문제를 시사하는 높은 트래픽 기간에 오류가 발생하는지 확인합니다. 트래픽 메트릭 및 오류 타임스탬프를 근거로 사용합니다.

VPC 또는 클라우드 네트워크 스로틀링을 확인하고, Node 인스턴스 유형이 충분한 네트워크 대역폭을 가지고 있는지 검증합니다. 클라우드 제공자 네트워크 메트릭을 근거로 사용합니다.

네트워크 드라이버 및 펌웨어 버전을 확인하고, NIC 또는 가상화 네트워크에 영향을 미치는 알려진 버그를 확인합니다. 드라이버 버전 및 벤더 권고를 근거로 사용합니다.

**지정된 시간 범위 내에서 상관관계를 찾을 수 없는 경우**: 네트워크 링 버퍼 크기를 늘리고, NIC 드라이버를 업데이트하며, 케이블 또는 하드웨어 문제를 확인하고, MTU 일관성을 검증하며, 클라우드 네트워크 인스턴스 제한을 검토하고, 네트워크 최적화 인스턴스 유형을 고려합니다.
