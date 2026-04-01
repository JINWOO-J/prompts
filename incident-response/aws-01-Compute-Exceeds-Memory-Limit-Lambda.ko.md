---
category: incident-response
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/AWS%20Playbooks/01-Compute/Exceeds-Memory-Limit-Lambda.md)'
role: SRE / AWS Incident Response
origin: scoutflo
extract_date: 2026-03-05
tags:
- cloudwatch
- compute
- exceeds
- incident-response
- k8s-deployment
- k8s-service
- lambda
- limit
- memory
- performance
- sts
---

# Lambda 함수 메모리 한도 초과 (Exceeds Memory Limit)

## 의미

Lambda 함수가 메모리 한도를 초과합니다(메모리 부족 에러 또는 LambdaMemoryError 알람 트리거). 함수 메모리 할당이 워크로드에 비해 부족하거나, 메모리 누수로 점진적 메모리 증가가 발생하거나, 함수가 메모리를 초과하는 대용량 데이터셋을 처리하거나, 동시 실행이 가용 메모리를 소진하거나, Lambda 함수 메모리 설정이 너무 낮기 때문입니다. Lambda 함수 실행이 메모리 부족 에러로 실패하고, 함수 호출이 종료되며, CloudWatch 메트릭이 메모리 사용률 한도 초과를 표시합니다. 이는 서버리스 컴퓨팅 계층에 영향을 미치며 함수 실행을 차단합니다. 일반적으로 메모리 할당 이슈, 메모리 누수, 또는 데이터 처리 요구사항이 원인이며, Lambda 컨테이너 이미지를 사용하는 경우 메모리 동작이 다를 수 있고 애플리케이션에서 함수 실행 실패가 발생할 수 있습니다.

## 영향

Lambda 함수 실행 실패; 메모리 부족 에러 발생; 함수 호출 종료; 애플리케이션 워크플로우 중단; Lambda 함수 에러 증가; LambdaMemoryError 알람 발생; 재시도 실패; 함수가 처리를 완료할 수 없음; 서비스 안정성 저하. CloudWatch Logs에 Lambda 함수 메모리 에러 표시; Lambda 컨테이너 이미지를 사용하는 경우 메모리 할당 동작이 다를 수 있음; 불완전한 함수 실행으로 인해 애플리케이션에 에러 또는 성능 저하 발생 가능; 다운스트림 서비스가 예상 데이터를 수신하지 못할 수 있음.

## 플레이북

1. Lambda 함수 `<function-name>`이 존재하고 리전 `<region>`에서 Lambda의 AWS 서비스 상태가 정상인지 확인합니다.
2. Lambda 함수 `<function-name>`의 CloudWatch 메트릭(MemoryUtilization, Duration, Errors 포함)을 최근 1시간 동안 조회하여 메모리 사용 패턴을 파악하고, 메모리 사용률 추이를 분석합니다.
3. 리전 `<region>`의 Lambda 함수 `<function-name>`을 조회하여 메모리 설정, 타임아웃 설정, 함수 코드 크기, 배포 패키지 유형(ZIP vs 컨테이너 이미지)을 검사합니다.
4. 로그 그룹 `/aws/lambda/<function-name>`의 CloudWatch Logs를 조회하여 메모리 부족 에러 패턴, 메모리 관련 예외, 또는 함수 종료 에러(메모리 사용률 로그 포함)를 필터링합니다.
5. Lambda 함수 `<function-name>`과 연관된 CloudWatch 알람을 Errors 또는 MemoryUtilization 메트릭으로 조회하고 ALARM 상태의 알람을 확인하며, 알람 임계값 설정을 검증합니다.
6. Lambda 함수 `<function-name>`의 CloudWatch 메트릭(ConcurrentExecutions 포함)을 조회하여 동시 실행이 메모리 고갈에 기여하는지 확인하고, 동시성 패턴을 분석합니다.
7. Lambda 함수 `<function-name>`의 예약 동시성 설정을 조회하여 예약 동시성 설정을 확인하고, 동시성 제한이 메모리 가용성에 영향을 미치는지 점검합니다.
8. 로그 그룹 `/aws/lambda/<function-name>`의 CloudWatch Logs를 조회하여 메모리 할당 에러 또는 메모리 관련 예외 패턴을 필터링하고, 메모리 누수 지표를 확인합니다.
9. 배포가 있었다면 Lambda 함수 `<function-name>`의 CloudWatch 메트릭(MemoryUtilization 포함)을 다른 함수 버전 간에 비교하여, 메모리 사용량 변화를 분석합니다.

## 진단

1. 플레이북 5단계의 CloudWatch 알람 이력을 분석하여 LambdaMemoryError 또는 Error 알람이 처음 트리거된 시점을 파악합니다. 이 타임스탬프가 메모리 고갈이 시작된 시점을 확립하고 상관관계 기준선이 됩니다.

2. 플레이북 2단계의 CloudWatch 메트릭이 알람 전에 MemoryUtilization이 지속적으로 100%에 가까운 경우, 플레이북 3단계의 함수 메모리 설정과 비교합니다. 설정된 메모리가 변경되지 않았지만 사용률이 임계값까지 올라갔다면, 워크로드 메모리 요구사항이 증가한 것입니다.

3. 플레이북 2단계에서 MemoryUtilization이 함수 Duration 동안 점진적으로 증가하는 경우, 플레이북 4단계와 8단계의 CloudWatch Logs에서 메모리 할당 패턴을 검사합니다. 단일 실행 내에서의 점진적 증가는 함수 코드의 메모리 누수를 나타냅니다.

4. 메모리 에러가 ConcurrentExecutions 급증(플레이북 6단계)과 상관관계가 있는 경우, 예약 동시성 설정(플레이북 7단계)이 동시 실행을 제한하여 요청이 큐에 쌓이고 타임아웃되는지 확인합니다.

5. 배포 후 메모리 에러가 시작된 경우, 에러 타임스탬프를 함수 버전 변경(플레이북 9단계)과 비교합니다. 배포 후 MemoryUtilization이 증가했다면, 새 코드가 메모리 집약적 작업 또는 누수를 도입한 것입니다.

6. 메모리 에러가 지속적이지 않고 간헐적인 경우, 플레이북 4단계의 CloudWatch Logs에서 특정 입력 패턴을 분석합니다. 대용량 페이로드 처리 또는 특정 이벤트 유형이 메모리 고갈을 트리거할 수 있습니다.

7. 컨테이너 이미지를 사용하는 경우(플레이북 3단계), 컨테이너 오버헤드가 기본 메모리를 소비할 수 있습니다 - 컨테이너 초기화 후 가용 메모리를 ZIP 기반 배포와 비교합니다.

상관관계를 찾을 수 없는 경우: 분석을 24시간으로 확장하고, CloudWatch Logs에서 메모리 프로파일링 데이터를 검토하고, 입력 데이터 크기 패턴을 확인하고, 메모리에 영향을 줄 수 있는 Lambda 임시 스토리지 제약을 검증하고, Java 함수의 Lambda SnapStart 메모리 할당을 검사합니다.
