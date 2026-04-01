---
category: incident-response
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/AWS%20Playbooks/04-Networking/Latency-Higher-Than-Expected-Direct-Connect.md)'
role: SRE / AWS Incident Response
origin: scoutflo
extract_date: 2026-03-05
tags:
- backup
- cloudwatch
- connect
- direct
- expected
- higher
- incident-response
- k8s-service
- latency
- networking
- performance
- sts
- than
---

# Direct Connect Latency Higher Than Expected - Direct Connect 지연 예상보다 높음

## 의미

Direct Connect 지연이 예상보다 높은 현상(성능 문제 또는 DirectConnectHighLatency 경보 트리거)은 네트워크 경로가 최적이 아니거나, Direct Connect 가상 인터페이스 구성이 잘못되었거나, BGP 라우팅 문제가 경로 비효율을 유발하거나, 네트워크 혼잡이 발생하거나, 교차 연결 구성에 문제가 있거나, Direct Connect 링크 사용률이 높아 혼잡을 유발할 때 발생합니다.
 Direct Connect 지연이 증가하고, 네트워크 성능이 저하되며, 애플리케이션 응답 시간이 증가합니다. 이는 네트워킹 및 연결 계층에 영향을 미치며 애플리케이션 성능에 영향을 줍니다. 일반적으로 라우팅 문제, 혼잡 문제 또는 구성 오류가 원인이며, VPN 백업과 함께 Direct Connect를 사용하는 경우 라우팅 동작이 다를 수 있고 애플리케이션에서 지연 문제가 발생할 수 있습니다.

## 영향

Direct Connect 지연이 증가합니다. 네트워크 성능이 저하됩니다. 애플리케이션 응답 시간이 증가합니다. 사용자 경험이 영향을 받습니다. 네트워크 처리량이 감소합니다. 지연에 민감한 애플리케이션이 실패합니다. 네트워크 성능이 SLA 요구사항을 충족하지 못합니다. 연결 품질이 저하됩니다. DirectConnectHighLatency 경보가 발생할 수 있습니다.

## 플레이북

1. Direct Connect 가상 인터페이스 `<virtual-interface-id>`가 존재하고 리전 `<region>`의 Direct Connect AWS 서비스 상태가 정상인지 확인합니다.
2. Direct Connect 가상 인터페이스 `<virtual-interface-id>`의 CloudWatch 지표(Latency, PacketLoss)를 최근 1시간 동안 조회하여 지연 패턴을 파악하고, 지연 추세를 분석합니다.
3. 리전 `<region>`의 Direct Connect 가상 인터페이스 `<virtual-interface-id>`를 조회하여 BGP 구성, 가상 인터페이스 상태, 연결 상태를 점검하고, BGP 상태를 검증합니다.
4. Direct Connect 이벤트가 포함된 CloudWatch Logs 로그 그룹에서 지연 관련 이벤트나 성능 저하 패턴을 필터링하여 성능 이벤트 세부 정보를 확인합니다.
5. 왕복 시간 및 패킷 손실을 포함한 네트워크 성능 CloudWatch 지표를 최근 1시간 동안 조회하여 네트워크 경로 문제를 파악하고, 네트워크 지표를 분석합니다.
6. 가상 인터페이스 `<virtual-interface-id>`의 Direct Connect 연결 이벤트를 나열하고 연결 상태 변경 및 성능 지표를 확인하여 연결 상태를 분석합니다.
7. Direct Connect 가상 인터페이스 `<virtual-interface-id>`의 CloudWatch 지표(BytesIn, BytesOut)를 조회하여 링크 사용률을 확인하고, 높은 사용률이 혼잡을 유발하는지 점검합니다.
8. Direct Connect 가상 인터페이스 `<virtual-interface-id>`의 BGP 라우트를 조회하여 라우트 광고를 확인하고, BGP 라우팅이 지연에 영향을 미치는지 점검합니다.
9. CloudTrail 이벤트가 포함된 CloudWatch Logs 로그 그룹에서 최근 24시간 이내 `<virtual-interface-id>` 관련 Direct Connect 가상 인터페이스 또는 BGP 구성 변경 이벤트를 필터링하여 구성 변경 사항을 확인합니다.

## 진단

1. Direct Connect 가상 인터페이스의 CloudWatch 지표(플레이북 2단계)를 분석하여 최근 1시간 동안의 Latency 및 PacketLoss를 포함한 지연 패턴을 파악합니다. 지연이 갑자기 증가했다면 타임스탬프를 BGP 또는 구성 변경과 상관 분석합니다.

2. 네트워크 성능 지표(플레이북 5단계)를 검토합니다. 패킷 손실이 높으면 재전송으로 인해 직접적으로 지연이 증가합니다. 패킷 손실 없이 왕복 시간이 증가했다면 네트워크 경로가 변경되었을 수 있습니다.

3. Direct Connect 가상 인터페이스 상태 및 BGP 상태(플레이북 3단계)를 확인하여 연결이 활성이고 BGP 세션이 설정되어 있는지 검증합니다. BGP 상태가 Established가 아니면 트래픽이 백업 경로를 통해 라우팅되어 지연이 증가할 수 있습니다.

4. 링크 사용률 지표(플레이북 7단계)를 검토합니다. 링크 사용률이 용량에 근접하면(80% 이상) 혼잡이 지연을 유발할 수 있습니다.

5. BGP 라우트 구성(플레이북 8단계)을 분석하여 라우트 광고가 최적인지 확인합니다. BGP 라우트가 변경되었거나 최적이 아닌 라우트가 선호되면 트래픽이 더 긴 경로를 사용하여 지연이 증가합니다.

6. CloudTrail 이벤트(플레이북 9단계)와 지연 증가 타임스탬프를 5분 이내로 상관 분석하여 가상 인터페이스 또는 BGP 구성 변경을 파악합니다.

7. 1시간 이내 여러 가상 인터페이스에 걸친 지연 패턴을 비교합니다. 지연이 인터페이스 고유의 것이면 해당 인터페이스의 구성과 BGP 설정에 집중합니다. 모든 가상 인터페이스에 영향을 미치는 연결 전체의 것이면 물리적 연결 또는 캐리어 네트워크 수준의 문제입니다.

상관관계를 찾을 수 없는 경우: 기간을 24시간으로 확장하고, BGP 라우트 광고 및 교차 연결 구성을 포함한 대안적 증거 소스를 검토하고, 온프레미스 네트워크 구성이나 캐리어 네트워크 성능과 같은 외부 종속성을 검증합니다.