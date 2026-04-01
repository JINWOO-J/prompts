---
category: incident-response
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/AWS%20Playbooks/02-Database/Instance-Not-Connecting-RDS.md)'
role: SRE / AWS Incident Response
origin: scoutflo
extract_date: 2026-03-05
tags:
- cloudwatch
- connecting
- database
- incident-response
- instance
- k8s-service
- performance
- rds
- security
- storage
- sts
---

# RDS Instance Not Connecting - RDS 인스턴스 연결 불가

## 의미

RDS 데이터베이스 연결이 타임아웃되거나 실패하는 현상(RDSInstanceUnavailable 또는 DatabaseConnectionErrors와 같은 경보 트리거)은 보안 그룹 규칙이 접근을 차단하거나, 데이터베이스가 사용 불가 상태이거나, 네트워크 연결 문제가 존재하거나, 연결 제한에 도달하거나, 데이터베이스 자격 증명이 잘못되었거나, RDS Proxy 구성이 연결을 차단할 때 발생합니다.
 데이터베이스 연결이 "Connection timed out" 또는 "Connection refused" 오류를 반환하고, RDS 인스턴스 상태는 "available"이지만 연결이 실패하며, CloudWatch 지표에 연결 실패가 표시됩니다. 이는 데이터베이스 계층에 영향을 미치며 데이터 접근을 방해합니다. 일반적으로 보안 그룹 제한, 네트워크 구성 문제, 커넥션 풀 소진 또는 RDS Proxy 잘못된 구성이 원인이며, RDS Aurora를 사용하는 경우 스토리지 모델 차이가 연결 동작에 영향을 미칠 수 있고 애플리케이션에서 데이터베이스 연결 오류가 발생할 수 있습니다.

## 영향

데이터베이스 연결이 실패합니다. 애플리케이션이 데이터에 접근할 수 없습니다. 읽기/쓰기 작업이 타임아웃됩니다. 커넥션 풀 소진이 발생합니다. 애플리케이션 오류가 증가합니다. RDSInstanceUnavailable 또는 DatabaseConnectionErrors 경보가 발생합니다. 애플리케이션 로그에 연결 거부 오류가 나타납니다. 데이터베이스가 사실상 애플리케이션에서 접근 불가능해집니다. 데이터베이스 쿼리가 타임아웃됩니다. 트랜잭션 실패가 발생합니다. RDS Aurora를 사용하는 경우 읽기 복제본 연결이 실패할 수 있습니다. 데이터베이스 사용 불가로 인해 애플리케이션에서 오류나 성능 저하가 발생할 수 있으며, 커넥션 풀 제한에 도달하여 새 연결이 방해될 수 있습니다.

## 플레이북

1. RDS 인스턴스 `<rds-instance-id>`가 존재하고 "available" 상태인지, 리전 `<region>`의 RDS AWS 서비스 상태가 정상인지 확인합니다.
2. 리전 `<region>`의 RDS 인스턴스 `<rds-instance-id>`를 조회하여 "available" 상태인지 확인하고, 상태 및 유지보수 윈도우 상태를 점검합니다.
3. RDS 인스턴스 `<rds-instance-id>`와 연관된 보안 그룹 `<security-group-id>`를 조회하여 올바른 포트(예: MySQL 3306, PostgreSQL 5432)에서 트래픽을 허용하는 인바운드 규칙을 확인하고, 소스 보안 그룹 또는 CIDR 블록을 검증합니다.
4. RDS 인스턴스 파라미터 그룹 설정을 조회하여 인증 관련 파라미터를 확인하고 데이터베이스 자격 증명 구성을 검증합니다.
5. RDS 인스턴스 `<rds-instance-id>`의 연결 엔드포인트를 조회하여 엔드포인트 구성을 확인하고, RDS Proxy 엔드포인트를 사용하는지 직접 인스턴스 엔드포인트를 사용하는지 점검합니다.
6. RDS Proxy를 사용하는 경우 RDS Proxy `<proxy-name>` 구성을 조회하여 프록시 엔드포인트, 대상 그룹 구성, IAM 인증 설정을 검증합니다.
7. RDS 인스턴스 `<rds-instance-id>`의 CloudWatch 지표(DatabaseConnections)를 조회하여 연결 수를 max_connections 파라미터와 비교하고 연결 제한 소진을 확인합니다.
8. VPC Flow Logs 또는 RDS 인스턴스 로그가 포함된 CloudWatch Logs 로그 그룹에서 RDS 엔드포인트 `<rds-endpoint>` 포트 `<port>`로의 차단된 트래픽이나 연결 오류, 인증 실패, 데이터베이스 오류를 필터링하여 플로우 로그 및 RDS 로그를 분석합니다.
9. RDS 인스턴스 `<rds-instance-id>`가 포함된 서브넷의 라우트 테이블 `<route-table-id>`를 조회하여 애플리케이션 서브넷에서의 트래픽을 허용하는 라우트 테이블 구성을 검증합니다.

