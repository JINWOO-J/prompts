---
category: security
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/07-RBAC/ServiceAccountNotFound-rbac.md)'
role: Kubernetes SRE
origin: scoutflo
extract_date: 2026-03-05
tags:
- k8s-deployment
- k8s-namespace
- k8s-pod
- k8s-rbac
- k8s-secret
- k8s-service
- kubernetes
- rbac
- security
- serviceaccountnotfound
- sts
---

---
title: Service Account Not Found - RBAC
weight: 252
categories:
  - kubernetes
  - rbac
---

# ServiceAccount 미발견 — ServiceAccountNotFound-rbac

## 의미

Pod에서 참조하는 ServiceAccount가 존재하지 않습니다(KubePodPending 알림 발생). 원인으로는 ServiceAccount가 생성되지 않았거나, 삭제되었거나, 다른 네임스페이스에 있거나, 참조 이름이 잘못된 경우입니다. Pod가 Pending 상태를 표시하고, Pod 이벤트에 ServiceAccount not found 오류가 표시되며, 컨테이너 대기 상태 사유가 ServiceAccount 접근 실패를 나타낼 수 있습니다. 이는 워크로드 플레인에 영향을 미치며 Pod 시작을 방해합니다. 일반적으로 누락된 ServiceAccount나 잘못된 참조가 원인이며, 누락된 ServiceAccount 의존성이 컨테이너 초기화를 차단할 수 있습니다.

## 영향

Pod 시작 불가, 배포의 Pod 생성 실패, ServiceAccount 참조 실패, Pod Pending 상태 유지, KubePodPending 알림 발생, Pod 인증 실패, RBAC 권한 미적용, 서비스 필요 리소스 접근 불가, ServiceAccount에서 참조하는 이미지 풀 시크릿 실패. Pod가 무기한 Pending 상태 표시. Pod 이벤트에 ServiceAccount not found 오류 표시. 누락된 ServiceAccount 의존성이 컨테이너 초기화를 차단할 수 있음. 애플리케이션이 시작할 수 없고 오류가 표시될 수 있습니다.

## 플레이북

1. 네임스페이스 <namespace>의 Pod <pod-name>을 설명하여 Pod 상태, 이벤트, 문제를 유발하는 ServiceAccount 참조를 확인합니다 - 이벤트에서 "serviceaccount not found"를 찾습니다.

2. 참조된 ServiceAccount <serviceaccount-name>이 네임스페이스 <namespace>에 존재하는지 확인합니다 - 발견되지 않으면 문제가 확인됩니다.

3. 네임스페이스 <namespace>의 Pod <pod-name>에 대한 이벤트를 조회하여 타임스탬프와 함께 ServiceAccount 관련 오류를 확인합니다.

4. ServiceAccount가 존재하면 ServiceAccount <namespace>:<sa-name>이 수행할 수 있는 액션을 확인하여 권한을 검증합니다.

5. 네임스페이스 <namespace>의 Deployment <deployment-name>을 설명하고 Pod 템플릿의 serviceAccountName 필드를 확인하여 ServiceAccount 이름이 올바르게 입력되었는지 검증합니다.

6. 네임스페이스 <namespace>의 모든 ServiceAccount를 나열하여 유사한 이름(오타)을 확인하거나 사용할 올바른 ServiceAccount를 검증합니다.

7. 교차 네임스페이스 접근이 의심되면 모든 네임스페이스에서 ServiceAccount를 나열하고 <sa-name>을 검색하여 다른 네임스페이스에 존재하는지 확인합니다.

## 진단

1. 플레이북 2단계에서 ServiceAccount가 예상 네임스페이스에 존재하는지 확인합니다. `kubectl get serviceaccount` 결과가 주요 진단 경로를 결정합니다:
   - ServiceAccount가 존재하지 않으면 2단계로 진행하여 이유를 파악합니다.
   - ServiceAccount가 존재하면 5단계로 진행하여 참조 또는 권한 문제를 확인합니다.

