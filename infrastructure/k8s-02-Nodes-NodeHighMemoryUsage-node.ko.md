---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/02-Nodes/NodeHighMemoryUsage-node.md)'
role: SRE / K8s Incident Response
origin: scoutflo
tags:
- ecs
- infrastructure
- k8s-node
- k8s-pod
- k8s-service
- kubernetes
- node
- nodehighmemoryusage
- nodes
---

---
title: Node High Memory Usage — Node 높은 메모리 사용량
weight: 31
categories: [kubernetes, node]
---

# NodeHighMemoryUsage

## 의미

Node에서 높은 메모리 사용률이 발생하고 있습니다(NodeHighMemoryUsage, NodeMemoryHighUtilization 알림 발생, 일반적으로 메모리 사용량이 80-90%를 초과할 때). Node의 RAM이 실행 중인 Pod, 시스템 캐시 또는 커널 버퍼에 의해 과도하게 사용되고 있습니다.
 Node 메트릭에서 높은 메모리 사용률이 나타나고, 사용 가능한 메모리가 부족하며, Node가 OOM 상태의 위험에 처할 수 있습니다. 이는 Node 및 실행 중인 모든 워크로드에 영향을 미칩니다. Pod가 축출되거나 OOMKill될 수 있고, 새 Pod 스케줄링이 제한되며, 시스템 안정성이 위험에 처합니다.

## 영향

NodeHighMemoryUsage 알림이 발생하고, Kubelet 축출로 인해 Pod가 OOMKill 위험에 처합니다. 이 Node에 새 Pod를 스케줄링할 수 없으며, 시스템이 응답하지 않을 수 있습니다. 활성화된 경우 Swap 사용량이 증가하고, 커널이 OOM Killer를 호출할 수 있습니다. 중요한 시스템 프로세스가 영향받을 수 있으며, Kubelet이 메모리 압박에 따라 Pod를 축출할 수 있습니다. 여러 애플리케이션에 걸쳐 서비스 중단이 발생하고, Node가 NotReady 상태가 될 수 있습니다.

## 플레이북

1. Node `<node-name>`을 조회하고 현재 메모리 사용률, 사용 가능한 메모리 및 MemoryPressure 조건을 확인합니다.

2. Node에서 실행 중인 모든 Pod를 조회하고 container_memory_working_set_bytes 메트릭을 사용하여 가장 많은 메모리를 소비하는 Pod를 파악합니다.

3. 실제 메모리 사용량과 캐시/버퍼(회수 가능)를 구분하여 실제 메모리 압박을 이해합니다.

4. 과도한 리소스를 소비할 수 있는 메모리 제한이 없는 Pod를 확인합니다.

5. Node 축출 임계값(Kubelet 구성)을 조회하고 Node가 축출 트리거에 얼마나 가까운지 확인합니다.

6. 상당한 메모리를 소비하는 시스템 프로세스(컨테이너 외부)를 확인합니다.

7. Node가 워크로드 조합에 적합한 메모리를 가지고 있는지 확인합니다.

## 진단

Pod 메모리 사용량을 Limit과 비교하고, 특정 Pod가 제한에 근접하거나 초과하여 Node 전체에 압박을 유발하는지 확인합니다. 컨테이너 메트릭 및 리소스 스펙을 근거로 사용합니다.

메모리 구성(Working Set vs 캐시 vs 버퍼)을 분석하고, 높은 메모리가 애플리케이션 데이터(우려됨) 때문인지 회수 가능한 캐시(덜 우려됨) 때문인지 확인합니다. 상세 메모리 메트릭을 근거로 사용합니다.

메모리 증가를 최근 배포와 대조하고, 새 워크로드 또는 업데이트된 버전이 메모리 회귀를 도입했는지 확인합니다. 배포 타임스탬프 및 메모리 추세를 근거로 사용합니다.

지속적으로 증가하는 메모리 사용량을 보이는 Pod를 식별하여 특정 컨테이너의 메모리 누수를 확인합니다. 장기 메모리 추세 및 재시작 이력을 근거로 사용합니다.

축출 임계값이 적절하게 구성되어 있는지, Kubelet이 Node 안정성을 보호하기 위해 더 일찍 Pod를 축출해야 하는지 확인합니다. Kubelet 구성 및 축출 이벤트를 근거로 사용합니다.

**지정된 시간 범위 내에서 상관관계를 찾을 수 없는 경우**: 메모리 누수가 있는 Pod를 식별하여 재시작하고, Pod에 메모리 제한을 추가하거나 늘리며, Node를 drain하여 워크로드를 재분배하는 것을 고려하고, Node 인스턴스 크기를 검토하며, 커널 메모리 누수나 드라이버 문제를 확인합니다.
