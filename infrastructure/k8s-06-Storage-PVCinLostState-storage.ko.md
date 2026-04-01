---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/06-Storage/PVCinLostState-storage.md)'
role: Kubernetes SRE
origin: scoutflo
extract_date: 2026-03-05
tags:
- database
- infrastructure
- k8s-namespace
- k8s-pod
- k8s-pvc
- k8s-service
- kubernetes
- pvcinloststate
- storage
- sts
---

---
title: PVC in Lost State - PVC Lost 상태
weight: 217
categories:
  - kubernetes
  - storage
---

# PVCinLostState-storage

## 의미

PersistentVolumeClaim이 Lost 상태에 있습니다(KubePersistentVolumeNotReady 알림 트리거). 기반 PersistentVolume 또는 스토리지 백엔드가 사용 불가하거나, 볼륨이 스토리지 프로바이더에서 삭제되었거나, 스토리지 연결이 끊어진 것이 원인입니다. kubectl에서 PersistentVolumeClaim 리소스가 Lost phase로 표시되며, PersistentVolume이 Failed 또는 Released 상태를 표시할 수 있고, Pod 이벤트에 VolumeLost 또는 스토리지 백엔드 사용 불가 오류가 표시됩니다. 이는 스토리지 플레인에 영향을 미치며 Pod가 영구 스토리지에 접근하지 못하게 합니다.

## 영향

PersistentVolumeClaim이 Lost 상태, Pod가 영구 스토리지에 접근 불가, 볼륨 마운트 실패, 애플리케이션이 데이터에 접근 불가, KubePersistentVolumeNotReady 알림 발생, 스테이트풀 워크로드 실패, 데이터베이스 Pod가 볼륨 마운트 불가, 영구 데이터 접근 불가, 스토리지 의존 서비스 사용 불가. PersistentVolumeClaim 리소스가 Lost phase로 무기한 표시되며, PersistentVolumeClaim 바인딩 실패로 Pod 생성이 차단될 수 있고, 애플리케이션이 데이터에 접근하지 못해 오류를 표시할 수 있습니다.

## 플레이북

1. namespace <namespace>에서 PersistentVolumeClaim <pvc-name>을 describe하여 PVC 상태, phase, 조건을 확인하고 Lost 상태의 원인을 식별합니다.

2. namespace <namespace>에서 PersistentVolumeClaim <pvc-name>의 이벤트를 타임스탬프 순으로 조회하여 VolumeLost 또는 스토리지 백엔드 사용 불가 오류를 식별합니다.

3. PersistentVolume <pv-name>을 describe하여 바인딩된 볼륨 상태, phase, 스토리지 백엔드 정보를 확인하고 볼륨이 존재하고 접근 가능한지 검증합니다.

4. PersistentVolume <pv-name>의 이벤트를 타임스탬프 순으로 조회하여 백엔드 연결 문제를 식별합니다.

5. 스토리지 백엔드(예: 클라우드 프로바이더 스토리지, NFS 서버)를 확인하여 기반 스토리지 리소스가 존재하고 접근 가능한지 검증합니다.

6. PVC가 참조하는 StorageClass를 describe하고 스토리지 프로비저너가 사용 가능하고 정상 작동하는지 확인합니다.

7. PVC를 사용하는 Pod를 나열하고 상태를 확인하여 볼륨 마운트 실패가 발생하고 있는지 검증합니다.

## 진단

1. 플레이북 2단계의 PVC 이벤트를 분석하여 Lost 상태의 특정 원인을 식별합니다. "VolumeLost" 또는 "VolumeNotFound"를 보여주는 이벤트는 기반 스토리지 리소스에 더 이상 접근할 수 없음을 나타냅니다. 이벤트 메시지에 일반적으로 스토리지 백엔드의 특정 오류가 포함됩니다.

2. 이벤트가 볼륨을 찾을 수 없음을 나타내면, 플레이북 3단계의 PersistentVolume 상태를 확인합니다. PV가 Failed 또는 Released 상태이거나 PV가 더 이상 존재하지 않으면, 기반 스토리지가 삭제되었거나 접근 불가 상태입니다:
   - PV가 Retain policy로 Released 상태이면, 이전 PVC가 삭제되었지만 볼륨 데이터는 여전히 존재
   - PV가 Failed 상태이면, 스토리지 백엔드가 오류를 보고
   - PV가 존재하지 않으면, 수동으로 또는 Delete reclaim policy에 의해 삭제됨

3. 플레이북 4단계의 PV 이벤트에 백엔드 연결 오류가 표시되면, 스토리지 백엔드(NFS 서버, 클라우드 스토리지 등)에 접근할 수 없습니다. 5단계에서 스토리지 백엔드 상태를 확인하여 가용성을 확인합니다.

4. 3-4단계에서 PV가 존재하고 정상으로 보이지만 PVC가 여전히 Lost이면, PV의 claimRef 필드를 확인합니다. claimRef가 다른 또는 존재하지 않는 PVC를 가리키면 바인딩 불일치가 있습니다.

5. 플레이북 6단계의 StorageClass 프로비저너에 문제가 있으면, 프로비저너 문제를 PVC가 Lost 상태에 진입한 시점과 상관 분석합니다. 실패하는 프로비저너는 볼륨 바인딩을 적절히 유지할 수 없습니다.

6. 플레이북 7단계에서 PVC를 사용하는 Pod가 Lost 상태 이전에 반복적인 마운트 실패를 보이면, 간헐적인 연결 문제가 완전한 실패로 악화된 것일 수 있습니다. Pod 마운트 실패 타임스탬프가 PVC Lost 상태보다 앞서는지 확인합니다.

**지정된 시간 범위 내에서 상관관계를 찾을 수 없는 경우**: 검색 범위를 확장하고(10분 → 30분, 30분 → 1시간, 1시간 → 2시간), 스토리지 플러그인 로그에서 점진적인 볼륨 연결 문제를 검토하고, 간헐적인 스토리지 백엔드 가용성 문제를 확인하고, 스토리지 리소스가 점진적으로 삭제되거나 마이그레이션되었는지 조사하고, 스토리지 프로바이더 연결이 시간이 지남에 따라 저하되었는지 확인하고, 리소스 제거를 유발했을 수 있는 스토리지 백엔드 쿼터 또는 용량 문제를 확인합니다. PVC Lost 상태는 즉각적인 삭제가 아닌 점진적인 스토리지 인프라 저하로 인해 발생할 수 있습니다.