## 진단

1. 플레이북 1단계의 AWS 서비스 상태를 분석하여 리전의 RDS 서비스 가용성을 확인합니다. 서비스 상태에 문제가 있으면 연결 실패는 구성 변경이 아닌 모니터링이 필요한 AWS 측 문제일 수 있습니다.

2. 플레이북 2단계의 RDS 인스턴스 상태가 "available"이 아닌 경우(예: "maintenance", "backing-up", "rebooting") 데이터베이스가 일시적으로 접근 불가능합니다. 유지보수 윈도우 상태와 예상 완료 시간을 확인합니다.

3. 플레이북 3단계의 보안 그룹 인바운드 규칙이 클라이언트 보안 그룹 또는 IP에서 데이터베이스 포트(MySQL 3306, PostgreSQL 5432)로의 트래픽을 허용하지 않으면 네트워크 접근이 차단된 것입니다. 소스 구성을 확인합니다.

4. 플레이북 5단계의 RDS 엔드포인트가 애플리케이션이 사용하는 엔드포인트와 다르면 연결 시도가 잘못된 주소를 대상으로 하고 있는 것입니다. 이는 Multi-AZ 장애 조치 후 애플리케이션이 이전 IP를 캐시할 때 흔히 발생합니다.

5. 플레이북 6단계의 RDS Proxy 구성에서 프록시가 활성화되어 있지만 잘못 구성된 경우, 프록시 엔드포인트, 대상 그룹, IAM 인증 설정을 검증합니다. 프록시 잘못된 구성은 RDS가 정상이어도 연결 실패를 유발합니다.

6. 플레이북 7단계의 DatabaseConnections 지표가 max_connections 파라미터와 같거나 초과하면 연결 제한 소진이 발생하고 있는 것입니다. 풀이 가득 차면 새 연결이 거부됩니다.

7. 플레이북 8단계의 VPC Flow Logs 또는 RDS 로그에서 차단된 트래픽이나 인증 실패가 표시되면 구체적인 실패 원인(네트워크 거부 vs 자격 증명 오류 vs SSL/TLS 문제)을 파악합니다.

8. 플레이북 9단계의 라우트 테이블이 애플리케이션 서브넷과 RDS 서브넷 간 트래픽을 허용하지 않으면 라우팅 구성이 연결을 방해하고 있는 것입니다. 교차 VPC인 경우 VPC 피어링 또는 Transit Gateway 라우트를 확인합니다.

상관관계를 찾을 수 없는 경우: VPC Flow Log 쿼리 기간을 30분으로 확장하고, RDS 엔드포인트의 DNS 해석을 확인하고, 애플리케이션 측 커넥션 풀 소진을 점검하고, SSL 인증서 요구사항을 확인합니다. 연결 실패는 자격 증명 만료, SSL/TLS 버전 불일치 또는 RDS Performance Insights 리소스 소비로 인해 발생할 수 있습니다.