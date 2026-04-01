---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/05-Networking/ServiceNotAccessible-service.md)'
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
- servicenotaccessible
---

---
title: Service Not Accessible - Service
weight: 207
categories:
  - kubernetes
  - service
---

# ServiceNotAccessible-service - Service 접근 불가

## 의미

Kubernetes Service가 백엔드 Pod에 트래픽을 노출하거나 전달하지 않고 있으며(KubeServiceNotReady 또는 Service 관련 알림 발생), Service에 Endpoint가 없거나, 셀렉터 불일치로 Pod 연결이 안 되거나, 포트 설정이 잘못되었거나, NetworkPolicy가 트래픽을 차단하거나, Service 유형 설정이 잘못된 것이 원인입니다.

## 영향

KubeServiceNotReady 알림 발생, Service가 Pod로 트래픽을 라우팅할 수 없음, Service Endpoint를 통해 애플리케이션 접근 불가, Service DNS 확인 실패, 로드 밸런싱 작동 불가, Pod에 트래픽 미도달, Service Endpoint에 Ready 주소 없음, Service 상태에 Endpoint 없음 표시, 클러스터 내부 Service Discovery 실패. Service에서 무기한 Endpoint 없음 표시, Endpoints 리소스에 Ready 주소 없음, Service DNS 확인 실패, 애플리케이션이 Service에 접근할 수 없어 오류 또는 성능 저하 발생 가능.

## 플레이북

1. `<namespace>` Namespace에서 Service `<service-name>`을 상세 조회하여 스펙, 상태, 셀렉터를 검사합니다.

2. `<namespace>` Namespace에서 Service `<service-name>`의 이벤트를 타임스탬프 순으로 조회하여 최근 문제를 파악합니다.

3. `<namespace>` Namespace에서 Service `<service-name>`의 Endpoints를 조회하고 Pod가 Endpoint로 등록되어 있는지, Readiness 상태를 확인합니다.

4. `<namespace>` Namespace에서 Service `<service-name>`의 EndpointSlice 리소스(Kubernetes 1.21+)를 조회하고 Pod가 Endpoint로 등록되어 있는지, Readiness 상태를 확인합니다.

5. `<namespace>` Namespace에서 Service 셀렉터와 일치하는 Pod를 조회하고 존재 여부, 실행 상태, Service 셀렉터와 일치하는 올바른 레이블을 확인합니다.

6. `kube-system` Namespace에서 kube-proxy ConfigMap을 확인하여 kube-proxy 모드를 확인하고 iptables 또는 ipvs 모드가 구성되어 있는지 판단합니다.

7. 테스트 Pod에서 `<service-name>.<namespace>.svc.cluster.local` 또는 동등한 DNS 쿼리에 대해 nslookup을 실행하여 Service DNS 확인을 검증합니다.

8. 테스트 Pod에서 Service Endpoint에 curl 또는 wget을 실행하여 연결을 테스트하고 트래픽 전달을 확인합니다.

9. `<namespace>` Namespace에서 NetworkPolicy 객체를 조회하고 규칙을 검토하여 정책이 Service 트래픽을 차단하는지 확인합니다.

## 진단

1. 플레이북에서 Service 이벤트와 Endpoint를 분석하여 Service에 Ready Endpoint가 있는지 확인합니다. Endpoints 또는 EndpointSlice에 Ready 주소가 없으면, 주요 문제는 Pod 선택 또는 Readiness입니다.

2. Endpoint가 비어 있으면, 플레이북에서 Service 셀렉터와 Pod 레이블을 비교합니다. 셀렉터가 어떤 Pod와도 일치하지 않으면, Pod 레이블과 Service 셀렉터 설정에서 불일치(오타, 누락된 레이블 또는 잘못된 값)를 확인합니다.

3. 셀렉터가 Pod와 일치하면, 플레이북에서 Pod 상태와 Ready 조건을 확인합니다. Pod가 Ready가 아니면(Readiness Probe 실패) Endpoint에서 제외됩니다. Pod 이벤트에서 Probe 실패 사유를 확인합니다.

4. Pod가 Ready이면, 플레이북에서 Service Pod로의 Ingress를 차단하는 NetworkPolicy 규칙을 확인합니다. Service 트래픽을 허용하는 규칙 없이 제한적 Ingress 정책이 존재하면, 연결이 차단됩니다.

5. NetworkPolicy가 트래픽을 허용하면, 플레이북 연결 테스트에서 DNS 확인을 검증합니다. Service 이름에 대한 nslookup이 실패하면, CoreDNS가 Service 이름을 올바르게 확인하지 못하고 있습니다.

6. DNS가 작동하면, 플레이북에서 kube-proxy 상태와 모드를 확인합니다. kube-proxy가 실행되지 않거나 ConfigMap에 잘못된 iptables/ipvs 설정이 표시되면, Service 라우팅 규칙이 프로그래밍되지 않습니다.

7. kube-proxy가 정상이면, 플레이북에서 Service 포트와 targetPort 설정이 Pod 컨테이너 포트와 일치하는지 확인합니다. 포트가 일치하지 않으면, 트래픽이 잘못되거나 닫힌 포트로 전달됩니다.

**설정 문제가 발견되지 않는 경우**: Kubernetes 1.21+에서 EndpointSlice Controller 상태를 확인하고, Service 유형이 올바르게 구성되어 있는지(ClusterIP, NodePort, LoadBalancer) 확인하고, externalTrafficPolicy가 접근성에 영향을 미치는지 검토하고, Service 세션 어피니티 설정이 예상치 못한 동작을 유발하는지 검사합니다.
