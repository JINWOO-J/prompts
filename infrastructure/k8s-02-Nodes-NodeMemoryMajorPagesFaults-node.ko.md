---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/02-Nodes/NodeMemoryMajorPagesFaults-node.md)'
role: SRE / K8s Incident Response
origin: scoutflo
tags:
- infrastructure
- k8s-node
- k8s-pod
- kubernetes
- node
- nodememorymajorpagesfaults
- nodes
- performance
---

---
title: Node Memory Major Page Faults — Node 메모리 메이저 페이지 폴트
weight: 46
categories: [kubernetes, node]
---

# NodeMemoryMajorPagesFaults

## 의미

Node에서 높은 비율의 메이저 페이지 폴트가 발생하고 있습니다(NodeMemoryMajorPagesFaults 알림 발생). 프로세스가 디스크에서 읽어야 하는 메모리 페이지에 자주 접근하고 있으며, 이는 메모리 압박 또는 Swap 사용을 나타냅니다.
 Node 메트릭에서 높은 메이저 폴트 비율이 나타나고, I/O 대기가 증가하며, 전체 시스템 성능이 저하됩니다. 이는 Node의 모든 워크로드에 영향을 미칩니다. 애플리케이션 지연이 증가하고, 처리량이 감소하며, 시스템이 느려집니다.

## 영향

NodeMemoryMajorPagesFaults 알림이 발생하고, 애플리케이션 성능이 크게 저하됩니다. I/O 대기가 증가하며, 디스크가 병목이 됩니다. 페이지가 폴트될 때 지연 스파이크가 발생하고, 메모리 집약적 작업이 극적으로 느려집니다. Swap 스래싱이 발생할 수 있으며, 전체 시스템 처리량이 감소합니다. 사용자 경험이 저하됩니다.

## 플레이북

1. Node `<node-name>`을 조회하고 메모리 사용률, Swap 사용량 및 페이지 폴트 비율을 확인합니다.

2. Swap이 활성화되어 있고 적극적으로 사용되고 있는지 확인합니다.

3. 가장 많은 메모리 압박을 유발하는 Pod 또는 프로세스를 파악합니다.

4. Node 메모리가 스케줄링된 워크로드에 적합한지 확인합니다.

5. 페이지 아웃을 강제하는 컨테이너의 메모리 누수를 확인합니다.

6. 메모리 집약적 워크로드를 더 많은 메모리가 있는 Node로 재스케줄링해야 하는지 평가합니다.

7. Node의 메모리 오버커밋 설정(vm.overcommit_memory)을 확인합니다.

## 진단

메이저 페이지 폴트를 Swap 사용량과 대조하고, 메모리 압박으로 인해 페이지가 디스크로 스왑되는지 확인합니다. Swap 메트릭 및 폴트 비율을 근거로 사용합니다.

다른 워크로드의 페이지를 스왑 아웃시킬 수 있는 메모리 집약적 Pod를 파악합니다. 컨테이너별 메모리 메트릭 및 Node 할당을 근거로 사용합니다.

일시적으로 사용 가능한 메모리를 초과하여 페이지 폴트를 유발하는 버스트 메모리 사용 패턴을 확인합니다. 메모리 사용량 타임라인을 근거로 사용합니다.

메모리 오버커밋이 너무 공격적이어서 사용 가능한 것보다 더 많은 메모리를 약속하는지 확인합니다. 메모리 Request, Limit 및 실제 사용량을 근거로 사용합니다.

메모리 압박을 해결하기 위해 더 많은 Node(수평) 또는 더 큰 Node(수직)를 추가하는 것이 적절한지 분석합니다. 클러스터 용량 및 워크로드 요구 사항을 근거로 사용합니다.

**지정된 시간 범위 내에서 상관관계를 찾을 수 없는 경우**: Swap 스래싱을 방지하고 대신 OOMKill을 허용하도록 Swap을 비활성화하고, Node 메모리를 늘리며, 워크로드를 재분배하고, 제한 없는 Pod에 메모리 제한을 추가하며, 메모리 기반 Pod 스케줄링을 구현합니다.
