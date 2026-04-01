---
category: incident-response
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/AWS%20Playbooks/02-Database/Throttling-Errors-DynamoDB.md)'
role: SRE / AWS Incident Response
origin: scoutflo
extract_date: 2026-03-05
tags:
- capacity
- cloudwatch
- database
- dynamodb
- errors
- incident-response
- k8s-service
- lambda
- performance
- sts
- throttling
---

# DynamoDB Throttling Errors - DynamoDB 스로틀링 오류

## 의미

DynamoDB 스로틀링 오류(ProvisionedThroughputExceededException)는 프로비저닝된 읽기 또는 쓰기 용량이 초과되거나, 핫 파티션으로 인해 용량이 불균등하게 분배되거나, 버스트 용량이 소진되거나, 온디맨드 모드에서 계정 수준 제한에 도달하거나, 갑작스러운 트래픽 급증이 용량을 초과하거나, DynamoDB 테이블 용량 설정이 부족할 때 발생합니다. DynamoDB 요청이 스로틀링 예외를 반환하고, 애플리케이션 요청이 실패하며, CloudWatch 지표에 스로틀링 이벤트가 표시됩니다. 이는 데이터베이스 계층에 영향을 미치며 데이터 접근을 차단합니다. 일반적으로 용량 계획 문제, 핫 파티션 문제 또는 트래픽 패턴 변경이 원인이며, Lambda나 애플리케이션 서비스와 함께 DynamoDB를 사용하는 경우 스로틀링 오류가 상위 서비스로 전파되어 데이터 접근 실패가 발생할 수 있습니다.

## 영향

DynamoDB 요청이 스로틀링됩니다. ProvisionedThroughputExceededException 오류가 발생합니다. 애플리케이션 요청이 실패합니다. 읽기 및 쓰기 작업이 거부됩니다. 사용자 대면 오류가 증가합니다. 애플리케이션 성능이 저하됩니다. 데이터베이스 작업을 완료할 수 없습니다. 서비스 가용성에 영향을 미칩니다. DynamoDB 스로틀링 오류가 애플리케이션 로그에 나타나며, Lambda나 애플리케이션 서비스와 함께 DynamoDB를 사용하는 경우 상위 서비스에서 오류나 성능 저하가 발생할 수 있습니다. 데이터 접근 작업이 실패하고, DynamoDB에 의존하는 사용자 대면 기능을 사용할 수 없게 됩니다.

## 플레이북

1. DynamoDB 테이블 `<table-name>`이 존재하고 "ACTIVE" 상태인지, 리전 `<region>`의 DynamoDB AWS 서비스 상태가 정상인지 확인합니다.
2. DynamoDB 테이블 `<table-name>`의 CloudWatch 지표(ReadThrottledEvents, WriteThrottledEvents, ConsumedReadCapacityUnits, ConsumedWriteCapacityUnits)를 최근 1시간 동안 조회하여 스로틀링 패턴을 파악하고, 스로틀링 빈도와 용량 소비를 분석합니다.
3. 리전 `<region>`의 DynamoDB 테이블 `<table-name>`을 조회하여 프로비저닝된 읽기/쓰기 용량 설정, 온디맨드 모드 구성, 테이블 상태, 용량 모드(프로비저닝 vs 온디맨드)를 점검합니다.
4. 애플리케이션 로그가 포함된 CloudWatch Logs 로그 그룹에서 테이블 `<table-name>` 관련 ProvisionedThroughputExceededException 오류 패턴을 필터링하여 스로틀링 예외 타임스탬프를 확인합니다.
5. DynamoDB 테이블 `<table-name>`과 연관된 ReadThrottledEvents 또는 WriteThrottledEvents 지표의 CloudWatch 경보를 조회하고 ALARM 상태인 경보를 확인하며, 경보 임계값 구성을 검증합니다.
6. DynamoDB 테이블 `<table-name>`의 CloudWatch 지표(UserErrors, SystemErrors)를 조회하여 스로틀링과 관련된 오류 패턴을 파악하고, 스로틀링 이벤트와의 오류 상관관계를 분석합니다.
7. DynamoDB 테이블 `<table-name>`의 파티션 키 구성을 조회하고 용량 소비 패턴을 분석하여 핫 파티션이나 불균등 분배를 식별하며, 파티션 키 설계를 점검합니다.
8. DynamoDB 테이블 `<table-name>`의 파티션 키별 ConsumedReadCapacityUnits 및 ConsumedWriteCapacityUnits CloudWatch 지표를 조회하여 핫 파티션 패턴을 식별하고, 파티션별 용량 소비를 분석합니다.
9. CloudTrail 이벤트가 포함된 CloudWatch Logs 로그 그룹에서 최근 24시간 이내 테이블 `<table-name>` 관련 DynamoDB 테이블 용량 변경 이벤트를 필터링하여 용량 변경 사항을 확인합니다.

## 진단

1. CloudWatch 경보 이력(플레이북 5단계)을 분석하여 ReadThrottledEvents 또는 WriteThrottledEvents 경보가 처음 트리거된 시점을 파악합니다. 이 타임스탬프가 스로틀링과 용량 또는 트래픽 패턴의 상관관계를 파악하는 기준선이 됩니다.

2. CloudWatch 지표(플레이북 2단계)에서 경보 시점 전후로 ConsumedReadCapacityUnits 또는 ConsumedWriteCapacityUnits가 프로비저닝된 용량을 초과한 경우, 단순 용량 소진이 근본 원인입니다.

3. 소비 용량 지표가 불균등한 분배를 보이면 파티션별 용량 소비(플레이북 8단계)를 확인합니다. 특정 파티션이 비정상적으로 높은 소비를 보이면 파티션 키 설계로 인한 핫 파티션 문제가 국소적 스로틀링을 유발하고 있는 것입니다.

4. 테이블 구성(플레이북 3단계)이 온디맨드 모드인데도 스로틀링이 발생하면 계정 수준 처리량 제한에 도달했을 수 있습니다. 프로비저닝 모드에서 CloudTrail(플레이북 9단계)에 최근 용량 감소가 표시되면 해당 감소가 스로틀링의 원인입니다.

5. 애플리케이션 로그(플레이북 4단계)에서 ProvisionedThroughputExceededException이 특정 작업이나 시간대와 상관관계를 보이면 요청 패턴을 분석합니다. 버스트 용량 할당을 초과하는 갑작스러운 트래픽 급증이 원인일 가능성이 높습니다.

6. UserErrors 및 SystemErrors 지표(플레이북 6단계)가 스로틀링 이벤트와 상관관계를 보이면 스로틀링의 하위 영향이 애플리케이션 수준 오류로 전파되고 있는 것입니다.

7. 스로틀링이 지속적이지 않고 간헐적인 경우(플레이북 2단계 추세 분석), 피크 시간대에 버스트 용량이 소진되고 있는 것입니다. 온디맨드 모드 또는 용량 Auto Scaling을 고려하세요.

상관관계를 찾을 수 없는 경우: 분석 기간을 24시간으로 확장하고, 핫 키 패턴에 대한 파티션 키 분배를 검토하고, DynamoDB Global Tables 복제 용량 오버헤드를 확인하고, DynamoDB Streams 용량 소비를 검증하고, 버스트 용량 활용 패턴을 점검합니다.
