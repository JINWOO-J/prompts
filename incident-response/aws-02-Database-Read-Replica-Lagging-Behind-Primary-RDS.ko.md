---
category: incident-response
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/AWS%20Playbooks/02-Database/Read-Replica-Lagging-Behind-Primary-RDS.md)'
role: SRE / AWS Incident Response
origin: scoutflo
extract_date: 2026-03-05
tags:
- behind
- cloudwatch
- database
- incident-response
- k8s-service
- lagging
- performance
- primary
- rds
- read
- replica
- scaling
---

# RDS Read Replica Lagging Behind Primary - RDS 읽기 복제본 프라이머리 대비 지연

## 의미

RDS 읽기 복제본에서 복제 지연이 발생하는 현상(ReplicaLag 또는 RDSReadReplicaLag와 같은 경보 트리거)은 복제본 인스턴스의 성능이 부족하거나, 복제 설정이 지연을 유발하거나, 프라이머리 인스턴스의 쓰기 부하가 과도하거나, 프라이머리와 복제본 간 네트워크 지연이 높거나, 복제 스레드 구성이 최적이 아니거나, 읽기 복제본 인스턴스 클래스가 프라이머리보다 작을 때 발생합니다.
 읽기 복제본 데이터가 오래되고, 읽기 쿼리가 오래된 결과를 반환하며, 복제 지연이 허용 가능한 임계값을 초과합니다. 이는 데이터베이스 계층에 영향을 미치며 읽기 일관성에 영향을 줍니다. 일반적으로 인스턴스 크기 문제, 복제 구성 문제 또는 쓰기 부하 증가가 원인이며, RDS Aurora를 사용하는 경우 복제 지연 동작이 다르고 애플리케이션에서 읽기 일관성 문제가 발생할 수 있습니다.

## 영향

읽기 복제본 데이터가 오래됩니다. 읽기 쿼리가 오래된 결과를 반환합니다. 복제 지연이 증가합니다. ReplicaLag 경보가 발생합니다. 읽기 스케일링 이점이 감소합니다. 최종 일관성이 지연됩니다. 읽기 복제본이 프라이머리 쓰기를 따라잡을 수 없습니다. 복제본에서의 애플리케이션 읽기가 불일치한 데이터를 볼 수 있습니다. RDSReadReplicaLag 경보가 발생할 수 있으며, RDS Aurora를 사용하는 경우 복제 지연 동작이 표준 RDS와 다릅니다. 오래된 데이터로 인해 애플리케이션에서 오류나 성능 저하가 발생할 수 있으며, 읽기 워크로드 분산이 효과적이지 않을 수 있습니다.

## 플레이북

1. RDS 읽기 복제본 `<replica-instance-id>`와 프라이머리 인스턴스 `<primary-instance-id>`가 존재하고 "available" 상태인지, 리전 `<region>`의 RDS AWS 서비스 상태가 정상인지 확인합니다.
2. RDS 읽기 복제본 `<replica-instance-id>`의 CloudWatch 지표(ReplicaLag)를 최근 1시간 동안 조회하여 지연 패턴과 급증을 파악하고, 지연 추세를 분석합니다.
3. 리전 `<region>`의 RDS 읽기 복제본 `<replica-instance-id>`를 조회하여 인스턴스 클래스, 복제 구성, 복제 상태를 점검하고, 프라이머리 인스턴스와 인스턴스 클래스를 비교합니다.
4. RDS 프라이머리 인스턴스 `<primary-instance-id>`의 CloudWatch 지표(WriteIOPS, WriteThroughput)를 최근 1시간 동안 조회하여 쓰기 부하를 평가하고, 쓰기 부하 패턴을 분석합니다.
5. RDS 이벤트가 포함된 CloudWatch Logs 로그 그룹에서 복제본 `<replica-instance-id>`의 복제 오류 이벤트나 지연 관련 패턴을 필터링하여 복제 오류 메시지를 확인합니다.
6. RDS 읽기 복제본 `<replica-instance-id>`와 연관된 ReplicaLag 지표의 CloudWatch 경보를 조회하고 ALARM 상태인 경보를 확인하며, 경보 임계값 구성을 검증합니다.
7. RDS 읽기 복제본 `<replica-instance-id>`의 CloudWatch 지표(CPUUtilization, NetworkReceiveThroughput)를 조회하여 리소스 사용률을 확인하고, 리소스 제약이 복제에 영향을 미치는지 점검합니다.
8. RDS 읽기 복제본 `<replica-instance-id>`와 프라이머리 인스턴스 `<primary-instance-id>`의 리전 구성을 조회하여 교차 리전 복제 지연이 지연에 기여하는지 확인하고, 리전 위치를 점검합니다.
9. CloudTrail 이벤트가 포함된 CloudWatch Logs 로그 그룹에서 최근 24시간 이내 복제본 `<replica-instance-id>` 관련 RDS 복제 구성 변경 이벤트를 필터링하여 구성 변경 사항을 확인합니다.

## 진단

1. CloudWatch 경보 이력(플레이북 6단계)을 분석하여 ReplicaLag 경보가 처음 ALARM 상태에 진입한 시점을 파악합니다. 이 타임스탬프가 복제 지연이 허용 가능한 임계값을 초과한 시점을 확립합니다.

2. 프라이머리 인스턴스의 WriteIOPS 및 WriteThroughput 지표(플레이북 4단계)에서 경보 시점 전후로 급증이 표시되면 프라이머리의 높은 쓰기 부하가 복제본의 처리 능력을 압도하고 있는 것입니다.

3. 복제본 인스턴스 클래스(플레이북 3단계)가 프라이머리 인스턴스 클래스보다 작으면 복제본의 성능이 부족할 수 있습니다. CPUUtilization 및 NetworkReceiveThroughput(플레이북 7단계)을 비교하여 높은 값이면 복제본의 리소스 제약을 나타냅니다.

4. 지연 추세(플레이북 2단계)에서 급증이 아닌 지속적으로 높은 지연을 보이면 복제본이 워크로드에 비해 영구적으로 부족한 것입니다. 지연 급증이 쓰기 부하 급증과 상관관계를 보이면 일시적인 쓰기 버스트가 문제입니다.

5. CloudTrail에서 지연 증가 시점 전후로 복제 파라미터 변경(플레이북 9단계)이 표시되면 해당 파라미터 변경이 복제 스레드 성능이나 바이너리 로그 처리에 영향을 미쳤을 수 있습니다.

6. 복제본과 프라이머리가 다른 리전에 있는 경우(플레이북 8단계), 네트워크 지연 패턴을 확인합니다. 교차 리전 복제는 본질적으로 더 높은 지연을 가지며, 상당한 증가는 네트워크 경로 문제를 나타냅니다.

7. 복제 이벤트 로그(플레이북 5단계)에서 경보 타임스탬프 전후로 복제 오류나 중단이 표시되면 복제 스레드 실패나 재시작이 지연 축적을 유발할 수 있습니다.

상관관계를 찾을 수 없는 경우: 분석 기간을 24시간으로 확장하고, 바이너리 로그 복제 진행 상황을 검토하고, Aurora 전용 복제 지연 패턴을 확인하고, Multi-AZ 읽기 복제본 구성을 검증하고, 교차 리전 네트워크 연결을 점검합니다.