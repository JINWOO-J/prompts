---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/02-Nodes/NodeSystemdServiceFailed-node.md)'
role: SRE / K8s Incident Response
origin: scoutflo
tags:
- docker
- infrastructure
- k8s-node
- k8s-pod
- k8s-service
- kubernetes
- logging
- monitoring
- networking
- node
- nodes
- nodesystemdservicefailed
---

---
title: Node Systemd Service Failed — Node Systemd 서비스 실패
weight: 37
categories: [kubernetes, node]
---

# NodeSystemdServiceFailed

## 의미

Node의 systemd 서비스가 실패했습니다(NodeSystemdServiceFailed, NodeSystemdServiceCrashlooping 알림 발생). 중요한 시스템 서비스가 실행되지 않으며 자동으로 복구할 수 없습니다.
 Node에서 systemctl에 실패한 유닛이 표시되고, 서비스가 크래시 루프 상태일 수 있으며, 의존하는 기능을 사용할 수 없습니다. 이는 Node 및 잠재적으로 클러스터 기능에 영향을 미칩니다. Kubelet이 영향받을 수 있고, 컨테이너 런타임이 실패할 수 있으며, 네트워킹이 중단될 수 있고, 로깅이 중단될 수 있습니다.

## 영향

NodeSystemdServiceFailed 알림이 발생하고, 의존 서비스가 영향받습니다. Kubelet이 실패하면 Node가 NotReady 상태가 됩니다. 컨테이너 런타임이 실패하면 컨테이너를 시작할 수 없습니다. 네트워킹 서비스가 실패하면 Pod 네트워킹이 중단됩니다. 로깅 서비스가 실패하면 로그 전달이 중단됩니다. node-exporter가 실패하면 모니터링 데이터가 손실됩니다. Node 기능이 저하되며, 이 Node에서의 클러스터 작업이 실패합니다.

## 플레이북

1. Node `<node-name>`을 조회하고 `systemctl --failed`를 사용하여 어떤 systemd 서비스가 실패했는지 파악합니다.

2. `systemctl status <service-name>`으로 서비스 상태를 확인하여 실패 원인 및 최근 로그를 확인합니다.

3. `journalctl -u <service-name>`을 사용하여 서비스 로그를 조회하고 실패의 근본 원인을 파악합니다.

4. 서비스 의존성을 확인하고 의존성 실패가 연쇄 장애를 유발하는지 검증합니다.

5. 서비스 구성 파일에서 구문 오류 또는 잘못된 구성을 확인합니다.

6. 서비스 운영을 방해할 수 있는 시스템 리소스(디스크 공간, 메모리)를 확인합니다.

7. 중요 서비스(kubelet, containerd, docker)의 경우 특정 구성 및 상태를 확인합니다.

## 진단

서비스 종료 코드 및 오류 메시지를 분석하고 실패 유형(구성 오류, 리소스 문제, 의존성 실패)을 분류합니다. 서비스 상태 및 로그를 근거로 사용합니다.

실패를 도입했을 수 있는 서비스 구성 또는 시스템 업데이트의 최근 변경 사항을 확인합니다. 구성 파일 타임스탬프 및 패키지 업데이트 이력을 근거로 사용합니다.

서비스에 대한 리소스 가용성(디스크 공간, 메모리, 포트, 파일 디스크립터)을 확인하고 리소스가 사용 가능한지 확인합니다. 시스템 리소스 메트릭 및 서비스 요구 사항을 근거로 사용합니다.

하나의 서비스 실패가 연쇄 실패를 유발하는 의존성 체인 실패를 확인합니다. 서비스 의존성 트리 및 실패 타임스탬프를 근거로 사용합니다.

재시작 패턴을 분석하고 서비스가 크래시 루프(근본 문제) 상태인지 또는 한 번 실패하고 중단된 상태(시작 문제)인지 확인합니다. 재시작 횟수 및 타임스탬프를 근거로 사용합니다.

**지정된 시간 범위 내에서 상관관계를 찾을 수 없는 경우**: 수동 서비스 재시작을 시도하고, 구성 오류를 검토 및 수정하며, 손상된 상태 파일을 확인하고, 손상된 경우 서비스를 재설치하며, 복구 불가능한 경우 Node 교체로 에스컬레이션합니다.
