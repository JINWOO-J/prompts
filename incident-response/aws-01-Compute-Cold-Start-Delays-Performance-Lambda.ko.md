---
category: incident-response
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/AWS%20Playbooks/01-Compute/Cold-Start-Delays-Performance-Lambda.md)'
role: SRE / AWS Incident Response
origin: scoutflo
extract_date: 2026-03-05
tags:
- cloudwatch
- cold
- compute
- delays
- incident-response
- k8s-service
- lambda
- performance
- start
- sts
- vpc
---

# Lambda Cold Start 지연으로 인한 성능 저하 (Cold Start Delays Performance)

## 의미

Lambda Cold Start 지연은 함수 초기화에 시간이 오래 걸리거나, 패키지 크기가 커서 시작 시간이 증가하거나, 런타임 초기화가 느리거나, Provisioned Concurrency가 설정되지 않았거나, 함수 코드에 무거운 초기화 로직이 있거나, Lambda VPC 설정이 지연을 추가하여 성능 저하를 유발합니다(LambdaDuration 또는 LambdaColdStart 같은 지연 알람 트리거). Lambda 함수 호출 시 높은 지연이 발생하고, Cold Start 지연으로 응답 시간이 증가하며, 유휴 기간 후 첫 번째 요청이 느려집니다. 이는 서버리스 컴퓨팅 계층에 영향을 미치며 애플리케이션 성능에 영향을 줍니다. 일반적으로 초기화 오버헤드, 패키지 크기, 또는 동시성 설정 누락이 원인이며, Lambda 컨테이너 이미지를 사용하는 경우 Cold Start 시간이 더 길어질 수 있고 애플리케이션이 일관되지 않은 성능을 경험할 수 있습니다.

## 영향

Lambda 함수 호출 시 높은 지연 발생; Cold Start 지연으로 응답 시간 증가; 사용자 대면 지연 저하; 유휴 기간 후 첫 번째 요청 느림; Lambda 함수 성능 불일치; LambdaDuration 또는 LambdaColdStart 알람 발생; 애플리케이션 사용자 경험 영향; 함수 시작 시간이 허용 임계값 초과. Lambda 함수 성능이 Cold 호출과 Warm 호출 간에 불일치; Lambda 컨테이너 이미지를 사용하는 경우 Cold Start가 상당히 더 오래 걸릴 수 있음; 일관되지 않은 지연으로 인해 애플리케이션에 에러 또는 성능 저하 발생 가능; 사용자 대면 서비스에서 응답 시간 급증 경험.

## 플레이북

1. Lambda 함수 `<function-name>`이 존재하고 리전 `<region>`에서 Lambda의 AWS 서비스 상태가 정상인지 확인합니다.
2. Lambda 함수 `<function-name>`의 CloudWatch 메트릭(Duration, InitDuration, ColdStartDuration 포함)을 최근 1시간 동안 조회하여 Cold Start 패턴을 파악하고, Cold Start 빈도와 지속 시간을 분석합니다.
3. 리전 `<region>`의 Lambda 함수 `<function-name>`을 조회하여 패키지 크기, 런타임 설정, Provisioned Concurrency 설정, 메모리 할당, 배포 패키지 유형(ZIP vs 컨테이너 이미지)을 검사합니다.
4. 로그 그룹 `/aws/lambda/<function-name>`의 CloudWatch Logs를 조회하여 초기화 로그, Cold Start 지표, 또는 시작 시간 패턴(InitDuration 메트릭 포함)을 필터링합니다.
5. Lambda 함수 `<function-name>`과 연관된 CloudWatch 알람을 Duration 메트릭으로 조회하고 지연 관련 ALARM 상태의 알람을 확인하며, 알람 임계값 설정을 검증합니다.
6. Lambda 함수 `<function-name>`의 CloudWatch 메트릭(Invocations, ConcurrentExecutions 포함)을 조회하여 호출 빈도를 파악하고, Cold Start를 유발하는 유휴 기간을 식별하기 위해 호출 패턴을 분석합니다.
7. Lambda 함수 `<function-name>`의 VPC 설정을 조회하여 함수가 VPC에 설정되어 있는지 확인하고, VPC 설정이 초기화 지연을 추가하는지 점검합니다.
8. Lambda 함수 `<function-name>`의 배포 패키지 유형을 조회하여 패키지 유형(ZIP vs 컨테이너 이미지)을 확인하고, 컨테이너 이미지 배포가 더 긴 Cold Start 시간을 가지는지 점검합니다.
9. 메모리 변경이 있었다면 Lambda 함수 `<function-name>`의 CloudWatch 메트릭(InitDuration 포함)을 다른 메모리 할당 간에 비교하여, 메모리와 Cold Start 지속 시간 간의 상관관계를 분석합니다.

## 진단

1. 플레이북 5단계의 CloudWatch 알람 이력을 분석하여 LambdaDuration 또는 LambdaColdStart 임계값이 처음 위반된 시점을 파악합니다. 이 알람 타임스탬프가 이후 모든 분석의 상관관계 기준선이 됩니다.

2. 플레이북 2단계의 CloudWatch 메트릭이 알람 시점 전후로 높은 InitDuration 값을 보이면, 플레이북 3단계의 함수 설정에서 초기화를 연장시킨 최근 패키지 크기 증가 또는 런타임 변경을 검사합니다.

3. InitDuration은 정상이지만 Cold Start 빈도가 높은 경우, 플레이북 6단계의 호출 패턴을 확인합니다. ConcurrentExecutions가 함수 유휴 타임아웃을 초과하는 간격으로 드문 트래픽을 보이면, 드문 호출이 Cold Start를 유발하고 있습니다.

4. 호출 패턴이 일관된 경우, 플레이북 7단계의 VPC 설정을 확인합니다. 함수가 VPC에 연결되어 있고 VPC 설정 후 Cold Start가 증가했다면, ENI 생성 지연이 원인일 가능성이 높습니다.

5. VPC가 설정되지 않은 경우, 플레이북 8단계의 배포 패키지 유형을 검사합니다. 컨테이너 이미지를 사용하는 경우, ZIP 배포와 InitDuration을 비교합니다 - 컨테이너 이미지는 이미지 레이어 로딩으로 인해 일반적으로 더 긴 Cold Start를 가집니다.

6. Cold Start가 Provisioned Concurrency 변경(플레이북 3단계)과 상관관계가 있는 경우, Provisioned Concurrency가 축소되거나 제거되어 함수가 온디맨드 초기화에 의존하게 되었는지 확인합니다.

7. Cold Start 지속 시간이 메모리 할당에 따라 달라지는 경우(플레이북 9단계), 메모리 부족이 초기화 중 CPU를 제한하고 있을 수 있습니다 - Lambda는 메모리에 비례하여 CPU를 할당합니다.

상관관계를 찾을 수 없는 경우: 분석을 24시간으로 확장하고, 플레이북 4단계의 CloudWatch Logs에서 초기화 에러 또는 느린 의존성 로딩을 검토하고, Java 런타임의 Lambda SnapStart 적격 여부를 확인하고, 컨테이너 이미지 레이어 캐싱 설정을 검증합니다. Cold Start 지연은 큰 패키지, 무거운 초기화 로직, VPC ENI 지연, 또는 컨테이너 이미지 오버헤드로 인해 발생할 수 있습니다.
