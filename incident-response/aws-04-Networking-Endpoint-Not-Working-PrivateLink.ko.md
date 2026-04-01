---
category: incident-response
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/AWS%20Playbooks/04-Networking/Endpoint-Not-Working-PrivateLink.md)'
role: SRE / AWS Incident Response
origin: scoutflo
extract_date: 2026-03-05
tags:
- cloudwatch
- dns
- endpoint
- incident-response
- k8s-service
- networking
- performance
- privatelink
- security
- sts
- vpc
- working
---

# PrivateLink Endpoint Not Working - PrivateLink 엔드포인트 미작동

## 의미

VPC PrivateLink 엔드포인트가 작동하지 않는 현상(연결 실패 또는 VPCEndpointConnectionFailed 경보 트리거)은 엔드포인트 서비스를 사용할 수 없거나, 엔드포인트 정책이 접근을 제한하거나, 보안 그룹 규칙이 트래픽을 차단하거나, 라우트 테이블 구성이 잘못되었거나, 엔드포인트 서비스 수락이 보류 중이거나, VPC 엔드포인트 DNS 해석이 실패할 때 발생합니다.
 PrivateLink 엔드포인트 연결이 실패하고, 프라이빗 서비스 접근이 차단되며, 엔드포인트 연결을 설정할 수 없습니다. 이는 네트워킹 및 서비스 접근 계층에 영향을 미치며 프라이빗 서비스 연결을 차단합니다. 일반적으로 엔드포인트 구성 문제, 정책 제한 또는 서비스 가용성 문제가 원인입니다.

## 영향

PrivateLink 엔드포인트 연결이 실패합니다. 프라이빗 서비스 접근이 차단됩니다. 엔드포인트 연결을 설정할 수 없습니다. 서비스 간 통신이 실패합니다. 엔드포인트 상태에 실패가 표시됩니다. 프라이빗 네트워크 접근을 사용할 수 없습니다. 애플리케이션 통합이 실패합니다.

## 플레이북

1. VPC 엔드포인트 `<vpc-endpoint-id>`가 존재하고 리전 `<region>`의 VPC AWS 서비스 상태가 정상인지 확인합니다.
2. 리전 `<region>`의 VPC 엔드포인트 `<vpc-endpoint-id>`를 조회하여 엔드포인트 상태, 서비스 이름, 엔드포인트 정책, 연결 상태를 점검하고, 엔드포인트가 "available" 상태인지 검증합니다.
3. VPC 엔드포인트 로그가 포함된 CloudWatch Logs 로그 그룹에서 엔드포인트 실패 이벤트, 연결 오류 또는 정책 거부 패턴을 필터링하여 실패 사유 세부 정보를 확인합니다.
4. VPC 엔드포인트 `<vpc-endpoint-id>`의 CloudWatch 지표(BytesIn, BytesOut)를 최근 1시간 동안 조회하여 연결 패턴을 파악하고, 트래픽 흐름을 분석합니다.
5. VPC 엔드포인트 `<vpc-endpoint-id>`와 연관된 보안 그룹 `<security-group-id>`를 조회하여 엔드포인트 트래픽에 대한 인바운드 및 아웃바운드 규칙을 점검하고, 보안 그룹 규칙을 검증합니다.
6. VPC 엔드포인트 `<vpc-endpoint-id>`가 포함된 서브넷의 라우트 테이블 항목을 나열하고 엔드포인트 트래픽에 대한 라우팅 구성을 확인하여 라우트 테이블 연결을 검증합니다.
7. VPC 엔드포인트 서비스 `<service-name>` 구성을 조회하여 엔드포인트 서비스 수락 상태를 확인하고, 엔드포인트 서비스 수락이 보류 중인지 점검합니다.
8. VPC 엔드포인트 `<vpc-endpoint-id>`의 DNS 구성을 조회하여 엔드포인트에 대한 DNS 해석을 확인하고, DNS 해석이 올바르게 구성되어 있는지 점검합니다.
9. VPC Flow Logs가 포함된 CloudWatch Logs 로그 그룹에서 VPC 엔드포인트 `<vpc-endpoint-id>`로의 또는 로부터의 차단된 트래픽을 필터링하여 플로우 로그를 분석합니다.

## 진단

1. VPC 엔드포인트 상태(플레이북 2단계)를 분석하여 엔드포인트가 실패 또는 사용 불가 상태에 진입한 시점을 파악합니다. 연결 상태를 확인하고 엔드포인트가 "available" 상태인지 검증합니다.

2. 엔드포인트 상태가 "pendingAcceptance"(플레이북 7단계)이면 엔드포인트 서비스 제공자가 연결 요청을 수락하지 않은 것입니다. 서비스 제공자의 조치가 필요합니다.

3. 엔드포인트가 "available"이지만 트래픽이 실패하면 보안 그룹 규칙(플레이북 5단계)을 확인합니다. 보안 그룹이 필요한 포트에서 엔드포인트로의/로부터의 트래픽을 허용하지 않으면 보안 그룹 수준에서 트래픽이 차단됩니다.

4. 보안 그룹이 올바르면 VPC Flow Logs(플레이북 9단계)에서 차단된 트래픽 패턴을 확인합니다.

5. 엔드포인트 정책(플레이북 2단계)이 최근 변경되었다면 제한적인 정책이 특정 서비스나 작업에 대한 접근을 거부하고 있을 수 있습니다.

6. DNS 해석(플레이북 8단계)이 엔드포인트에 대한 프라이빗 IP 주소를 반환하지 않으면 Private DNS가 활성화되지 않았거나 잘못 구성되었을 수 있습니다.

7. CloudWatch 지표(플레이북 4단계)에서 BytesIn/BytesOut이 0이면 트래픽이 엔드포인트에 전혀 도달하지 않고 있는 것입니다. 엔드포인트로의 올바른 라우팅을 위해 라우트 테이블 연결(플레이북 6단계)을 확인합니다.

상관관계를 찾을 수 없는 경우: 분석 기간을 24시간으로 확장하고, 엔드포인트 서비스 제공자 구성을 확인하고, 소비자 VPC에서의 DNS 해석을 점검하고, 엔드포인트 라우팅에 대한 라우트 테이블 항목을 확인하고, 엔드포인트 정책 크기 제한이 초과되지 않았는지 검증합니다.