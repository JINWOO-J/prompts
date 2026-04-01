---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/08-Configuration/ConfigMapTooLarge-configmap.md)'
role: Kubernetes SRE
origin: scoutflo
extract_date: 2026-03-05
tags:
- configmap
- configmaptoolarge
- configuration
- infrastructure
- k8s-configmap
- k8s-deployment
- k8s-namespace
- k8s-pod
- k8s-service
- kubernetes
---

---
title: ConfigMap Too Large - ConfigMap 크기 초과
weight: 287
categories:
  - kubernetes
  - configmap
---

# ConfigMapTooLarge-configmap

## 의미

ConfigMap이 1MB 크기 제한을 초과합니다(ConfigMap 마운트 실패로 Pod 시작 불가 시 KubePodPending 알림 트리거). 구성 데이터가 너무 크거나, 단일 ConfigMap에 여러 대용량 파일이 저장되었거나, 시간이 지남에 따라 구성이 증가한 것이 원인입니다.

## 영향

ConfigMap 생성이 유효성 검사 오류로 실패, ConfigMap 업데이트가 API 서버에 의해 거부, 애플리케이션이 구성에 접근 불가, ConfigMap에 의존하는 Pod가 시작 불가하고 Pending 상태 유지, Pod가 ConfigMap 볼륨 마운트 실패 시 KubePodPending 알림 발생, 구성 데이터 사용 불가, 필수 구성 없이 서비스 시작 불가, 배포 업데이트 실패. ConfigMap 생성 또는 업데이트가 유효성 검사 오류로 무기한 실패하며, 애플리케이션이 시작 불가하고 오류를 표시할 수 있습니다.

## 플레이북

1. namespace <namespace>에서 ConfigMap <configmap-name>을 describe하여 데이터 크기와 내용을 확인하고 1MB 제한을 초과하는지 검증합니다 - 데이터 키와 크기를 확인합니다.

2. namespace <namespace>에서 ConfigMap <configmap-name>의 이벤트를 타임스탬프 순으로 조회하여 ConfigMap 관련 이벤트 순서를 확인합니다. Failed 등의 reason이나 크기 제한 초과를 나타내는 메시지에 집중합니다.

3. namespace <namespace>에서 ConfigMap <configmap-name>을 조회하고 총 크기를 계산하여 1MB 제한에 근접하거나 초과하는지 식별합니다.

4. namespace <namespace>의 ConfigMap <configmap-name>에 다른 곳에 저장해야 할 대용량 바이너리 데이터, 파일, 구성이 포함되어 있는지 확인합니다.

5. namespace <namespace>의 Pod를 나열하고 ConfigMap 참조를 분석하여 ConfigMap이 어떻게 사용되는지 이해하고 분할 가능한지 확인합니다.

6. namespace <namespace>에서 ConfigMap <configmap-name>의 수정 이력과 resourceVersion을 확인하여 ConfigMap 크기가 시간이 지남에 따라 증가했는지 검증합니다.

## 진단

1. 플레이북의 이벤트를 분석하여 ConfigMap 크기 제한 오류를 식별합니다. "exceeds maximum size" 또는 "too large"를 보여주는 이벤트는 ConfigMap이 1MB etcd 객체 크기 제한을 초과했음을 나타냅니다. 상관 분석을 위해 정확한 오류 메시지와 타임스탬프를 기록합니다.

2. 이벤트가 생성 시 크기 제한 초과를 나타내면, 플레이북 검사에서 현재 ConfigMap 크기를 계산합니다. 가장 큰 데이터 값을 포함하는 키를 식별하고 분할하거나 외부에 저장할 수 있는지 판단합니다.

3. 이벤트가 업데이트 시 크기 제한 초과를 나타내면, 현재 ConfigMap 데이터를 최근 변경사항과 비교합니다. 총 크기를 1MB 이상으로 밀어올린 새 키 추가 또는 기존 키 확장을 식별합니다.

4. ConfigMap에 바이너리 데이터(binaryData 필드)가 포함된 경우, 이 데이터를 Secret(민감 데이터용) 또는 외부 스토리지(대용량 파일용) 등 다른 리소스 유형에 저장해야 하는지 평가합니다.

5. ConfigMap이 시간이 지남에 따라 증가한 경우, 플레이북 출력에서 ConfigMap의 resourceVersion과 수정 이력을 검토합니다. 점진적 증가 패턴을 식별하고 오래되거나 사용하지 않는 키를 제거할 수 있는지 판단합니다.

6. 이벤트가 ConfigMap 크기로 인한 Pod 마운트 실패를 나타내면, ConfigMap을 여러 개의 작은 ConfigMap으로 분할할 수 있는지 확인합니다. 전체 ConfigMap 대신 특정 키만 마운트하기 위해 subPath 마운트 사용을 고려합니다.

**이벤트에서 명확한 원인이 식별되지 않는 경우**: 구성 관리 도구(Helm, Kustomize, Operator)가 대용량 ConfigMap을 생성하는지 조사하고, ConfigMap이 구성이 아닌 일반 데이터 저장소로 사용되고 있는지 확인하고, PersistentVolume 또는 외부 구성 서비스 등 대용량 데이터를 위한 대안 스토리지 솔루션을 평가합니다.
