---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/05-Networking/Kube-proxyFailing-network.md)'
role: Kubernetes SRE
origin: scoutflo
extract_date: 2026-03-05
tags:
- dns
- infrastructure
- k8s-daemonset
- k8s-namespace
- k8s-pod
- k8s-service
- kube
- kubernetes
- network
- networking
- performance
- proxyfailing
---

---
title: Kube-proxy Failing - Network
weight: 280
categories:
  - kubernetes
  - network
---

# Kube-proxyFailing-network - kube-proxy 장애

## 의미

kube-proxy Pod가 장애 상태이며(KubeProxyDown 또는 KubeServiceNotReady 알림 발생), kube-proxy DaemonSet Pod가 시작할 수 없거나, CrashLoopBackOff 상태에서 크래시하거나, API Server 엔드포인트에 연결할 수 없는 것이 원인입니다. kube-system Namespace에서 kube-proxy Pod가 CrashLoopBackOff 또는 Failed 상태를 보이고, kube-proxy 로그에 연결 타임아웃 오류 또는 프로세스 장애가 표시되며, Service IP 라우팅이 실패합니다. 이는 네트워크 계층에 영향을 미치며 Service가 백엔드 Pod로 트래픽을 전달하는 것을 방해하고, 일반적으로 kube-proxy 프로세스 크래시, API Server 연결 문제 또는 리소스 제약이 원인입니다. 애플리케이션이 Service에 접근할 수 없으며 오류가 발생할 수 있습니다.

## 영향

Service가 트래픽을 전달할 수 없음, Service IP 라우팅 실패, 로드 밸런싱 작동 불가, Pod가 Service 이름 또는 ClusterIP로 Service에 접근 불가, kube-proxy Pod가 실행되지 않을 때 KubeProxyDown 알림 발생, Service가 트래픽을 라우팅할 수 없을 때 KubeServiceNotReady 알림 발생, kube-proxy Pod 크래시 또는 재시작, Service Endpoint 미업데이트, 클러스터 내부 Service 통신 실패, 애플리케이션이 Service에 접근 불가, Service DNS 확인은 되지만 연결 실패. kube-proxy Pod가 무기한 CrashLoopBackOff 또는 Failed 상태 유지, kube-proxy 로그에 연결 타임아웃 오류 표시, 애플리케이션이 Service에 접근할 수 없어 오류 또는 성능 저하 발생 가능, 클러스터 내부 Service 통신 실패.

## 플레이북

1. `kube-system` Namespace에서 kube-proxy Pod `<kube-proxy-pod-name>`을 상세 조회하여 상태, 조건, 장애 사유를 포함한 상세 정보를 확인합니다.

2. `kube-system` Namespace에서 kube-proxy Pod `<kube-proxy-pod-name>`의 이벤트를 타임스탬프 순으로 조회하여 최근 장애와 문제를 파악합니다.

3. `kube-system` Namespace에서 kube-proxy Pod를 조회하고 상태를 확인하여 어떤 Pod가 장애 또는 크래시 상태인지 파악합니다.

4. `kube-system` Namespace에서 kube-proxy Pod의 로그를 조회하고, kube-proxy 장애 원인을 설명하는 오류, 크래시 또는 시작 실패를 필터링합니다.

5. `kube-system` Namespace에서 kube-proxy DaemonSet을 상세 조회하여 Pod가 올바르게 생성되고 스케줄링되는지 확인합니다.

6. kube-proxy Pod에서 API Server 엔드포인트에 접근할 수 있는지 확인하여 API Server 연결을 검증합니다.

7. kube-proxy Pod가 스케줄링된 노드의 리소스 가용성을 확인하여 리소스 제약이 장애를 유발하는지 확인합니다.

## 진단

1. 플레이북에서 kube-proxy Pod 이벤트를 분석하여 장애 사유와 오류 패턴을 파악합니다. 이벤트에서 CrashLoopBackOff, BackOff 또는 FailedScheduling이 표시되면, 이벤트 메시지에서 구체적인 장애 사유를 확인합니다.

2. 이벤트에서 Pod 크래시가 표시되면, 플레이북에서 kube-proxy 로그의 오류 패턴(panic, fatal, connection refused, timeout)을 확인합니다. 로그에서 API Server 연결 오류가 표시되면, kube-proxy가 Service/Endpoint 정보를 동기화할 수 없습니다.

3. API Server 연결이 실패하면, API Server 가용성과 kube-proxy Service Account 권한을 확인합니다. kube-proxy가 인증할 수 없거나 API Server에 접근할 수 없으면, Service 라우팅 규칙을 업데이트할 수 없습니다.

4. API Server에 접근 가능하면, 플레이북에서 kube-proxy DaemonSet 상태를 확인합니다. Pod가 모든 노드에 스케줄링되지 않으면, 영향받는 노드의 노드 셀렉터, Toleration, 리소스 가용성을 확인합니다.

5. DaemonSet이 올바르게 구성되어 있으면, 플레이북에서 노드 리소스 상태를 검토합니다. 노드에서 MemoryPressure, DiskPressure 또는 PIDPressure가 표시되면, 리소스 제약이 kube-proxy의 올바른 작동을 방해할 수 있습니다.

6. 리소스가 가용하면, 플레이북에서 kube-proxy 설정(ConfigMap)의 iptables/ipvs 모드 설정을 확인하고 네트워크 인터페이스 설정이 클러스터 네트워킹 요구사항과 일치하는지 확인합니다.

**설정 문제가 발견되지 않는 경우**: 영향받는 노드의 iptables/ipvs 규칙 손상을 검토하고, kube-proxy에 필요한 커널 모듈이 로드되어 있는지 확인하고, 컨테이너 런타임이 올바르게 작동하는지 확인하고, 최근 클러스터 업그레이드가 kube-proxy 버전과의 호환성 문제를 도입했는지 검사합니다.
