---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/05-Networking/IngressRedirectLoop-ingress.md)'
role: Kubernetes SRE
origin: scoutflo
extract_date: 2026-03-05
tags:
- infrastructure
- ingress
- ingressredirectloop
- k8s-ingress
- k8s-namespace
- k8s-service
- kubernetes
- networking
- nginx
- performance
- sts
---

---
title: Ingress Redirect Loop - Ingress
weight: 298
categories:
  - kubernetes
  - ingress
---

# IngressRedirectLoop-ingress - Ingress 리다이렉트 루프

## 의미

Ingress 리소스가 리다이렉트 루프를 유발하고 있으며(KubeIngressNotReady 알림 발생), 잘못 구성된 Ingress 규칙이 트래픽을 동일 경로로 리다이렉트하거나, 백엔드 서비스가 다른 Ingress 규칙과 일치하는 경로로 리다이렉트하거나, SSL/TLS 리다이렉트 어노테이션(nginx.ingress.kubernetes.io/ssl-redirect)이 순환 리다이렉트를 생성하는 것이 원인입니다.
Ingress Endpoint에서 무한 리다이렉트 발생, Ingress Controller 로그에 리다이렉트 루프 및 순환 리다이렉트 패턴 표시, 브라우저에서 리다이렉트 루프 오류 표시. 이는 네트워크 계층에 영향을 미치며 외부 트래픽이 애플리케이션에 도달하는 것을 방해하고, 일반적으로 잘못 구성된 Ingress 리다이렉트 규칙 또는 SSL/TLS 리다이렉트 충돌이 원인입니다. 애플리케이션이 사용자에게 접근 불가능해지며 오류가 발생할 수 있습니다.

## 영향

Ingress Endpoint에서 무한 리다이렉트 발생, 브라우저에서 리다이렉트 루프 오류 표시, 요청이 완료되지 않음, 애플리케이션 접근 불가, Ingress Controller 로그에 리다이렉트 루프 및 순환 리다이렉트 패턴 표시, Ingress가 트래픽을 성공적으로 라우팅할 수 없을 때 KubeIngressNotReady 알림 발생, 사용자 트래픽 차단, SSL/TLS 리다이렉트가 루프 생성, Ingress 상태에 라우팅 실패 표시, 애플리케이션에 대한 외부 접근 완전 실패. Ingress Endpoint에서 무기한 무한 리다이렉트 발생, Ingress Controller 로그에 리다이렉트 루프 표시, 애플리케이션이 사용자에게 접근 불가능해지며 오류 또는 성능 저하 발생 가능, 애플리케이션에 대한 외부 접근 완전 실패.

## 플레이북

1. `<namespace>` Namespace에서 `kubectl describe ingress <ingress-name> -n <namespace>`를 사용하여 Ingress `<ingress-name>`을 상세 조회하고, 규칙, 어노테이션, 리다이렉트 설정을 검사하여 잠재적 루프 원인을 파악합니다.

2. `<namespace>` Namespace에서 `kubectl get events -n <namespace> --field-selector involvedObject.name=<ingress-name> --sort-by='.lastTimestamp'`를 사용하여 이벤트를 조회하고, `Sync`, `Failed` 또는 리다이렉트/라우팅 문제를 나타내는 메시지에 초점을 맞춰 Ingress 관련 이벤트를 필터링합니다.

3. `<namespace>` Namespace에서 Ingress Controller Pod `<controller-pod-name>`의 로그를 조회하고, 리다이렉트 루프 오류, 순환 리다이렉트 메시지 또는 라우팅 충돌을 필터링합니다.

4. SSL/TLS 리다이렉트 설정에 대한 Ingress 어노테이션(예: `nginx.ingress.kubernetes.io/ssl-redirect`, `cert-manager.io/issuer`)을 확인하고 리다이렉트가 루프를 생성하는지 확인합니다.

5. `<namespace>` Namespace의 모든 Ingress 리소스를 조회하고, 리다이렉트 루프를 유발할 수 있는 충돌하는 규칙 또는 겹치는 경로를 확인합니다.

6. 테스트 Pod에서 Pod Exec 도구를 사용하여 리다이렉트 추적을 비활성화한 `curl`을 실행하여 리다이렉트 경로를 추적하고 루프가 발생하는 위치를 파악합니다.

## 진단

플레이북 섹션에서 수집한 Ingress 상세 조회 출력과 curl 추적 결과를 분석하는 것부터 시작합니다. Ingress 어노테이션, TLS 설정, 리다이렉트 경로 추적이 주요 진단 신호를 제공합니다.

**Ingress에 `nginx.ingress.kubernetes.io/ssl-redirect: "true"`가 있고 백엔드도 HTTPS로 리다이렉트하는 경우:**
- Ingress와 애플리케이션 모두 HTTPS를 강제하여 루프가 생성됩니다. TLS 종료가 Ingress Controller에서 이루어지므로 Ingress에서 `nginx.ingress.kubernetes.io/ssl-redirect: "false"`를 설정합니다.

**curl 추적에서 HTTP→HTTPS 리다이렉트 후 HTTPS→HTTP 리다이렉트가 표시되는 경우:**
- 백엔드 애플리케이션이 HTTP로 리다이렉트하는 반면 Ingress는 HTTPS를 강제합니다. 백엔드가 리다이렉트에서 HTTPS URL을 사용하도록 구성하거나, `X-Forwarded-Proto`와 같은 적절한 헤더를 설정하여 백엔드에 TLS 종료 뒤에 있음을 알립니다.

**여러 Ingress 리소스가 서로 다른 리다이렉트 규칙으로 동일 호스트명과 일치하는 경우:**
- 충돌하는 Ingress 리소스가 루프를 유발합니다. 해당 호스트명과 일치하는 모든 Ingress 리소스를 조회하고 리다이렉트 규칙을 단일 Ingress로 통합하거나 경로가 겹치지 않도록 합니다.

**curl 추적에서 서로 다른 Ingress 규칙과 일치하는 경로 간 리다이렉트가 표시되는 경우:**
- 경로 기반 라우팅이 리다이렉트 순환을 생성합니다. 해당 호스트명의 모든 Ingress 경로 규칙을 검토합니다. 애플리케이션 리다이렉트가 동일 백엔드에서 처리하는 경로를 대상으로 하도록 하거나 Ingress 경로 매칭을 조정합니다.

**백엔드 애플리케이션이 자체 리다이렉트 로직을 구현하는 경우:**
- 애플리케이션의 리다이렉트 URL이 Ingress 라우팅과 충돌합니다. 애플리케이션 설정에서 리다이렉트 URL을 확인합니다. 리다이렉트가 Ingress가 기대하는 올바른 프로토콜과 호스트명을 사용하는지 확인합니다.

**이벤트가 결론적이지 않은 경우, 타임스탬프를 상관 분석합니다:**
1. Ingress 수정 이력을 검사하여 TLS 설정 또는 ssl-redirect 어노테이션 추가 후 루프가 시작되었는지 확인합니다.
2. 동일 호스트명에 대한 새 Ingress 생성 후 루프가 시작되었는지 확인합니다.
3. 백엔드 Deployment 변경이 애플리케이션 수준 리다이렉트를 도입했는지 확인합니다.

**명확한 원인이 파악되지 않는 경우:** 일시적으로 ssl-redirect를 비활성화하고 HTTP만으로 테스트하여 문제가 TLS 관련인지 분리합니다. `curl -L -v --max-redirs 10`을 사용하여 전체 리다이렉트 체인을 캡처하고 정확한 루프 패턴을 추적합니다.
