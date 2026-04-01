---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/03-Pods/KubePodFrequentlyRestarting-pod.md)'
role: SRE / K8s Incident Response
origin: scoutflo
tags:
- database
- infrastructure
- k8s-deployment
- k8s-namespace
- k8s-pod
- k8s-service
- kubepodfrequentlyrestarting
- kubernetes
- monitoring
- pods
---

---
title: Kube Pod Frequently Restarting
weight: 28
categories: [kubernetes, pod]
---

# KubePodFrequentlyRestarting — Pod 빈번한 재시작

## 의미

Pod가 빈번하게 재시작되고 있습니다(KubePodFrequentlyRestarting 또는 KubePodContainerRestarting 알림 발생). Container가 반복적인 실패를 겪고 있으며 안정적인 운영을 유지하지 못합니다.
 짧은 기간 동안 Pod 재시작 횟수가 높고, Container가 계속 크래시되고 재시작되며, 애플리케이션이 안정적인 실행 상태를 달성하지 못합니다. 이는 워크로드 플레인에 영향을 미치며, 안정적 운영을 방해하는 지속적인 문제를 나타냅니다. 서비스가 간헐적으로 가용하고, 사용자가 예측 불가능한 실패를 경험하며, 재시작 중 데이터가 손실될 수 있습니다.

## 영향

KubePodFrequentlyRestarting 알림 발생; 서비스 가용성 저하; 재시작으로 인한 서비스 중단; 메모리 내 상태가 반복적으로 손실; 각 재시작 시 연결 초기화; 의존 서비스에서 간헐적 실패 발생; 사용자 경험 저하; SLO 위반 증가; 재시작 백오프 지연 증가; CrashLoopBackOff로 진행 가능; Deployment가 비정상으로 표시; 모니터링에서 높은 변동 표시.

## 플레이북

1. Namespace `<namespace>`에서 Pod `<pod-name>`을 조회하고 재시작 횟수, 마지막 재시작 시간, 지난 1시간 동안의 재시작 빈도를 확인합니다.

2. Pod `<pod-name>`의 이벤트를 조회하고 재시작 관련 이벤트를 필터링하여 실패 패턴과 타임스탬프를 파악합니다.

3. --previous 플래그를 사용하여 현재 및 이전 Container 인스턴스의 로그를 조회하고 각 재시작 전 오류 메시지를 캡처합니다.

4. Container 종료 상태와 종료 코드를 분석하여 실패 유형(OOMKilled, 애플리케이션 오류, 시그널)을 분류합니다.

5. Liveness Probe 구성을 조회하고 Probe 설정(timeout, period, failureThreshold)이 적절한지 확인합니다.

6. 재시작 직전의 리소스 사용률(CPU, 메모리) 패턴을 확인하여 리소스 고갈을 파악합니다.

7. 외부 의존성(데이터베이스, API, 구성 서비스)이 가용하고 올바르게 응답하는지 확인합니다.

## 진단

재시작 타임스탬프를 Probe 실패 이벤트와 비교하고, 느린 애플리케이션 응답으로 인해 Liveness Probe가 재시작을 유발하는지 확인합니다. Probe 구성과 Pod 이벤트를 근거로 판단합니다.

재시작을 로그의 애플리케이션 오류와 상관 분석하고, 일관된 오류 패턴이 실패를 유발하는지 확인합니다. 로그 분석과 오류 분류를 근거로 판단합니다.

재시작 전 리소스 사용률을 분석하고, CPU Throttling이나 메모리 압박이 애플리케이션 실패를 유발하는지 확인합니다. 리소스 메트릭과 Container 상태를 근거로 판단합니다.

시작 경쟁 조건을 확인하고, 애플리케이션이 Ready 상태가 되기 전 초기화 중 실패하는지 확인합니다. 시작 로그와 Readiness Probe 상태를 근거로 판단합니다.

동일 Deployment의 다른 Replica와 비교하고, 문제가 모든 Pod에 영향을 미치는지 또는 특정 인스턴스에만 발생하는지(노드 또는 데이터 문제 시사) 확인합니다. Pod별 메트릭과 노드 배치를 근거로 판단합니다.

지정된 시간 범위 내에서 상관관계를 찾지 못한 경우: 더 긴 초기화를 허용하기 위한 Startup Probe 추가, Liveness Probe 임계값 증가, 애플리케이션 예외 처리 검토, 외부 의존성 타임아웃 문제 확인, 애플리케이션 시작 의존성을 점검합니다.
