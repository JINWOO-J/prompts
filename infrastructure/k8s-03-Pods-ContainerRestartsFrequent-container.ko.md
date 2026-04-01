---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/03-Pods/ContainerRestartsFrequent-container.md)'
role: SRE / K8s Incident Response
origin: scoutflo
tags:
- container
- containerrestartsfrequent
- infrastructure
- k8s-namespace
- k8s-pod
- k8s-service
- kubernetes
- pods
- sts
---

---
title: Container Restarts Frequent
weight: 24
categories: [kubernetes, container]
---

# ContainerRestartsFrequent — Container 빈번한 재시작

## 의미

Container가 빈번하게 재시작되고 있습니다(ContainerRestartsFrequent 알림 발생). Container가 반복적인 실패와 재시작을 겪고 있으며, 이는 애플리케이션 또는 환경의 체계적 문제를 나타냅니다. Container 재시작 횟수가 빠르게 증가하고, Pod 이벤트에서 여러 재시작 주기가 관찰되며, 애플리케이션이 안정적인 운영을 유지하지 못합니다. 이는 워크로드 플레인에 영향을 미치며, 안정적 운영을 방해하는 지속적인 문제를 나타냅니다. 서비스 가용성이 저하되고, 재시작 중 데이터가 손실될 수 있으며, 사용자가 간헐적 장애를 경험합니다.

## 영향

ContainerRestartsFrequent 알림 발생; 재시작 주기로 인한 서비스 가용성 저하; 재시작 중 진행 중인 요청 손실; 연결 초기화; 시작 시간이 비가용성에 추가됨; 각 재시작 시 메모리 내 데이터 손실; 의존 서비스에서 연결 실패 발생;
 재시작 백오프 지연이 시간이 지남에 따라 증가; Pod가 CrashLoopBackOff 상태에 진입할 수 있음; 서비스 엔드포인트가 반복적으로 제거 및 추가됨; 로드 밸런서 Health check가 간헐적으로 실패.

## 플레이북

1. Namespace `<namespace>`에서 Pod `<pod-name>`을 조회하고 재시작 횟수, 마지막 재시작 시간, Container 종료 코드를 확인합니다.

2. Namespace `<namespace>`에서 Pod `<pod-name>`의 이벤트를 조회하고 'Killing', 'Started', 'Created', 'Failed' 등 재시작 관련 이벤트를 필터링하여 재시작 패턴을 파악합니다.

3. --previous 플래그를 사용하여 여러 재시작 주기에 걸친 Container 로그를 조회하고, 크래시된 인스턴스의 로그를 캡처하여 근본 원인을 파악합니다.

4. Container 종료 코드를 분석합니다: 0(정상 종료), 1(애플리케이션 오류), 137(SIGKILL/OOMKilled), 143(SIGTERM), 139(세그폴트)로 실패 유형을 분류합니다.

5. Liveness 및 Readiness Probe 구성을 조회하고, 공격적인 Probe 설정이 불필요한 재시작을 유발하는지 확인합니다.

6. 각 재시작 직전의 리소스 사용률(CPU, 메모리)을 확인하여 리소스 고갈 패턴을 파악합니다.

7. 노드 상태와 이벤트를 조회하여 노드 수준의 문제가 Container 실패를 유발하는지 확인합니다.

## 진단

재시작 타임스탬프를 OOMKilled 이벤트와 비교하고, 재시작이 메모리 고갈(종료 코드 137)로 인한 것인지 확인합니다. Container 상태와 메모리 메트릭을 근거로 판단합니다.

재시작을 Liveness Probe 실패와 상관 분석하고, Probe가 너무 공격적인지(짧은 타임아웃, 낮은 실패 임계값) 확인합니다. Probe 구성과 Pod 이벤트를 근거로 판단합니다.

재시작 주기에 걸친 애플리케이션 로그에서 일관된 오류 패턴을 분석하고, 동일한 오류가 반복되는지 확인합니다. 로그 집계와 오류 패턴 매칭을 근거로 판단합니다.

재시작 패턴을 외부 의존성 가용성(데이터베이스, API)과 비교하고, 연결 실패가 애플리케이션 크래시를 유발하는지 확인합니다. 의존성 상태와 연결 오류 로그를 근거로 판단합니다.

재시작이 패턴을 따르는지(시간대, 특정 작업 후) 확인하고, 예약된 작업이나 부하 패턴이 실패를 트리거하는지 확인합니다. 재시작 타임스탬프와 작업 스케줄을 근거로 판단합니다.

지정된 시간 범위 내에서 상관관계를 찾지 못한 경우: 크래시 분석을 위한 코어 덤프 활성화, 크래시 지점 전 디버그 로깅 추가, 시작 시퀀스의 경쟁 조건 확인, Container 이미지 무결성 확인, 의존성에 대한 Init Container 완료 검토를 수행합니다.
