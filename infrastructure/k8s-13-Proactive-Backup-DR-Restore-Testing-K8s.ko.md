---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/13-Proactive/03-Backup-DR/Restore-Testing-K8s.md)'
role: SRE / K8s Proactive Operations
origin: scoutflo
tags:
- backup
- infrastructure
- k8s-namespace
- k8s-service
- restore
- storage
- testing
---

# Restore Testing (복원 테스트)

## 의미

복원 테스트 알림은 백업 복원 절차를 검증할 수 없거나 테스트 중 복원 작업이 실패하는 상황(RestoreJobFailed 또는 RestoreTestFailed 같은 알림 발생)을 나타냅니다. 복원 Job 실패, 복원 시간이 RTO 목표 초과, 복원된 데이터 무결성 확인 불가, 복원 작업 타임아웃, 또는 복원 Job 메타데이터의 불완전한 복원 표시 등이 원인입니다. 복원 Job이 클러스터 복원 도구에서 실패 상태를 보이고, 복원 작업이 무기한 실행 상태에 머물며, 복원 완료 타임스탬프가 누락되고, 복원된 데이터 검증 검사가 실패합니다.
 이는 스토리지 계층과 재해 복구 절차에 영향을 미치며, 주로 복원 서비스 문제, 데이터 손상, 복원 타임아웃 문제, 또는 복원 Job 실패가 원인입니다. 복원이 컨테이너 워크로드를 보호하는 경우, 컨테이너 데이터 복구가 실패하고 애플리케이션이 데이터 손실을 겪을 수 있습니다.

## 영향

RestoreTestFailed 알림 발생, RestoreJobFailed 알림 발생, 재해 복구 절차 검증 불가, RTO 목표 미충족, 복원 Job 실패, 복원된 데이터 무결성 확인 불가, 복원 작업 타임아웃, 복원 완료 확인 불가. 복원 Job이 실행 또는 실패 상태로 유지되고, 복원 메타데이터가 불완전하거나 손상된 복원을 보입니다. 복원이 컨테이너 워크로드를 보호하는 경우, 컨테이너 데이터 복구가 실패하고, 영구 볼륨 데이터가 손상되며, 컨테이너 애플리케이션이 데이터 손실을 겪을 수 있습니다. 애플리케이션이 데이터 손실이나 복구 실패를 경험할 수 있습니다.

## 플레이북

1. namespace <namespace>에서 label app=restore인 Job을 조회하여 복원 테스트 검증을 위한 복원 Job과 현재 상태를 확인합니다.
2. namespace <namespace>에서 최근 이벤트를 타임스탬프 순으로 조회하여 복원 작업, 실패, 데이터 무결성 문제 관련 이벤트를 확인합니다.
3. namespace <namespace>에서 Job <restore-job-name>을 describe하여 복원 Job 세부 정보(상태, 완료 타임스탬프, 오류 메시지)를 점검합니다.
4. namespace <namespace>에서 Pod <restore-pod-name>의 로그를 조회하고 최근 24시간 내 'restore failed', 'restore timeout', 'data integrity failed' 등의 오류 패턴을 필터링합니다.
5. 복원 서비스의 Prometheus 메트릭(restore_job_success_rate, restore_job_duration)을 최근 24시간 동안 조회하여 복원 Job 실패 패턴을 확인합니다.
6. 복구 포인트 <recovery-point-name>의 세부 정보를 조회하고 생성 타임스탬프, 백업 완료 상태, 데이터 무결성 체크섬을 점검하여 복구 포인트 유효성을 확인합니다.
7. 복원 Job 완료 타임스탬프와 RTO 목표를 비교하여 복원 작업이 예상 시간 내에 완료되는지 확인하고, 복원 Job 메타데이터를 보조 증거로 활용합니다.
8. 복원 완료 후 복원된 리소스 <resource-name>의 설정을 조회하고 리소스 상태가 예상 복원 상태와 일치하는지 확인하여 복원된 리소스 무결성을 점검합니다.

## 진단

1. 1단계와 3단계의 복원 Job 상태를 검토합니다. Job이 실패 상태이면 오류 메시지를 분석하여 실패 원인(복구 포인트 문제, 스토리지 제약, 권한, 타임아웃)을 파악합니다.

2. 4단계의 복원 Pod 로그를 분석합니다. 로그에 타임아웃 패턴이 있으면 복원 작업이 너무 오래 걸리고 있습니다. 로그에 데이터 무결성 실패가 있으면 복구 포인트가 손상되었을 수 있습니다.

3. 5단계의 복원 메트릭에서 성공률이 낮으면 체계적인 복원 문제가 존재합니다. 성공률은 높지만 특정 복원 테스트가 실패하면 해당 테스트의 설정 문제입니다.

4. 6단계의 복구 포인트 세부 정보를 검토합니다. 복구 포인트에 생성 문제나 유효하지 않은 체크섬이 있으면 복원 절차가 아닌 소스 백업이 문제입니다.

5. 7단계에서 복원 완료가 RTO 목표를 초과하면 복원이 최종적으로 성공하더라도 복원 성능 최적화가 필요합니다. 완료가 RTO 내이면 복원 절차가 목표를 충족합니다.

분석이 결론에 이르지 못하면: 2단계의 이벤트에서 복원 관련 실패를 확인합니다. 8단계의 복원된 리소스 무결성을 검토하여 복원이 유효한 리소스를 생성하는지 확인합니다. 실패가 모든 복원 테스트에 영향을 미치는지(인프라 문제 시사) 또는 특정 복구 포인트에만 영향을 미치는지(포인트별 손상 시사) 판단합니다.
