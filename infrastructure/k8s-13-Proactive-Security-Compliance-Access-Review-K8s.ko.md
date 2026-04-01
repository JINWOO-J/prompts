---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/13-Proactive/02-Security-Compliance/Access-Review-K8s.md)'
role: SRE / K8s Proactive Operations
origin: scoutflo
tags:
- access
- compliance
- infrastructure
- k8s-namespace
- k8s-pod
- k8s-rbac
- k8s-service
- monitoring
- review
- security
---

# Access Review — 접근 권한 검토

## 의미

접근 권한 검토는 접근 권한을 검토할 수 없거나 과도한 접근 권한이 감지되었음을 나타냅니다(ExcessiveAccessDetected 또는 AccessReviewFailed 같은 알림 발생). 접근 권한 검토 도구가 실패하거나, 접근 권한이 검토되지 않거나, 과도한 접근 권한이 감지되거나, 접근 권한 검토 모니터링에서 문제가 감지되거나, 접근 권한 검토 구성이 누락된 것이 원인입니다. 접근 권한 검토에서 실패가 나타나고, 접근 권한이 검토되지 않으며, 과도한 접근 권한이 감지되고, 접근 권한 검토가 실패합니다. 이는 컴플라이언스 계층과 접근 관리에 영향을 미치며, 일반적으로 접근 권한 검토 구성 실패, 접근 권한 검토 도구 실패, 접근 권한 분석 문제, 또는 접근 권한 검토 모니터링 격차로 인해 발생합니다. 접근 권한 검토가 컨테이너 워크로드에 영향을 미치면 컨테이너 접근 권한이 과도하고 애플리케이션에서 접근 관리 위험이 발생할 수 있습니다.

## 영향

ExcessiveAccessDetected 알림 발생, AccessReviewFailed 알림 발생, 접근 권한 검토 불가, 과도한 접근 권한 감지, 접근 관리 저하 가능, 보안 위험 존재 가능. 접근 권한 검토에서 실패가 나타나며, 접근 권한 검토가 컨테이너 워크로드에 영향을 미치면 컨테이너 접근 권한이 과도하고, Pod 접근 제어가 잘못 구성되며, 컨테이너 애플리케이션에서 접근 관리 위험이 발생할 수 있습니다. 애플리케이션에서 접근 권한 검토 격차 또는 보안 위험이 발생할 수 있습니다.

## 플레이북

1. 네임스페이스 <namespace>의 RoleBinding과 ClusterRoleBinding을 상세 조회하여 현재 접근 바인딩과 구성을 파악합니다.

2. 네임스페이스 <namespace>의 최근 이벤트를 타임스탬프 순으로 조회하여 최근 RBAC 변경이나 접근 문제를 확인합니다.

3. 네임스페이스 <namespace>의 모든 ServiceAccount를 조회하여 권한을 가질 수 있는 모든 ID를 확인합니다.

4. 각 ServiceAccount에 대해 네임스페이스 <namespace>의 ServiceAccount <sa-name>의 권한을 확인하여 허용된 모든 작업을 조회합니다.

5. 네임스페이스 <namespace>의 Role <role-name> 또는 ClusterRole <role-name>을 상세 조회하여 와일드카드 및 광범위한 동사를 포함한 과도한 권한 규칙을 확인합니다.

6. 네임스페이스 <namespace>의 ServiceAccount <sa-name>이 Pod를 생성할 수 있는지 확인하고 Secret, ConfigMap, exec 작업 등 민감한 리소스에 대해 유사한 테스트를 수행합니다.

7. ClusterRoleBinding을 조회하고 cluster-admin 또는 admin 역할에 바인딩된 모든 주체를 확인합니다.

8. 네임스페이스 <namespace>의 ServiceAccount와 Pod ServiceAccount 참조를 비교하여 사용되지 않는 ServiceAccount를 확인합니다.

## 진단

1. 6단계의 권한 점검을 검토합니다. ServiceAccount가 문서화된 요구사항을 초과하는 민감한 작업(Pod 생성, Secret 접근, 컨테이너 exec)을 수행할 수 있으면 해결이 필요한 과도한 접근입니다.

2. 5단계의 역할 정의를 분석합니다. 역할에 리소스나 동사에 대한 와일드카드가 포함되어 있으면 과도한 권한이며 필요한 특정 권한으로 제한해야 합니다.

3. 7단계의 ClusterRoleBinding에서 문서화된 정당성 없이 cluster-admin에 바인딩된 ID가 나타나면 최우선 발견 사항입니다. 각 admin 바인딩에 정당한 비즈니스 요구사항이 있는지 확인합니다.

4. 8단계의 ServiceAccount 비교를 검토합니다. Pod에서 참조하지 않는 ServiceAccount가 존재하면 사용되지 않으며 제거 후보입니다. Pod에서 사용 중이면 권한이 Pod 요구사항과 일치하는지 확인합니다.

5. 4단계의 권한 분석에서 ServiceAccount가 연관된 워크로드에 필요하지 않은 작업을 수행할 수 있으면 권한 축소가 필요합니다.

분석이 결론에 도달하지 못하는 경우: 2단계의 이벤트에서 권한 확대를 도입했을 수 있는 최근 RBAC 변경을 확인합니다. 과도한 접근이 특정 네임스페이스에 집중되어 있는지(국소적 구성 문제 시사) 또는 클러스터 전체에 분산되어 있는지(정책 격차 시사) 판단합니다. 정기적인 접근 권한 검토 프로세스가 존재하고 준수되고 있는지 확인합니다.
