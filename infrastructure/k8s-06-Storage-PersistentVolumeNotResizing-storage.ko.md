---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/06-Storage/PersistentVolumeNotResizing-storage.md)'
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
- persistentvolumenotresizing
- storage
- sts
---

---
title: PersistentVolume Not Resizing - PV 크기 조정 실패
weight: 297
categories:
  - kubernetes
  - storage
---

# PersistentVolumeNotResizing-storage

## 의미

PersistentVolumeClaim 확장 시 PersistentVolume의 크기가 조정되지 않습니다(KubePersistentVolumeFillingUp 또는 KubePersistentVolumeNotReady 알림 트리거). StorageClass에 allowVolumeExpansion이 true로 설정되지 않았거나, 스토리지 백엔드(CSI 드라이버, 클라우드 프로바이더)가 크기 조정을 지원하지 않거나, kube-system namespace의 볼륨 확장 컨트롤러 Pod가 정상 작동하지 않거나, PVC 크기 조정 요청이 스토리지 프로비저너에 의해 처리되지 않는 것이 원인입니다. PersistentVolumeClaim 리소스에 크기 조정 보류 또는 실패 조건이 표시되며, StorageClass에 allowVolumeExpansion이 false로 표시될 수 있습니다.

## 영향

볼륨 용량 증가 불가, PVC 크기 조정 요청 미적용, 애플리케이션 디스크 공간 부족, 영구 스토리지 확장 불가, 볼륨이 용량 한계에 근접할 때 KubePersistentVolumeFillingUp 알림 발생, 볼륨 확장 실패 시 KubePersistentVolumeNotReady 알림 발생, 볼륨 확장 오류 발생, 스토리지 용량 제약으로 애플리케이션 성장 제한, 데이터베이스 Pod가 데이터 볼륨 확장 불가, PVC 상태에 크기 조정 보류 또는 실패 조건 표시. PersistentVolumeClaim 리소스에 크기 조정 보류 또는 실패 조건이 무기한 표시되며, 애플리케이션이 디스크 공간 부족으로 오류를 표시할 수 있습니다.

## 플레이북

1. namespace <namespace>에서 PersistentVolumeClaim <pvc-name>을 describe하여 PVC 상태, 조건, 크기 조정 요청을 확인하고 크기 조정이 보류 또는 실패 상태인지 검증합니다.

2. namespace <namespace>에서 PersistentVolumeClaim <pvc-name>의 이벤트를 타임스탬프 순으로 조회하여 VolumeResizeFailed 또는 FileSystemResizePending 이벤트를 식별합니다.

3. PersistentVolume <pv-name>을 describe하여 바인딩된 볼륨 상태, 용량을 확인하고 현재 볼륨 크기를 검증합니다.

4. PersistentVolume <pv-name>의 이벤트를 타임스탬프 순으로 조회하여 크기 조정 상태 이벤트를 식별합니다.

5. PVC가 참조하는 StorageClass를 describe하고 StorageClass 구성에서 allowVolumeExpansion이 true로 설정되어 있는지 확인합니다.

6. kube-system namespace의 Pod를 나열하고 볼륨 확장 컨트롤러 Pod 상태를 확인하여 컨트롤러가 실행 중이고 크기 조정 요청을 처리하고 있는지 검증합니다.

7. 스토리지 백엔드(예: 클라우드 프로바이더 스토리지)가 볼륨 확장을 지원하는지 스토리지 프로바이더 문서 또는 기능을 확인하여 검증합니다.

## 진단

1. 플레이북 2단계의 PVC 이벤트를 분석하여 특정 크기 조정 실패 원인을 식별합니다. 이벤트가 실패 지점을 나타냅니다:
   - "VolumeResizeFailed" - 스토리지 백엔드가 볼륨을 확장할 수 없음
   - "FileSystemResizePending" - 볼륨은 확장되었지만 파일시스템 크기 조정에 Pod 재시작 필요
   - 크기 조정 이벤트 없음 - 크기 조정 요청이 컨트롤러에 의해 처리되지 않음

2. 이벤트에 "FileSystemResizePending"이 표시되면, 볼륨 백엔드 확장은 성공했지만 파일시스템 크기 조정이 필요합니다. 일반적으로 다음이 필요합니다:
   - 볼륨을 사용하는 Pod 재시작 (온라인 크기 조정 가능 스토리지의 경우)
   - 볼륨 분리 후 재연결 (오프라인 크기 조정의 경우)
   이는 실패가 아니라 플레이북 1단계 조건의 보류 작업입니다.

3. 이벤트에 "VolumeResizeFailed"가 표시되거나 크기 조정 이벤트가 없으면, 플레이북 5단계의 StorageClass를 확인합니다. allowVolumeExpansion이 false이거나 설정되지 않은 경우, StorageClass가 볼륨 확장을 허용하지 않습니다. 이는 런타임 오류가 아닌 구성 제한입니다.

4. StorageClass가 확장을 허용하지만 크기 조정이 여전히 실패하면, 플레이북 7단계의 스토리지 백엔드 기능을 확인합니다. 모든 스토리지 백엔드가 온라인 확장을 지원하는 것은 아니며, 일부는 최소/최대 크기 제약이 있습니다.

5. StorageClass와 백엔드가 확장을 지원하면, 플레이북 6단계의 볼륨 확장 컨트롤러 Pod를 확인합니다. 컨트롤러 Pod가 Running이 아니거나 오류를 표시하면, 크기 조정 요청을 처리할 수 없습니다. 컨트롤러 Pod 재시작을 크기 조정 요청 제출 시점과 상관 분석합니다.

6. 플레이북 4단계의 PV 이벤트에 크기 조정 활동이 표시되지만 PVC에 여전히 보류가 표시되면, PV 용량(3단계)과 PVC 요청 용량(1단계)을 비교합니다. PV에 새 크기가 표시되지만 PVC에는 표시되지 않으면, 컨트롤러 동기화 문제일 수 있습니다.

**지정된 시간 범위 내에서 상관관계를 찾을 수 없는 경우**: 검색 범위를 확장하고(5분 → 10분, 30분 → 1시간, 1시간 → 2시간), 볼륨 확장 컨트롤러 로그에서 점진적인 처리 문제를 검토하고, 간헐적인 스토리지 백엔드 연결 문제를 확인하고, StorageClass 구성이 시간이 지남에 따라 변경되었는지 조사하고, 스토리지 프로바이더 기능이 점진적으로 변경되었는지 확인하고, 누적되었을 수 있는 볼륨 확장 쿼터 또는 제한 문제를 확인합니다. 볼륨 크기 조정 실패는 즉각적인 변경이 아닌 점진적인 스토리지 인프라 또는 구성 문제로 인해 발생할 수 있습니다.
