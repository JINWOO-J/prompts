---
category: incident-response
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/AWS%20Playbooks/04-Networking/Route-Not-Matching-Requests-API-Gateway.md)'
role: SRE / AWS Incident Response
origin: scoutflo
extract_date: 2026-03-05
tags:
- cloudwatch
- gateway
- incident-response
- k8s-service
- matching
- networking
- performance
- requests
- route
- sts
---

# API Gateway Route Not Matching Requests - API Gateway 라우트 요청 불일치

## 의미

API Gateway 라우트가 요청과 일치하지 않는 현상(라우팅 실패 또는 APIGatewayRouteMismatch 경보 트리거)은 라우트 구성이 잘못되었거나, 라우트 경로 패턴이 요청 경로와 일치하지 않거나, HTTP 메서드 매핑이 잘못되었거나, 라우트 우선순위 충돌이 존재하거나, 라우트 통합이 잘못 구성되었거나, API Gateway 라우트 경로 파라미터가 잘못 구성되었을 때 발생합니다.
 API Gateway 라우트가 요청과 일치하지 않고, 요청이 404 Not Found 오류를 반환하며, 라우트 라우팅이 실패합니다. 이는 API 계층에 영향을 미치며 엔드포인트 접근을 차단합니다. 일반적으로 라우트 구성 문제, 경로 패턴 문제 또는 통합 오류가 원인입니다.

## 영향

API Gateway 라우트가 요청과 일치하지 않습니다. 요청이 404 Not Found 오류를 반환합니다. 라우트 라우팅이 실패합니다. API 엔드포인트에 접근할 수 없습니다. 라우트 구성이 효과가 없습니다. 요청 라우팅이 잘못됩니다. API 통합이 실패합니다. 사용자 대면 라우팅 오류가 발생합니다.

## 플레이북

1. API Gateway API `<api-id>`가 존재하고 리전 `<region>`의 API Gateway AWS 서비스 상태가 정상인지 확인합니다.
2. 리전 `<region>`의 API Gateway REST API `<api-id>` 또는 HTTP API `<api-id>`를 조회하여 라우트 구성, 경로 패턴, HTTP 메서드 매핑, 라우트 우선순위를 점검합니다.
3. API Gateway 접근 로그가 포함된 CloudWatch Logs에서 API `<api-id>` 관련 404 오류 패턴이나 라우트 불일치 이벤트를 필터링합니다.
4. API Gateway API `<api-id>`의 CloudWatch 지표(4XXError, Count)를 최근 1시간 동안 조회하여 라우팅 오류 패턴을 파악합니다.
5. API `<api-id>`의 API Gateway 라우트를 나열하고 라우트 경로 패턴, 메서드 구성, 라우트 통합 설정을 확인합니다.
6. API Gateway 실행 로그가 포함된 CloudWatch Logs에서 라우트 일치 실패나 라우팅 결정 패턴을 필터링합니다.
7. API Gateway API `<api-id>`의 라우트 경로 파라미터 구성을 조회하여 경로 파라미터가 올바르게 구성되어 있는지 확인합니다.
8. API Gateway API `<api-id>`의 라우트 통합 구성을 조회하여 통합 설정을 검증합니다.
9. CloudTrail 이벤트가 포함된 CloudWatch Logs에서 최근 24시간 이내 API `<api-id>` 관련 API Gateway 라우트 또는 경로 패턴 변경 이벤트를 필터링합니다.

## 진단

1. API Gateway 접근 로그가 포함된 CloudWatch Logs(플레이북 3단계)를 분석하여 구체적인 404 오류 패턴과 실패한 요청 경로를 파악합니다. 접근 로그에서 존재해야 할 경로에 대한 요청이 표시되면 라우트 경로 패턴이 요청 형식과 일치하지 않을 수 있습니다.

2. CloudWatch 지표(플레이북 4단계)를 검토하여 라우팅 오류 패턴을 파악합니다. 4XX 오류가 갑자기 증가했다면 최근 라우트 구성 변경과 상관 분석합니다.

3. API Gateway 라우트 구성(플레이북 2단계)을 확인하여 라우트 경로 패턴, HTTP 메서드, 라우트 우선순위를 검증합니다. 경로 패턴이 잘못된 구문을 사용하면(특히 HTTP API vs REST API의 경로 파라미터) 요청이 라우트와 일치하지 않습니다.

4. API Gateway 실행 로그(플레이북 6단계)를 검토하여 실패한 요청에 대한 라우팅 결정 로직을 이해합니다.

5. 라우트 경로 파라미터 구성(플레이북 7단계)을 확인하여 경로 파라미터가 올바르게 정의되어 있는지 검증합니다. HTTP API는 {proxy+} 구문을 사용하고 REST API는 다른 형식을 사용할 수 있습니다.

6. CloudTrail 이벤트(플레이북 9단계)와 라우트 불일치 타임스탬프를 5분 이내로 상관 분석합니다.

상관관계를 찾을 수 없는 경우: 기간을 24시간으로 확장하고, 라우트 통합 구성 및 API Gateway 스테이지 설정을 포함한 대안적 증거 소스를 검토합니다.