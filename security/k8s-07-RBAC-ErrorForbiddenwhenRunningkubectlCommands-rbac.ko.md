---
category: security
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/07-RBAC/ErrorForbiddenwhenRunningkubectlCommands-rbac.md)'
role: Kubernetes SRE
origin: scoutflo
extract_date: 2026-03-05
tags:
- errorforbiddenwhenrunningkubectlcommands
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
title: Error Forbidden when Running kubectl Commands - RBAC
weight: 261
categories:
  - kubernetes
  - rbac
---

# kubectl 명령 실행 시 Forbidden 오류 — ErrorForbiddenwhenRunningkubectlCommands-rbac

## 의미

kubectl 명령이 Forbidden(403) 오류를 반환합니다(KubeAPIErrorsHigh 알림 발생). 원인으로는 사용자 또는 서비스 계정에 필요한 RBAC 권한이 없거나, Role 또는 RoleBinding 리소스가 누락되었거나 잘못되었거나, 권한이 취소된 경우입니다. API 요청이 403 상태 코드를 반환하고, Role 또는 RoleBinding 리소스에 권한 누락이 표시될 수 있으며, 인가 실패로 리소스 관리가 차단됩니다. 이는 인증 및 인가 플레인에 영향을 미치며 클러스터 작업을 방해합니다. 일반적으로 RBAC 권한 누락이나 잘못된 Role/RoleBinding 구성이 원인이며, Kubernetes API를 사용하는 애플리케이션에서 오류가 발생할 수 있습니다.

## 영향

kubectl 명령 Forbidden 오류 실패, 클러스터 작업 차단, 사용자 필요 작업 수행 불가, KubeAPIErrorsHigh 알림 발생, API 서버 403 상태 코드 반환, 인가 실패로 리소스 관리 차단, 서비스 계정 필요 리소스 접근 불가, 권한 거부로 애플리케이션 실패. API 요청이 무기한 403 상태 코드 반환. Role 또는 RoleBinding 리소스에 권한 누락 표시 가능. Kubernetes API를 사용하는 애플리케이션에서 오류나 성능 저하 발생 가능. 클러스터 작업이 차단됩니다.

## 플레이북

1. `kubectl auth can-i <verb> <resource> -n <namespace>`로 실패한 정확한 명령을 테스트하여 어떤 특정 권한이 거부되는지 확인합니다 - 이것이 즉시 권한 갭을 식별합니다.

2. `kubectl auth whoami`(K8s 1.27+) 또는 `kubectl config current-context`와 `kubectl config view --minify -o jsonpath='{.contexts[0].context.user}'`로 현재 ID를 확인하여 어떤 사용자 또는 서비스 계정이 사용되고 있는지 검증합니다.

3. `kubectl auth can-i --list -n <namespace>`로 현재 모든 권한을 나열하여 무엇을 할 수 있는지 확인하고 누락된 항목을 식별합니다.

4. `kubectl get rolebindings -n <namespace> -o yaml | grep -A5 "<your-username-or-sa>"` 또는 `kubectl get clusterrolebindings -o yaml | grep -A5 "<your-username-or-sa>"`로 사용자에 대한 RoleBinding이 존재하는지 확인합니다.

5. 바인딩이 존재하면 `kubectl describe role <role-name> -n <namespace>` 또는 `kubectl describe clusterrole <role-name>`을 실행하여 역할이 부여하는 권한을 확인합니다.

6. `kubectl get events --all-namespaces --field-selector=reason=Forbidden`으로 인가 실패 관련 이벤트를 나열하여 타임스탬프와 함께 최근 권한 거부를 확인합니다.

7. 가용한 경우 `kubectl logs -n kube-system -l component=kube-apiserver --tail=100 | grep -i "403\|forbidden"`으로 API 서버 감사 로그를 확인하여 인가 결정을 검토합니다.

## 진단

1. Forbidden 오류 타임스탬프와 Role 또는 ClusterRole 수정 타임스탬프를 비교하고, Forbidden 오류 30분 이내에 권한이 제거되었는지 확인합니다.

2. Forbidden 오류 타임스탬프와 RoleBinding 또는 ClusterRoleBinding 삭제 타임스탬프를 비교하고, Forbidden 오류 30분 이내에 바인딩이 제거되었는지 확인합니다.

3. Forbidden 오류 타임스탬프와 사용자 또는 서비스 계정 수정 타임스탬프를 비교하고, Forbidden 오류 30분 이내에 계정 변경이 발생했는지 확인합니다.

4. Forbidden 오류 타임스탬프와 클러스터 업그레이드 또는 RBAC 정책 업데이트 타임스탬프를 비교하고, Forbidden 오류 1시간 이내에 권한 적용에 영향을 미치는 인프라 변경이 발생했는지 확인합니다.

5. Forbidden 오류 타임스탬프와 API 서버 구성 수정 타임스탬프를 비교하고, Forbidden 오류 30분 이내에 인가 설정이 변경되었는지 확인합니다.

6. Forbidden 오류 타임스탬프와 리소스 생성 또는 네임스페이스 생성 타임스탬프를 비교하고, Forbidden 오류 30분 이내에 새로운 권한이 필요한 새 리소스나 네임스페이스가 생성되었는지 확인합니다.

**지정된 시간 범위 내에서 상관관계가 발견되지 않는 경우**: 검색 범위를 확장하고(30분→1시간, 1시간→2시간), 점진적 권한 변경에 대한 API 서버 감사 로그를 검토하고, 간헐적 RBAC 정책 적용 문제를 확인하고, Role 또는 RoleBinding 구성이 시간이 지남에 따라 드리프트되었는지 조사하고, 권한이 점진적으로 제한되었는지 확인하고, RBAC 조회에 영향을 미치는 API 서버 또는 etcd 문제를 확인합니다. Forbidden 오류는 즉각적인 취소가 아닌 점진적인 권한 정책 변경으로 인해 발생할 수 있습니다.
