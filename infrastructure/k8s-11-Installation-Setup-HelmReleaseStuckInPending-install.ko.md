---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/11-Installation-Setup/HelmReleaseStuckInPending-install.md)'
role: Kubernetes SRE
origin: scoutflo
extract_date: 2026-03-05
tags:
- helmreleasestuckinpending
- infrastructure
- install
- installation
- k8s-deployment
- k8s-helm
- k8s-namespace
- k8s-pod
- k8s-rbac
- k8s-service
- kubernetes
- setup
---

---
title: Helm Release Stuck in PENDING_INSTALL - Helm 릴리스 설치 보류 고착
weight: 244
categories:
  - kubernetes
  - workload
---

# HelmReleaseStuckInPending-install

## 의미

Helm 릴리스가 PENDING_INSTALL 상태에 고착되어 있습니다. 하나 이상의 차트 리소스가 클러스터에서 성공적으로 생성, 검증, 스케줄링될 수 없는 것이 원인입니다.

## 영향

Helm 릴리스 설치 완료 불가, 애플리케이션 배포 실패, 리소스가 Pending 상태 유지, 배포 미완료, 서비스 시작 불가, Helm 설치 중단, 차트 리소스 생성 실패, 설치 진행 정체.

## 플레이북

1. namespace `<namespace>`에서 릴리스 `<release-name>`의 Helm 릴리스 상태를 조회하여 설치 상태를 확인합니다.
2. namespace `<namespace>`의 이벤트를 타임스탬프 순으로 조회하여 Helm 릴리스 실패와 리소스 생성 오류를 식별합니다.
3. namespace `<namespace>`의 실패하는 Pod 로그를 조회하고 오류 패턴을 필터링합니다.
4. Helm 차트 구성을 확인하여 Helm 차트 값과 템플릿을 검증합니다.
5. namespace `<namespace>`의 Pod를 조회하여 리소스 제약을 확인합니다.
6. namespace `<namespace>`의 ResourceQuota와 RBAC 권한을 조회합니다.

## 진단

플레이북 섹션에서 수집한 Helm 릴리스 상태, Namespace 이벤트, Pod 상태를 분석하는 것으로 시작합니다.

**이벤트에 RBAC 또는 권한 오류와 함께 FailedCreate가 표시되는 경우:**
- 권한 부족으로 Helm이 리소스를 생성할 수 없습니다. Helm을 실행하는 서비스 계정 또는 사용자에게 차트의 모든 리소스 유형에 대한 ClusterRole 또는 Role 바인딩이 있는지 확인합니다.

**이벤트에 차트가 생성한 Pod의 FailedScheduling이 표시되는 경우:**
- 리소스 제약 또는 노드 셀렉터로 Pod를 스케줄링할 수 없습니다. Pod Pending 이유를 확인합니다. `Insufficient cpu` 또는 `Insufficient memory`이면 클러스터 용량을 추가하거나 리소스 요청을 줄입니다.

**이벤트에 admission webhook 거부 또는 유효성 검사 오류가 표시되는 경우:**
- Admission controller가 리소스 생성을 차단하고 있습니다. 이벤트 메시지에서 어떤 webhook이 요청을 거부했는지 확인합니다.

**이벤트에 ResourceQuota 초과가 표시되는 경우:**
- Namespace 쿼터가 리소스 생성을 차단합니다. `kubectl get resourcequota -n <namespace>`를 확인합니다. 쿼터 제한을 증가시키거나 차트 리소스 요구사항을 줄입니다.

**Helm 상태에 "another operation in progress"가 표시되는 경우:**
- 이전 Helm 작업이 깨끗하게 완료되지 않았습니다. `helm history <release> -n <namespace>`를 실행하여 고착된 릴리스를 확인합니다. `helm rollback`으로 이전 리비전으로 롤백하거나 적절한 경우 `helm uninstall`을 사용합니다.

**차트 리소스는 생성되었지만 Deployment Pod가 시작되지 않는 경우:**
- 차트는 설치되었지만 애플리케이션 Pod에 문제가 있습니다. 컨테이너 시작 오류에 대한 Pod describe 출력을 확인합니다. 이는 Helm 문제가 아닌 애플리케이션 문제입니다.

**명확한 원인이 식별되지 않는 경우:** `helm install --dry-run --debug`를 실행하여 적용하지 않고 차트 템플릿을 검증합니다. 템플릿 렌더링 오류 또는 잘못된 리소스 사양을 확인합니다.
