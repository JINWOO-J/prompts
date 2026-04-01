---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/05-Networking/CoreDNSDown-dns.md)'
role: Kubernetes SRE
origin: scoutflo
extract_date: 2026-03-05
tags:
- corednsdown
- database
- dns
- infrastructure
- k8s-deployment
- k8s-ingress
- k8s-namespace
- k8s-node
- k8s-pod
- k8s-service
- kubernetes
- networking
---

---
title: CoreDNS Down
weight: 10
categories: [kubernetes, dns]
---

# CoreDNSDown - CoreDNS 중단

## 의미

CoreDNS Pod가 실행되지 않거나 응답하지 않는 상태(CoreDNSDown 또는 KubeDNSDown 알림 발생)로, Pod 크래시, 리소스 고갈, 설정 오류 또는 노드 문제로 인해 DNS 서비스에 장애가 발생한 것입니다. kubectl에서 CoreDNS Deployment의 Ready 레플리카가 0이거나 부족하게 표시되며, 클러스터 전체에서 DNS 확인이 실패하고, 모든 Namespace의 Pod에서 'connection refused' 또는 'no such host' 오류가 로그에 나타나며, 애플리케이션 로그에 DNS 조회 실패가 기록됩니다. 이는 클러스터 DNS 계층에 영향을 미치며, 리소스 제약, 설정 오류, 노드 장애 또는 네트워크 문제로 인한 심각한 인프라 장애를 나타냅니다. 애플리케이션이 Service 이름이나 외부 도메인을 확인할 수 없으며, 초기화 중 DNS 확인에 의존하는 새 Pod는 시작에 실패할 수 있습니다.

## 영향

CoreDNSDown 알림 발생, 클러스터 전체 DNS 확인 실패, Pod가 Service 이름을 확인할 수 없음, 애플리케이션 로그에 'no such host' 오류 표시, 외부 도메인 확인 실패, DNS에 의존하는 kubectl exec 및 logs 실패 가능, 새 Pod 배포가 ContainerCreating 상태에서 멈출 수 있음, Service Mesh 통신 중단, DNS에 의존하는 헬스 체크 실패, 호스트명 확인 오류로 데이터베이스 연결 실패, 외부 서비스 API 호출이 DNS 오류로 타임아웃. 애플리케이션 오류가 급격히 증가하고, 모든 Namespace에서 연쇄 장애 발생, Service Endpoint에 접근 불가, Ingress Controller가 백엔드 서비스를 확인할 수 없으며, 전체 애플리케이션 스택이 사용 불가능해질 수 있습니다.

## 플레이북

1. `kube-system` Namespace에서 CoreDNS Deployment를 조회하고 Ready 레플리카 수를 확인하여, 레플리카가 0이거나 원하는 수보다 적은지 확인하여 DNS 서비스 중단을 확인합니다.

2. `kube-system` Namespace에서 모든 CoreDNS Pod를 조회하고 상태, 재시작 횟수, 노드 배치를 검사하여 어떤 Pod가 어디서 실패하고 있는지 파악합니다. 'CrashLoopBackOff', 'Pending', 'Error', 'OOMKilled' 상태 패턴을 필터링합니다.

3. `kube-system` Namespace에서 CoreDNS Pod의 이벤트를 조회하고 'Failed', 'Error', 'OOMKilled', 'Evicted', 'FailedScheduling', 'BackOff' 등의 오류 패턴을 필터링하여 Pod 라이프사이클 문제를 파악합니다.

4. `kube-system` Namespace에서 CoreDNS Pod의 로그를 조회하고 'SERVFAIL', 'NXDOMAIN', 'connection refused', 'plugin/errors', 'context deadline exceeded', 'i/o timeout' 등의 오류 패턴을 필터링하여 DNS 관련 오류를 파악합니다.

5. `kube-system` Namespace에서 CoreDNS ConfigMap(coredns 또는 kube-dns)을 조회하고 Corefile 설정에서 구문 오류, 누락된 플러그인 또는 잘못 구성된 업스트림 리졸버를 확인합니다.

6. CoreDNS Pod가 스케줄링된 노드를 조회하고 Ready, MemoryPressure, DiskPressure, NetworkUnavailable 등의 노드 상태를 확인하여 DNS Pod에 영향을 미치는 노드 수준 문제를 파악합니다.

7. 실행 중인 Pod에서 Pod Exec 도구를 사용하여 'nslookup kubernetes.default.svc.cluster.local'을 실행하고 kube-dns Service IP에 대한 DNS 확인을 테스트하여 DNS가 완전히 중단되었는지 부분적으로 저하되었는지 확인합니다.

## 진단

플레이북 3단계의 CoreDNS Pod 이벤트를 분석하여 주요 장애 원인을 파악합니다. 이벤트에서 종료 코드 137과 함께 'OOMKilled'가 표시되면, Pod 종료 타임스탬프와 5분 이내의 메모리 사용량 메트릭을 상관 분석하고, 컨테이너 메모리 메트릭과 Pod 리소스 사양을 근거로 메모리 제한이 너무 낮아 Pod가 종료되고 있는지 확인합니다.

이벤트에서 'node(s) had taints' 또는 'Insufficient cpu/memory' 메시지와 함께 'FailedScheduling'이 표시되면, Pod 스케줄링 타임스탬프와 노드 가용 리소스를 비교하고, 노드 할당 가능 리소스와 Pod Toleration을 근거로 스케줄링 제약 또는 리소스 고갈이 CoreDNS Pod 실행을 방해하는지 확인합니다.

CoreDNS Pod 종료 타임스탬프와 5분 이내의 노드 상태 전환 시간을 비교하고, 노드 이벤트와 Pod 스케줄링 이력을 근거로 DNS 장애가 노드 장애 또는 네트워크 불가 상태와 일치하는지 확인합니다.

CoreDNS 설정 변경(ConfigMap 수정 타임스탬프)과 5분 이내의 DNS 장애 타임스탬프를 상관 분석하고, ConfigMap 리비전 이력과 컨트롤러 로그를 근거로 Corefile 구문 오류 또는 잘못 구성된 업스트림 리졸버가 장애를 유발했는지 확인합니다.

CoreDNS Pod가 'Pending' 상태를 보이면, Pod 이벤트에서 Affinity, Toleration 또는 리소스 제약 위반을 분석하고, Pod 스펙과 노드 레이블을 근거로 노드 셀렉터 또는 Anti-Affinity 규칙이 스케줄링을 방해하는지 확인합니다.

지정된 시간 범위 내에서 상관관계가 발견되지 않으면: CNI Pod 상태를 확인하여 클러스터 네트워킹(CNI)이 정상 작동하는지 확인하고, 모든 노드에서 kube-proxy가 실행 중인지 확인하고, CoreDNS의 ServiceAccount 및 RBAC 권한을 확인하고, 기반 노드 네트워킹의 인터페이스 오류를 검사하고, DNS 트래픽(포트 53 UDP/TCP)을 차단하는 NetworkPolicy 규칙이 있는지 확인합니다.
