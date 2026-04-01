---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/05-Networking/NginxIngressHighLatency-ingress.md)'
role: Kubernetes SRE
origin: scoutflo
extract_date: 2026-03-05
tags:
- capacity
- infrastructure
- ingress
- k8s-ingress
- k8s-pod
- k8s-service
- kubernetes
- networking
- nginx
- nginxingresshighlatency
- performance
- scaling
- sts
---

---
title: Nginx Ingress High Latency
weight: 52
categories: [kubernetes, ingress]
---

# NginxIngressHighLatency - Nginx Ingress 높은 지연 시간

## 의미

Nginx Ingress에서 높은 요청 지연이 발생하고 있으며(NginxIngressHighLatency, IngressHighLatency 알림 발생), 요청 완료가 예상보다 오래 걸리고 있어 백엔드 느림, Ingress 리소스 제약 또는 네트워크 문제를 나타냅니다. Ingress 메트릭에서 응답 시간이 증가하고, 사용자가 느린 페이지 로드를 경험하며, SLO 지연 임계값이 위반되었습니다. 사용자 경험에 영향을 미치며, 애플리케이션이 느리게 느껴지고, 타임아웃 오류가 증가할 수 있으며, 고객 만족도가 감소합니다.

## 영향

NginxIngressHighLatency 알림 발생, 사용자 대면 응답 시간 증가, 페이지 로드 시간 느림, API 응답 지연, 타임아웃 오류 발생 가능, 사용자 경험 저하, 이탈률 증가, SLO 위반 발생, 다운스트림 시스템이 응답 대기 중 타임아웃 가능, Service Mesh 전체에 연쇄 지연.

## 플레이북

1. Ingress Controller 지연 메트릭을 조회하고 가장 높은 지연을 보이는 백엔드 서비스를 파악합니다.

2. 지연 분석: Ingress에서 소요된 시간 대 백엔드에서 소요된 시간(upstream_response_time)을 분석합니다.

3. 백엔드 서비스 Pod 성능과 리소스 사용률을 확인합니다.

4. 리소스 제약에 대해 Ingress Controller Pod CPU 및 메모리 사용률을 확인합니다.

5. 용량 문제를 나타내는 Ingress 수준의 연결 큐잉을 확인합니다.

6. 부하에 대해 백엔드 서비스 수평 스케일링이 적절한지 확인합니다.

7. Ingress Pod와 백엔드 서비스 간 네트워크 지연을 확인합니다.

## 진단

Ingress 처리 시간과 업스트림 응답 시간을 비교하여 지연이 Ingress에 있는지 백엔드에 있는지 판단하고, Nginx 타이밍 메트릭을 근거로 확인합니다.

업스트림 지연이 높으면, 백엔드 서비스 성능(CPU, 메모리, 의존성)을 조사하고, 백엔드 메트릭과 애플리케이션 프로파일링을 근거로 확인합니다.

Ingress 처리 시간이 높으면, Ingress Controller 리소스 사용률과 연결 처리 용량을 확인하고, Controller 메트릭과 Pod 리소스를 근거로 확인합니다.

지연과 트래픽 볼륨을 상관 분석하여 부하 증가에 따라 지연이 증가하는지 확인하여 용량 문제를 파악하고, 트래픽 메트릭과 지연 상관관계를 근거로 확인합니다.

느리게 응답하는 백엔드가 연결을 점유하여 커넥션 풀 고갈로 다른 요청에 영향을 미치는지 확인하고, 연결 메트릭과 타임아웃 설정을 근거로 확인합니다.

지정된 시간 범위 내에서 상관관계가 발견되지 않으면: 백엔드 서비스를 스케일링하고, Ingress Controller 리소스를 늘리고, 백엔드 애플리케이션 성능을 최적화하고, 캐싱 레이어를 추가하고, 데이터베이스 쿼리 성능을 검토하고, 정적 콘텐츠에 CDN 사용을 고려합니다.
