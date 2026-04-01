---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/13-Proactive/02-Security-Compliance/Compliance-Check-K8s.md)'
role: SRE / K8s Proactive Operations
origin: scoutflo
tags:
- check
- compliance
- infrastructure
- k8s-namespace
- k8s-pod
- kubernetes
- monitoring
- rds
- security
---

# Compliance Check — 컴플라이언스 점검

## 의미

컴플라이언스 점검은 Kubernetes 리소스 또는 구성이 컴플라이언스 요구사항, 보안 표준, 또는 규제 정책을 위반했음을 나타냅니다(ComplianceViolation 또는 SecurityComplianceFailed 같은 알림 발생).
 보안 감사 결과에서 컴플라이언스 실패가 나타나거나, 컴플라이언스 점검이 실패하거나, 보안 표준이 위반되거나, 규제 요구사항이 충족되지 않거나, 컴플라이언스 상태에서 정책 위반이 나타나는 것이 원인입니다. 이는 보안 계층과 컴플라이언스 상태에 영향을 미치며, 일반적으로 잘못 구성된 보안 설정, 비준수 리소스 구성, 컴플라이언스 정책 위반, 또는 컴플라이언스 모니터링 실패로 인해 발생합니다. 컴플라이언스가 컨테이너 워크로드에 영향을 미치면 컨테이너 보안 구성이 정책을 위반하고 애플리케이션에서 컴플라이언스 위험이 발생할 수 있습니다.

## 영향

ComplianceViolation 알림 발생, SecurityComplianceFailed 알림 발생, 컴플라이언스 요구사항 위반, 보안 표준 미충족, 규제 요구사항 미충족, 컴플라이언스 상태 저하. 컴플라이언스가 컨테이너 워크로드에 영향을 미치면 컨테이너 보안 구성이 정책을 위반하고, Pod 보안 컨텍스트가 비준수이며, 컨테이너 애플리케이션에서 컴플라이언스 위험이 발생할 수 있습니다.

## 플레이북

1. 네임스페이스 <namespace>의 Pod를 YAML 출력으로 조회하여 컴플라이언스 검토를 위한 Pod와 보안 컨텍스트 설정을 확인합니다.
2. 네임스페이스 <namespace>의 최근 이벤트를 타임스탬프 순으로 조회하여 최근 보안 정책 위반이나 컴플라이언스 문제를 확인합니다.
3. 네임스페이스 <namespace>의 Pod <pod-name>을 상세 조회하여 보안 컨텍스트 구성을 확인하고 비준수 설정을 식별합니다.
4. 네임스페이스 <namespace>의 PodSecurityPolicy와 NetworkPolicy를 조회하여 구성된 보안 정책을 검토합니다.
5. 네임스페이스 <namespace>에서 app=security-audit 레이블의 보안 감사 Pod 로그를 조회하고 컴플라이언스 위반 패턴을 필터링합니다.
6. Pod Security Standards, CIS Kubernetes, 또는 규제 컴플라이언스 상태를 포함한 보안 컴플라이언스 표준 상태를 조회하여 표준별 위반을 확인합니다.
7. 컴플라이언스 위반에 대한 보안 감사 결과 상세를 조회하고 위반 설명, 영향받는 리소스, 해결 권장사항을 확인합니다.
8. 네임스페이스 <namespace>의 Role과 RoleBinding을 조회하고 RBAC 보안 모범 사례 및 최소 권한 원칙 준수를 확인합니다.

## 진단

1. 1단계와 3단계의 Pod 보안 컨텍스트를 검토합니다. Pod가 root로 실행되거나, 특권 컨테이너를 사용하거나, 보안 컨텍스트가 없으면 일반적인 컴플라이언스 위반입니다. 가장 심각한 위반부터 해결합니다.

2. 4단계의 보안 정책 구성을 분석합니다. PodSecurityPolicy나 NetworkPolicy가 누락되거나 잘못 구성되면 보안 적용이 불완전합니다.

3. 5단계의 보안 감사 로그에서 위반 패턴이 나타나면 위반이 특정 네임스페이스에 집중되어 있는지 또는 분산되어 있는지 확인합니다. 집중된 위반은 국소적 설정 오류를, 분산된 위반은 정책 템플릿 문제를 시사합니다.

4. 6단계의 컴플라이언스 표준 상태를 검토합니다. 특정 표준(Pod Security Standards, CIS Kubernetes)에서 위반이 나타나면 표준 중요도와 감사 요구사항에 따라 해결 우선순위를 정합니다.

5. 8단계의 RBAC 분석에서 최소 권한 원칙 위반이 나타나면 워크로드 컴플라이언스와 함께 접근 제어 컴플라이언스에도 주의가 필요합니다.

분석이 결론에 도달하지 못하는 경우: 2단계의 이벤트에서 보안 정책 위반을 확인합니다. 7단계의 위반 심각도를 검토하여 해결 우선순위를 정합니다. 위반이 증가하고 있는지(컴플라이언스 상태 저하 시사) 또는 안정적인지(문서화가 필요한 알려진 수용 위험 시사) 판단합니다.
