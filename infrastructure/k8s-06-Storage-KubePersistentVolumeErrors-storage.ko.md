---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/06-Storage/KubePersistentVolumeErrors-storage.md)'
role: Kubernetes SRE
origin: scoutflo
extract_date: 2026-03-05
tags:
- capacity
- infrastructure
- k8s-namespace
- k8s-pod
- k8s-pvc
- k8s-service
- kubepersistentvolumeerrors
- performance
- storage
---

---
title: Kube Persistent Volume Errors - PersistentVolume 오류
weight: 20
---

# KubePersistentVolumeErrors

## 의미

PersistentVolume에서 프로비저닝 또는 운영 오류가 발생하고 있습니다(PersistentVolume 관련 알림 트리거). 볼륨 프로비저닝 실패, 볼륨 바인딩 미완료, 또는 스토리지 백엔드 문제가 원인입니다. kubectl에서 PersistentVolume이 Failed 또는 Pending 상태로 표시되며, 볼륨 이벤트에 FailedBinding, ProvisioningFailed, VolumeFailed 오류가 나타나고, Pod는 볼륨 대기 중 Pending 또는 ContainerCreating 상태로 남습니다. 이는 스토리지 플레인에 영향을 미치며 Pod가 필요한 영구 스토리지를 마운트하지 못하게 합니다. 일반적으로 스토리지 백엔드 장애, 용량 고갈, 스토리지 프로바이더 문제가 원인이며, PersistentVolumeClaim 바인딩 실패로 Pod 생성이 차단될 수 있습니다.

## 영향

PersistentVolume 오류 알림 발생, 볼륨 사용 불가, 볼륨 누락으로 Pod 시작 불가, 데이터 접근 실패, PersistentVolume 이벤트에 오류 표시, 볼륨 바인딩 실패, PVC가 Pending 상태 유지, 서비스 저하 또는 불가용, 볼륨 손상 시 데이터 손실 가능성, 볼륨 프로비저닝 또는 바인딩 작업 완전 실패. PersistentVolume이 Failed 또는 Pending 상태로 무기한 유지되며, PersistentVolumeClaim 바인딩 실패로 Pod 생성이 차단될 수 있고, 애플리케이션이 데이터에 접근하지 못해 오류 또는 성능 저하가 발생할 수 있습니다.

## 플레이북

1. PersistentVolume <pv-name>을 describe하여 볼륨 상태, phase, reclaim policy, StorageClass, claim 참조, 프로비저닝 또는 운영 오류를 나타내는 오류 메시지를 확인합니다.

2. PersistentVolume <pv-name>의 이벤트를 타임스탬프 순으로 조회하여 FailedBinding, ProvisioningFailed, VolumeFailed, StorageClassNotFound 오류를 식별합니다.

3. namespace <namespace>에서 PersistentVolumeClaim <pvc-name>을 describe하여 PVC 상태, phase, 바인딩 상태를 확인합니다.

4. namespace <namespace>에서 PersistentVolumeClaim <pvc-name>의 이벤트를 타임스탬프 순으로 조회하여 바인딩 또는 프로비저닝 문제를 식별합니다.

5. StorageClass <storageclass-name>을 describe하여 StorageClass가 존재하고 올바르게 구성되어 있는지 확인합니다.

6. 스토리지 프로바이더 로그에 접근 가능한 경우, 볼륨 프로비저닝 오류에 대한 스토리지 프로바이더 로그를 조회하여 백엔드 문제를 식별합니다.

7. 클라우드 프로바이더에서 namespace 또는 클러스터의 스토리지 쿼터를 확인하여 쿼터가 볼륨 생성을 차단하고 있는지 검증합니다.

8. Bound 상태가 아닌 모든 PersistentVolume을 나열하여 Released 또는 Failed 상태의 고아 볼륨이 스토리지 백엔드 문제를 나타내는지 확인합니다.

## 진단

1. 플레이북 2단계의 PV 이벤트를 분석하여 특정 오류 유형을 식별합니다. 이벤트 reason이 장애 범주를 나타냅니다:
   - "FailedBinding" - 적합한 PV가 없거나 PVC 요구사항을 충족할 수 없음
   - "ProvisioningFailed" - 스토리지 백엔드가 요청된 볼륨을 생성할 수 없음
   - "VolumeFailed" - 기존 볼륨에서 오류 발생
   - "StorageClassNotFound" - 참조된 StorageClass가 존재하지 않음

2. 이벤트에 "ProvisioningFailed"가 표시되면 특정 백엔드 장애에 대한 오류 메시지를 확인합니다:
   - Quota exceeded - 스토리지 쿼터 소진 (7단계 확인)
   - Capacity unavailable - 스토리지 백엔드에 용량 없음
   - Permission denied - 프로비저너에 자격 증명 부족
   - Timeout - 스토리지 백엔드가 느리거나 접근 불가

3. 이벤트에 "FailedBinding"이 표시되면 플레이북 3-4단계의 PVC 요구사항을 8단계의 사용 가능한 PV와 비교합니다:
   - Access mode 불일치 (ReadWriteOnce vs ReadWriteMany)
   - 용량 불일치 (PVC가 사용 가능한 PV보다 더 많은 용량 요청)
   - StorageClass 불일치 (PVC가 매칭되는 PV가 없는 클래스를 지정)
   - Node affinity 충돌 (PV가 Pod가 실행될 수 없는 노드로 제한됨)

4. 이벤트에 "StorageClassNotFound"가 표시되면 플레이북 5단계에서 StorageClass 존재 여부를 확인합니다. 클래스가 삭제되거나 이름이 변경된 경우, 이를 참조하는 모든 PVC가 실패합니다.

5. PV 이벤트의 오류 패턴이 일관적이지 않고 간헐적이라면, 구성 문제가 아닌 스토리지 백엔드 불안정이 원인일 가능성이 높습니다. 6단계의 스토리지 프로바이더 로그에서 백엔드 상태 문제를 확인합니다.

6. 플레이북 8단계에서 Released 또는 Failed 상태의 PV가 존재하면, 이러한 고아 볼륨은 반복적인 프로비저닝/정리 문제를 나타낼 수 있습니다. 이 볼륨들이 오류 상태에 진입한 타임스탬프를 현재 PV 오류 타임스탬프와 상관 분석합니다.

**지정된 시간 범위 내에서 상관관계를 찾을 수 없는 경우**: 스토리지 시스템 변경에 대해 시간 범위를 24시간으로 확장하고, 스토리지 프로바이더 상태를 검토하고, 스토리지 백엔드 용량 문제를 확인하고, StorageClass 구성을 검증하고, 과거 볼륨 프로비저닝 패턴을 조사합니다. PersistentVolume 오류는 즉각적인 구성 변경이 아닌 스토리지 백엔드 장애, 용량 고갈, 스토리지 프로바이더 문제로 인해 발생할 수 있습니다.
