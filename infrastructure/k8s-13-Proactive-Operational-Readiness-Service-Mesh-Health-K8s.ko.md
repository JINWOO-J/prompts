---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/13-Proactive/07-Operational-Readiness/Service-Mesh-Health-K8s.md)'
role: SRE / K8s Proactive Operations
origin: scoutflo
tags:
- health
- infrastructure
- k8s-configmap
- k8s-namespace
- k8s-pod
- k8s-service
- mesh
- monitoring
- operational
- readiness
- service
---

# Service Mesh Health — 서비스 메시 상태

## 의미

서비스 메시 상태는 서비스 메시 컴포넌트가 비정상이거나 서비스 메시 연결 문제가 감지되었음을 나타냅니다(ServiceMeshUnhealthy 또는 ServiceMeshConnectivityFailed 같은 알림 발생).
 서비스 메시 상태 점검이 실패하거나, 서비스 메시 연결이 손상되거나, 서비스 메시 구성 오류가 발생하거나, 서비스 메시 모니터링에서 문제가 감지되거나, 서비스 메시 컴포넌트가 사용 불가한 것이 원인입니다. 서비스 메시 상태 점검에서 실패가 나타나고, 서비스 메시 연결이 손상되며, 서비스 메시 구성 오류가 감지되고, 서비스 메시 모니터링에서 문제가 표시됩니다. 이는 의존성 관리 계층과 서비스 메시 신뢰성에 영향을 미치며, 일반적으로 서비스 메시 컴포넌트 실패, 서비스 메시 구성 문제, 서비스 메시 연결 문제, 또는 서비스 메시 모니터링 실패로 인해 발생합니다. 서비스 메시 상태가 컨테이너 워크로드에 영향을 미치면 컨테이너 서비스 메시가 비정상이고 애플리케이션에서 서비스 메시 관련 실패가 발생할 수 있습니다.

## 영향

ServiceMeshUnhealthy 알림 발생, ServiceMeshConnectivityFailed 알림 발생, 서비스 메시 상태 확인 불가, 서비스 메시 연결 문제 감지, 서비스 메시 신뢰성 저하, 서비스 간 통신 실패 가능. 서비스 메시 상태 점검에서 실패가 나타나며, 서비스 메시 상태가 컨테이너 워크로드에 영향을 미치면 컨테이너 서비스 메시가 비정상이고, Pod 서비스 메시 연결이 실패하며, 컨테이너 애플리케이션에서 서비스 메시 관련 실패가 발생할 수 있습니다. 애플리케이션에서 서비스 통신 실패 또는 서비스 메시 상태 문제가 발생할 수 있습니다.

## 플레이북

1. <service-mesh-namespace> 네임스페이스에서 app=istiod 레이블의 Pod를 wide 출력으로 조회하여 서비스 메시 컨트롤 플레인 Pod 상태를 확인하고 컨트롤 플레인 컴포넌트 상태를 검증합니다.
2. <service-mesh-namespace> 네임스페이스의 최근 이벤트를 타임스탬프 순으로 조회하여 서비스 메시 컴포넌트 실패, 연결 오류, 구성 문제를 확인합니다.
3. 네임스페이스 <namespace>의 ConfigMap <service-mesh-configmap-name>을 상세 조회하여 서비스 메시 구성을 확인하고 메시 상태 설정 및 컴포넌트 가용성을 검증합니다.
4. 지난 24시간 동안의 서비스 메시에 대한 Prometheus 메트릭(mesh_health_status, service_connectivity_status 포함)을 조회하여 서비스 메시 상태 문제를 확인합니다.
5. 네임스페이스 `<namespace>`의 서비스 메시 컨트롤 플레인 Pod 로그를 조회하고 지난 24시간 이내의 서비스 메시 상태 점검 실패 또는 연결 오류 패턴을 필터링합니다.
6. 서비스 메시 VirtualService `<virtual-service-name>` 구성을 조회하고 VirtualService 상태 및 라우팅 구성을 확인합니다.
7. 서비스 메시 상태 점검 실패 타임스탬프와 서비스 메시 컴포넌트 오류 타임스탬프를 5분 이내로 비교하고, 서비스 메시 구성 데이터를 보조 증거로 사용하여 컴포넌트 오류가 상태 점검 실패를 유발하는지 확인합니다.
8. 지난 24시간 동안의 서비스 메시에 대한 Prometheus 메트릭(request_count, error_rate 포함)을 조회하여 서비스 메시 성능 문제를 확인합니다.
9. 서비스 메시 라우트를 조회하고 라우트 상태 및 대상 서비스 가용성을 확인합니다.

## 진단

1. 1단계의 컨트롤 플레인 Pod 상태를 검토합니다. istiod 또는 기타 컨트롤 플레인 Pod가 실행되지 않거나 오류를 보이면 이것이 서비스 메시 상태 문제의 근본 원인입니다. 컨트롤 플레인 기능 복구에 집중합니다.

2. 4단계의 메시 상태 메트릭을 분석합니다. mesh_health_status에서 비정상이 나타나거나 service_connectivity_status에서 실패가 나타나면 메트릭 레이블을 기반으로 어떤 특정 컴포넌트나 서비스가 영향을 받는지 확인합니다.

3. 5단계의 컨트롤 플레인 로그에서 상태 점검 실패 또는 연결 오류가 나타나면 오류 패턴을 확인하여 문제가 인증 관련, 구성 관련, 또는 네트워크 관련인지 판단합니다.

4. 6단계의 VirtualService 상태를 검토합니다. VirtualService에서 잘못된 구성이 나타나면 라우팅이 실패할 수 있습니다. VirtualService가 정상이면 기본 연결이 문제입니다.

5. 8단계의 요청 메트릭에서 높은 오류율이나 성능 저하가 나타나면 서비스 메시가 작동하지만 저하된 상태입니다. 메트릭에서 트래픽이 없으면 연결이 완전히 끊어진 것입니다.

분석이 결론에 도달하지 못하는 경우: 2단계의 이벤트에서 컴포넌트 실패나 구성 문제를 확인합니다. 9단계의 라우트 상태를 검토하여 대상 서비스가 사용 가능한지 확인합니다. 상태 문제가 모든 서비스에 영향을 미치는지(컨트롤 플레인 문제 시사) 또는 특정 서비스에만 영향을 미치는지(해당 서비스의 구성 또는 네트워크 문제 시사) 판단합니다.
