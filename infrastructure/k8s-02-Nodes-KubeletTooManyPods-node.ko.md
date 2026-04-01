---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/02-Nodes/KubeletTooManyPods-node.md)'
role: SRE / K8s Incident Response
origin: scoutflo
tags:
- capacity
- infrastructure
- k8s-node
- k8s-pod
- kubelettoomanypods
- node
- nodes
- performance
- rds
---

---
title: Kubelet Too Many Pods — Kubelet Pod 수 초과
weight: 20
---

# KubeletTooManyPods

## 의미

특정 Node가 Pod 용량 제한(기본값 110, 구성 가능)의 95% 이상을 실행하고 있습니다(KubeletTooManyPods 알림 발생). Node가 지원할 수 있는 최대 Pod 수에 도달했거나 근접하고 있습니다.
 클러스터 대시보드에서 Node의 높은 Pod 수가 용량 제한에 근접하고 있으며, Node 메트릭이 높은 Pod 밀도로 인한 리소스 압박을 나타내고, 추가 Pod에 대한 스케줄링이 실패할 수 있습니다. 이는 데이터 플레인에 영향을 미치며, Pod 밀도가 너무 높아 Container Runtime Interface(CRI), Container Network Interface(CNI) 및 운영체제 리소스에 부담을 줄 수 있음을 나타냅니다. 일반적으로 스케줄링 불균형, 클러스터 용량 제약 또는 워크로드 분배 문제가 원인이며, 영향받는 Node에서 실행 중인 애플리케이션의 성능이 저하될 수 있습니다.

## 영향

KubeletTooManyPods 알림이 발생하고, 단일 Node에서 많은 Pod를 실행하면 CRI, CNI 및 운영체제에 부담이 됩니다. Pod 제한에 근접하면 해당 Node의 성능과 가용성에 영향을 줄 수 있으며, Node가 추가 Pod를 스케줄링할 수 없게 될 수 있습니다. Node 성능이 저하되고, 컨테이너 런타임 작업이 느려질 수 있으며, CRI, CNI 및 운영체제 리소스에 부담이 됩니다. Node에서 높은 Pod 수가 용량 제한에 근접하고, 추가 Pod에 대한 스케줄링이 실패하며, Node 성능이 저하됩니다. 영향받는 Node에서 실행 중인 애플리케이션의 성능이 저하되거나 리소스 경합이 발생할 수 있습니다.

## 플레이북

1. Node <node-name>을 describe하여 다음을 확인합니다:
   - Conditions 섹션에서 Ready 상태 및 압박 조건 확인
   - Capacity 및 Allocatable 섹션에서 최대 Pod 구성 확인
   - Non-terminated Pods 섹션에서 현재 Pod 수 및 리소스 사용량 확인

2. Node <node-name>의 이벤트를 타임스탬프 순으로 조회하여 Pod 용량과 관련된 Node 문제의 순서를 확인합니다.

3. Node <node-name>에 스케줄링된 Pod를 조회하고 Node의 Pod 수를 확인하여 높은 Pod 밀도를 검증합니다.

4. Node <node-name>의 리소스 사용량 메트릭을 조회하여 높은 Pod 밀도로 인한 현재 CPU 및 메모리 사용률을 확인합니다.

5. 모든 네임스페이스의 Pod를 조회하고 Pod 분배를 확인하여 Pod 밀도가 특정 Node에 집중되어 있는지 파악합니다.

6. Cluster Autoscaler 상태 및 Pod 부하 재분배를 위한 Node 가용성을 확인하고, Cluster Autoscaler 구성 및 Node Pool 상태를 점검합니다.

## 진단

1. 플레이북 2단계의 Node 이벤트를 분석하여 Pod 용량 경고 또는 스케줄링 이벤트가 발생한 시점을 파악합니다. "TooManyPods" 사유의 "FailedScheduling" 또는 Node 용량 경고를 나타내는 이벤트가 용량 고갈의 타임라인을 보여줍니다.

2. Node 이벤트가 갑작스러운 Pod 수 증가를 나타내는 경우, 플레이북 3단계의 Pod 목록을 확인하여 최근 이 Node에 스케줄링된 워크로드를 파악합니다. 최근 Pod 생성 타임스탬프를 찾고 원인이 되는 Deployment, Job 또는 DaemonSet을 식별합니다.

3. Node 이벤트가 점진적인 Pod 축적을 보이는 경우, 플레이북 5단계에서 모든 Node에 걸친 Pod 분배를 비교합니다. 불균등한 분배는 Node Affinity, Taint 또는 다른 Node의 리소스 제약으로 인한 스케줄링 불균형을 나타냅니다.

4. Node 이벤트가 높은 Pod 수와 함께 리소스 압박을 나타내는 경우, 플레이북 4단계에서 리소스 사용량 메트릭을 확인합니다. 높은 Pod 밀도와 MemoryPressure 또는 DiskPressure의 결합은 Node가 리소스 제약 상태임을 나타냅니다.

5. 플레이북 1단계의 Node 용량 및 할당 가능 값에서 Pod 제한에 도달하고 있는 것으로 나타나는 경우, Node의 maxPods 구성이 Node 크기 및 워크로드 요구 사항에 적합한지 확인합니다.

6. Cluster Autoscaler가 활성화된 경우, 플레이북 6단계에서 Autoscaler 상태를 확인하여 Pod 부하를 분배하기 위해 새 Node가 프로비저닝되어야 하는지, 그리고 스케일링이 발생하지 않는 이유를 확인합니다.

7. 높은 Pod 수가 다른 Node에 용량이 있는데도 이 Node에만 집중된 경우, 해당 특정 Node에 Pod를 강제하는 Pod 스케줄링 제약(nodeSelector, Affinity 규칙, Toleration)을 조사합니다.

**이벤트에서 근본 원인을 파악할 수 없는 경우**: Pod 스케줄링 정책 및 Affinity 규칙을 검토하고, 다른 Node의 Taint가 스케줄링을 방해하는지 확인하며, 클러스터 전체 용량 및 새 Node 추가 가능 여부를 검증하고, 과도한 Pod를 생성할 수 있는 워크로드 스케일링 구성을 확인합니다.
