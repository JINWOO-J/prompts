---
category: incident-response
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/AWS%20Playbooks/04-Networking/CORS-Issues-API-Gateway.md)'
role: SRE / AWS Incident Response
origin: scoutflo
extract_date: 2026-03-05
tags:
- cloudwatch
- cors
- gateway
- incident-response
- issues
- k8s-deployment
- k8s-service
- networking
- performance
- sts
---

# API Gateway CORS Issues - API Gateway CORS 문제

## 의미

API Gateway CORS(Cross-Origin Resource Sharing) 문제(CORS 오류 또는 APIGatewayCORS 오류 트리거)는 CORS 헤더가 구성되지 않았거나, 허용된 오리진이 잘못되었거나, 프리플라이트 OPTIONS 요청이 실패하거나, CORS 구성이 누락되었거나 잘못 구성되었거나, 응답 헤더에 필요한 CORS 헤더가 포함되지 않았거나, API Gateway 배포가 CORS 설정을 제거할 때 발생합니다.
 교차 오리진 요청이 실패하고, 브라우저 CORS 오류가 발생하며, 웹 애플리케이션이 다른 오리진의 API에 접근할 수 없습니다. 이는 API 계층에 영향을 미치며 교차 오리진 접근을 차단합니다. 일반적으로 CORS 구성 문제, OPTIONS 메서드 누락 또는 배포 문제가 원인이며, API Gateway HTTP API vs REST API를 사용하는 경우 CORS 동작이 다르고 애플리케이션에서 교차 오리진 요청 실패가 발생할 수 있습니다.

## 영향

교차 오리진 요청이 실패합니다. 브라우저 CORS 오류가 발생합니다. 웹 애플리케이션이 API에 접근할 수 없습니다. 프리플라이트 요청이 거부됩니다. API 응답에 CORS 헤더가 없습니다. 프론트엔드 애플리케이션이 백엔드 API와 통신할 수 없습니다. 사용자 대면 오류가 증가합니다. API 통합이 실패합니다. APIGatewayCORS 오류가 발생합니다. API Gateway HTTP API vs REST API를 사용하는 경우 CORS 구성이 다릅니다. 차단된 교차 오리진 요청으로 인해 애플리케이션에서 오류나 성능 저하가 발생할 수 있으며, 프론트엔드-백엔드 통합이 중단됩니다.

## 플레이북

1. API Gateway API `<api-id>`가 존재하고 배포되어 있으며, 리전 `<region>`의 API Gateway AWS 서비스 상태가 정상인지 확인합니다.
2. 리전 `<region>`의 API Gateway REST API `<api-id>` 또는 HTTP API `<api-id>`를 조회하여 CORS 구성, 허용된 오리진, 허용된 메서드, 허용된 헤더 설정을 점검하고, CORS가 활성화되어 있는지 검증합니다.
3. API Gateway 접근 로그가 포함된 CloudWatch Logs 로그 그룹에서 CORS 관련 오류 패턴이나 프리플라이트 요청 실패를 필터링하여 OPTIONS 요청 실패를 확인합니다.
4. API Gateway API `<api-id>`의 CloudWatch 지표(4XXError, 5XXError)를 최근 1시간 동안 조회하여 CORS 관련 오류 패턴을 파악하고, 오류 빈도를 분석합니다.
5. API Gateway `<api-id>`의 API 유형(REST API vs HTTP API)을 조회하여 API 유형 구성을 확인하고, 유형별 CORS 동작 차이를 점검합니다.
6. API Gateway `<api-id>`의 메서드 구성을 조회하여 OPTIONS 메서드 구성과 CORS 헤더 설정을 확인하고, 프리플라이트 요청을 위한 OPTIONS 메서드가 존재하는지 검증합니다.
7. 애플리케이션 로그가 포함된 CloudWatch Logs 로그 그룹에서 CORS 오류 메시지나 교차 오리진 요청 실패를 필터링하여 브라우저 콘솔 오류 패턴을 확인합니다.
8. API Gateway `<api-id>`의 배포 구성을 조회하여 CORS 설정이 배포에 포함되어 있는지 확인하고, 배포가 CORS 구성을 제거했는지 점검합니다.
9. API Gateway 실행 로그가 포함된 CloudWatch Logs 로그 그룹에서 CORS 헤더 응답 패턴을 필터링하여 응답의 CORS 헤더를 검증합니다.

## 진단

1. CloudWatch 지표(플레이북 4단계)를 분석하여 4XXError 비율이 증가한 시점을 파악합니다. 접근 로그(플레이북 3단계)와 교차 참조하여 이 타임스탬프에 CORS 관련 403 또는 프리플라이트 실패가 발생했는지 확인합니다.

2. API 유형 확인(플레이북 5단계)에서 HTTP API이면 CORS 구성이 API 수준에서 설정되어 있는지 확인합니다. REST API이면 각 리소스에 OPTIONS 메서드가 존재하는지 확인합니다(플레이북 6단계). OPTIONS 메서드 누락은 프리플라이트 요청 실패를 유발합니다.

3. CloudTrail 이벤트(플레이북 9단계)에서 오류 타임스탬프 전후로 API Gateway 배포가 표시되면 배포 전후 CORS 설정을 비교합니다. 배포가 의도치 않게 CORS 구성을 제거하거나 덮어썼을 수 있습니다.

4. CORS 구성이 존재하지만(플레이북 2단계) 오류가 지속되면 허용된 오리진 설정을 확인합니다. 요청 오리진이 구성된 오리진과 정확히 일치하지 않으면(프로토콜과 포트 포함) CORS 거부가 발생합니다.

5. 접근 로그(플레이북 3단계)에서 프리플라이트 OPTIONS 요청이 4XX 오류를 반환하면 OPTIONS 메서드 구성(플레이북 6단계)을 확인합니다. OPTIONS 응답에는 Access-Control-Allow-Origin, Access-Control-Allow-Methods, Access-Control-Allow-Headers가 포함되어야 합니다.

6. CORS 오류가 메서드별인 경우(플레이북 3단계 분석), 통합 응답 헤더(플레이북 9단계)에서 해당 특정 메서드에 CORS 헤더가 누락되어 있을 수 있으며 다른 메서드는 정상 작동합니다.

7. 브라우저 콘솔 오류(플레이북 7단계)에서 자격 증명 관련 CORS 실패를 나타내면 인증된 요청에 대해 Access-Control-Allow-Credentials 헤더가 누락되었거나 잘못 구성되었을 수 있습니다.

상관관계를 찾을 수 없는 경우: 분석 기간을 2시간으로 확장하고, 프론트엔드 애플리케이션 오리진이 구성된 허용 오리진과 정확히 일치하는지 확인하고, HTTP API vs REST API CORS 동작 차이를 점검하고, 인증된 엔드포인트에 대한 인증자 CORS 처리를 확인합니다.