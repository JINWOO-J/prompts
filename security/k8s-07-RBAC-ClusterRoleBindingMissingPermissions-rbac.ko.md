---
category: security
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/07-RBAC/ClusterRoleBindingMissingPermissions-rbac.md)'
role: Kubernetes SRE
origin: scoutflo
extract_date: 2026-03-05
tags:
- clusterrolebindingmissingpermissions
- k8s-namespace
- k8s-rbac
- k8s-service
- kubernetes
- performance
- rbac
- security
- sts
---

---
title: ClusterRoleBinding Missing Permissions - RBAC
weight: 218
categories:
  - kubernetes
  - rbac
---

# ClusterRoleBinding 권한 누락 — ClusterRoleBindingMissingPermissions-rbac

## 의미

ClusterRoleBinding이 충분한 권한을 부여하지 않습니다(KubeAPIErrorsHigh 알림 발생). 원인으로는 참조된 ClusterRole에 필요한 규칙이 없거나, 바인딩에 필요한 모든 주체가 포함되지 않았거나, ClusterRole에서 권한이 제거된 경우입니다. ClusterRoleBinding 리소스에 권한 누락이 표시되고, ClusterRole 리소스에 불충분한 규칙이 표시될 수 있으며, API 요청이 403 상태 코드를 반환합니다. 이는 인증 및 인가 플레인에 영향을 미치며 클러스터 전체 작업을 방해합니다. 일반적으로 ClusterRole 규칙 누락이나 잘못된 ClusterRoleBinding 구성이 원인이며, Kubernetes API를 사용하는 애플리케이션에서 오류가 발생할 수 있습니다.

## 영향

클러스터 전체 작업 실패, 사용자 필요 작업 수행 불가, 서비스 계정 권한 부족, KubeAPIErrorsHigh 알림 발생, API 서버 Forbidden 오류 반환, 인가 실패로 클러스터 관리 차단, 권한 거부로 애플리케이션 실패, 클러스터 관리 차단. ClusterRoleBinding 리소스에 권한 누락 무기한 표시. ClusterRole 리소스에 불충분한 규칙 표시 가능. Kubernetes API를 사용하는 애플리케이션에서 오류나 성능 저하 발생 가능. 클러스터 관리가 차단됩니다.

## 플레이북

1. 사용자 또는 ServiceAccount <namespace>:<sa-name>이 <resource>에 대해 <verb>를 수행할 수 있는지 확인하여 실패하는 특정 권한을 테스트하고 어떤 액션이 거부되는지 즉시 식별하여 권한 갭을 확인합니다.

2. 영향받는 사용자 또는 ServiceAccount <namespace>:<sa-name>의 모든 권한을 나열하여 부여된 권한의 전체 세트를 확인하고 누락된 항목을 식별합니다.

3. ClusterRoleBinding <binding-name>을 설명하여 주체, 역할 참조, 어떤 사용자나 서비스 계정이 바인딩되었는지와 어떤 ClusterRole이 참조되는지를 보여주는 어노테이션을 검사합니다.

4. ClusterRole <role-name>을 설명하여 규칙을 검사하고 어떤 권한이 부여되는지 확인하며 1단계에서 거부된 액션과 비교합니다.

5. 모든 네임스페이스에서 Forbidden 사유로 필터링된 이벤트를 조회하여 권한 거부를 나타내는 인가 관련 이벤트를 식별합니다.

6. 가용한 경우 API 서버 감사 로그를 확인하여 forbidden 또는 unauthorized 액션에 대한 인가 결정을 검토합니다.

7. ClusterRoleBinding에 권한이 필요한 모든 주체(사용자, 서비스 계정, 그룹)가 포함되어 있는지 확인하며 주체 목록을 1단계의 ID와 비교합니다.

## 진단

1. 플레이북 1단계에서 `auth can-i` 확인이 특정 권한 갭(verb + resource)을 식별합니다. 이 결과를 사용하여 RBAC 체인에서 이 정확한 권한이 누락된 이유에 대한 조사에 집중합니다.

2. `auth can-i` 결과가 필요한 verb+resource에 대해 "no"를 표시하면 ClusterRole 규칙(플레이북 4단계)을 확인합니다:
   - ClusterRole에 필요한 verb+resource 규칙이 포함되지 않으면 **ClusterRole 규칙 누락** 문제입니다. ClusterRole 수정 타임스탬프와 권한 거부 시작 시점을 비교하여 규칙이 최근 제거되었는지 판단합니다.
   - ClusterRole에 권한을 포함해야 하는 와일드카드 규칙이 있으면 명시적 거부 규칙이나 리소스 그룹 불일치를 확인합니다.

3. ClusterRole에 필요한 규칙이 있지만 주체가 ClusterRoleBinding(플레이북 3단계)에 나열되지 않으면 **주체 바인딩 누락** 문제입니다:
   - 사용자, ServiceAccount, 그룹이 최근 바인딩에서 제거되었는지 확인합니다.
   - 바인딩에서 주체 이름이나 네임스페이스가 잘못 입력되었는지 확인합니다.
   - ServiceAccount의 경우 형식이 `system:serviceaccount:<namespace>:<sa-name>`인지 확인합니다.

4. ClusterRole과 ClusterRoleBinding 모두 올바른 것으로 보이면 **네임스페이스 범위 불일치**를 확인합니다:
   - 네임스페이스 리소스에 접근하는 경우 ClusterRole/ClusterRoleBinding 대신 Role/RoleBinding을 사용해야 하는지 확인합니다.
   - ClusterRoleBinding이 특정 네임스페이스의 RoleBinding으로 잘못 생성되었는지 확인합니다.

5. ClusterRole이 집계를 통해 규칙을 상속해야 하는 경우 **집계 규칙 누락**을 확인합니다:
   - 집계된 ClusterRole에 올바른 `aggregationRule.clusterRoleSelectors` 레이블이 있는지 확인합니다.
   - 규칙을 기여하는 하위 ClusterRole이 여전히 존재하고 매칭되는 레이블이 있는지 확인합니다.

6. ClusterRole 또는 ClusterRoleBinding이 삭제되거나 교체된 경우 API 서버 감사 로그(플레이북 6단계)에서 삭제 타임스탬프를 확인합니다:
   - 권한 거부 30분 이내에 ClusterRole에 대한 `delete` 또는 `patch` 작업을 확인합니다.
   - RBAC 리소스를 수정했을 수 있는 컨트롤러나 오퍼레이터 활동을 확인합니다.

7. 모든 RBAC 리소스가 올바른 것으로 보이면 Forbidden 이벤트(플레이북 5단계)와 API 서버 감사 로그(플레이북 6단계)에서 인가 결정 세부사항을 검토합니다:
   - 거부가 간헐적인지 확인합니다(캐싱 또는 API 서버 동기화 문제 가능).
   - 여러 인가 모드가 구성되어 있고 다른 인가자가 요청을 거부하는지 확인합니다.
   - 평가되는 ID에 영향을 줄 수 있는 가장(impersonation) 헤더를 확인합니다.

**근본 원인이 식별되지 않는 경우**: 타임스탬프 상관관계의 검색 범위를 확장하고(30분→1시간, 1시간→2시간), GitOps나 정책 컨트롤러를 통한 점진적 RBAC 정책 드리프트를 확인하고, RBAC 리소스 조회 문제에 대한 etcd 상태를 확인하고, 어드미션 컨트롤러나 OPA/Gatekeeper 정책이 RBAC 결정에 간섭하는지 조사합니다.
