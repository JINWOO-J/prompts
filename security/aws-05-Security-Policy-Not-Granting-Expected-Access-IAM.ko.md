---
category: security
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/AWS%20Playbooks/05-Security/Policy-Not-Granting-Expected-Access-IAM.md)'
role: SRE / AWS Incident Response
origin: scoutflo
extract_date: 2026-03-05
tags:
- access
- cloudwatch
- expected
- granting
- iam
- k8s-service
- performance
- policy
- security
---

# IAM 정책 예상 접근 권한 미부여 — IAM Policy Not Granting Expected Access

## 의미

IAM 정책이 예상 권한을 부여하지 못합니다(접근 거부 오류 또는 IAMPolicyAccessDenied 알람 발생). 원인으로는 정책 JSON 구문 오류, 올바른 사용자나 역할에 정책 미연결, 정책 조건으로 인한 접근 차단, 다른 정책의 충돌하는 Deny 문, 서비스 제어 정책(SCP)의 권한 오버라이드, 리소스 기반 정책과 ID 기반 정책의 충돌, 정책 평가 순서의 접근 영향 등이 있습니다. 사용자와 역할이 필요한 리소스에 접근할 수 없고, 애플리케이션이 권한 오류로 실패하며, CloudWatch Logs에서 접근 거부 이벤트가 확인됩니다. 이는 보안 및 접근 통제 계층에 영향을 미치며 리소스 접근을 차단합니다. 일반적으로 정책 구성 문제, 평가 순서 문제, SCP 제한이 원인이며, AWS Organizations를 사용하는 경우 서비스 제어 정책이 IAM 정책을 오버라이드할 수 있고 애플리케이션에서 권한 오류가 발생할 수 있습니다.

## 영향

사용자와 역할의 필요 리소스 접근 불가, 애플리케이션 권한 오류 실패, 서비스 작업 차단, CloudTrail 이벤트가 포함된 CloudWatch Logs에 접근 거부 오류 발생, IAM 정책 평가 실패, 예상 권한 미적용, 보안 정책의 정상 접근 차단, 운영 작업 완료 불가. IAMPolicyAccessDenied 알람 발생. AWS Organizations를 사용하는 경우 서비스 제어 정책이 IAM 정책을 오버라이드할 수 있음. 권한 실패로 인해 애플리케이션 오류나 성능 저하 발생 가능. 서비스 간 통신이 차단될 수 있습니다.

## 플레이북

1. IAM 정책 `<policy-name>`과 사용자 `<user-name>` 또는 역할 `<role-name>`의 존재를 확인하고 리전 `<region>`의 IAM AWS 서비스 상태가 정상인지 확인합니다.
2. IAM 정책 `<policy-name>`을 조회하여 정책 JSON의 구문 오류를 검토하고, 정책 구조를 검증하고, 정책이 올바른 사용자 `<user-name>` 또는 역할 `<role-name>`에 연결되었는지 확인하고, 정책 조건이 의도치 않게 접근을 차단하지 않는지 검사합니다. JSON 구문, 정책 버전, 연결 상태, 조건 연산자 및 값을 확인합니다.
3. 사용자 `<user-name>` 또는 역할 `<role-name>`에 연결된 모든 IAM 정책을 나열하고 다른 정책의 충돌하는 Deny 문을 확인하며 정책 평가 순서와 명시적 Deny가 Allow보다 우선하는지 확인합니다.
4. IAM 정책 `<policy-name>`의 리소스 ARN 형식을 조회하여 리소스 ARN이 정확히 일치하는지 확인하고 ARN 형식과 와일드카드를 확인합니다.
5. Organizations를 사용하는 경우 AWS Organizations 서비스 제어 정책(SCP)을 조회하여 SCP가 IAM 정책 권한을 오버라이드하지 않는지 확인하고 SCP 제한을 확인합니다.
6. 접근 대상 리소스의 리소스 기반 정책을 조회하여 리소스 기반 정책이 접근을 허용하는지 확인하고 ID 기반 정책과의 정책 평가를 확인합니다.
7. CloudTrail 이벤트가 포함된 CloudWatch Logs 로그 그룹을 조회하여 지난 1시간 동안 정책 `<policy-name>`과 관련된 접근 거부 이벤트를 필터링하고 정책 평가 세부사항을 포함합니다.

## 진단

1. 플레이북 1단계의 AWS 서비스 상태를 분석하여 IAM 서비스 가용성을 확인합니다. IAM은 글로벌 서비스이므로 AWS 전체 서비스 상태 문제를 확인합니다.

2. 플레이북 2단계의 정책 JSON에 구문 오류가 있으면 정책이 유효하지 않아 권한이 적용되지 않습니다. 일반적인 오류로는 쉼표 누락, 잘못된 따옴표, 유효하지 않은 ARN 형식이 있습니다.

3. 플레이북 2단계의 정책 연결 상태에서 정책이 의도한 사용자나 역할에 연결되지 않은 것으로 확인되면 권한이 적용되지 않습니다. 정책이 직접 또는 그룹 멤버십을 통해 연결되었는지 확인합니다.

4. 플레이북 2단계의 정책 조건에 요청에서 충족되지 않는 제한(aws:SourceIp, aws:MultiFactorAuthPresent, aws:PrincipalTag)이 포함되어 있으면 조건부 접근이 작업을 거부하고 있습니다.

5. 플레이북 3단계의 충돌하는 정책에 요청된 액션에 대한 명시적 Deny 문이 포함되어 있으면 Deny가 모든 Allow를 오버라이드합니다. IAM 정책 평가 순서: 명시적 Deny 우선, 그 다음 명시적 Allow, 그 다음 암시적 Deny.

6. 플레이북 4단계의 리소스 ARN 형식이 실제 리소스 ARN과 일치하지 않으면(예: 리전 누락, 잘못된 계정 ID, 잘못된 리소스 이름) 정책이 의도한 리소스에 적용되지 않습니다.

7. 플레이북 5단계의 SCP가 조직 수준에서 액션을 제한하면 IAM 권한이 오버라이드됩니다. SCP는 최대 권한을 설정하며, IAM 정책은 SCP 경계를 넘어서는 권한을 부여할 수 없습니다.

8. 플레이북 6단계의 리소스 기반 정책이 주체를 명시적으로 Deny하거나, 교차 계정 접근에 ID 기반과 리소스 기반 모두 Allow가 필요한 경우 어느 한쪽의 권한 누락이 접근을 차단합니다.

9. 플레이북 7단계의 CloudTrail 이벤트에서 특정 인가 실패 컨텍스트가 확인되면 오류 세부사항을 사용하여 어떤 정책(ID 기반, 리소스 기반, SCP, 권한 경계)이 거부를 유발했는지 식별합니다.

수집된 데이터에서 상관관계가 발견되지 않는 경우: CloudTrail 쿼리 기간을 1시간으로 확장하고, IAM 정책 크기 제한(사용자 2 KB, 역할 5 KB, 관리형 정책 10 KB)을 확인하고, 유효 권한을 제한하는 권한 경계를 확인하고, 위임된 역할의 세션 정책을 조사합니다. 접근 실패는 정책 버전 문제, AWS 관리형 정책 업데이트, 신뢰 정책 설정 오류로 인해 발생할 수 있습니다.
