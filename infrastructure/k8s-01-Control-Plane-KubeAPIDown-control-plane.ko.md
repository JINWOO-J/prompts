---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/01-Control-Plane/KubeAPIDown-control-plane.md)'
role: SRE / K8s Incident Response
origin: scoutflo
tags:
- control
- infrastructure
- k8s-namespace
- k8s-node
- k8s-pod
- k8s-service
- kubeapidown
- kubernetes
- monitoring
- performance
- plane
---

---
title: Kube API Down - API Server 다운
weight: 20
---

# KubeAPIDown

## 의미

Kubernetes API Server에 접근할 수 없거나 응답하지 않으며(KubeAPIDown 알림 트리거), 모든 API Server 인스턴스가 실패하거나, 네트워크 연결이 끊기거나, 심각한 장애를 겪고 있습니다. API Server Pod가 kubectl에서 CrashLoopBackOff 또는 Failed 상태를 보이고, 로그에 치명적 오류, panic 메시지 또는 연결 타임아웃 오류가 나타나며, kubectl 명령이 연결 거부 또는 타임아웃 오류를 반환합니다. 이는 Control Plane에 영향을 미치며, API Server 통신이 필요한 모든 클러스터 운영을 차단합니다. 일반적으로 Pod 크래시, etcd 비가용성, 인증서 만료, 노드 실패 또는 네트워크 파티션이 원인이며, 애플리케이션이 클러스터 리소스에 접근할 수 없습니다.

## 영향

KubeAPIDown 알림이 발생합니다. 모든 API 작업이 실패하고, 클러스터가 완전히 비기능 상태가 됩니다. kubectl 명령이 실패하고, Controller가 조정을 중단하며, 노드가 Control Plane과 통신할 수 없습니다. 새 Pod를 스케줄링할 수 없고, 리소스 업데이트가 차단되며, 클러스터가 사실상 다운됩니다. 인증 및 권한 부여가 실패하고, 서비스 디스커버리 및 엔드포인트 업데이트가 중단됩니다. Prometheus 모니터링이 API Server 메트릭을 스크레이핑할 수 없습니다.

## 플레이북

1. kube-system 네임스페이스에서 component=kube-apiserver 레이블을 가진 Pod를 describe하여 상태, 재시작 횟수, 컨테이너 상태 및 오류 조건을 포함한 상세 API Server Pod 정보를 확인합니다.

2. kube-system 네임스페이스에서 마지막 타임스탬프 순으로 이벤트를 나열하여 최근 Control Plane 이벤트를 조회하고, API Server 실패, CrashLoopBackOff 또는 연결 오류를 필터링합니다.

3. kube-system 네임스페이스에서 component=kube-apiserver 레이블을 가진 Pod `<pod-name>`의 로그를 조회하고 'panic', 'fatal', 'connection refused', 'etcd', 'timeout', 'certificate'를 포함한 오류 패턴을 필터링하여 시작 또는 런타임 실패를 식별합니다.

4. cluster-info를 확인하고 API Server 헬스 엔드포인트를 테스트하여 API Server 엔드포인트 연결성을 검증합니다.

5. API Server Pod를 호스팅하는 Control Plane 노드의 Node `<node-name>`을 조회하고 노드 상태와 네트워크 연결성을 확인하여 노드 상태를 검증합니다.

6. kube-system 네임스페이스에서 component=etcd 레이블을 가진 Pod `<pod-name>`을 조회하고 etcd Pod 상태와 상태를 확인하여 API Server가 의존하는 etcd 가용성을 검증합니다.

7. NetworkPolicy 리소스를 조회하고 Prometheus 또는 모니터링 시스템의 API Server 엔드포인트 접근을 차단할 수 있는 네트워크 정책과 방화벽 규칙을 검증합니다.

## 진단

1. 플레이북의 API Server Pod 이벤트를 분석하여 실패 모드를 식별합니다. 이벤트에서 CrashLoopBackOff, Failed 또는 특정 오류 메시지와 함께 Pod 종료가 나타나면, 이벤트 타임스탬프를 사용하여 실패 시작 시점과 근본 원인 범주를 판단합니다.

2. 이벤트에서 API Server 크래시 또는 panic이 나타나면, 이벤트 타임스탬프에서 API Server 로그의 치명적 오류 또는 panic 트레이스를 검토합니다. 로그에 panic 메시지 또는 치명적 오류가 나타나면, 애플리케이션 수준 문제 또는 구성 문제가 크래시를 유발한 것입니다.

3. 이벤트에서 etcd 연결 실패가 나타나면, 플레이북 6단계의 etcd Pod 이벤트와 상태를 분석합니다. API Server 실패 이전 타임스탬프에서 etcd 이벤트가 비가용성, 리더 선출 문제 또는 실패를 보이면, etcd가 근본 원인입니다.

4. 이벤트에서 인증서 오류 또는 인증 실패가 나타나면, API Server 로그에서 인증서 만료와 유효성을 검증합니다. 이벤트 타임스탬프에서 인증서 관련 오류가 나타나면, 만료되거나 유효하지 않은 인증서가 API Server 실패를 유발한 것입니다.

5. 이벤트에서 리소스 압박(OOMKilled, CPU 스로틀링)이 나타나면, API Server Pod 리소스 사용량을 제한과 비교합니다. 이벤트 타임스탬프에서 리소스 사용량이 제한을 초과했다면, 리소스 제약이 실패를 유발한 것입니다.

6. 이벤트에서 Control Plane 노드 문제가 나타나면, 플레이북 5단계의 노드 조건 전환을 분석합니다. API Server 실패 이전 타임스탬프에서 노드 이벤트가 NotReady, MemoryPressure 또는 DiskPressure를 보이면, 노드 수준 문제가 근본 원인입니다.

7. 이벤트에서 네트워크 정책 또는 방화벽 변경이 나타나면, 네트워크 구성 변경 타임스탬프와 API Server 실패 시작을 연관시킵니다. API Server에 접근할 수 없게 되기 전에 네트워크 변경이 발생했다면, 네트워크 구성이 연결을 차단한 것입니다.

**연관 관계를 찾을 수 없는 경우**: 인프라 변경에 대해 시간 범위를 1시간으로 확장하고, Control Plane 노드 시스템 로그를 검토하며, etcd에 영향을 미치는 스토리지 문제를 확인하고, 외부 Load Balancer 상태를 검증하며, 과거 API Server 안정성 패턴을 검토합니다. API Server 실패는 즉각적인 구성 변경보다 하드웨어 실패, 네트워크 인프라 문제 또는 Control Plane 노드 실패로 인해 발생할 수 있습니다.
