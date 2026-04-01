---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/01-Control-Plane/KubeAggregatedAPIErrors-control-plane.md)'
role: SRE / K8s Incident Response
origin: scoutflo
tags:
- autoscal
- capacity
- control
- infrastructure
- k8s-namespace
- k8s-pod
- k8s-service
- kubeaggregatedapierrors
- kubernetes
- performance
- plane
- scaling
---

---
title: Kube Aggregated API Errors - Aggregated API 오류
weight: 20
---

# KubeAggregatedAPIErrors

## 의미

Kubernetes Aggregated API Server가 간헐적 실패 또는 높은 오류율을 경험하고 있으며(KubeAggregatedAPIErrors 알림 트리거, 지난 10분 평균 4회 이상 사용 불가 발생 시), Aggregated API Server가 안정성 문제, 연결 문제 또는 리소스 제약을 겪고 있습니다. Aggregated API Server Pod가 간헐적 실패 또는 높은 재시작 횟수를 보이고, 로그에 연결 타임아웃 오류 또는 속도 제한 오류가 나타나며, Aggregated API 엔드포인트가 간헐적으로 500 또는 503 오류를 반환합니다. 이는 Control Plane에 영향을 미치며, Aggregated API 기능 저하를 나타냅니다. 일반적으로 네트워크 불안정, Pod 불안정, 구성 문제 또는 용량 문제가 원인이며, Custom Resource를 사용하는 애플리케이션에서 오류가 발생할 수 있습니다.

## 영향

KubeAggregatedAPIErrors 알림이 발생합니다. Aggregated API 엔드포인트가 간헐적 오류를 반환하고, Custom Resource가 불안정할 수 있습니다. Custom Metrics를 사용하는 경우 HPA가 실패할 수 있습니다. Aggregated API에 의존하는 클러스터 기능이 저하되고, 간헐적으로 클러스터 메트릭을 볼 수 없으며, Custom Metrics를 사용한 안정적인 스케일링이 불가능합니다. 클러스터 운영에 간헐적 실패가 발생하고, Custom Resource Definition이 일시적으로 사용 불가할 수 있으며, 메트릭 기반 오토스케일링이 불안정해집니다.

## 플레이북

1. 모든 APIService 리소스를 describe하여 모든 Aggregated API 서비스의 상세 정보를 확인하고 오류 또는 간헐적 실패를 겪고 있는 서비스를 식별합니다.

2. kube-system 네임스페이스에서 마지막 타임스탬프 순으로 이벤트를 나열하여 최근 Control Plane 이벤트를 조회하고, Aggregated API 오류, 타임아웃 또는 연결 문제를 필터링합니다.

3. `<namespace>` 네임스페이스에서 Aggregated API Server Deployment의 Pod `<pod-name>`을 조회하고 상태, 재시작 횟수 및 컨테이너 상태를 검사하여 오류 상태의 Pod를 식별합니다.

4. `<namespace>` 네임스페이스의 Pod `<pod-name>`에서 로그를 조회하고 'error', 'failed', 'timeout', 'connection refused', 'rate limit'를 포함한 오류 패턴을 필터링하여 오류 원인을 식별합니다.

5. Aggregated API Server 오류율과 응답 시간 메트릭을 조회하여 오류 패턴과 성능 저하를 식별합니다.

6. `<namespace>` 네임스페이스에서 Aggregated API Server 엔드포인트의 Service `<service-name>`을 조회하고 API Server와 Aggregated API Server 엔드포인트 간의 네트워크 연결성을 검증합니다.

7. `<namespace>` 네임스페이스에서 NetworkPolicy 리소스를 조회하고 네트워크 정책이 API Server와 Aggregated API Server 간의 통신을 간헐적으로 차단하는지 확인합니다.

## 진단

1. 플레이북의 Aggregated API Server Pod 이벤트를 분석하여 Pod 불안정성이 간헐적 오류를 유발하는지 식별합니다. 이벤트에서 재시작, 프로브 실패 또는 일시적 오류가 나타나면, 이벤트 타임스탬프를 사용하여 오류 급증과 연관시킵니다.

2. 이벤트에서 Pod 재시작 또는 불안정성이 나타나면, 플레이북 3단계의 재시작 패턴과 원인을 검토합니다. 오류 급증 타임스탬프에서 재시작이 빈번하면, Pod 불안정성이 간헐적 실패를 유발하고 있습니다.

3. 이벤트에서 네트워크 연결 문제가 나타나면, 플레이북 6단계의 서비스 엔드포인트와 연결성을 검증합니다. 오류 타임스탬프에서 네트워크 이벤트가 간헐적 실패를 보이면, 네트워크 불안정이 근본 원인입니다.

4. 이벤트에서 네트워크 정책 변경이 나타나면, 플레이북 7단계의 NetworkPolicy 수정을 검토합니다. 오류 증가 전에 정책 변경이 발생했다면, 네트워크 구성이 간헐적으로 통신을 차단하고 있을 수 있습니다.

5. 이벤트에서 리소스 압박이 나타나면, 오류 타임스탬프에서 Pod 리소스 사용량을 검증합니다. 오류 급증 시 CPU 또는 메모리가 제한에 근접했다면, 리소스 제약이 간헐적 실패를 유발하고 있습니다.

6. 이벤트에서 API Server 부하 문제가 나타나면, 오류 타임스탬프에서 API Server 메트릭을 분석합니다. Aggregated API 오류 급증 시 API Server 지연 또는 오류율이 증가했다면, 업스트림 API Server 문제가 기여하고 있습니다.

7. 이벤트에서 일관된 오류 패턴(간헐적이 아닌)이 나타나면, 문제는 일시적이 아닌 지속적입니다. 오류가 일정한 간격으로 발생하면, 해당 타임스탬프에서 예약된 작업 또는 반복 트리거를 조사합니다.

8. 이벤트에서 간헐적 오류 패턴이 나타나면, 일시적 원인에 집중합니다. 오류가 특정 시간대 또는 작업과 상관관계가 있으면, 네트워크 불안정, API Server 부하 또는 리소스 경합이 원인일 수 있습니다.

**연관 관계를 찾을 수 없는 경우**: 인프라 변경에 대해 시간 범위를 1시간으로 확장하고, Aggregated API Server 구성을 검토하며, 네트워크 불안정을 확인하고, API Server Aggregation 레이어 상태를 검증하며, 과거 Aggregated API 오류 패턴을 검토합니다. Aggregated API 오류는 즉각적인 변경보다 네트워크 불안정, 리소스 제약 또는 안정성 문제로 인해 발생할 수 있습니다.
