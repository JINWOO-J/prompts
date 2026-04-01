---
category: incident-response
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/AWS%20Playbooks/03-Storage/Intelligent-Tiering-Not-Moving-Data-as-Expected-S3.md)'
role: SRE / AWS Incident Response
origin: scoutflo
extract_date: 2026-03-05
tags:
- cloudwatch
- cost
- data
- expected
- incident-response
- intelligent
- k8s-service
- monitoring
- moving
- s3
- storage
- sts
- tiering
---

# S3 Intelligent-Tiering Not Moving Data as Expected - S3 Intelligent-Tiering 데이터 이동 예상과 다름

## 의미

S3 Intelligent-Tiering이 예상대로 데이터를 이동하지 않는 현상(스토리지 최적화 실패 또는 S3IntelligentTieringNotWorking 경보 트리거)은 Intelligent-Tiering이 활성화되지 않았거나, 데이터 접근 패턴이 티어 전환을 트리거하지 않거나, 티어 전환 규칙이 잘못 구성되었거나, 데이터 접근 빈도 임계값이 충족되지 않거나, Intelligent-Tiering 서비스가 티어 분석 중 오류를 만나거나, Intelligent-Tiering 모니터링 기간이 완료되지 않았을 때 발생합니다.
 S3 Intelligent-Tiering 티어 전환이 발생하지 않고, 스토리지 비용 최적화가 실패하며, 데이터가 비싼 티어에 남아 있습니다. 이는 스토리지 및 비용 최적화 계층에 영향을 미치며 스토리지 비용을 증가시킵니다. 일반적으로 Intelligent-Tiering 구성 문제, 접근 패턴 문제 또는 모니터링 기간 제약이 원인이며, 다른 접근 티어와 함께 S3 Intelligent-Tiering을 사용하는 경우 전환 동작이 다를 수 있고 애플리케이션에서 최적이 아닌 스토리지 비용이 발생할 수 있습니다.

## 영향

S3 Intelligent-Tiering 티어 전환이 발생하지 않습니다. 스토리지 비용 최적화가 실패합니다. 데이터가 비싼 티어에 남아 있습니다. 티어 전환 자동화가 효과가 없습니다. 스토리지 비용이 예상보다 높습니다. Intelligent-Tiering 이점이 실현되지 않습니다. 비용 관리 목표가 충족되지 않습니다. S3IntelligentTieringNotWorking 경보가 발생할 수 있으며, 다른 접근 티어와 함께 S3 Intelligent-Tiering을 사용하는 경우 전환 동작이 다를 수 있습니다. 애플리케이션에서 더 높은 스토리지 비용이 발생할 수 있으며, 비용 최적화 이점이 실현되지 않을 수 있습니다.

## 플레이북

1. S3 버킷 `<bucket-name>`이 존재하고 리전 `<region>`의 S3 AWS 서비스 상태가 정상인지 확인합니다.
2. 리전 `<region>`의 S3 버킷 `<bucket-name>`을 조회하여 Intelligent-Tiering 구성, 티어 전환 설정, Intelligent-Tiering 상태를 점검하고, Intelligent-Tiering이 활성화되어 있는지 검증합니다.
3. S3 서버 접근 로그가 포함된 CloudWatch Logs 로그 그룹에서 버킷 `<bucket-name>` 관련 객체 접근 패턴, 접근 빈도, 티어 전환 이벤트를 필터링하여 접근 패턴 세부 정보를 확인합니다.
4. S3 버킷 `<bucket-name>`의 CloudWatch 지표(스토리지 클래스별 BucketSizeBytes)를 최근 30일 동안 조회하여 티어 분포 패턴을 파악하고, 티어 분포를 분석합니다.
5. 버킷 `<bucket-name>`에서 Intelligent-Tiering이 활성화된 S3 객체를 나열하고 객체 접근 타임스탬프, 티어 할당, 티어 전환 적격성을 확인하여 객체 티어 상태를 분석합니다.
6. CloudTrail 이벤트가 포함된 CloudWatch Logs 로그 그룹에서 버킷 `<bucket-name>` 관련 S3 Intelligent-Tiering 구성 또는 티어 전환 이벤트를 필터링하여 구성 변경 사항을 확인합니다.
7. S3 버킷 `<bucket-name>`의 Intelligent-Tiering 모니터링 구성을 조회하여 모니터링 기간 설정을 확인하고, 모니터링 기간이 티어 전환에 영향을 미치는지 점검합니다.
8. S3 Intelligent-Tiering의 CloudWatch 지표(가용한 경우 TierTransitionCount)를 조회하여 티어 전환 활동을 확인하고, 전환이 발생하고 있는지 점검합니다.
9. CloudTrail 이벤트가 포함된 CloudWatch Logs 로그 그룹에서 최근 30일 이내 버킷 `<bucket-name>` 관련 S3 객체 접근 패턴 변경 또는 Intelligent-Tiering 구성 변경 이벤트를 필터링하여 접근 또는 구성 변경 사항을 확인합니다.

