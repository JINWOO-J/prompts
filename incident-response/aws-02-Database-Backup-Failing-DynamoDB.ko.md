---
category: incident-response
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/AWS%20Playbooks/02-Database/Backup-Failing-DynamoDB.md)'
role: SRE / AWS Incident Response
origin: scoutflo
extract_date: 2026-03-05
tags:
- backup
- cloudwatch
- compliance
- database
- dynamodb
- failing
- incident-response
- k8s-service
- sts
---

# DynamoDB Backup Failing - DynamoDB 백업 실패

## 의미

DynamoDB 백업이 실패하는 현상(백업 실패 또는 DynamoDBBackupFailed 경보 트리거)은 백업 권한이 부족하거나, 백업 요청 제한이 초과되거나, 테이블이 백업에 유효하지 않은 상태이거나, 백업 이름 충돌이 존재하거나, 백업 생성 중 백업 서비스에 오류가 발생하거나, DynamoDB 테이블 백업 설정이 백업 생성을 방해할 때 발생합니다.
 DynamoDB 백업이 생성되지 않고, 특정 시점 복구를 사용할 수 없으며, 백업 보존 정책이 실패합니다. 이는 데이터베이스 백업 및 데이터 보호 계층에 영향을 미치며 재해 복구를 손상시킵니다. 일반적으로 권한 문제, 제한 제약 또는 테이블 상태 문제가 원인이며, DynamoDB Global Tables를 사용하는 경우 백업 동작이 다를 수 있고 애플리케이션이 백업 보호 누락의 영향을 받을 수 있습니다.

## 영향

DynamoDB 백업이 생성되지 않습니다. 특정 시점 복구를 사용할 수 없습니다. 백업 보존 정책이 실패합니다. 데이터 보호가 손상됩니다. 백업 자동화가 효과가 없습니다. 재해 복구 기능이 상실됩니다. 백업 실패 경보가 발생합니다. 백업 일정이 실행되지 않습니다. DynamoDBBackupFailed 경보가 발생할 수 있으며, DynamoDB Global Tables를 사용하는 경우 백업 동작이 다를 수 있습니다. 백업 보호 누락으로 애플리케이션이 영향을 받을 수 있으며, 백업 누락으로 인해 컴플라이언스 요구사항을 위반할 수 있습니다.

## 플레이북

1. DynamoDB 테이블 `<table-name>`이 존재하고 리전 `<region>`의 DynamoDB AWS 서비스 상태가 정상인지 확인합니다.
2. 리전 `<region>`의 DynamoDB 테이블 `<table-name>`을 조회하여 백업 구성, 백업 상태, 최근 백업 생성 시도를 점검하고, 테이블 상태가 백업에 유효한지 검증합니다.
3. DynamoDB 이벤트가 포함된 CloudWatch Logs 로그 그룹에서 테이블 `<table-name>` 관련 백업 실패 이벤트나 오류 패턴을 필터링하여 실패 사유 세부 정보를 확인합니다.
4. DynamoDB 테이블 `<table-name>`의 CloudWatch 지표(UserErrors)를 최근 24시간 동안 조회하여 백업 관련 오류 패턴을 파악하고, 오류 빈도를 분석합니다.
5. 테이블 `<table-name>`의 DynamoDB 백업 요청을 나열하고 백업 상태, 실패 사유, 백업 생성 타임스탬프를 확인하여 백업 이력을 분석합니다.
6. CloudTrail 이벤트가 포함된 CloudWatch Logs 로그 그룹에서 테이블 `<table-name>` 관련 DynamoDB 백업 API 호출 실패를 필터링하여 API 오류 세부 정보를 확인합니다.
7. DynamoDB 테이블 `<table-name>`의 특정 시점 복구(PITR) 상태를 조회하고 필요한 경우 PITR이 활성화되어 있는지 확인하며, PITR 구성을 점검합니다.
8. DynamoDB의 백업 요청 수 CloudWatch 지표를 조회하여 백업 요청 제한에 도달했는지 확인하고, 제한 제약을 점검합니다.
9. CloudTrail 이벤트가 포함된 CloudWatch Logs 로그 그룹에서 최근 24시간 이내 DynamoDB 백업 작업 관련 IAM 정책 변경 이벤트를 필터링하여 권한 변경 사항을 확인합니다.

## 진단

1. DynamoDB 이벤트가 포함된 CloudWatch Logs와 CloudTrail API 호출 실패(플레이북 3단계 및 6단계)를 분석하여 구체적인 백업 실패 오류 메시지를 파악합니다. 오류가 "AccessDenied"를 나타내면 즉시 IAM 권한 검증으로 진행합니다. "LimitExceededException"을 나타내면 백업 요청 제한이 원인입니다. "ResourceInUseException"을 나타내면 테이블 상태가 백업을 방해하고 있는 것입니다.

2. 접근 거부 오류의 경우, 백업 작업과 관련된 IAM 정책 권한(플레이북 9단계)을 검토합니다. 최근 IAM 정책 변경으로 DynamoDB 백업 권한이 제거되었다면 필요한 권한을 복원합니다. 최근 변경이 없다면 IAM 역할 또는 사용자에게 dynamodb:CreateBackup, dynamodb:DescribeBackup 및 관련 권한이 있는지 확인합니다.

3. DynamoDB 테이블 UserErrors의 CloudWatch 지표(플레이북 4단계)를 검토하여 최근 24시간 동안의 백업 관련 오류 패턴을 파악합니다. 오류 빈도가 일정하면 지속적인 구성 문제를 시사합니다. 오류가 간헐적이면 서비스 제한이나 일시적인 테이블 상태와 관련될 수 있습니다.

4. DynamoDB 테이블 구성(플레이북 2단계)을 확인하여 테이블 상태와 백업 적격성을 점검합니다. 테이블이 CREATING, UPDATING 또는 DELETING 상태이면 테이블이 ACTIVE 상태로 돌아올 때까지 백업을 생성할 수 없습니다. 특정 시점 복구(PITR)가 필요하지만 활성화되지 않은 경우(플레이북 7단계) 연속 백업 기능을 위해 활성화합니다.

5. 백업 이력과 요청 패턴(플레이북 5단계)을 확인하여 백업 요청 제한이 초과되고 있는지 판단합니다. 여러 백업 요청이 동시에 이루어지거나 백업 이름이 기존 백업과 충돌하면 서비스가 새 요청을 거부합니다.

6. 24시간 이내 여러 테이블에 걸친 백업 실패 패턴을 비교합니다. 실패가 테이블 고유의 것이면 해당 테이블의 상태나 구성과 관련된 문제입니다. 실패가 여러 테이블에 영향을 미치는 계정 전체의 것이면 IAM 권한이나 서비스 제한이 원인일 가능성이 높습니다.

7. 백업 실패 타임스탬프와 CloudTrail 이벤트(플레이북 9단계)를 30분 이내로 상관 분석하여 백업이 실패하기 시작한 시점과 일치하는 구성 또는 권한 변경을 파악합니다.

상관관계를 찾을 수 없는 경우: 기간을 30일로 확장하고, 백업 이름 충돌 및 테이블 백업 설정을 포함한 대안적 증거 소스를 검토하고, 백업 요청 제한 소진이나 테이블 상태 전환과 같은 점진적 문제를 확인하고, DynamoDB 백업 서비스 가용성과 같은 외부 종속성을 검증하고, 백업 실패의 과거 패턴을 점검하고, DynamoDB Global Tables 백업 구성 차이를 확인하고, 백업에 영향을 미치는 DynamoDB 테이블 암호화를 검증합니다.