---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/01-Control-Plane/KubeAggregatedAPIDown-control-plane.md)'
role: SRE / K8s Incident Response
origin: scoutflo
tags:
- autoscal
- control
- infrastructure
- k8s-namespace
- k8s-pod
- k8s-service
- kubeaggregatedapidown
- kubernetes
- performance
- plane
- scaling
---

---
title: Kube Aggregated API Down - Aggregated API 다운
weight: 20
---

# KubeAggregatedAPIDown

## 의미

Kubernetes Aggregated API Server가 사용 불가 상태이며(KubeAggregatedAPIDown 알림 트리거), Aggregated API Server가 실패하거나, 네트워크 연결이 끊기거나, API Server Aggregation 레이어에서 접근할 수 없습니다. Aggregated API Server Pod가 kubectl에서 CrashLoopBackOff 또는 Failed 상태를 보이고, 로그에 치명적 오류, panic 메시지 또는 연결 타임아웃 오류가 나타나며, Aggregated API 엔드포인트가 연결 거부 또는 타임아웃 오류를 반환합니다. 이는 Control Plane에 영향을 미치며, Custom Resource, Metrics API 또는 기타 Aggregated API 기능이 작동하지 않습니다. 일반적으로 Pod 실패, 네트워크 문제, 구성 문제 또는 리소스 제약이 원인이며, Custom Resource를 사용하는 애플리케이션에서 오류가 발생할 수 있습니다.

## 영향

KubeAggregatedAPIDown 알림이 발생합니다. Aggregated API 엔드포인트가 오류를 반환하고, Custom Resource를 사용할 수 없을 수 있습니다. Custom Metrics를 사용하는 경우 HPA가 실패할 수 있습니다. Aggregated API에 의존하는 클러스터 기능이 저하되고, 클러스터 메트릭을 볼 수 없으며, Custom Metrics를 사용한 스케일링이 불가능합니다. 클러스터 운영이 심각하게 제한될 수 있고, Custom Resource Definition에 접근할 수 없으며, 메트릭 기반 오토스케일링이 실패합니다.

## 플레이북

1. 모든 APIService 리소스를 describe하여 모든 Aggregated API 서비스의 상세 정보를 확인하고 사용 불가 또는 저하 상태의 서비스를 식별합니다.

2. kube-system 네임스페이스에서 마지막 타임스탬프 순으로 이벤트를 나열하여 최근 Control Plane 이벤트를 조회하고, Aggregated API Server 오류 또는 연결 실패를 필터링합니다.

3. `<namespace>` 네임스페이스에서 Aggregated API Server Deployment의 Pod `<pod-name>`을 조회하고 상태, 재시작 횟수 및 컨테이너 상태를 검사하여 Aggregated API Server가 실행 중인지 확인합니다.

4. `<namespace>` 네임스페이스의 Pod `<pod-name>`에서 로그를 조회하고 'panic', 'fatal', 'connection refused', 'timeout', 'certificate'를 포함한 오류 패턴을 필터링하여 시작 또는 런타임 실패를 식별합니다.

5. `<namespace>` 네임스페이스에서 Aggregated API Server 엔드포인트의 Service `<service-name>`을 조회하고 API Server와 Aggregated API Server 엔드포인트 간의 네트워크 연결성을 검증합니다.

6. `<namespace>` 네임스페이스에서 NetworkPolicy 리소스를 조회하고 네트워크 정책이 API Server와 Aggregated API Server 간의 통신을 차단하는지 확인합니다.

7. `<namespace>` 네임스페이스에서 Aggregated API Server의 Service `<service-name>`과 Endpoints를 조회하고 Aggregated API Server 구성과 서비스 엔드포인트를 검증합니다.

8. APIService 리소스를 조회하고 API Server Aggregation 레이어 구성과 Aggregated API Server 등록을 확인합니다.

## 진단

1. 플레이북의 Aggregated API Server Pod 이벤트를 분석하여 실패 모드와 시점을 식별합니다. 이벤트에서 CrashLoopBackOff, Failed 또는 Pod 종료가 나타나면, 이벤트 타임스탬프와 오류 메시지를 사용하여 근본 원인을 판단합니다.

2. 이벤트에서 Aggregated API Server 크래시 또는 실패가 나타나면, 플레이북 4단계의 Pod 로그를 검토합니다. 이벤트 타임스탬프에서 로그가 panic 메시지, 치명적 오류 또는 시작 실패를 보이면, 애플리케이션 수준 문제가 비가용성을 유발한 것입니다.

3. 이벤트에서 네트워크 연결 문제가 나타나면, 플레이북 5단계의 서비스 엔드포인트를 검증합니다. Aggregated API가 실패한 타임스탬프에서 서비스 또는 엔드포인트 이벤트가 비가용성을 보이면, 네트워크 연결이 근본 원인입니다.

4. 이벤트에서 네트워크 정책 변경이 나타나면, 플레이북 6단계의 NetworkPolicy 수정을 검토합니다. Aggregated API가 사용 불가가 되기 전에 네트워크 정책 이벤트가 발생했다면, 정책 변경이 API Server와 Aggregated API 간의 통신을 차단했을 수 있습니다.

5. 이벤트에서 APIService 등록 문제가 나타나면, 플레이북 8단계의 APIService 상태를 검증합니다. 비가용성 타임스탬프에서 APIService 이벤트가 등록 실패 또는 조건 변경을 보이면, Aggregation 레이어 구성이 문제입니다.

6. 이벤트에서 리소스 압박(OOMKilled, CPU 스로틀링)이 나타나면, 이벤트 타임스탬프에서 Pod 리소스 사용량을 검증합니다. 실패 시작 시 리소스 사용량이 제한을 초과했다면, 리소스 제약이 비가용성을 유발한 것입니다.

7. 이벤트에서 구성 변경이 나타나면, 변경 타임스탬프와 실패 시작을 연관시킵니다. Aggregated API가 사용 불가가 되기 전에 구성 수정이 발생했다면, 최근 변경이 잘못된 설정을 도입했을 수 있습니다.

**연관 관계를 찾을 수 없는 경우**: 인프라 변경에 대해 시간 범위를 1시간으로 확장하고, Aggregated API Server 구성을 검토하며, API Server Aggregation 레이어 문제를 확인하고, 네트워크 연결성을 검증하며, 과거 Aggregated API 안정성 패턴을 검토합니다. Aggregated API 실패는 즉각적인 변경보다 네트워크 문제, 구성 문제 또는 리소스 제약으로 인해 발생할 수 있습니다.
