---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/13-Proactive/03-Backup-DR/RTO-RPO-Validation-K8s.md)'
role: SRE / K8s Proactive Operations
origin: scoutflo
tags:
- backup
- compliance
- infrastructure
- k8s-namespace
- validation
---

# RTO/RPO Validation (RTO/RPO 검증)

## 의미

RTO/RPO 검증 알림은 Recovery Time Objective와 Recovery Point Objective 목표를 충족하거나 정확히 측정할 수 없는 상황(RTOExceeded 또는 RPOExceeded 같은 알림 발생)을 나타냅니다. 백업 빈도가 RPO 목표를 충족하지 못하거나, 복원 작업이 RTO 목표를 초과하거나, 백업 완료 시간이 추적되지 않거나, 복원 완료 시간이 측정되지 않거나, RTO/RPO 메트릭이 목표 위반을 나타내는 것이 원인입니다. 백업 완료 시간이 RPO 윈도우를 초과하고, 복원 작업이 RTO 목표를 초과하며, RTO/RPO 메트릭이 목표 위반을 보이고, 백업/복원 타임스탬프가 목표 미준수를 나타냅니다. 이는 재해 복구 계층과 백업 인프라에 영향을 미치며, 주로 백업 스케줄 불일치, 복원 작업 지연, 메트릭 추적 실패, 또는 RTO/RPO 목표 설정 오류가 원인입니다. RTO/RPO 검증이 컨테이너 워크로드를 보호하는 경우, 컨테이너 데이터 복구가 목표를 충족하지 못하고 애플리케이션이 복구 시간 연장을 겪을 수 있습니다.

## 영향

RTOExceeded 알림 발생, RPOExceeded 알림 발생, 재해 복구 목표 미충족, 백업 빈도가 RPO 목표 위반, 복원 작업이 RTO 목표 초과, 복구 절차 검증 불가. 백업 완료 시간이 RPO 윈도우를 초과하고, 복원 작업이 RTO 시간 제한을 초과합니다. RTO/RPO 검증이 컨테이너 워크로드를 보호하는 경우, 컨테이너 데이터 복구가 목표를 충족하지 못하고, 영구 볼륨 복구가 RTO를 초과하며, 컨테이너 애플리케이션이 복구 시간 연장을 겪을 수 있습니다. 애플리케이션이 허용 한도를 넘는 장시간 다운타임이나 데이터 손실을 경험할 수 있습니다.

## 플레이북

1. namespace <namespace>에서 label app=backup인 CronJob을 조회하여 RPO 검증을 위한 백업 스케줄 Job과 현재 설정을 확인합니다.

2. namespace <namespace>에서 최근 이벤트를 타임스탬프 순으로 조회하여 RTO/RPO 준수에 영향을 줄 수 있는 백업 또는 복원 작업 관련 이벤트를 확인합니다.

3. namespace <namespace>에서 CronJob <backup-cronjob-name>을 describe하여 백업 스케줄 설정, 빈도, 마지막 성공 실행 시간을 점검합니다.

4. namespace <namespace>에서 label app=backup인 Job을 완료 시간 순으로 조회하여 RPO 검증을 위한 백업 Job 완료 타임스탬프를 확인하고 실제 백업 빈도를 계산합니다.

5. namespace <namespace>에서 label app=restore인 Job을 완료 시간 순으로 조회하여 RTO 검증을 위한 복원 Job 완료 타임스탬프를 확인하고 실제 복원 소요 시간을 계산합니다.

6. 백업 서비스의 Prometheus 메트릭(backup_job_duration, restore_job_duration)을 최근 30일 동안 조회하여 RTO/RPO 준수 패턴을 확인합니다.

7. 백업 Job 완료 타임스탬프와 백업 스케줄 타임스탬프를 비교하여 백업 빈도가 RPO 목표를 충족하는지 확인하고, 백업 Job 메타데이터를 보조 증거로 활용합니다.

8. 복원 Job 완료 타임스탬프와 RTO 목표를 비교하여 복원 작업이 RTO 시간 제한 내에 완료되는지 확인하고, 복원 Job 메타데이터를 보조 증거로 활용합니다.

## 진단

1. 3단계의 백업 CronJob 설정과 4단계의 Job 완료 시간을 검토합니다. 백업 빈도가 RPO 요구사항과 맞지 않으면(예: RPO 1시간인데 백업이 4시간마다) 백업 스케줄 조정이 필요합니다.

2. 5단계의 복원 Job 소요 시간을 분석합니다. 복원 시간이 지속적으로 RTO 목표에 근접하거나 초과하면 복원 최적화가 필요합니다. 복원 시간에 충분한 여유가 있으면 RTO 준수가 유지되고 있습니다.

3. 6단계의 백업/복원 메트릭이 30일간 소요 시간 증가를 보이면 성능이 저하되고 있으며, 현재는 준수하더라도 결국 RTO/RPO 위반이 발생할 수 있습니다.

4. 7단계의 백업 스케줄 비교를 검토합니다. 실제 백업 완료가 예정 시간과 맞지 않으면 백업 Job이 실패하거나 지연되고 있습니다. 백업 Job 실패를 조사합니다.

5. 8단계의 복원 완료 분석에서 RTO를 놓치고 있으면 병목(데이터 전송, 컴퓨팅 리소스, 스토리지 I/O)을 파악하고 그에 맞게 최적화합니다.

분석이 결론에 이르지 못하면: 2단계의 이벤트에서 백업 또는 복원 실패를 확인합니다. RTO/RPO 위반이 특정 시간대에 집중되어 있는지(리소스 경합 시사) 또는 무작위인지(인프라 문제 시사) 판단합니다. RTO/RPO 목표가 데이터 볼륨과 인프라 역량에 비해 현실적인지 확인합니다.
