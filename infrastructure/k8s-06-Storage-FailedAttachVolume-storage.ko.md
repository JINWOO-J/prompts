---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/06-Storage/FailedAttachVolume-storage.md)'
role: Kubernetes SRE
origin: scoutflo
extract_date: 2026-03-05
tags:
- database
- failedattachvolume
- infrastructure
- k8s-namespace
- k8s-node
- k8s-pod
- k8s-pvc
- k8s-service
- kubernetes
- storage
---

---
title: Failed Attach Volume - 볼륨 연결 실패
weight: 227
categories:
  - kubernetes
  - storage
---

# FailedAttachVolume-storage

## 의미

Kubernetes가 PersistentVolume을 Pod에 연결하거나 마운트할 수 없습니다(스토리지가 가득 찬 경우 KubePersistentVolumeFillingUp 알림과 관련될 수 있음). 일반적으로 PVC/PV 바인딩 문제, CSI 또는 스토리지 드라이버 장애, 노드-스토리지 연결 문제, 스토리지 프로비저너 오류가 원인입니다. 볼륨 연결 실패로 Pod가 영구 스토리지에 접근하지 못합니다.

## 영향

Pod 시작 불가, 영구 스토리지가 필요한 애플리케이션 실패, 스테이트풀 워크로드가 데이터에 접근 불가, 데이터베이스 및 스토리지 의존 서비스 사용 불가, Pod가 Pending 상태 유지, 볼륨 마운트 오류 발생, PVC 바인딩 실패, 스토리지 프로비저너 오류, CSI 드라이버 통신 문제.

## 플레이북

1. namespace <namespace>에서 PersistentVolumeClaim <pvc-name>을 describe하여 PVC 상태, phase, 바인딩된 볼륨, StorageClass, 볼륨 연결 불가 원인을 나타내는 조건이나 이벤트를 확인합니다.

2. namespace <namespace>에서 PersistentVolumeClaim <pvc-name>의 이벤트를 타임스탬프 순으로 조회하여 FailedAttachVolume, ProvisioningFailed, FailedMount 오류를 식별합니다.

3. namespace <namespace>에서 Pod <pod-name>을 describe하여 Pod 볼륨 정의, 상태 필드, 이벤트를 확인하고 어떤 볼륨이 연결 또는 마운트에 실패하는지 파악합니다.

4. namespace <namespace>에서 Pod <pod-name>의 이벤트를 타임스탬프 순으로 조회하여 Pod별 볼륨 연결 실패를 식별합니다.

5. PVC가 사용하는 StorageClass를 describe하고 kube-system의 해당 스토리지 프로비저너 Pod를 나열하여 CSI 또는 프로비저너 컴포넌트가 실행 중이고 정상인지 확인합니다.

6. Pod가 스케줄링된 노드 <node-name>을 describe하고 조건과 레이블을 확인하여 Ready 상태이고 스토리지 백엔드에 접근 가능한지 검증합니다.

7. PVC 또는 Pod와 관련된 VolumeAttachment 객체를 나열하고 CSI 드라이버가 볼륨을 연결됨으로 보고하는지 확인하거나 특정 오류를 식별합니다.

8. 노드 <node-name>의 용량 필드(연결 가능한 볼륨 제한 등)를 describe하여 스토리지 프로바이더의 최대 연결 가능 볼륨 수를 초과하지 않았는지 확인합니다.

9. 클러스터의 모든 VolumeAttachment를 나열하여 새 연결을 차단할 수 있는 고아 볼륨 연결을 확인하고 실행 중인 Pod와 비교합니다.

## 진단

1. 플레이북 4단계의 Pod 이벤트를 분석하여 특정 연결 실패 원인을 식별합니다. 이벤트 메시지에 중요한 진단 정보가 포함됩니다:
   - "Multi-Attach error" - 볼륨이 이미 다른 노드에 연결됨 (ReadWriteOnce 볼륨에서 흔함)
   - "attachment timeout" - CSI 드라이버 또는 스토리지 백엔드가 느리거나 접근 불가
   - "volume not found" - 기반 스토리지 리소스가 존재하지 않음
   - "permission denied" - 노드에 볼륨 연결 자격 증명 부족

2. 이벤트에 "Multi-Attach error"가 표시되면 볼륨이 다른 노드에 연결되어 있습니다. 플레이북 7단계의 VolumeAttachment 객체를 확인합니다:
   - 이전 Pod가 종료되었지만 VolumeAttachment가 남아있으면 분리가 멈춘 상태
   - 이전 Pod가 다른 노드에서 여전히 실행 중이면 RWO 볼륨의 정상 동작
   - 9단계의 고아 VolumeAttachment와 비교하여 멈춘 연결을 식별

3. 이벤트에 연결 타임아웃 또는 CSI 오류가 표시되면 플레이북 5단계의 스토리지 프로비저너 Pod를 확인합니다. CSI 드라이버 Pod가 Running이 아니거나 재시작이 표시되면, 재시작 타임스탬프를 연결 실패 시작 시점과 상관 분석합니다.

4. 플레이북 2단계의 PVC 이벤트에서 PVC가 Bound가 아닌 경우, 연결 실패는 PVC 바인딩 문제의 증상입니다. PVC Pending 진단을 따릅니다.

5. 플레이북 6단계의 노드 설명에서 볼륨 연결 제한에 도달한 경우(8단계), 노드에 더 이상 볼륨을 연결할 수 없습니다. 이는 노드당 볼륨을 제한하는 클라우드 프로바이더에서 흔합니다(예: AWS는 인스턴스 유형별 EBS 볼륨 제한).

6. 모든 컴포넌트가 정상으로 보이면 7단계의 VolumeAttachment 객체에서 특정 연결 상태를 확인합니다. attachmentMetadata에 오류가 표시되거나 attached=false와 오류 메시지가 있으면, 스토리지 백엔드가 연결 요청을 거부하고 있습니다.

**지정된 시간 범위 내에서 상관관계를 찾을 수 없는 경우**: 검색 범위를 확장하고(5분 → 10분, 1시간 → 2시간), 스토리지 프로비저너 로그에서 이전 오류나 경고를 검토하고, 점진적인 볼륨 제한 소진을 확인하고, 더 긴 기간에 걸친 CSI 드라이버 상태를 조사하고, 스토리지 백엔드 연결 문제가 점진적으로 발생했는지 확인하고, 이전에 도달했을 수 있는 노드 볼륨 연결 제한을 확인합니다. 볼륨 연결 실패는 누적된 문제나 즉시 보이지 않는 스토리지 백엔드 문제로 인해 발생할 수 있습니다.
