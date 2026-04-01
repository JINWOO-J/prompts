---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/AWS%20Playbooks/07-CI-CD/Stuck-in-Progress-CodePipeline.md)'
role: SRE / AWS Incident Response
origin: scoutflo
extract_date: 2026-03-05
tags:
- ci-cd
- cloudwatch
- codepipeline
- iam
- infrastructure
- k8s-deployment
- k8s-service
- performance
- pipeline
- progress
- sts
- stuck
---

# AWS CodePipeline 진행 중 멈춤

## 의미

CodePipeline 실행이 진행 중 상태에서 멈추는(파이프라인 실행 지연 또는 CodePipelineExecutionStuck 알람 트리거) 이유는 파이프라인 단계가 수동 승인을 기다리고 있거나, 단계 액션이 실패하거나 타임아웃되거나, IAM 권한이 단계 액션에 부족하거나, 소스 또는 빌드 아티팩트가 사용 불가하거나, 배포 단계가 완료될 수 없거나, 파이프라인 단계 전환 조건이 충족되지 않았기 때문입니다. CodePipeline 실행이 지연되고, 배포가 차단되며, CI/CD 워크플로우가 완료될 수 없습니다. 이는 CI/CD 계층에 영향을 미치며 릴리스를 차단합니다. 일반적으로 승인 게이트, 액션 실패 또는 아티팩트 가용성 문제로 인해 발생합니다. 여러 단계와 함께 CodePipeline을 사용하는 경우 멈춤 상태가 연쇄될 수 있으며 애플리케이션에서 배포 지연이 발생할 수 있습니다.

## 영향

CodePipeline 실행 지연; 배포 차단; CI/CD 워크플로우 완료 불가; 파이프라인 단계 중단; 수동 개입 필요; 배포 자동화 실패; 파이프라인 실행 이력에 멈춤 상태 표시; 릴리스 프로세스 중단. CodePipelineExecutionStuck 알람이 발생할 수 있으며, 여러 단계와 함께 CodePipeline을 사용하는 경우 멈춤 상태가 연쇄될 수 있고, 차단된 배포로 인해 애플리케이션에서 오류 또는 성능 저하가 발생할 수 있으며, 릴리스 프로세스가 완전히 중단될 수 있습니다.

## 플레이북

1. 파이프라인 `<pipeline-name>`이 존재하고 리전 `<region>`에서 CodePipeline의 AWS 서비스 상태가 정상인지 확인합니다.
2. 리전 `<region>`에서 CodePipeline `<pipeline-name>`을 조회하고 실행 이력, 현재 실행 상태, 단계 액션 상태를 검사하여 어떤 단계가 멈춰 있는지 확인합니다.
3. CodePipeline 실행 로그가 포함된 CloudWatch Logs 로그 그룹을 쿼리하고 파이프라인 `<pipeline-name>`과 관련된 오류 패턴, 타임아웃 이벤트 또는 단계 실패 메시지를 필터링하여 멈춤 단계 세부 정보를 포함합니다.
4. 지난 24시간 동안 CodePipeline `<pipeline-name>`의 FailedExecutions 및 SucceededExecutions를 포함한 CloudWatch 메트릭을 조회하여 실행 패턴을 식별하고 실행 이력을 분석합니다.
5. CodePipeline `<pipeline-name>`에서 사용하는 IAM 역할 `<role-name>`을 조회하고 파이프라인 단계 액션에 대한 정책 권한을 검사하여 IAM 권한을 확인합니다.
6. CodePipeline `<pipeline-name>`에 의해 트리거된 빌드에 대한 CodeBuild 빌드 이력을 나열하고 파이프라인을 중단시킬 수 있는 빌드 실패 또는 오류를 확인하여 빌드 상태를 분석합니다.
7. CodePipeline `<pipeline-name>` 단계 구성을 조회하고 수동 승인 게이트를 확인하여 수동 승인이 실행을 차단하고 있는지 확인합니다.
8. CodePipeline `<pipeline-name>` 아티팩트 구성을 조회하고 아티팩트 가용성을 확인하여 아티팩트가 누락되었거나 사용 불가한지 확인합니다.
9. CloudTrail 이벤트가 포함된 CloudWatch Logs 로그 그룹을 쿼리하고 지난 24시간 이내 파이프라인 `<pipeline-name>`과 관련된 CodePipeline 단계 또는 액션 수정 이벤트를 필터링하여 구성 변경을 확인합니다.

## 진단

1. CodePipeline 실행 이력(플레이북 2단계)을 분석하여 어떤 단계가 멈춰 있는지와 실행이 멈춤 상태에 진입한 시점을 식별합니다. 단계 이름과 타임스탬프가 상관관계 기준선을 수립합니다.

2. 파이프라인 구성(플레이북 7단계)이 멈춤 단계가 수동 승인 액션임을 표시하면 실행이 사람의 승인을 기다리고 있습니다. 이는 수동 개입이 필요한 예상된 동작입니다.

3. 실행 로그(플레이북 3단계)가 멈춤 단계가 빌드 또는 배포 액션임을 표시하면 CodeBuild 빌드 이력(플레이북 6단계)을 확인합니다. 연결된 빌드가 실행 중이거나 실패한 경우 빌드 완료 또는 실패가 파이프라인 진행을 차단하고 있습니다.

4. 아티팩트 구성(플레이북 8단계)이 아티팩트 접근 문제를 표시하면 S3 버킷 권한을 확인합니다. 아티팩트 가용성 누락이 후속 단계가 필요한 입력을 검색하는 것을 차단합니다.

5. IAM 역할 권한(플레이북 5단계)이 멈춤 타임스탬프 전후로 수정된 경우(플레이북 9단계의 CloudTrail 확인) 단계 액션(CodeBuild, CodeDeploy, Lambda 호출)에 대한 누락된 권한이 실행을 차단하고 있습니다.

6. CloudWatch 메트릭(플레이북 4단계)이 이전에는 성공적인 실행을 표시하지만 현재는 실패를 표시하면 변경을 식별하기 위해 전후 파이프라인 구성을 비교합니다.

7. 멈춤 상태가 소스 단계에 있으면 소스 저장소 접근(GitHub, CodeCommit, S3)을 확인합니다. 인증 또는 연결 문제가 아티팩트 검색을 차단합니다.

상관관계를 찾을 수 없는 경우: 분석을 48시간으로 확장하고, 수동 승인 게이트 요구사항을 확인하고, 외부 서비스 통합 상태를 확인하고, 크로스 리전 아티팩트 복제 지연을 검사하고, 단계 전환 조건 구성을 검토합니다.
