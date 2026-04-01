---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/04-Workloads/KubeDaemonSetNotReady-daemonset.md)'
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
- kubedaemonsetnotready
- kubernetes
- logging
- monitoring
- networking
- security
- sts
- workloads
---

---
title: Kube DaemonSet Not Ready
weight: 47
categories: [kubernetes, daemonset]
---

# DaemonSet가 Ready 상태가 아님 (KubeDaemonSetNotReady)

## 의미

DaemonSet Pod가 예상 Node에서 Ready 상태가 아닌 상태입니다(KubeDaemonSetNotReady 알림 발생). DaemonSet Pod가 하나 이상의 Node에서 시작에 실패하거나, 크래시하거나, Readiness 검사를 통과하지 못하기 때문입니다.
DaemonSet 상태에 원하는 것보다 적은 Ready Pod가 표시되며, 영향받는 Node에서 DaemonSet이 제공하는 Node 수준 기능을 사용할 수 없습니다. DaemonSet이 제공하는 기능에 따라 클러스터 기능에 영향을 미치며, 영향받는 Node에서 모니터링, 로깅, 네트워킹 또는 보안 기능이 누락될 수 있습니다.

## 영향

KubeDaemonSetNotReady 알림이 발생하며, 영향받는 Node에서 DaemonSet 기능이 누락됩니다. CNI 플러그인인 경우 해당 Node에서 네트워킹이 중단되고, 로그 수집기인 경우 로그가 수집되지 않으며, 모니터링 에이전트인 경우 Metrics가 누락되고, 보안 에이전트인 경우 보안 공백이 발생합니다. Node 기능이 저하되며, DaemonSet 서비스에 의존하는 새로 스케줄링된 Pod가 실패할 수 있습니다.

## 플레이북

1. namespace `<namespace>`에서 DaemonSet `<daemonset-name>`을 조회하여 Ready 상태가 아닌 Pod 수와 해당 Node를 확인합니다.

2. DaemonSet Pod를 조회하여 어떤 Pod가 Ready 상태가 아닌지와 해당 상태를 확인합니다.

3. Ready 상태가 아닌 Pod의 이벤트를 조회하여 실패 원인을 파악합니다.

4. 실패하는 DaemonSet Pod의 로그를 조회하여 애플리케이션 수준 문제를 파악합니다.

5. 영향받는 Node의 Node Condition을 확인합니다(Ready, MemoryPressure, DiskPressure).

6. Pod가 실행되어야 하는 Node에서 DaemonSet Toleration이 Node Taint와 일치하는지 확인합니다.

7. 리소스 요청과 Node 사용 가능 리소스를 비교합니다.

## 진단

Pod 상태를 근거로 Pod 실패를 분류합니다: CrashLoopBackOff는 애플리케이션 문제를 나타내고, Pending은 스케줄링 문제를 나타내며, ImagePullBackOff는 이미지 문제를 나타냅니다.

영향받는 Node와 정상 Node를 비교하여 Node별 문제(리소스, Taint, Label)를 파악합니다. Node 특성과 Pod 배치를 근거로 사용합니다.

DaemonSet 업데이트가 진행 중이고 Pod가 롤아웃되어 일시적으로 Not Ready 상태인지 확인합니다. 롤아웃 상태와 업데이트 전략을 근거로 사용합니다.

실패를 유발했을 수 있는 DaemonSet 스펙 변경(리소스 변경, 이미지 변경, 설정 변경)을 확인합니다. DaemonSet 리비전 이력을 근거로 사용합니다.

DaemonSet Pod 작동을 방해할 수 있는 디스크 압박 또는 메모리 압박과 같은 Node별 문제를 확인합니다. Node Condition을 근거로 사용합니다.

지정된 시간 범위 내에서 상관관계를 찾을 수 없는 경우: 새 Taint에 대한 DaemonSet Toleration을 확인하고, 모든 Node에서 이미지가 사용 가능한지 확인하고, 리소스 제약을 검토하고, PodSecurityPolicy 또는 Admission Controller 차단을 확인하고, Node별 설정을 검토합니다.
