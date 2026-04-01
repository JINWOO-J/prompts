---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/04-Workloads/KubeDaemonSetMisScheduled-daemonset.md)'
role: SRE / K8s Incident Response
origin: scoutflo
tags:
- daemonset
- infrastructure
- k8s-daemonset
- k8s-namespace
- k8s-node
- k8s-pod
- k8s-service
- kubedaemonsetmisscheduled
- workloads
---

---
title: Kube DaemonSet MisScheduled
weight: 20
---

# DaemonSet 잘못된 스케줄링 (KubeDaemonSetMisScheduled)

## 의미

DaemonSet Pod가 스케줄링되어서는 안 되는 Node에서 실행되고 있는 상태입니다(DaemonSet 스케줄링 관련 알림 발생). Node Selector, Toleration 또는 Affinity 규칙이 잘못 설정되었거나, DaemonSet 설정을 업데이트하지 않고 Node Taint 및 Label이 변경되었기 때문입니다.
kubectl에서 DaemonSet의 잘못 스케줄된 수가 표시되고, Pod가 잘못된 Node에서 실행되며, Node Taint/Label이 DaemonSet Selector 요구사항과 불일치할 수 있습니다. 이는 워크로드 플레인에 영향을 미치며 DaemonSet 요구사항과 Node 설정 간의 설정 불일치를 나타냅니다. 주로 설정 드리프트, Node Pool 변경 또는 Feature Discovery Label 업데이트가 원인이며, Node Feature Discovery Label 변경이 Selector 불일치를 유발할 수 있습니다.

## 영향

DaemonSet 잘못된 스케줄링 알림이 발생하며, 서비스 저하 또는 사용 불가가 발생합니다. 의도하지 않은 Node에서 과도한 리소스 사용이 발생하고, DaemonSet Pod가 잘못된 Node에서 실행됩니다. DaemonSet 원하는 상태가 불일치하며, Pod가 Eviction되거나 올바르게 실행되지 않을 수 있습니다. 시스템 구성 요소가 잘못 설정될 수 있고, 부적절한 Node에서 리소스가 낭비됩니다.

## 플레이북

1. namespace <namespace>에서 DaemonSet <daemonset-name>을 describe하여 다음을 확인합니다:
   - 스케줄된 수, 준비 수 및 잘못 스케줄된 수
   - Node Selector, Toleration 및 Affinity 규칙 설정
   - 스케줄링 불일치를 보여주는 Condition
   - 스케줄링 관련 문제를 보여주는 Event

2. namespace <namespace>에서 DaemonSet <daemonset-name>의 이벤트를 타임스탬프 순으로 조회하여 잘못된 스케줄링 문제 순서를 확인합니다.

3. namespace <namespace>에서 label app=<daemonset-label>로 DaemonSet에 속한 Pod를 조회하고 Pod를 describe하여 잘못된 Node에서 실행 중인 Pod를 식별합니다.

4. DaemonSet Pod가 잘못 스케줄링된 node <node-name>을 describe하고 Node Taint 및 Label을 확인하여 Node 설정 불일치를 검증합니다.

5. kube-system namespace에서 node-feature-discovery Pod를 확인하여 DaemonSet Selector가 사용하는 Node Label에 영향을 미칠 수 있는 도구를 검증합니다.

## 진단

1. 플레이북의 DaemonSet 이벤트와 Pod 분포를 분석하여 잘못된 스케줄링 패턴을 파악합니다. DaemonSet의 nodeSelector 및 Node Affinity 규칙을 기반으로 DaemonSet Pod가 실행되어서는 안 되는 Node를 식별합니다.

2. 잘못 스케줄된 Pod가 nodeSelector에 의해 제외되어야 하는 Node에서 실행 중이면, Node Label과 DaemonSet nodeSelector 요구사항을 비교합니다. Pod가 스케줄링된 후 Node의 Label이 변경되었을 수 있습니다. Label 변경 전에 스케줄링된 Pod는 더 이상 Selector와 일치하지 않더라도 계속 실행됩니다.

3. 잘못 스케줄된 Pod가 Taint된 Node에서 실행 중이면, DaemonSet Toleration이 지나치게 허용적인지 확인합니다. operator "Exists"이고 key가 없는 Toleration은 모든 Taint와 일치합니다. 의도하지 않은 Node에서 스케줄링을 허용하는 Toleration이 추가되었는지 확인합니다.

4. Node Feature Discovery 또는 유사한 도구가 사용 중이면, 자동 Label 업데이트로 Node가 DaemonSet의 Selector와 일치하거나 불일치하게 되었는지 확인합니다. 동적 Label 변경은 현재 Node 상태에 비해 Pod가 잘못 스케줄링되게 할 수 있습니다.

5. 잘못된 스케줄링이 많은 Node에 걸쳐 체계적이면, DaemonSet의 스케줄링 제약이 잘못 설정되었을 수 있습니다. nodeSelector, nodeAffinity 및 Toleration이 함께 의도한 Node 타겟팅을 올바르게 표현하는지 확인합니다. 광범위한 Toleration과 함께 nodeSelector가 누락되면 모든 Node에 스케줄링됩니다.

6. 잘못된 스케줄링이 특정 Node에 국한되면, 해당 Node에서 최근 Taint가 제거되었거나 DaemonSet의 요구사항과 일치하는 Label이 추가되었는지 확인합니다. 현재 Node 설정과 의도한 Node Pool 멤버십을 비교합니다.

7. DaemonSet Pod가 리소스 경합 또는 정책 위반을 유발하는 Node에 존재하면, DaemonSet 스케줄링 제약을 업데이트하거나 잘못 스케줄된 Pod를 수동으로 삭제해야 할 수 있습니다. 제약 변경 전에 Node에 스케줄링된 Pod는 자동으로 Eviction되지 않습니다.
