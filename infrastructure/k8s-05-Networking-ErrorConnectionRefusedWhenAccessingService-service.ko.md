---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/05-Networking/ErrorConnectionRefusedWhenAccessingService-service.md)'
role: Kubernetes SRE
origin: scoutflo
extract_date: 2026-03-05
tags:
- dns
- errorconnectionrefusedwhenaccessingservice
- infrastructure
- k8s-namespace
- k8s-pod
- k8s-service
- kubernetes
- networking
- performance
- service
---

---
title: Error Connection Refused When Accessing Service - Service
weight: 289
categories:
  - kubernetes
  - service
---

# ErrorConnectionRefusedWhenAccessingService-service - Service 접근 시 연결 거부 오류

## 의미

Kubernetes Service에 대한 연결이 거부되고 있으며(KubeServiceNotReady 알림 발생), Service에 Endpoint가 없거나, Service 포트가 수신 대기하지 않거나, Pod가 Ready 상태가 아니거나, kube-proxy가 트래픽을 올바르게 전달하지 않는 것이 원인입니다. Service 연결이 connection refused 오류를 반환하고, Endpoints 리소스에 Ready 주소가 없으며, Service 셀렉터와 일치하는 Pod가 NotReady 상태일 수 있습니다. 이는 네트워크 계층에 영향을 미치며 Service 연결을 방해하고, 일반적으로 Pod Readiness 실패, 포트 설정 문제 또는 kube-proxy 문제가 원인입니다. 애플리케이션이 Service에 연결할 수 없으며 오류가 발생할 수 있습니다.

## 영향

Service 연결 거부, 애플리케이션이 Service에 연결 불가, Service Endpoint가 존재하지만 연결을 수락하지 않음, KubeServiceNotReady 알림 발생, 로드 밸런싱 실패, 클러스터 내부 Service 통신 차단, Service DNS는 확인되지만 연결 실패, 애플리케이션이 백엔드 서비스에 접근 불가. Service 연결이 지속적으로 connection refused 오류를 반환하고, Endpoints 리소스에 Ready 주소가 없으며, 애플리케이션이 Service에 연결할 수 없어 오류 또는 성능 저하가 발생하고, 클러스터 내부 Service 통신이 차단됩니다.

## 플레이북

1. `<namespace>` Namespace에서 Service `<service-name>`을 상세 조회하여 설정, 포트, 셀렉터, 현재 상태를 검사합니다.

2. `<namespace>` Namespace에서 Service `<service-name>`의 이벤트를 타임스탬프 순으로 조회하여 최근 문제를 파악합니다.

3. `<namespace>` Namespace에서 Service `<service-name>`의 Endpoints를 조회하고 Pod가 Endpoint로 등록되어 있는지, Readiness 상태를 확인합니다.

4. `<namespace>` Namespace에서 Service 셀렉터와 일치하는 Pod를 조회하고 존재 여부, 실행 상태, 올바른 레이블, 연결 수락 준비 상태를 확인합니다.

5. 테스트 Pod에서 Service Endpoint에 curl 또는 telnet을 실행하여 연결을 테스트하고 연결이 거부되는지 확인합니다.

6. Service와 연결된 Pod `<pod-name>`을 확인하고 포트 체크를 실행하여 애플리케이션이 예상 포트에서 수신 대기하고 있는지 확인합니다.

7. `kube-system` Namespace에서 kube-proxy Pod 상태를 확인하여 Service 프록시가 올바르게 작동하는지 확인합니다.

## 진단

1. 플레이북에서 Service Endpoint를 분석하여 Service에 Ready Endpoint가 있는지 확인합니다. Endpoint 목록이 비어 있거나 Ready 주소가 없으면, 사용 가능한 백엔드 Pod가 없어 연결이 거부됩니다.

2. Endpoint가 비어 있으면, 플레이북에서 Service 셀렉터와 Pod 레이블을 비교합니다. 셀렉터가 Pod 레이블과 일치하지 않으면 Endpoint로 선택되는 Pod가 없어 모든 연결이 거부됩니다.

3. 셀렉터가 일치하면, 플레이북에서 Pod Ready 상태를 확인합니다. Pod가 Ready가 아니면(Readiness Probe 실패 또는 아직 시작 중) Endpoint에서 제외됩니다. Pod 이벤트에서 Readiness Probe 실패 세부 정보를 확인합니다.

4. Pod가 Ready이고 Endpoint에 있으면, 플레이북에서 애플리케이션이 예상 포트에서 수신 대기하는지 확인합니다. 컨테이너 프로세스가 targetPort에 바인딩되지 않으면 연결이 Pod에 도달하지만 OS에서 거부됩니다.

5. 애플리케이션이 수신 대기 중이면, 플레이북에서 Service 포트와 targetPort 설정을 확인합니다. 포트 불일치가 있으면(Service 포트가 targetPort 또는 컨테이너 포트와 다르면) 트래픽이 잘못된 포트로 전달됩니다.

6. 포트 설정이 올바르면, 플레이북에서 kube-proxy 상태를 확인합니다. kube-proxy가 실행되지 않거나 iptables/ipvs 규칙이 오래되었으면 Endpoint로의 트래픽 라우팅이 실패합니다.

7. kube-proxy가 정상이면, 플레이북에서 Ingress 정책에 대한 NetworkPolicy 규칙을 확인합니다. 정책이 Service 포트 또는 클라이언트 소스의 트래픽을 차단하면 네트워크 계층에서 연결이 거부됩니다.

**설정 문제가 발견되지 않는 경우**: Pod에 여러 컨테이너가 있어 트래픽이 잘못된 컨테이너 포트로 라우팅되는지 확인하고, Init Container가 메인 컨테이너 시작을 차단하는지 확인하고, Readiness 달성 전에 Liveness Probe가 Pod를 종료하는지 검토하고, 리소스 제한이 시작 후 애플리케이션 크래시를 유발하는지 검사합니다.
