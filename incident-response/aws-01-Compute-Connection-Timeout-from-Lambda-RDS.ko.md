---
category: incident-response
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/AWS%20Playbooks/01-Compute/Connection-Timeout-from-Lambda-RDS.md)'
role: SRE / AWS Incident Response
origin: scoutflo
extract_date: 2026-03-05
tags:
- cloudwatch
- compute
- connection
- database
- from
- incident-response
- k8s-service
- lambda
- networking
- performance
- rds
- security
- sts
- timeout
- vpc
---

# Lambda에서 RDS 연결 타임아웃 (RDS Connection Timeout from Lambda)

## 의미

Lambda 함수가 RDS 데이터베이스에 연결할 수 없습니다(연결 타임아웃 에러 또는 LambdaRDSConnectionTimeout 알람 트리거). 데이터베이스가 실행 중이지 않거나, VPC 보안 그룹이 인바운드 접근을 차단하거나, 서브넷 그룹 설정이 잘못되었거나, 데이터베이스가 잘못된 가용 영역에 있거나, 필요한 퍼블릭 접근이 비활성화되었거나, Lambda VPC 설정이 누락되었거나, 동일 VPC에서의 연결 테스트가 실패하거나, Lambda ENI 생성 지연이 연결을 방해하기 때문입니다. Lambda 함수가 데이터베이스에 접근할 수 없고, 연결 타임아웃 에러가 발생하며, CloudWatch Logs에 연결 실패가 표시됩니다. 이는 서버리스 및 데이터베이스 통합 계층에 영향을 미치며 데이터 접근을 차단합니다. 일반적으로 VPC 네트워킹 이슈, 보안 그룹 제한, 또는 Lambda VPC 설정 문제가 원인이며, Lambda 컨테이너 이미지를 사용하는 경우 VPC 설정이 다를 수 있고 애플리케이션에서 데이터베이스 연결 에러가 발생할 수 있습니다.

## 영향

Lambda 함수가 데이터베이스에 접근 불가; 연결 타임아웃 에러 발생; 데이터베이스 쿼리 실패; 애플리케이션 데이터 작업 에러; Lambda 함수 실행 실패; 커넥션 풀 고갈 가능; RDS 연결 타임아웃 알람 발생 가능; 서비스-데이터베이스 간 통신 단절; 데이터 처리 워크플로우 실패. LambdaRDSConnectionTimeout 알람 발생; Lambda 컨테이너 이미지를 사용하는 경우 VPC ENI 생성이 더 오래 걸릴 수 있음; 데이터베이스 비가용으로 인해 애플리케이션에 에러 또는 성능 저하 발생 가능; VPC가 포함된 Lambda 함수 Cold Start가 상당한 지연을 추가할 수 있음.

## 플레이북

1. Lambda 함수 `<function-name>`과 RDS 인스턴스 `<rds-instance-id>`가 존재하고, 리전 `<region>`에서 Lambda 및 RDS의 AWS 서비스 상태가 정상인지 확인합니다.
2. 리전 `<region>`의 RDS 인스턴스 `<rds-instance-id>`를 조회하여 인스턴스 상태를 확인하고, 인스턴스가 "available" 상태인지 검증하여 데이터베이스가 실행 중인지 확인합니다.
3. RDS 인스턴스 `<rds-instance-id>`와 연관된 보안 그룹 `<security-group-id>`를 조회하여 VPC 보안 그룹의 인바운드 규칙이 Lambda 실행 환경에서의 접근을 허용하는지 확인하고, Lambda 보안 그룹 소스를 검증합니다.
4. Lambda 함수 `<function-name>`의 VPC 설정을 조회하여 Lambda가 올바른 서브넷과 보안 그룹으로 VPC에 설정되어 있는지 확인하고, Lambda 보안 그룹에 RDS 접근을 허용하는 아웃바운드 규칙이 있는지 확인하며, Lambda 서브넷이 RDS 서브넷 그룹과 동일한 VPC에 있는지 검증합니다. VPC 서브넷 설정, 보안 그룹 이그레스 규칙, VPC ID 일치를 점검합니다.
5. RDS 인스턴스 `<rds-instance-id>`의 서브넷 그룹 설정을 조회하여 서브넷 그룹과 데이터베이스가 올바른 가용 영역에 있는지 확인하고, 서브넷 그룹 가용 영역을 점검합니다.
6. VPC Flow Logs 또는 Lambda 함수 로그가 포함된 로그 그룹의 CloudWatch Logs를 조회하여 Lambda 보안 그룹에서 RDS 엔드포인트 `<rds-endpoint>`로의 차단된 트래픽 또는 VPC ENI 생성 에러(연결 타임아웃 에러 포함)를 필터링하고, 플로우 로그 및 Lambda 로그를 분석합니다.
7. Lambda 함수 `<function-name>`의 CloudWatch 메트릭(Duration 포함)을 조회하여 VPC ENI 생성 시간을 확인하고, ENI 생성 지연이 타임아웃을 유발하는지 점검합니다.

