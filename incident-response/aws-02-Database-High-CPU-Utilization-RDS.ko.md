---
category: incident-response
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/AWS%20Playbooks/02-Database/High-CPU-Utilization-RDS.md)'
role: SRE / AWS Incident Response
origin: scoutflo
extract_date: 2026-03-05
tags:
- cloudwatch
- database
- high
- incident-response
- k8s-service
- performance
- rds
- storage
- sts
- utilization
---

# RDS High CPU Utilization - RDS 높은 CPU 사용률

## 의미

RDS 인스턴스에서 지속적으로 높은 CPU 사용률이 발생하는 현상(CPUUtilizationHigh 또는 RDSHighCPU와 같은 경보 트리거)은 데이터베이스 쿼리가 비효율적이거나, 커넥션 풀 소진으로 CPU 경합이 발생하거나, 인스턴스 유형이 워크로드에 비해 부족하거나, 백그라운드 유지보수 작업이 CPU를 소비하거나, 데이터베이스 파라미터 그룹 설정이 최적이 아니거나, 읽기 복제본 지연 처리가 CPU 사용량을 증가시킬 때 발생합니다.
 데이터베이스 성능이 저하되고, 쿼리 응답 시간이 증가하며, CPU 사용률이 지속적으로 임계값을 초과합니다. 이는 데이터베이스 계층에 영향을 미치며 애플리케이션 성능에 영향을 줍니다. 일반적으로 쿼리 최적화 문제, 인스턴스 크기 문제 또는 워크로드 증가가 원인이며, RDS Aurora를 사용하는 경우 스토리지 모델 차이가 CPU 동작에 영향을 미칠 수 있고 애플리케이션에서 데이터베이스 성능 저하가 발생할 수 있습니다.

## 영향

CPUUtilizationHigh 경보가 발생합니다. 데이터베이스 성능이 저하됩니다. 쿼리 응답 시간이 증가합니다. 애플리케이션 연결이 타임아웃됩니다. 데이터베이스가 응답하지 않게 됩니다. 읽기 및 쓰기 작업이 느려집니다. 커넥션 풀 소진이 발생합니다. 데이터베이스 복제 지연이 증가합니다. 애플리케이션 성능이 심각하게 영향을 받습니다. RDSHighCPU 경보가 발생할 수 있으며, RDS Aurora를 사용하는 경우 공유 스토리지 모델로 인해 CPU 사용률 패턴이 다를 수 있습니다. 데이터베이스 속도 저하로 인해 애플리케이션에서 오류나 성능 저하가 발생할 수 있으며, 사용자 대면 서비스의 지연이 증가합니다.

## 플레이북

1. RDS 인스턴스 `<db-instance-id>`가 존재하고 "available" 상태인지, 리전 `<region>`의 RDS AWS 서비스 상태가 정상인지 확인합니다.
2. RDS 인스턴스 `<db-instance-id>`의 CloudWatch 지표(CPUUtilization)를 최근 1시간 동안 조회하여 CPU 사용 패턴과 급증을 파악하고, 시간에 따른 CPU 추세를 분석합니다.
3. 리전 `<region>`의 RDS 인스턴스 `<db-instance-id>`를 조회하여 인스턴스 클래스, 파라미터 그룹 구성, Performance Insights 상태를 점검하고, 인스턴스 유형이 워크로드에 적합한지 검증합니다.
4. RDS Performance Insights 또는 슬로우 쿼리 로그가 포함된 CloudWatch Logs 로그 그룹에서 인스턴스 `<db-instance-id>`의 높은 CPU 쿼리 패턴을 필터링하여 쿼리 실행 시간 지표를 확인합니다.
5. RDS 인스턴스 `<db-instance-id>`와 연관된 CPUUtilization 지표의 CloudWatch 경보를 조회하고 ALARM 상태인 경보를 확인하며, 경보 임계값 구성을 검증합니다.
6. RDS 인스턴스 `<db-instance-id>`의 CloudWatch 지표(DatabaseConnections)를 조회하여 연결 수 패턴을 확인하고, 커넥션 풀 소진이 CPU 경합에 기여하는지 점검합니다.
7. 리전 `<region>`에서 `<db-instance-id>`와 동일한 인스턴스 클래스의 RDS 인스턴스를 나열하고 CPU 사용률 패턴을 비교하여 문제가 인스턴스 고유의 것인지 판단하며, 유사 인스턴스 간 CPU 사용률을 분석합니다.
8. RDS 인스턴스 `<db-instance-id>`의 파라미터 그룹 설정을 조회하여 파라미터 그룹 구성을 검증하고, 쿼리 성능에 영향을 미치는 파라미터 설정을 점검합니다.
9. CloudTrail 이벤트가 포함된 CloudWatch Logs 로그 그룹에서 최근 24시간 이내 인스턴스 `<db-instance-id>` 관련 RDS 파라미터 그룹 변경 이벤트를 필터링하여 파라미터 변경 사항을 확인합니다.

## 진단

1. CloudWatch 경보 이력(플레이북 5단계)을 분석하여 CPUUtilizationHigh 또는 RDSHighCPU 경보가 처음 ALARM 상태에 진입한 시점을 파악합니다. 이 타임스탬프가 이후 모든 분석의 상관관계 기준선이 됩니다.

2. Performance Insights 또는 슬로우 쿼리 로그(플레이북 4단계)에서 경보 시점 전후로 높은 CPU를 소비하는 특정 쿼리가 표시되면 해당 비효율적인 쿼리가 근본 원인일 가능성이 높습니다. CPU 시간이 높거나 전체 테이블 스캔을 수행하는 쿼리에 집중합니다.

3. 특정 쿼리가 식별되지 않으면 연결 수 패턴(플레이북 6단계)을 확인합니다. 경보 시점 전후로 DatabaseConnections가 급증했다면 커넥션 풀 소진이나 연결 폭주가 CPU 경합을 유발하고 있는 것입니다.

4. 연결 수가 정상이면 CPU 급증과 CloudTrail의 파라미터 그룹 변경(플레이북 9단계)을 비교합니다. 최근 파라미터 변경이 쿼리 옵티마이저 동작이나 버퍼 풀 크기에 영향을 미쳤을 수 있습니다.

5. 파라미터 변경이 없으면 24시간 동안의 CPU 추세(플레이북 2단계)를 분석합니다. 점진적 증가는 더 큰 인스턴스 클래스가 필요한 워크로드 증가를 나타내며, 갑작스러운 급증은 쿼리 패턴 변경이나 배치 작업 실행을 나타냅니다.

6. 인스턴스 클래스 비교(플레이북 7단계)에서 유사 인스턴스의 CPU가 더 낮으면 문제는 인스턴스 크기보다 워크로드 고유의 것일 가능성이 높습니다. 대기 이벤트에 대해 Performance Insights(플레이북 3단계)를 확인합니다.

7. Aurora를 사용하는 경우(플레이북 3단계), 공유 스토리지 모델로 인해 대량 읽기 작업 시 표준 RDS와 다른 CPU 패턴을 보일 수 있습니다.

상관관계를 찾을 수 없는 경우: 분석 기간을 4시간으로 확장하고, 대기 이벤트와 상위 쿼리에 대한 Performance Insights를 검토하고, 인덱스 단편화나 테이블 비대화를 확인하고, 장애 조치 이벤트 시 Multi-AZ 복제 오버헤드를 검증하고, 최적화 기회를 위한 쿼리 실행 계획을 점검합니다.