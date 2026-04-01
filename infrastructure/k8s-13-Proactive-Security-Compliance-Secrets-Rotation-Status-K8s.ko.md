---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/13-Proactive/02-Security-Compliance/Secrets-Rotation-Status-K8s.md)'
role: SRE / K8s Proactive Operations
origin: scoutflo
tags:
- compliance
- infrastructure
- k8s-namespace
- k8s-pod
- k8s-secret
- k8s-service
- rotation
- secrets
- security
- status
---

# Secrets Rotation Status — Secret 로테이션 상태

## 의미

Secret 로테이션 상태는 Secret 로테이션이 일정에 따라 수행되지 않았거나 로테이션 작업이 실패했음을 나타냅니다(SecretsRotationFailed 또는 SecretsRotationOverdue 같은 알림 발생). Secret 로테이션 일정이 충족되지 않거나, 로테이션 작업이 실패하거나, 로테이션 상태가 기한 초과를 나타내거나, 로테이션 자동화가 트리거되지 않거나, 로테이션 완료를 확인할 수 없는 것이 원인입니다. Secret에서 로테이션 기한 초과 상태가 나타나고, 로테이션 작업에서 실패 상태가 나타나며, 로테이션 일정이 충족되지 않고, 로테이션 자동화 트리거가 활성화되지 않습니다. 이는 보안 계층과 Secret 관리에 영향을 미치며, 일반적으로 로테이션 자동화 실패, 로테이션 일정 구성 오류, 로테이션 ServiceAccount 권한 문제, 또는 로테이션 서비스 비가용으로 인해 발생합니다. Secret이 컨테이너 워크로드를 보호하는 경우 컨테이너 Secret 로테이션이 실패하고 애플리케이션에서 인증 실패가 발생할 수 있습니다.

## 영향

SecretsRotationFailed 알림 발생, SecretsRotationOverdue 알림 발생, Secret이 침해될 수 있음, 로테이션 일정 미충족, 로테이션 자동화 실패, 보안 정책 위반. Secret 로테이션 상태에서 기한 초과 또는 실패가 나타나며, Secret이 컨테이너 워크로드를 보호하는 경우 컨테이너 Secret 로테이션이 실패하고, Pod Secret 업데이트가 이루어지지 않으며, 컨테이너 애플리케이션에서 인증 실패가 발생할 수 있습니다. 애플리케이션에서 인증 실패 또는 오래된 Secret으로 인한 보안 위험이 발생할 수 있습니다.

## 플레이북

1. 네임스페이스 <namespace>의 모든 Secret을 상세 조회하여 생성 타임스탬프와 유형을 포함한 Secret 메타데이터를 확인합니다.
2. 네임스페이스 <namespace>의 최근 이벤트를 타임스탬프 순으로 조회하여 Secret 로테이션 실패, 권한 오류, Secret 관련 경고를 확인합니다.
3. 네임스페이스 <namespace>의 Secret <secret-name>을 상세 조회하여 로테이션 구성 어노테이션과 마지막 로테이션 타임스탬프를 포함한 Secret 세부 정보를 검사합니다.
4. 네임스페이스 `<namespace>`에서 자동 Secret 로테이션이 활성화된 Pod를 조회하고 로테이션 상태와 마지막 로테이션 타임스탬프를 확인합니다.
5. 네임스페이스 `<namespace>`의 Secret 로테이션 Pod 로그를 조회하고 최근 7일 이내의 로테이션 실패 패턴이나 로테이션 기한 초과 경고를 필터링합니다.
6. 최근 30일간의 Secret 로테이션 서비스에 대한 Prometheus 메트릭(rotation_success_rate, rotation_duration 포함)을 조회하여 로테이션 실패 패턴을 파악합니다.
7. 네임스페이스 `<namespace>`에서 Secret 로테이션에 연결된 ServiceAccount `<service-account-name>`을 조회하고 RoleBinding 권한을 확인하여 로테이션 역할 접근을 검증합니다.
8. Secret 로테이션 일정 타임스탬프와 실제 로테이션 완료 타임스탬프를 비교하고, Secret 로테이션 데이터를 보조 증거로 사용하여 로테이션이 일정에 따라 수행되는지 확인합니다.
9. Secret `<secret-name>` 로테이션 Job 구성을 조회하고 로테이션 자동화가 올바르게 구성되어 있는지 확인하며 로테이션 Job 접근성을 점검합니다.

## 진단

1. 1단계와 3단계의 Secret 메타데이터를 검토합니다. 어노테이션에서 로테이션 타임스탬프가 로테이션 일정 요구사항보다 상당히 오래된 것으로 나타나면 로테이션이 기한을 초과한 것이며 즉시 로테이션이 필요합니다.

2. 5단계의 로테이션 Pod 로그를 분석합니다. 로그에서 로테이션 실패 패턴이 나타나면 실패가 권한, 네트워크 문제, 또는 대상 비가용 중 어떤 원인인지 파악합니다. 로그에서 로테이션 시도가 없으면 스케줄링이 문제입니다.

3. 6단계의 로테이션 메트릭에서 낮은 성공률이 나타나면 로테이션 인프라에 체계적 문제가 있습니다. 성공률은 높지만 특정 Secret이 기한을 초과했으면 해당 Secret에 구성 문제가 있을 수 있습니다.

4. 7단계의 ServiceAccount 권한을 검토합니다. 로테이션 ServiceAccount에 필요한 권한이 없으면 RBAC 구성 업데이트가 필요합니다. 권한이 올바르면 운영상의 문제가 실패를 유발하고 있습니다.

5. 8단계의 일정 비교에서 로테이션이 예정된 시간에 수행되지 않으면 9단계의 로테이션 Job 구성이 적절한 트리거와 일정으로 올바르게 구성되어 있는지 확인합니다.

분석이 결론에 도달하지 못하는 경우: 2단계의 이벤트에서 권한 오류나 Secret 관련 경고를 확인합니다. 로테이션 실패가 모든 Secret에 영향을 미치는지(인프라 문제 시사) 또는 특정 Secret에만 영향을 미치는지(Secret별 구성 문제 시사) 판단합니다. Secret 로테이션 자동화가 로테이션된 Secret을 소비하는 다운스트림 시스템에 대한 필요한 네트워크 접근 권한을 가지고 있는지 확인합니다.
