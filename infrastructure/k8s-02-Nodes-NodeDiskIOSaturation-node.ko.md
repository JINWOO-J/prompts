---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/02-Nodes/NodeDiskIOSaturation-node.md)'
role: SRE / K8s Incident Response
origin: scoutflo
tags:
- database
- docker
- infrastructure
- k8s-node
- k8s-pod
- kubernetes
- node
- nodediskiosaturation
- nodes
- performance
---

---
title: Node Disk IO Saturation — Node 디스크 I/O 포화
weight: 33
categories: [kubernetes, node]
---

# NodeDiskIOSaturation

## 의미

Node 디스크 I/O가 포화 상태입니다(NodeDiskIOSaturation 알림 발생). 디스크 서브시스템이 효율적으로 처리할 수 있는 것보다 더 많은 I/O 작업을 처리하고 있어 I/O 대기 및 지연이 발생합니다.
 Node 메트릭에서 높은 I/O 대기 시간이 나타나고, 디스크 큐 깊이가 높아지며, I/O 작업에 상당한 지연이 발생합니다. 이는 디스크 작업을 수행하는 Node의 모든 워크로드에 영향을 미칩니다. 데이터베이스 성능이 저하되고, 로그 쓰기가 지연되며, 컨테이너 시작이 느려지고, 애플리케이션에 타임아웃이 발생합니다.

## 영향

NodeDiskIOSaturation 알림이 발생하고, 모든 디스크 작업이 느려집니다. 데이터베이스 쿼리가 타임아웃되고, 로그 쓰기가 지연됩니다. 컨테이너 이미지 풀이 느려지며, 애플리케이션 응답 시간이 증가합니다. I/O 바운드 작업이 큐에 쌓이고, CPU에서 높은 iowait 비율이 나타납니다. 시스템이 느리게 보이며, fsync 작업이 차단됩니다. 쓰기 집약적 워크로드가 영향받고, 컨테이너 시작 시간이 증가합니다.

## 플레이북

1. Node `<node-name>`을 조회하고 iowait, 디스크 사용률, 큐 깊이를 포함한 디스크 I/O 메트릭을 확인합니다.

2. 어떤 디스크 장치가 포화 상태이며 어떤 파일시스템을 서비스하는지 파악합니다 (/var/lib/docker, /var/lib/kubelet, 데이터 볼륨).

3. Node에서 실행 중인 Pod를 조회하고 가장 많은 디스크 I/O를 생성하는 Pod를 파악합니다.

4. 과도한 디스크 쓰기를 유발할 수 있는 데이터베이스 또는 로그 집약적 워크로드를 확인합니다.

5. 디스크 유형(HDD vs SSD vs NVMe)이 워크로드 I/O 패턴에 적합한지 확인합니다.

6. 클라우드 환경에서 디스크 성능 저하(버스트 크레딧 소진으로 인한 스로틀링)를 확인합니다.

7. Node에 연결된 PersistentVolume과 해당 I/O 특성을 검토합니다.

## 진단

디스크 I/O 패턴을 워크로드 활동과 비교하고 특정 Pod가 과도한 I/O를 생성하는지 확인합니다. 컨테이너별 I/O 메트릭 및 Pod 활동을 근거로 사용합니다.

I/O 패턴 유형(순차 vs 랜덤, 읽기 vs 쓰기)을 분석하고 디스크 유형이 워크로드 패턴에 적합한지 확인합니다. I/O 메트릭 및 디스크 사양을 근거로 사용합니다.

I/O 포화를 클라우드 디스크 스로틀링(IOPS 제한, 처리량 제한, 버스트 크레딧)과 대조하고 클라우드 디스크 제한이 초과되는지 확인합니다. 클라우드 제공자 메트릭 및 디스크 티어 구성을 근거로 사용합니다.

쓰기 증폭을 유발하는 로그 로테이션 문제 또는 과도한 로깅을 확인합니다. 로그 파일 크기 및 쓰기 패턴을 근거로 사용합니다.

컨테이너 이미지 풀 또는 빌드가 일시적인 I/O 스파이크를 유발하는지 확인합니다. Kubelet 활동 및 이미지 풀 이벤트를 근거로 사용합니다.

**지정된 시간 범위 내에서 상관관계를 찾을 수 없는 경우**: 더 빠른 티어(SSD/NVMe)로 디스크를 업그레이드하고, 클라우드에서 디스크 IOPS 제한을 늘리며, 여러 디스크에 I/O를 분산합니다. 로그 집약적 워크로드를 별도 디스크로 이동하고, 로그 속도 제한을 구현하며, 로컬 NVMe 스토리지가 있는 Node를 고려합니다.