## 진단

1. 플레이북 1단계의 AWS 서비스 상태를 분석하여 리전 내 Lambda 및 RDS 서비스 가용성을 확인합니다. 서비스 상태에 이슈가 있으면, 연결 타임아웃은 설정 변경이 아닌 모니터링이 필요한 AWS 측 문제일 수 있습니다.

2. 플레이북 2단계의 RDS 인스턴스 상태가 "available" 상태가 아닌 경우, 데이터베이스를 사용할 수 없습니다. 상태 변경 타임스탬프와 원인(유지보수, 페일오버, 스토리지 이슈)에 대한 RDS 이벤트를 확인합니다.

3. 플레이북 3단계의 보안 그룹에 데이터베이스 포트에서 Lambda 보안 그룹의 트래픽을 허용하는 인바운드 규칙이 없으면, 네트워크 접근이 차단되어 있습니다. Lambda 보안 그룹이 허용된 소스로 등록되어 있는지 확인합니다.

4. 플레이북 4단계의 Lambda VPC 설정에서 함수가 VPC에 없거나 RDS와 다른 VPC에 있으면, 네트워크 연결이 불가능합니다. VPC ID가 일치하고 Lambda 서브넷이 RDS 서브넷으로 라우팅할 수 있는지 확인합니다.

5. 플레이북 4단계의 Lambda 보안 그룹 이그레스 규칙이 RDS 포트로의 아웃바운드 트래픽을 허용하지 않으면, Lambda 함수가 연결을 시작할 수 없습니다. 이그레스 규칙이 데이터베이스 포트 접근을 허용하는지 확인합니다.

6. 플레이북 5단계의 RDS 서브넷 그룹에서 데이터베이스가 Lambda 서브넷이 커버하지 않는 가용 영역에 있으면, 교차 AZ 라우팅이 실패할 수 있습니다. Lambda 서브넷이 RDS와 동일한 AZ에 걸쳐 있는지 확인합니다.

7. 플레이북 6단계의 VPC Flow Logs 또는 Lambda 로그에서 차단된 트래픽 또는 ENI 생성 에러가 표시되면, 구체적인 차단 원인(보안 그룹, NACL, 또는 ENI 제한)을 파악합니다.

8. 플레이북 7단계의 Lambda Duration 메트릭에서 연결 실패와 상관관계가 있는 연장된 Cold Start 시간이 보이면, VPC ENI 생성 지연이 초기 호출 시 타임아웃을 유발하고 있습니다.

수집된 데이터에서 상관관계를 찾을 수 없는 경우: VPC Flow Log 조회 기간을 30분으로 확장하고, 데이터베이스 연결 제한(max_connections)을 검토하고, VPC 엔드포인트 설정 오류를 확인하고, Lambda 실행 역할 권한을 검사합니다. 연결 타임아웃은 데이터베이스 커넥션 풀 고갈, DNS 해석 실패, 또는 RDS Proxy 설정 이슈로 인해 발생할 수 있습니다.
