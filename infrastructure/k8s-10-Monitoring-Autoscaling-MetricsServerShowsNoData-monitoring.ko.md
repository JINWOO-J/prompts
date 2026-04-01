---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/10-Monitoring-Autoscaling/MetricsServerShowsNoData-monitoring.md)'
role: Kubernetes SRE
origin: scoutflo
extract_date: 2026-03-05
tags:
- autoscal
- autoscaling
- infrastructure
- k8s-deployment
- k8s-namespace
- k8s-node
- k8s-pod
- kubernetes
- metricsservershowsnodata
- monitoring
- performance
- scaling
---

---
title: Metrics Server Shows No Data - Metrics Server 데이터 없음
weight: 258
categories:
  - kubernetes
  - monitoring
---

# MetricsServerShowsNoData-monitoring

## 의미

Metrics Server가 리소스 메트릭을 수집하거나 보고하지 않습니다(KubeMetricsServerDown 또는 KubeMetricsServerUnavailable 알림 트리거). kube-system namespace에서 metrics-server Pod가 실행되지 않거나, 노드의 kubelet에서 메트릭을 수집할 수 없거나, API 서버 연결 문제로 메트릭 보고가 불가하거나, metrics.k8s.io/v1beta1 API에 접근할 수 없는 것이 원인입니다.

## 영향

메트릭 사용 불가, HPA가 CPU 또는 메모리 메트릭 기반 스케일링 불가, `kubectl top pod`와 `kubectl top node` 명령이 데이터 없음 또는 오류 반환, 리소스 사용량 메트릭 누락, metrics-server Pod가 실행되지 않을 때 KubeMetricsServerDown 알림 발생, 메트릭 API에 접근 불가 시 KubeMetricsServerUnavailable 알림 발생, 오토스케일링 비활성화, 리소스 모니터링 중단, 클러스터 리소스 가시성 상실. Metrics-server Pod가 CrashLoopBackOff 또는 Failed 상태로 무기한 유지되며, 애플리케이션이 자동 스케일링 불가하여 오류 또는 성능 저하가 발생할 수 있습니다.

## 플레이북

1. `kube-system` namespace에서 metrics-server Deployment를 describe하여 상태, 구성, 이벤트를 확인합니다.
2. `kube-system` namespace의 이벤트를 타임스탬프 순으로 조회하여 metrics-server 관련 실패와 수집 문제를 식별합니다.
3. kube-system namespace에서 metrics-server Pod를 나열하고 상태를 확인하여 Pod가 실행 중이고 준비 상태인지 검증합니다.
4. kube-system namespace의 metrics-server Pod `<metrics-server-pod-name>` 로그를 조회하고 오류, 수집 실패, API 연결 문제를 필터링합니다.
5. `kubectl top pod` 또는 `kubectl top node`를 실행하여 메트릭이 반환되는지 확인하여 메트릭 수집을 테스트합니다.
6. metrics-server Pod에서 API 서버 연결을 확인하여 metrics server가 API 서버 엔드포인트에 도달할 수 있는지 검증합니다.
7. metrics-server Pod에서 노드 연결을 확인하여 노드의 kubelet에서 메트릭을 수집할 수 있는지 검증합니다.

## 진단

플레이북 섹션에서 수집한 metrics-server Deployment 상태, Pod 로그, `kubectl top` 테스트 결과를 분석하는 것으로 시작합니다.

**metrics-server Pod가 Running이 아니거나 CrashLoopBackOff를 보이는 경우:**
- Metrics Server 자체가 실패하고 있습니다. Pod 로그에서 시작 오류를 확인합니다. 일반적인 원인: RBAC 권한 누락, 잘못된 명령줄 플래그, 인증서 문제.

**로그에 "unable to fetch metrics from node" 또는 kubelet 연결 오류가 표시되는 경우:**
- Metrics Server가 노드의 kubelet에 도달할 수 없습니다. `--kubelet-insecure-tls` 플래그가 필요한지 확인합니다(자체 서명 인증서 환경에서 흔함). kubelet이 실행 중이고 포트 10250에서 접근 가능한지 확인합니다.

**로그에 인증서 검증 실패가 표시되는 경우:**
- metrics-server와 kubelet 간 TLS 인증서 문제입니다. 테스트를 위해 `--kubelet-insecure-tls` 플래그를 추가하거나, kubelet 서빙 인증서를 올바르게 구성합니다.

**로그에 API 서버 연결 실패가 표시되는 경우:**
- Metrics Server가 API 서버에 등록할 수 없습니다. metrics-server 서비스 계정 RBAC 권한을 확인합니다. APIService `v1beta1.metrics.k8s.io`가 등록되어 있고 정상인지 확인합니다.

**`kubectl top`이 "metrics API not available"을 반환하는 경우:**
- 메트릭 API가 등록되지 않았습니다. APIService 존재 여부를 확인합니다: `kubectl get apiservice v1beta1.metrics.k8s.io`. 누락된 경우 metrics-server를 재설치합니다.

**metrics-server Pod가 Running이지만 HPA에 "unknown" 메트릭이 표시되는 경우:**
- 메트릭이 지연되거나 특정 메트릭을 사용할 수 없습니다. metrics-server 로그에서 수집 오류를 확인합니다. 대상 Pod에 리소스 요청이 설정되어 있는지 확인합니다(백분율 기반 HPA에 필요).

**명확한 원인이 식별되지 않는 경우:** 디버그 Pod에서 kubelet 메트릭 엔드포인트를 직접 테스트합니다: `curl -k https://<node-ip>:10250/stats/summary`. 이를 통해 문제가 kubelet 측인지 metrics-server 측인지 분리합니다.
