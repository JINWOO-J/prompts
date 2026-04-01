---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/05-Networking/CoreDNSPodsCrashLooping-dns.md)'
role: Kubernetes SRE
origin: scoutflo
extract_date: 2026-03-05
tags:
- compute
- corednspodscrashlooping
- dns
- infrastructure
- k8s-configmap
- k8s-deployment
- k8s-namespace
- k8s-pod
- k8s-service
- kubernetes
- networking
- sts
---

---
title: CoreDNS Pods CrashLooping - DNS
weight: 276
categories:
  - kubernetes
  - dns
---

# CoreDNSPodsCrashLooping-dns - CoreDNS Pod 반복 크래시

## 의미

CoreDNS Pod가 반복적으로 크래시하거나 재시작하고 있으며(KubePodCrashLooping 또는 KubeDNSDown 알림 발생), 잘못된 DNS 설정, 업스트림 의존성 누락, 컴퓨팅 리소스 부족 또는 Corefile 구문 오류로 인해 클러스터 내 Service 이름 확인 및 DNS 쿼리 처리가 중단되었습니다.

## 영향

클러스터 전체 DNS 확인 실패, Service Discovery 중단, Pod가 Service 이름을 확인할 수 없음, 애플리케이션이 Service에 연결 실패, 클러스터 네트워킹 불안정, KubeDNSRequestsErrors 알림 발생, CoreDNS Pod가 CrashLoopBackOff 상태, DNS 쿼리 실패 발생, Service Endpoint 확인 불가.

## 플레이북

1. `kube-system` Namespace에서 `kubectl describe pod -n kube-system -l k8s-app=kube-dns`를 사용하여 CoreDNS Pod를 상세 조회하고, Pod 세부 정보, 상태, 재시작 횟수, 최근 이벤트를 검사합니다.

2. `kube-system` Namespace에서 `kubectl get events -n kube-system --field-selector involvedObject.name=coredns --sort-by='.metadata.creationTimestamp'`를 사용하여 이벤트를 조회하고, 최근 CoreDNS 관련 이벤트와 문제를 파악합니다.

3. `kube-system`에서 CoreDNS Pod의 로그를 조회하고 설정 오류, 업스트림 DNS 조회 실패 또는 리소스 고갈을 나타내는 메시지를 확인합니다.

4. `kube-system`에서 CoreDNS ConfigMap을 조회하고 Corefile의 구문 정확성, 플러그인 설정, 업스트림 DNS 서버 정의를 검토합니다.

5. `kube-system`에서 CoreDNS Deployment를 조회하고 리소스 요청 및 제한을 검사하여 Pod에 충분한 CPU와 메모리가 할당되어 있는지 확인합니다.

6. 테스트 Pod에서 내부 및 외부 도메인에 대해 `nslookup` 또는 `dig`를 실행하여 클러스터 내 DNS 확인 동작을 검증합니다.

7. 테스트 Pod에서 구성된 업스트림 DNS 서버에 직접 `nslookup` 또는 `dig` 쿼리를 실행하여 접근 가능하고 올바르게 응답하는지 확인합니다.

## 진단

플레이북 섹션에서 수집한 이벤트를 분석하는 것부터 시작합니다. Pod 상세 조회 출력과 Namespace 이벤트가 주요 진단 신호를 제공합니다.

**이벤트에서 OOMKilled 또는 메모리 관련 종료 사유가 표시되는 경우:**
- CoreDNS Pod가 메모리 고갈로 종료되고 있습니다. Deployment의 리소스 제한을 확인하고 로그의 실제 메모리 사용량과 비교합니다. 메모리 제한을 늘리거나 Corefile의 캐시 크기를 줄입니다.

**이벤트에서 CrashLoopBackOff와 함께 로그에 Corefile 파싱 오류가 표시되는 경우:**
- CoreDNS 설정에 구문 오류가 포함되어 있습니다. ConfigMap `coredns`에서 잘못된 플러그인 설정, 누락된 중괄호 또는 잘못된 업스트림 서버 정의를 검토합니다. 적용 전에 Corefile 구문을 검증합니다.

**이벤트에서 업스트림 DNS에 대한 connection refused 또는 timeout 오류가 표시되는 경우:**
- CoreDNS가 업스트림 DNS 서버에 접근할 수 없습니다. Corefile의 업스트림 서버 IP가 올바르고 접근 가능한지 확인합니다. `kube-system`의 NetworkPolicy가 업스트림 DNS 포트로의 Egress를 차단하고 있는지 확인합니다.

**이벤트에서 플러그인 초기화 실패가 표시되는 경우:**
- CoreDNS 플러그인이 시작에 실패했습니다. 로그에서 특정 플러그인 이름과 오류를 확인합니다. 일반적인 원인으로는 누락된 의존성, 잘못된 플러그인 설정 또는 업그레이드 후 호환되지 않는 플러그인 버전이 있습니다.

**이벤트에서 크래시 사유 없이 Readiness Probe 실패가 표시되는 경우:**
- CoreDNS가 시작되지만 헬스 체크에 실패하고 있습니다. Deployment의 Probe 설정과 CoreDNS 시작 시간을 비교합니다. 리소스 제약이 느린 시작을 유발하는지 확인합니다.

**이벤트가 결론적이지 않은 경우, 타임스탬프를 상관 분석합니다:**
1. 크래시 타임스탬프와 ConfigMap `metadata.resourceVersion` 변경을 비교하여 CoreDNS 크래시가 ConfigMap 수정 직후에 시작되었는지 확인합니다.
2. Deployment 리비전 이력과 롤아웃 타임스탬프를 검사하여 크래시가 Deployment 롤아웃과 상관관계가 있는지 확인합니다.
3. CoreDNS 로그의 쿼리 속도 패턴을 검토하여 크래시가 클러스터 전체 DNS 쿼리 급증과 일치하는지 확인합니다.

**명확한 원인이 파악되지 않는 경우:** 첫 번째 크래시 이전의 경고에 대해 CoreDNS 로그를 검토하고, 메모리 누수를 나타내는 점진적 메모리 증가 패턴을 확인하고, 크래시 기간 동안 업스트림 DNS 서버 상태를 확인합니다.
