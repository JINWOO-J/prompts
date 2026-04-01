---
category: security
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/AWS%20Playbooks/05-Security/Blocking-Legitimate-Traffic-WAF.md)'
role: SRE / AWS Incident Response
origin: scoutflo
extract_date: 2026-03-05
tags:
- blocking
- cloudfront
- cloudwatch
- k8s-service
- legitimate
- performance
- security
- sts
- traffic
- waf
---

# AWS WAF 정상 트래픽 차단 — AWS WAF Blocking Legitimate Traffic

## 의미

AWS WAF가 정상 트래픽을 차단하고 있습니다(오탐 또는 WAFBlockingLegitimateTraffic 알람 발생). 원인으로는 WAF 규칙이 너무 제한적이거나, 규칙 조건이 정상 요청을 잘못 매칭하거나, 규칙 우선순위로 인한 잘못된 차단, 속도 기반 규칙이 정상 트래픽에 트리거되거나, IP 평판 규칙이 유효한 IP를 차단하거나, WAF 규칙 액션 오버라이드가 규칙을 잘못 허용하는 경우입니다. 정상 사용자 트래픽이 차단되고, WAF 규칙이 오탐을 발생시키며, 정상 요청이 403 Forbidden 오류를 반환합니다. 이는 보안 및 애플리케이션 접근 계층에 영향을 미치며 애플리케이션 가용성을 저하시킵니다. 일반적으로 규칙 설정 오류, 조건 임계값 문제, 우선순위 충돌이 원인이며, CloudFront와 Application Load Balancer에서 WAF를 사용할 때 규칙 동작이 다를 수 있고 애플리케이션에서 오탐 차단이 발생할 수 있습니다.

## 영향

정상 사용자 트래픽 차단, WAF 규칙 오탐 발생, 정상 요청에 403 Forbidden 오류 반환, 사용자 접근 부당 거부, WAF 차단 알람 발생, 애플리케이션 가용성 영향, 보안 규칙 과도한 적용, 사용자 경험 저하. WAFBlockingLegitimateTraffic 알람 발생 가능. CloudFront와 Application Load Balancer에서 WAF를 사용할 때 규칙 동작이 다를 수 있음. 차단된 정상 트래픽으로 인해 애플리케이션 오류나 성능 저하 발생 가능. 사용자 대면 서비스가 접근 불가능해질 수 있습니다.

## 플레이북

1. WAF Web ACL `<web-acl-id>`의 존재를 확인하고 리전 `<region>`의 WAF AWS 서비스 상태가 정상인지 확인합니다.
2. 리전 `<region>`의 WAF Web ACL `<web-acl-id>`를 조회하여 규칙 구성, 규칙 우선순위, 규칙 액션, 규칙 조건을 검사하고 규칙 평가 순서를 확인합니다.
3. WAF 로그가 포함된 CloudWatch Logs 로그 그룹을 조회하여 Web ACL `<web-acl-id>`와 관련된 차단 요청 패턴, 403 오류 패턴, 오탐 지표를 필터링하고 차단 사유 세부사항을 포함합니다.
4. WAF Web ACL `<web-acl-id>`의 BlockedRequests 및 AllowedRequests를 포함한 CloudWatch 메트릭을 지난 1시간 동안 조회하여 차단 패턴을 식별하고 차단 빈도를 분석합니다.
5. Web ACL `<web-acl-id>`의 WAF 규칙 평가 결과를 나열하고 규칙 매칭 패턴, 차단 사유, 요청 특성을 확인하며 규칙 매칭을 분석합니다.
6. 애플리케이션 접근 로그가 포함된 CloudWatch Logs 로그 그룹을 조회하여 WAF에 의해 차단된 정상 요청을 필터링하고 요청 세부사항을 포함합니다.
7. WAF Web ACL `<web-acl-id>`의 기본 액션을 조회하여 기본 액션 구성을 확인하고 기본 액션이 정상 트래픽에 영향을 미치는지 확인합니다.
8. WAF Web ACL `<web-acl-id>`의 연결된 리소스(CloudFront 배포 또는 ALB)를 조회하여 WAF 연결을 확인하고 연결이 규칙 평가에 영향을 미치는지 확인합니다.
9. CloudTrail 이벤트가 포함된 CloudWatch Logs 로그 그룹을 조회하여 지난 24시간 동안 `<web-acl-id>`와 관련된 WAF 규칙 또는 Web ACL 수정 이벤트를 필터링하고 규칙 변경을 확인합니다.

