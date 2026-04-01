---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/02-Nodes/KubeNodeUnreachable-node.md)'
role: SRE / K8s Incident Response
origin: scoutflo
tags:
- capacity
- infrastructure
- k8s-node
- k8s-pod
- k8s-service
- kubenodeunreachable
- kubernetes
- monitoring
- node
- nodes
- performance
- rds
---

---
title: Kube Node Unreachable — Node 접근 불가
weight: 20
---

# KubeNodeUnreachable

## 의미

Kubernetes Node에 접근할 수 없으며 일부 워크로드가 재스케줄링될 수 있습니다(KubeNodeUnreachable 또는 KubeNodeNotReady와 같은 알림 발생). Node가 네트워크 연결을 잃었거나, Kubelet이 Control Plane과 통신할 수 없거나, Node가 완전히 장애 상태입니다. 클러스터 대시보드에서 Node가 Unknown 또는 NotReady 상태로 표시되고, Node 이벤트에 NodeUnreachable 또는 NodeLost 오류가 나타나며, kubectl 명령이 연결 타임아웃 오류로 실패합니다. 이는 데이터 플레인에 영향을 미치며 네트워크 파티셔닝, 하드웨어 장애 또는 통신을 방해하는 Node 수준 문제를 나타냅니다. 일반적으로 네트워크 인프라 문제, Node 하드웨어 장애 또는 파괴적인 소프트웨어 업그레이드가 원인이며, 영향받는 Node에서 실행 중인 애플리케이션에 오류가 발생하거나 접근이 불가능해질 수 있습니다.

## 영향

KubeNodeUnreachable 알림이 발생하고, Node에 접근할 수 없게 됩니다. Node의 Pod가 재스케줄링될 수 있으며, 워크로드에 중단이 발생합니다. Node 상태가 Unknown 또는 NotReady로 전환되고, Pod 상태가 Unknown이 됩니다. 서비스 엔드포인트가 제거될 수 있으며, 데이터 플레인 용량이 감소합니다. 애플리케이션에 다운타임이 발생할 수 있습니다. Node가 무기한 Unknown 또는 NotReady 상태로 표시되고, 영향받는 Node의 Pod가 재스케줄링되거나 접근 불가능해질 수 있으며, 실행 중인 애플리케이션에 오류나 성능 저하가 발생할 수 있습니다.

## 플레이북

1. Node <node-name>을 describe하여 다음을 확인합니다:
   - Conditions 섹션에서 Ready 상태 확인 (Unknown 또는 False 예상)
   - Events 섹션에서 NodeUnreachable, NodeNotReady 또는 NodeLost 이벤트 확인
   - 마지막 하트비트 시간 및 조건 전환 확인

2. Node <node-name>의 이벤트를 타임스탬프 순으로 조회하여 'NodeUnreachable', 'NodeNotReady', 'NodeLost'를 포함한 접근 불가 이벤트 순서를 확인합니다.

3. Node <node-name>의 조건을 확인하여 Node가 접근 불가를 나타내는 Unknown 상태인지 검증합니다.

4. 모니터링 시스템과 Node <node-name> 간의 네트워크 연결을 확인하여 연결 문제를 확인합니다.

5. Pod Exec 도구 또는 SSH(Node 접근 가능 시)를 통해 Node <node-name>의 Kubelet 상태를 확인하여 Kubelet 동작을 검증합니다.

6. Node <node-name> 관점에서 API 서버 연결을 확인하여 Control Plane 통신 문제를 파악합니다.

7. Node 접근성에 영향을 줄 수 있는 최근 Node 유지보수, 업그레이드 또는 인프라 변경 사항을 Node 이벤트 및 유지보수 로그를 검토하여 확인합니다.

## 진단

1. 플레이북 1-2단계의 Node 이벤트를 분석하여 접근 불가의 주요 원인을 파악합니다. "NodeUnreachable" 또는 "NodeLost" 사유의 이벤트는 통신의 완전한 단절을 나타냅니다. Unknown 상태의 "NodeNotReady" 사유 이벤트는 하트비트 타임아웃을 나타냅니다. 이벤트 타임스탬프를 기록하여 접근 불가가 시작된 시점을 파악합니다.

2. Node 이벤트가 Kubelet 통신 실패(최근 하트비트 없음)를 나타내는 경우, 플레이북 4단계에서 네트워크 연결을 확인하여 모니터링 시스템이나 다른 클러스터 Node에서 해당 Node에 네트워크로 접근 가능한지 확인합니다.

3. Node 이벤트가 Kubelet 문제를 나타내는 경우, 플레이북 5단계에서 Kubelet 상태를 확인합니다(Node 접근 가능 시). Kubelet 서비스 장애나 크래시는 네트워크가 정상이더라도 Node가 접근 불가능한 것처럼 보이게 합니다.

4. 네트워크 연결 테스트가 실패하는 경우, 플레이북 6단계에서 API 서버 연결을 확인합니다. 이를 통해 Node 측 네트워크 문제와 Control Plane 접근성 문제를 구분할 수 있습니다.

5. Node 이벤트가 여러 Node에 동시에 영향을 미치는 접근 불가를 보이는 경우, 이는 개별 Node 장애가 아닌 Control Plane 문제, 네트워크 인프라 장애 또는 API 서버 비가용성과 같은 클러스터 전체 문제를 나타냅니다.

6. Node 이벤트가 단일 Node에 대한 격리된 접근 불가를 보이는 경우, Node별 문제를 확인합니다: 하드웨어 장애, 운영체제 크래시 또는 로컬 네트워크 문제.

7. Node 이벤트가 계획된 유지보수를 나타내는 경우, 플레이북 7단계의 유지보수 로그와 대조하여 유지보수 기간 동안의 예상된 동작인지 확인합니다.

**이벤트에서 근본 원인을 파악할 수 없는 경우**: 클라우드 제공자의 인프라 상태에서 Node 또는 가용 영역 문제를 검토하고, Node 연결에 영향을 미치는 네트워크 인프라 문제를 확인하며, 대역 외 관리를 통해 Node 하드웨어 상태를 검증하고, 인프라 수준에서 Node가 종료되거나 중지되었는지 확인합니다.
