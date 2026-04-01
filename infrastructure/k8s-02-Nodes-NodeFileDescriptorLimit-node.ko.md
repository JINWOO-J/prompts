---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/02-Nodes/NodeFileDescriptorLimit-node.md)'
role: SRE / K8s Incident Response
origin: scoutflo
tags:
- database
- infrastructure
- k8s-node
- k8s-pod
- k8s-service
- kubernetes
- node
- nodefiledescriptorlimit
- nodes
- security
---

---
title: Node File Descriptor Limit — Node 파일 디스크립터 제한
weight: 36
categories: [kubernetes, node]
---

# NodeFileDescriptorLimit

## 의미

Node가 파일 디스크립터 제한에 근접하거나 초과하고 있습니다(NodeFileDescriptorLimit, NodeFileDescriptorsExhaustion 알림 발생). 열린 파일, 소켓, 파이프의 수가 시스템 제한에 근접하고 있습니다.
 Node 메트릭에서 높은 파일 디스크립터 사용률이 나타나고, 새 연결이 실패하며, 프로세스가 파일을 열 수 없습니다. 이는 Node의 모든 워크로드에 영향을 미칩니다. 네트워크 연결이 실패하고, 파일 작업이 실패하며, 컨테이너 생성이 실패하고, 시스템이 불안정해집니다.

## 영향

NodeFileDescriptorLimit 알림이 발생하고, 새 소켓 연결이 "too many open files"로 실패합니다. 파일 열기 작업이 실패하며, 컨테이너 생성이 실패할 수 있습니다. Kubelet 작업에 영향을 미치고, 데이터베이스 연결을 설정할 수 없습니다. 로그 파일을 열 수 없으며, 네트워크 서비스가 연결 수락을 중단합니다. 기존 연결이 강제로 닫힐 수 있으며, 시스템 안정성이 저하됩니다.

## 플레이북

1. Node `<node-name>`을 조회하고 현재 파일 디스크립터 사용량 대비 제한(node_filefd_allocated, node_filefd_maximum)을 확인합니다.

2. lsof 또는 /proc/<pid>/fd 카운트를 사용하여 가장 많은 파일 디스크립터를 소비하는 프로세스를 파악합니다.

3. 파일 디스크립터 누수(연결이 닫히지 않음)가 있는 Pod 또는 컨테이너를 확인합니다.

4. /etc/sysctl.conf의 시스템 전체 제한(fs.file-max) 및 /etc/security/limits.conf의 프로세스별 제한을 확인합니다.

5. Kubelet 및 컨테이너 런타임의 파일 디스크립터 사용량을 확인합니다.

6. 시간이 지남에 따라 파일 디스크립터를 축적할 수 있는 장기 실행 Pod를 파악합니다.

7. 애플리케이션 연결 풀이 올바르게 구성되어 있고 연결이 반환되고 있는지 확인합니다.

## 진단

상위 파일 디스크립터 소비자를 파악하고 특정 프로세스가 디스크립터를 누수하는지 확인합니다. 프로세스별 fd 카운트 및 프로세스 식별을 근거로 사용합니다.

파일 디스크립터 증가를 가동 시간과 대조하고, 디스크립터가 시간이 지남에 따라 축적되는지(누수 표시) 또는 높은 수준에서 안정적인지(정당한 사용 표시) 확인합니다. fd 카운트 추세 및 프로세스 재시작 이력을 근거로 사용합니다.

TIME_WAIT, CLOSE_WAIT 상태의 소켓 축적을 확인하여 연결 처리 문제를 나타내는지 확인합니다. netstat 출력 및 연결 상태 분석을 근거로 사용합니다.

애플리케이션 연결 풀 구성을 확인하고 연결이 적절히 제한되고 해제되는지 확인합니다. 애플리케이션 구성 및 연결 메트릭을 근거로 사용합니다.

다른 Node와 비교하고 문제가 이 Node의 특정 워크로드에 한정되는지 확인합니다. Node 간 비교 및 워크로드 배치를 근거로 사용합니다.

**지정된 시간 범위 내에서 상관관계를 찾을 수 없는 경우**: fs.file-max 시스템 제한을 늘리고, 영향받는 서비스의 프로세스별 제한을 늘리며, 파일 디스크립터 누수가 있는 Pod를 재시작하고, 애플리케이션 연결 처리를 검토 및 수정하며, 연결 타임아웃 및 정리를 구현합니다.
