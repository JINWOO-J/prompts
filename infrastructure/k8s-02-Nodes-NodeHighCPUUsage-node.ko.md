---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/02-Nodes/NodeHighCPUUsage-node.md)'
role: SRE / K8s Incident Response
origin: scoutflo
tags:
- capacity
- infrastructure
- k8s-node
- k8s-pod
- kubernetes
- node
- nodehighcpuusage
- nodes
- performance
- sts
---

---
title: Node High CPU Usage — Node 높은 CPU 사용량
weight: 30
categories: [kubernetes, node]
---

# NodeHighCPUUsage

## 의미

Node에서 높은 CPU 사용률이 발생하고 있습니다(NodeHighCPUUsage, NodeCPUHighUsage 알림 발생, 일반적으로 CPU 사용량이 80-90%를 초과할 때). Node의 프로세서가 실행 중인 워크로드, 시스템 프로세스 또는 폭주 작업에 의해 과부하 상태입니다.
 Node 메트릭에서 코어 전반에 걸쳐 높은 CPU 사용률이 나타나고, 시스템 로드 평균이 높아지며, Pod 성능이 저하될 수 있습니다. 이는 Node 및 실행 중인 모든 워크로드에 영향을 미칩니다. 컨테이너가 CPU 스로틀링을 경험하고, 애플리케이션 지연이 증가하며, 시스템 응답성이 저하됩니다.

## 영향

NodeHighCPUUsage 알림이 발생하고, Node의 모든 Pod가 성능 저하를 경험합니다. CPU 집약적 워크로드가 스로틀링되며, 시스템 프로세스가 지연될 수 있습니다. Kubelet 응답성이 감소하고, 헬스 체크가 타임아웃될 수 있습니다. 컨테이너 스케줄링에 영향을 줄 수 있으며, 극단적인 경우 Node가 응답하지 않을 수 있습니다. Pod 지연이 증가하고, SLO 위반이 발생하며, 전체 클러스터 용량이 감소합니다.

## 플레이북

1. Node `<node-name>`을 조회하고 현재 CPU 사용률, 로드 평균 및 할당 가능한 리소스를 확인합니다.

2. Node에서 실행 중인 모든 Pod를 조회하고 container_cpu_usage_seconds_total 메트릭을 사용하여 가장 많은 CPU를 소비하는 Pod를 파악합니다.

3. 과도한 리소스를 소비할 수 있는 CPU 제한이 없는 Pod를 확인합니다.

4. Node 시스템 프로세스 CPU 사용량을 조회하여 호스트 수준 프로세스(컨테이너가 아닌)가 CPU를 소비하는지 파악합니다.

5. Kubelet 및 컨테이너 런타임 프로세스가 과도한 CPU를 소비하는지 확인하여 시스템 수준 문제를 나타내는지 검증합니다.

6. 가상화 환경에서 하이퍼바이저 수준 경합을 나타내는 CPU Steal이 발생하는 Node를 확인합니다.

7. Node가 합리적인 버스트 용량을 초과하여 오버커밋되었는지 판단하기 위해 Pod 스케줄링을 검토합니다.

## 진단

Pod CPU 사용량을 Request 및 Limit과 비교하고, 특정 Pod가 할당량 이상을 소비하여 Node 전체에 압박을 유발하는지 확인합니다. 컨테이너 메트릭 및 리소스 스펙을 근거로 사용합니다.

CPU 스파이크를 특정 워크로드 패턴(배치 작업, 트래픽 피크)과 대조하고, 특정 기간 동안 높은 사용량이 예상되는지 확인합니다. 작업 스케줄 및 트래픽 메트릭을 근거로 사용합니다.

CPU 사용량 분석(user, system, iowait, steal)을 통해 문제가 애플리케이션 부하(user), 커널 작업(system), 디스크 병목(iowait) 또는 가상화(steal)인지 확인합니다. 상세 CPU 메트릭을 근거로 사용합니다.

해당 작업 없이 지속적으로 높은 CPU를 보이는 Pod를 식별하여 컨테이너의 폭주 프로세스 또는 무한 루프를 확인합니다. 컨테이너 메트릭 및 애플리케이션 처리량을 근거로 사용합니다.

nodeSelector, Affinity 또는 Anti-Affinity 규칙이 불균등한 Pod 분배를 유발하여 핫스팟을 만드는지 확인합니다. Pod 배치 및 Node 리소스 비교를 근거로 사용합니다.

**지정된 시간 범위 내에서 상관관계를 찾을 수 없는 경우**: Node를 cordon하고 Pod를 drain하여 워크로드를 재분배하고, 커널 버그나 드라이버 문제를 확인하며, 암호화폐 채굴이 없는지 검증하고, 가상화 환경에서 하이퍼바이저 리소스 할당을 검토하며, Node 인스턴스 유형의 적정 크기를 고려합니다.
