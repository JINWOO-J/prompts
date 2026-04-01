---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/13-Proactive/03-Backup-DR/Disaster-Recovery-Runbook-Execution-K8s.md)'
role: SRE / K8s Proactive Operations
origin: scoutflo
tags:
- backup
- disaster
- disaster-recovery
- execution
- infrastructure
- k8s-namespace
- k8s-service
- recovery
- runbook
---

# Disaster Recovery Runbook Execution (재해 복구 런북 실행)

## 의미

Disaster Recovery 런북 실행 알림은 DR 런북 절차를 실행할 수 없거나 재해 복구 시나리오에서 런북 단계가 실패하는 상황(DRRunbookFailed 또는 DRExecutionFailed 같은 알림 발생)을 나타냅니다. 런북 자동화 실패, 런북 단계 타임아웃, 런북 의존성 미가용, 런북 유효성 검사 실패, 또는 런북 실행 로그의 단계 실패 등이 원인입니다. DR 런북 실행이 실패 상태를 보이고, 런북 단계가 대기 상태에 머물며, 런북 자동화 트리거가 활성화되지 않고, 런북 실행 로그에 오류 패턴이 나타납니다. 이는 재해 복구 계층과 자동화 인프라에 영향을 미치며, 주로 런북 자동화 설정 오류, 의존성 미가용, 타임아웃 문제, 또는 런북 단계 실패가 원인입니다. DR 런북이 컨테이너 워크로드를 보호하는 경우, 컨테이너 재해 복구가 실패하고 애플리케이션이 장시간 다운타임을 겪을 수 있습니다.

## 영향

DRRunbookFailed 알림 발생, DRExecutionFailed 알림 발생, 재해 복구 절차 실행 불가, DR 런북 자동화 실패, 런북 단계 타임아웃, 런북 의존성 미가용, 런북 유효성 검사 실패. DR 런북 실행이 실패 또는 대기 상태로 유지되고, 런북 자동화 트리거가 활성화되지 않습니다. DR 런북이 컨테이너 워크로드를 보호하는 경우, 컨테이너 재해 복구가 실패하고, 클러스터 복구 절차가 실행되지 않으며, 컨테이너 애플리케이션이 장시간 다운타임을 겪을 수 있습니다. 애플리케이션이 장시간 서비스 중단 또는 복구 실패를 경험할 수 있습니다.

## 플레이북

1. namespace <namespace>에서 label app=dr-runbook인 Job을 조회하여 모든 재해 복구 런북 Job과 현재 상태를 확인합니다.

2. namespace <namespace>에서 최근 이벤트를 타임스탬프 순으로 조회하여 최근 런북 실행 실패나 문제를 확인합니다.

3. namespace <namespace>에서 Job <runbook-job-name>을 describe하여 단계 실행 상태, 완료 타임스탬프, 오류 메시지를 점검합니다.

4. namespace <namespace>에서 런북 Pod <runbook-pod-name>의 로그를 조회하고 'runbook failed', 'step timeout', 'dependency unavailable' 등의 오류 패턴을 필터링합니다.

5. 런북 서비스의 Prometheus 메트릭(runbook_execution_success_rate, runbook_step_duration)을 최근 24시간 동안 조회하여 런북 실행 실패 패턴을 확인합니다.

6. namespace <namespace>에서 서비스 어카운트 <service-account-name>을 describe하고 역할 바인딩 권한을 확인하여 런북 자동화 서비스 어카운트 권한을 검증합니다.

7. namespace <namespace>에서 ConfigMap <runbook-configmap-name>을 YAML 출력으로 조회하여 단계 정의와 자동화 트리거를 점검합니다.

8. namespace <namespace>에서 label app=dr-dependency인 모든 리소스를 조회하고 의존성 리소스 가용성을 확인합니다.

## 진단

1. 1단계와 3단계의 DR 런북 Job 상태를 검토합니다. Job이 실패 상태이면 오류 메시지를 분석하여 실패 원인(의존성 미가용, 권한, 타임아웃, 설정 문제)을 파악합니다.

2. 4단계의 런북 Pod 로그를 분석합니다. 로그에 단계 타임아웃이나 의존성 미가용 패턴이 있으면 어떤 단계가 왜 실패하는지 확인합니다.

3. 5단계의 런북 메트릭에서 성공률이 낮으면 체계적인 런북 문제가 존재합니다. 성공률은 높지만 특정 런북이 실패하면 해당 런북의 설정 문제입니다.

4. 6단계의 서비스 어카운트 권한을 검토합니다. 권한이 부족하면 런북 자동화가 필요한 작업을 실행할 수 없습니다. RBAC 권한이 런북 요구사항과 일치하는지 확인합니다.

5. 8단계의 의존성 리소스 가용성에서 미가용 리소스가 있으면 런북 의존성이 준비되지 않은 것입니다. 런북 실행 전에 의존성 리소스가 배포되고 정상인지 확인합니다.

분석이 결론에 이르지 못하면: 2단계의 이벤트에서 런북 실행 실패를 확인합니다. 7단계의 런북 설정을 검토하여 단계 정의와 자동화 트리거가 올바른지 확인합니다. 런북 실패가 특정 단계에 집중되어 있는지(단계별 문제 시사) 또는 분산되어 있는지(인프라 문제 시사) 판단합니다.
