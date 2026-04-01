---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/06-Storage/VolumeMountPermissionsDenied-storage.md)'
role: Kubernetes SRE
origin: scoutflo
extract_date: 2026-03-05
tags:
- database
- infrastructure
- k8s-namespace
- k8s-pod
- kubernetes
- performance
- security
- sg
- storage
- volumemountpermissionsdenied
---

---
title: Volume Mount Permissions Denied - 볼륨 마운트 권한 거부
weight: 247
categories:
  - kubernetes
  - storage
---

# VolumeMountPermissionsDenied-storage

## 의미

컨테이너가 권한 문제로 마운트된 볼륨에 접근할 수 없습니다(KubePodCrashLooping 또는 KubePodNotReady 알림 트리거). 스토리지 백엔드의 볼륨 파일 권한이 잘못되었거나, 컨테이너의 security context runAsUser가 볼륨 소유권과 일치하지 않거나, Pod security context의 파일시스템 그룹 ID(fsGroup)가 올바르게 설정되지 않은 것이 원인입니다.

## 영향

컨테이너가 볼륨 읽기/쓰기 불가, 볼륨 마운트 권한 거부, 애플리케이션이 영구 데이터 접근 실패, Pod는 시작되지만 애플리케이션이 권한 거부 오류로 충돌, 컨테이너가 권한 실패로 재시작될 때 KubePodCrashLooping 알림 발생, Pod가 필요한 볼륨에 접근하지 못할 때 KubePodNotReady 알림 발생, Pod 로그에 파일 권한 오류 표시, 데이터베이스 Pod가 데이터 디렉토리 접근 불가, 로그 수집 실패, 영구 스토리지 접근 불가. Pod 로그에 권한 거부 오류가 무기한 표시되며, 애플리케이션이 영구 데이터에 접근하지 못해 오류 또는 성능 저하가 발생할 수 있습니다.

## 플레이북

1. namespace <namespace>에서 Pod <pod-name>을 describe하여 Pod security context, 컨테이너 security context, 사용자 ID(runAsUser), 그룹 ID(fsGroup), 볼륨 마운트 구성을 확인합니다.

2. namespace <namespace>에서 Pod <pod-name>의 이벤트를 타임스탬프 순으로 조회하여 FailedMount 오류 또는 권한 관련 문제를 식별합니다.

3. namespace <namespace>에서 Pod <pod-name>의 로그를 조회하고 권한 거부 오류, 접근 거부 메시지, 파일시스템 권한 실패를 필터링합니다.

4. namespace <namespace>에서 PersistentVolumeClaim <pvc-name>을 describe하여 PVC 상태를 확인하고 볼륨 소유권 설정을 검증합니다.

5. PersistentVolume <pv-name>을 describe하여 볼륨 상태를 확인하고 스토리지 백엔드의 권한을 검증합니다.

6. Pod <pod-name>에서 마운트된 볼륨 경로의 디렉토리 목록을 실행하여 파일 권한과 소유권을 확인합니다.

7. namespace <namespace>에서 Deployment <deployment-name>을 describe하고 Pod 템플릿의 security context 구성을 검토하여 fsGroup과 runAsUser 설정을 확인합니다.

## 진단

1. 플레이북 2단계의 Pod 이벤트를 분석하여 특정 권한 오류 유형을 식별합니다. 권한 관련 메시지와 함께 "FailedMount"를 보여주는 이벤트는 정확한 실패 지점을 나타냅니다. 오류가 특정 경로에서 "permission denied"를 언급하면 파일시스템 수준 문제이고, "operation not permitted"를 언급하면 security context 관련 문제입니다.

2. 이벤트가 FailedMount 오류를 나타내면, 플레이북 3단계의 Pod 로그에서 특정 권한 거부 메시지를 확인합니다. 오류 경로와 작업(읽기/쓰기/실행)이 다음 중 어떤 문제인지 나타냅니다:
   - 파일 소유권 불일치 (1단계의 runAsUser를 6단계의 볼륨 권한과 비교)
   - 그룹 권한 불일치 (1단계의 fsGroup을 6단계의 볼륨 그룹 소유권과 비교)
   - SELinux 또는 seccomp 제한 (1/7단계의 security context)

3. 플레이북 1단계의 Pod security context에 runAsUser 또는 fsGroup 설정이 있으면, 이 값을 6단계의 실제 파일 소유권과 비교합니다. 컨테이너 UID/GID와 볼륨 소유권 간의 불일치가 권한 거부 오류의 가장 흔한 원인입니다.

4. security context가 올바른 것으로 보이면, 플레이북 4-5단계의 PVC 및 PV 상태를 확인합니다. 볼륨이 최근에 프로비저닝되거나 마이그레이션된 경우, 스토리지 백엔드의 기본 권한이 애플리케이션 요구사항과 일치하지 않을 수 있습니다.

5. 플레이북 7단계의 Deployment security context가 실행 중인 Pod(1단계)와 다르면, 최근 배포 롤아웃이 권한 불일치를 도입했을 가능성이 높습니다. 배포 타임스탬프를 이벤트에서 권한 오류가 처음 나타난 시점과 상관 분석합니다.

6. 모든 security context가 일관된 것으로 보이면, 스토리지 백엔드 수준의 문제일 수 있습니다. 5단계의 PV 스토리지 백엔드가 Kubernetes fsGroup 설정을 재정의하는 자체 권한 모델을 가지고 있는지 확인합니다.

**지정된 시간 범위 내에서 상관관계를 찾을 수 없는 경우**: 검색 범위를 확장하고(30분 → 1시간, 1시간 → 2시간), Pod 로그에서 점진적인 권한 문제를 검토하고, 간헐적인 파일시스템 권한 문제를 확인하고, security context 구성이 시간이 지남에 따라 변경되었는지 조사하고, 볼륨 소유권이 점진적으로 변경되었는지 확인하고, 누적되었을 수 있는 스토리지 백엔드 권한 변경을 확인합니다. 볼륨 권한 문제는 즉각적인 변경이 아닌 점진적인 security context 또는 스토리지 구성 변경으로 인해 발생할 수 있습니다.
