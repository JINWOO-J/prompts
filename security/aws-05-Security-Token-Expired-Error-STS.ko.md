---
category: security
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/AWS%20Playbooks/05-Security/Token-Expired-Error-STS.md)'
role: SRE / AWS Incident Response
origin: scoutflo
extract_date: 2026-03-05
tags:
- cloudwatch
- expired
- iam
- k8s-service
- performance
- security
- sts
- token
---

# STS 토큰 만료 오류 — AWS STS Token Expired Error

## 의미

AWS STS 토큰 만료 오류가 발생합니다(인증 실패 또는 STSTokenExpired 오류 발생). 원인으로는 임시 자격 증명 만료, IAM 역할 세션 기간 제한 도달, MFA 토큰 검증 실패, 역할 신뢰 정책의 세션 기간 제한, 토큰 갱신 메커니즘의 자격 증명 갱신 실패, STS 세션 정책 제한으로 인한 토큰 유효성 감소 등이 있습니다. 임시 자격 증명이 만료되고, API 호출이 토큰 만료 오류로 실패하며, 애플리케이션이 AWS 서비스 접근을 상실합니다. 이는 인증 및 인가 계층에 영향을 미치며 서비스 접근을 차단합니다. 일반적으로 세션 기간 제한, 토큰 갱신 실패, 신뢰 정책 제한이 원인이며, 교차 계정 역할 위임을 사용하는 경우 세션 기간이 더 제한될 수 있고 애플리케이션에서 인증 실패가 발생할 수 있습니다.

## 영향

임시 자격 증명 만료, API 호출 토큰 만료 오류 실패, 애플리케이션 AWS 서비스 접근 상실, 역할 위임 실패, 세션 기반 접근 거부, 인증 오류 발생, 서비스 간 통신 실패, 자동화 프로세스 인증 불가. STSTokenExpired 오류 발생 가능. 교차 계정 역할 위임을 사용하는 경우 세션 기간 제한이 더 엄격할 수 있음. 인증 실패로 인해 애플리케이션 오류나 성능 저하 발생 가능. 자격 증명 만료로 인해 자동화 워크플로우가 중단될 수 있습니다.

## 플레이북

1. IAM 역할 `<role-name>`의 존재를 확인하고 리전 `<region>`의 STS 및 IAM AWS 서비스 상태가 정상인지 확인합니다.
2. CloudTrail 이벤트가 포함된 CloudWatch Logs 로그 그룹을 조회하여 토큰 만료를 나타내는 오류 패턴이 있는 STS AssumeRole 또는 GetSessionToken 이벤트를 필터링하고 만료 오류 세부사항을 포함합니다.
3. STS 토큰 생성에 사용되는 IAM 역할 `<role-name>`을 조회하여 신뢰 정책, 세션 기간 설정, 최대 세션 기간 구성을 검사하고 세션 기간 제한을 확인합니다.
4. AssumeRole 및 GetSessionToken 오류율을 포함한 STS API 호출 CloudWatch 메트릭을 지난 1시간 동안 조회하여 토큰 만료 패턴을 식별하고 만료 빈도를 분석합니다.
5. 역할 `<role-name>`의 IAM 역할 세션을 나열하고 세션 만료 타임스탬프와 활성 세션 수를 확인하며 세션 기간을 검증합니다.
6. 애플리케이션 로그가 포함된 CloudWatch Logs 로그 그룹을 조회하여 STS 토큰 만료 오류 메시지나 인증 실패 패턴을 필터링하고 만료 타임스탬프를 포함합니다.
7. IAM 역할 `<role-name>`의 신뢰 정책을 조회하여 해당되는 경우 교차 계정 역할 위임 구성을 확인하고 교차 계정 제한이 세션 기간에 영향을 미치는지 확인합니다.
8. CloudTrail 이벤트가 포함된 CloudWatch Logs 로그 그룹을 조회하여 지난 24시간 동안 역할 `<role-name>`과 관련된 IAM 역할 신뢰 정책 수정 이벤트를 필터링하고 세션 기간 변경을 확인합니다.
9. SAML 또는 OIDC를 사용하는 경우 AssumeRoleWithSAML 또는 AssumeRoleWithWebIdentity를 포함한 STS API 호출 CloudWatch 메트릭을 조회하여 다른 토큰 유형의 토큰 만료 패턴을 확인합니다.

## 진단

1. CloudTrail 이벤트(플레이북 2단계)를 분석하여 STS 토큰 만료 오류가 처음 발생한 시점을 식별합니다. AssumeRole 또는 GetSessionToken 오류 타임스탬프를 비교하여 상관관계 기준선을 수립합니다.

2. IAM 역할 구성(플레이북 3단계)에서 MaxSessionDuration이 확인되면 애플리케이션 사용 패턴과 비교합니다. 애플리케이션이 구성된 기간보다 오래 세션을 유지하면 토큰은 예상대로 만료되며 갱신이 필요합니다.

3. CloudTrail에서 오류 타임스탬프 전후로 신뢰 정책 수정(플레이북 8단계)이 확인되면 신뢰 정책 변경이 세션 기간을 제한했거나 토큰 발급을 방해하는 조건을 추가했는지 확인합니다.

4. STS API 호출 메트릭(플레이북 4단계)에서 여러 역할에 걸쳐 오류가 확인되면 계정 전체(STS 서비스 문제) 또는 애플리케이션 전체(갱신 로직 실패) 문제일 수 있습니다. 오류가 특정 역할에 한정되면 역할 구성 문제입니다.

5. 만료 패턴(플레이북 6단계)에서 세션 기간 제한과 일치하는 일관된 타이밍이 확인되면 애플리케이션이 만료 전에 토큰을 갱신하지 않는 것입니다. 패턴이 불규칙하면 갱신 메커니즘 실패가 원인입니다.

6. 교차 계정 역할 위임이 관련된 경우(플레이북 7단계), 신뢰 정책이 위임 주체를 허용하는지 확인하고 교차 계정 시나리오의 세션 기간 제한을 확인합니다.

7. SAML 또는 OIDC 인증 메트릭(플레이북 9단계)에서 토큰 만료 전후로 오류가 확인되면 ID 제공자 토큰 유효 기간이 STS 세션 기간보다 짧을 수 있습니다.

상관관계가 발견되지 않는 경우: 분석을 48시간으로 확장하고, 애플리케이션 토큰 갱신 로직 구현을 검토하고, MFA 보호 세션의 MFA 디바이스 가용성을 확인하고, STS 세션 정책 제한을 확인하고, 교차 계정 역할 위임 기간 제한을 조사합니다.
