---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/03-Pods/PodCannotAccessClusterInternalDNS-dns.md)'
role: SRE / K8s Incident Response
origin: scoutflo
tags:
- dns
- infrastructure
- k8s-namespace
- k8s-pod
- k8s-service
- kubernetes
- podcannotaccessclusterinternaldns
- pods
- sts
---

---
title: Pod Cannot Access Cluster Internal DNS - DNS
weight: 284
categories:
  - kubernetes
  - dns
---

# PodCannotAccessClusterInternalDNS-dns — 클러스터 내부 DNS 접근 불가

## 의미

Pod가 클러스터 내부 DNS에 접근할 수 없습니다(KubeDNSDown 또는 KubeDNSRequestsErrors 알림 발생). CoreDNS Pod가 실행되지 않거나, kube-dns 서비스가 불가용하거나,
 DNS 구성이 잘못되었거나, NetworkPolicy가 DNS 트래픽을 차단하거나, Pod의 DNS 구성이 잘못되었습니다. Pod에서 DNS 쿼리 실패가 발생하고, kube-system Namespace에서 CoreDNS Pod가 CrashLoopBackOff 또는 Failed 상태를 보이며, DNS 쿼리가 오류를 반환합니다. 이는 DNS 플레인에 영향을 미치며, CoreDNS Pod 실패, NetworkPolicy 제한 또는 DNS 구성 문제로 인해 클러스터 내부 서비스 디스커버리를 방해합니다. 애플리케이션이 이름으로 서비스에 연결할 수 없습니다.

## 영향

Pod가 서비스 DNS 이름을 해석할 수 없음; 클러스터 내부 서비스 디스커버리 실패; 애플리케이션이 이름으로 서비스에 연결 불가; DNS 쿼리 실패; CoreDNS Pod가 실행되지 않거나 접근 불가; KubeDNSDown 알림 발생; KubeDNSRequestsErrors 알림 발생; 서비스 간 통신 실패; 애플리케이션이 서비스 엔드포인트를 해석할 수 없음.

## 플레이북

1. `kubectl describe pod <pod-name> -n <namespace>`를 사용하여 Namespace `<namespace>`에서 Pod `<pod-name>`을 describe하고 `spec.dnsPolicy`와 `spec.dnsConfig`의 DNS 구성을 확인하며, Pod 조건과 이벤트를 검토합니다.

2. `kubectl get events -n <namespace> --field-selector involvedObject.name=<pod-name> --sort-by='.metadata.creationTimestamp'`를 사용하여 Pod의 이벤트를 조회하고 DNS 접근 문제와 관련된 최근 이벤트를 파악합니다.

3. kube-system Namespace의 Pod를 나열하고 CoreDNS Pod 상태를 확인하여 DNS Pod가 실행 중이고 Ready 상태인지 확인합니다.

4. kube-system Namespace에서 kube-dns Service를 조회하고 존재하며 엔드포인트가 있는지 확인하여 DNS 서비스가 접근 가능한지 확인합니다.

5. Pod `<pod-name>`에서 `nslookup <service-name>.<namespace>.svc.cluster.local` 또는 동등한 DNS 쿼리를 Pod Exec 도구를 사용하여 실행하고 DNS 해석을 테스트합니다.

6. Namespace `<namespace>`와 kube-system Namespace의 NetworkPolicy 객체를 나열하고 정책이 CoreDNS Pod로의 DNS 트래픽을 차단하는지 확인합니다.

7. kube-system Namespace에서 CoreDNS Pod 로그를 조회하고 오류를 확인하여 DNS가 작동하지 않는 이유를 파악합니다.

## 진단

플레이북 섹션에서 수집한 Pod describe 출력과 이벤트를 분석하는 것으로 시작합니다. Pod의 DNS 구성, CoreDNS Pod 상태, kube-dns 서비스 상태가 주요 진단 신호를 제공합니다.

**Pod describe에서 dnsPolicy: None 또는 사용자 정의 dnsConfig가 표시되는 경우:**
- Pod에 잘못 구성될 수 있는 사용자 정의 DNS 설정이 있습니다. `dnsConfig.nameservers`에 kube-dns 서비스 IP(일반적으로 10.96.0.10)가 포함되어 있는지 확인합니다. dnsPolicy가 None이면 모든 DNS 설정을 명시적으로 제공해야 합니다.

**kube-system의 CoreDNS Pod가 Running 또는 Ready 상태가 아닌 경우:**
- 클러스터 DNS 서비스가 불가용합니다. 이것이 근본 원인입니다. 계속하기 전에 CoreDNSPodsCrashLooping 플레이북을 사용하여 CoreDNS Pod 실패를 별도로 조사합니다.

**kube-dns 서비스에 엔드포인트가 없는 경우:**
- DNS 서비스는 존재하지만 백엔드 Pod가 없습니다. CoreDNS Pod가 존재하고 `k8s-app=kube-dns`로 올바르게 레이블되어 있는지 확인합니다. CoreDNS Deployment Replica가 0으로 스케일되지 않았는지 확인합니다.

**Pod의 Namespace 또는 kube-system에 NetworkPolicy가 존재하는 경우:**
- NetworkPolicy가 DNS 트래픽을 차단할 수 있습니다. 정책이 포트 53(UDP 및 TCP)에서 kube-dns 서비스로의 이그레스를 허용하는지 확인합니다. kube-system 정책이 Pod의 Namespace에서의 인그레스를 허용하는지 확인합니다.

**Pod에서 DNS 쿼리가 타임아웃되지만 CoreDNS가 정상인 경우:**
- Pod와 CoreDNS 간 네트워크 연결이 차단되었습니다. Pod의 노드가 CoreDNS Pod 노드에 네트워크 연결이 가능한지 확인합니다. 양쪽 노드의 CNI 플러그인 상태를 확인합니다.

**이벤트가 결론을 내리기 어려운 경우, 타임스탬프를 상관 분석합니다:**
1. Pod 생성 시간과 DNS 구성을 확인하여 특정 DNS 정책으로 Pod가 생성된 후 DNS 실패가 시작되었는지 확인합니다.
2. 실패 시작 시점과 정책 생성 타임스탬프를 비교하여 실패가 NetworkPolicy 변경과 상관관계가 있는지 확인합니다.
3. 서비스 리소스 버전 변경을 확인하여 kube-dns 서비스 또는 엔드포인트가 수정되었는지 확인합니다.

**명확한 원인을 파악하지 못한 경우:** 동일 Namespace에 기본 DNS 설정으로 디버그 Pod를 생성하여 문제가 Pod 특정인지 Namespace 전체인지 격리합니다. 클러스터 서비스와 외부 도메인 모두에 대한 DNS 해석을 테스트합니다.
