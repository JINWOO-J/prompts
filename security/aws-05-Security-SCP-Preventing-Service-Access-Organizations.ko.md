---
category: security
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/AWS%20Playbooks/05-Security/SCP-Preventing-Service-Access-Organizations.md)'
role: SRE / AWS Incident Response
origin: scoutflo
extract_date: 2026-03-05
tags:
- access
- cloudwatch
- k8s-service
- organizations
- performance
- preventing
- security
- service
- sts
---

# Organizations SCP 서비스 접근 차단 — AWS Organizations SCP Preventing Service Access

## 의미

AWS Organizations 서비스 제어 정책(SCP)이 서비스 접근을 차단하고 있습니다(접근 거부 오류 또는 OrganizationsSCPAccessDenied 알람 발생). 원인으로는 SCP 정책이 필요한 서비스 액션을 거부하거나, SCP 정책 조건이 너무 제한적이거나, SCP 정책이 잘못된 조직 단위(OU)에 연결되었거나, SCP 정책 평가가 정상 접근을 차단하거나, SCP 정책 구문에 오류가 있는 경우입니다. AWS Organizations SCP가 서비스 접근을 차단하고, 서비스 작업이 거부되며, 접근 거부 오류가 발생합니다. 이는 거버넌스 및 접근 통제 계층에 영향을 미치며 서비스 작업을 차단합니다. 일반적으로 SCP 정책 설정 오류, 조건 임계값 문제, OU 연결 문제가 원인이며, 여러 OU가 있는 Organizations를 사용하는 경우 SCP 계층 구조가 접근에 영향을 줄 수 있고 애플리케이션에서 서비스 접근 실패가 발생할 수 있습니다.

## 영향

AWS Organizations SCP 서비스 접근 차단, 서비스 작업 거부, SCP 정책 제한으로 정상 접근 차단, 접근 거부 오류 발생, 서비스 자동화 차단, 조직 정책 적용 과도, 서비스 접근 부당 제한. OrganizationsSCPAccessDenied 알람 발생 가능. 여러 OU가 있는 Organizations를 사용하는 경우 SCP 계층 구조가 접근에 영향을 줄 수 있음. 차단된 서비스 접근으로 인해 애플리케이션 오류나 성능 저하 발생 가능. 서비스 작업이 완전히 차단될 수 있습니다.

## 플레이북

1. AWS Organizations SCP `<scp-id>`의 존재를 확인하고 리전 `<region>`의 Organizations AWS 서비스 상태가 정상인지 확인합니다.
2. AWS Organizations 서비스 제어 정책 `<scp-id>`를 조회하여 정책 문서, 정책 연결, 조직 단위 연결, 정책 조건을 검사하고 정책 구문을 확인합니다.
3. CloudTrail 이벤트가 포함된 CloudWatch Logs 로그 그룹을 조회하여 SCP `<scp-id>`와 관련된 접근 거부 이벤트, SCP 정책 평가 패턴, 서비스 접근 실패를 필터링하고 접근 거부 세부사항을 포함합니다.
4. SCP `<scp-id>`가 연결된 AWS Organizations 조직 단위 `<ou-id>`를 조회하여 OU 구조, 계정 연결, SCP 정책 계층 구조를 검사하고 SCP 연결 구성을 확인합니다.
5. SCP `<scp-id>`에 의해 거부된 AWS 서비스 API 호출을 나열하고 거부된 액션 패턴, 서비스 패턴, 계정 패턴을 확인하며 거부 패턴을 분석합니다.
6. AWS Organizations SCP `<scp-id>`의 정책 평가 순서를 조회하여 정책 평가 계층 구조를 확인하고 여러 SCP가 평가에 영향을 미치는지 확인합니다.
7. CloudTrail 이벤트가 포함된 CloudWatch Logs 로그 그룹을 조회하여 지난 24시간 동안 SCP `<scp-id>`와 관련된 SCP 정책 수정 이벤트나 정책 연결 변경을 필터링하고 구성 변경을 확인합니다.
8. 가용한 경우 AWS Organizations CloudWatch 메트릭을 조회하여 Organizations 서비스 상태를 확인하고 서비스 문제가 SCP 평가에 영향을 미치는지 확인합니다.
9. CloudTrail 이벤트가 포함된 CloudWatch Logs 로그 그룹을 조회하여 지난 24시간 동안 OU `<ou-id>`와 관련된 조직 단위 구조 수정 이벤트를 필터링하고 OU 변경을 확인합니다.

## 진단

1. **3단계의 CloudTrail 이벤트 분석**: 접근 거부 이벤트와 SCP 정책 평가 패턴에 대한 CloudTrail 로그를 검토합니다. CloudTrail에서 오류 컨텍스트에 "Organizations" 또는 "SCP"가 포함된 "AccessDenied"가 확인되면 SCP가 적극적으로 액션을 차단하고 있는 것입니다. 로그에서 구체적으로 거부된 액션과 리소스를 식별합니다. 접근 거부 패턴이 불명확하면 2단계로 진행합니다.

2. **2단계의 SCP 정책 문서 평가**: 2단계의 SCP 정책에 3단계에서 식별된 차단된 서비스 액션과 매칭되는 명시적 "Deny" 문이 포함되어 있으면 정책 구성이 제한을 유발하는 것입니다. 정책 조건을 확인합니다 - `aws:RequestedRegion`, `aws:PrincipalOrgID`, IP 제한 같은 조건이 있으면 요청 컨텍스트가 조건 요구사항과 일치하는지 확인합니다. 정책이 올바른 것으로 보이면 3단계로 진행합니다.

3. **4단계의 SCP 연결 및 OU 계층 구조 확인**: SCP가 이 제한이 적용되지 않아야 하는 OU에 연결되어 있으면 잘못된 연결이 문제입니다. 4단계의 OU 구조를 검토합니다 - 영향받는 계정이 상위 OU에서 상속된 제한적 SCP가 있는 OU에 있으면 정책 계층 구조가 누적 제한을 유발하는 것입니다. 9단계의 CloudTrail 이벤트와 비교합니다 - 접근 거부 1시간 이내에 OU 구조 수정이 발생했으면 최근 OU 변경이 정책 적용에 영향을 미친 것입니다.

4. **7단계의 정책 수정 이벤트 상관관계 분석**: 7단계의 CloudTrail 이벤트에서 접근 거부 시작 5분 이내에 SCP 정책 수정이 확인되면 최근 정책 변경이 제한을 도입한 것입니다. 수정 전후의 정책 버전을 검토하여 거부를 유발한 구체적인 변경을 식별합니다.

5. **6단계의 정책 평가 순서 분석**: 여러 SCP가 다른 수준(루트, OU, 계정)에 연결되어 있으면 결합된 유효 권한을 평가합니다. 계층 구조의 어떤 SCP에서든 명시적 "Allow"가 누락되어 유효 정책 평가가 거부로 이어지면 정책 상속 모델이 제한을 유발하는 것입니다.

**상관관계가 발견되지 않는 경우**: 3단계의 CloudTrail 패턴을 사용하여 분석을 30일로 확장합니다. 조건이 너무 제한적인 SCP 정책 조건 평가 문제를 확인합니다. 8단계의 Organizations 서비스 상태를 확인하고 2단계의 정책 구문 오류가 올바른 평가를 방해하는지 조사합니다. 여러 겹치는 SCP가 의도치 않은 제한을 만드는 SCP 정책 계층 구조 충돌을 검토합니다.
