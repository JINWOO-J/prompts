---
category: incident-response
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/AWS%20Playbooks/04-Networking/Throttling-Requests-API-Gateway.md)'
role: SRE / AWS Incident Response
origin: scoutflo
extract_date: 2026-03-05
tags:
- capacity
- cloudwatch
- gateway
- incident-response
- k8s-service
- lambda
- networking
- performance
- requests
- sts
- throttling
---

# API Gateway Throttling Requests - API Gateway 요청 스로틀링

## 의미

API Gateway가 요청을 스로틀링하는 현상(429 Too Many Requests 오류 반환 또는 APIGatewayThrottling 경보 트리거)은 속도 제한 또는 버스트 제한이 초과되거나, 스로틀링 구성이 너무 제한적이거나, Lambda 동시성 제한에 도달하거나, 갑작스러운 트래픽 급증이 구성된 스로틀링 임계값을 초과하거나, API Gateway 사용 계획 스로틀링 제한에 도달할 때 발생합니다.
 API 요청이 스로틀링되고, 429 Too Many Requests 오류가 발생하며, 애플리케이션 요청이 실패합니다. 이는 API 계층에 영향을 미치며 서비스 가용성을 감소시킵니다.

## 영향

API 요청이 스로틀링됩니다. 429 Too Many Requests 오류가 발생합니다. API 가용성이 저하됩니다. 사용자 대면 오류가 증가합니다. API 속도 제한이 초과됩니다. 버스트 용량이 소진됩니다. 애플리케이션 요청이 실패합니다. 서비스 안정성에 영향을 미칩니다.

## 플레이북

1. API Gateway API `<api-id>`가 존재하고 배포되어 있으며, 리전 `<region>`의 API Gateway AWS 서비스 상태가 정상인지 확인합니다.
2. API Gateway API `<api-id>`의 CloudWatch 지표(4XXError, Count, ThrottleCount)를 최근 1시간 동안 조회하여 스로틀링 패턴을 파악합니다.
3. 리전 `<region>`의 API Gateway REST API `<api-id>` 또는 HTTP API `<api-id>`를 조회하여 스로틀링 구성, 속도 제한, 버스트 제한을 점검합니다.
4. API Gateway 접근 로그가 포함된 CloudWatch Logs에서 429 오류 패턴이나 스로틀링 관련 로그 항목을 필터링합니다.
5. API Gateway API `<api-id>`와 연관된 4XXError 또는 ThrottleCount 지표의 CloudWatch 경보를 조회하고 ALARM 상태인 경보를 확인합니다.
6. API Gateway `<api-id>`의 API 유형(REST API vs HTTP API)을 조회하여 유형별 스로틀링 동작 차이를 점검합니다.
7. API Gateway `<api-id>`의 사용 계획 구성을 조회하여 사용 계획 스로틀링 설정을 확인합니다.
8. API Gateway API `<api-id>`와 통합된 Lambda 함수의 동시성 지표를 나열하고 Lambda 스로틀링이 API 스로틀링에 기여하는지 확인합니다.
9. CloudTrail 이벤트가 포함된 CloudWatch Logs에서 최근 24시간 이내 API `<api-id>` 관련 API Gateway 스로틀링 구성 변경을 필터링합니다.

## 진단

1. CloudWatch 경보 이력(플레이북 5단계)을 분석하여 APIGatewayThrottling 또는 4XXError 경보가 처음 트리거된 시점을 파악합니다.

2. CloudWatch 지표(플레이북 2단계)에서 경보 시점 전후로 Count가 속도 제한을 초과하면 스로틀링 구성(플레이북 3단계)과 비교합니다. 구성된 속도/버스트 제한이 피크 트래픽보다 낮으면 부족한 제한이 근본 원인입니다.

3. CloudTrail에서 구성 변경(플레이북 9단계) 후 스로틀링이 발생했다면 속도 제한 감소 또는 사용 계획 변경이 스로틀링을 유발했는지 확인합니다.

4. 접근 로그(플레이북 4단계)에서 429 오류가 특정 API 키나 스테이지에 집중되면 사용 계획 구성(플레이북 7단계)을 확인합니다.

5. Lambda 동시성 지표(플레이북 8단계)에서 API 스로틀링과 동일한 타임스탬프에 스로틀링이 표시되면 Lambda 동시성 제한이 API 계층으로 전파되는 백엔드 스로틀링을 유발하고 있는 것입니다.

6. 스로틀링이 지속적이지 않고 간헐적인 경우(플레이북 2단계 추세) 피크 시간대에 버스트 용량이 소진되고 있는 것입니다.

상관관계를 찾을 수 없는 경우: 분석 기간을 24시간으로 확장하고, API 키별 스로틀링 제한을 검토하고, 계정 수준 API Gateway 스로틀링 할당량을 확인합니다.