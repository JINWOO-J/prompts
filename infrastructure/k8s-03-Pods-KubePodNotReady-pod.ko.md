---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/03-Pods/KubePodNotReady-pod.md)'
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
- kubepodnotready
- monitoring
- performance
- pods
---

---
title: Kube Pod Not Ready
weight: 20
---

# KubePodNotReady — Pod 준비 안 됨

## 의미

Pod가 15분 이상 비정상(Not Ready) 상태에 있습니다(KubePodNotReady 또는 KubePodPending 등의 알림 발생). Readiness Probe 실패, Pod가 Pending 단계에 고착, 또는 Container가 Health check를 통과하지 못하고 있습니다.
 kubectl에서 Pod가 NotReady 조건을 보이고, Pod 이벤트에 Readiness Probe 실패가 나타나며, 애플리케이션 로그에 시작 오류나 Health check 실패가 표시될 수 있습니다. 이는 워크로드 플레인에 영향을 미치며, 잘못 구성된 Health Probe, 애플리케이션 시작 실패, 리소스 제약 또는 누락된 의존성으로 인해 Pod가 Ready 상태가 되지 못하는 애플리케이션 상태 문제, 구성 문제 또는 리소스 제약을 나타냅니다.

## 영향

KubePodNotReady 알림 발생; 서비스 저하 또는 불가용; Pod가 서비스 엔드포인트에 연결되지 않음; 트래픽이 Pod로 라우팅되지 않음; Pod가 비정상 상태로 유지; Readiness Probe 실패; 애플리케이션이 트래픽을 처리할 수 없음; Deployment 완료 실패 가능; Replica 수가 원하는 상태와 불일치. kubectl에서 Pod가 무기한 NotReady 조건 표시; 서비스에서 서비스 엔드포인트 제거; 롤링 업데이트 완료 불가; 예약된 작업 실패.

## 플레이북

1. Namespace `<namespace>`에서 Pod `<pod-name>`을 describe하여 확인합니다:
   - Conditions 섹션에서 Ready=False와 사유
   - Container 상태에서 waiting/running 상태
   - Events 섹션에서 Probe 실패 또는 기타 오류

2. Namespace `<namespace>`에서 Pod `<pod-name>`의 이벤트를 타임스탬프 순으로 조회하여 Readiness Probe 실패, 시작 문제 또는 의존성 오류를 타임스탬프와 함께 확인합니다.

3. Namespace `<namespace>`에서 Pod `<pod-name>`의 조건을 조회하고 어떤 조건이 실패하는지(Ready, ContainersReady, PodScheduled 또는 Initialized) 파악합니다.

4. Namespace `<namespace>`에서 Pod `<pod-name>`의 로그를 조회하여 초기화 중 오류나 Health check 엔드포인트 실패 등 애플리케이션 시작 문제를 확인합니다.

5. Namespace `<namespace>`에서 Deployment `<deployment-name>`을 describe하여 확인합니다:
   - Readiness Probe 구성 (path, port, timeoutSeconds, failureThreshold)
   - 느린 시작을 유발할 수 있는 리소스 request/limit
   - 환경 변수 또는 ConfigMap/Secret 참조

6. 의존성 존재 여부를 확인합니다: Namespace `<namespace>`에서 ConfigMap, Secret, PVC를 확인합니다.

7. Pod가 실행 중인 노드 `<node-name>`을 describe하고 Conditions 섹션을 확인하여 노드 문제가 Pod 상태에 영향을 미치는지 확인합니다.

## 진단

1. 플레이북 1-2단계의 Pod 이벤트를 분석하여 Pod가 NotReady인 이유를 파악합니다. Probe 실패, 시작 오류 또는 의존성 문제를 보여주는 이벤트가 구체적인 원인을 나타냅니다.

2. Pod 조건에서 Ready=False와 사유가 표시되면(플레이북 3단계), 실패하는 조건을 파악합니다:
   - ContainersReady=False: Container Health check 실패
   - PodScheduled=False: Pod 스케줄링 불가 (여전히 Pending)
   - Initialized=False: Init Container 미완료

3. 이벤트에 "Readiness probe failed"가 표시되면(플레이북 2단계):
   - Probe 구성 확인 (플레이북 5단계)
   - 애플리케이션이 Probe 엔드포인트에서 응답하는지 확인
   - 시작이 느린 경우 initialDelaySeconds 조정
   - 오류에 대한 애플리케이션 로그 검토 (플레이북 4단계)

4. Pod가 CrashLoopBackOff 또는 Container 재시작을 보이면:
   - 종료 사유 확인 (OOMKilled, Error)
   - 크래시 원인에 대한 이전 Container 로그 검토
   - 리소스 limit이 적절한지 확인

5. 이벤트에서 누락된 의존성이 표시되면(플레이북 6단계):
   - ConfigMap 또는 Secret이 존재하지 않음
   - PVC를 바인딩할 수 없음
   - 서비스 의존성 불가용

6. 노드에 문제가 표시되면(플레이북 7단계):
   - 노드 NotReady는 해당 노드의 모든 Pod에 영향
   - 노드 리소스 압박이 Pod 축출을 유발할 수 있음
   - 노드 조건과 리소스 사용량 확인

7. 애플리케이션 로그에 시작 또는 런타임 오류가 표시되면(플레이북 4단계):
   - 애플리케이션 구성 문제
   - 데이터베이스 또는 외부 API 연결 문제
   - 누락된 환경 변수 또는 파일

**NotReady Pod 해결을 위해**: 이벤트와 로그에서 파악된 근본 문제를 수정합니다. Readiness Probe 실패의 경우 Probe 구성을 조정하거나 애플리케이션 Health 엔드포인트를 수정합니다. 크래시의 경우 애플리케이션 코드 또는 구성의 근본 원인을 해결합니다. 누락된 의존성의 경우 필요한 리소스를 생성합니다.
