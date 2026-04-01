---
category: incident-response
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/AWS%20Playbooks/01-Compute/Instance-Cant-Reach-Internet-via-NAT-Gateway-EC2.md)'
role: SRE / AWS Incident Response
origin: scoutflo
extract_date: 2026-03-05
tags:
- cant
- compute
- ec2
- gateway
- incident-response
- instance
- internet
- k8s-service
- networking
- performance
- reach
- security
- sts
- vpc
---

# EC2 인스턴스가 NAT Gateway를 통해 인터넷에 접근할 수 없음 (Instance Can't Reach Internet via NAT Gateway)

## 의미

프라이빗 서브넷의 EC2 인스턴스가 NAT Gateway를 통해 인터넷에 접근할 수 없습니다(네트워크 연결 에러 또는 EC2InstanceNATConnectivityFailed 알람 트리거). 인스턴스가 프라이빗 서브넷에 있지 않거나, NAT Gateway가 퍼블릭 서브넷과 연결되지 않았거나, 라우트 테이블에 NAT Gateway로의 라우트가 없거나, 보안 그룹 또는 네트워크 ACL이 아웃바운드 트래픽을 차단하거나, NAT Gateway 상태가 비가용이거나, 연결 테스트가 실패하거나, NAT Gateway Elastic IP가 연결되지 않았기 때문입니다. 프라이빗 서브넷의 인스턴스가 인터넷에 접근할 수 없고, 소프트웨어 업데이트가 실패하며, 외부 API 호출이 타임아웃됩니다. 이는 네트워킹 계층에 영향을 미치며 아웃바운드 인터넷 접근을 차단합니다. 일반적으로 NAT Gateway 설정 이슈, 라우트 테이블 문제, 또는 보안 그룹 제한이 원인이며, AWS Direct Connect 또는 VPN을 사용하는 경우 라우팅이 다를 수 있고 애플리케이션에서 외부 의존성 실패가 발생할 수 있습니다.

## 영향

프라이빗 서브넷의 인스턴스가 인터넷에 접근 불가; 소프트웨어 업데이트 실패; 외부 API 호출 타임아웃; 아웃바운드 연결 차단; NAT Gateway 라우팅 실패; 네트워크 연결 에러 발생; 외부 서비스에 대한 애플리케이션 의존성 실패; 보안 패치 다운로드 불가; 서비스 통합 중단. EC2InstanceNATConnectivityFailed 알람 발생; AWS Direct Connect 또는 VPN을 사용하는 경우 라우팅 충돌 발생 가능; 외부 의존성 누락으로 인해 애플리케이션에 에러 또는 성능 저하 발생 가능; 퍼블릭 레지스트리에서 컨테이너 이미지 풀 불가.

## 플레이북

1. 인스턴스 `<instance-id>`와 NAT Gateway `<nat-gateway-id>`가 존재하고, 리전 `<region>`에서 EC2 및 VPC의 AWS 서비스 상태가 정상인지 확인합니다.
2. EC2 인스턴스 `<instance-id>`를 조회하여 서브넷 설정과 라우트 테이블 연결을 확인하고, 서브넷이 퍼블릭이 아닌지 검증하여 프라이빗 서브넷에 있는지 확인합니다.
3. NAT Gateway `<nat-gateway-id>`를 조회하여 퍼블릭 서브넷과 연결되어 있는지 확인하고, NAT Gateway 상태와 서브넷 연결을 점검하여 게이트웨이가 "available" 상태인지 확인합니다.
4. NAT Gateway `<nat-gateway-id>`의 Elastic IP 연결을 조회하여 Elastic IP가 NAT Gateway에 연결되어 있는지 확인하고, EIP 연결 상태를 점검합니다.
5. 인스턴스 `<instance-id>`가 포함된 프라이빗 서브넷의 라우트 테이블 `<route-table-id>`을 조회하여 NAT Gateway로의 라우트(0.0.0.0/0 → nat-gateway-id)가 있는지 확인하고, 라우트 테이블 연결을 점검합니다.
6. 인스턴스 `<instance-id>`의 보안 그룹 `<security-group-id>`과 네트워크 ACL `<nacl-id>`을 조회하여 인터넷 접근을 허용하는 아웃바운드 규칙을 확인하고, 이그레스 규칙을 검증합니다.
7. NAT Gateway가 포함된 퍼블릭 서브넷의 라우트 테이블 `<route-table-id>`을 조회하여 퍼블릭 서브넷에 인터넷 게이트웨이로의 라우트가 있는지 확인하고, 인터넷 게이트웨이 라우트를 점검합니다.
8. NAT Gateway `<nat-gateway-id>`의 CloudWatch 메트릭(BytesOutToDestination, BytesInFromDestination, 대역폭 사용률 포함)을 조회하여 트래픽 흐름을 확인하고, NAT Gateway가 트래픽을 처리하고 있으며 용량 제한에 도달하지 않았는지 점검합니다.
9. VPC Flow Logs가 포함된 로그 그룹의 CloudWatch Logs를 조회하여 인스턴스 `<instance-id>`에서의 차단된 아웃바운드 트래픽을 필터링하고, 플로우 로그를 분석합니다.

