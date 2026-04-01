---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/13-Proactive/03-Backup-DR/Cross-cluster-Backup-Sync-K8s.md)'
role: SRE / K8s Proactive Operations
origin: scoutflo
tags:
- backup
- cluster
- cross
- infrastructure
- k8s-namespace
- k8s-rbac
- k8s-service
- storage
- sync
---

# Cross-cluster Backup Sync (크로스 클러스터 백업 동기화)

## 의미

크로스 클러스터 백업 동기화 알림은 클러스터 간 백업 동기화가 완료되지 않거나 백업 동기화 작업이 실패하는 상황(BackupSyncFailed 또는 CrossClusterBackupSyncFailed 같은 알림 발생)을 나타냅니다. 백업 동기화 Job 실패, 백업 동기화 지연이 임계값 초과, 백업 동기화 상태 오류, 크로스 클러스터 백업 복제 비동기화, 또는 백업 동기화 헬스 체크 실패 등이 원인입니다. 백업 동기화 Job이 실패 상태를 보이고, 백업 동기화 지연 메트릭이 임계값을 초과하며, 백업 동기화 상태가 오류를 나타내고, 크로스 클러스터 백업 복제가 동기화 실패를 보입니다.
 이는 스토리지 계층과 백업 인프라에 영향을 미치며, 주로 백업 동기화 서비스 문제, 크로스 클러스터 네트워크 연결 문제, 백업 동기화 Job 실패, 또는 백업 동기화 설정 오류가 원인입니다. 백업 동기화가 컨테이너 워크로드를 보호하는 경우, 컨테이너 백업 데이터가 비동기화되고 애플리케이션이 백업 가용성 문제를 겪을 수 있습니다.

## 영향

CrossClusterBackupSyncFailed 알림 발생, BackupSyncFailed 알림 발생, 크로스 클러스터 백업 동기화 실패, 백업 동기화 Job 실패, 백업 동기화 지연이 허용 임계값 초과, 재해 복구 절차가 크로스 클러스터 백업에 의존 불가. 백업 동기화 Job이 실패 또는 대기 상태로 유지되고, 백업 동기화 지연 메트릭이 증가하는 지연을 보입니다. 백업 동기화가 컨테이너 워크로드를 보호하는 경우, 컨테이너 백업 데이터가 비동기화되고, 영구 볼륨 백업이 보조 클러스터에서 사용 불가하며, 컨테이너 애플리케이션이 백업 가용성 문제를 겪을 수 있습니다. 애플리케이션이 백업 미가용 또는 크로스 클러스터 백업 동기화 실패를 경험할 수 있습니다.

## 플레이북

1. namespace <namespace>에서 label app=backup-sync인 Job을 조회하여 모든 크로스 클러스터 백업 동기화 Job과 현재 상태를 확인합니다.

2. namespace <namespace>에서 최근 이벤트를 타임스탬프 순으로 조회하여 최근 백업 복사 실패나 동기화 문제를 확인합니다.

3. namespace <namespace>에서 Job <copy-job-name>을 describe하여 상태, 완료 타임스탬프, 오류 메시지를 점검합니다.

4. namespace <namespace>에서 label app=backup-sync인 백업 동기화 Pod의 로그를 조회하고 'copy failed', 'sync failed', 'replication error' 등의 오류 패턴을 필터링합니다.

5. 백업 서비스의 Prometheus 메트릭(backup_copy_job_success_rate, backup_copy_job_duration)을 최근 24시간 동안 조회하여 백업 복사 Job 실패 패턴을 확인합니다.

6. 소스 클러스터의 백업 복사 Job 완료 타임스탬프와 백업 생성 타임스탬프를 비교하여 백업 복사가 예상 시간 내에 완료되는지 확인하고, 백업 복사 Job 메타데이터를 보조 증거로 활용합니다.

7. namespace <namespace>에서 ConfigMap <backup-vault-configmap-name>을 YAML 출력으로 조회하고 복제 규칙 설정을 확인합니다.

8. namespace <namespace>에서 볼륨 스냅샷을 조회하고 복구 포인트 생성 타임스탬프가 소스 클러스터 백업 타임스탬프와 일치하는지 확인합니다.

## 진단

1. 1단계와 3단계의 백업 동기화 Job 상태를 검토합니다. Job이 실패 상태이면 오류 메시지를 분석하여 실패 원인(네트워크 연결, 권한, 스토리지 용량, 소스 백업 문제)을 파악합니다.

2. 4단계의 백업 동기화 Pod 로그를 분석합니다. 로그에 복사 실패나 복제 오류 패턴이 있으면 실패가 네트워크 문제(연결 문제 시사)인지 데이터 문제(소스 백업 문제 시사)인지 확인합니다.

3. 5단계의 백업 메트릭에서 성공률이 낮으면 체계적인 동기화 문제가 존재합니다. 성공률은 높지만 특정 Job이 실패하면 해당 Job의 설정 문제입니다.

4. 6단계의 백업 완료 비교를 검토합니다. 소스 백업 생성 후 예상 시간 내에 백업 복사가 완료되지 않으면 동기화 성능 또는 용량 문제가 존재합니다.

5. 8단계의 복구 포인트 타임스탬프가 소스 클러스터 백업과 일치하지 않으면 동기화 지연이 존재하며 재해 복구 준비 상태가 위험합니다.

분석이 결론에 이르지 못하면: 2단계의 이벤트에서 백업 복사 실패나 동기화 문제를 확인합니다. 7단계의 복제 규칙 설정을 검토하여 설정이 올바른지 확인합니다. 동기화 실패가 모든 백업에 영향을 미치는지(인프라 문제 시사) 또는 특정 백업 유형에만 영향을 미치는지(해당 백업 유형의 설정 문제 시사) 판단합니다.
