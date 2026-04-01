---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/03-Pods/ContainerHighCPUThrottling-container.md)'
role: SRE / K8s Incident Response
origin: scoutflo
tags:
- container
- containerhighcputhrottling
- infrastructure
- k8s-deployment
- k8s-namespace
- k8s-pod
- k8s-statefulset
- kubernetes
- performance
- pods
- sts
---

---
title: Container High CPU Throttling
weight: 20
categories: [kubernetes, container]
---

# ContainerHighCPUThrottling — Container CPU Throttling 과다

## 의미

Container가 높은 CPU Throttling을 겪고 있습니다(ContainerHighCPUThrottling 또는 CPUThrottlingHigh 알림 발생). Container가 CPU limit에 도달하여 Linux CFS 스케줄러에 의해 throttling되면서 성능이 저하됩니다. Container 메트릭에서 throttled_time이 증가하고, CPU 사용량이 지속적으로 limit 근처이거나 limit에 도달하며, 애플리케이션 응답 시간이 증가합니다. 이는 워크로드 플레인에 영향을 미치며, Container에 더 많은 CPU 리소스가 필요하거나 비효율적인 CPU 사용 패턴이 있음을 나타냅니다. 애플리케이션 지연 시간이 증가하고, 요청 처리가 느려지며, 타임아웃이 발생할 수 있습니다.

## 영향

ContainerHighCPUThrottling 알림 발생; 애플리케이션 응답 시간이 크게 증가; 요청 처리 속도 저하; 타임아웃 오류 증가; 처리량 감소; 지연에 민감한 작업 실패; Health check 응답 지연; Pod가 비정상으로 표시될 수 있음; 사용자 대면 지연 시간 증가; SLO 위반 가능; 배치 작업 완료 시간 증가; CPU 바운드 작업이 대기열에 쌓임; 애플리케이션 스레드가 CPU 시간을 대기함.

## 플레이북

1. Namespace `<namespace>`에서 Pod `<pod-name>`을 조회하고 Container CPU limit과 request를 확인하여 현재 리소스 할당량을 파악합니다.

2. Container `<container-name>`의 CPU throttling 메트릭(container_cpu_cfs_throttled_seconds_total, container_cpu_cfs_throttled_periods_total)을 조회하여 throttling 심각도를 정량화합니다.

3. Container CPU 사용량 메트릭(container_cpu_usage_seconds_total)을 조회하고 CPU limit과 비교하여 Container가 지속적으로 limit에 도달하는지 확인합니다.

4. Container `<container-name>`의 애플리케이션 메트릭 또는 로그를 조회하고 지연 시간이나 타임아웃 패턴을 필터링하여 CPU throttling과 애플리케이션 성능 저하의 상관관계를 확인합니다.

5. Namespace `<namespace>`에서 Deployment 또는 StatefulSet `<workload-name>`을 조회하고 모든 Container의 CPU 리소스 사양(request 및 limit)을 검토합니다.

6. Pod가 실행 중인 노드 `<node-name>`을 조회하고 노드 CPU 용량과 현재 사용률을 확인하여 노드 수준의 리소스 경합이 있는지 점검합니다.

7. Vertical Pod Autoscaler(VPA)가 구성되어 있는 경우 권장 사항을 확인하여 과거 사용량 기반의 CPU limit 조정 제안을 파악합니다.

## 진단

Throttling 비율(throttled_periods / total_periods * 100)을 애플리케이션 지연 시간 메트릭과 비교하고, 25% 이상의 throttling이 응답 시간 증가와 상관관계가 있는지 확인합니다. Container 메트릭과 애플리케이션 APM 데이터를 근거로 판단합니다.

CPU throttling 패턴을 특정 시간대나 워크로드 패턴과 상관 분석하고, throttling이 피크 부하 시간대에 발생하는지 확인합니다. 요청 비율 메트릭과 throttling 타임스탬프를 근거로 판단합니다.

CPU request가 적절하게 설정되어 있는지 분석합니다(request는 일반적인 사용량을 반영하고, limit은 버스트를 수용해야 함). Request 대 limit 비율이 과도한 스케줄링을 유발하는지 확인합니다. Pod 스케줄링 결정과 노드 할당을 근거로 판단합니다.

동일 Deployment의 Replica 간 CPU 사용 패턴을 비교하고, throttling이 모든 Pod에 균등하게 영향을 미치는지 또는 특정 인스턴스에만 발생하는지 확인합니다. Pod별 메트릭과 로드 밸런싱 분배를 근거로 판단합니다.

애플리케이션이 비효율적인 코드, 블로킹 작업 또는 과도한 가비지 컬렉션으로 인해 CPU 바운드 상태인지 확인합니다. 애플리케이션 프로파일링 데이터와 GC 메트릭을 근거로 판단합니다.

지정된 시간 범위 내에서 상관관계를 찾지 못한 경우: CPU 집약적 작업에 대한 애플리케이션 코드 검토, 폭주 스레드나 무한 루프 확인, 암호화폐 채굴이나 악성 프로세스가 없는지 확인, JVM 또는 런타임 CPU 설정 점검, 워크로드가 근본적으로 CPU 바운드이며 더 높은 limit이 필요한지 검토합니다.
