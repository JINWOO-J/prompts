---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/04-Workloads/JobFailingToComplete-job.md)'
role: SRE / K8s Incident Response
origin: scoutflo
tags:
- infrastructure
- jobfailingtocomplete
- k8s-namespace
- k8s-pod
- kubernetes
- pipeline
- workloads
---

---
title: Job Failing To Complete - Job
weight: 286
categories:
  - kubernetes
  - workload
---

# Job 완료 실패 (JobFailingToComplete-job)

## 의미

Kubernetes Job이 성공적인 완료 상태에 도달할 수 없는 상태입니다(KubeJobFailed 또는 KubeJobCompletionStuck 알림 발생 가능). Pod가 0이 아닌 상태로 종료되거나, 반복적으로 재시작되거나, backoff 또는 activeDeadlineSeconds 제한에 도달하기 때문입니다. Job 실행 실패, Pod 실패, 리소스 제약 또는 Job 설정 문제로 성공적인 Job 완료가 방해됩니다.

## 영향

Job이 성공적으로 완료되지 않으며, 배치 처리 작업이 완료되지 않습니다. CronJob이 실패하고, 데이터 처리 파이프라인이 중단됩니다. 예약된 작업이 미완료 상태로 남으며, KubeJobFailed 알림이 발생합니다. KubeJobCompletionStuck 알림이 발생할 수 있고, Job Pod가 오류로 종료되며, Job backoff 제한에 도달하고, Job 데드라인이 초과됩니다.

## 플레이북

1. namespace `<namespace>`에서 job `<job-name>`을 describe하여 Job 상태, 완료 상태 및 설정을 검사합니다.

2. namespace `<namespace>`에서 이벤트를 타임스탬프 순으로 조회하여 Job 관련 실패와 Pod 오류를 확인합니다.

3. namespace `<namespace>`에서 Job Pod의 로그를 조회하고 오류를 필터링합니다.

4. namespace `<namespace>`에서 Pod를 조회하고 Job Pod를 필터링하여 Pod 상태와 재시작 횟수를 확인합니다.

5. namespace `<namespace>`에서 job `<job-name>`을 조회하고 backoffLimit 및 activeDeadlineSeconds를 포함한 Job 설정을 확인합니다.

6. namespace `<namespace>`에서 Job Pod를 조회하여 리소스 제약을 확인합니다.

## 진단

플레이북 섹션에서 수집한 Job describe 출력, Pod 로그 및 이벤트를 분석하는 것으로 시작합니다. Job Condition, Pod 종료 코드 및 컨테이너 종료 사유가 주요 진단 신호를 제공합니다.

**Job 상태가 backoffLimitExceeded를 표시하는 경우:**
- Job Pod가 `backoffLimit`이 허용하는 것보다 더 많이 실패했습니다. Pod 로그에서 실패를 유발하는 실제 오류를 확인합니다. Job 설정이 아닌 애플리케이션이 실패하는 것입니다.

**Job 상태가 DeadlineExceeded를 표시하는 경우:**
- Job이 완료 전에 `activeDeadlineSeconds`를 초과했습니다. Job이 정당하게 더 많은 시간이 필요하면 데드라인을 늘리거나, Job이 예상보다 오래 걸리는 이유를 조사합니다.

**Pod 로그에 애플리케이션 오류 또는 0이 아닌 종료 코드가 표시되는 경우:**
- Job 컨테이너가 애플리케이션 문제로 실패하고 있습니다. 로그의 구체적인 오류를 검토합니다. 일반적인 원인에는 누락된 환경 변수, 실패한 데이터베이스 연결 또는 잘못된 입력 데이터가 포함됩니다.

**Pod 종료 사유에 OOMKilled가 표시되는 경우:**
- Job 컨테이너가 메모리 제한을 초과했습니다. Job 스펙에서 메모리 제한을 늘리거나, Job 워크로드를 최적화하여 메모리 사용량을 줄입니다.

**Pod가 Evicted 상태를 표시하는 경우:**
- Node 리소스 압박으로 Pod가 Eviction되었습니다. Node Condition에서 메모리 또는 디스크 압박을 확인합니다. Job Pod를 Eviction으로부터 보호하기 위해 리소스 요청 추가를 고려합니다.

**Pod가 스케줄링 실패로 Pending 상태에 머물러 있는 경우:**
- Job Pod를 스케줄링할 수 없습니다. 이벤트에서 `Insufficient cpu`, `Insufficient memory` 또는 Node Affinity 문제를 확인합니다. 리소스 요청 또는 Node Selector를 조정합니다.

**Job이 실행되지만 완료되지 않는 경우(Pod가 Running 상태 유지):**
- Job 프로세스가 중단되었을 수 있습니다. Pod 로그에서 마지막 활동을 확인합니다. 애플리케이션이 외부 의존성을 기다리거나 루프에 빠져 있을 수 있습니다.

**이벤트가 결정적이지 않은 경우 타임스탬프를 연관시킵니다:**
1. Job 스펙이 수정된 후 Job 실패가 시작되었는지 확인합니다.
2. Job이 의존하는 ConfigMap 또는 Secret 변경과 실패가 연관되는지 확인합니다.
3. 외부 서비스 의존성이 사용 불가능해졌는지 확인합니다.

**명확한 원인을 찾을 수 없는 경우:** 동일한 이미지와 환경으로 Job 컨테이너를 로컬 또는 디버그 Pod에서 실행하여 애플리케이션 실패를 대화형으로 재현하고 디버깅합니다.
