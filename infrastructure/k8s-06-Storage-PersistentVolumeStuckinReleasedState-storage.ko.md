---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/06-Storage/PersistentVolumeStuckinReleasedState-storage.md)'
role: Kubernetes SRE
origin: scoutflo
extract_date: 2026-03-05
tags:
- capacity
- infrastructure
- k8s-pvc
- kubernetes
- persistentvolumestuckinreleasedstate
- storage
---

---
title: PersistentVolume Stuck in Released State - PV Released 상태 고착
weight: 285
categories:
  - kubernetes
  - storage
---

# PersistentVolumeStuckinReleasedState-storage

## 의미

PersistentVolume이 Released 상태에 고착되어 있습니다(KubePersistentVolumeNotReady 알림 트리거). 바인딩된 PersistentVolumeClaim이 삭제되었지만 볼륨의 persistentVolumeReclaimPolicy가 Retain으로 설정되어 자동 삭제가 방지되거나, 스토리지 백엔드(CSI 드라이버, 클라우드 프로바이더)가 백엔드 문제로 볼륨을 해제할 수 없는 것이 원인입니다. kubectl에서 PersistentVolume이 Released phase로 표시되며, reclaim policy가 Retain으로 표시될 수 있고, 스토리지 백엔드가 사용 불가 상태일 수 있습니다. 이는 스토리지 플레인에 영향을 미치며 스토리지 리소스를 차단합니다.

## 영향

PersistentVolume이 Released 상태로 무기한 유지, 스토리지 리소스 미해제, 볼륨 재사용 불가, 볼륨이 필요한 경우 새 PVC 바인딩 실패 가능, 스토리지 용량 낭비, 볼륨이 Released 상태일 때 KubePersistentVolumeNotReady 알림 발생, 볼륨 정리 차단, 클러스터 스토리지 관리 저하, 볼륨 상태가 Released phase 표시, 스토리지 백엔드 리소스가 할당된 상태로 유지. PersistentVolume이 Released phase로 무기한 표시되며, 볼륨이 필요한 경우 PersistentVolumeClaim 바인딩이 실패할 수 있고, 스토리지 용량이 낭비되며 클러스터 스토리지 관리가 저하됩니다.

## 플레이북

1. PersistentVolume <pv-name>을 describe하여 볼륨 상태, phase, reclaim policy, claim 참조, finalizer를 확인하고 Released 상태에 고착된 이유를 파악합니다.

2. PersistentVolume <pv-name>의 이벤트를 타임스탬프 순으로 조회하여 볼륨 해제 또는 삭제 관련 이벤트와 정리를 방해하는 오류를 식별합니다.

3. Released 상태의 모든 PersistentVolume을 나열하여 클러스터 내 모든 고착 볼륨을 식별합니다.

4. 이전에 볼륨에 바인딩되었던 PersistentVolumeClaim이 여전히 존재하는지 또는 삭제되었는지 확인합니다.

5. PersistentVolume reclaim policy가 Retain, Delete, Recycle 중 어느 것으로 설정되어 있는지 확인합니다.

6. 스토리지 백엔드를 확인하여 기반 스토리지 리소스를 해제할 수 있는지 또는 백엔드 문제가 정리를 방해하고 있는지 검증합니다.

7. 클라우드 프로바이더에서 수동 정리가 필요할 수 있는 고아 스토리지 리소스를 확인합니다.

## 진단

1. 플레이북 2단계의 PV 이벤트를 분석하여 볼륨이 Released 상태에 고착된 이유를 식별합니다. 이벤트에 다음이 표시될 수 있습니다:
   - 정리 이벤트 없음 - Retain reclaim policy가 설계대로 작동 중 (오류 아님)
   - "VolumeFailedDelete" - 스토리지 백엔드가 기반 리소스를 삭제할 수 없음
   - Finalizer 관련 이벤트 - 외부 컨트롤러가 정리를 차단 중

2. 플레이북 5단계에서 reclaim policy를 확인합니다. persistentVolumeReclaimPolicy가 "Retain"이면 PVC 삭제 후 Released 상태는 예상된 동작입니다:
   - Retain이 의도적(데이터 보호용)이었다면, 볼륨은 수동 정리 또는 재구성이 필요
   - Retain이 의도치 않았다면, 향후 PVC 삭제 전에 reclaim policy를 변경해야 함

3. reclaim policy가 "Delete"인데 볼륨이 고착되어 있다면, 2단계의 PV 이벤트에서 스토리지 백엔드 오류를 확인합니다. CSI 드라이버 또는 스토리지 프로비저너가 기반 스토리지 리소스를 삭제할 수 없습니다. 다음을 확인합니다:
   - 스토리지 백엔드 리소스가 여전히 존재하는지 (6단계)
   - 스토리지 백엔드에 접근 가능한지 (6단계)
   - CSI 드라이버/프로비저너에 리소스 삭제 권한이 있는지

4. 플레이북 1단계의 PV 설명에 finalizer가 표시되면, 어떤 컨트롤러가 finalizer를 소유하는지 식별합니다. 고착된 finalizer는 Delete policy에서도 볼륨 정리를 방해합니다.

5. 플레이북 4단계에서 이전에 바인딩된 PVC가 여전히 존재하지만 이 PV에 바인딩되지 않은 경우, claimRef 불일치가 있을 수 있습니다. PV는 claim이 삭제되었다고 판단하지만 PVC는 다른 상태로 존재합니다.

6. 7단계에서 클라우드 프로바이더 고아 리소스가 존재하면, PV가 부분적으로 정리되었지만 백엔드 리소스가 남아있습니다. 클라우드 프로바이더 콘솔에서 수동 정리가 필요합니다.

**지정된 시간 범위 내에서 상관관계를 찾을 수 없는 경우**: 검색 범위를 확장하고(10분 → 30분, 30분 → 1시간, 1시간 → 2시간), 스토리지 플러그인 로그에서 점진적인 볼륨 정리 문제를 검토하고, 간헐적인 스토리지 백엔드 연결 문제를 확인하고, reclaim policy가 항상 Retain으로 설정되어 있었지만 최근에야 적용되었는지 조사하고, 스토리지 프로바이더 기능이 점진적으로 변경되었는지 확인하고, 누적되었을 수 있는 볼륨 finalizer 처리 문제를 확인합니다. PersistentVolume Released 상태 문제는 즉각적인 변경이 아닌 점진적인 스토리지 인프라 또는 정책 구성으로 인해 발생할 수 있습니다.
