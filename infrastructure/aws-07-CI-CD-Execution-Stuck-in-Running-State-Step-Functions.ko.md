---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/AWS%20Playbooks/07-CI-CD/Execution-Stuck-in-Running-State-Step-Functions.md)'
role: SRE / AWS Incident Response
origin: scoutflo
extract_date: 2026-03-05
tags:
- ci-cd
- execution
- functions
- infrastructure
- k8s-service
- lambda
- monitoring
- performance
- running
- state
- step
- sts
- stuck
---

# AWS Step Functions 실행이 실행 중 상태에서 멈춤

## 의미

AWS Step Functions 실행이 실행 중 상태에서 멈추는(워크플로우 실패 또는 StepFunctionsExecutionStuck 알람 트리거) 이유는 실행이 태스크 토큰을 기다리고 있거나, Lambda 함수 타임아웃이 완료를 방해하거나, 상태 머신 정의에 오류가 있거나, 실행 입력이 유효하지 않거나, Step Functions 서비스가 실행 중 오류를 만나거나, Step Functions 실행 시간 제한이 초과되었기 때문입니다. Step Functions 실행이 멈추고, 워크플로우 자동화가 차단되며, 실행 상태 전환이 실패합니다. 이는 워크플로우 오케스트레이션 및 서버리스 계층에 영향을 미치며 워크플로우 실행을 차단합니다. 일반적으로 상태 머신 정의 문제, Lambda 함수 문제 또는 태스크 토큰 실패로 인해 발생합니다. Express 워크플로우와 Standard 워크플로우에서 Step Functions를 사용하는 경우 실행 동작이 다르며 애플리케이션에서 실행 지연이 발생할 수 있습니다.

## 영향

Step Functions 실행 멈춤; 워크플로우 자동화 차단; 실행 상태 전환 실패; 워크플로우 프로세스 완료 불가; 실행 자동화 무효; 상태 머신 실행 중단; 워크플로우 신뢰성 손상; 실행 모니터링에서 멈춤 상태 표시. StepFunctionsExecutionStuck 알람이 발생할 수 있으며, Express 워크플로우와 Standard 워크플로우에서 실행 동작이 다르고, 멈춘 워크플로우로 인해 애플리케이션에서 오류 또는 성능 저하가 발생할 수 있으며, 워크플로우 자동화가 완전히 차단될 수 있습니다.

## 플레이북

1. Step Functions 실행 `<execution-arn>`이 존재하고 리전 `<region>`에서 Step Functions의 AWS 서비스 상태가 정상인지 확인합니다.
2. 리전 `<region>`에서 Step Functions 실행 `<execution-arn>`을 조회하고 실행 상태, 실행 이력, 현재 상태, 실행 입력을 검사하여 실행이 "RUNNING" 상태인지 확인합니다.
3. 실행 `<execution-arn>`에 대한 Step Functions 상태 머신 `<state-machine-arn>`을 조회하고 상태 머신 정의, 상태 구성, 오류 처리 설정을 검사하여 상태 머신 정의를 확인합니다.
4. Step Functions 실행 로그가 포함된 CloudWatch Logs 로그 그룹을 쿼리하고 실행 멈춤 패턴, 상태 전환 오류 또는 타임아웃 이벤트를 필터링하여 오류 메시지 세부 정보를 포함합니다.
5. 지난 24시간 동안 Step Functions 상태 머신 `<state-machine-arn>`의 ExecutionsFailed 및 ExecutionsTimedOut을 포함한 CloudWatch 메트릭을 조회하여 실행 패턴을 식별하고 실행 메트릭을 분석합니다.
6. 실행 `<execution-arn>`의 Step Functions 실행 이벤트를 나열하고 실행 이벤트 이력, 상태 전환, 오류 이벤트를 확인하여 이벤트 연대기를 분석합니다.
7. Step Functions 실행 `<execution-arn>` 태스크 토큰 상태를 조회하고 태스크 토큰 콜백 상태를 확인하여 태스크 토큰 콜백이 대기 중인지 확인합니다.
8. 실행이 Lambda 태스크를 포함하는 경우 Lambda 함수 `<function-name>`을 조회하고 Lambda 함수 실행 상태를 확인하여 Lambda 타임아웃이 실행에 영향을 미치는지 확인합니다.
9. CloudTrail 이벤트가 포함된 CloudWatch Logs 로그 그룹을 쿼리하고 지난 24시간 이내 `<execution-arn>`과 관련된 Step Functions 상태 머신 정의 또는 실행 수정 이벤트를 필터링하여 구성 변경을 확인합니다.

