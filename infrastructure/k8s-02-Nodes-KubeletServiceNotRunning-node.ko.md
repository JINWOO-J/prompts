---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/02-Nodes/KubeletServiceNotRunning-node.md)'
role: SRE / K8s Incident Response
origin: scoutflo
tags:
- capacity
- infrastructure
- k8s-node
- k8s-pod
- k8s-service
- kubeletservicenotrunning
- kubernetes
- node
- nodes
- performance
- rds
- sts
---

---
title: Kubelet Service Not Running — Kubelet 서비스 미실행
weight: 225
categories:
  - kubernetes
  - node
---

# KubeletServiceNotRunning-node

## 의미

Node에서 Kubelet 서비스가 실행되지 않고 있습니다(KubeNodeNotReady 또는 KubeletDown 알림 발생). 서비스가 중지되었거나, 크래시되었거나, 시작에 실패했거나, 비활성화되었습니다.
 클러스터 대시보드에서 Node가 NotReady 상태로 표시되고, Kubelet 서비스 상태가 중지 또는 실패로 나타나며, Kubelet 서비스 로그에 오류 메시지, 크래시 또는 시작 실패가 기록됩니다. 이는 데이터 플레인에 영향을 미치며, Node가 Pod를 관리하거나 상태를 보고하거나 API 서버 요청에 응답하는 것을 방해합니다. 일반적으로 Kubelet 프로세스 크래시, 리소스 제약, 컨테이너 런타임 문제 또는 구성 문제가 원인이며, 영향받는 Node에서 실행 중인 애플리케이션에 오류가 발생하거나 접근이 불가능해질 수 있습니다.

## 영향

Node가 NotReady 상태가 되고, Node의 Pod를 관리할 수 없습니다. 해당 Node에 새로운 Pod를 스케줄링할 수 없으며, Pod 상태를 Control Plane에 보고할 수 없습니다. KubeNodeNotReady 알림이 발생하고, KubeletDown 알림이 발생합니다. Node 상태가 NotReady로 전환되며, 클러스터가 Node 용량을 잃습니다. Node의 애플리케이션이 사용 불가능해집니다. Node가 무기한 NotReady 상태로 표시되고, Kubelet 서비스 상태가 중지 또는 실패로 나타나며, 영향받는 Node의 Pod가 접근 불가능해지거나 축출될 수 있습니다. 영향받는 Node에서 실행 중인 애플리케이션에 오류나 성능 저하가 발생할 수 있습니다.

## 플레이북

1. Node <node-name>을 describe하여 다음을 확인합니다:
   - Conditions 섹션에서 Ready 상태 확인 (False 또는 Unknown 예상)
   - Events 섹션에서 NodeNotReady 또는 Kubelet 서비스 실패 이벤트 확인
   - System Info 및 리소스 할당 세부 정보 확인

2. Node <node-name>의 이벤트를 타임스탬프 순으로 조회하여 'NodeNotReady' 또는 Kubelet 서비스 실패를 나타내는 메시지를 포함한 Kubelet 관련 이벤트의 순서를 확인합니다.

3. Node에서 Pod Exec 도구 또는 SSH(Node 접근 가능 시)를 사용하여 Kubelet 서비스 상태를 확인하고, 서비스가 실행 중인지, 중지되었는지, 실패했는지 검증합니다.

4. Node에서 Pod Exec 도구 또는 SSH를 통해 Kubelet 서비스 로그를 조회하고, Kubelet이 실행되지 않는 이유를 설명하는 오류, 크래시 또는 시작 실패를 필터링합니다.

5. Kubelet이 크래시되거나 종료될 수 있는 리소스 제약(CPU, 메모리, 디스크)이 Node에 있는지 확인합니다.

6. Kubelet이 컨테이너 런타임에 의존하므로 Node의 컨테이너 런타임 상태를 확인하고, 런타임 문제가 Kubelet 시작을 방해하는지 확인합니다.

## 진단

1. 플레이북 1-2단계의 Node 이벤트를 분석하여 Kubelet 서비스 문제가 시작된 시점을 파악합니다. "NodeNotReady" 사유와 "Kubelet stopped posting node status" 메시지가 있는 이벤트가 Kubelet이 응답하지 않게 된 시점을 보여줍니다. 이벤트 타임스탬프를 기록하여 장애 타임라인을 파악합니다.

2. Node 이벤트가 Kubelet의 예기치 않은 중지를 나타내는 경우, 플레이북 3-4단계에서 Kubelet 서비스 상태 및 로그를 확인합니다. 크래시 원인, OOM Kill, panic 메시지 또는 치명적 오류를 찾아 Kubelet이 중지된 이유를 파악합니다.

3. Kubelet 로그에서 OOM Kill 또는 리소스 고갈이 나타나는 경우, 플레이북 5단계에서 Node 리소스 제약을 확인합니다. 메모리 압박이나 디스크 고갈은 Kubelet이 OOM Killer에 의해 종료되거나 기능하지 못하게 할 수 있습니다.

4. Node 이벤트가 컨테이너 런타임 문제를 나타내는 경우, 플레이북 6단계에서 컨테이너 런타임 상태를 확인합니다. Kubelet은 컨테이너 런타임(containerd/docker)에 의존하므로 런타임이 사용 불가능하면 시작하거나 기능할 수 없습니다.

5. Kubelet 로그에서 구성 오류나 시작 실패가 나타나는 경우, 최근 Kubelet 구성 변경을 확인합니다. 잘못된 구성은 Kubelet이 시작되지 못하거나 즉시 크래시되게 합니다.

6. Kubelet 로그에서 인증서 또는 인증 오류가 나타나는 경우, Kubelet 인증서가 유효하고 접근 가능한지 확인합니다. 인증서 문제는 Kubelet이 API 서버에 인증하는 것을 방해합니다.

7. Kubelet 서비스 상태에서 서비스가 비활성화되었거나 활성화되지 않은 것으로 나타나는 경우, systemd 서비스 구성을 확인하여 Kubelet이 자동으로 시작되도록 구성되어 있는지 검증합니다.

**이벤트에서 근본 원인을 파악할 수 없는 경우**: 시스템 로그(journalctl, dmesg)에서 커널 수준 문제나 하드웨어 장애를 검토하고, Kubelet 바이너리나 구성에 영향을 미치는 디스크 손상을 확인하며, Node 운영체제 상태를 검증하고, Kubelet이 수동으로 중지되었거나 비활성화되었는지 확인합니다.
