---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/08-Configuration/ConfigMapNotFound-configmap.md)'
role: Kubernetes SRE
origin: scoutflo
extract_date: 2026-03-05
tags:
- configmap
- configmapnotfound
- configuration
- infrastructure
- k8s-configmap
- k8s-deployment
- k8s-namespace
- k8s-pod
- k8s-service
- kubernetes
- sts
---

---
title: ConfigMap Not Found - ConfigMap 미발견
weight: 209
categories:
  - kubernetes
  - configmap
---

# ConfigMapNotFound-configmap

## 의미

Pod 또는 Deployment에서 참조하는 ConfigMap이 존재하지 않습니다(KubePodPending 알림 트리거). ConfigMap이 생성되지 않았거나, 삭제되었거나, 다른 namespace에 있거나, 참조 이름이 잘못된 것이 원인입니다.

## 영향

Pod 시작 불가, Deployment가 Pod 생성 실패, ConfigMap 참조 실패, Pod가 Pending 상태 유지, KubePodPending 알림 발생, 애플리케이션이 구성에 접근 불가, 환경 변수 미설정, 볼륨 마운트 실패, 필수 구성 없이 서비스 시작 불가. Pod가 Pending 또는 CrashLoopBackOff 상태로 무기한 유지되며, ConfigMap 의존성 누락으로 컨테이너 초기화가 차단될 수 있습니다.

## 플레이북

1. namespace <namespace>에서 Pod <pod-name>을 describe하여 Pod 볼륨 구성과 환경 변수 소스를 확인하고 어떤 ConfigMap이 참조되는지 식별합니다 - Events 섹션에서 누락된 특정 ConfigMap 이름과 함께 "FailedMount"를 확인합니다.

2. namespace <namespace>에서 Pod <pod-name>의 이벤트를 타임스탬프 순으로 조회하여 ConfigMap 관련 실패 순서를 확인합니다. FailedMount 등의 reason이나 ConfigMap 미발견을 나타내는 메시지에 집중합니다.

3. namespace <namespace>의 ConfigMap을 나열하고 참조된 ConfigMap이 존재하는지 확인합니다.

4. namespace <namespace>에서 Deployment <deployment-name>을 조회하고 Pod 템플릿의 ConfigMap 참조를 검토하여 ConfigMap 이름이 올바른지 확인합니다.

5. namespace <namespace>에서 Pod <pod-name> 상태를 확인하고 컨테이너 대기 상태 reason과 message 필드를 확인하여 ConfigMap 미발견 오류를 식별합니다.

6. 모든 namespace에서 ConfigMap을 나열하고 <configmap-name>을 검색하여 ConfigMap이 다른 namespace에 존재하는지 확인하고 cross-namespace 접근이 필요하고 구성되어 있는지 확인합니다.

## 진단

1. 플레이북의 Pod 이벤트를 분석하여 정확한 ConfigMap 미발견 오류를 식별합니다. "configmap not found"와 함께 "FailedMount"를 보여주는 이벤트는 ConfigMap이 존재하지 않음을 확인합니다. 오류 메시지에 언급된 특정 ConfigMap 이름을 기록합니다.

2. 이벤트가 ConfigMap 미발견을 확인하면, 플레이북 결과를 사용하여 ConfigMap이 클러스터에 존재하는지 확인합니다. ConfigMap 목록에 Pod의 namespace에 일치하는 ConfigMap이 없으면, ConfigMap이 생성되지 않았거나 삭제된 것입니다.

3. ConfigMap이 다른 namespace에 존재하면, Pod의 namespace와 ConfigMap이 발견된 위치를 비교합니다. ConfigMap은 namespace 간 접근이 불가하므로 Pod와 동일한 namespace에 생성해야 합니다.

4. ConfigMap 이름이 올바른 것으로 보이면, 오타 또는 대소문자 구분 문제를 확인합니다. Pod spec의 정확한 ConfigMap 이름(플레이북 describe 출력)을 namespace의 실제 ConfigMap 이름과 비교합니다.

5. ConfigMap이 최근에 삭제된 경우, 이벤트 타임스탬프를 검토하여 ConfigMap이 사용 불가해진 시점을 파악합니다. 배포 또는 정리 프로세스가 Pod가 여전히 참조하는 동안 ConfigMap을 제거했는지 확인합니다.

6. 이벤트가 ConfigMap 참조가 최근에 변경되었음을 나타내면, 플레이북 출력의 Deployment 구성을 검토합니다. 최근 롤아웃이 잘못된 ConfigMap 이름을 도입했는지 또는 ConfigMap 의존성이 배포의 일부로 생성되지 않았는지 확인합니다.

**이벤트에서 명확한 원인이 식별되지 않는 경우**: ConfigMap 생성이 실패했을 수 있는 Helm, Kustomize, 또는 Operator에 의해 관리되는지 확인하고, ConfigMap이 아직 완료되지 않은 init 프로세스에 의해 생성되어야 하는지 확인하고, ConfigMap이 불완전한 namespace 마이그레이션 또는 클러스터 복원의 일부였는지 조사합니다.