## 진단

1. **4단계 및 6단계의 CloudWatch Logs 및 실행 이벤트 분석**: 현재 상태와 오류 패턴에 대한 Step Functions 실행 로그를 검토합니다. 4단계의 CloudWatch Logs가 실행이 특정 태스크 상태에서 대기 중임을 나타내면 태스크 유형을 식별합니다. 6단계의 실행 이벤트가 마지막 전환이 후속 이벤트 없이 "Task" 상태로의 전환이었음을 표시하면 실행이 태스크 완료를 기다리고 있습니다. 로그가 타임아웃 경고를 표시하면 2단계로 계속합니다.

2. **7단계의 태스크 토큰 상태 확인**: 실행이 `.waitForTaskToken` 태스크를 포함하고 7단계에서 콜백 없이 대기 중인 태스크 토큰을 표시하면 누락된 태스크 토큰 콜백이 멈춤 상태를 유발하고 있습니다. `SendTaskSuccess` 또는 `SendTaskFailure`를 보내는 외부 시스템이 작동 중인지 확인합니다. 태스크 토큰이 관련되지 않으면 3단계로 계속합니다.

3. **8단계의 Lambda 함수 상태 평가**: 멈춤 상태가 Lambda 호출을 포함하는 경우 8단계의 Lambda 함수 상태를 확인합니다. CloudWatch Logs가 실행이 멈춘 시점 5분 이내에 상관되는 Lambda 함수 타임아웃 또는 콜드 스타트 문제를 표시하면 Lambda 성능이 근본 원인입니다. 3단계의 상태 머신 타임아웃 설정에 대한 Lambda 타임아웃 구성을 검토합니다. Lambda가 정상이면 4단계로 계속합니다.

4. **3단계의 상태 머신 정의 검토**: 3단계의 상태 머신 정의에 무한 루프, 누락된 오류 처리 또는 적절한 전환 정의가 없는 상태가 포함된 경우 정의 오류가 멈춤 상태를 유발하고 있습니다. 9단계의 CloudTrail 이벤트를 확인합니다 - 실행 시작 30분 이내에 정의 수정이 발생한 경우 최근 변경이 문제를 도입했을 수 있습니다.

5. **5단계의 실행 메트릭 분석**: CloudWatch 메트릭이 멈춘 실행과 상관되는 ExecutionsTimedOut 증가 또는 ExecutionsFailed 패턴을 표시하면 체계적인 문제가 상태 머신에 영향을 미치고 있습니다. 상태 머신 간 실행 패턴을 비교합니다 - 여러 상태 머신이 유사한 문제를 표시하면 계정 전체 Step Functions 서비스 문제가 원인일 수 있습니다.

**상관관계를 찾을 수 없는 경우**: 실행 상태 데이터를 사용하여 분석을 30일로 확장합니다. Express 워크플로우의 경우 5분 실행 제한을 확인합니다. Standard 워크플로우의 경우 1년 실행 제한에 접근하고 있지 않은지 확인합니다. 처리되지 않은 예외에 대한 Lambda 함수 실행 로그를 검토하고 태스크 토큰 콜백 전달 메커니즘이 올바르게 작동하는지 확인합니다.
