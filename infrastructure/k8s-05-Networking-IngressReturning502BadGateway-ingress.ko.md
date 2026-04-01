---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/05-Networking/IngressReturning502BadGateway-ingress.md)'
role: Kubernetes SRE
origin: scoutflo
extract_date: 2026-03-05
tags:
- infrastructure
- ingress
- ingressreturning502badgateway
- k8s-ingress
- k8s-namespace
- k8s-pod
- k8s-service
- kubernetes
- networking
- performance
---

---
title: Ingress Returning 502 Bad Gateway - Ingress
weight: 245
categories:
  - kubernetes
  - ingress
---

# IngressReturning502BadGateway-ingress - Ingress 502 Bad Gateway 반환

## 의미

Ingress 리소스가 502 Bad Gateway 오류를 반환하고 있으며(KubeIngressNotReady 또는 KubeServiceNotReady 알림 발생), Ingress 규칙에서 참조하는 백엔드 서비스에 Endpoint가 없거나, Service 셀렉터와 일치하는 Pod가 Ready 상태가 아니거나, Service 포트 설정이 Pod 컨테이너 포트와 일치하지 않거나, NetworkPolicy 또는 Pod 장애로 인해 백엔드 서비스에 접근할 수 없는 것이 원인입니다.

## 영향

Ingress Endpoint에서 502 Bad Gateway 오류 반환, 외부 트래픽이 애플리케이션에 도달 불가, 사용자에게 Bad Gateway 오류 표시, 서비스 사용 불가로 표시, Ingress Controller 로그에 백엔드 연결 실패 및 업스트림 오류 표시, Ingress가 백엔드 서비스로 라우팅할 수 없을 때 KubeIngressNotReady 알림 발생, 백엔드 서비스에 Ready Endpoint가 없을 때 KubeServiceNotReady 알림 발생, 백엔드 서비스에 Ready Endpoint 없음, 애플리케이션 트래픽 차단, Ingress 상태에 백엔드 서비스 오류 표시. Ingress Endpoint에서 무기한 502 Bad Gateway 오류 반환, 백엔드 서비스에 Endpoint 없음, 애플리케이션이 사용자에게 접근 불가능해지며 오류 또는 성능 저하 발생 가능, 사용자 대면 서비스 차단.

## 플레이북

1. `<namespace>` Namespace에서 `kubectl describe ingress <ingress-name> -n <namespace>`를 사용하여 Ingress `<ingress-name>`을 상세 조회하고, 설정, 백엔드 서비스 참조, 어노테이션을 검사하여 라우팅 규칙을 확인합니다.

2. `<namespace>` Namespace에서 `kubectl get events -n <namespace> --field-selector involvedObject.name=<ingress-name> --sort-by='.lastTimestamp'`를 사용하여 이벤트를 조회하고, `Failed`, `Sync` 또는 백엔드 연결/라우팅 오류를 나타내는 메시지에 초점을 맞춰 Ingress 관련 이벤트를 필터링합니다.

3. `<namespace>` Namespace에서 Ingress Controller Pod `<controller-pod-name>`의 로그를 조회하고, Ingress와 관련된 502 오류, 백엔드 연결 실패 또는 서비스 접근 불가 메시지를 필터링합니다.

4. Ingress에서 백엔드로 참조된 Service `<service-name>`을 조회하고 존재 여부, Endpoint 유무, 포트 설정을 확인합니다.

5. `<namespace>` Namespace에서 Service `<service-name>`의 Endpoints를 조회하고 Pod가 Endpoint로 등록되어 있고 Ready 상태인지 확인합니다.

6. 테스트 Pod에서 Pod Exec 도구를 사용하여 백엔드 서비스 Endpoint에 직접 `curl` 또는 `wget`을 실행하여 연결을 테스트하고 서비스가 내부적으로 접근 가능한지 확인합니다.

## 진단

플레이북 섹션에서 수집한 Ingress 상세 조회 출력과 백엔드 서비스 상태를 분석하는 것부터 시작합니다. Service Endpoint, 백엔드 Pod Readiness, Controller 오류 로그가 주요 진단 신호를 제공합니다.

**백엔드 서비스에 Endpoint가 없는 경우:**
- 정상 Pod가 없습니다. Service 셀렉터와 일치하는 Pod가 존재하는지 확인합니다. Pod가 존재하면 Readiness Probe를 통과하는지 확인합니다. Ingress가 트래픽을 라우팅하기 전에 Pod 상태 문제를 해결합니다.

**Endpoint가 존재하지만 Pod가 NotReady 상태인 경우:**
- Pod가 실행 중이지만 Readiness Probe에 실패하고 있습니다. Pod 로그에서 애플리케이션 시작 오류를 확인합니다. Readiness Probe 설정이 애플리케이션의 실제 헬스 엔드포인트와 일치하는지 확인합니다.

**Service 포트가 컨테이너 포트와 일치하지 않는 경우:**
- 포트 불일치로 트래픽이 애플리케이션에 도달하지 못합니다. Service `targetPort`가 애플리케이션이 수신 대기하는 컨테이너 포트와 일치하는지 확인합니다. Ingress `backend.service.port`가 Service 포트와 일치하는지 확인합니다.

**백엔드 서비스 ClusterIP에 직접 curl이 실패하는 경우:**
- 백엔드 서비스 자체에 접근할 수 없습니다. NetworkPolicy가 서비스로의 트래픽을 차단하는지 확인합니다. 애플리케이션이 예상 포트에서 수신 대기하는지 확인합니다.

**백엔드에 curl은 성공하지만 Ingress가 502를 반환하는 경우:**
- Ingress Controller가 백엔드에 접근할 수 없습니다. NetworkPolicy가 Ingress Controller Namespace에서 백엔드 Namespace로의 트래픽을 차단하는지 확인합니다. Controller가 Service DNS 이름을 확인할 수 있는지 확인합니다.

**Controller 로그에서 업스트림 연결 타임아웃이 표시되는 경우:**
- 백엔드 응답이 너무 느립니다. 백엔드 Pod 리소스 사용량에서 CPU 또는 메모리 압박을 확인합니다. 백엔드가 정당하게 더 많은 시간이 필요한 경우 Ingress 프록시 타임아웃 어노테이션을 늘립니다.

**이벤트가 결론적이지 않은 경우, 타임스탬프를 상관 분석합니다:**
1. 오류 발생 시점과 Pod 생성 타임스탬프를 비교하여 Deployment 롤아웃 후 502 오류가 시작되었는지 확인합니다.
2. 백엔드의 Pod 재시작 또는 OOM Kill과 오류가 일치하는지 확인합니다.
3. Service 또는 Endpoint 리소스가 수정되었는지 확인합니다.

**명확한 원인이 파악되지 않는 경우:** Ingress Controller Namespace의 디버그 Pod에 접속하여 백엔드 서비스에 직접 curl을 실행하여 Controller 관점에서 네트워크 연결을 테스트합니다.