## 진단

1. 플레이북 1단계의 AWS 서비스 상태를 분석하여 리전 내 EC2 및 VPC 서비스 가용성을 확인합니다. 서비스 상태에 이슈가 있으면, 연결 실패는 설정 변경이 아닌 모니터링이 필요한 AWS 측 문제일 수 있습니다.

2. 플레이북 3단계의 NAT Gateway 상태가 "available"이 아닌 경우, NAT Gateway가 작동하지 않습니다. 상태 변경 타임스탬프를 확인하여 연결 이슈가 시작된 시점과 상관관계를 분석합니다. "failed" 또는 "deleted" 같은 상태는 NAT Gateway 문제를 나타냅니다.

3. 플레이북 4단계의 NAT Gateway Elastic IP가 연결되지 않은 경우, NAT Gateway가 인터넷으로 트래픽을 라우팅할 수 없습니다. EIP 연결 상태와 연결 타임스탬프를 확인합니다.

4. 플레이북 5단계의 프라이빗 서브넷 라우트 테이블에 NAT Gateway로의 라우트(0.0.0.0/0 -> nat-*)가 없으면, 아웃바운드 인터넷 트래픽에 경로가 없습니다. 라우트가 존재하고 올바른 NAT Gateway ID를 대상으로 하는지 확인합니다.

5. 플레이북 2단계의 인스턴스 서브넷 설정에서 인스턴스가 퍼블릭 서브넷(프라이빗이 아닌)에 있으면, NAT Gateway가 아닌 인터넷 게이트웨이를 직접 사용해야 합니다. 서브넷 분류를 확인합니다.

6. 플레이북 7단계의 퍼블릭 서브넷 라우트 테이블에 인터넷 게이트웨이로의 라우트가 없으면, NAT Gateway 자체가 인터넷에 접근할 수 없습니다. NAT Gateway가 작동하려면 인터넷 접근이 필요합니다.

7. 플레이북 6단계의 보안 그룹 또는 NACL이 인스턴스에서의 아웃바운드 트래픽을 차단하면, NAT Gateway에 도달하기 전에 이그레스가 차단됩니다. 아웃바운드 규칙이 필요한 트래픽을 허용하는지 확인합니다.

8. 플레이북 8단계의 NAT Gateway 메트릭에서 BytesOutToDestination이 0이거나 매우 낮으면, NAT Gateway가 트래픽을 처리하지 않고 있습니다. 높은 ErrorPortAllocation은 포트 고갈을 나타냅니다.

9. 플레이북 9단계의 VPC Flow Logs에서 아웃바운드 트래픽에 REJECT 액션이 표시되면, 거부가 보안 그룹, NACL, 또는 라우트 수준에서 발생하는지 파악합니다.

수집된 데이터에서 상관관계를 찾을 수 없는 경우: VPC Flow Log 조회 기간을 1시간으로 확장하고, NAT Gateway 대역폭 제한을 확인하고, AWS Direct Connect 또는 VPN에서의 충돌 라우트가 없는지 검증하고, 여러 AZ에 걸친 NAT Gateway 고가용성을 검사합니다. 연결 실패는 NAT Gateway 포트 고갈, 대역폭 스로틀링, 또는 비대칭 라우팅 설정으로 인해 발생할 수 있습니다.
