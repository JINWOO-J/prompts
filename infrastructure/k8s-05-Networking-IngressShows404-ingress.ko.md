---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/05-Networking/IngressShows404-ingress.md)'
role: Kubernetes SRE
origin: scoutflo
extract_date: 2026-03-05
tags:
- infrastructure
- ingress
- ingressshows404
- k8s-ingress
- k8s-namespace
- k8s-service
- kubernetes
- networking
- performance
- sts
---

---
title: Ingress Shows 404 - Ingress
weight: 230
categories:
  - kubernetes
  - ingress
---

# IngressShows404-ingress - Ingress 404 반환

## 의미

Ingress 리소스가 404 Not Found 오류를 반환하고 있으며(KubeIngressNotReady 알림 발생), Ingress 라우팅 규칙이 요청 경로 또는 호스트명과 일치하지 않거나, 백엔드 서비스 경로 설정이 잘못되었거나, Ingress Controller가 요청된 URL에 대한 일치하는 규칙을 찾을 수 없거나, Ingress 규칙에서 참조하는 백엔드 서비스가 올바르게 구성되지 않은 것이 원인입니다.

## 영향

Ingress Endpoint에서 404 Not Found 오류 반환, 사용자에게 Not Found 오류 표시, 트래픽이 애플리케이션에 도달 불가, Ingress 라우팅 실패, Ingress Controller 로그에 요청된 경로 또는 호스트명에 대한 일치 규칙 없음 표시, Ingress가 요청을 성공적으로 라우팅할 수 없을 때 KubeIngressNotReady 알림 발생, 애플리케이션 Endpoint 접근 불가, URL 경로가 Ingress 규칙과 불일치, Ingress 상태에 라우팅 설정 오류 표시, 특정 애플리케이션 경로에 대한 외부 접근 실패. Ingress Endpoint에서 무기한 404 Not Found 오류 반환, Ingress Controller 로그에 일치 규칙 없음 표시, 애플리케이션이 사용자에게 접근 불가능해지며 오류 또는 성능 저하 발생 가능, 특정 애플리케이션 경로에 대한 외부 접근 실패.

## 플레이북

1. `<namespace>` Namespace에서 `kubectl describe ingress <ingress-name> -n <namespace>`를 사용하여 Ingress `<ingress-name>`을 상세 조회하고, 규칙, 경로, 어노테이션, 백엔드 서비스 참조를 검사하여 라우팅 설정을 확인합니다.

2. `<namespace>` Namespace에서 `kubectl get events -n <namespace> --field-selector involvedObject.name=<ingress-name> --sort-by='.lastTimestamp'`를 사용하여 이벤트를 조회하고, `Sync`, `Failed` 또는 라우팅/경로 매칭 오류를 나타내는 메시지에 초점을 맞춰 Ingress 관련 이벤트를 필터링합니다.

3. `<namespace>` Namespace에서 Ingress Controller Pod `<controller-pod-name>`의 로그를 조회하고, Ingress와 관련된 404 오류, 일치 규칙 없음 또는 라우팅 실패 메시지를 필터링합니다.

4. 요청 경로가 Ingress 규칙 경로와 일치하는지, 경로 매칭 규칙(exact, prefix)이 올바르게 구성되어 있는지 확인합니다.

5. Ingress에서 백엔드로 참조된 Service `<service-name>`을 조회하고 존재 여부와 접근 가능 여부를 확인합니다.

6. 테스트 Pod에서 Pod Exec 도구를 사용하여 Ingress 호스트명과 경로에 `curl` 또는 `wget`을 실행하여 라우팅 동작을 테스트하고 어떤 경로가 접근 가능한지 확인합니다.

## 진단

플레이북 섹션에서 수집한 Ingress 상세 조회 출력과 Controller 로그를 분석하는 것부터 시작합니다. Ingress 규칙, 경로 매칭 설정, 요청 경로 비교가 주요 진단 신호를 제공합니다.

**요청된 호스트명과 일치하는 Ingress 규칙이 없는 경우:**
- 요청의 호스트명이 어떤 Ingress `host` 필드와도 일치하지 않습니다. 요청에 사용된 정확한 호스트명을 확인합니다. Ingress에 이 호스트명에 대한 규칙이 있거나 와일드카드 호스트를 사용하는지 확인합니다.

**Ingress에 규칙이 있지만 요청된 경로와 일치하는 것이 없는 경우:**
- 요청의 경로가 어떤 Ingress 경로 규칙과도 일치하지 않습니다. 정확한 요청 경로와 Ingress 경로 규칙을 비교합니다. Ingress가 `Exact` pathType을 사용하지만 요청에 후행 슬래시가 있거나 그 반대인지 확인합니다.

**Ingress가 `Prefix` pathType을 사용하고 하위 경로에서 404를 반환하는 경우:**
- 백엔드 애플리케이션이 전체 경로를 처리하지 못할 수 있습니다. 백엔드로 전달하기 전에 경로 접두사를 제거하기 위해 Ingress에 `nginx.ingress.kubernetes.io/rewrite-target` 어노테이션이 필요한지 확인합니다.

**Ingress가 최근 생성되었지만 404를 반환하는 경우:**
- Ingress Controller가 아직 이 Ingress를 처리하지 않았을 수 있습니다. Ingress 상태에서 할당된 주소를 확인합니다. Controller 로그에서 이 Ingress와 관련된 동기화 오류를 확인합니다.

**Ingress에 Controller와 일치하지 않는 IngressClass가 있는 경우:**
- Controller가 이 Ingress를 무시하고 있습니다. `spec.ingressClassName`이 실행 중인 Controller가 감시하는 IngressClass와 일치하는지 확인합니다. Controller 시작 인수에서 클래스 필터링을 확인합니다.

**백엔드 서비스가 존재하지만 애플리케이션이 404를 반환하는 경우:**
- 트래픽이 애플리케이션에 도달하지만 애플리케이션에 해당 경로에 대한 핸들러가 없습니다. 이는 Ingress 문제가 아닌 애플리케이션 문제입니다. 애플리케이션 라우트가 Ingress가 전달하는 것과 일치하는지 확인합니다.

**이벤트가 결론적이지 않은 경우, 타임스탬프를 상관 분석합니다:**
1. Ingress 리소스 버전을 검사하여 Ingress 경로 변경 후 404 오류가 시작되었는지 확인합니다.
2. 백엔드 Deployment가 라우팅 설정을 변경했는지 확인합니다.
3. Ingress Controller가 재시작되어 설정을 잃었는지 확인합니다.

**명확한 원인이 파악되지 않는 경우:** `kubectl get ingress -A -o wide`를 사용하여 모든 Ingress 리소스와 주소를 조회합니다. Ingress Controller의 기본 백엔드 설정이 일치하지 않는 요청을 처리하는지 확인합니다.
