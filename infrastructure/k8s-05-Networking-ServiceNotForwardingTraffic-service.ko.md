---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/05-Networking/ServiceNotForwardingTraffic-service.md)'
role: Kubernetes SRE
origin: scoutflo
extract_date: 2026-03-05
tags:
- dns
- infrastructure
- k8s-namespace
- k8s-pod
- k8s-service
- kubernetes
- networking
- performance
- service
- servicenotforwardingtraffic
---

---
title: Service Not Forwarding Traffic - Service
weight: 265
categories:
  - kubernetes
  - service
---

# ServiceNotForwardingTraffic-service - Service 트래픽 전달 불가

## 의미

Kubernetes Service가 백엔드 Pod로 트래픽을 전달하지 않고 있으며(KubeServiceNotReady 알림 발생), Service에 Endpoint가 없거나, 셀렉터가 어떤 Pod와도 일치하지 않거나, 포트 설정이 잘못되었거나, kube-proxy가 작동하지 않는 것이 원인입니다.

## 영향

Service가 Pod로 트래픽을 라우팅할 수 없음, Service Endpoint를 통해 애플리케이션 접근 불가, Service DNS 확인은 되지만 연결 실패, 로드 밸런싱 작동 불가, Pod에 트래픽 미도달, KubeServiceNotReady 알림 발생, Service Endpoint에 Ready 주소 없음, 클러스터 내부 Service 통신 실패. Service에서 무기한 Endpoint 없음 표시, Endpoints 리소스에 Ready 주소 없음, kube-proxy Pod에서 장애 표시 가능, 애플리케이션이 Service에 접근할 수 없어 오류 또는 성능 저하 발생 가능.

## 플레이북

1. `<namespace>` Namespace에서 Service `<service-name>`을 상세 조회하여 스펙, 셀렉터, 포트 설정을 검사합니다.

2. `<namespace>` Namespace에서 Service `<service-name>`의 이벤트를 타임스탬프 순으로 조회하여 Endpoint 업데이트 실패를 파악합니다.

3. `<namespace>` Namespace에서 Service `<service-name>`의 Endpoints를 조회하고 Pod가 Endpoint로 등록되어 있는지, Readiness 상태를 확인합니다.

4. `<namespace>` Namespace에서 Service 셀렉터와 일치하는 Pod를 조회하고 존재 여부, 실행 상태, Service 셀렉터와 일치하는 올바른 레이블, Ready 상태를 확인합니다.

5. 테스트 Pod에서 Service Endpoint에 curl 또는 wget을 실행하여 연결을 테스트하고 트래픽 전달이 작동하는지 확인합니다.

6. `kube-system` Namespace에서 kube-proxy Pod 상태를 확인하여 Service 프록시가 올바르게 작동하는지 확인합니다.

## 진단

1. 플레이북에서 Service Endpoint를 분석하여 Service에 Ready Endpoint가 있는지 확인합니다. Endpoint 목록이 비어 있거나 Ready 주소가 없으면, 문제는 Pod 선택(셀렉터 불일치 또는 일치하는 Pod 없음)입니다.

2. Endpoint가 비어 있으면, 플레이북 데이터에서 Service 셀렉터와 Pod 레이블을 비교합니다. Service 셀렉터 키 또는 값이 Namespace의 어떤 Pod 레이블과도 일치하지 않으면, Endpoint로 선택되는 Pod가 없습니다.

3. 셀렉터가 Pod와 일치하면, 플레이북에서 Pod Ready 조건을 확인합니다. Pod가 존재하지만 NotReady이면, Readiness Probe를 통과할 때까지 Service Endpoint에서 제외됩니다.

4. Pod가 Ready이고 Endpoint여야 하면, 플레이북에서 Service 포트 설정이 Pod 컨테이너 포트와 일치하는지 확인합니다. targetPort가 컨테이너 포트와 일치하지 않으면, 트래픽 전달이 실패합니다.

5. 포트 설정이 올바르면, 플레이북 데이터에서 kube-proxy 상태를 확인합니다. kube-proxy Pod가 실행되지 않거나 장애를 보이면, Service 라우팅을 위한 iptables/ipvs 규칙이 프로그래밍되지 않습니다.

6. kube-proxy가 정상이면, 플레이북에서 Service Pod로의 트래픽을 차단하는 Ingress 정책에 대한 NetworkPolicy 규칙을 확인합니다. 정책이 Service CIDR 또는 다른 Pod에서의 Ingress를 제한하면, 네트워크 수준에서 트래픽이 차단됩니다.

**설정 문제가 발견되지 않는 경우**: kube-controller-manager 로그를 확인하여 Endpoint Controller가 작동하는지 확인하고, EndpointSlice Controller가 활성화되어 작동하는지(Kubernetes 1.21+) 검토하고, Service Account 토큰 또는 RBAC 권한이 Endpoint 업데이트를 방해하는지 확인합니다.
