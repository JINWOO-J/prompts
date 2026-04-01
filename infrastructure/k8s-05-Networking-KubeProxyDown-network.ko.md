---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/05-Networking/KubeProxyDown-network.md)'
role: Kubernetes SRE
origin: scoutflo
extract_date: 2026-03-05
tags:
- infrastructure
- k8s-daemonset
- k8s-namespace
- k8s-node
- k8s-pod
- k8s-service
- kubeproxydown
- kubernetes
- monitoring
- network
- networking
- performance
---

---
title: KubeProxy Down
weight: 20
---

# KubeProxyDown - KubeProxy 중단

## 의미

Kubernetes Proxy(kube-proxy) 인스턴스에 접근할 수 없거나 응답하지 않는 상태(KubeProxyDown 알림 발생)로, 모든 kube-proxy DaemonSet Pod가 실패했거나, 네트워크 연결이 끊어졌거나, 모니터링 시스템에서 접근할 수 없는 것이 원인입니다. kubectl에서 kube-proxy Pod가 CrashLoopBackOff 또는 Failed 상태를 보이고, kube-proxy 로그에 치명적 오류, panic 메시지 또는 연결 타임아웃 오류가 표시되며, Service Endpoint가 트래픽 라우팅에 실패합니다. 이는 네트워크 계층에 영향을 미치며 영향받는 노드에서 Service 네트워킹, 로드 밸런싱, 네트워크 규칙 관리를 방해하고, 일반적으로 Pod 장애, 노드 네트워킹 문제, iptables/ipvs 문제 또는 컨테이너 런타임 문제가 원인입니다. 애플리케이션이 Service에 접근할 수 없으며 오류가 발생할 수 있습니다.

## 영향

KubeProxyDown 알림 발생, Pod로의 네트워크 통신 실패, Service Endpoint 작동 불가 가능, 로드 밸런싱 실패, 네트워크 규칙 미유지, Pod가 Service를 통해 통신 불가, 클러스터 네트워킹 저하, Pod 간 통신 실패 가능, Service Discovery 영향, Service 네트워킹 및 로드 밸런싱 작업 실패. kube-proxy Pod가 CrashLoopBackOff 또는 Failed 상태 유지, Service Endpoint에서 connection refused 또는 타임아웃 오류 반환, 애플리케이션이 Service에 접근할 수 없어 오류 또는 성능 저하 발생 가능.

## 플레이북

1. `kube-system` Namespace에서 kube-proxy Pod `<pod-name>`을 상세 조회하여 상태, 조건, 이벤트를 포함한 상세 정보를 확인합니다.

2. `kube-system` Namespace에서 kube-proxy Pod `<pod-name>`의 이벤트를 타임스탬프 순으로 조회하여 최근 문제를 파악합니다.

3. `kube-system` Namespace에서 kube-proxy DaemonSet을 조회하고 상태를 검사하여 kube-proxy DaemonSet 상태를 확인합니다.

4. `kube-system` Namespace에서 kube-proxy Pod의 로그를 조회하고 'panic', 'fatal', 'connection refused', 'timeout', 'iptables', 'ipvs' 등의 오류 패턴을 필터링하여 kube-proxy 장애를 파악합니다.

5. 모니터링 시스템과 kube-proxy Pod Endpoint 간 네트워크 연결을 확인하여 연결 문제를 확인합니다.

6. kube-proxy Pod가 실행되어야 하는 노드 `<node-name>`을 상세 조회하고 노드 상태와 조건을 확인하여 노드 문제를 파악합니다.

7. `kube-system` Namespace에서 kube-proxy 설정용 ConfigMap을 조회하고 kube-proxy 설정에 문제가 있는지 확인합니다.

## 진단

1. 플레이북에서 kube-proxy Pod 이벤트를 분석하여 장애 사유를 파악합니다. 이벤트에서 CrashLoopBackOff, Failed 또는 BackOff 상태가 표시되면, kube-proxy 장애 원인을 나타내는 구체적인 오류 메시지를 확인합니다.

2. 이벤트에서 Pod 장애가 표시되면, 플레이북에서 kube-proxy 로그의 panic, fatal 또는 연결 오류를 확인합니다. 로그에서 API Server 연결 타임아웃 또는 거부 오류가 표시되면, kube-proxy가 Control Plane과 통신할 수 없습니다.

3. API Server 연결 문제가 있으면, 영향받는 노드에서 API Server Endpoint 접근 가능성을 확인합니다. API Server에 접근할 수 없으면, kube-proxy가 Endpoint를 동기화할 수 없고 iptables/ipvs 규칙이 오래됩니다.

4. API Server에 접근 가능하면, 플레이북에서 kube-proxy DaemonSet 상태를 확인합니다. 원하는 수와 Ready 수가 일치하지 않으면, kube-proxy Pod가 누락된 노드를 파악하고 노드 상태를 확인합니다.

5. DaemonSet 스케줄링이 올바르면, 플레이북에서 노드 상태의 NotReady 상태, MemoryPressure, DiskPressure 또는 PIDPressure를 검토합니다. 노드에서 리소스 압박이 표시되면, kube-proxy가 축출되거나 시작할 수 없을 수 있습니다.

6. 노드 리소스가 가용하면, 플레이북에서 kube-proxy ConfigMap의 설정 문제를 확인합니다. iptables/ipvs 모드가 잘못 구성되었거나 clusterCIDR이 올바르지 않으면, kube-proxy가 네트워크 규칙을 프로그래밍하는 데 실패합니다.

**설정 문제가 발견되지 않는 경우**: iptables/ipvs 커널 모듈 가용성을 검토하고, 영향받는 노드의 컨테이너 런타임 상태를 확인하고, kube-proxy와 API Server 간 네트워크 연결을 확인하고, 보안 컨텍스트 또는 Pod Security Policy가 kube-proxy의 필요한 권한으로의 실행을 방해하는지 검사합니다.
