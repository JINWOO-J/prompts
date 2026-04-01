---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/01-Control-Plane/KubeAPIErrorBudgetBurn-control-plane.md)'
role: SRE / K8s Incident Response
origin: scoutflo
tags:
- capacity
- control
- infrastructure
- k8s-namespace
- k8s-pod
- kubeapierrorbudgetburn
- kubernetes
- monitoring
- performance
- plane
---

---
title: Kube API Error Budget Burn - API Error Budget 소진
weight: 20
---

# KubeAPIErrorBudgetBurn

## 의미

KubeAPIErrorBudgetBurn은 과도한 오류 또는 느린 응답으로 인해 API Server가 허용된 Error Budget을 너무 빠르게 소진할 때 발생합니다(KubeAPIErrorBudgetBurn 알림 트리거). API Server 메트릭에서 높은 오류율 또는 느린 응답 시간이 나타나고, 로그에 타임아웃 오류 또는 Admission Webhook 실패가 나타나며, Error Budget 소비가 허용 임계값을 초과합니다. 이는 Control Plane에 영향을 미치며, API Server 가용성 또는 성능이 허용 가능한 SLO 임계값을 넘어 저하되고 있음을 나타냅니다. 일반적으로 높은 오류율, 느린 응답 시간, etcd 문제, Admission Webhook 문제 또는 용량 제약이 원인이며, Kubernetes API를 사용하는 애플리케이션에서 오류가 발생할 수 있습니다.

## 영향

KubeAPIErrorBudgetBurn 알림이 발생합니다. Kubernetes 클러스터의 전반적인 가용성이 더 이상 보장되지 않습니다. API Server에서 반환하는 오류가 너무 많거나 응답이 너무 느려 적절한 조정을 보장할 수 없습니다. API Server Error Budget이 소진되고 있으며, 클러스터 SLO 목표가 위험에 처할 수 있습니다. API 작업이 불안정해지고, Controller 조정에 영향을 미칠 수 있습니다. 읽기/쓰기 동사 작업이 Error Budget 소진에 기여하며, 클러스터 운영이 허용 가능한 임계값을 넘어 저하됩니다.

## 플레이북

1. kube-system 네임스페이스에서 component=kube-apiserver 레이블을 가진 Pod를 describe하여 상태, 리소스 사용량 및 Error Budget 소진에 기여하는 오류 조건을 포함한 상세 API Server Pod 정보를 확인합니다.

2. kube-system 네임스페이스에서 마지막 타임스탬프 순으로 이벤트를 나열하여 최근 Control Plane 이벤트를 조회하고, API Server 오류, 타임아웃 또는 Admission Webhook 실패를 필터링합니다.

3. API Server 메트릭에서 현재 가용성, 남은 Error Budget 및 어떤 동사(읽기/쓰기)가 소진에 기여하는지 조회하여 Error Budget 소비를 정량화합니다.

4. kube-system 네임스페이스에서 component=kube-apiserver 레이블을 가진 Pod `<pod-name>`의 로그를 조회하고 높은 오류율, 타임아웃 및 네임스페이스, 사용자 또는 Admission Webhook과 관련된 느린 요청을 포함한 오류 패턴을 필터링하여 오류 소스를 식별합니다.

5. kube-system 네임스페이스에서 component=etcd 레이블을 가진 Pod `<pod-name>`을 조회하고 etcd 상태를 검증하며, Aggregated API Server를 확인하고, 소진율을 증폭시킬 수 있는 Admission Webhook을 검증합니다.

6. API Server 메트릭에서 요청률, 오류율 및 지연 패턴을 조회하여 성능 저하 패턴을 식별합니다.

7. kube-system 네임스페이스에서 component=kube-apiserver 레이블을 가진 Pod `<pod-name>`을 조회하고 API Server 리소스 사용량과 용량 제약을 검증하여 리소스 제한을 식별합니다.

## 진단

1. 플레이북의 API Server 이벤트를 분석하여 오류 패턴과 시점을 식별합니다. 이벤트에서 타임아웃 오류, Admission Webhook 실패 또는 연결 문제가 나타나면, 이벤트 타임스탬프를 사용하여 Error Budget 소진이 가속된 시점을 판단합니다.

2. 이벤트에서 높은 오류율 또는 실패한 요청이 나타나면, 이벤트 타임스탬프에서 API Server 로그의 특정 오류 유형을 검토합니다. 로그에 5xx 오류, 타임아웃 또는 거부 패턴이 나타나면, 어떤 요청 유형이 Error Budget 소진에 기여하는지 식별합니다.

3. 이벤트에서 etcd 연결 또는 성능 문제가 나타나면, 플레이북 5단계의 etcd Pod 이벤트와 상태를 분석합니다. Error Budget 소진과 상관관계가 있는 타임스탬프에서 etcd 이벤트가 지연 급증, 리더 선출 또는 실패를 보이면, etcd가 주요 기여 요인입니다.

4. 이벤트에서 Admission Webhook 타임아웃 또는 실패가 나타나면, Admission Webhook 메트릭과 로그를 검토합니다. 소진 기간의 타임스탬프에서 Webhook 이벤트가 느린 응답 또는 오류를 보이면, Webhook 지연이 Error Budget을 소비하고 있습니다.

5. 이벤트에서 Aggregated API Server 문제가 나타나면, 플레이북 5단계의 Aggregated API 상태를 검증합니다. 소진과 상관관계가 있는 타임스탬프에서 Aggregated API 이벤트가 실패를 보이면, Aggregated API 문제가 Error Budget 소비에 기여하고 있습니다.

6. 이벤트에서 API Server 리소스 압박이 나타나면, 이벤트 타임스탬프에서 Pod 리소스 사용량을 검증합니다. 소진 기간에 CPU 또는 메모리가 제한에 근접했다면, 리소스 제약이 느린 응답을 유발하여 Budget 소진에 기여하고 있습니다.

7. 이벤트가 결론적이지 않으면, 이벤트 타임스탬프에서 API Server 요청 지속 시간 메트릭을 검토하여 소진이 오류(높은 5xx 비율)로 인한 것인지 지연(느린 응답)으로 인한 것인지 분석합니다. 지연 패턴이 지배적이면 성능 최적화에 집중하고, 오류가 지배적이면 안정성 문제에 집중합니다.

**연관 관계를 찾을 수 없는 경우**: 인프라 변경에 대해 시간 범위를 24시간으로 확장하고, API Server 용량과 제한을 검토하며, 점진적 성능 저하를 확인하고, 외부 의존성 상태를 검증하며, 과거 Error Budget 소비 패턴을 검토합니다. API Error Budget 소진은 즉각적인 변경보다 지속적인 높은 부하, 용량 제한 또는 점진적 성능 저하로 인해 발생할 수 있습니다.
