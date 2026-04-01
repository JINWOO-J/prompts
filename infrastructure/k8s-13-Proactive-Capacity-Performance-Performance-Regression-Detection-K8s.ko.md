---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/13-Proactive/01-Capacity-Performance/Performance-Regression-Detection-K8s.md)'
role: SRE / K8s Proactive Operations
origin: scoutflo
tags:
- capacity
- detection
- infrastructure
- k8s-deployment
- k8s-namespace
- k8s-pod
- monitoring
- performance
- regression
---

# Performance Regression Detection (성능 회귀 감지)

## 의미

성능 회귀 감지 알림은 성능 회귀가 감지되거나 성능 베이스라인 비교가 실패하는 상황(PerformanceRegressionDetected 또는 BaselineComparisonFailed 같은 알림 발생)을 나타냅니다. 성능 메트릭이 베이스라인 임계값 초과, 성능 회귀 분석 도구 실패, 성능 베이스라인 비교의 회귀 표시, 성능 추세 분석의 저하 표시, 또는 성능 회귀 모니터링의 문제 감지 등이 원인입니다.
 성능 회귀가 감지되고, 성능 베이스라인 비교가 실패를 보이며, 성능 메트릭이 임계값을 초과하고, 성능 회귀 분석이 실패합니다. 이는 성능 모니터링 계층과 애플리케이션 성능에 영향을 미치며, 주로 성능 저하, 베이스라인 임계값 설정 오류, 성능 회귀 분석 도구 실패, 또는 성능 모니터링 문제가 원인입니다. 성능 회귀가 컨테이너 워크로드에 영향을 미치는 경우, 컨테이너 성능이 저하되고 애플리케이션이 성능 문제를 겪을 수 있습니다.

## 영향

PerformanceRegressionDetected 알림 발생, BaselineComparisonFailed 알림 발생, 성능 회귀 감지, 성능 베이스라인 비교 실패, 애플리케이션 성능 저하 가능, 사용자 경험 영향 가능. 성능 회귀가 감지됩니다. 성능 회귀가 컨테이너 워크로드에 영향을 미치는 경우, 컨테이너 성능이 저하되고, Pod 성능이 회귀하며, 컨테이너 애플리케이션이 성능 문제를 겪을 수 있습니다. 애플리케이션이 성능 저하나 사용자 경험 영향을 경험할 수 있습니다.

## 플레이북

1. namespace <namespace>에서 Deployment <deployment-name>을 describe하여 배포 설정, 리소스 할당, 성능 회귀와 상관관계가 있을 수 있는 최근 변경사항을 점검합니다.
2. namespace <namespace>에서 최근 이벤트를 타임스탬프 순으로 조회하여 성능 관련 문제나 배포 변경을 나타내는 이벤트를 확인합니다.
3. 서비스 <service-name>의 Prometheus 메트릭(latency, throughput, error_rate)을 최근 7일 동안 조회하고 성능 베이스라인 메트릭과 비교하여 성능 회귀를 식별합니다.
4. 서비스 <service-name>의 성능 베이스라인 설정을 조회하고 베이스라인 임계값 설정과 비교 기준을 확인하여 베이스라인 설정을 점검합니다.
5. 성능 모니터링 Pod의 로그를 조회하고 최근 7일 내 성능 회귀 패턴이나 베이스라인 비교 실패를 필터링합니다.
6. 서비스 <service-name>의 서비스 메시 트레이스 데이터를 조회하고 트레이스 성능 메트릭을 분석하여 성능 회귀 패턴을 식별합니다.
7. 성능 회귀 감지 타임스탬프와 Pod 배포 타임스탬프를 1시간 이내로 비교하여 배포가 성능 회귀를 유발하는지 확인하고, Prometheus 메트릭을 보조 증거로 활용합니다.
8. 성능 회귀 분석 결과를 조회하고 회귀 심각도와 영향 평가를 확인하여 중요 성능 회귀를 식별합니다.

## 진단

1. 3단계의 성능 메트릭(latency, throughput, error_rate)을 검토하고 베이스라인과 비교합니다. 현재 메트릭이 베이스라인 임계값을 상당히 초과하면(예: >20%) 실제 성능 회귀가 발생한 것입니다.

2. 1단계의 배포 설정을 분석합니다. 최근 변경이 성능 저하와 상관관계가 있으면 배포 변경이 유력한 원인입니다. 최근 변경이 없으면 외부 요인(부하, 의존성)이 원인일 수 있습니다.

3. 5단계의 성능 모니터링 로그에서 회귀 패턴이 있으면 영향받는 특정 메트릭과 서비스를 식별합니다. 로그에 베이스라인 비교 실패가 있으면 모니터링 인프라에 주의가 필요합니다.

4. 6단계의 트레이스 수준 성능을 검토합니다. 트레이스 분석에서 특정 서비스 스팬의 높은 지연이 보이면 해당 서비스에 조사를 집중합니다. 지연이 스팬 전체에 분산되어 있으면 체계적 문제가 존재합니다.

5. 8단계의 회귀 심각도 평가에서 중요 회귀가 있으면 즉시 조치를 우선합니다. 회귀가 경미하면 다음 유지보수 윈도우에 조사를 예약합니다.

분석이 결론에 이르지 못하면: 2단계의 이벤트에서 배포 변경이나 리소스 제약 경고를 확인합니다. 4단계의 베이스라인 설정을 검토하여 임계값이 적절히 보정되었는지 확인합니다. 회귀가 특정 배포 이벤트나 트래픽 패턴과 상관관계가 있는지 판단합니다.