## 진단

1. **4단계의 CloudWatch 지표 및 스토리지 클래스 분포 분석**: S3 스토리지 지표에서 티어 분포 패턴을 검토합니다. CloudWatch 지표에서 BucketSizeBytes가 Frequent Access 티어에 정적으로 유지되고 Infrequent Access 또는 Archive 티어로의 이동이 없으면 전환이 발생하지 않고 있는 것입니다. 30일간 지표를 비교합니다. Intelligent-Tiering은 Infrequent Access 티어로 전환하기 전에 접근 없이 연속 30일이 필요합니다. 모니터링 기간 내에 객체가 접근되고 있으면 2단계로 진행합니다.

2. **3단계의 S3 접근 로그 검토**: 서버 접근 로그에서 객체가 정기적으로 접근(GET 요청)되고 있으면 접근 패턴이 전환 타이머를 재설정하고 있는 것입니다. 객체는 Infrequent Access로 이동하려면 30일, Archive Instant Access는 90일, Deep Archive는 180일 동안 접근되지 않아야 합니다. 접근 패턴이 임계값을 충족하지만 전환이 여전히 발생하지 않으면 3단계로 진행합니다.

3. **2단계의 Intelligent-Tiering 구성 확인**: Intelligent-Tiering 구성이 버킷이나 특정 객체에 활성화되어 있지 않으면 데이터가 티어 전환 대상이 아닙니다. 객체에 INTELLIGENT_TIERING 스토리지 클래스가 있는지 확인합니다. STANDARD 또는 다른 스토리지 클래스의 객체는 자동으로 전환되지 않습니다. Archive 전환을 기대하는 경우 7단계에서 아카이브 접근 티어 구성이 활성화되어 있는지 확인합니다. 구성이 올바르면 4단계로 진행합니다.

4. **5단계의 객체 티어 상태 확인**: 객체 메타데이터에서 객체가 INTELLIGENT_TIERING에 있지만 티어 전환이 예상대로 발생하지 않으면 객체 업로드 날짜를 확인합니다. 객체는 Intelligent-Tiering 활성화 날짜가 아닌 업로드 날짜부터 모니터링 기간을 완료해야 합니다. 객체가 최근에 INTELLIGENT_TIERING 스토리지 클래스로 전환되었다면 전체 모니터링 기간을 완료해야 합니다.

5. **9단계의 구성 변경과 상관 분석**: CloudTrail 이벤트에서 모니터링 기간 내에 Intelligent-Tiering 구성 변경이나 접근 패턴 변경이 표시되면 최근 변경이 전환 타이머를 재설정하거나 적격성을 변경했을 수 있습니다.

**상관관계를 찾을 수 없는 경우**: 5단계의 객체 메타데이터를 사용하여 분석을 180일로 확장합니다. 7단계의 Intelligent-Tiering 구성에서 Archive Instant Access 및 Deep Archive Access 티어가 활성화되어 있는지 확인합니다. Intelligent-Tiering은 설계상 최소 30일 대기 기간이 있습니다. 더 빠른 전환을 기대하는 경우 수명 주기 정책을 대신 고려하세요. 객체 크기를 확인합니다. 128KB보다 작은 객체는 접근 티어 간에 전환되지 않습니다.