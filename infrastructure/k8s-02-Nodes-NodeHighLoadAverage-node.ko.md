---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/02-Nodes/NodeHighLoadAverage-node.md)'
role: SRE / K8s Incident Response
origin: scoutflo
tags:
- infrastructure
- k8s-node
- k8s-pod
- kubernetes
- node
- nodehighloadaverage
- nodes
---

---
title: Node High Load Average — Node 높은 로드 평균
weight: 38
categories: [kubernetes, node]
---

# NodeHighLoadAverage

## 의미

Node에서 높은 로드 평균이 발생하고 있습니다(NodeHighLoadAverage, NodeSystemSaturation 알림 발생). 사용 가능한 CPU 코어가 처리할 수 있는 것보다 더 많은 프로세스가 실행을 원하여 프로세스가 큐에 대기하고 있습니다.
 Node 메트릭에서 로드 평균이 CPU 수보다 상당히 높게 나타나고, 시스템 응답성이 저하되며, 모든 작업이 느려집니다. 이는 Node의 모든 워크로드에 영향을 미칩니다. 응답 시간이 증가하고, 처리량이 감소하며, 시스템이 느려집니다.

## 영향

NodeHighLoadAverage 알림이 발생하고, Node의 모든 프로세스가 느려집니다. 컨테이너 작업이 지연되며, Kubelet 응답성이 감소합니다. 헬스 체크가 타임아웃될 수 있고, 네트워크 작업이 큐에 대기합니다. 디스크 I/O가 큐에 쌓이며, 시스템이 응답하지 않는 것처럼 보입니다. SSH 접근이 느려지고, Node를 대상으로 하는 kubectl 명령이 타임아웃됩니다. 애플리케이션 지연이 크게 증가합니다.

## 플레이북

1. Node `<node-name>`을 조회하고 CPU 코어 수와 비교하여 로드 평균(1분, 5분, 15분)을 확인합니다.

2. 부하의 원인을 파악합니다: CPU 포화, I/O 대기 또는 인터럽트 불가능 슬립 프로세스.

3. Node에서 실행 중인 상위 CPU 소비 프로세스 및 Pod를 조회합니다.

4. 부하에 기여하는 디스크 병목을 나타내는 높은 I/O 대기를 확인합니다.

5. I/O 또는 NFS 문제를 나타내는 인터럽트 불가능 슬립(D 상태) 프로세스를 확인합니다.

6. Node가 워크로드에 적합한 리소스를 가지고 있는지 확인합니다.

7. 과도한 프로세스 수를 생성하는 폭주 프로세스 또는 Fork Bomb을 확인합니다.

## 진단

로드 평균을 CPU 사용률과 비교하고, 부하가 CPU 바운드(높은 CPU%)인지 I/O 바운드(높은 iowait)인지 확인합니다. CPU 분석 메트릭을 근거로 사용합니다.

프로세스 상태를 분석하고 멈춘 I/O 또는 NFS 행을 나타낼 수 있는 D 상태(인터럽트 불가능 슬립) 프로세스를 파악합니다. 프로세스 상태 카운트를 근거로 사용합니다.

부하 스파이크를 워크로드 변경과 대조하고, 특정 Pod 또는 Job이 부하 증가를 유발하는지 확인합니다. Job 스케줄 및 부하 타임라인을 근거로 사용합니다.

CPU 사용량을 증가시키지 않으면서 부하를 높이는 프로세스 수 폭증을 확인합니다. 프로세스 수 메트릭 및 Fork 이벤트를 근거로 사용합니다.

다른 Node와 비교하고, 부하가 균등하게 분배되는지 또는 스케줄링 불균형으로 인해 이 Node가 과부하인지 확인합니다. Node 간 비교를 근거로 사용합니다.

**지정된 시간 범위 내에서 상관관계를 찾을 수 없는 경우**: 워크로드를 drain하여 재분배하고, 멈춘 I/O(NFS, 디스크 문제)를 조사하며, 폭주 프로세스를 식별하여 종료하고, 불균형을 유발하는 스케줄링 제약을 검토하며, 더 큰 인스턴스 유형으로 업그레이드를 고려합니다.
