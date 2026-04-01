---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/12-Namespaces/CannotDeleteNamespace-namespace.md)'
role: Kubernetes SRE
origin: scoutflo
extract_date: 2026-03-05
tags:
- cannotdeletenamespace
- infrastructure
- k8s-namespace
- kubernetes
- namespace
- namespaces
---

---
title: Cannot Delete Namespace - Namespace 삭제 불가
weight: 254
categories:
  - kubernetes
  - namespace
---

# CannotDeleteNamespace-namespace

## 의미

Namespace를 삭제할 수 없습니다(Namespace 관련 알림 트리거). 리소스의 finalizer가 삭제를 방해하거나, 커스텀 리소스 컨트롤러가 finalizer를 처리하지 않거나, finalizer가 있는 리소스를 정리할 수 없는 것이 원인입니다.

## 영향

Namespace가 Terminating 상태 유지, Namespace 정리 차단, 리소스가 할당된 상태 유지, finalizer가 Namespace 삭제 방해, KubeNamespaceTerminating 알림 발생 가능, Namespace 상태가 무기한 Terminating 표시, 클러스터 리소스 관리 저하, 동일 이름의 새 Namespace 생성 불가. Namespace가 무기한 Terminating 상태로 표시되며, 애플리케이션이 리소스 할당 문제를 경험할 수 있습니다.

## 플레이북

1. Namespace `<namespace-name>`을 describe하여 Namespace 삭제 타임스탬프, finalizer, 상태를 확인하고 Terminating 상태를 확인하며 어떤 finalizer가 존재하는지(kubernetes finalizer 또는 커스텀 finalizer) 식별합니다.
2. Namespace `<namespace-name>`의 이벤트를 타임스탬프 순으로 조회하여 삭제 관련 이벤트와 finalizer 처리 실패를 식별합니다.
3. Namespace `<namespace-name>`의 모든 리소스를 나열하여 삭제를 방해하는 finalizer가 있는 리소스를 식별합니다.
4. API 서버 로그에서 finalizer 처리 타임아웃 또는 오류를 검토하여 API 서버 finalizer 처리를 확인합니다.
5. finalizer를 담당하는 커스텀 리소스 컨트롤러 또는 Operator를 확인하고 컨트롤러 Pod 상태를 확인하여 실행 중이고 finalizer를 올바르게 처리하는지 검증합니다.
6. CustomResourceDefinition 객체를 조회하고 finalizer 처리 컨트롤러가 사용 가능하고 정상 작동하는지 확인합니다.
7. finalizer가 있는 리소스를 삭제할 수 있는지 또는 finalizer 컨트롤러에 문제가 있는지 컨트롤러 로그를 확인하여 검증합니다.

## 진단

1. 플레이북의 Namespace 상태와 finalizer를 분석하여 삭제 차단 요인을 식별합니다. metadata.finalizers를 확인하여 Namespace에 어떤 finalizer가 남아있는지 확인합니다. 모든 finalizer가 제거될 때까지 Namespace를 삭제할 수 없습니다.

2. Namespace에 finalizer가 있는 남은 리소스가 있으면, 플레이북에서 해당 리소스를 식별합니다. Namespace를 삭제하기 전에 리소스를 삭제해야 합니다. finalizer가 있는 각 리소스는 삭제가 완료되기 전에 컨트롤러가 finalizer를 처리해야 합니다.

3. 이벤트가 finalizer 컨트롤러 실패 또는 타임아웃을 나타내면, 고착된 finalizer를 담당하는 컨트롤러를 식별합니다. 일반적인 컨트롤러: Istio, Prometheus Operator, cert-manager, 커스텀 Operator. 컨트롤러가 실행 중이고 정상인지 확인합니다.

4. 담당 컨트롤러가 삭제되었거나 실행되지 않으면, finalizer가 자동으로 처리되지 않습니다. 영향받는 리소스에서 finalizer를 수동으로 제거해야 합니다.

5. 이벤트가 finalizer 처리 중 API 서버 오류를 나타내면, API 서버 상태와 연결을 확인합니다. finalizer 처리에는 성공적인 API 서버 통신이 필요합니다.

6. 리소스가 삭제된 CustomResourceDefinition을 참조하면, 해당 리소스는 고아가 되어 정상적으로 처리할 수 없습니다. Namespace의 리소스가 사용하는 CRD가 삭제되어 작동하는 API 없이 리소스가 남아있는지 확인합니다.

7. 모든 보이는 리소스가 삭제되었지만 Namespace가 여전히 Terminating이면, Namespace 수준의 "kubernetes" finalizer가 고착되었을 수 있습니다. kube-controller-manager가 정상이고 Namespace 삭제를 처리할 수 있는지 확인합니다. controller-manager 로그에서 Namespace 컨트롤러 오류를 확인합니다.
