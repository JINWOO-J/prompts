---
category: security
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/AWS%20Playbooks/05-Security/User-Pool-Login-Issues-Cognito.md)'
role: SRE / AWS Incident Response
origin: scoutflo
extract_date: 2026-03-05
tags:
- cloudwatch
- cognito
- issues
- k8s-service
- login
- performance
- pool
- security
- sts
- user
---

# Cognito User Pool 로그인 문제 — AWS Cognito User Pool Login Issues

## 의미

AWS Cognito User Pool 로그인이 실패합니다(인증 실패 또는 CognitoLoginFailure 알람 발생). 원인으로는 사용자 자격 증명 오류, 사용자 계정 비활성화, MFA 필수이나 미완료, User Pool 구성 오류, Cognito 서비스의 인증 중 오류, Cognito User Pool 비밀번호 정책으로 인한 로그인 차단 등이 있습니다. Cognito User Pool 로그인이 실패하고, 사용자 인증이 거부되며, 애플리케이션 접근이 차단됩니다. 이는 인증 및 ID 관리 계층에 영향을 미치며 사용자 접근을 차단합니다. 일반적으로 자격 증명 문제, MFA 문제, User Pool 구성 오류가 원인이며, 외부 ID 제공자와 함께 Cognito를 사용하는 경우 인증 흐름이 다를 수 있고 애플리케이션에서 로그인 실패가 발생할 수 있습니다.

## 영향

Cognito User Pool 로그인 실패, 사용자 인증 거부, 애플리케이션 접근 차단, 사용자 로그인 오류 발생, MFA 인증 실패, User Pool 인증 자동화 무효, 사용자 경험 저하, 애플리케이션 인증 저해. CognitoLoginFailure 알람 발생 가능. 외부 ID 제공자와 함께 Cognito를 사용하는 경우 인증 흐름이 다를 수 있음. 차단된 사용자 접근으로 인해 애플리케이션 오류나 성능 저하 발생 가능. 사용자 대면 인증이 실패할 수 있습니다.

## 플레이북

1. Cognito User Pool `<user-pool-id>`의 존재를 확인하고 리전 `<region>`의 Cognito AWS 서비스 상태가 정상인지 확인합니다.
2. 리전 `<region>`의 Cognito User Pool `<user-pool-id>`를 조회하여 User Pool 구성, 인증 설정, MFA 구성, User Pool 정책을 검사하고 User Pool이 활성화되었는지 확인합니다.
3. Cognito 이벤트가 포함된 CloudWatch Logs 로그 그룹을 조회하여 인증 실패 패턴, 로그인 오류, User Pool 인증 오류를 필터링하고 오류 메시지 세부사항을 포함합니다.
4. Cognito User Pool `<user-pool-id>`의 SignInSuccesses 및 SignInFailures를 포함한 CloudWatch 메트릭을 지난 24시간 동안 조회하여 인증 패턴을 식별하고 인증 실패 빈도를 분석합니다.
5. Cognito User Pool 사용자를 나열하고 사용자 상태, 계정 활성화, 인증 시도 패턴을 확인하며 사용자 계정 상태를 검증합니다.
6. 애플리케이션 로그가 포함된 CloudWatch Logs 로그 그룹을 조회하여 Cognito 인증 오류 메시지나 로그인 실패 패턴을 필터링하고 애플리케이션 오류 세부사항을 포함합니다.
7. Cognito User Pool `<user-pool-id>`의 비밀번호 정책 구성을 조회하여 비밀번호 정책 설정을 확인하고 비밀번호 정책이 로그인에 영향을 미치는지 확인합니다.
8. Cognito User Pool `<user-pool-id>`의 MFA 구성을 조회하여 MFA 설정을 확인하고 MFA 요구사항이 인증에 영향을 미치는지 확인합니다.
9. CloudTrail 이벤트가 포함된 CloudWatch Logs 로그 그룹을 조회하여 지난 24시간 동안 Pool `<user-pool-id>`와 관련된 Cognito User Pool 구성 수정 이벤트를 필터링하고 구성 변경을 확인합니다.

## 진단

1. **3단계 및 4단계의 CloudWatch Logs 및 메트릭 분석**: 구체적인 오류 패턴에 대한 Cognito 인증 로그를 검토합니다. 3단계의 CloudWatch Logs에서 "NotAuthorizedException"과 "Incorrect username or password"가 확인되면 자격 증명 문제가 원인입니다. 로그에서 "UserNotConfirmedException"이 확인되면 사용자 확인이 보류 중입니다. 4단계의 CloudWatch 메트릭에서 모든 사용자에 걸쳐 SignInFailures가 급증하면 Pool 전체 구성 문제가 있는 것입니다. 실패가 특정 사용자에 한정되면 2단계로 진행합니다.

2. **5단계의 사용자 계정 상태 확인**: 5단계의 사용자 계정 상태가 "DISABLED", "FORCE_CHANGE_PASSWORD", "RESET_REQUIRED"이면 계정 상태가 로그인을 차단하는 것입니다. 사용자 확인 상태를 확인합니다 - 사용자가 미확인이면 이메일/전화 인증이 미완료입니다. 계정 상태가 정상이면 3단계로 진행합니다.

3. **8단계의 MFA 구성 평가**: 8단계에서 MFA가 필수이지만 CloudWatch Logs에서 "CodeMismatchException"이나 "ExpiredCodeException" 같은 MFA 관련 오류가 확인되면 MFA가 실패를 유발하는 것입니다. 사용자가 MFA 디바이스를 등록하지 않았지만 MFA가 필수이면 MFA 등록 갭이 있는 것입니다. MFA가 문제가 아니면 4단계로 진행합니다.

4. **7단계의 비밀번호 정책 검토**: 7단계의 비밀번호 정책이 특정 복잡성을 요구하고 CloudWatch Logs에서 "InvalidPasswordException"이 확인되면 비밀번호 요구사항이 충족되지 않은 것입니다. 비밀번호 정책에 만료가 포함되어 있고 사용자가 비밀번호를 업데이트하지 않았으면 만료된 자격 증명이 접근을 차단하는 것입니다. 비밀번호 정책이 문제가 아니면 5단계로 진행합니다.

5. **9단계의 구성 변경 상관관계 분석**: 9단계의 CloudTrail 이벤트에서 로그인 실패 시작 5분 이내에 User Pool 구성 수정(인증 설정, 앱 클라이언트 설정, Lambda 트리거)이 확인되면 최근 변경이 문제를 유발한 것입니다. 구체적인 수정 사항을 검토하여 원인이 되는 변경을 식별합니다.

**상관관계가 발견되지 않는 경우**: 로그인 실패 패턴을 사용하여 분석을 7일로 확장합니다. 외부 ID 제공자를 사용하는 경우 SAML/OIDC 구성과 ID 제공자 가용성을 확인합니다. 6단계의 애플리케이션 로그에서 클라이언트 측 인증 오류를 확인합니다. 1단계의 Cognito 서비스 상태를 확인하고 앱 클라이언트 설정(OAuth 범위, 콜백 URL)이 올바르게 구성되었는지 검토합니다.
