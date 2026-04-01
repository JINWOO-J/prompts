---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/13-Proactive/07-Operational-Readiness/API-Dependency-Status-K8s.md)'
role: SRE / K8s Proactive Operations
origin: scoutflo
tags:
- dependency
- infrastructure
- k8s-namespace
- k8s-pod
- k8s-service
- monitoring
- operational
- performance
- readiness
- status
---

# API Dependency Status — API 의존성 상태

## 의미

API 의존성 상태는 API 의존성이 사용 불가하거나 API 의존성 상태 문제가 감지되었음을 나타냅니다(APIDependencyUnavailable 또는 APIDependencyHealthFailed 같은 알림 발생).
 API 의존성 상태 점검이 실패하거나, API 의존성 연결이 손상되거나, API 의존성 응답 시간이 임계값을 초과하거나, API 의존성 오류율이 높거나, API 의존성 모니터링에서 문제가 감지되는 것이 원인입니다. API 의존성 상태 점검에서 실패가 나타나고, API 의존성 연결이 손상되며, API 의존성 응답 시간이 높고, API 의존성 모니터링에서 문제가 표시됩니다. 이는 의존성 관리 계층과 API 신뢰성에 영향을 미치며, 일반적으로 API 의존성 서비스 비가용, API 의존성 연결 문제, API 의존성 성능 문제, 또는 API 의존성 모니터링 실패로 인해 발생합니다. API 의존성이 컨테이너 워크로드에 영향을 미치면 컨테이너 API 호출이 실패하고 애플리케이션에서 API 의존성 관련 실패가 발생할 수 있습니다.

## 영향

APIDependencyUnavailable 알림 발생, APIDependencyHealthFailed 알림 발생, API 의존성 상태 확인 불가, API 의존성 연결 문제 감지, API 신뢰성 저하, API 호출 실패 가능. API 의존성 상태 점검에서 실패가 나타나며, API 의존성이 컨테이너 워크로드에 영향을 미치면 컨테이너 API 호출이 실패하고, Pod API 의존성이 사용 불가하며, 컨테이너 애플리케이션에서 API 의존성 관련 실패가 발생할 수 있습니다. 애플리케이션에서 API 호출 실패 또는 API 의존성 상태 문제가 발생할 수 있습니다.

## 플레이북

1. 네임스페이스 <namespace>의 Service <service-name>을 상세 조회하여 서비스 엔드포인트 상태와 백엔드 서비스 연결을 확인합니다.

2. 네임스페이스 <namespace>의 최근 이벤트를 타임스탬프 순으로 조회하여 최근 API 의존성 문제나 서비스 변경을 확인합니다.

3. 네임스페이스 <namespace>의 Endpoints <service-name>을 YAML 출력으로 조회하여 백엔드 Pod 연결 및 상태를 확인합니다.

4. 네임스페이스 <namespace>에서 app=<app-name> 레이블의 애플리케이션 Pod 로그를 조회하고 API 의존성 오류 패턴 또는 타임아웃 패턴을 필터링합니다.

5. 지난 24시간 동안의 서비스 API에 대한 Prometheus 메트릭(4xx_error_rate, 5xx_error_rate, latency 포함)을 조회하여 API 의존성 상태 문제를 확인합니다.

6. API 호출에 대한 서비스 메시 트레이스 데이터를 조회하고 트레이스 세그먼트를 분석하여 API 의존성 응답 시간과 오류율을 확인합니다.

7. 지난 24시간 동안의 서비스 API에 대한 Prometheus 메트릭(integration_latency, backend_latency 포함)을 조회하여 API 의존성 성능 문제를 확인합니다.

8. 서비스 API에 대한 활성 Prometheus 알림(firing 상태)을 조회하고 알림 상태가 API 의존성 상태 문제를 나타내는지 확인합니다.

## 진단

1. 1단계와 3단계의 엔드포인트 상태를 검토합니다. 엔드포인트에서 비정상 백엔드나 누락된 주소가 나타나면 API 의존성 연결이 끊어진 것입니다. 백엔드 Pod 상태와 네트워크 정책을 확인합니다.

2. 5단계의 API 오류율 메트릭을 분석합니다. 4xx 오류가 높으면 클라이언트 측 요청 문제가 존재합니다. 5xx 오류가 높으면 백엔드 서비스 실패가 발생하고 있습니다. 오류 유형에 따라 해결에 집중합니다.

3. 4단계의 애플리케이션 로그에서 타임아웃 패턴이 나타나면 API 의존성 응답 시간이 클라이언트 타임아웃을 초과하는 것입니다. 7단계의 지연 시간 메트릭을 검토하여 백엔드 지연인지 통합 지연인지 확인합니다.

4. 6단계의 트레이스 데이터를 검토합니다. 트레이스 분석에서 특정 API 엔드포인트의 높은 오류율이나 지연이 나타나면 해당 엔드포인트에 조사를 집중합니다. 모든 엔드포인트가 영향을 받으면 서비스 전체 문제입니다.

5. 8단계의 알림에서 API 서비스에 대해 발생하고 있으면 알림이 문제를 정확히 감지하고 있습니다. 상태 문제에도 알림이 발생하지 않으면 알림 임계값 조정이 필요합니다.

분석이 결론에 도달하지 못하는 경우: 2단계의 이벤트에서 API 서비스 변경이나 엔드포인트 업데이트를 확인합니다. 상태 문제가 모든 API 소비자에 영향을 미치는지(서버 측 문제 시사) 또는 특정 소비자에만 영향을 미치는지(클라이언트 측 또는 네트워크 문제 시사) 판단합니다. API 의존성 상태 점검에 적절한 타임아웃과 임계값이 설정되어 있는지 확인합니다.
