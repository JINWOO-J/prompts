---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/05-Networking/NginxIngressDown-ingress.md)'
role: Kubernetes SRE
origin: scoutflo
extract_date: 2026-03-05
tags:
- dns
- infrastructure
- ingress
- k8s-configmap
- k8s-deployment
- k8s-ingress
- k8s-namespace
- k8s-node
- k8s-pod
- k8s-service
- kubernetes
- networking
- nginx
- nginxingressdown
---

---
title: Nginx Ingress Down
weight: 50
categories: [kubernetes, ingress]
---

# NginxIngressDown - Nginx Ingress 중단

## 의미

Nginx Ingress Controller가 실행되지 않거나 응답하지 않는 상태(NginxIngressDown, NginxIngressControllerDown 알림 발생)로, Ingress Controller Pod가 크래시하거나, 스케줄링되지 않거나, 정상이 아닌 것이 원인입니다. Ingress Controller Deployment에서 Ready 레플리카가 0이고, Ingress 트래픽이 라우팅되지 않으며, 모든 HTTP/HTTPS Endpoint에 접근할 수 없습니다. 모든 Ingress 라우팅 트래픽에 영향을 미치며, 서비스에 대한 외부 접근이 차단되고, 클러스터가 외부 사용자에게 사실상 오프라인 상태입니다.

## 영향

NginxIngressDown 알림 발생, 모든 Ingress 트래픽 중단, 외부 사용자가 어떤 서비스에도 접근 불가, HTTP 및 HTTPS Endpoint에서 connection refused 또는 타임아웃 반환, 로드 밸런서 헬스 체크 실패, DNS 기반 페일오버 트리거 가능, Ingress 라우팅 애플리케이션의 완전한 서비스 중단, 고객 대면 서비스의 매출 손실.

## 플레이북

1. ingress-nginx Namespace에서 ingress-nginx Deployment를 조회하고 레플리카 상태를 확인합니다.

2. Ingress Controller Pod 상태, 재시작 횟수, 장애 사유에 대한 이벤트를 확인합니다.

3. 설정 오류 또는 런타임 장애에 대한 Ingress Controller 로그를 조회합니다.

4. Nginx용 ConfigMap 설정이 유효하고 손상되지 않았는지 확인합니다.

5. Pod 작동을 방해하는 리소스 제약(CPU, 메모리)을 확인합니다.

6. LoadBalancer 또는 NodePort Service가 Controller를 올바르게 노출하는지 확인합니다.

7. Admission Webhook 실패가 Controller 작동을 방해하는지 확인합니다.

## 진단

Controller Pod 상태를 분석하고 Pod가 CrashLooping(설정 오류), Pending(스케줄링 문제) 또는 종료됨(리소스 문제)인지 파악하고, Pod 상태와 이벤트를 근거로 확인합니다.

로그에서 설정 리로드 오류를 확인하여 Nginx 설정 유효성을 검증하고, Controller 로그와 Nginx 오류 메시지를 근거로 확인합니다.

Ingress 리소스에 리로드 시 Controller 장애를 유발하는 잘못된 설정이 없는지 확인하고, 최근 Ingress 변경과 설정 검증을 근거로 확인합니다.

Ingress 라우트 수에 비해 Controller 메모리가 부족한 경우 OOMKilled 이벤트를 확인하고, 컨테이너 상태와 메모리 메트릭을 근거로 확인합니다.

Webhook 실패가 Ingress 업데이트와 잠재적으로 Controller 작동을 차단할 수 있으므로 Admission Webhook이 정상인지 확인하고, Webhook Pod 상태와 API Server 로그를 근거로 확인합니다.

지정된 시간 범위 내에서 상관관계가 발견되지 않으면: 최근 Ingress 설정 변경을 롤백하고, Controller Pod를 재시작하고, 리소스 제한을 늘리고, 충돌하는 Ingress 리소스를 확인하고, LoadBalancer Service가 올바르게 프로비저닝되었는지 확인합니다.
