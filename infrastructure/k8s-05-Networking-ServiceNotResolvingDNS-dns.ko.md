---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/05-Networking/ServiceNotResolvingDNS-dns.md)'
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
- servicenotresolvingdns
- sts
---

---
title: Service Not Resolving DNS - DNS
weight: 216
categories:
  - kubernetes
  - dns
---

# ServiceNotResolvingDNS-dns - Service DNS 확인 실패

## 의미

Kubernetes Service DNS 확인이 실패하고 있으며(KubeDNSDown 또는 KubeDNSRequestsErrors 알림 발생), CoreDNS Pod가 실행되지 않거나, kube-dns Service가 사용 불가능하거나, DNS 설정이 잘못되었거나, NetworkPolicy가 DNS 트래픽을 차단하고 있는 것이 원인입니다.

## 영향

Service DNS 이름 확인 불가, 클러스터 내부 Service Discovery 실패, 애플리케이션이 이름으로 Service에 연결 불가, DNS 쿼리에서 오류 반환, CoreDNS Pod 미실행, KubeDNSDown 알림 발생, KubeDNSRequestsErrors 알림 발생, Service 간 통신 실패, 애플리케이션이 Service Endpoint를 확인할 수 없음. CoreDNS Pod가 무기한 CrashLoopBackOff 또는 Failed 상태, DNS 쿼리에서 오류 반환, 애플리케이션이 이름으로 Service에 연결할 수 없어 오류 발생 가능, Service 간 통신 실패.

## 플레이북

1. `kube-system` Namespace에서 `kubectl describe pod -n kube-system -l k8s-app=kube-dns`를 사용하여 CoreDNS Pod를 상세 조회하고, Pod 세부 정보, 상태, 최근 이벤트를 검사합니다.

2. `kube-system` Namespace에서 `kubectl get events -n kube-system --field-selector involvedObject.name=coredns --sort-by='.metadata.creationTimestamp'`를 사용하여 이벤트를 조회하고, 최근 CoreDNS 관련 이벤트와 문제를 파악합니다.

3. `kube-system` Namespace에서 kube-dns Service를 조회하고 존재 여부와 Endpoint 유무를 확인하여 DNS 서비스에 접근 가능한지 확인합니다.

4. `kube-system` Namespace에서 CoreDNS Pod 로그를 조회하고 DNS가 작동하지 않는 이유를 파악하기 위해 오류를 검사합니다.

5. CoreDNS Pod에서 Pod Exec 도구를 사용하여 `coredns -plugins`를 실행하여 CoreDNS 플러그인 상태를 확인하고 플러그인이 올바르게 작동하는지 확인합니다.

6. CoreDNS 로그에서 업스트림 DNS 연결 실패 또는 타임아웃을 검토하여 업스트림 DNS 서버 가용성을 확인합니다.

7. 테스트 Pod에서 Pod Exec 도구를 사용하여 `nslookup <service-name>.<namespace>.svc.cluster.local` 또는 동등한 DNS 쿼리를 실행하여 DNS 확인을 테스트하고 쿼리가 작동하는지 확인합니다.

8. `kube-system` Namespace에서 ConfigMap `coredns`를 조회하여 CoreDNS 설정을 확인하고 DNS 서버 설정과 업스트림 서버 설정을 검토합니다.

9. `kube-system` Namespace에서 NetworkPolicy 객체를 조회하고 정책이 CoreDNS Pod로의 또는 CoreDNS Pod에서의 DNS 트래픽을 차단하는지 확인합니다.

## 진단

플레이북 섹션에서 수집한 이벤트와 CoreDNS 상태를 분석하는 것부터 시작합니다. CoreDNS Pod 상태, kube-dns Service Endpoint, DNS 쿼리 테스트 결과가 주요 진단 신호를 제공합니다.

**CoreDNS Pod가 CrashLoopBackOff를 보이거나 Ready가 아닌 경우:**
- DNS 서비스가 중단되었습니다. 상세 조회 출력에서 Pod 종료 사유를 확인합니다. OOMKilled인 경우 메모리 제한을 늘립니다. 로그에 설정 오류가 나타나면 ConfigMap `coredns`의 Corefile을 검토합니다.

**kube-dns Service가 존재하지만 Endpoint가 없는 경우:**
- CoreDNS Pod가 Service에 등록되지 않았습니다. Pod에 `k8s-app=kube-dns` 레이블이 있고 Ready 상태인지 확인합니다. Service 셀렉터가 Pod 레이블과 일치하는지 확인합니다.

**CoreDNS 로그에서 클러스터 도메인에 대해 SERVFAIL 또는 NXDOMAIN이 표시되는 경우:**
- CoreDNS가 요청된 Service를 확인할 수 없습니다. 지정된 Namespace에 Service가 존재하는지 확인합니다. Service에 유효한 ClusterIP가 있고 Endpoint 없는 Headless가 아닌지 확인합니다.

**CoreDNS 로그에서 업스트림 연결 실패가 표시되는 경우:**
- 외부 DNS 확인이 실패하며, 플러그인이 체인되어 있으면 클러스터 DNS에 영향을 줄 수 있습니다. Corefile의 업스트림 DNS 서버에 접근 가능한지 확인합니다. 이는 일반적으로 클러스터 내부 서비스가 아닌 외부 도메인 확인에 영향을 미칩니다.

**DNS 쿼리가 CoreDNS Pod에서는 작동하지만 다른 Pod에서 실패하는 경우:**
- CoreDNS로의 네트워크 경로가 차단되었습니다. kube-system에서 Ingress를 제한할 수 있는 NetworkPolicy를 확인합니다. 실패하는 Pod가 실행되는 노드에서 CNI 플러그인이 작동하는지 확인합니다.

**Service가 존재하지만 nslookup이 잘못된 IP를 반환하거나 결과가 없는 경우:**
- DNS 캐시에 오래된 항목이 포함되어 있거나 Service가 최근 수정되었을 수 있습니다. Service ClusterIP가 최근 변경되었는지 확인합니다. CoreDNS 캐시 업데이트에 시간이 걸릴 수 있습니다.

**이벤트가 결론적이지 않은 경우, 타임스탬프를 상관 분석합니다:**
1. 실패 시간과 Pod 재시작 타임스탬프를 매칭하여 CoreDNS Pod 재시작 후 확인 실패가 시작되었는지 확인합니다.
2. ConfigMap 리소스 버전을 검사하여 CoreDNS ConfigMap이 최근 수정되었는지 확인합니다.
3. 클러스터 이벤트를 검토하여 CoreDNS에 영향을 줄 수 있는 클러스터 업그레이드가 발생했는지 확인합니다.

**명확한 원인이 파악되지 않는 경우:** 여러 Service에 대해 DNS 확인을 테스트하여 문제가 특정 Service에 한정되는지 클러스터 전체인지 판단합니다. 메트릭이 가용한 경우 CoreDNS 메트릭에서 쿼리 성공/실패율을 확인합니다.
