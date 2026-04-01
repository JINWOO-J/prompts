---
category: security
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/AWS%20Playbooks/05-Security/Not-Rotating-Credentials-Secrets-Manager.md)'
role: SRE / AWS Incident Response
origin: scoutflo
extract_date: 2026-03-05
tags:
- credentials
- iam
- k8s-secret
- k8s-service
- lambda
- manager
- performance
- rds
- rotating
- secrets
- security
- sts
---

# Secrets Manager 자격 증명 교체 실패 — AWS Secrets Manager Not Rotating Credentials

## 의미

AWS Secrets Manager가 자격 증명을 교체하지 않습니다(교체 실패 또는 SecretsManagerRotationFailed 알람 발생). 원인으로는 교체 미활성화, 교체 Lambda 함수 오류, 교체를 위한 IAM 권한 부족, 교체 스케줄 설정 오류, 교체 Lambda 함수의 시크릿 접근 불가, Secrets Manager 교체 Lambda 함수 런타임 오류 등이 있습니다. Secrets Manager 자격 증명이 자동으로 교체되지 않고, 자격 증명 교체가 실패하며, 시크릿 교체 자동화가 무효화됩니다. 이는 보안 및 자격 증명 관리 계층에 영향을 미치며 자격 증명 보안을 저해합니다. 일반적으로 교체 구성 문제, Lambda 함수 문제, 권한 실패가 원인이며, RDS와 함께 Secrets Manager를 사용하는 경우 교체 동작이 다를 수 있고 애플리케이션에서 자격 증명 교체 실패가 발생할 수 있습니다.

## 영향

Secrets Manager 자격 증명 자동 교체 실패, 자격 증명 교체 실패, 교체 스케줄 미실행, 시크릿 교체 자동화 무효, 자격 증명 보안 저해, 교체 Lambda 함수 오류 발생, 교체 알람 발생, 자격 증명 관리 실패. SecretsManagerRotationFailed 알람 발생 가능. RDS와 함께 Secrets Manager를 사용하는 경우 교체 동작이 다를 수 있음. 만료된 자격 증명으로 인해 애플리케이션 오류나 성능 저하 발생 가능. 자격 증명 보안이 저해될 수 있습니다.

## 플레이북

1. Secrets Manager 시크릿 `<secret-name>`의 존재를 확인하고 리전 `<region>`의 Secrets Manager 및 Lambda AWS 서비스 상태가 정상인지 확인합니다.
2. 리전 `<region>`의 Secrets Manager 시크릿 `<secret-name>`을 조회하여 교체 구성, 교체 활성화 상태, 교체 스케줄, 교체 Lambda 함수 ARN을 검사하고 교체가 활성화되었는지 확인합니다.
3. 시크릿 교체에 사용되는 Lambda 함수 `<function-name>`을 조회하여 함수 코드, 실행 역할, 오류 로그를 검사하고 함수가 구성되었는지 확인합니다.
4. 로그 그룹 `/aws/lambda/<function-name>`의 CloudWatch Logs를 조회하여 교체 오류 패턴, 권한 오류, 교체 실패 메시지를 필터링하고 오류 세부사항을 포함합니다.
5. Lambda 함수 `<function-name>`에 연결된 IAM 역할 `<role-name>`을 조회하여 Secrets Manager 교체 작업에 대한 정책 권한을 검사하고 IAM 권한을 확인합니다.
6. 시크릿 `<secret-name>`의 Secrets Manager 교체 이벤트를 나열하고 교체 상태, 실패 사유, 교체 시도 타임스탬프를 확인하며 교체 이력을 분석합니다.
7. Lambda 함수 `<function-name>`의 Errors 및 Invocations를 포함한 CloudWatch 메트릭을 조회하여 함수 실행 패턴을 확인하고 함수가 호출되고 있는지 확인합니다.
8. Secrets Manager 시크릿 `<secret-name>`의 교체 Lambda 함수 구성을 조회하여 Lambda 함수가 시크릿에 접근할 수 있는지 확인하고 시크릿 접근 권한을 확인합니다.
9. CloudTrail 이벤트가 포함된 CloudWatch Logs 로그 그룹을 조회하여 지난 30일 동안 시크릿 `<secret-name>`과 관련된 Secrets Manager 교체 구성 또는 Lambda 함수 수정 이벤트를 필터링하고 구성 변경을 확인합니다.

