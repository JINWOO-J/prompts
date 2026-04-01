---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/13-Proactive/02-Security-Compliance/Compliance-Status-Check-K8s.md)'
role: SRE / K8s Proactive Operations
origin: scoutflo
tags:
- check
- compliance
- infrastructure
- k8s-namespace
- k8s-pod
- monitoring
- security
- status
---

# Compliance Status Check — 컴플라이언스 상태 점검

## 의미

컴플라이언스 상태 점검은 컴플라이언스 상태를 확인할 수 없거나 컴플라이언스 위반이 감지되었음을 나타냅니다(ComplianceViolation 또는 ComplianceStatusCheckFailed 같은 알림 발생). 컴플라이언스 상태 점검이 실패하거나, 컴플라이언스 위반이 감지되거나, 컴플라이언스 모니터링에서 문제가 감지되거나, 컴플라이언스 구성이 누락되거나, 컴플라이언스 상태 데이터가 사용 불가한 것이 원인입니다. 이는 컴플라이언스 계층과 규제 준수에 영향을 미치며, 일반적으로 컴플라이언스 구성 실패, 컴플라이언스 모니터링 도구 실패, 컴플라이언스 위반 감지 문제, 또는 컴플라이언스 상태 점검 모니터링 격차로 인해 발생합니다.

## 영향

ComplianceViolation 알림 발생, ComplianceStatusCheckFailed 알림 발생, 컴플라이언스 상태 확인 불가, 컴플라이언스 위반 감지, 규제 준수 저하 가능, 컴플라이언스 위험 존재 가능.

## 플레이북

1. 네임스페이스 <namespace>의 모든 리소스를 조회하여 컴플라이언스 검증이 필요한 모든 리소스를 확인합니다.
2. 네임스페이스 <namespace>의 최근 이벤트를 타임스탬프 순으로 조회하여 최근 컴플라이언스 위반이나 정책 문제를 확인합니다.
3. 네임스페이스 <namespace>의 Pod를 상세 조회하여 보안 컨텍스트와 컴플라이언스 관련 설정을 확인합니다.
4. 네임스페이스 <namespace>의 NetworkPolicy와 PodSecurityPolicy를 조회하여 정책 평가 상태를 검토합니다.
5. 네임스페이스 <namespace>에서 app=compliance-monitor 레이블의 컴플라이언스 모니터링 Pod 로그를 조회하고 컴플라이언스 위반 패턴을 필터링합니다.
6. Pod Security Standards, CIS Kubernetes, 또는 규제 컴플라이언스 상태를 포함한 컴플라이언스 표준 상태를 조회하여 표준별 위반을 확인합니다.
7. 컴플라이언스 위반에 대한 보안 감사 결과 상세를 조회하고 위반 설명, 영향받는 리소스, 해결 권장사항을 확인합니다.
8. 네임스페이스 <namespace>의 Role, RoleBinding, ClusterRole, ClusterRoleBinding을 조회하고 RBAC 보안 모범 사례 준수를 확인합니다.

## 진단

1. 1단계의 리소스 목록과 3단계의 Pod 구성을 검토합니다. Pod에 보안 컨텍스트 문제가 있거나 상승된 권한으로 실행되면 해결이 필요한 일반적인 컴플라이언스 위반입니다.
2. 4단계의 정책 구성을 분석합니다. NetworkPolicy나 PodSecurityPolicy에 격차가 있으면 보안 적용이 불완전하고 컴플라이언스 상태에 위반이 반영됩니다.
3. 5단계의 컴플라이언스 모니터링 로그에서 위반 패턴이 나타나면 실패하는 특정 컴플라이언스 제어와 위반을 유발하는 리소스를 확인합니다.
4. 6단계의 컴플라이언스 표준 상태를 검토합니다. 표준에서 FAILED 상태가 나타나면 규제 요구사항과 감사 일정에 따라 해결 우선순위를 정합니다.
5. 4단계의 해결 추적에서 위반이 신속하게 해결되지 않으면 컴플라이언스 해결 프로세스 개선이 필요합니다. 해결이 이루어지지만 새 위반이 나타나면 예방 조치가 불충분합니다.

분석이 결론에 도달하지 못하는 경우: 2단계의 이벤트에서 컴플라이언스 관련 문제를 확인합니다. 7단계의 위반 심각도를 검토하여 해결 우선순위를 정합니다. 컴플라이언스 모니터링 도구가 올바르게 구성되어 있고 컴플라이언스 검증이 필요한 모든 리소스에 대한 가시성이 있는지 확인합니다.
