---
category: incident-response
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/AWS%20Playbooks/02-Database/Query-Performance-Slower-Than-Expected-DynamoDB.md)'
role: SRE / AWS Incident Response
origin: scoutflo
extract_date: 2026-03-05
tags:
- capacity
- cloudwatch
- database
- dynamodb
- expected
- incident-response
- k8s-service
- performance
- query
- slower
- sts
- than
---

# DynamoDB Query Performance Slower Than Expected - DynamoDB 쿼리 성능 예상보다 느림

## 의미

DynamoDB 쿼리 성능이 예상보다 느린 현상(DynamoDBQueryLatency 또는 DynamoDBThrottling과 같은 지연 경보 트리거)은 쿼리 패턴이 비효율적이거나, 글로벌 보조 인덱스가 누락되었거나 잘못 구성되었거나, 프로비저닝된 처리량이 부족하거나, 항목 크기가 커서 스캔 작업이 발생하거나, 핫 파티션이 스로틀링을 유발하거나, DynamoDB 테이블 용량 모드가 쿼리 성능에 영향을 미칠 때 발생합니다. 쿼리 응답 시간이 증가하고, 애플리케이션 성능이 저하되며, 데이터베이스 쿼리가 예상보다 오래 걸립니다. 이는 데이터베이스 계층에 영향을 미치며 애플리케이션 성능에 영향을 줍니다. 일반적으로 인덱스 구성 문제, 용량 제약 또는 쿼리 패턴 문제가 원인이며, DynamoDB Global Tables를 사용하는 경우 복제가 성능에 영향을 미칠 수 있고 애플리케이션에서 쿼리 지연 문제가 발생할 수 있습니다.

## 영향

쿼리 응답 시간이 증가합니다. 애플리케이션 성능이 저하됩니다. 사용자 대면 지연이 증가합니다. DynamoDB 스로틀링이 발생할 수 있습니다. 읽기 용량이 소진됩니다. 쿼리 타임아웃이 발생합니다. 애플리케이션 확장성이 제한됩니다. 데이터베이스 성능이 SLA 요구사항을 충족하지 못합니다. DynamoDBQueryLatency 경보가 발생할 수 있으며, DynamoDB Global Tables를 사용하는 경우 복제가 쿼리 성능에 영향을 미칠 수 있습니다. 느린 쿼리로 인해 애플리케이션에서 오류나 성능 저하가 발생할 수 있으며, 사용자 대면 서비스의 지연이 증가합니다.

## 플레이북

1. DynamoDB 테이블 `<table-name>`이 존재하고 "ACTIVE" 상태인지, 리전 `<region>`의 DynamoDB AWS 서비스 상태가 정상인지 확인합니다.
2. DynamoDB 테이블 `<table-name>`의 CloudWatch 지표(ConsumedReadCapacityUnits, ReadThrottledEvents, SuccessfulRequestLatency)를 최근 1시간 동안 조회하여 성능 패턴을 파악하고, 지연 추세를 분석합니다.
3. 리전 `<region>`의 DynamoDB 테이블 `<table-name>`을 조회하여 테이블 구성, 글로벌 보조 인덱스, 프로비저닝된 읽기 용량 설정, 용량 모드(프로비저닝 vs 온디맨드)를 점검합니다.
4. DynamoDB 접근 로그가 포함된 CloudWatch Logs 로그 그룹에서 테이블 `<table-name>` 관련 느린 쿼리 패턴이나 스로틀링 이벤트를 필터링하여 쿼리 실행 시간 지표를 확인합니다.
5. DynamoDB 테이블 `<table-name>`과 연관된 지연 또는 스로틀링 관련 지표의 CloudWatch 경보를 조회하고 ALARM 상태인 경보를 확인하며, 경보 임계값 구성을 검증합니다.
6. DynamoDB 테이블 `<table-name>`의 CloudWatch 지표(ItemCount, TableSizeBytes)를 조회하여 테이블 크기를 확인하고, 큰 테이블 크기가 쿼리 성능에 영향을 미치는지 점검합니다.
7. DynamoDB 테이블 `<table-name>`의 파티션 키 및 정렬 키 구성을 조회하고 쿼리 패턴을 분석하여 쿼리가 파티션 키를 효과적으로 사용하는지 검증합니다.
8. DynamoDB 테이블 `<table-name>`의 테이블 지표를 나열하고 유사한 테이블과 쿼리 성능 패턴을 비교하여 문제가 테이블 고유의 것인지 판단하며, 성능 차이를 분석합니다.
9. CloudTrail 이벤트가 포함된 CloudWatch Logs 로그 그룹에서 최근 24시간 이내 테이블 `<table-name>` 관련 DynamoDB 인덱스 생성 또는 수정 이벤트를 필터링하여 인덱스 구성 변경 사항을 확인합니다.

## 진단

1. CloudWatch 경보 이력(플레이북 5단계)을 분석하여 DynamoDBQueryLatency 또는 스로틀링 경보가 처음 트리거된 시점을 파악합니다. 이 타임스탬프가 성능 저하가 시작된 시점을 확립합니다.

2. CloudWatch 지표(플레이북 2단계)에서 지연 증가 시점 전후로 ReadThrottledEvents가 표시되면 스로틀링이 직접적으로 쿼리 속도 저하를 유발하고 있는 것입니다. 소비 용량 대비 프로비저닝 용량을 확인하여 확인합니다.

3. 테이블 구성(플레이북 3단계)에서 쿼리가 파티션 키를 사용한 Query 작업 대신 Scan 작업을 사용하고 있으면 인덱스가 누락되었거나 잘못 구성되어 전체 테이블 스캔이 강제되고 있는 것입니다.

4. 글로벌 보조 인덱스가 존재하지만(플레이북 3단계) 쿼리가 여전히 느리면 쿼리 패턴이 올바른 인덱스를 사용하고 있는지 확인합니다. 인덱스를 지정하지 않거나 인덱싱되지 않은 속성을 사용하는 쿼리는 스캔으로 대체됩니다.

5. 테이블 크기 지표(플레이북 6단계)에서 큰 ItemCount 또는 TableSizeBytes를 보이고, 파티션 키 설계(플레이북 7단계)에서 제한된 카디널리티를 보이면 핫 파티션이 불균등한 용량 분배를 유발할 수 있습니다.

6. CloudTrail에서 지연 증가 시점 전후로 용량 변경(플레이북 9단계)이 표시되면 용량 감소가 직접적으로 성능 저하를 유발한 것입니다.

7. 지연이 간헐적이지 않고 지속적인 경우(플레이북 2단계 추세) 문제는 구조적(인덱스 설계)입니다. 간헐적인 경우 문제는 용량 관련(프로비저닝된 처리량 또는 버스트 소진)입니다.

8. 테이블 간 성능 비교(플레이북 8단계)에서 이 테이블만 느린 경우 문제는 테이블 고유의 설계 또는 구성입니다.

상관관계를 찾을 수 없는 경우: 분석 기간을 24시간으로 확장하고, 최적화 기회를 위한 쿼리 패턴을 검토하고, Global Tables 복제 오버헤드를 확인하고, Streams 용량 소비를 검증하고, 지연에 영향을 미치는 큰 항목에 대한 항목 크기 분포를 점검합니다.
