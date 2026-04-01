---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/05-Networking/IngressNotWorking-ingress.md)'
role: Kubernetes SRE
origin: scoutflo
extract_date: 2026-03-05
tags:
- dns
- infrastructure
- ingress
- ingressnotworking
- k8s-ingress
- k8s-namespace
- k8s-pod
- k8s-service
- kubernetes
- networking
- nginx
- performance
- sts
---

---
title: Ingress Not Working - Ingress
weight: 208
categories:
  - kubernetes
  - ingress
---

# IngressNotWorking-ingress - Ingress 작동 불가

## 의미

Ingress 리소스가 백엔드 서비스로 트래픽을 라우팅하지 않고 있으며(KubeIngressNotReady 또는 KubeIngressDown 알림 발생), Ingress Controller Namespace(일반적으로 ingress-nginx 또는 kube-system)에서 Ingress Controller Pod가 실행되지 않거나, Ingress 규칙이 잘못된 경로 또는 호스트명으로 잘못 구성되었거나, Ingress 규칙에서 참조하는 백엔드 서비스가 사용 불가능하거나 Endpoint가 없거나, Ingress 호스트명에 대한 DNS가 올바르게 구성되지 않았거나, NetworkPolicy가 Ingress Controller와 백엔드 서비스 간 트래픽을 차단하고 있는 것이 원인입니다.
kubectl에서 Ingress Controller Pod가 CrashLoopBackOff 또는 Failed 상태를 보이고, Ingress Endpoint에서 502 Bad Gateway 또는 503 Service Unavailable 오류를 반환하며, Ingress Controller 로그에 라우팅 실패 또는 백엔드 연결 오류가 표시됩니다. 이는 네트워크 계층에 영향을 미치며 외부 트래픽이 애플리케이션에 도달하는 것을 방해하고, 일반적으로 Ingress Controller 장애, 잘못 구성된 Ingress 규칙 또는 백엔드 서비스 불가용이 원인입니다. 애플리케이션이 사용자에게 접근 불가능해지며 오류가 발생할 수 있습니다.

## 영향

KubeIngressNotReady 또는 KubeIngressDown 알림 발생, Ingress Endpoint를 통해 외부 트래픽이 애플리케이션에 도달 불가, Ingress Endpoint에서 502 Bad Gateway 또는 503 Service Unavailable 오류 반환, 클러스터 외부에서 서비스 접근 불가, 애플리케이션이 사용자에게 접근 불가, Ingress Controller 로그에 라우팅 실패 및 백엔드 연결 오류 표시, 백엔드 서비스에 트래픽 미도달, Ingress 호스트에 대한 DNS 확인 실패, Ingress 상태에 주소 없음 또는 백엔드 서비스 오류 표시, 사용자 대면 서비스 완전 사용 불가. Ingress Controller Pod가 CrashLoopBackOff 또는 Failed 상태 유지, Ingress Endpoint에서 무기한 오류 반환, 애플리케이션이 사용자에게 접근 불가능해지며 오류 또는 성능 저하 발생 가능.

## 플레이북

1. `<namespace>` Namespace에서 `kubectl describe ingress <ingress-name> -n <namespace>`를 사용하여 Ingress `<ingress-name>`을 상세 조회하고, 상태, 규칙, 어노테이션, 백엔드 서비스 참조를 검사하여 설정을 확인합니다.

2. `<namespace>` Namespace에서 `kubectl get events -n <namespace> --field-selector involvedObject.name=<ingress-name> --sort-by='.lastTimestamp'`를 사용하여 이벤트를 조회하고, `Failed`, `Sync` 또는 라우팅/백엔드 오류를 나타내는 메시지에 초점을 맞춰 Ingress 관련 이벤트를 필터링합니다.

3. Ingress Controller Namespace(일반적으로 `ingress-nginx` 또는 `kube-system`)에서 IngressController Pod를 조회하고 상태와 Readiness를 확인하여 Controller가 실행 중인지 확인합니다.

4. `<namespace>` Namespace에서 Ingress Controller Pod `<controller-pod-name>`의 로그를 조회하고, Ingress 리소스, 백엔드 서비스 또는 라우팅 실패와 관련된 오류를 필터링합니다.

5. Ingress에서 백엔드로 참조된 Service `<service-name>`을 조회하고 존재 여부, Endpoint 유무, 접근 가능 여부를 확인합니다.

6. 테스트 Pod에서 Pod Exec 도구를 사용하여 Ingress 호스트명 또는 IP 주소에 `curl` 또는 `wget`을 실행하여 연결을 테스트하고 라우팅 동작을 확인합니다.

## 진단

플레이북 섹션에서 수집한 Ingress 상세 조회 출력과 이벤트를 분석하는 것부터 시작합니다. Ingress 상태, Controller Pod 상태, 백엔드 서비스 가용성이 주요 진단 신호를 제공합니다.

**Ingress Controller Pod가 Running이 아니거나 CrashLoopBackOff를 보이는 경우:**
- Ingress Controller가 중단되었습니다. 이것이 근본 원인입니다. 계속하기 전에 IngressControllerPodsCrashLooping 플레이북을 사용하여 Controller Pod 장애를 조사합니다.

**Ingress 상태에 할당된 주소가 없는 경우:**
- Ingress Controller가 이 Ingress 리소스를 처리하지 않았습니다. IngressClass가 Controller의 클래스와 일치하는지 확인합니다. Controller가 올바른 Namespace를 감시하고 있는지 확인합니다.

**백엔드 서비스에 Endpoint가 없는 경우(Ingress 상세 조회에서 표시):**
- 트래픽을 처리할 Pod가 없습니다. Service 셀렉터와 일치하는 Pod가 존재하고 Ready 상태인지 확인합니다. Service 셀렉터 레이블이 Pod 레이블과 정확히 일치하는지 확인합니다.

**curl 테스트에서 502 Bad Gateway가 반환되는 경우:**
- Controller가 Service에 도달하지만 백엔드 Pod가 응답하지 않습니다. 상세 진단을 위해 IngressReturning502BadGateway 플레이북을 따릅니다.

**curl 테스트에서 404 Not Found가 반환되는 경우:**
- 요청과 일치하는 Ingress 규칙이 없습니다. 요청의 호스트명과 경로가 Ingress 규칙과 일치하는지 확인합니다. 필요시 IngressShows404 플레이북을 따릅니다.

**Ingress 호스트명에 대한 DNS 확인이 실패하는 경우:**
- Ingress 호스트명에 대한 DNS가 구성되지 않았습니다. DNS 레코드가 Ingress Controller의 외부 IP 또는 로드 밸런서를 가리키는지 확인합니다. 이는 Kubernetes 외부 문제입니다.

**이벤트가 결론적이지 않은 경우, 타임스탬프를 상관 분석합니다:**
1. Ingress 리소스 버전 변경을 검사하여 Ingress 수정 후 라우팅 실패가 시작되었는지 확인합니다.
2. Deployment 롤아웃 타임스탬프와 비교하여 실패가 백엔드 Deployment 변경과 일치하는지 확인합니다.
3. Controller에서 백엔드로의 트래픽을 차단하는 NetworkPolicy가 추가되었는지 확인합니다.

**명확한 원인이 파악되지 않는 경우:** 디버그 Pod를 사용하여 클러스터 내부에서 백엔드 서비스를 직접 테스트하여 Ingress Controller를 우회하고, 문제가 라우팅에 있는지 백엔드 자체에 있는지 분리합니다.
