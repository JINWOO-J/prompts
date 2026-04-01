---
category: incident-response
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/AWS%20Playbooks/04-Networking/Peering-Not-Working-VPC.md)'
role: SRE / AWS Incident Response
origin: scoutflo
extract_date: 2026-03-05
tags:
- dns
- incident-response
- k8s-service
- networking
- peering
- performance
- security
- sts
- vpc
- working
---

# VPC Peering Not Working - VPC 피어링 미작동

## 의미

VPC 피어링 연결이 VPC 간 트래픽을 라우팅하지 못하는 현상(네트워크 연결 오류 또는 VPCPeeringConnectionFailed 경보 트리거)은 피어링 연결이 Active 상태가 아니거나, 라우트 테이블에 피어링된 VPC에 대한 라우트가 없거나, 보안 그룹 또는 Network ACL이 VPC 간 트래픽을 차단하거나, 프라이빗 IP 주소에 대한 DNS 해석이 비활성화되었거나, CIDR 블록 겹침이 피어링을 방해할 때 발생합니다.
 VPC 간 통신이 실패하고, 다른 VPC의 서비스가 통신할 수 없으며, 네트워크 연결 오류가 발생합니다. 이는 네트워킹 계층에 영향을 미치며 교차 VPC 통신을 차단합니다.

## 영향

VPC 간 통신이 실패합니다. 다른 VPC의 서비스가 통신할 수 없습니다. VPC 피어링 라우트가 효과가 없습니다. 네트워크 연결 오류가 발생합니다. 교차 VPC 리소스 접근이 차단됩니다. VPC 간 애플리케이션 통합이 실패합니다. VPC 간 데이터 복제가 중지됩니다. 서비스 종속성이 중단됩니다.

## 플레이북

1. VPC 피어링 연결 `<peering-connection-id>`가 존재하고 양쪽 VPC가 존재하며, 리전 `<region>`의 VPC AWS 서비스 상태가 정상인지 확인합니다.
2. VPC 피어링 연결 `<peering-connection-id>`를 조회하여 "Active" 상태인지 확인하고, 연결 상태를 점검하며, 양쪽 VPC 소유자가 피어링 연결을 수락했는지 검증합니다.
4. VPC `<vpc-id>`의 라우트 테이블 `<route-table-id>`를 조회하여 피어링된 VPC CIDR 블록에 대한 라우트가 포함되어 있는지 확인합니다.
5. 양쪽 VPC의 라우트 테이블 `<route-table-id>`를 조회하여 양방향 라우트가 존재하는지 확인합니다.
6. 양쪽 VPC의 인스턴스에 대한 보안 그룹 `<security-group-id>` 및 Network ACL `<nacl-id>`를 조회하여 VPC 간 트래픽을 허용하는 규칙을 확인합니다.
7. VPC 피어링 연결 `<peering-connection-id>`의 DNS 설정을 조회하여 프라이빗 IP 주소에 대한 DNS 해석이 활성화되어 있는지 확인합니다.
8. 양쪽 VPC의 VPC `<vpc-id>` CIDR 블록을 조회하여 CIDR 블록이 겹치지 않는지 확인합니다.
9. VPC 피어링 연결 `<peering-connection-id>`의 CloudWatch 지표(가용한 경우)를 조회하여 트래픽 흐름 지표를 확인합니다.
10. VPC Flow Logs가 포함된 CloudWatch Logs에서 VPC 간 차단된 트래픽을 필터링합니다.

## 진단

1. 플레이북 1단계의 AWS 서비스 상태를 분석하여 리전의 VPC 서비스 가용성을 확인합니다.

2. 플레이북 2단계의 피어링 연결 상태가 "active"가 아니면 피어링이 작동하지 않습니다. "pending-acceptance"는 피어 VPC 소유자가 수락하지 않은 것이며, "failed" 또는 "rejected"는 구성 또는 권한 문제를 나타냅니다.

3. 플레이북 8단계의 CIDR 블록에서 두 VPC 간 겹치는 IP 범위가 표시되면 피어링이 불가능합니다. 겹치는 CIDR은 라우트 테이블 항목이 로컬 트래픽과 피어링된 트래픽을 구분하는 것을 방해합니다.

4. 플레이북 4~5단계의 라우트 테이블에 피어링 연결(pcx-*)을 가리키는 피어링된 VPC CIDR 블록에 대한 라우트가 없으면 트래픽이 피어 VPC로 갈 경로가 없습니다. 양쪽 VPC에 양방향 라우트가 존재하는지 확인합니다.

5. 플레이북 6단계의 보안 그룹이 피어 VPC CIDR 범위에서의 트래픽을 허용하지 않으면 VPC 간 통신이 차단됩니다.

6. 플레이북 6단계의 Network ACL에 피어 VPC CIDR에 대한 Deny 규칙이 포함되어 있거나 명시적 Allow 규칙이 없으면 NACL이 트래픽을 차단하고 있는 것입니다.

7. 플레이북 7단계의 DNS 해석 설정에서 DNS 해석이 비활성화되어 있으면 인스턴스가 피어링 연결을 통해 프라이빗 DNS 호스트 이름을 해석할 수 없습니다.

8. 플레이북 10단계의 VPC Flow Logs에서 VPC 간 트래픽에 대한 REJECT 작업이 표시되면 거부하는 구성 요소와 차단을 유발하는 구체적인 규칙을 파악합니다.

상관관계를 찾을 수 없는 경우: VPC Flow Log 쿼리 기간을 1시간으로 확장하고, AWS Organizations의 교차 계정 피어링 수락을 확인하고, Transit Gateway 라우트 테이블 충돌을 점검하고, 해당되는 경우 IPv6 피어링 구성을 확인합니다.