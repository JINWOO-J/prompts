---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/13-Proactive/03-Backup-DR/Backup-Verification-K8s.md)'
role: SRE / K8s Proactive Operations
origin: scoutflo
tags:
- backup
- infrastructure
- k8s-namespace
- k8s-service
- storage
- verification
---

# Backup Verification (백업 검증)

## 의미

백업 검증 알림은 etcd 백업 또는 클러스터 상태 백업이 성공적으로 완료되지 않거나 백업 무결성을 확인할 수 없는 상황(KubeBackupFailed 또는 BackupVerificationFailed 같은 알림 발생)을 나타냅니다. 백업 Job 실패, 백업 보존 정책 미충족, 백업 암호화 검증 실패, 백업 완료 상태 확인 불가, 또는 백업 메타데이터의 불완전한 백업 표시 등이 원인입니다. 백업이 클러스터 백업 도구에서 실패 상태를 보이고, 백업 Job이 무기한 실행 상태에 머물며, 백업 완료 타임스탬프가 누락되거나 오래되었고, 백업 검증 검사가 실패합니다. 이는 스토리지 계층과 백업 인프라에 영향을 미치며, 주로 백업 서비스 문제, 보존 정책 위반, 암호화 키 문제, 또는 백업 Job 실패가 원인입니다. 백업이 컨테이너 워크로드를 보호하는 경우, 컨테이너 데이터 복구가 불가능해지고 애플리케이션이 데이터 손실 위험을 겪을 수 있습니다.

## 영향

KubeBackupFailed 알림 발생, BackupVerificationFailed 알림 발생, 데이터 복구 불가능, RTO 및 RPO 목표 미충족, 백업 Job 실패, 백업 보존 정책 위반, 백업 암호화 검증 실패, 백업 완료 확인 불가, 재해 복구 절차 실행 불가.
 백업 Job이 실행 또는 실패 상태로 유지되고, 백업 메타데이터가 불완전하거나 손상된 백업을 보입니다. 백업이 컨테이너 워크로드를 보호하는 경우, 컨테이너 데이터 복구가 실패하고, 영구 볼륨 데이터가 손실되며, 컨테이너 애플리케이션이 데이터 손실 위험을 겪을 수 있습니다. 애플리케이션이 데이터 손실이나 복구 실패를 경험할 수 있습니다.

## 플레이북

1. namespace <namespace>에서 label app=etcd-backup인 Job을 조회하여 모든 백업 Job과 완료 상태를 확인합니다.

2. namespace <namespace>에서 최근 이벤트를 타임스탬프 순으로 조회하여 최근 백업 실패나 문제를 확인합니다.

3. namespace <namespace>에서 Job <backup-job-name>을 describe하여 상태, 완료 타임스탬프, 오류 메시지를 점검합니다.

4. namespace <namespace>에서 백업 Pod <backup-pod-name>의 로그를 조회하고 'backup failed', 'verification failed', 'retention policy violation' 등의 오류 패턴을 필터링합니다.

5. 백업 서비스의 Prometheus 메트릭(backup_job_success_rate, backup_job_duration)을 최근 24시간 동안 조회하여 백업 Job 실패 패턴을 확인합니다.

6. namespace <namespace>에서 볼륨 스냅샷을 조회하고 복구 포인트 생성 타임스탬프가 백업 스케줄과 일치하는지 확인합니다.

7. namespace <namespace>에서 Secret <backup-secret-name>을 YAML 출력으로 조회하여 암호화 키 접근성을 확인합니다.

8. 백업 Job 완료 타임스탬프와 백업 스케줄 타임스탬프를 비교하여 백업 Job이 예상 시간 내에 완료되는지 확인하고, 백업 Job 메타데이터를 보조 증거로 활용합니다.

## 진단

1. 1단계와 3단계의 백업 Job 상태를 검토합니다. Job이 실패 상태이거나 불완전한 완료를 보이면 오류 메시지를 분석하여 실패 원인(권한, 스토리지, 암호화, 리소스 제약)을 파악합니다.

2. 4단계의 백업 Pod 로그를 분석합니다. 로그에 암호화 또는 검증 실패 패턴이 있으면 7단계의 암호화 키 접근성을 조사해야 합니다. 로그에 보존 정책 위반이 있으면 백업 정리 자동화가 실패하고 있습니다.

3. 5단계의 백업 메트릭에서 24시간 동안 성공률이 낮으면 체계적인 백업 문제가 존재합니다. 성공률은 높지만 특정 Job이 실패하면 해당 Job의 설정 문제입니다.

4. 6단계의 볼륨 스냅샷 타임스탬프를 검토합니다. 복구 포인트가 백업 스케줄 대비 누락되거나 오래되었으면 백업 완료가 실패하거나 스냅샷이 생성되지 않고 있습니다.

5. 8단계의 백업 Job 완료 분석에서 Job이 예상 시간 내에 완료되지 않으면 백업 성능 문제나 리소스 제약이 타임아웃을 유발할 수 있습니다.

분석이 결론에 이르지 못하면: 2단계의 이벤트에서 백업 관련 실패를 확인합니다. 실패가 모든 백업 Job에 영향을 미치는지(인프라 문제 시사) 또는 특정 Job에만 영향을 미치는지(Job별 설정 문제 시사) 판단합니다. 백업 스토리지 용량과 백업 Job 서비스 어카운트 권한을 확인합니다.
