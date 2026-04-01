---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/03-Pods/CPUThrottlingHigh-container.md)'
role: SRE / K8s Incident Response
origin: scoutflo
tags:
- container
- cputhrottlinghigh
- infrastructure
- k8s-deployment
- k8s-namespace
- k8s-pod
- k8s-service
- k8s-statefulset
- kubernetes
- performance
- pods
- sts
---

---
title: CPU Throttling High
weight: 22
categories: [kubernetes, container]
---

# CPUThrottlingHigh — CPU Throttling 과다

## 의미

Container가 심각한 CPU Throttling을 겪고 있습니다(CPUThrottlingHigh 알림 발생, 일반적으로 throttling이 전체 주기의 25%를 초과할 때 트리거). Container의 CPU 사용량이 CPU limit을 초과하면 CFS bandwidth controller에 의해 제한됩니다. Container 메트릭에서 높은 throttled_periods 비율이 관찰되고, throttling 중 애플리케이션 지연 시간이 증가하며, 성능이 불안정해집니다. 이는 워크로드 플레인에 영향을 미치며, 워크로드 요구사항에 비해 CPU limit이 부족함을 나타냅니다. 지연에 민감한 애플리케이션은 성능 저하를 겪고, 배치 처리가 느려지며, 사용자 경험이 악화됩니다.

## 영향

CPUThrottlingHigh 알림 발생; 애플리케이션 지연 시간이 예측 불가능하게 증가; 요청 처리가 불안정해짐; P99 지연 시간 급증; 타임아웃 오류 증가; 처리량이 예상 수준 이하로 감소; Health check가 간헐적으로 실패할 수 있음; 사용자 대면 작업 속도 저하; SLO 위반 발생; 실시간 처리 지연; 마이크로서비스 호출 체인에서 연쇄적 지연 발생; Worker 스레드가 CPU 시간을 확보하지 못함.

## 플레이북

1. Namespace `<namespace>`에서 Pod `<pod-name>`을 조회하고 Container CPU limit과 request를 확인하여 현재 리소스 할당량과 limit 대 request 비율을 파악합니다.

2. 메트릭을 사용하여 throttling 비율을 계산합니다: (container_cpu_cfs_throttled_periods_total / container_cpu_cfs_periods_total * 100)으로 심각도를 정량화합니다.

3. 지난 1시간 동안의 CPU 사용 패턴을 조회하고, throttling이 지속적인지 특정 피크 시간대에만 발생하는지 확인합니다.

4. 애플리케이션 지연 시간 메트릭(p50, p95, p99)을 조회하고 throttling 타임스탬프와 상관관계를 분석하여 성능 영향을 확인합니다.

5. Deployment 또는 StatefulSet의 리소스 사양을 조회하고 워크로드 유형에 적합한 CPU limit이 설정되어 있는지 평가합니다.

6. 워크로드가 Burstable QoS 클래스(requests < limits)를 사용하고 있는지 확인하고, Guaranteed QoS가 더 적합한지 판단합니다.

7. Vertical Pod Autoscaler(VPA) 권장 사항이 있는 경우 검토하여 데이터 기반 리소스 조정 제안을 확인합니다.

## 진단

CPU throttling과 요청 비율을 비교하고, throttling이 피크 부하 시간대에만 발생하는지 확인합니다. 이는 버스트 시 더 높은 limit이 필요함을 시사하며, 요청 메트릭과 throttling 상관관계를 근거로 판단합니다.

CPU 사용량을 request 대 limit과 비교 분석하고, request가 너무 높게 설정되었는지(과잉 프로비저닝) 또는 limit이 너무 낮은지(과소 프로비저닝) 확인합니다. 실제 사용량 메트릭을 근거로 판단합니다.

Replica 간 throttling을 상관 분석하고, 로드 밸런싱이 불균등하여 일부 Pod만 throttling되고 나머지는 유휴 상태인지 확인합니다. Pod별 CPU 메트릭과 요청 분배를 근거로 판단합니다.

CPU 사용량을 급증시키는 CPU 집약적 초기화 또는 주기적 작업이 있는지 확인하여 일시적 throttling의 원인을 파악합니다. CPU 사용량 타임라인과 작업 스케줄을 근거로 판단합니다.

애플리케이션이 단일 스레드로 동작하여 여러 CPU 코어를 효과적으로 활용하지 못하는지 평가합니다. 이 경우 limit에서 throttling이 발생하면서도 가용 request를 완전히 활용하지 못할 수 있습니다. 스레드 메트릭과 CPU 분배를 근거로 판단합니다.

지정된 시간 범위 내에서 상관관계를 찾지 못한 경우: CPU limit을 완전히 제거하는 것을 고려(스케줄링에는 request만 사용), 애플리케이션의 CPU 최적화 기회를 프로파일링, 수직 확장 대신 수평 확장 평가, 워크로드가 컨테이너화된 배포에 적합한지 검토, 노드에서의 Noisy Neighbor 효과를 확인합니다.
