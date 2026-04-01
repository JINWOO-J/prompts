---
category: incident-response
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/AWS%20Playbooks/02-Database/Automatic-Backup-Not-Working-RDS.md)'
role: SRE / AWS Incident Response
origin: scoutflo
extract_date: 2026-03-05
tags:
- automatic
- backup
- cloudwatch
- compliance
- database
- iam
- incident-response
- k8s-service
- rds
- storage
- sts
- working
---

# RDS Automatic Backup Not Working - RDS 자동 백업 미작동

## 의미

RDS 자동 백업이 실패하거나 생성되지 않는 현상(BackupFailure 또는 RDSBackupFailure와 같은 경보 트리거)은 백업 보존 기간이 0으로 설정되었거나, 백업 윈도우가 유지보수 윈도우와 충돌하거나, IAM 권한이 백업 작업에 불충분하거나, 스토리지가 가득 차서 백업 생성이 불가능하거나, 백업 서비스에 오류가 발생하거나, RDS 인스턴스 백업 구성이 비활성화되었을 때 발생합니다. 데이터베이스 백업이 생성되지 않고, 데이터 보호가 손상되며, 특정 시점 복구를 사용할 수 없습니다. 이는 데이터베이스 계층에 영향을 미치며 데이터 보호를 손상시킵니다. 일반적으로 구성 문제, 스토리지 문제 또는 권한 실패가 원인이며, RDS Aurora를 사용하는 경우 백업 동작이 다르고 애플리케이션이 백업 데이터 보호 누락의 영향을 받을 수 있습니다.

## 영향

데이터베이스 백업이 생성되지 않습니다. 데이터 보호가 손상됩니다. 특정 시점 복구를 사용할 수 없습니다. 백업 보존 정책이 실패합니다.
 BackupFailure 경보가 발생합니다. 재해 복구 기능이 상실됩니다. 자동 백업 일정이 실행되지 않습니다. 데이터 손실 위험이 증가합니다. RDSBackupFailure 경보가 발생할 수 있으며, RDS Aurora를 사용하는 경우 백업 구성이 표준 RDS와 다릅니다. 백업 보호 누락으로 애플리케이션이 영향을 받을 수 있으며, 백업 누락으로 인해 컴플라이언스 요구사항을 위반할 수 있습니다.

## 플레이북

1. RDS 인스턴스 `<db-instance-id>`가 존재하고 "available" 상태인지, 리전 `<region>`의 RDS AWS 서비스 상태가 정상인지 확인합니다.
2. 리전 `<region>`의 RDS 인스턴스 `<db-instance-id>`를 조회하여 백업 보존 기간, 자동 백업 설정, 백업 윈도우 구성, 최신 백업 상태를 점검하고, 백업 구성이 활성화되어 있는지 검증합니다.
3. RDS 이벤트가 포함된 CloudWatch Logs 로그 그룹에서 인스턴스 `<db-instance-id>` 관련 백업 실패 이벤트나 오류 패턴을 필터링하여 백업 오류 메시지를 확인합니다.
4. RDS 인스턴스 `<db-instance-id>`의 CloudWatch 지표(FreeStorageSpace)를 최근 24시간 동안 조회하여 백업을 위한 스토리지 가용성을 확인하고, 스토리지 추세를 분석합니다.
5. RDS 인스턴스 `<db-instance-id>`와 연관된 BackupFailure 지표의 CloudWatch 경보를 조회하고 ALARM 상태인 경보를 확인하며, 경보 구성을 검증합니다.
6. RDS 인스턴스 `<db-instance-id>`의 유지보수 윈도우 구성을 조회하여 백업 윈도우가 유지보수 윈도우와 충돌하지 않는지 확인하고, 윈도우 스케줄링을 점검합니다.
7. RDS 인스턴스 `<db-instance-id>`의 IAM 역할 구성을 조회하여 백업 작업에 대한 IAM 권한을 검증하고, 서비스 연결 역할 권한을 점검합니다.
8. 인스턴스 `<db-instance-id>`의 RDS 백업 이벤트를 나열하고 백업 생성 타임스탬프, 백업 상태, 실패 사유를 확인하여 백업 이력을 분석합니다.
9. CloudTrail 이벤트가 포함된 CloudWatch Logs 로그 그룹에서 최근 7일 이내 인스턴스 `<db-instance-id>` 관련 RDS 백업 구성 변경 이벤트를 필터링하여 구성 변경 사항을 확인합니다.

## 진단

1. CloudWatch 경보 이력(플레이북 5단계)을 분석하여 BackupFailure 경보가 처음 트리거된 시점을 파악합니다. RDS 백업 이벤트(플레이북 8단계)와 교차 참조하여 백업이 완료되지 않기 시작한 정확한 타임스탬프를 확립합니다.

2. 인스턴스 구성(플레이북 2단계)에서 백업 보존 기간이 0이면 자동 백업이 비활성화된 것입니다. 이것이 근본 원인이며, 자동 백업을 활성화하려면 보존 기간을 1~35일로 설정해야 합니다.

3. 보존 기간이 구성되어 있지만 백업이 실패하면 FreeStorageSpace 지표(플레이북 4단계)를 확인합니다. 백업 타임스탬프 전후로 스토리지가 심각하게 부족하면 스토리지 부족으로 백업 생성이 불가능했던 것입니다.

4. 스토리지가 충분하면 백업 윈도우와 유지보수 윈도우(플레이북 6단계)를 비교합니다. 윈도우가 겹치면 유지보수 작업이 백업 완료를 방해하는 충돌이 발생할 수 있습니다.

5. CloudTrail 이벤트(플레이북 9단계)에서 실패 타임스탬프 전후로 백업 구성 변경이 표시되면 해당 변경이 의도치 않게 백업 설정을 비활성화하거나 잘못 구성했을 수 있습니다.

6. 백업 이벤트 로그(플레이북 3단계 및 8단계)에서 권한 오류가 표시되면 IAM 서비스 연결 역할 권한(플레이북 7단계)을 검증합니다. 누락되거나 변경된 권한은 RDS가 스냅샷을 생성하는 것을 방해합니다.

7. 백업 실패가 지속적이지 않고 간헐적인 경우(백업 이력 분석), 일시적인 서비스 문제이거나 백업 윈도우 동안의 주기적인 스토리지 압박일 수 있습니다.

상관관계를 찾을 수 없는 경우: 분석 기간을 14일로 확장하고, 상세 오류 메시지를 위한 RDS 이벤트 구독을 검토하고, 해당되는 경우 Aurora 전용 백업 구성을 확인하고, 교차 리전 스냅샷 복사 권한을 검증하고, Multi-AZ 백업 복제 상태를 점검합니다.