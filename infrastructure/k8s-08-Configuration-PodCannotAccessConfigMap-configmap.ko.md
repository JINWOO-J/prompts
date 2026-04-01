---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/08-Configuration/PodCannotAccessConfigMap-configmap.md)'
role: Kubernetes SRE
origin: scoutflo
extract_date: 2026-03-05
tags:
- configmap
- configuration
- infrastructure
- k8s-configmap
- k8s-namespace
- k8s-pod
- k8s-rbac
- k8s-service
- kubernetes
- podcannotaccessconfigmap
- sts
---

---
title: Pod Cannot Access ConfigMap - Pod의 ConfigMap 접근 불가
weight: 238
categories:
  - kubernetes
  - configmap
---

# PodCannotAccessConfigMap-configmap

## 의미

Pod가 ConfigMap 데이터에 접근할 수 없습니다(Pod 관련 알림 트리거). ConfigMap이 존재하지 않거나, ConfigMap 참조가 잘못되었거나, Pod의 namespace가 ConfigMap namespace와 일치하지 않거나, RBAC 권한이 접근을 차단하는 것이 원인입니다.

## 영향

Pod 시작 불가, 애플리케이션이 구성 읽기 실패, ConfigMap 마운트 실패, 환경 변수 미설정, Pod가 CrashLoopBackOff 또는 Pending 상태 진입, KubePodPending 알림 발생 가능, 애플리케이션 구성 누락, 필수 구성 데이터 없이 서비스 시작 불가. Pod가 CrashLoopBackOff 또는 Pending 상태로 무기한 유지되며, ConfigMap 의존성 누락으로 컨테이너 초기화가 차단될 수 있습니다.

## 플레이북

1. namespace <namespace>에서 Pod <pod-name>을 describe하여 Pod 볼륨 구성과 컨테이너 볼륨 마운트 또는 환경 변수 소스를 확인하고 어떤 ConfigMap이 참조되는지 식별합니다 - Events 섹션에서 특정 ConfigMap 이름과 함께 "FailedMount"를 확인합니다.

2. namespace <namespace>에서 Pod <pod-name>의 이벤트를 타임스탬프 순으로 조회하여 ConfigMap 관련 이벤트 순서를 확인합니다. FailedMount 등의 reason이나 ConfigMap 접근 실패를 나타내는 메시지에 집중합니다.

3. namespace <namespace>에서 ConfigMap <configmap-name>을 조회하고 동일 namespace에 존재하는지 확인하거나 해당되는 경우 cross-namespace 접근을 검증합니다.

4. namespace <namespace>에서 Pod <pod-name> 상태를 확인하고 컨테이너 대기 상태 reason과 message 필드를 확인하여 ConfigMap 접근 오류를 식별합니다.

5. Pod의 서비스 계정 <service-account-name>이 namespace <namespace>에서 ConfigMap에 접근할 권한이 있는지 확인하여 RBAC 권한을 검증합니다.

6. namespace <namespace>에서 Deployment <deployment-name>을 조회하고 Pod 템플릿의 ConfigMap 참조를 검토하여 구성이 올바른지 확인합니다.

## 진단

1. 플레이북의 Pod 이벤트를 분석하여 특정 ConfigMap 접근 오류를 식별합니다. "configmap not found"와 함께 "FailedMount"를 보여주는 이벤트는 ConfigMap이 존재하지 않음을 나타냅니다. "forbidden"을 보여주는 이벤트는 RBAC 권한 문제를 나타냅니다. "invalid key"를 보여주는 이벤트는 키 참조 문제를 나타냅니다.

2. 이벤트가 ConfigMap 미발견을 나타내면, 플레이북 조회 결과를 사용하여 ConfigMap 존재 여부를 확인합니다. Pod spec의 ConfigMap 이름이 정확히 일치하는지(대소문자 구분) 확인하고 Pod와 동일한 namespace에 존재하는지 확인합니다.

3. 이벤트가 RBAC 권한 문제를 나타내면, 플레이북 RBAC 검증 결과를 사용하여 서비스 계정에 ConfigMap에 대한 "get" 권한이 있는지 확인합니다. Role 또는 RoleBinding이 최근에 수정되었거나 서비스 계정에 대해 누락되었는지 확인합니다.

4. 이벤트가 namespace 불일치를 나타내면, Pod의 namespace와 ConfigMap의 예상 namespace를 비교합니다. ConfigMap은 참조하는 Pod와 동일한 namespace에 존재해야 합니다(cross-namespace 접근은 기본적으로 지원되지 않음).

5. 이벤트가 키 참조 오류를 나타내면, volumeMounts items 또는 env valueFrom에서 참조된 키를 ConfigMap 데이터의 실제 키와 비교합니다. 대소문자 구분을 포함하여 키 이름이 정확히 일치하는지 확인합니다.

6. 이벤트가 불확실하면, 이벤트 타임스탬프를 최근 Deployment 또는 ConfigMap 변경과 비교합니다. ConfigMap 참조가 수정되었는지, ConfigMap 데이터가 호환되지 않는 키로 업데이트되었는지, Pod 템플릿이 변경되었는지 확인합니다.

**이벤트에서 명확한 원인이 식별되지 않는 경우**: ConfigMap 데이터가 비어있지 않은지 확인하고, ConfigMap이 최근에 다른 키로 재생성되었는지 확인하고, admission webhook이 ConfigMap 접근을 차단하는지 조사하고, 마운트 경로가 다른 볼륨 마운트와 충돌하는지 검토합니다.
