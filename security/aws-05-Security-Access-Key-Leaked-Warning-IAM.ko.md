---
category: security
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/AWS%20Playbooks/05-Security/Access-Key-Leaked-Warning-IAM.md)'
role: SRE / AWS Incident Response
origin: scoutflo
extract_date: 2026-03-05
tags:
- access
- cloudwatch
- compliance
- guardduty
- iam
- k8s-deployment
- k8s-secret
- k8s-service
- leaked
- performance
- pipeline
- security
- sts
- warning
---

# AWS Access Key 유출 경고 — AWS Access Key Leaked Warning

## 의미

AWS 액세스 키가 유출되었거나 침해된 것으로 의심됩니다(IAMAccessKeyExposed 또는 GuardDuty 발견사항 등 보안 알림 발생). 원인으로는 공개 리포지토리에 액세스 키 노출, 비인가 위치에서의 키 사용, CloudTrail 이벤트가 포함된 CloudWatch Logs에서 의심스러운 API 호출 감지, MFA 미적용, 과도한 권한을 허용하는 보안 정책 등이 있습니다. CloudTrail 로그에서 예상치 못한 지리적 위치나 IP 주소에서의 API 호출이 확인되고, 액세스 키 사용 패턴이 비인가 접근을 나타내며, Security Hub 또는 GuardDuty 발견사항이 침해된 자격 증명을 식별합니다. 이는 보안 계층에 영향을 미치며 자격 증명 침해를 나타냅니다. 일반적으로 키 노출, 비인가 접근, 불충분한 보안 통제가 원인이며, 침해된 키가 CI/CD 파이프라인에서 사용되거나 환경 변수에 노출되거나 AWS Secrets Manager 또는 Parameter Store에 안전하지 않게 저장될 수 있습니다.

## 영향

보안 침해 위험 증가, 비인가 접근 발생 가능, 침해된 자격 증명의 악의적 사용 가능, IAMAccessKeyExposed 또는 GuardDuty 발견사항 발생, 계정 보안 침해, 민감 데이터 접근 가능, 리소스 변경 발생 가능, 컴플라이언스 위반 가능, 즉각적인 자격 증명 교체 필요. CloudTrail 로그에서 예상치 못한 위치의 의심스러운 API 호출 확인, 비인가 리소스 접근 발생, 데이터 유출 가능, 비인가 서비스 변경 수행. CI/CD 파이프라인에서 키가 사용되는 경우 자동 배포가 침해될 수 있으며, 비인가 변경으로 인해 애플리케이션 오류나 성능 저하가 발생할 수 있습니다.

## 플레이북

1. 액세스 키 `<access-key-id>`의 존재를 확인하고 IAM Access Key `<access-key-id>`의 상태 및 마지막 사용 정보를 조회하여 마지막 사용 시간과 위치를 확인합니다.
2. CloudTrail 이벤트가 포함된 CloudWatch Logs 로그 그룹을 조회하여 지난 24시간 동안 액세스 키 `<access-key-id>`와 관련된 의심스러운 API 호출을 필터링하고 지리적 위치 분석을 포함합니다.
3. IAM 사용자 `<user-name>`의 MFA 구성을 조회하고 모든 사용자에 대한 MFA 적용 상태를 확인합니다.
4. IAM 사용자 `<user-name>`에 연결된 IAM 정책을 조회하고 과도한 권한에 대한 보안 정책을 검토합니다.
5. CloudTrail 이벤트가 포함된 CloudWatch Logs 로그 그룹을 조회하여 액세스 키 `<access-key-id>` 또는 사용자 `<user-name>`과 관련된 Security Hub 또는 GuardDuty 발견사항을 필터링하고 보안 서비스 통합 로그를 확인합니다.
6. GuardDuty 로그가 포함된 CloudWatch Logs 로그 그룹(가용 시)을 조회하여 액세스 키 `<access-key-id>`와 관련된 자격 증명 침해 발견사항을 필터링하고 GuardDuty 탐지 로그를 확인합니다.
7. CloudTrail 이벤트가 포함된 CloudWatch Logs 로그 그룹을 조회하여 사용자 `<user-name>` 또는 액세스 키 `<access-key-id>`와 관련된 IAM Access Analyzer 발견사항이나 외부 접근 시도를 필터링하고 접근 분석 로그를 확인합니다.
8. CloudTrail 이벤트가 포함된 CloudWatch Logs 로그 그룹을 조회하여 액세스 키 `<access-key-id>`를 사용한 교차 계정 접근 시도를 필터링합니다.
9. Secrets Manager 또는 Systems Manager Parameter Store 로그가 포함된 CloudWatch Logs 로그 그룹을 조회하여 사용자 `<user-name>`과 관련된 액세스 키 사용을 필터링하고 교체가 필요한 저장된 자격 증명을 확인합니다.

## 진단

1. 플레이북 5-6단계의 GuardDuty 발견사항 및 Security Hub 알림을 분석하여 자격 증명 침해가 처음 탐지된 시점을 식별합니다. 발견사항 타임스탬프가 다른 모든 이벤트와의 상관관계 기준선을 제공합니다.

2. GuardDuty에서 IAMAccessKeyExposed 또는 UnauthorizedAccess 발견사항이 확인되면, 플레이북 2단계의 CloudTrail 이벤트에서 침해된 키를 사용한 특정 API 호출을 조사합니다. 이벤트 타임스탬프와 소스 IP 주소가 비인가 접근의 범위를 나타냅니다.

3. 플레이북 2단계의 CloudTrail 이벤트에서 예상치 못한 지리적 위치나 IP 주소의 API 호출이 확인되면, 플레이북 1단계의 액세스 키 마지막 사용 정보와 상관관계를 분석하여 비인가 사용 패턴을 확인합니다.

4. 플레이북 3단계의 MFA 구성에서 영향받는 사용자에 대해 MFA가 적용되지 않은 것으로 확인되면, MFA 요구사항을 우회한 자격 증명 기반 접근에 대한 CloudTrail 이벤트를 확인합니다. 이는 MFA 갭이 침해를 가능하게 했는지 여부를 나타냅니다.

5. 플레이북 4단계의 IAM 정책에서 과도한 권한이 확인되면, 과도하게 허용적인 접근을 악용한 리소스 변경에 대한 CloudTrail 이벤트를 조사합니다. 교차 서비스 접근이나 관리 작업을 보여주는 이벤트는 권한 상승을 나타냅니다.

6. 플레이북 9단계의 Secrets Manager 또는 Parameter Store 로그에서 액세스 키 조회가 확인되면, 키가 악의적으로 사용되기 전에 비인가 주체가 저장된 자격 증명에 접근했는지 확인합니다.

7. 의심스러운 API 호출의 빈도와 패턴을 분석하여 활동이 지속적인지(진행 중인 자동화된 침해) 또는 간헐적인지(즉각적인 격리가 필요한 표적 수동 공격) 판단합니다.

수집된 데이터에서 상관관계가 발견되지 않는 경우: CloudTrail 쿼리 기간을 7일로 확장하고, 플레이북 7단계의 IAM Access Analyzer 발견사항에서 외부 접근 시도를 검토하고, CI/CD 파이프라인 구성이나 환경 변수에 노출된 키를 확인하고, 플레이북 8단계의 교차 계정 접근 패턴을 조사합니다. 보안 침해는 직접적인 키 노출이 아닌 자격 증명 공유, 서드파티 서비스 침해, 소셜 엔지니어링, 안전하지 않게 저장된 키로 인해 발생할 수 있습니다.
