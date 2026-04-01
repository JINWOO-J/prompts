---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/13-Proactive/03-Backup-DR/Backup-Integrity-Verification-K8s.md)'
role: SRE / K8s Proactive Operations
origin: scoutflo
tags:
- backup
- infrastructure
- integrity
- k8s-namespace
- k8s-pod
- k8s-service
- monitoring
- sts
- verification
---

# Backup Integrity Verification (백업 무결성 검증)

## 의미

백업 무결성 검증 알림은 etcd 백업 데이터의 무결성을 확인할 수 없거나 백업 손상이 감지된 상황(BackupIntegrityFailed 또는 BackupCorruptionDetected 같은 알림 발생)을 나타냅니다. 백업 무결성 검사 실패, 백업 손상 감지, 백업 체크섬 검증 실패, 백업 복원 테스트 실패, 또는 백업 무결성 모니터링의 위반 감지 등이 원인입니다. 백업 무결성 검사가 실패를 보이고, 백업 손상이 감지되며, 백업 체크섬 검증이 실패하고, 백업 무결성 모니터링이 문제를 나타냅니다. 이는 데이터 무결성 계층과 백업 신뢰성에 영향을 미치며, 주로 백업 손상, 백업 서비스 문제, 체크섬 검증 실패, 또는 백업 무결성 모니터링 실패가 원인입니다. 백업 무결성이 컨테이너 워크로드에 영향을 미치는 경우, 컨테이너 백업 데이터가 손상되고 애플리케이션이 백업 복원 실패를 겪을 수 있습니다.

## 영향

BackupIntegrityFailed 알림 발생, BackupCorruptionDetected 알림 발생, 백업 무결성 확인 불가, 백업 손상 감지, 백업 복원 실패 가능, 재해 복구 절차 위험. 백업 무결성 검증이 실패를 보입니다. 백업 무결성이 컨테이너 워크로드에 영향을 미치는 경우, 컨테이너 백업 데이터가 손상되고, 영구 볼륨 백업이 유효하지 않으며, 컨테이너 애플리케이션이 백업 복원 실패를 겪을 수 있습니다. 애플리케이션이 데이터 손실이나 백업 복원 실패를 경험할 수 있습니다.

## 플레이북

1. namespace <namespace>에서 label app=backup인 Job을 조회하여 모든 백업 Job과 현재 상태를 확인합니다.

2. namespace <namespace>에서 최근 이벤트를 타임스탬프 순으로 조회하여 최근 백업 무결성 문제나 실패를 확인합니다.

3. namespace <namespace>에서 Job <backup-job-name>을 describe하여 Job 완료 상태, 오류 메시지, 무결성 검사 결과를 점검합니다.

4. namespace <namespace>에서 label app=backup인 백업 Pod의 로그를 조회하고 백업 무결성 오류나 손상 감지 패턴을 필터링합니다.

5. 백업 서비스의 Prometheus 메트릭(backup_job_success_rate, backup_integrity_check_results)을 최근 30일 동안 조회하여 백업 무결성 문제를 확인합니다.

6. namespace <namespace>에서 볼륨 스냅샷을 조회하여 스냅샷 데이터 무결성 상태와 완료 여부를 확인합니다.

7. 백업 무결성 검사 실패 타임스탬프와 백업 Job 완료 타임스탬프를 1시간 이내로 비교하여 무결성 실패가 백업 완료 후에 발생하는지 확인하고, 백업 무결성 검사 결과를 보조 증거로 활용합니다.

8. etcd 백업 무결성 검사 결과를 조회하고 백업 데이터 무결성 상태를 확인합니다.

## 진단

1. 1단계와 3단계의 백업 Job 상태를 검토합니다. Job이 실패 상태이거나 무결성 검사 실패를 보이면 오류 메시지를 분석하여 손상 원인(스토리지 문제, 네트워크 전송 오류, 서비스 실패)을 파악합니다.

2. 4단계의 백업 Pod 로그를 분석합니다. 로그에 무결성 오류나 손상 감지 패턴이 있으면 손상이 백업 생성 중에 발생했는지 또는 이후 저장 중에 발생했는지 확인합니다.

3. 5단계의 백업 메트릭에서 무결성 검사 실패가 있으면 실패가 증가하고 있는지(지속적인 손상 문제 시사) 또는 안정적인지(과거 이벤트 시사) 평가합니다.

4. 6단계의 볼륨 스냅샷 상태를 검토합니다. 스냅샷에 무결성 문제가 있으면 스냅샷 데이터가 손상된 것이며 대체 백업 소스에서 복구해야 합니다.

5. 7단계의 무결성 검사 비교에서 백업 완료 후에 실패가 발생하면 스토리지나 백업 후 프로세스가 손상을 유발하고 있습니다. 백업 중에 실패가 발생하면 백업 생성이 문제입니다.

분석이 결론에 이르지 못하면: 2단계의 이벤트에서 백업 관련 실패를 확인합니다. 8단계의 etcd 백업 무결성을 검토하여 클러스터 상태 백업 무결성을 확인합니다. 손상이 모든 백업에 영향을 미치는지(체계적 문제 시사) 또는 특정 백업에만 영향을 미치는지(대상 손상 또는 Job별 문제 시사) 판단합니다.
