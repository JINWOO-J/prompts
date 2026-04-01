---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/05-Networking/ServiceNodePortNotAccessible-service.md)'
role: Kubernetes SRE
origin: scoutflo
extract_date: 2026-03-05
tags:
- infrastructure
- k8s-namespace
- k8s-node
- k8s-pod
- k8s-service
- kubernetes
- networking
- security
- service
- servicenodeportnotaccessible
---

---
title: Service NodePort Not Accessible - Service
weight: 232
categories:
  - kubernetes
  - service
---

# ServiceNodePortNotAccessible-service - Service NodePort 접근 불가

## 의미

NodePort Service가 클러스터 외부에서 접근할 수 없으며(Service 관련 알림 발생), 방화벽 규칙이 NodePort를 차단하거나, 노드가 NodePort에서 접근 불가하거나, kube-proxy가 작동하지 않거나, Service 설정이 잘못된 것이 원인입니다.

## 영향

클러스터 외부에서 NodePort Service 접근 불가, 외부 트래픽이 애플리케이션에 도달 불가, NodePort 연결 거부, 방화벽이 NodePort 접근 차단, KubeServiceNotReady 알림 발생 가능, Service 상태에 NodePort 구성되었지만 접근 불가 표시, 애플리케이션 외부 접근 불가, NodePort를 통한 로드 밸런싱 실패. NodePort 연결이 무기한 거부, kube-proxy Pod에서 장애 표시 가능, 애플리케이션이 외부에서 접근 불가능하며 오류 발생 가능, 외부 트래픽이 애플리케이션에 도달 불가.

## 플레이북

1. `<namespace>` Namespace에서 Service `<service-name>`을 상세 조회하여 유형, NodePort 설정, 포트 매핑을 검사합니다.

2. `<namespace>` Namespace에서 Service `<service-name>`의 이벤트를 타임스탬프 순으로 조회하여 NodePort 설정 문제를 파악합니다.

3. 모든 노드를 조회하고 외부 IP 주소를 확인하여 NodePort 연결에 접근 가능한 노드를 파악합니다.

4. 외부 클라이언트 또는 테스트 Pod에서 `<node-ip>:<node-port>`에 curl 또는 telnet을 실행하여 NodePort 접근 가능 여부를 확인합니다.

5. 노드 또는 클라우드 프로바이더 보안 그룹의 방화벽 규칙을 확인하여 NodePort 포트가 열려 있고 접근 가능한지 확인합니다.

6. `kube-system` Namespace에서 kube-proxy Pod 상태를 확인하여 Service 프록시가 올바르게 작동하고 NodePort 트래픽을 전달하는지 확인합니다.

## 진단

1. 플레이북에서 Service 이벤트와 설정을 분석하여 NodePort가 올바르게 할당되었는지 확인합니다. Service 유형이 NodePort가 아니거나 nodePort 필드가 설정되지 않으면, NodePort를 통한 외부 접근이 구성되지 않은 것입니다.

2. NodePort가 구성되어 있으면, 플레이북에서 Service Endpoint를 확인합니다. Endpoint 목록이 비어 있으면, 트래픽을 수신할 백엔드 Pod가 없습니다(셀렉터 불일치 또는 Pod가 Ready가 아님).

3. Endpoint가 존재하면, 플레이북에서 kube-proxy 상태를 확인합니다. kube-proxy가 노드에서 실행되지 않거나 장애를 보이면, NodePort iptables/ipvs 규칙이 프로그래밍되지 않아 트래픽이 전달되지 않습니다.

4. kube-proxy가 정상이면, 플레이북에서 연결 테스트 결과(node-ip:node-port에 curl)를 확인합니다. 연결이 거부되면, NodePort가 허용 범위(기본 30000-32767) 내에 있고 기존 포트와 충돌하지 않는지 확인합니다.

5. NodePort가 유효하면, 방화벽 규칙과 보안 그룹 설정을 확인합니다. NodePort가 노드 방화벽(iptables 규칙), 클라우드 보안 그룹 또는 네트워크 ACL에 의해 차단되면, 외부 트래픽이 노드에 도달할 수 없습니다.

6. 방화벽이 트래픽을 허용하면, 플레이북에서 노드 외부 IP 주소를 확인하고 노드가 네트워크에서 접근 가능한지 확인합니다. 노드에 내부 IP만 있거나 적절한 포트 포워딩 없이 NAT 뒤에 있으면, NodePort에 외부에서 접근할 수 없습니다.

**설정 문제가 발견되지 않는 경우**: 트래픽 라우팅 동작에 대한 externalTrafficPolicy 설정(Local vs Cluster)을 확인하고, 노드가 배스천 또는 VPN 접근이 필요한 프라이빗 서브넷에 있는지 확인하고, 직접 NodePort 접근 대신 로드 밸런서 또는 Ingress Controller를 사용해야 하는지 검토합니다.