## 진단

1. WAF 로그가 포함된 CloudWatch Logs(플레이북 3단계)를 분석하여 차단된 요청 패턴을 식별합니다. 차단을 트리거한 특정 규칙과 요청 특성을 포함합니다. 로그에서 특정 규칙이 지속적으로 정상 요청을 차단하는 것으로 확인되면 해당 규칙의 조건을 조정해야 합니다. 여러 규칙이 차단하는 경우 규칙 우선순위 순서를 검토합니다.

2. WAF BlockedRequests 및 AllowedRequests에 대한 CloudWatch 메트릭(플레이북 4단계)을 검토하여 기준 차단 패턴을 수립합니다. 차단 요청 수가 갑자기 증가했다면 타임스탬프를 최근 규칙 수정과 상관관계를 분석합니다. 차단 패턴이 점진적으로 변경되었다면 트래픽 패턴 변화 또는 관리형 규칙 업데이트와 관련될 수 있습니다.

3. WAF 규칙 평가 결과(플레이북 5단계)를 조사하여 어떤 특정 규칙 조건이 정상 요청과 매칭되는지 파악합니다. 규칙 조건이 지나치게 광범위한 패턴(예: 일반적인 요청 문자열과 매칭되는 정규식)을 사용하는 경우 조건을 정제해야 합니다. 속도 기반 규칙이 트리거되는 경우 정상 트래픽 볼륨 대비 임계값을 확인합니다.

4. WAF 로그와 애플리케이션 접근 로그(플레이북 6단계)를 비교하여 차단된 요청이 실제로 정상인지 확인합니다. 차단된 요청에 예상되는 User-Agent 문자열, 유효한 소스 IP, 적절한 요청 형식이 포함되어 있다면 WAF 규칙이 너무 제한적인 것입니다.

5. CloudTrail 이벤트(플레이북 9단계)를 차단 증가 타임스탬프와 5분 이내로 상관관계를 분석하여 WAF 규칙 또는 Web ACL 수정을 식별합니다. 규칙 변경이 차단 증가와 일치하면 해당 변경이 과도하게 제한적인 조건을 도입한 것입니다.

6. WAF 규칙 구성(플레이북 2단계)을 분석합니다. 규칙 우선순위, 액션, 조건을 포함합니다. 관리형 규칙이 커스텀 규칙과 충돌하거나 규칙 우선순위로 인해 잘못된 평가 순서가 발생하면 허용 규칙이 평가되기 전에 정상 트래픽이 차단될 수 있습니다.

7. 속도 기반 규칙이 관련된 경우, 현재 트래픽 볼륨을 속도 기반 규칙 임계값과 비교합니다. 정상 트래픽 패턴이 임계값을 초과하면 임계값을 높이거나 알려진 정상 트래픽 소스에 대한 예외를 추가합니다.

지정된 시간 범위 내에서 상관관계가 발견되지 않는 경우: 기간을 7일로 확장하고, IP 평판 데이터 및 요청 패턴 분석을 포함한 대안적 증거 소스를 검토하고, 규칙 조건 임계값 변경이나 IP 평판 목록 업데이트 같은 점진적 문제를 확인하고, 위협 인텔리전스 피드 업데이트나 규칙 조건 평가 로직 같은 외부 의존성을 확인하고, 오탐의 과거 패턴을 조사하고, WAF 규칙 액션 오버라이드 문제를 확인하고, WAF 커스텀 규칙과 관리형 규칙 충돌을 확인합니다. 오탐은 즉각적인 WAF 규칙 변경이 아닌 규칙 조건 임계값 문제, IP 평판 목록 부정확성, 속도 기반 규칙 설정 오류, WAF 규칙 액션 오버라이드, WAF 커스텀 규칙과 관리형 규칙 충돌로 인해 발생할 수 있습니다.