2. ServiceAccount가 존재하지 않으면 근본 원인을 파악합니다:
   - **ServiceAccount가 삭제됨**: Pod 실패 30분 이내에 ServiceAccount에 대한 `delete` 작업에 대한 API 서버 감사 로그나 이벤트를 확인합니다. 오퍼레이터, 컨트롤러, 수동 삭제 활동을 확인합니다.
   - **ServiceAccount가 생성되지 않음**: ServiceAccount가 Helm 차트, 오퍼레이터, 매니페스트에 의해 생성되어야 하는지 확인합니다. 배포 전제 조건과 순서를 확인합니다.
   - **ServiceAccount 생성 실패**: 실패한 ServiceAccount 생성 시도(할당량 제한, 어드미션 웹훅 거부, 검증 오류)에 대한 네임스페이스 이벤트를 검토합니다.

3. Pod 이벤트(플레이북 1단계 및 3단계)에서 "serviceaccount not found"가 확인되면 **네임스페이스 불일치**를 확인합니다:
   - 교차 네임스페이스 검색(플레이북 7단계)에서 다른 네임스페이스에 ServiceAccount가 발견되면 네임스페이스 참조 오류입니다.
   - Pod의 네임스페이스가 ServiceAccount가 존재하는 곳과 일치하는지 확인합니다 - ServiceAccount는 네임스페이스 범위이며 네임스페이스 간 참조할 수 없습니다.
   - Pod가 잘못된 네임스페이스에 배포되었거나 ServiceAccount가 잘못된 네임스페이스에 생성되었는지 확인합니다.

4. ServiceAccount 목록(플레이북 6단계)에서 유사한 이름이 확인되면 **ServiceAccount 참조 오타**를 확인합니다:
   - Deployment 스펙(플레이북 5단계)의 `serviceAccountName`을 기존 ServiceAccount 이름과 비교합니다.
   - 일반적인 오타를 확인합니다: 복수형(`serviceaccount` vs `serviceaccounts`), 대소문자 구분, 하이픈 vs 밑줄.
   - 문서나 템플릿에서의 복사-붙여넣기 오류를 확인합니다.

5. ServiceAccount가 존재하고 올바르게 참조되지만 Pod가 여전히 실패하면 **권한 또는 토큰 문제**를 확인합니다:
   - `auth can-i` 검증(플레이북 4단계)을 사용하여 ServiceAccount에 필요한 권한이 있는지 확인합니다.
   - Kubernetes 1.24+의 경우 ServiceAccount 토큰 Secret이 명시적으로 생성되었는지 확인합니다(자동 토큰 생성이 제거됨).
   - Pod가 API 접근을 필요로 할 때 ServiceAccount의 `automountServiceAccountToken`이 false로 설정되어 있는지 확인합니다.

6. ServiceAccount가 최근까지 작동했다면 **최근 변경**을 확인합니다:
   - Pod 실패 타임스탬프와 Deployment 롤아웃 타임스탬프(플레이북 5단계)를 비교하여 최근 업데이트에서 `serviceAccountName`이 변경되었는지 식별합니다.
   - 실패 1시간 이내의 네임스페이스 마이그레이션이나 클러스터 업그레이드 활동을 검토합니다.
   - GitOps나 구성 관리 도구가 최근 ServiceAccount 리소스에 영향을 미치는 변경을 동기화했는지 확인합니다.

**근본 원인이 식별되지 않는 경우**: 타임스탬프 상관관계의 검색 범위를 확장하고(30분→1시간), ServiceAccount 조회 문제에 대한 etcd 상태를 확인하고, 어드미션 컨트롤러가 ServiceAccount 생성을 차단하는지 확인하고, ServiceAccount가 생성되었지만 컨트롤러나 정리 정책에 의해 즉시 삭제되었는지 조사합니다. ServiceAccount not found 오류는 ServiceAccount가 생성되기 전에 Pod가 스케줄링되는 네임스페이스 생성 중에 일시적으로 발생할 수도 있습니다.
