---
category: security
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/07-RBAC/RBACPermissionDeniedError-rbac.md)'
role: Kubernetes SRE
origin: scoutflo
extract_date: 2026-03-05
tags:
- k8s-deployment
- k8s-namespace
- k8s-pod
- k8s-rbac
- k8s-service
- kubernetes
- performance
- rbac
- rbacpermissiondeniederror
- security
- sts
---

---
title: RBAC Permission Denied Error - RBAC
weight: 223
categories:
  - kubernetes
  - rbac
---

# RBAC 권한 거부 오류 — RBACPermissionDeniedError-rbac

## 의미

사용자 또는 서비스 계정의 API 요청이 forbidden 또는 permission denied 오류로 거부됩니다(KubeAPIErrorsHigh 알림 발생 가능). 원인으로는 RBAC 역할과 바인딩이 대상 리소스에 필요한 권한을 부여하지 않기 때문입니다. API 요청이 403 상태 코드를 반환하고, Role 또는 RoleBinding 리소스에 권한 누락이 표시될 수 있으며, Pod 로그에 permission denied 오류가 표시될 수 있습니다. 이는 RBAC 구성 오류, 권한 누락, 역할 바인딩 문제로 인해 클러스터 리소스에 대한 인가된 접근이 차단되는 것을 나타냅니다. Kubernetes API를 사용하는 애플리케이션에서 오류가 발생할 수 있습니다.

## 영향

API 작업 permission denied 실패, Pod 필요 리소스 접근 불가, 컨트롤러 상태 조정 불가, 배포 실패, 애플리케이션 필요 작업 수행 불가, 클러스터 작업 차단, KubeAPIErrorsHigh 알림 발생 가능, 로그에 forbidden 오류 발생, permission denied 오류 발생, RBAC 검증 실패로 작업 차단. API 요청이 무기한 403 상태 코드 반환. Role 또는 RoleBinding 리소스에 권한 누락 표시 가능. Kubernetes API를 사용하는 애플리케이션에서 오류나 성능 저하 발생 가능. 클러스터 작업이 차단됩니다.

## 플레이북

1. `kubectl auth can-i <verb> <resource> -n <namespace> --as=system:serviceaccount:<namespace>:<sa-name>`으로 실패하는 정확한 권한을 테스트하여 어떤 특정 액션이 거부되는지 확인합니다.

2. `kubectl auth can-i --list -n <namespace> --as=system:serviceaccount:<namespace>:<sa-name>`으로 영향받는 ID의 모든 권한을 나열하여 부여된 권한을 확인하고 갭을 식별합니다.

3. `kubectl get rolebindings -n <namespace> -o yaml | grep -B5 -A10 "<sa-name>"`으로 서비스 계정에 대한 RoleBinding이 존재하는지 확인하여 관련 바인딩을 찾습니다.

4. `kubectl get clusterrolebindings -o yaml | grep -B5 -A10 "<sa-name>"`으로 ClusterRoleBinding을 확인하여 클러스터 전체 권한 부여를 확인합니다.

5. 바인딩이 존재하면 `kubectl describe role <role-name> -n <namespace>` 또는 `kubectl describe clusterrole <role-name>`으로 참조된 역할을 설명하여 부여된 권한을 확인합니다.

6. `kubectl get validatingwebhookconfigurations,mutatingwebhookconfigurations`로 요청을 차단할 수 있는 어드미션 웹훅을 확인하고 규칙을 검토합니다.

7. `kubectl logs -n kube-system -l component=kube-apiserver --tail=100 | grep -i "forbidden\|denied"`로 API 서버 로그에서 권한 결정을 확인하여 정확한 거부 사유를 식별합니다.

## 진단

1. permission denied 오류 발생 타임스탬프(Pod 로그 또는 API 서버 로그)와 RoleBinding 또는 ClusterRoleBinding 변경 타임스탬프를 비교하고, 역할 바인딩 수정 1시간 이내에 오류가 시작되었는지 확인합니다.

2. permission denied 오류 타임스탬프와 서비스 계정 변경 타임스탬프를 비교하고, 서비스 계정 수정과 동시에 오류가 상관관계가 있는지 확인합니다.

3. permission denied 오류 타임스탬프와 배포 또는 구성 변경 타임스탬프를 비교하고, 배포 변경 1시간 이내에 오류가 시작되었는지 확인합니다.

4. permission denied 오류 타임스탬프와 클러스터 업그레이드 또는 유지보수 기간 타임스탬프를 비교하고, 인프라 변경 1시간 이내에 오류가 상관관계가 있는지 확인합니다.

5. permission denied 오류 타임스탬프와 사용자 또는 서비스 계정 변경 타임스탬프를 비교하고, 계정 수정과 오류가 상관관계가 있는지 확인합니다.

6. permission denied 오류 타임스탬프와 네임스페이스 변경 타임스탬프, 리소스 생성 타임스탬프, 어드미션 웹훅 차단 타임스탬프를 비교하고, 네임스페이스 또는 웹훅 변경과 동시에 오류가 상관관계가 있는지 확인합니다.

**지정된 시간 범위 내에서 상관관계가 발견되지 않는 경우**: 검색 범위를 확장하고(1시간→2시간), 누락된 권한에 대한 RBAC 역할 정의를 검토하고, 클러스터 역할을 오버라이드할 수 있는 네임스페이스 수준 역할 바인딩을 확인하고, 차단 결정에 대한 어드미션 웹훅 로그를 조사하고, 서비스 계정 토큰이 유효한지 확인하고, 역할 집계 문제를 확인하고, 상세한 권한 확인을 위한 RBAC 감사 로그를 검토합니다. Permission denied 오류는 단일 변경 이벤트에서 즉시 보이지 않는 누적된 권한 변경이나 역할 바인딩 충돌로 인해 발생할 수 있습니다.
