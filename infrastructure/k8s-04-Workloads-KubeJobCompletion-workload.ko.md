---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/04-Workloads/KubeJobCompletion-workload.md)'
role: SRE / K8s Incident Response
origin: scoutflo
tags:
- infrastructure
- k8s-namespace
- k8s-pod
- kubejobcompletion
- monitoring
- performance
- pipeline
- workload
- workloads
---

---
title: Kube Job Completion
weight: 20
---

# Job 완료 지연 (KubeJobCompletion)

## 의미

Job이 완료하는 데 1시간 이상 소요되는 상태입니다(Job 완료 시간 관련 알림 발생). Job 실행이 예상보다 오래 걸리고 있어 잠재적인 성능 문제, 리소스 제약 또는 애플리케이션 문제를 나타냅니다.
Job이 1시간을 초과하는 실행 시간을 보이고, Job Pod가 장기간 Running 상태를 보이며, Job 로그에 느린 처리 또는 리소스 경합이 표시될 수 있습니다. 이는 워크로드 플레인에 영향을 미치며 배치 Job이 예상 시간 내에 완료되지 않음을 나타냅니다. 주로 리소스 제약, 데이터 볼륨 증가, 애플리케이션 성능 문제 또는 잘못 설정된 리소스 할당이 원인이며, 애플리케이션 모니터링에 오류가 표시될 수 있습니다.

## 영향

Job 완료 알림이 발생하며, 배치 Job의 처리가 길어집니다. 다음 Job 스케줄링에 문제가 발생할 수 있고, Job 실행이 예상 시간을 초과합니다. 의존 워크플로우가 지연될 수 있으며, 배치 처리 파이프라인이 느려집니다. 리소스 소비가 연장되고, Job 실행이 예상 시간보다 상당히 오래 걸립니다.

## 플레이북

1. namespace <namespace>에서 job <job-name>을 describe하여 다음을 확인합니다:
   - 시작 시간, 지속 시간 및 완료 상태
   - Active Deadline Seconds 및 Backoff Limit 설정
   - Parallelism 및 Completions 설정
   - Job이 오래 걸리는 이유를 보여주는 Condition
   - 실행 중 문제를 보여주는 Event

2. namespace <namespace>에서 job <job-name>의 이벤트를 타임스탬프 순으로 조회하여 Job 실행 이벤트 순서를 확인합니다.

3. namespace <namespace>에서 job <job-name>에 속한 Pod를 조회하고 Pod를 describe하여 실행 중인지 중단되었는지 확인합니다.

4. namespace <namespace>에서 job pod <pod-name>의 로그를 조회하여 처리 진행 상황 또는 병목 현상을 파악합니다.

5. Job Pod가 실행 중인 node <node-name>을 describe하여 리소스 가용성과 Condition을 확인합니다.

6. namespace <namespace>에서 job pod <pod-name>의 리소스 사용량 메트릭을 조회하고 리소스 요청과 비교하여 리소스 제약을 식별합니다.

## 진단

1. 플레이북의 Job 및 Pod 이벤트를 분석하여 실행 상태와 경고 이벤트를 파악합니다. 이벤트에서 Job이 여전히 실행 중이지만 느리게 진행되고 있으면, 이벤트 타임스탬프를 사용하여 Job이 시작된 시점과 현재 진행 상황을 파악합니다.

2. 이벤트가 리소스 스로틀링 또는 경합을 나타내면, 플레이북 6단계의 Pod 리소스 사용량을 확인합니다. CPU 또는 메모리 사용량이 지속적으로 제한에 도달하면 리소스 제약이 Job 실행을 느리게 하는 것입니다.

3. 이벤트가 Node 리소스 압박을 나타내면, 플레이북 5단계의 Node Condition을 분석합니다. Job 실행 시점에 Node 이벤트에 MemoryPressure, DiskPressure 또는 높은 사용률이 표시되면 Node 수준 제약이 성능에 영향을 미치는 것입니다.

4. 이벤트가 Job이 데드라인에 근접하고 있음을 나타내면, 플레이북 1단계의 Active Deadline 설정을 확인합니다. Job 실행 시간이 activeDeadlineSeconds에 근접하면 완료 전에 Job이 타임아웃될 수 있습니다.

5. 이벤트에 리소스 문제가 없으면, 플레이북 4단계의 Job 로그에서 처리 진행 상황을 검사합니다. 로그에 느린 처리, 외부 리소스 대기 또는 I/O 병목 현상이 표시되면 애플리케이션 수준 성능 문제가 원인입니다.

6. 이벤트가 반복 패턴을 나타내면, 현재 실행과 과거 Job 완료 시간을 비교합니다. Job이 유사한 과거 Job보다 지속적으로 오래 걸리면 데이터 볼륨 증가 또는 알고리즘 효율성을 조사합니다.

7. 이벤트가 Parallelism 또는 Completions 설정을 나타내면, Job Parallelism이 적절한지 확인합니다. 워크로드에 비해 Parallelism이 너무 낮게 설정되었으면 병렬 Pod 수를 늘려 완료 시간을 개선할 수 있습니다.

**상관관계를 찾을 수 없는 경우**: Job 실행 시간으로 시간 범위를 확장하고, Job 애플리케이션 로직과 알고리즘을 검토하고, 데이터 처리 비효율성을 확인하고, Job 리소스 할당을 검증하고, 과거 Job 성능 패턴을 검사합니다. Job 완료 지연은 즉각적인 인프라 변경이 아닌 애플리케이션 성능 문제, 데이터 볼륨 증가 또는 리소스 할당 문제로 인해 발생할 수 있습니다.