## 진단

1. 교체 Lambda 함수에 대한 CloudWatch Logs(플레이북 4단계)를 분석하여 구체적인 교체 오류 메시지를 식별합니다. 오류가 "AccessDenied"를 나타내면 즉시 IAM 권한 확인으로 진행합니다. 오류가 데이터베이스 연결 실패를 나타내면 외부 연결성을 확인합니다. 오류가 Lambda 함수 코드 오류를 나타내면 함수 코드를 검토합니다.

2. 접근 거부 오류의 경우, 교체 Lambda 함수에 연결된 IAM 역할 권한(플레이북 5단계)을 확인합니다. 역할에는 Secrets Manager API 호출 권한(secretsmanager:GetSecretValue, secretsmanager:PutSecretValue, secretsmanager:UpdateSecretVersionStage)과 자격 증명 교체에 필요한 서비스별 권한(예: RDS의 경우 rds:ModifyDBInstance)이 있어야 합니다.

3. Lambda 함수 메트릭(플레이북 7단계)에서 Errors 및 Invocations를 검토하여 함수가 호출되고 있는지 판단합니다. Invocations가 0이면 교체 스케줄이 트리거되지 않는 것입니다. Errors가 Invocations와 같으면 모든 교체 시도가 실패하는 것입니다.

4. Secrets Manager 교체 구성(플레이북 2단계)을 조사하여 교체가 활성화되었는지, 교체 스케줄이 올바른지, Lambda 함수 ARN이 올바르게 지정되었는지 확인합니다. 교체가 비활성화되었거나 스케줄이 잘못 구성되면 교체가 발생하지 않습니다.

5. 교체 이벤트 이력(플레이북 6단계)을 검토하여 교체 시도 패턴과 실패 사유를 식별합니다. 교체 시도가 발생하지만 지속적으로 실패하면 구체적인 실패 사유에 집중합니다. 교체 시도가 기록되지 않으면 교체 스케줄 구성이 문제입니다.

6. Lambda 함수가 시크릿에 접근할 수 있는지(플레이북 8단계) 확인합니다. 함수의 IAM 역할에 필요한 Secrets Manager 권한이 있는지, 시크릿의 리소스 정책이 접근을 제한하는지 확인합니다.

7. CloudTrail 이벤트(플레이북 9단계)를 교체 실패 타임스탬프와 30분 이내로 상관관계를 분석하여 교체 구성이나 IAM 정책 수정을 식별합니다. 권한 변경이 교체 실패 시작 시점과 일치하면 해당 변경이 원인일 가능성이 높습니다.

8. 24시간 이내의 여러 시크릿에 걸친 교체 실패 패턴을 비교합니다. 실패가 특정 시크릿에 한정되면 해당 시크릿의 교체 Lambda 함수나 구성에 문제가 있는 것입니다. 동일한 Lambda 함수를 사용하는 모든 시크릿에서 실패가 발생하면 Lambda 함수 코드나 IAM 권한을 조사합니다.

9. 데이터베이스 자격 증명 교체의 경우, Lambda 함수가 데이터베이스에 연결할 수 있는지 확인합니다. 네트워크 연결성(VPC 구성, 보안 그룹)이 Lambda 함수의 데이터베이스 접근을 차단하면 교체를 완료할 수 없습니다.

지정된 시간 범위 내에서 상관관계가 발견되지 않는 경우: 기간을 90일로 확장하고, 교체 Lambda 함수 코드 및 시크릿 접근 패턴을 포함한 대안적 증거 소스를 검토하고, Lambda 함수 코드 오류나 시크릿 접근 권한 변경 같은 점진적 문제를 확인하고, 자격 증명 업데이트를 위한 데이터베이스 연결성이나 외부 서비스 가용성 같은 외부 의존성을 확인하고, 교체 실패의 과거 패턴을 조사하고, Secrets Manager 교체 스케줄 구성 문제를 확인하고, Secrets Manager 교체 Lambda 함수 타임아웃 설정을 확인합니다. 교체 실패는 즉각적인 교체 구성 변경이 아닌 Lambda 함수 코드 오류, 시크릿 접근 권한 문제, 외부 서비스 연결 문제, Secrets Manager 교체 스케줄 설정 오류, Secrets Manager 교체 Lambda 함수 타임아웃 설정으로 인해 발생할 수 있습니다.
