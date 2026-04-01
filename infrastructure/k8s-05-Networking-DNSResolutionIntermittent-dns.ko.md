---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/05-Networking/DNSResolutionIntermittent-dns.md)'
role: Kubernetes SRE
origin: scoutflo
extract_date: 2026-03-05
tags:
- dns
- dnsresolutionintermittent
- infrastructure
- k8s-namespace
- k8s-pod
- k8s-service
- kubernetes
- networking
- performance
- sts
---

---
title: DNS Resolution Intermittent - DNS
weight: 259
categories:
  - kubernetes
  - dns
---

# DNSResolutionIntermittent-dns - DNS 확인 간헐적 실패

## 의미

DNS 확인이 간헐적으로 실패하고 있으며(KubeDNSRequestsErrors 알림 발생), CoreDNS Pod의 높은 부하, CoreDNS 설정 미최적화, DNS 쿼리 타임아웃 또는 NetworkPolicy의 간헐적 DNS 트래픽 차단이 원인입니다. DNS 쿼리가 때때로 작동하지만 다른 때에는 실패하며, CoreDNS Pod의 리소스 사용량이 높을 수 있고, DNS 쿼리 타임아웃이 간헐적으로 발생합니다. 이는 DNS 계층에 영향을 미치며 불안정한 Service Discovery를 유발하고, 일반적으로 CoreDNS 성능 문제 또는 NetworkPolicy 제한이 원인입니다. 애플리케이션에서 산발적인 DNS 오류가 발생합니다.

## 영향

DNS 확인이 간헐적으로 실패, Service Discovery 불안정, 애플리케이션에서 산발적 DNS 오류 발생, KubeDNSRequestsErrors 알림 간헐적 발생, Service 간 통신 무작위 실패, DNS 쿼리 타임아웃 발생, CoreDNS Pod 과부하 가능, 클러스터 DNS 성능 저하. DNS 쿼리가 간헐적으로 실패하고, CoreDNS Pod의 리소스 사용량이 높을 수 있으며, 애플리케이션에서 산발적 DNS 오류와 장애가 발생할 수 있고, Service 간 통신이 무작위로 실패합니다.

## 플레이북

1. `kube-system` Namespace에서 `kubectl describe pod -n kube-system -l k8s-app=kube-dns`를 사용하여 CoreDNS Pod를 상세 조회하고, Pod 세부 정보, 상태, 리소스 사용량, 재시작 횟수를 검사합니다.

2. `kube-system` Namespace에서 `kubectl get events -n kube-system --field-selector involvedObject.name=coredns --sort-by='.metadata.creationTimestamp'`를 사용하여 이벤트를 조회하고, 시간에 따른 CoreDNS 관련 이벤트와 패턴을 파악합니다.

3. `kube-system` Namespace에서 CoreDNS Pod의 로그를 조회하고 타임아웃 오류, 쿼리 실패 또는 성능 문제를 필터링합니다.

4. 테스트 Pod에서 Pod Exec 도구를 사용하여 `nslookup` 또는 `dig`로 반복적인 DNS 쿼리를 실행하고, DNS 확인 패턴을 테스트하여 간헐적 실패를 파악합니다.

5. `kube-system` Namespace에서 ConfigMap `coredns`를 조회하여 CoreDNS 설정을 확인하고, DNS 서버 설정, 캐시 설정, 업스트림 서버 설정을 검토합니다.

6. CoreDNS Pod 리소스 사용량 메트릭을 모니터링하여 CPU 또는 메모리 제약이 성능 문제를 유발하는지 확인합니다.

## 진단

플레이북 섹션에서 수집한 이벤트와 Pod 상태를 분석하는 것부터 시작합니다. CoreDNS Pod 상태, 리소스 사용량, 반복 DNS 쿼리 테스트 결과가 주요 진단 신호를 제공합니다.

**Pod 상세 조회에서 높은 재시작 횟수 또는 최근 재시작이 표시되는 경우:**
- CoreDNS Pod 불안정이 간헐적 실패를 유발하고 있습니다. 이전 컨테이너 상태에서 종료 사유를 확인합니다. OOMKilled인 경우 메모리 제한을 늘립니다. Error인 경우 로그에서 구체적인 실패 원인을 확인합니다.

**CoreDNS 로그에서 업스트림 DNS 서버에 대한 타임아웃 오류가 표시되는 경우:**
- 업스트림 DNS 연결이 불안정합니다. 디버그 Pod에서 업스트림 DNS 서버를 직접 테스트합니다. 간헐적 네트워크 문제 또는 업스트림 서버 과부하를 확인합니다. 이중화를 위해 여러 업스트림 서버 추가를 고려합니다.

**CoreDNS 로그에서 높은 쿼리 지연 또는 큐 오버플로 메시지가 표시되는 경우:**
- CoreDNS가 과부하 상태입니다. Pod 메트릭에서 CPU 사용량을 확인합니다. 제한에 근접한 경우 CPU 요청/제한을 늘리거나 CoreDNS 레플리카를 수평 확장합니다.

**DNS 테스트 쿼리가 특정 도메인에서만 실패하는 경우:**
- 일반적인 CoreDNS 문제가 아닌 도메인별 문제입니다. 해당 도메인이 클러스터 DNS에 존재하는지 확인하고, Service와 Endpoint가 존재하는지 확인하고, Service가 Ready 상태인지 확인합니다.

**DNS 쿼리가 CoreDNS Pod에서는 성공하지만 애플리케이션 Pod에서 실패하는 경우:**
- 애플리케이션 Pod와 CoreDNS 간의 네트워크 경로에 문제가 있습니다. DNS 트래픽(포트 53 UDP/TCP)을 간헐적으로 차단하는 NetworkPolicy가 있는지 확인합니다. kube-dns Service Endpoint가 채워져 있는지 확인합니다.

**이벤트가 결론적이지 않은 경우, 타임스탬프를 상관 분석합니다:**
1. 실패 타임스탬프와 상세 조회 출력의 Pod 재시작 시간을 매칭하여 간헐적 실패가 CoreDNS Pod 재시작과 일치하는지 확인합니다.
2. DNS 쿼리 부하를 증가시킨 클러스터 스케일링 이벤트와 실패가 상관관계가 있는지 확인합니다.
3. 예약된 작업이나 Cron 워크로드를 나타낼 수 있는 특정 시간대에 실패가 발생하는지 확인합니다.

**명확한 원인이 파악되지 않는 경우:** 가용성 향상을 위해 CoreDNS 레플리카를 늘리고, 최적화 기회를 위해 DNS 캐시 설정을 검토하고, 패턴 파악을 위해 장기간 DNS 쿼리 지연을 모니터링합니다.
