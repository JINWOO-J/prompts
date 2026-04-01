---
category: incident-response
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/AWS%20Playbooks/04-Networking/Connection-Dropping-Frequently-VPN.md)'
role: SRE / AWS Incident Response
origin: scoutflo
extract_date: 2026-03-05
tags:
- cloudwatch
- connection
- dropping
- frequently
- incident-response
- k8s-service
- networking
- performance
- sts
- vpc
---

# VPN Connection Dropping Frequently - VPN 연결 빈번한 끊김

## 의미

VPN 연결이 빈번하게 끊기는 현상(연결 실패 또는 VPNConnectionDropped 경보 트리거)은 VPN 터널 안정성 문제가 발생하거나, 네트워크 경로 변경이 터널 재협상을 유발하거나, VPN 게이트웨이 또는 고객 게이트웨이 구성이 잘못되었거나, 터널 인증이 실패하거나, 네트워크 지연이 터널 타임아웃을 유발하거나, VPN 게이트웨이 리소스 제약이 불안정을 유발할 때 발생합니다.
 VPN 연결이 빈번하게 끊기고, 원격 접근이 중단되며, 사이트 간 연결이 실패합니다. 이는 네트워킹 계층에 영향을 미치며 연결을 방해합니다. 일반적으로 터널 구성 문제, 네트워크 경로 문제 또는 게이트웨이 리소스 제약이 원인이며, Direct Connect와 함께 AWS Site-to-Site VPN을 사용하는 경우 라우팅이 안정성에 영향을 미칠 수 있고 애플리케이션에서 연결 중단이 발생할 수 있습니다.

## 영향

VPN 연결이 빈번하게 끊깁니다. 원격 접근이 중단됩니다. 사이트 간 연결이 실패합니다. VPN 터널 재협상이 발생합니다. 연결 안정성이 손상됩니다. 사용자 연결이 불안정합니다. VPN 연결 경보가 발생합니다. 네트워크 안정성이 저하됩니다. VPNConnectionDropped 경보가 발생할 수 있으며, Direct Connect와 함께 AWS Site-to-Site VPN을 사용하는 경우 라우팅이 안정성에 영향을 미칠 수 있습니다. 연결 중단으로 인해 애플리케이션에서 오류나 성능 저하가 발생할 수 있으며, 사이트 간 연결이 불안정할 수 있습니다.

## 플레이북

1. VPN 연결 `<vpn-connection-id>`가 존재하고 리전 `<region>`의 VPC AWS 서비스 상태가 정상인지 확인합니다.
2. 리전 `<region>`의 VPN 연결 `<vpn-connection-id>`를 조회하여 터널 상태, 연결 상태, 터널 구성을 점검하고, 터널 상태를 검증합니다.
3. VPN 연결 로그가 포함된 CloudWatch Logs 로그 그룹에서 터널 다운 이벤트, 재협상 패턴 또는 연결 실패 메시지를 필터링하여 터널 상태 전환을 확인합니다.
4. VPN 연결 `<vpn-connection-id>`의 CloudWatch 지표(TunnelState, TunnelDataIn, TunnelDataOut)를 최근 1시간 동안 조회하여 연결 끊김 패턴을 파악하고, 끊김 빈도를 분석합니다.
5. VPN 연결 `<vpn-connection-id>`와 연관된 CloudWatch 경보를 조회하고 터널 상태 관련 ALARM 상태인 경보를 확인하며, 경보 구성을 검증합니다.
6. 연결 `<vpn-connection-id>`의 VPN 연결 이벤트를 나열하고 터널 상태 변경 타임스탬프와 재협상 빈도를 확인하여 연결 안정성을 분석합니다.
7. VPN 연결 `<vpn-connection-id>`의 고객 게이트웨이 구성을 조회하여 고객 게이트웨이 IP 주소와 라우팅 구성을 확인하고, 게이트웨이 구성을 점검합니다.
8. VPN 연결 `<vpn-connection-id>`의 CloudWatch 지표(TunnelState)를 조회하여 터널 업/다운 패턴을 확인하고, 양쪽 터널 모두 영향을 받는지 점검합니다.
9. CloudTrail 이벤트가 포함된 CloudWatch Logs 로그 그룹에서 최근 24시간 이내 연결 `<vpn-connection-id>` 관련 VPN 연결 또는 고객 게이트웨이 변경 이벤트를 필터링하여 구성 변경 사항을 확인합니다.

## 진단

1. CloudWatch 경보 이력(플레이북 5단계)을 분석하여 VPNConnectionDropped 또는 터널 상태 경보가 처음 트리거된 시점을 파악합니다. 이 타임스탬프가 연결 불안정이 시작된 시점을 확립합니다.

2. CloudWatch 지표(플레이북 4단계)에서 경보 시점 전후로 TunnelState 전환(업에서 다운)이 표시되면 양쪽 터널 모두 영향을 받는지 하나의 터널만 영향을 받는지 확인합니다. 단일 터널 문제는 터널 고유 구성을 시사하며, 양쪽 터널 모두는 게이트웨이 또는 네트워크 문제를 시사합니다.

3. VPN 연결 로그(플레이북 3단계)에서 끊김 타임스탬프 전후로 재협상 패턴이나 인증 실패가 표시되면 IKE Phase 1 또는 Phase 2 협상 문제가 리키 작업 중 끊김을 유발하고 있는 것입니다.

4. TunnelDataIn/TunnelDataOut 지표(플레이북 4단계 및 8단계)에서 끊김 전에 트래픽이 중지되면 유휴 기간으로 인해 DPD(Dead Peer Detection) 타임아웃이 터널 해제를 트리거할 수 있습니다.

5. CloudTrail에서 끊김 타임스탬프 전후로 VPN 구성 변경(플레이북 9단계)이 표시되면 해당 변경이 터널 재협상이나 호환되지 않는 설정을 유발했을 수 있습니다.

6. 고객 게이트웨이 구성(플레이북 7단계)에서 최근 IP 주소 또는 라우팅 변경이 표시되면 고객 게이트웨이가 AWS VPN 터널 구성 요구사항과 일치하는지 확인합니다.

7. 연결 이벤트 이력(플레이북 6단계)에서 일정한 간격으로 주기적 끊김이 표시되면 DPD 타임아웃 또는 리키 타이머 잘못된 구성이 예측 가능한 터널 순환을 유발하고 있을 가능성이 높습니다.

상관관계를 찾을 수 없는 경우: 분석 기간을 24시간으로 확장하고, 인증 실패에 대한 고객 게이트웨이 로그를 검토하고, VPN 장애 조치에 영향을 미치는 Direct Connect 라우팅 충돌을 확인하고, 고객 게이트웨이와 AWS 엔드포인트 간 인터넷 경로 안정성을 검증하고, VPN 게이트웨이 리소스 제약을 점검합니다.