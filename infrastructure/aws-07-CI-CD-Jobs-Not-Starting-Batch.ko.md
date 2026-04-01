---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/AWS%20Playbooks/07-CI-CD/Jobs-Not-Starting-Batch.md)'
role: SRE / AWS Incident Response
origin: scoutflo
extract_date: 2026-03-05
tags:
- batch
- capacity
- ci-cd
- cloudwatch
- compute
- ecs
- iam
- infrastructure
- jobs
- k8s-service
- performance
- pipeline
- starting
- sts
---

# AWS Batch 작업 시작 불가

## 의미

AWS Batch 작업이 시작되지 않는(작업 실행 실패 또는 BatchJobStartFailed 알람 트리거) 이유는 컴퓨팅 환경이 사용 불가하거나, 작업 큐가 잘못 구성되었거나, IAM 권한이 부족하거나, 작업 정의에 오류가 있거나, Batch 서비스가 작업 제출 중 오류를 만나거나, Batch 컴퓨팅 환경 용량이 부족하기 때문입니다. AWS Batch 작업이 시작될 수 없고, 작업 실행이 차단되며, 배치 처리 워크플로우가 실패합니다. 이는 배치 처리 및 컴퓨팅 계층에 영향을 미치며 작업 실행을 차단합니다. 일반적으로 컴퓨팅 환경 문제, 큐 구성 문제 또는 권한 실패로 인해 발생합니다. ECS와 함께 Batch를 사용하는 경우 컴퓨팅 환경 동작이 다를 수 있으며 애플리케이션에서 작업 제출 실패가 발생할 수 있습니다.

## 영향

AWS Batch 작업 시작 불가; 작업 실행 차단; 배치 처리 워크플로우 실패; 작업 큐 처리 중단; 배치 작업 자동화 무효; 작업 제출 실패; 배치 처리 신뢰성 손상; 작업 스케줄링 실패. BatchJobStartFailed 알람이 발생할 수 있으며, ECS와 함께 Batch를 사용하는 경우 컴퓨팅 환경 동작이 다를 수 있고, 실패한 작업 실행으로 인해 애플리케이션에서 오류 또는 성능 저하가 발생할 수 있으며, 배치 처리 파이프라인이 완전히 차단될 수 있습니다.

## 플레이북

1. Batch 작업 큐 `<job-queue-name>`이 존재하고 리전 `<region>`에서 Batch의 AWS 서비스 상태가 정상인지 확인합니다.
2. 리전 `<region>`에서 Batch 작업 큐 `<job-queue-name>`을 조회하고 큐 구성, 컴퓨팅 환경 연결, 큐 상태를 검사하여 큐가 "VALID" 상태인지 확인합니다.
3. 작업 큐 `<job-queue-name>`과 연결된 Batch 컴퓨팅 환경 `<compute-environment-name>`을 조회하고 컴퓨팅 환경 상태, 인스턴스 구성, 리소스 할당을 검사하여 컴퓨팅 환경이 "VALID" 상태인지 확인합니다.
4. Batch 이벤트가 포함된 CloudWatch Logs 로그 그룹을 쿼리하고 작업 제출 실패 패턴, 작업 시작 오류 또는 컴퓨팅 환경 오류를 필터링하여 오류 메시지 세부 정보를 포함합니다.
5. 제출된 작업에 대한 Batch 작업 정의 `<job-definition-arn>`을 조회하고 작업 정의 구성, 리소스 요구사항, 컨테이너 구성을 검사하여 작업 정의가 유효한지 확인합니다.
6. 큐 `<job-queue-name>`의 Batch 작업을 나열하고 작업 상태, 작업 제출 타임스탬프, 작업 실패 이유를 확인하여 작업 상태 패턴을 분석합니다.
7. Batch 컴퓨팅 환경 `<compute-environment-name>` 컴퓨팅 리소스를 조회하고 컴퓨팅 리소스가 사용 가능한지 확인하여 용량 제약이 작업 시작을 방해하는지 확인합니다.
8. Batch가 작업 실행에 사용하는 IAM 역할 `<role-name>`을 조회하고 IAM 권한을 확인하여 권한 문제가 작업 시작을 방해하는지 확인합니다.
9. CloudTrail 이벤트가 포함된 CloudWatch Logs 로그 그룹을 쿼리하고 지난 24시간 이내 `<job-queue-name>`과 관련된 Batch 작업 큐 또는 컴퓨팅 환경 수정 이벤트를 필터링하여 구성 변경을 확인합니다.

