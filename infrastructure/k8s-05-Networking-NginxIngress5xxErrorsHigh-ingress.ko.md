---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/05-Networking/NginxIngress5xxErrorsHigh-ingress.md)'
role: Kubernetes SRE
origin: scoutflo
extract_date: 2026-03-05
tags:
- infrastructure
- ingress
- k8s-ingress
- k8s-pod
- k8s-service
- kubernetes
- networking
- nginx
- nginxingress5xxerrorshigh
- sts
---

---
title: Nginx Ingress 5xx Errors High
weight: 51
categories: [kubernetes, ingress]
---

# NginxIngress5xxErrorsHigh - Nginx Ingress 5xx 오류 높음

## 의미

Nginx Ingress에서 높은 비율의 5xx 서버 오류가 반환되고 있으며(NginxIngress5xxErrorsHigh, NginxIngressHighErrorRate 알림 발생), 백엔드 서비스가 실패하거나, 사용 불가능하거나, 타임아웃되는 것이 원인입니다. Ingress 메트릭에서 5xx 응답이 증가하고, 사용자가 서버 오류를 경험하며, 백엔드 서비스 상태가 저하되었습니다. 사용자 경험과 서비스 안정성에 영향을 미치며, 요청이 실패하고, SLO 위반이 발생하며, 고객 영향이 큽니다.

## 영향

NginxIngress5xxErrorsHigh 알림 발생, 사용자에게 500, 502, 503 또는 504 오류 표시, API 호출 실패, 애플리케이션 기능 중단, 모바일 앱 실패, 연동 중단, 고객 불만 증가, 매출 영향, SLA 위반 가능, 오류율 SLO 위반.

## 플레이북

1. Ingress Controller 메트릭을 조회하고 어떤 백엔드 서비스가 5xx 오류를 생성하는지 파악합니다.

2. HTTP 상태 코드별 오류 분석(500=서버 오류, 502=Bad Gateway, 503=서비스 사용 불가, 504=Gateway 타임아웃)을 수행합니다.

3. 오류를 반환하는 서비스의 백엔드 서비스 Pod 상태와 Readiness를 확인합니다.

4. 영향받는 Ingress로 필터링된 Ingress Controller 로그를 조회하고 업스트림 연결 실패를 확인합니다.

5. 백엔드 서비스 Endpoint가 존재하고 Pod가 Ready 상태인지 확인합니다.

6. 500 응답을 유발하는 애플리케이션 오류에 대해 백엔드 Pod 로그를 확인합니다.

7. 타임아웃 설정과 프록시 동작에 대한 Ingress 어노테이션을 확인합니다.

## 진단

오류 코드 분포 분석: 502는 백엔드 연결 실패, 503은 정상 백엔드 없음, 504는 타임아웃, 500은 애플리케이션 오류를 나타내며, 오류 코드 메트릭을 근거로 확인합니다.

502 오류의 경우, 백엔드 Pod가 실행 중이고 Ingress와 백엔드 간 네트워크 연결이 존재하는지 확인하고, Pod 상태와 네트워크 테스트를 근거로 확인합니다.

503 오류의 경우, Service Endpoint를 확인하고 Pod가 Ready 상태(Readiness Probe 통과)인지 확인하고, Endpoint 상태와 Pod Readiness를 근거로 확인합니다.

504 오류의 경우, 백엔드 응답 시간을 확인하고 Ingress 타임아웃 설정이 적절한지 확인하고, 지연 메트릭과 Ingress 어노테이션을 근거로 확인합니다.

500 오류의 경우, 백엔드 애플리케이션 로그에서 예외와 오류를 조사하고, 애플리케이션 로그와 오류 패턴을 근거로 확인합니다.

지정된 시간 범위 내에서 상관관계가 발견되지 않으면: Deployment 롤아웃 문제를 확인하고, 백엔드 설정 변경을 확인하고, 데이터베이스 또는 의존성 가용성을 확인하고, 애플리케이션 릴리스를 검토하고, 최근 변경 롤백을 고려합니다.
