---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/04-Workloads/KubeDaemonSetRolloutStuck-daemonset.md)'
role: SRE / K8s Incident Response
origin: scoutflo
tags:
- capacity
- daemonset
- infrastructure
- k8s-daemonset
- k8s-namespace
- k8s-pod
- k8s-service
- kubedaemonsetrolloutstuck
- workloads
---

---
title: Kube DaemonSet Rollout Stuck
weight: 20
---

# DaemonSet 롤아웃 중단 (KubeDaemonSetRolloutStuck)

## 의미

DaemonSet 업데이트가 Pod 교체를 기다리며 중단된 상태입니다(DaemonSet 롤아웃 관련 알림 발생). 롤링 업데이트 과정에서 새 Pod를 스케줄링할 수 없거나 이전 Pod를 종료할 수 없기 때문입니다.
DaemonSet의 롤아웃 상태가 중단되고, Pod가 Pending 또는 Terminating 상태로 남으며, DaemonSet 이벤트에 FailedCreate, FailedScheduling 또는 FailedDelete 오류가 표시됩니다. 이는 워크로드 플레인에 영향을 미치며 스케줄링 제약, 리소스 가용성 문제 또는 Pod 종료 문제로 DaemonSet 업데이트가 방해됩니다. 주로 지속적인 리소스 제약, 잘못 설정된 Affinity 규칙 또는 클러스터 용량 제한이 원인이며, PodDisruptionBudget 제약이 Pod 종료를 방해할 수 있습니다.

## 영향

DaemonSet 롤아웃 알림이 발생하며, DaemonSet이 롤링 업데이트를 완료할 수 없습니다. 이전 Pod가 오래된 설정으로 계속 실행되고, 새 Pod를 스케줄링할 수 없습니다. 서비스 저하 또는 사용 불가가 발생하며, DaemonSet 원하는 상태가 불일치합니다. Pod가 Terminating 상태에 머물고, 업데이트 전략이 진행할 수 없으며, 시스템 구성 요소가 일관되지 않은 버전으로 실행될 수 있습니다.

## 플레이북

1. namespace <namespace>에서 DaemonSet <daemonset-name>을 describe하여 다음을 확인합니다:
   - 롤아웃 상태, 원하는 스케줄 수 및 준비 수
   - 업데이트 전략 설정
   - 롤아웃이 중단된 이유를 보여주는 Condition
   - FailedCreate, FailedScheduling 또는 FailedDelete 오류를 보여주는 Event

2. namespace <namespace>에서 DaemonSet <daemonset-name>의 이벤트를 타임스탬프 순으로 조회하여 롤아웃 문제 순서를 확인합니다.

3. namespace <namespace>에서 label app=<daemonset-label>로 DaemonSet에 속한 Pod를 조회하고 Pod를 describe하여 Pending 또는 Terminating 상태의 Pod를 식별합니다.

4. namespace <namespace>에서 DaemonSet <daemonset-name>의 롤아웃 상태를 확인하여 롤아웃이 진행 중인지 중단되었는지 확인합니다.

5. DaemonSet Pod가 스케줄링되어야 하는 Node에 대해 node <node-name>을 describe하여 Node 가용성과 Condition을 확인합니다.

6. namespace <namespace>에서 PodDisruptionBudget 리소스를 describe하여 Pod 종료를 방해하는 제약이 있는지 확인합니다.

## 진단

1. 플레이북의 DaemonSet 이벤트를 분석하여 롤아웃 차단 요인을 파악합니다. "FailedCreate" 이벤트는 Pod 생성 문제를 나타냅니다. "FailedScheduling" 이벤트는 리소스 또는 배치 제약을 나타냅니다. "FailedDelete" 이벤트는 새 Pod를 위한 공간을 만들기 위해 Pod를 종료할 수 없음을 나타냅니다.

2. 이벤트가 특정 Node에서 Pod 생성 실패를 나타내면, 해당 Node의 사용 가능한 리소스와 Condition을 확인합니다. RollingUpdate 전략을 사용하는 DaemonSet은 같은 Node에서 새 Pod를 생성하기 전에 이전 Pod를 종료해야 합니다. 새 Pod의 리소스 요청이 더 높으면 다른 워크로드와 함께 배치되지 않을 수 있습니다.

3. 이벤트가 스케줄링 실패를 나타내면(InsufficientCPU, InsufficientMemory), 새 DaemonSet Pod 템플릿이 대상 Node에서 사용 가능한 것보다 더 많은 리소스를 요구하는 것입니다. 새 Pod 리소스 요청과 Node 할당 가능 리소스에서 기존 Pod 요청을 뺀 값을 비교합니다.

4. 이벤트가 Pod가 Terminating 상태에 머물러 있음을 나타내면, 이전 Pod의 Finalizer 또는 Eviction을 방해하는 PodDisruptionBudget 제약을 확인합니다. maxUnavailable=1인 DaemonSet은 하나의 Pod 종료라도 차단되면 진행할 수 없습니다.

5. Pod가 생성되었지만 Ready 상태가 되지 않으면, 플레이북의 Pod 로그와 컨테이너 상태를 분석합니다. 롤아웃은 다음 이전 Pod를 종료하기 전에 새 Pod가 Ready 상태가 되기를 기다립니다. Readiness Probe 실패 또는 애플리케이션 시작 문제가 롤아웃을 차단합니다.

6. 이벤트가 Node 관련 문제를 나타내면(NodeNotReady, Node Taint), Node Condition과 Taint가 DaemonSet Toleration과 일치하는지 확인합니다. 롤아웃 중 추가된 새 Taint가 이전 Pod가 실행 중이었더라도 새 Pod의 스케줄링을 방해할 수 있습니다.

7. 명확한 이벤트 패턴이 없으면, DaemonSet의 updateStrategy 설정을 확인합니다. maxUnavailable 및 maxSurge 설정이 Pod 교체를 허용하는지 확인합니다. 또한 namespace의 PodDisruptionBudget이 업데이트에 필요한 Pod Eviction을 차단하는지 확인합니다.
