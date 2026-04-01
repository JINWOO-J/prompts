---
category: security
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/AWS%20Playbooks/05-Security/Rules-Causing-False-Positives-WAF.md)'
role: SRE / AWS Incident Response
origin: scoutflo
extract_date: 2026-03-05
tags:
- causing
- cloudfront
- cloudwatch
- 'false'
- k8s-service
- performance
- positives
- rules
- security
- sts
- waf
---

# WAF 규칙 오탐 발생 — AWS WAF Rules Causing False Positives

## 의미

AWS WAF 규칙이 오탐을 발생시킵니다(잘못된 차단 또는 WAFFalsePositive 알람 발생). 원인으로는 WAF 규칙이 너무 제한적이거나, 규칙 조건이 정상 요청을 잘못 매칭하거나, 규칙 우선순위로 인한 잘못된 차단, 속도 기반 규칙이 정상 트래픽에 트리거되거나, IP 평판 규칙이 유효한 IP를 차단하거나, WAF 규칙 액션 오버라이드가 규칙을 잘못 허용하는 경우입니다. 정상 사용자 트래픽이 차단되고, WAF 규칙이 오탐을 발생시키며, 정상 요청이 403 Forbidden 오류를 반환합니다. 이는 보안 및 애플리케이션 접근 계층에 영향을 미치며 애플리케이션 가용성을 저하시킵니다. 일반적으로 규칙 설정 오류, 조건 임계값 문제, 우선순위 충돌이 원인이며, CloudFront와 Application Load Balancer에서 WAF를 사용할 때 규칙 동작이 다를 수 있고 애플리케이션에서 오탐 차단이 발생할 수 있습니다.

## 영향

정상 사용자 트래픽 차단, WAF 규칙 오탐 발생, 정상 요청에 403 Forbidden 오류 반환, 사용자 접근 부당 거부, WAF 차단 알람 발생, 애플리케이션 가용성 영향, 보안 규칙 과도한 적용, 사용자 경험 저하. WAFFalsePositive 알람 발생 가능. CloudFront와 Application Load Balancer에서 WAF를 사용할 때 규칙 동작이 다를 수 있음. 차단된 정상 트래픽으로 인해 애플리케이션 오류나 성능 저하 발생 가능. 사용자 대면 서비스가 접근 불가능해질 수 있습니다.

## 플레이북

1. WAF Web ACL `<web-acl-id>`의 존재를 확인하고 리전 `<region>`의 WAF AWS 서비스 상태가 정상인지 확인합니다.
2. 리전 `<region>`의 WAF Web ACL `<web-acl-id>`를 조회하여 규칙 구성, 규칙 우선순위, 규칙 액션, 규칙 조건을 검사하고 규칙 평가 순서를 확인합니다.
3. WAF 로그가 포함된 CloudWatch Logs 로그 그룹을 조회하여 Web ACL `<web-acl-id>`와 관련된 차단 요청 패턴, 403 오류 패턴, 오탐 지표를 필터링하고 차단 사유 세부사항을 포함합니다.
4. WAF Web ACL `<web-acl-id>`의 BlockedRequests 및 AllowedRequests를 포함한 CloudWatch 메트릭을 지난 24시간 동안 조회하여 차단 패턴을 식별하고 차단 빈도를 분석합니다.
5. Web ACL `<web-acl-id>`의 WAF 규칙 평가 결과를 나열하고 규칙 매칭 패턴, 차단 사유, 요청 특성을 확인하며 규칙 매칭을 분석합니다.
6. 애플리케이션 접근 로그가 포함된 CloudWatch Logs 로그 그룹을 조회하여 WAF에 의해 차단된 정상 요청을 필터링하고 요청 세부사항을 포함합니다.
7. WAF Web ACL `<web-acl-id>`의 기본 액션을 조회하여 기본 액션 구성을 확인하고 기본 액션이 정상 트래픽에 영향을 미치는지 확인합니다.
8. WAF Web ACL `<web-acl-id>`의 연결된 리소스(CloudFront 배포 또는 ALB)를 조회하여 WAF 연결을 확인하고 연결이 규칙 평가에 영향을 미치는지 확인합니다.
9. CloudTrail 이벤트가 포함된 CloudWatch Logs 로그 그룹을 조회하여 지난 24시간 동안 `<web-acl-id>`와 관련된 WAF 규칙 또는 Web ACL 수정 이벤트를 필터링하고 규칙 변경을 확인합니다.

## 진단

1. **3단계 및 5단계의 WAF 로그 분석**: 차단된 요청 패턴과 차단을 유발하는 특정 규칙에 대한 WAF 로그를 검토합니다. 3단계의 WAF 로그에서 특정 규칙 ID가 지속적으로 정상 트래픽을 차단하는 것으로 식별되면 해당 규칙을 조정해야 합니다. 차단된 요청에서 `terminatingRuleId`와 요청 특성을 추출합니다. 로그에서 여러 규칙이 차단하는 것으로 확인되면 2단계로 진행합니다.

2. **4단계의 차단 메트릭 평가**: 4단계의 CloudWatch 메트릭에서 BlockedRequests가 특정 시간에 급증하거나 정상 트래픽 패턴(예: 업무 시간, 배포)과 상관관계가 있으면 트래픽 패턴 변화가 과도하게 민감한 규칙을 트리거하는 것입니다. BlockedRequests 대 AllowedRequests 비율을 비교합니다 - 차단율이 예상 기준선을 초과하면 규칙 민감도가 너무 높은 것입니다. 3단계로 진행합니다.

3. **2단계의 규칙 구성 검토**: 차단 규칙에 지나치게 광범위한 정규식 패턴, 낮은 속도 기반 임계값, 공격적인 SQL 인젝션/XSS 탐지가 포함되어 있으면 규칙 조건을 정제해야 합니다. 규칙 우선순위를 확인합니다 - 차단 규칙이 트래픽을 화이트리스트해야 하는 허용 규칙보다 높은 우선순위를 가지면 우선순위 설정 오류가 있는 것입니다. 규칙이 올바른 것으로 보이면 4단계로 진행합니다.

4. **6단계의 애플리케이션 접근 패턴 확인**: 6단계의 애플리케이션 로그에서 정상 요청이 403 오류로 차단되는 것으로 확인되면 요청 특성과 WAF 규칙 조건의 상관관계를 분석합니다. 정상 요청에 보안 규칙과 매칭되는 패턴(예: 코드 스니펫, 특수 문자)이 포함되어 있으면 규칙 예외나 커스텀 규칙이 필요합니다. 차단된 요청의 User-Agent, IP, 경로를 비교하여 패턴을 식별합니다.

5. **9단계의 규칙 수정 상관관계 분석**: 9단계의 CloudTrail 이벤트에서 오탐 시작 5분 이내에 WAF 규칙 또는 Web ACL 수정이 확인되면 최근 변경이 문제를 도입한 것입니다. 관리형 규칙 그룹 업데이트를 검토합니다 - AWS Managed Rules가 업데이트되었으면 새로운 시그니처가 오탐을 유발할 수 있습니다.

**상관관계가 발견되지 않는 경우**: WAF 로그를 사용하여 분석을 30일로 확장합니다. 4단계 메트릭의 정상 트래픽 볼륨 대비 속도 기반 규칙 임계값을 확인합니다. IP 평판 목록이 정상 트래픽을 차단하지 않는지 확인합니다. 관리형 규칙이 문제를 유발하는 경우 규칙 액션 오버라이드를 사용하여 차단 대신 카운트로 변경하거나 특정 예외를 추가하는 것을 고려합니다. 커스텀 규칙과 관리형 규칙의 충돌을 검토합니다.
