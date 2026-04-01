---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/13-Proactive/02-Security-Compliance/IAM-Policy-Review-K8s.md)'
role: SRE / K8s Proactive Operations
origin: scoutflo
tags:
- compliance
- iam
- infrastructure
- k8s-namespace
- k8s-pod
- k8s-rbac
- k8s-service
- policy
- review
- security
---

# RBAC Policy Review — RBAC 정책 검토

## 의미

RBAC 정책 검토는 RBAC 정책이 과도하게 허용적이거나, 잘못 구성되었거나, 최소 권한 원칙을 위반하고 있음을 나타냅니다(OverlyPermissiveRBACPolicy 또는 RBACPolicyAuditFailed 같은 알림 발생). RBAC 정책이 과도한 권한을 부여하거나, 사용되지 않는 RBAC 역할이 존재하거나, RBAC 정책이 최소 권한 원칙을 위반하거나, RBAC RoleBinding이 와일드카드 리소스를 허용하거나, RBAC 정책 조건이 누락되거나 잘못 구성된 것이 원인입니다. RBAC 정책에서 과도하게 허용적인 구문이 나타나고, RBAC 정책 감사 결과에서 위반이 감지되며, 사용되지 않는 RBAC 역할이 탐지되고, RBAC 정책 구성이 보안 정책을 위반합니다. 이는 보안 계층과 접근 제어에 영향을 미치며, 일반적으로 잘못 구성된 RBAC 정책, RBAC 역할 수명주기 관리 부재, 또는 보안 정책 위반으로 인해 발생합니다. RBAC 정책이 컨테이너 워크로드를 보호하는 경우 컨테이너 ServiceAccount 권한이 과도하게 허용적이고 애플리케이션에서 보안 위험이 발생할 수 있습니다.

## 영향

RBACPolicyAuditFailed 알림 발생, OverlyPermissiveRBACPolicy 알림 발생, 접근 권한이 과도하게 허용적, 보안 정책 위반, 사용되지 않는 RBAC 역할이 리소스 소비, RBAC 정책이 최소 권한 원칙 위반. RBAC 정책 구성에서 과도하게 허용적인 구문이 나타나며, RBAC 정책이 컨테이너 워크로드를 보호하는 경우 컨테이너 ServiceAccount 권한이 과도하게 허용적이고, Pod RBAC 역할 권한이 잘못 구성되며, 컨테이너 애플리케이션에서 보안 위험이 발생할 수 있습니다. 애플리케이션에서 보안 취약점 또는 무단 접근 위험이 발생할 수 있습니다.

## 플레이북

1. 네임스페이스 <namespace>의 Role과 RoleBinding을 상세 조회하고, ClusterRole과 ClusterRoleBinding을 상세 조회하여 환경의 모든 역할과 바인딩을 파악합니다.

2. 모든 네임스페이스에서 최근 이벤트를 타임스탬프 순으로 조회하고 관련 오브젝트 종류가 Role 및 ClusterRole인 것을 필터링하여 최근 RBAC 수정 사항을 확인합니다.

3. 네임스페이스 <namespace>의 Role을 YAML 형식으로 조회하고 리소스나 동사에 대한 와일드카드 권한이 있는지 분석하여 과도하게 허용적인 구성을 확인합니다.

4. 네임스페이스 <namespace>의 Role <role-name>을 상세 조회하여 전체 규칙 세트를 확인하고 리소스나 동사에 대한 과도한 권한이 있는지 점검합니다.

5. 네임스페이스 <namespace>의 ServiceAccount <sa-name>에 대해 허용된 모든 작업을 조회하여 역할이 허용하는 권한을 확인합니다.

6. ClusterRole을 YAML 형식으로 조회하고 Secret 접근, pods/exec, 와일드카드 리소스 등 위험한 권한이 있는지 분석합니다.

7. 네임스페이스 <namespace>의 RoleBinding을 상세 조회하고 ClusterRoleBinding을 상세 조회하여 어떤 ID가 어떤 역할을 가지고 있는지 확인합니다.

8. 네임스페이스 <namespace>의 ServiceAccount <sa-name>이 Secret 생성, ConfigMap 생성, pods/exec, Node 접근 등 민감한 작업을 수행할 수 있는지 확인하여 최소 권한 요구사항에 대한 권한을 검증합니다.

## 진단

1. 3단계와 6단계의 Role 및 ClusterRole 구성을 검토합니다. 리소스나 동사에 대한 와일드카드 권한이 있으면 즉시 해결이 필요한 최우선 보안 문제입니다.

2. 8단계의 권한 점검을 분석합니다. ServiceAccount가 운영 요구사항을 초과하는 민감한 작업(Secret 생성, pods/exec, Node 접근)을 수행할 수 있으면 최소 권한 원칙이 위반되고 있습니다.

3. 4단계의 역할 규칙에서 과도한 권한이 나타나면 의도적으로 구성된 것인지 템플릿/기본 구성에서 비롯된 것인지 확인합니다. 권한이 문서화된 요구사항을 초과하면 역할 적정화가 필요합니다.

4. 7단계의 RoleBinding을 활성 Pod 사용량과 비교합니다. ID가 역할에 바인딩되어 있지만 해당 권한을 적극적으로 사용하지 않으면 사용되지 않는 RoleBinding이 존재하며 제거를 검토해야 합니다.

5. 7단계에서 cluster-admin 또는 admin 바인딩이 확인되면 각 주체에 문서화된 비즈니스 정당성이 있는지 확인합니다. 정당성이 없으면 권한 상승 위험이 존재합니다.

분석이 결론에 도달하지 못하는 경우: 2단계의 RBAC 이벤트를 검토하여 권한 확대를 도입했을 수 있는 최근 수정 사항을 확인합니다. 과도하게 허용적인 정책이 특정 네임스페이스에 집중되어 있는지(국소적 구성 오류 시사) 또는 광범위하게 분산되어 있는지(체계적 정책 문제 시사) 판단합니다. RBAC 역할 수명주기 관리 프로세스를 점검하고 정기적인 접근 권한 검토가 수행되고 있는지 확인합니다.
