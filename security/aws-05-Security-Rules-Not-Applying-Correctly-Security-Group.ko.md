---
category: security
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/AWS%20Playbooks/05-Security/Rules-Not-Applying-Correctly-Security-Group.md)'
role: SRE / AWS Incident Response
origin: scoutflo
extract_date: 2026-03-05
tags:
- applying
- correctly
- ec2
- group
- k8s-service
- networking
- performance
- rules
- security
- sts
- vpc
- waf
---

# Security Group 규칙 미적용 — Security Group Rules Not Applying Correctly

## 의미

Security Group 규칙이 예상 트래픽을 허용하지 못합니다(연결 타임아웃 오류 또는 SecurityGroupRuleNotEffective 알람 발생). 원인으로는 잘못된 포트 개방, 충돌하는 인바운드/아웃바운드 규칙의 트래픽 차단, Security Group이 올바른 인스턴스에 연결되지 않음, IP 주소나 CIDR 블록의 잘못된 제한, 연결 테스트 실패, Security Group 규칙 평가 순서의 접근 영향, 규칙 할당량 도달 등이 있습니다. 예상 네트워크 트래픽이 차단되고, 연결 타임아웃이 발생하며, Security Group 규칙이 무효화됩니다. 이는 보안 및 네트워킹 계층에 영향을 미치며 네트워크 접근을 차단합니다. 일반적으로 규칙 구성 문제, 평가 순서 문제, 할당량 제한이 원인이며, AWS WAF를 사용하는 경우 WAF 규칙이 Security Group과 상호작용할 수 있고 애플리케이션에서 네트워크 접근 실패가 발생할 수 있습니다.

## 영향

예상 네트워크 트래픽 차단, 연결 타임아웃 발생, Security Group 규칙 무효, 애플리케이션 통신 실패, 서비스 엔드포인트 접근 불가, 연결 거부 오류 발생, 네트워크 접근 거부, 방화벽 규칙 예상대로 미작동, 네트워크 접근이 필요한 운영 작업 실패. SecurityGroupRuleNotEffective 알람 발생. AWS WAF를 사용하는 경우 WAF 규칙이 Security Group과 상호작용할 수 있음. 네트워크 접근 실패로 인해 애플리케이션 오류나 성능 저하 발생 가능. 서비스 간 통신이 차단될 수 있습니다.

## 플레이북

1. Security Group `<security-group-id>`와 EC2 인스턴스 `<instance-id>`의 존재를 확인하고 리전 `<region>`의 EC2 및 VPC AWS 서비스 상태가 정상인지 확인합니다.
2. EC2 인스턴스 `<instance-id>`에 연결된 Security Group `<security-group-id>`를 조회하여 인바운드 규칙에서 올바른 포트(예: SSH용 22, HTTP용 80)가 개방되었는지 확인하고 포트 범위와 프로토콜을 확인합니다.
3. Security Group `<security-group-id>`를 조회하여 트래픽을 차단할 수 있는 충돌하는 인바운드/아웃바운드 규칙을 확인하고, 규칙 평가 로직(명시적 Deny 우선)을 검증하고, IP 주소나 CIDR 블록을 제한하는 규칙을 검토하며 규칙 평가 순서와 소스 CIDR 블록을 확인합니다.
4. 인스턴스 `<instance-id>`의 인스턴스 Security Group 연결을 조회하여 Security Group `<security-group-id>`가 올바른 인스턴스에 연결되었는지 확인하고 다중 Security Group 연결을 확인합니다.
5. Security Group `<security-group-id>`의 규칙 할당량을 조회하여 Security Group 규칙 제한이 초과되지 않았는지 확인하고 할당량 대비 규칙 수를 확인합니다.
6. 인스턴스 `<instance-id>`의 NetworkIn 및 NetworkOut을 포함한 CloudWatch 메트릭을 조회하여 네트워크 활동을 확인하고 트래픽이 인스턴스에 도달하는지 확인합니다.
7. VPC Flow Logs 또는 WAF 로그가 포함된 CloudWatch Logs 로그 그룹을 조회하여 Security Group `<security-group-id>`와 관련된 차단 트래픽을 필터링하고 Flow Log 및 WAF 규칙 평가를 확인합니다.

## 진단

1. 플레이북 1단계의 AWS 서비스 상태를 분석하여 해당 리전의 EC2 및 VPC 서비스 가용성을 확인합니다. 서비스 상태에 문제가 있으면 규칙 적용 실패는 구성 변경이 아닌 AWS 측 문제로 모니터링이 필요합니다.

2. 플레이북 2단계의 Security Group 인바운드 규칙에 필요한 포트(SSH용 22, HTTP용 80, HTTPS용 443)가 포함되지 않으면 해당 포트의 트래픽이 차단됩니다. Security Group은 인바운드 트래픽에 대해 기본 거부입니다.

3. 플레이북 3단계의 Security Group 규칙에서 충돌하는 구성이 확인되면, Security Group에는 Allow 규칙만 있다는 점을 기억합니다(명시적 Deny 없음). 트래픽이 차단되면 매칭되는 Allow 규칙이 없기 때문입니다. 지나치게 제한적인 CIDR 블록이나 Security Group 참조를 확인합니다.

4. 플레이북 4단계의 Security Group 연결에서 Security Group이 대상 인스턴스에 연결되지 않았거나 충돌하는 의도의 여러 Security Group이 연결된 경우, 올바른 Security Group이 연결되었는지 확인합니다. 여러 Security Group은 OR 로직으로 평가됩니다(어떤 Allow든 트래픽을 허용).

5. 플레이북 5단계의 규칙 할당량에서 Security Group이 규칙 제한(기본 인바운드 60 + 아웃바운드 60)에 도달한 경우 추가 규칙을 추가할 수 없습니다. 할당량 대비 현재 규칙 수를 확인합니다.

6. 플레이북 6단계의 NetworkIn/NetworkOut 메트릭에서 트래픽이 인스턴스에 도달하는 것으로 확인되면 문제는 Security Group이 아닌 애플리케이션 계층에 있을 수 있습니다. 애플리케이션이 예상 포트에서 리스닝하고 있는지 확인합니다.

7. 플레이북 7단계의 VPC Flow Logs 또는 WAF 로그에서 REJECT 액션이 확인되면 거부하는 계층을 식별합니다. Security Group 거부는 Flow Logs에 특정 액션 유형으로 나타나고, WAF 거부는 WAF 로그에 규칙 ID와 함께 나타납니다.

수집된 데이터에서 상관관계가 발견되지 않는 경우: VPC Flow Log 쿼리 기간을 30분으로 확장하고, Network ACL 규칙이 트래픽을 차단하지 않는지 확인하고(NACL은 Security Group보다 먼저 평가됨), 인스턴스 수준 방화벽 규칙(iptables, Windows Firewall)을 확인하고, 소스 IP 주소 변경을 조사합니다. 연결 실패는 Security Group 전파 지연(일반적으로 수 초), 클라이언트 측 NAT IP 변경, AWS Shield DDoS 보호 활성화로 인해 발생할 수 있습니다.
