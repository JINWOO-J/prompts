---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/06-Storage/PVCPendingDueToStorageClassIssues-storage.md)'
role: Kubernetes SRE
origin: scoutflo
extract_date: 2026-03-05
tags:
- capacity
- database
- infrastructure
- k8s-namespace
- k8s-pod
- k8s-pvc
- kubernetes
- pvcpendingduetostorageclassissues
- storage
---

---
title: PVC Pending Due To StorageClass Issues - StorageClass 문제로 PVC Pending
weight: 274
categories:
  - kubernetes
  - storage
---

# PVCPendingDueToStorageClassIssues-storage

## 의미

PersistentVolumeClaim이 Pending phase에 머물러 있습니다(용량 관련 시 KubePersistentVolumeFillingUp 알림 트리거 가능). 참조된 StorageClass가 누락되었거나, 잘못 구성되었거나, 프로비저너가 요청된 용량과 파라미터에 대한 백업 볼륨을 생성할 수 없는 것이 원인입니다. kubectl에서 PersistentVolumeClaim 리소스가 Pending phase로 표시되며, StorageClass가 누락 또는 잘못된 구성 상태를 표시할 수 있고, kube-system namespace의 스토리지 프로비저너 Pod에 장애가 표시될 수 있습니다.

## 영향

PVC가 볼륨에 바인딩 불가, 영구 스토리지가 필요한 Pod 시작 불가, 스테이트풀 워크로드 배포 실패, 데이터베이스 및 스토리지 의존 애플리케이션 사용 불가, 용량 관련 시 KubePersistentVolumeFillingUp 알림 발생 가능, PVC가 Pending 상태 유지, 볼륨 프로비저닝 실패, 스토리지 의존 Pod 시작 불가. PersistentVolumeClaim 리소스가 Pending phase로 무기한 표시되며, PersistentVolumeClaim 바인딩 실패로 Pod 생성이 차단될 수 있고, 애플리케이션이 데이터에 접근하지 못해 오류를 표시할 수 있습니다.

## 플레이북

1. namespace <namespace>에서 PersistentVolumeClaim <pvc-name>을 describe하여 PVC 상태, phase, StorageClass 참조, 요청 용량, Pending 상태 유지 원인을 나타내는 조건을 확인합니다.

2. namespace <namespace>에서 PersistentVolumeClaim <pvc-name>의 이벤트를 타임스탬프 순으로 조회하여 프로비저닝 실패, StorageClass 미발견 오류, 용량 문제를 식별합니다.

3. StorageClass <storage-class-name>을 describe하여 StorageClass 구성, 프로비저너, 파라미터, allowVolumeExpansion 설정을 확인합니다.

4. 클러스터의 모든 StorageClass를 나열하여 사용 가능한 StorageClass를 확인하고 기본값을 식별합니다.

5. kube-system namespace의 Pod를 나열하고 스토리지 프로비저너 Pod를 필터링하여 스토리지 프로비저너 Pod 상태를 확인합니다.

6. 클러스터의 모든 PersistentVolume을 나열하고 재사용 가능한 고아 볼륨을 확인하며 reclaim policy를 검증합니다.

## 진단

1. 플레이북 2단계의 PVC 이벤트를 분석하여 특정 프로비저닝 실패 원인을 식별합니다. "ProvisioningFailed"를 보여주는 이벤트는 스토리지 프로비저너의 정확한 오류를 나타냅니다. 일반적인 원인:
   - "storageclass.storage.k8s.io not found" - StorageClass가 누락되었거나 철자 오류
   - "waiting for first consumer" - WaitForFirstConsumer 바인딩 모드로 Pod 스케줄링이 먼저 필요
   - "exceeded quota" - 스토리지 쿼터 소진
   - 프로비저너별 오류로 백엔드 문제 표시

2. 이벤트가 StorageClass 미발견을 나타내면, 플레이북 3-4단계에서 StorageClass 존재 여부를 확인합니다. 참조된 StorageClass가 목록에 없으면 삭제되었거나 생성되지 않은 것입니다. 기본 StorageClass가 존재하는지, PVC가 이를 사용해야 하는지 확인합니다.

3. 이벤트가 프로비저너 오류를 나타내면, 플레이북 5단계의 스토리지 프로비저너 Pod 상태를 확인합니다. 프로비저너 Pod가 Running이 아니거나 재시작이 표시되면, 프로비저너 자체가 비정상입니다. 프로비저너 Pod 재시작 타임스탬프를 PVC가 Pending 상태에 진입한 시점과 상관 분석합니다.

4. 이벤트가 용량 또는 쿼터 오류를 나타내면, 3단계의 StorageClass 파라미터와 6단계의 사용 가능한 PV를 조사합니다. 기존 Released PV가 PVC 요구사항과 일치하면, 수동으로 Available 상태로 만들어 문제를 해결할 수 있습니다.

5. 이벤트가 "waiting for first consumer"를 나타내지만 PVC를 사용하는 Pod도 Pending이면, WaitForFirstConsumer 바인딩 모드의 정상 동작입니다. 근본 원인은 Pod가 스케줄링되지 못하는 이유입니다(Pod 이벤트를 별도로 확인).

6. 이벤트가 불확실하거나 일반적인 오류를 표시하면, 스토리지 백엔드 수준의 문제일 가능성이 높습니다. StorageClass(3단계)의 프로비저너가 설치된 CSI 드라이버와 일치하는지 확인하고, 스토리지 백엔드 연결을 검증합니다.

**지정된 시간 범위 내에서 상관관계를 찾을 수 없는 경우**: 검색 범위를 확장하고(1시간 → 2시간, 5분 → 10분), 스토리지 프로비저너 로그에서 상세 오류 메시지를 검토하고, 스토리지 백엔드 쿼터 제한을 확인하고, StorageClass 파라미터의 잘못된 구성을 조사하고, 스토리지 프로비저너에 충분한 권한이 있는지 확인하고, 스토리지 백엔드 연결 문제를 확인하고, 시간에 따른 스토리지 용량 추세를 검토합니다. PVC Pending 문제는 Kubernetes 이벤트에서 즉시 보이지 않는 스토리지 백엔드 제한 또는 프로비저너 구성 문제로 인해 발생할 수 있습니다.