## 진단

1. **4단계의 CloudWatch Logs 분석**: 작업 제출 실패 패턴과 오류 메시지에 대한 Batch 이벤트 로그를 검토합니다. CloudWatch Logs가 "compute environment capacity" 또는 "insufficient resources" 오류를 나타내면 컴퓨팅 환경에 용량이 부족합니다(3단계 데이터로 진행). CloudWatch Logs가 "InvalidParameterException" 또는 "job definition" 오류를 표시하면 작업 정의가 잘못 구성되었습니다(5단계 데이터로 진행). 로그가 결론적이지 않으면 2단계로 계속합니다.

2. **8단계의 IAM 권한 확인**: 문제가 CloudWatch Logs에서 접근 거부 또는 권한 오류를 포함하는 경우 IAM 역할 권한을 먼저 확인합니다. IAM 역할 `<role-name>`에 `batch:SubmitJob`, `ecs:RunTask` 또는 필요한 서비스 연결 역할 권한이 없으면 권한 부족이 작업 실행을 차단하고 있습니다. IAM 권한이 올바른 것으로 보이면 3단계로 계속합니다.

3. **3단계의 컴퓨팅 환경 상태 평가**: 3단계의 컴퓨팅 환경이 "VALID" 또는 "ENABLED" 이외의 상태를 표시하면 컴퓨팅 환경 문제가 작업 시작을 방해하고 있습니다. 4단계의 CloudWatch Logs가 작업 실패 5분 이내에 상관되는 컴퓨팅 리소스 오류를 표시하면 리소스 할당이 근본 원인입니다. 컴퓨팅 환경이 정상이면 4단계로 계속합니다.

4. **2단계의 작업 큐 구성 상관관계**: 2단계의 작업 큐 상태가 "VALID"가 아니거나 연결된 컴퓨팅 환경이 없으면 큐 잘못된 구성이 작업을 차단하고 있습니다. 작업 시작 실패 타임스탬프를 9단계의 CloudTrail 이벤트와 비교합니다 - 큐 수정이 실패 5분 이내에 발생한 경우 최근 구성 변경이 문제를 유발했습니다. 큐 구성이 유효하면 5단계로 계속합니다.

5. **5단계의 작업 정의 검증**: 5단계의 작업 정의가 유효하지 않은 컨테이너 구성, 누락된 필수 파라미터 또는 7단계의 컴퓨팅 환경 용량을 초과하는 리소스 요구사항을 표시하면 작업 정의 오류가 시작을 방해하고 있습니다. 9단계의 작업 정의 수정 타임스탬프를 실패 시작과 상관시킵니다 - 실패가 시작되기 30분 이내에 수정이 발생한 경우 최근 변경이 문제를 도입했습니다.

**상관관계를 찾을 수 없는 경우**: 6단계의 작업 상태 패턴을 사용하여 분석을 7일로 확장합니다. 실패가 지속적이면 구성 문제를 의심합니다. 실패가 간헐적이면 7단계의 리소스 가용성 또는 ECS 클러스터 상태를 의심합니다. 1단계의 Batch 서비스 상태를 확인하고 작업 스케줄링에 영향을 미치는 컴퓨팅 환경 인스턴스 유형 제약 또는 작업 큐 우선순위 충돌을 확인합니다.
