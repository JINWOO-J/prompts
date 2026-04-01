---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/06-Storage/PodCannotAccessPersistentVolume-storage.md)'
role: Kubernetes SRE
origin: scoutflo
extract_date: 2026-03-05
tags:
- database
- infrastructure
- k8s-namespace
- k8s-pod
- k8s-pvc
- kubernetes
- podcannotaccesspersistentvolume
- storage
---

---
title: Pod Cannot Access PersistentVolume - Pod의 PV 접근 불가
weight: 260
categories:
  - kubernetes
  - storage
---

# PodCannotAccessPersistentVolume-storage

## 의미

Pod가 PersistentVolume에 접근할 수 없습니다(KubePodPending 또는 스토리지 관련 알림 트리거). PersistentVolumeClaim이 바인딩되지 않았거나, 볼륨 연결 불가, 볼륨 마운트 실패, StorageClass 잘못된 구성, 스토리지 백엔드 사용 불가가 원인입니다.

## 영향

Pod 시작 불가, 영구 스토리지 사용 불가, 볼륨 마운트 실패, Pod가 Pending 또는 ContainerCreating 상태 유지, KubePodPending 알림 발생, PersistentVolumeClaim 바인딩 미완료, 애플리케이션이 데이터에 접근 불가, 스테이트풀 워크로드 시작 실패, 데이터베이스 Pod가 데이터 볼륨 마운트 불가. Pod가 Pending 또는 ContainerCreating 상태로 무기한 유지되며, PersistentVolumeClaim 바인딩 실패로 Pod 생성이 차단될 수 있고, 애플리케이션이 데이터에 접근하지 못해 오류를 표시할 수 있습니다.

## 플레이북

1. namespace <namespace>에서 PersistentVolumeClaim <pvc-name>을 describe하여 PVC 상태, phase, 조건을 확인하고 PersistentVolume에 바인딩되어 있는지 검증합니다.

2. namespace <namespace>에서 PersistentVolumeClaim <pvc-name>의 이벤트를 타임스탬프 순으로 조회하여 바인딩 실패 또는 프로비저닝 문제를 식별합니다.

3. namespace <namespace>에서 Pod <pod-name>을 describe하여 Pod 볼륨 구성을 확인하고 어떤 PersistentVolumeClaim이 참조되는지 식별합니다.

4. namespace <namespace>에서 Pod <pod-name>의 이벤트를 타임스탬프 순으로 조회하여 FailedMount, FailedAttachVolume, 볼륨 연결 실패를 식별합니다.

5. PersistentVolume <pv-name>을 describe하여 바인딩된 볼륨 상태, phase, access mode를 확인하고 볼륨 가용성을 검증합니다.

6. PVC가 참조하는 StorageClass를 describe하고 존재하며 프로비저너가 사용 가능한지 확인합니다.

7. Pod가 스케줄링된 노드를 describe하여 볼륨 연결 상태를 확인하고 볼륨이 노드에 연결 가능한지 검증합니다.

## 진단

1. 플레이북 4단계의 Pod 이벤트를 분석하여 특정 볼륨 접근 실패 유형을 식별합니다. 이벤트 reason이 실패 지점을 나타냅니다:
   - "FailedMount" - 볼륨이 존재하지만 마운트 불가 (권한, 파일시스템, 노드 문제)
   - "FailedAttachVolume" - 볼륨을 노드에 연결 불가 (CSI 드라이버 또는 백엔드 문제)
   - 볼륨 관련 메시지와 함께 "FailedScheduling" - 볼륨 요구사항을 충족하는 노드 없음

2. 이벤트에 FailedMount 또는 FailedAttachVolume이 표시되면, 플레이북 1단계의 PVC 상태를 확인합니다. PVC phase가 "Bound"가 아니면 볼륨 바인딩이 근본 원인입니다:
   - PVC가 Pending이면, PVC Pending 진단을 따름 (6단계의 StorageClass 확인)
   - PVC가 Lost이면, 기반 PV가 더 이상 사용 불가 (5단계의 PV 확인)

3. PVC가 Bound이지만 Pod에 여전히 볼륨 오류가 표시되면, 플레이북 2단계의 PVC 이벤트를 확인합니다. 이벤트에 다음이 표시될 수 있습니다:
   - "WaitForFirstConsumer" - 특정 바인딩 모드의 정상 동작, Pod 스케줄링이 바인딩을 트리거
   - "ProvisioningFailed" - 스토리지 백엔드가 볼륨을 생성할 수 없음
   - Access mode 충돌 - PV access mode가 Pod 요구사항과 일치하지 않음

4. 1-5단계에서 PVC와 PV가 정상으로 보이면, 플레이북 7단계의 노드 상태를 확인합니다. 노드에 볼륨 연결 제한 도달 또는 스토리지 관련 조건이 표시되면, 해당 노드에 더 이상 볼륨을 연결할 수 없습니다.

5. 6단계의 StorageClass가 누락되었거나 잘못 구성된 경우, StorageClass가 수정/삭제된 시점을 Pod가 볼륨 접근에 실패하기 시작한 시점과 상관 분석합니다.

6. 모든 Kubernetes 리소스가 올바른 것으로 보이면, 스토리지 백엔드 수준의 문제입니다. 5단계의 PV volumeHandle 또는 스토리지 경로가 여전히 존재하고 스케줄링된 노드에서 접근 가능한지 확인합니다.

**지정된 시간 범위 내에서 상관관계를 찾을 수 없는 경우**: 검색 범위를 확장하고(10분 → 30분, 30분 → 1시간, 1시간 → 2시간), 스토리지 플러그인 로그에서 점진적인 볼륨 프로비저닝 문제를 검토하고, 간헐적인 스토리지 백엔드 연결 문제를 확인하고, StorageClass 구성이 시간이 지남에 따라 변경되었는지 조사하고, 볼륨 연결 제한이 점진적으로 누적되었는지 확인하고, 발생했을 수 있는 스토리지 프로바이더 쿼터 또는 용량 문제를 확인합니다. 볼륨 접근 실패는 즉각적인 변경이 아닌 점진적인 스토리지 인프라 저하로 인해 발생할 수 있습니다.
