---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/02-Nodes/NodeExporterDown-node.md)'
role: SRE / K8s Incident Response
origin: scoutflo
tags:
- alerting
- capacity
- infrastructure
- k8s-daemonset
- k8s-namespace
- k8s-node
- k8s-pod
- k8s-service
- kubernetes
- monitoring
- node
- nodeexporterdown
- nodes
- observability
- rds
---

---
title: Node Exporter Down — Node Exporter 중단
weight: 39
categories: [kubernetes, node]
---

# NodeExporterDown

## 의미

Node Exporter가 실행되지 않거나 응답하지 않습니다(NodeExporterDown 알림 발생). Node 수준 메트릭을 수집하는 모니터링 에이전트가 실패했거나 접근할 수 없습니다. Prometheus가 Node 메트릭을 스크레이핑할 수 없고, Node 상태 가시성이 상실되며, Node 수준 알림이 작동하지 않습니다.
 이는 클러스터 관측성에 영향을 미칩니다. Node 문제가 감지되지 않을 수 있고, 용량 계획 데이터가 불완전하며, 문제 해결이 어려워집니다.

## 영향

NodeExporterDown 알림이 발생하고, Node 수준 메트릭을 사용할 수 없습니다. CPU, 메모리, 디스크, 네트워크 모니터링이 작동하지 않습니다. 데이터 누락으로 인해 다른 Node 알림이 발생할 수 없으며, 대시보드에 공백이 나타납니다. 용량 계획에 영향을 미치고, 이 Node에 대한 사전 알림이 비활성화됩니다. 문제 해결에 수동 검사가 필요하며, SRE 가시성이 감소합니다.

## 플레이북

1. 모니터링 네임스페이스(일반적으로 prometheus, monitoring 또는 kube-system)에서 node-exporter Pod 또는 DaemonSet 상태를 확인합니다.

2. kubectl get pods -o wide를 사용하여 영향받는 Node에서 node-exporter Pod가 실행 중인지 확인합니다.

3. 작동을 방해하는 오류에 대해 node-exporter Pod 로그를 조회합니다.

4. Prometheus ServiceMonitor 또는 스크레이핑 구성이 올바른 포트와 경로를 대상으로 하는지 확인합니다.

5. Prometheus에서 node-exporter 포트(일반적으로 9100)로의 네트워크 연결을 확인합니다.

6. node-exporter DaemonSet Toleration이 Taint된 Node를 포함한 모든 Node에서 스케줄링을 허용하는지 확인합니다.

7. NetworkPolicy가 Prometheus의 node-exporter 스크레이핑을 차단하는지 확인합니다.

## 진단

영향받는 Node에서 Pod 존재 여부 및 상태를 확인하고, Pod가 누락되었는지, 크래시되었는지, 대기 중인지 파악합니다. Pod 상태 및 이벤트를 근거로 사용합니다.

DaemonSet Toleration을 확인하고 Node에 node-exporter 스케줄링을 방해하는 Taint가 있는지 검증합니다. Node Taint 및 DaemonSet 스펙을 근거로 사용합니다.

Prometheus 스크레이핑 구성을 확인하고 node-exporter 엔드포인트에 대한 서비스 디스커버리가 올바르게 작동하는지 확인합니다. Prometheus 타겟 페이지 및 서비스 디스커버리를 근거로 사용합니다.

NetworkPolicy를 확인하고 Prometheus 네임스페이스에서 포트 9100으로의 인그레스가 허용되는지 검증합니다. NetworkPolicy 규칙 및 연결 테스트를 근거로 사용합니다.

node-exporter Pod 로그에서 시작 실패(포트 이미 사용 중, 권한 거부, 구성 오류)를 분석합니다. Pod 로그를 근거로 사용합니다.

**지정된 시간 범위 내에서 상관관계를 찾을 수 없는 경우**: node-exporter Pod를 재시작하고, DaemonSet Toleration을 업데이트하며, NetworkPolicy 규칙을 수정하고, ServiceMonitor 구성을 확인하며, Pod 스케줄링을 방해하는 리소스 제약을 확인합니다.
