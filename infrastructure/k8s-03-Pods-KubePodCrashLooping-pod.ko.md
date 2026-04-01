---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/03-Pods/KubePodCrashLooping-pod.md)'
role: SRE / K8s Incident Response
origin: scoutflo
tags:
- infrastructure
- k8s-configmap
- k8s-deployment
- k8s-namespace
- k8s-pod
- k8s-secret
- k8s-service
- kubepodcrashlooping
- kubernetes
- monitoring
- performance
- pods
---

---
title: Kube Pod Crash Looping
weight: 20
---

# KubePodCrashLooping — Pod 크래시 루프

## 의미

Pod가 CrashLoopBackOff 상태에 있습니다(KubePodCrashLooping 또는 KubePodNotReady 등의 알림 발생). Container 애플리케이션이 시작 직후 크래시되거나 종료되어 Kubernetes가 반복적으로 재시작합니다.
 kubectl에서 Pod의 재시작 횟수가 지속적으로 증가하고, Container 종료 코드가 0이 아닌 실패(일반적으로 1, 137 또는 143)를 나타내며, 애플리케이션 로그에 치명적 오류, panic 메시지 또는 예외가 표시됩니다. 이는 워크로드 플레인에 영향을 미치며, 구성 오류, 리소스 제약, 누락된 의존성 또는 애플리케이션 버그로 인한 애플리케이션 수준 실패를 나타냅니다. 애플리케이션 모니터링에서 크래시와 예외가 나타날 수 있으며, 누락된 ConfigMap, Secret 또는 PersistentVolumeClaim 의존성이 Container 초기화를 차단할 수 있습니다.

## 영향

KubePodCrashLooping 알림 발생; Pod가 트래픽을 처리할 수 없음; 서비스 불가용 또는 저하; 애플리케이션 시작 실패; Pod가 CrashLoopBackOff 상태로 유지; 재시작 횟수 지속 증가; Container 종료 코드가 0이 아닌 값(일반적으로 1, 137 또는 143); 애플리케이션 로그에 치명적 오류, panic 메시지 또는 예외 표시; Readiness Probe가 성공하지 못함; 워크로드가 원하는 상태에 도달하지 못함. 롤링 업데이트 완료 불가; 예약된 작업 실패; kubectl에서 Pod 상태가 무기한 CrashLoopBackOff로 표시; 서비스 엔드포인트 제거; Deployment에 Replica 수 불일치 표시 가능. 애플리케이션 오류 증가; 애플리케이션 예외 빈번 발생; 애플리케이션 성능 저하; 누락된 ConfigMap, Secret 또는 PersistentVolumeClaim 의존성이 초기화 실패를 유발할 수 있음.

## 플레이북

1. Namespace `<namespace>`에서 Pod `<pod-name>`을 조회하고 상태와 재시작 횟수를 확인하여 크래시 루프를 확인하고 재시작 원인을 파악합니다.

2. Namespace `<namespace>`에서 Pod `<pod-name>`의 이벤트를 조회하고 'Failed', 'Error', 'CrashLoopBackOff', 'BackOff' 등 오류 패턴을 필터링하여 Pod 라이프사이클 문제를 파악합니다.

3. Namespace `<namespace>`에서 Pod `<pod-name>`의 Container `<container-name>` 로그를 조회하고 'fatal', 'panic', 'exception', 'failed to start', 'connection refused', 'permission denied' 등 오류 패턴을 필터링하여 애플리케이션 오류를 파악합니다.

4. Namespace `<namespace>`에서 Deployment 또는 StatefulSet `<workload-name>`을 조회하고 리소스 request/limit, Readiness/Liveness Probe 구성, 보안 컨텍스트 설정, 볼륨 마운트, 환경 변수 등 Pod 템플릿 파라미터를 확인하여 구성 문제를 확인합니다.

5. Pod `<pod-name>`이 스케줄된 노드 `<node-name>`을 조회하고 노드 리소스 가용성과 조건을 확인하여 리소스 제약을 파악합니다.

6. Namespace `<namespace>`에서 Pod `<pod-name>`이 참조하는 ConfigMap, Secret, PersistentVolumeClaim 리소스를 조회하고 Container 초기화를 차단하는 누락된 의존성을 확인합니다.

## 진단

Pod 재시작 타임스탬프를 30분 이내의 Deployment 또는 StatefulSet 변경 타임스탬프와 비교하고, 구성 변경 직후 크래시가 시작되었는지 확인합니다. Pod 이벤트와 Deployment 롤아웃 이력을 근거로 판단합니다.

Pod 크래시 타임스탬프를 5분 이내의 노드 조건 전환 시간과 상관 분석하고, 크래시가 노드 리소스 압박(MemoryPressure, DiskPressure, PIDPressure)과 일치하는지 확인합니다. 노드 조건과 Pod 스케줄링 이벤트를 근거로 판단합니다.

지난 15분간의 재시작 빈도를 분석하여 재시작이 지속적인지(시작 시 애플리케이션 크래시) 또는 간헐적인지(리소스 제약 또는 의존성 실패) 판단합니다. Pod 재시작 횟수와 Container 종료 코드를 근거로 판단합니다.

여러 재시작 주기에 걸쳐 Container 종료 코드와 로그 오류 패턴을 비교하고, 동일한 오류 패턴이 일관되게 반복되는지 확인합니다. Pod 로그와 Container 상태를 근거로 판단합니다.

Pod 크래시 타임스탬프를 5분 이내의 ConfigMap 또는 Secret 업데이트 타임스탬프와 상관 분석하고, 구성 변경 후 크래시가 시작되었는지 확인합니다. Pod 이벤트와 리소스 수정 시간을 근거로 판단합니다.

Pod 리소스 request를 크래시 시점의 노드 가용 리소스와 비교하고, 리소스 제약이 정상 시작을 방해하는지 확인합니다. 노드 메트릭과 Pod 리소스 사양을 근거로 판단합니다.

지정된 시간 범위 내에서 상관관계를 찾지 못한 경우: Deployment 변경에 대해 1시간으로 시간 범위 확장, 점진적 저하 패턴에 대한 애플리케이션 로그 검토, 외부 의존성 실패(데이터베이스, API) 확인, 과거 재시작 패턴 점검, Container 이미지 변경 확인. Pod 크래시는 즉각적인 구성 변경이 아닌 애플리케이션 버그, 이미지 손상 또는 런타임 환경 문제로 인해 발생할 수 있습니다.
