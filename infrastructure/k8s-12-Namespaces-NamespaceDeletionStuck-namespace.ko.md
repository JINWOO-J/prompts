---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/12-Namespaces/NamespaceDeletionStuck-namespace.md)'
role: Kubernetes SRE
origin: scoutflo
extract_date: 2026-03-05
tags:
- infrastructure
- k8s-namespace
- kubernetes
- namespace
- namespacedeletionstuck
- namespaces
---

---
title: Namespace Deletion Stuck - Namespace 삭제 고착
weight: 228
categories:
  - kubernetes
  - namespace
---

# NamespaceDeletionStuck-namespace

## 의미

Namespace가 Terminating 상태에 고착되어 있습니다(Namespace 관련 알림 트리거). finalizer가 있는 리소스를 삭제할 수 없거나, 커스텀 리소스 컨트롤러가 finalizer를 처리하지 않거나, API 서버가 리소스 정리를 완료할 수 없는 것이 원인입니다.

## 영향

Namespace가 무기한 Terminating 상태 유지, Namespace 정리 차단, 리소스가 할당된 상태 유지, finalizer가 리소스 삭제 방해, KubeNamespaceTerminating 알림 발생 가능, Namespace 상태가 Terminating 표시, 클러스터 리소스 관리 저하, 동일 이름의 새 Namespace 생성 불가. Namespace가 무기한 Terminating 상태로 표시되며, 애플리케이션이 리소스 할당 문제를 경험할 수 있습니다.

## 플레이북

1. Namespace `<namespace-name>`을 describe하여 Namespace 삭제 타임스탬프, finalizer, 상태를 확인하고 Terminating 상태를 확인하며 삭제를 방해하는 finalizer를 식별합니다.
2. Namespace `<namespace-name>`의 이벤트를 타임스탬프 순으로 조회하여 삭제 관련 이벤트와 finalizer 처리 실패를 식별합니다.
3. Namespace `<namespace-name>`의 모든 리소스를 나열하고 남아있으며 finalizer가 있는 리소스를 식별합니다.
4. finalizer를 담당하는 커스텀 리소스 컨트롤러 또는 Operator를 확인하고 실행 중이며 finalizer를 처리할 수 있는지 검증합니다.
5. CustomResourceDefinition 객체를 조회하고 finalizer 처리가 올바르게 구성되어 있는지 확인합니다.
6. API 서버 연결과 성능을 확인하여 finalizer 처리가 완료될 수 있는지 확인합니다.

## 진단

1. 플레이북의 Namespace 이벤트와 finalizer를 분석하여 삭제를 차단하는 요인을 식별합니다. Namespace의 metadata.finalizers 필드를 확인하여 어떤 finalizer가 남아있는지 확인합니다. 일반적인 finalizer: "kubernetes"(내장) 및 Operator의 커스텀 finalizer.

2. kubernetes finalizer가 남아있으면, Namespace 내에 먼저 삭제해야 할 리소스가 여전히 존재합니다. 플레이북에서 Namespace의 모든 리소스를 나열하여 남은 리소스를 식별합니다. 정리를 차단할 수 있는 자체 finalizer가 있는 리소스에 집중합니다.

3. 커스텀 리소스 finalizer가 남아있으면(예: Istio, Prometheus, 커스텀 컨트롤러의 Operator), 해당 finalizer를 담당하는 컨트롤러가 실행 중이고 정상인지 확인합니다. 리소스보다 먼저 컨트롤러가 삭제된 경우 finalizer가 처리되지 않습니다.

4. finalizer가 있는 리소스가 존재하지만 컨트롤러가 누락되거나 삭제된 경우, finalizer를 수동으로 제거해야 합니다. 플레이북 출력에서 특정 리소스와 finalizer를 식별합니다.

5. 이벤트가 finalizer 처리 중 API 서버 오류 또는 타임아웃을 나타내면, API 서버 상태와 연결을 확인합니다. finalizer 처리에는 API 서버가 리소스 메타데이터를 업데이트해야 합니다.

6. Namespace에 삭제된 CustomResourceDefinition이 포함되어 있으면, 해당 유형의 리소스는 고아가 되어 정상적으로 삭제할 수 없습니다. API 그룹이 더 이상 존재하지 않는 리소스를 확인합니다.

7. 모든 리소스가 삭제된 것으로 보이지만 Namespace가 여전히 Terminating이면, Namespace 수준의 kubernetes finalizer가 고착되었을 수 있습니다. 이는 Namespace 컨트롤러가 정리를 완료할 수 없을 때 발생할 수 있습니다. kube-controller-manager 상태를 확인하고 로그에서 Namespace 컨트롤러 오류를 확인합니다.
