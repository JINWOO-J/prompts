---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/05-Networking/CoreDNSLatencyHigh-dns.md)'
role: Kubernetes SRE
origin: scoutflo
extract_date: 2026-03-05
tags:
- corednslatencyhigh
- database
- dns
- infrastructure
- k8s-configmap
- k8s-namespace
- k8s-pod
- k8s-service
- kubernetes
- networking
- performance
- sts
---

---
title: CoreDNS Latency High
weight: 11
categories: [kubernetes, dns]
---

# CoreDNSLatencyHigh - CoreDNS 지연 시간 높음

## 의미

CoreDNS에서 높은 쿼리 지연 시간이 발생하고 있으며(CoreDNSLatencyHigh 알림 발생), 업스트림 리졸버 지연, 높은 쿼리 볼륨, 리소스 제약 또는 네트워크 문제로 인해 DNS 요청 확인이 예상보다 오래 걸리고 있습니다. CoreDNS 메트릭에서 DNS 요청 소요 시간이 정상 임계값(보통 1초 초과)을 넘어서고, 애플리케이션 응답 시간이 증가하며, Service 간 통신이 느려집니다. 이는 클러스터 네트워킹 계층에 영향을 미치며, DNS 확인에 의존하는 모든 애플리케이션에 영향을 주는 DNS 성능 저하를 나타냅니다. 데이터베이스 연결 수립이 오래 걸리고, API 호출 지연이 증가하며, 전반적인 애플리케이션 성능이 저하됩니다.

## 영향

CoreDNSLatencyHigh 알림 발생, 애플리케이션 응답 시간 증가, Service 간 통신 지연, 데이터베이스 연결 수립 시간 증가, 외부 서비스 API 호출 타임아웃, DNS 지연으로 인한 헬스 체크 실패 가능, Pod 시작 시간 증가, 사용자 대면 지연 시간 증가, SLO 위반 가능, 애플리케이션 로그에 타임아웃 오류 증가, DNS 대기 중 커넥션 풀 고갈 가능, 애플리케이션 처리량 감소.

## 플레이북

1. `kube-system` Namespace에서 CoreDNS Pod를 조회하고 CPU 및 메모리 사용률을 확인하여 DNS Pod가 리소스 제약 상태인지 점검합니다.

2. CoreDNS 메트릭(coredns_dns_request_duration_seconds)을 조회하고 어떤 DNS 쿼리 유형(A, AAAA, SRV)과 존에서 높은 지연이 발생하는지 파악합니다.

3. `kube-system` Namespace에서 CoreDNS Pod의 로그를 조회하고 'duration', 'timeout', 'SERVFAIL' 등의 느린 쿼리 패턴을 필터링하여 지연을 유발하는 특정 도메인이나 쿼리 패턴을 파악합니다.

4. `kube-system` Namespace에서 CoreDNS ConfigMap을 조회하고 업스트림 DNS 서버 및 헬스 체크 설정을 포함한 forward 플러그인 설정을 확인합니다.

5. 실행 중인 Pod에서 시간 기반 DNS 쿼리를 사용하여 kube-dns Service에 대한 DNS 확인 지연을 테스트하고, 내부 도메인과 외부 도메인의 실제 확인 시간을 측정합니다.

6. CoreDNS Pod가 호스팅된 노드의 네트워크 메트릭을 조회하고 DNS 성능에 영향을 줄 수 있는 네트워크 지연, 패킷 손실, 인터페이스 오류를 확인합니다.

7. CoreDNS Horizontal Pod Autoscaler(구성된 경우)를 확인하고 쿼리 부하를 처리하기 위해 추가 레플리카가 필요한지 확인합니다.

## 진단

CoreDNS CPU 사용률과 쿼리 지연 메트릭을 비교하고, Pod 리소스 메트릭과 DNS 요청 속도를 근거로 지연 증가가 CPU 포화(80% 초과)와 상관관계가 있는지 확인합니다.

업스트림 DNS 서버 응답 시간과 CoreDNS 지연 스파이크를 상관 분석하고, forward 플러그인 메트릭과 업스트림 서버 상태를 근거로 외부 DNS 확인이 지연을 유발하는지 확인합니다.

DNS 쿼리 패턴을 분석하여 특정 도메인이나 쿼리 유형(IPv6용 AAAA 쿼리, 외부 도메인)이 불균형적인 지연을 유발하는지 파악하고, DNS 쿼리 로그와 응답 유형 분석을 근거로 확인합니다.

CoreDNS Pod 수와 DNS 쿼리 속도를 비교하고, HPA 메트릭과 Pod Ready 수를 근거로 레플리카 부족이 쿼리 큐잉과 지연을 유발하는지 확인합니다.

Pod의 NDOTS 설정 문제(기본 ndots:5는 과도한 검색 도메인 쿼리를 유발)가 DNS 쿼리를 증가시키고 전체 지연을 높이는지 확인하고, Pod DNS 설정과 쿼리 패턴을 근거로 확인합니다.

지정된 시간 범위 내에서 상관관계가 발견되지 않으면: 업스트림 DNS 서버에 대한 네트워크 연결을 확인하고, DNS 트래픽을 차단하거나 속도 제한하는 방화벽 규칙을 확인하고, CoreDNS 캐시 적중률을 검사하고, DNS 증폭 또는 루프 상태가 없는지 확인하고, 반복적인 실패 조회를 유발하는 네거티브 캐시 TTL 문제를 확인합니다.
