---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/05-Networking/ServicesIntermittentlyUnreachable-service.md)'
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
- service
- servicesintermittentlyunreachable
---

---
title: Services Intermittently Unreachable - Service
weight: 288
categories:
  - kubernetes
  - service
---

# ServicesIntermittentlyUnreachable-service - Service 간헐적 접근 불가

## 의미

Kubernetes Service가 간헐적으로 접근 불가 상태이며(KubeServiceNotReady 알림 발생), Endpoint가 변동하거나, Pod가 빈번하게 NotReady 상태가 되거나, kube-proxy에 문제가 있거나, NetworkPolicy가 간헐적으로 트래픽을 차단하는 것이 원인입니다.

## 영향

Service가 간헐적으로 사용 불가, 연결이 무작위로 실패, 애플리케이션에서 산발적 연결 문제 발생, Service Endpoint 변동, KubeServiceNotReady 알림 간헐적 발생, 로드 밸런싱 불일관, Service DNS 확인이 간헐적으로 작동, 클러스터 내부 Service 통신 불안정. Service Endpoint가 가용과 불가용 사이에서 변동, Pod에서 빈번한 Ready/NotReady 전환 표시, 애플리케이션에서 산발적 연결 문제와 오류 발생 가능, 클러스터 내부 Service 통신 불안정.

## 플레이북

1. `<namespace>` Namespace에서 Service `<service-name>`을 상세 조회하여 상태와 Endpoint 설정을 검사합니다.

2. `<namespace>` Namespace에서 Service `<service-name>`의 이벤트를 타임스탬프 순으로 조회하여 Service 문제의 패턴을 파악합니다.

3. `<namespace>` Namespace에서 Service `<service-name>`의 Endpoints를 시간에 따라 조회하여 Endpoint가 변동하거나 빈번하게 변경되는지 파악합니다.

4. Service와 연결된 Pod를 조회하고 Ready 상태 전환을 모니터링하여 Pod가 빈번하게 NotReady 상태가 되었다가 복구되는지 확인합니다.

5. `kube-system` Namespace에서 kube-proxy Pod 상태와 로그를 확인하여 프록시 문제가 간헐적 실패를 유발하는지 확인합니다.

6. 테스트 Pod에서 Service Endpoint에 반복적인 curl 또는 연결 테스트를 실행하여 간헐적 연결 패턴을 확인합니다.

## 진단

1. 플레이북에서 Service 이벤트와 Endpoint 변경을 분석하여 Endpoint 가용성의 패턴을 파악합니다. Endpoint에서 빈번한 추가와 제거가 표시되면, 백엔드 Pod가 불안정하여 Ready와 NotReady 상태 사이를 전환하고 있습니다.

2. Endpoint가 변동하면, 플레이북 데이터에서 Pod Ready 상태 전환을 확인합니다. Pod가 빈번하게 Ready와 NotReady 사이를 전환하면, Pod 헬스 체크 실패(Liveness/Readiness Probe 문제)를 조사합니다.

3. Pod가 안정적이면, 플레이북에서 Service 셀렉터와 Pod 레이블을 비교합니다. 레이블 변경 또는 Deployment 업데이트로 인해 셀렉터가 Pod와 일관되게 일치하지 않으면, Endpoint가 간헐적으로 가용해집니다.

4. 셀렉터 매칭이 올바르면, 플레이북에서 kube-proxy Pod 상태와 로그를 확인합니다. kube-proxy에서 간헐적 장애 또는 재시작이 표시되면, iptables/ipvs 규칙이 일관되게 프로그래밍되지 않습니다.

5. kube-proxy가 안정적이면, 플레이북에서 Service 트래픽에 영향을 미치는 NetworkPolicy 규칙을 확인합니다. 정책이 동적 셀렉터 또는 Namespace 조건에 따라 간헐적으로 트래픽을 차단하면, 연결이 불안정해집니다.

6. NetworkPolicy가 트래픽에 영향을 미치지 않으면, 플레이북 연결 테스트에서 Service 이름에 대한 DNS 확인을 검증합니다. DNS 확인이 느리거나 간헐적으로 실패하면, Service Discovery가 불안정해집니다.

**설정 문제가 발견되지 않는 경우**: OOMKilled 또는 CPU 스로틀링 이벤트에 대한 Pod 리소스 사용률을 검토하고, 간헐적 네트워크 문제에 대한 노드 상태를 확인하고, 로드 밸런서 헬스 체크가 너무 공격적이어서 Endpoint 플래핑을 유발하는지 확인하고, 애플리케이션 시작 시간이 Readiness Probe 초기 지연을 초과하는지 검사합니다.
