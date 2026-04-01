---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/02-Nodes/NodeClockSkewDetected-node.md)'
role: SRE / K8s Incident Response
origin: scoutflo
tags:
- database
- infrastructure
- k8s-node
- k8s-pod
- k8s-service
- kubernetes
- node
- nodeclockskewdetected
- nodes
---

---
title: Node Clock Skew Detected — Node 시간 편차 감지
weight: 35
categories: [kubernetes, node]
---

# NodeClockSkewDetected

## 의미

Node 시계가 편차가 있거나 동기화되지 않았습니다(NodeClockSkewDetected, NodeClockNotSynchronising, NodeClockSkew 알림 발생). 시스템 시계가 정확한 시간 소스에서 벗어났거나 NTP 동기화가 실패하고 있습니다.
 Node 시간이 참조 시간 소스와 허용 가능한 임계값 이상으로 차이가 나며, 시간 의존적 작업이 신뢰할 수 없게 됩니다. 이는 모든 워크로드의 시간 민감 작업에 영향을 미칩니다. 인증서 검증이 실패하고, 인증 토큰이 잘못 만료되며, 로그 타임스탬프가 잘못되고, 분산 시스템 조정이 실패합니다.

## 영향

NodeClockSkewDetected 알림이 발생하고, TLS 인증서 검증이 실패할 수 있습니다. JWT 토큰이 만료되었거나 아직 유효하지 않은 것으로 거부됩니다. 로그 타임스탬프가 잘못되어 디버깅이 어려워집니다. 분산 합의가 실패하고(etcd, 데이터베이스), 스케줄러 타이밍이 잘못됩니다. Cron Job이 잘못된 시간에 실행되고, Lease 만료가 잘못 계산됩니다. Kubernetes Node 하트비트가 영향받을 수 있으며, 인증 및 권한 부여 실패가 증가합니다.

## 플레이북

1. Node `<node-name>`을 조회하고 정확한 참조와 비교하여 현재 시스템 시간을 확인합니다.

2. Node에서 NTP 서비스 상태(chrony, ntpd, systemd-timesyncd)를 확인합니다.

3. NTP 서버 구성을 확인하고 Node가 구성된 시간 서버에 도달할 수 있는지 검증합니다.

4. Stratum 레벨 및 참조로부터의 오프셋을 포함한 NTP 동기화 문제를 확인합니다.

5. 가상화 레이어(하이퍼바이저)가 시간 동기화에 영향을 미치는지 확인합니다.

6. 커널 시계 드리프트 문제 또는 하드웨어 시계 문제를 확인합니다.

7. 시간 민감 검증을 실행하여 Pod가 영향받는지 확인합니다.

## 진단

NTP 데몬 상태를 확인하고 서비스가 실행 중이며 적극적으로 동기화하고 있는지 검증합니다. 서비스 상태 및 동기화 상태 출력을 근거로 사용합니다.

NTP 서버 접근성을 확인하고 시간 서버로의 네트워크 연결(UDP 123의 NTP 트래픽)을 확인합니다. 네트워크 연결 테스트 및 방화벽 규칙을 근거로 사용합니다.

시계 오프셋 추세를 분석하고 시계가 지속적으로 드리프트하는지(하드웨어 문제) 또는 갑자기 점프했는지(구성 변경, VM 마이그레이션) 판단합니다. 시간 오프셋 이력을 근거로 사용합니다.

Node 간 시계를 비교하고 시계 편차가 단일 Node에 영향을 미치는지 또는 여러 Node에 영향을 미치는지(NTP 서버 문제 시사) 확인합니다. Node 간 시간 비교를 근거로 사용합니다.

가상화 시간 동기화 설정을 확인하고 게스트 추가 기능이나 하이퍼바이저 시간 동기화가 NTP와 충돌하는지 검증합니다. VM 구성 및 하이퍼바이저 설정을 근거로 사용합니다.

**지정된 시간 범위 내에서 상관관계를 찾을 수 없는 경우**: NTP 서비스를 재시작하고, 신뢰할 수 있는 서버로 NTP를 재구성하며, 하드웨어 시계 배터리 문제를 확인하고, VM 시간 동기화 설정을 검증합니다. 클러스터 전용 시간 서버를 고려하고, 윤초 처리 문제를 확인합니다.
