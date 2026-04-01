---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/04-Workloads/KubeJobFailed-workload.md)'
role: SRE / K8s Incident Response
origin: scoutflo
tags:
- infrastructure
- k8s-namespace
- k8s-node
- k8s-pod
- kubejobfailed
- monitoring
- performance
- workload
- workloads
---

---
title: Kube Job Failed
weight: 20
---

# Job 실패 (KubeJobFailed)

## 의미

Job이 성공적으로 완료되지 못한 상태입니다(KubeJobFailed 알림 발생). Job Pod가 실패했거나, 재시도 제한을 초과했거나, 실행 중 오류가 발생했기 때문입니다.
kubectl에서 Job이 Failed 상태를 보이고, Job Pod가 Failed 또는 CrashLoopBackOff 상태를 보이며, Job 로그에 치명적 오류, panic 메시지 또는 예외가 표시됩니다. 이는 워크로드 플레인에 영향을 미치며 Job 완료를 방해하는 애플리케이션 오류, 리소스 제약 또는 설정 문제를 나타냅니다. 주로 애플리케이션 버그, 리소스 소진, 설정 문제 또는 외부 의존성 실패가 원인이며, 애플리케이션 모니터링에 오류가 표시될 수 있습니다.

## 영향

KubeJobFailed 알림이 발생하며, 예약된 작업 처리가 실패합니다. Job을 완료할 수 없고, Job이 Failed 상태로 남습니다. 배치 처리 작업이 실패하며, 의존 워크플로우가 차단될 수 있습니다. 데이터 처리 또는 마이그레이션 작업이 완료되지 않고, Job Pod가 실패했거나 재시도 제한을 초과했습니다. Job 재시작 정책이 성공적인 완료를 방해합니다.

## 플레이북

1. namespace <namespace>에서 job <job-name>을 describe하여 다음을 확인합니다:
   - 완료 상태 및 실패한 Pod 수
   - Backoff Limit 및 Active Deadline Seconds 설정
   - 실패 원인을 보여주는 Condition
   - Failed, Error 또는 BackoffLimitExceeded 오류를 보여주는 Event

2. namespace <namespace>에서 job <job-name>의 이벤트를 타임스탬프 순으로 조회하여 실패 이벤트 순서를 확인합니다.

3. namespace <namespace>에서 job <job-name>에 속한 Pod를 조회하고 실패한 Pod를 describe하여 상태를 확인합니다.

4. namespace <namespace>에서 실패한 job pod <pod-name>의 로그를 조회하여 fatal, panic, exception 또는 error 패턴을 식별합니다.

5. Job Pod가 실행된 node <node-name>을 describe하여 리소스 가용성과 Condition을 확인합니다.

6. Pod가 재시작된 경우 namespace <namespace>에서 pod <pod-name>의 이전 컨테이너 로그를 조회하여 실패의 근본 원인을 파악합니다.

## 진단

1. 플레이북의 Job 및 Pod 이벤트를 분석하여 실패 모드와 타이밍을 파악합니다. 이벤트에 BackoffLimitExceeded, DeadlineExceeded 또는 Pod 실패가 표시되면, 이벤트 타임스탬프와 오류 메시지를 사용하여 실패 범주를 결정합니다.

2. 이벤트가 Job이 시작 직후 실패했음을 나타내면, Job 설정과 컨테이너 설정을 검사합니다. Job 시작 후 수초 내에 실패 이벤트가 발생했다면 설정 문제, 이미지 Pull 실패 또는 컨테이너 시작 문제가 원인일 가능성이 높습니다.

3. 이벤트가 Job이 일정 기간 실행 후 실패했음을 나타내면, 플레이북 4, 6단계의 Pod 로그를 분석합니다. 실패 시점에 로그에 애플리케이션 오류, 예외 또는 panic 트레이스가 표시되면 애플리케이션 수준 버그 또는 데이터 문제가 실패를 유발한 것입니다.

4. 이벤트가 Pod OOMKilled 또는 리소스 관련 종료를 나타내면, Job 리소스 요청과 실제 사용량을 비교합니다. 리소스 이벤트에 메모리 또는 CPU 제한 초과가 표시되면 리소스 제약이 Job Pod 실패를 유발한 것입니다.

5. 이벤트가 Node 문제를 나타내면, 플레이북 5단계의 Node Condition을 분석합니다. Job 실패 시점에 Node 이벤트에 리소스 압박, 디스크 문제 또는 NotReady Condition이 표시되면 Node 수준 문제가 Pod Eviction 또는 실패를 유발한 것입니다.

6. 이벤트가 스케줄링 실패를 나타내면, 리소스 Quota와 Node 용량을 확인합니다. Quota 이벤트에 소진이 표시되거나 스케줄링 이벤트에 리소스 부족이 표시되면 용량 제약이 Job 완료를 방해한 것입니다.

7. 이벤트가 모든 Job Pod에서 일관된 실패를 보이면 문제는 결정적입니다(애플리케이션 버그 또는 데이터 문제). 실패가 특정 Pod에 국한되면 Node 문제 또는 네트워크 실패와 같은 일시적 문제가 원인일 수 있습니다.

**상관관계를 찾을 수 없는 경우**: Job 실행 시간으로 시간 범위를 확장하고, Job 애플리케이션 로직을 검토하고, 외부 의존성 실패를 확인하고, Job 설정 파라미터를 검증하고, 과거 Job 실행 패턴을 검사합니다. Job 실패는 즉각적인 인프라 변경이 아닌 애플리케이션 버그, 데이터 문제 또는 외부 의존성 문제로 인해 발생할 수 있습니다.
