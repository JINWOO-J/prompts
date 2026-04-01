---
category: incident-response
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/AWS%20Playbooks/04-Networking/Returning-500-Internal-Server-Error-API-Gateway.md)'
role: SRE / AWS Incident Response
origin: scoutflo
extract_date: 2026-03-05
tags:
- cloudwatch
- gateway
- iam
- incident-response
- internal
- k8s-service
- lambda
- networking
- performance
- returning
- server
- sts
- waf
---

# API Gateway Returning 500 Internal Server Error - API Gateway 500 내부 서버 오류 반환

## 의미

API Gateway가 500 Internal Server Error 응답을 반환하는 현상(API Gateway 5XX 오류 또는 APIGateway500Error 경보 트리거)은 API Gateway 리소스 정책이 접근을 차단하거나, IAM 역할 및 권한이 잘못 구성되었거나, Lambda 함수 실행 역할에 호출 권한이 없거나, AWS WAF 규칙이 요청을 차단하거나, 통합 타임아웃 설정이 너무 낮거나, 통합 엔드포인트 실패가 발생할 때 발생합니다.
 API 요청이 500 오류로 실패하고, API 엔드포인트를 사용할 수 없으며, CloudWatch Logs에 API Gateway 오류가 표시됩니다. 이는 API 계층에 영향을 미치며 API 접근을 차단합니다.

## 영향

API 요청이 500 오류로 실패합니다. API 엔드포인트를 사용할 수 없습니다. API Gateway 5XX 오류 경보가 발생합니다. 다운스트림 서비스가 요청을 받을 수 없습니다. 애플리케이션 통합이 실패합니다. 사용자 대면 API 호출에 오류가 발생합니다. 서비스 간 통신이 중단됩니다.

## 플레이북

1. API Gateway API `<api-id>`가 존재하고 배포되어 있으며, 리전 `<region>`의 API Gateway AWS 서비스 상태가 정상인지 확인합니다.
2. API Gateway `<api-id>`의 리소스 정책을 조회하여 정책이 API Gateway에 대한 접근을 허용하는지 확인합니다.
3. API Gateway `<api-id>`의 API 유형(REST API vs HTTP API)을 조회하여 유형별 오류 동작을 확인합니다.
4. IAM 역할 `<role-name>` 및 정책 `<policy-name>`을 조회하여 API Gateway 접근을 위한 IAM 역할 및 권한이 올바르게 설정되어 있는지 확인하고, Lambda 통합을 사용하는 경우 Lambda 함수 `<function-name>` 실행 역할에 lambda:InvokeFunction 권한이 있는지 검증합니다.
6. API Gateway `<api-id>`의 통합 타임아웃 설정을 조회하여 다운스트림 서비스에 충분한 통합 타임아웃인지 확인합니다.
7. API Gateway `<api-id>`의 통합 유형(Lambda vs HTTP vs AWS 서비스)을 조회하여 통합 엔드포인트를 확인합니다.
8. API `<api-id>`의 API Gateway 로그가 포함된 CloudWatch Logs에서 오류 패턴, 500 오류 또는 실행 실패를 필터링합니다.
9. API Gateway `<api-id>`의 요청/응답 매핑 템플릿을 조회하여 매핑 템플릿이 올바르게 구성되어 있는지 확인합니다.
10. AWS WAF를 사용하는 경우 WAF 로그가 포함된 CloudWatch Logs에서 API Gateway `<api-id>` 관련 차단된 요청을 필터링합니다.

## 진단

1. 플레이북 1단계의 AWS 서비스 상태를 분석하여 리전의 API Gateway 서비스 가용성을 확인합니다.

2. 플레이북 8단계의 API Gateway 로그에서 구체적인 오류 메시지가 표시되면 이를 사용하여 실패 지점을 파악합니다.

3. 플레이북 2단계의 리소스 정책에 Deny 문이 포함되어 있거나 요청 소스를 Allow하지 않으면 API Gateway가 정책 위반에 대해 500을 반환합니다.

4. Lambda 통합(플레이북 4단계)에서 실행 역할에 lambda:InvokeFunction 권한이 없거나 Lambda 리소스 정책이 API Gateway를 허용하지 않으면 호출이 500으로 실패합니다.

5. 플레이북 6단계의 통합 타임아웃이 Lambda 실행 시간보다 짧으면 API Gateway가 타임아웃되어 504를 반환합니다.

6. 플레이북 7단계의 통합 유형에서 접근할 수 없거나 실패하는 백엔드와의 HTTP 통합이 표시되면 API Gateway가 500을 반환합니다.

7. 플레이북 9단계의 매핑 템플릿에 구문 오류가 있거나 존재하지 않는 요청/응답 필드를 참조하면 변환이 500으로 실패합니다.

8. 플레이북 10단계의 WAF 로그에서 차단된 요청이 표시되면 WAF 규칙이 API Gateway 통합에 도달하기 전에 트래픽을 거부하고 있을 수 있습니다.

상관관계를 찾을 수 없는 경우: API Gateway 로그 쿼리 기간을 30분으로 확장하고, 실행 오류에 대한 Lambda 함수 CloudWatch 로그를 확인하고, API Gateway 인증자 실패(Lambda 또는 Cognito)를 점검합니다.