---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/02-Nodes/NodeFilesystemAlmostOutOfSpace-node.md)'
role: SRE / K8s Incident Response
origin: scoutflo
tags:
- database
- docker
- infrastructure
- k8s-node
- k8s-pod
- k8s-service
- kubernetes
- node
- nodefilesystemalmostoutofspace
- nodes
- storage
---

---
title: Node Filesystem Almost Out of Space — Node 파일시스템 공간 부족 임박
weight: 32
categories: [kubernetes, node]
---

# NodeFilesystemAlmostOutOfSpace

## 의미

Node 파일시스템의 디스크 공간이 부족해지고 있습니다(NodeFilesystemAlmostOutOfSpace, NodeDiskSpaceLow, NodeDiskSpaceCritical 알림 발생, 일반적으로 사용량이 80-90%를 초과할 때). 컨테이너 이미지, 로그, 임시 스토리지 또는 영구 데이터로 디스크가 채워지고 있습니다.
 Node 메트릭에서 높은 파일시스템 사용률이 나타나고, 사용 가능한 공간이 심각하게 부족하며, Node가 새 워크로드 수락을 중단할 수 있습니다. 이는 Node 및 모든 워크로드에 영향을 미칩니다. Pod가 축출될 수 있고, 새 Pod를 스케줄링할 수 없으며, 컨테이너 생성이 실패하고, 로그를 기록할 수 없으며, 시스템이 불안정해질 수 있습니다.

## 영향

NodeFilesystemAlmostOutOfSpace 알림이 발생하고, 새 컨테이너 이미지를 풀할 수 없습니다. DiskPressure로 인해 Pod가 축출될 수 있으며, 이 Node에 새 Pod를 스케줄링할 수 없습니다. 컨테이너 로그를 기록할 수 없고, 애플리케이션 쓰기가 실패합니다. 데이터가 이 파일시스템에 있는 경우 데이터베이스 작업이 실패합니다. Kubelet이 Node에 DiskPressure 조건을 표시하며, 시스템 서비스가 실패할 수 있습니다. Node가 NotReady 상태가 될 수 있으며, 디스크가 완전히 차면 데이터 손상 위험이 있습니다.

## 플레이북

1. Node `<node-name>`을 조회하고 현재 디스크 사용량, 사용 가능한 공간 및 DiskPressure 조건을 확인합니다.

2. 어떤 파일시스템이 부족한지 파악합니다 (/var/lib/docker, /var/lib/containerd, /var/log, /var/lib/kubelet).

3. 컨테이너 이미지 캐시 크기를 확인하고 가비지 컬렉션할 수 있는 미사용 이미지를 파악합니다.

4. Pod 임시 스토리지 사용량을 조회하고 과도한 로컬 스토리지를 소비하는 Pod를 파악합니다.

5. 컨테이너 로그 크기를 확인하고 과도한 로그를 생성하는 Pod를 파악합니다.

6. 이미지 및 컨테이너에 대한 Kubelet 가비지 컬렉션 설정을 확인합니다.

7. Node에서 로컬 스토리지를 사용하는 PersistentVolume을 확인합니다.

## 진단

디스크 사용량 분석을 통해 공간이 컨테이너 이미지, 컨테이너 로그, 임시 스토리지 또는 시스템 파일에 의해 소비되는지 파악합니다. 디스크 사용량 분석 및 파일시스템 검사를 근거로 사용합니다.

컨테이너 이미지 연령 및 사용량을 비교하고, 가비지 컬렉션이 회수해야 할 오래된 미사용 이미지가 공간을 소비하는지 확인합니다. 이미지 목록 및 마지막 사용 타임스탬프를 근거로 사용합니다.

디스크 증가를 특정 Pod와 대조하고, 특정 Pod가 emptyDir 또는 hostPath 볼륨에 과도한 데이터를 쓰는지 확인합니다. Pod 임시 스토리지 메트릭을 근거로 사용합니다.

로그 파일 크기 및 로테이션 구성을 확인하고, 로그 로테이션 누락으로 인해 로그 파일이 무제한으로 증가하는지 확인합니다. 로그 파일 크기 및 로테이션 구성을 근거로 사용합니다.

Kubelet 축출 임계값이 올바르게 구성되어 있는지, imagefs 또는 nodefs가 압박 상태인지 확인합니다. Kubelet 구성 및 축출 이벤트를 근거로 사용합니다.

**지정된 시간 범위 내에서 상관관계를 찾을 수 없는 경우**: 미사용 컨테이너 이미지를 수동으로 제거하고, 오래된 로그를 압축 또는 삭제하며, 크래시된 컨테이너 데이터를 정리하고, 클라우드 환경인 경우 디스크 크기를 늘리며, Pod 임시 스토리지 제한을 검토 및 설정합니다.
