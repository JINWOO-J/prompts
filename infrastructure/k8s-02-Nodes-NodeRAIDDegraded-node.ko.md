---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/02-Nodes/NodeRAIDDegraded-node.md)'
role: SRE / K8s Incident Response
origin: scoutflo
tags:
- infrastructure
- k8s-node
- kubernetes
- node
- noderaiddegraded
- nodes
- performance
---

---
title: Node RAID Degraded — Node RAID 저하
weight: 45
categories: [kubernetes, node]
---

# NodeRAIDDegraded

## 의미

Node RAID 어레이가 저하 상태입니다(NodeRAIDDegraded, NodeRAIDDiskFailure 알림 발생). RAID 어레이의 하나 이상의 디스크가 실패했거나 제거되었으며, 어레이가 감소된 이중화로 운영되고 있습니다.
 Node 메트릭에서 RAID 어레이가 최적 상태가 아닌 것으로 나타나고, 데이터 이중화가 손상되었으며, 추가 디스크 장애 시 데이터 손실이 발생할 수 있습니다. 이는 Node의 데이터 내구성에 영향을 미칩니다. 즉각적인 디스크 교체가 필요하며, 리빌드 중 성능이 저하될 수 있습니다.

## 영향

NodeRAIDDegraded 알림이 발생하고, 데이터 이중화가 상실됩니다. 추가 디스크 장애 시 데이터 손실이 발생합니다. 성능이 저하될 수 있으며, 디스크 교체 후 RAID 리빌드가 필요합니다. 잠재적 데이터 손상 위험이 있으며, Node를 유지보수 일정에 포함해야 합니다. 가능하면 워크로드를 마이그레이션해야 합니다.

## 플레이북

1. Node `<node-name>`을 조회하고 어떤 RAID 어레이가 저하되었는지 파악합니다.

2. mdadm 또는 벤더별 도구를 사용하여 RAID 상태를 확인하고 실패한 디스크를 파악합니다.

3. 디스크 시리얼 번호 및 슬롯 정보를 사용하여 어떤 물리 디스크가 실패했는지 확인합니다.

4. 핫 스페어 디스크가 사용 가능하고 리빌드가 자동으로 시작되었는지 확인합니다.

5. 최소한의 워크로드 중단으로 디스크 교체를 계획합니다.

6. 리빌드 후 중요 볼륨의 데이터 무결성을 확인합니다.

7. 디스크 교체 중 Node를 다른 Node로 drain하는 것을 고려합니다.

## 진단

RAID 어레이 멤버 상태 및 디스크 SMART 데이터를 검사하여 어떤 디스크가 실패했는지 파악합니다. mdadm 상태 및 smartctl 출력을 근거로 사용합니다.

나머지 디스크의 SMART 속성에서 임박한 장애를 나타낼 수 있는 경고 징후를 확인합니다. SMART 로그 및 예측 장애 지표를 근거로 사용합니다.

핫 스페어가 사용 가능한 경우 RAID 리빌드가 진행 중인지 확인합니다. 리빌드 진행률 및 예상 완료 시간을 근거로 사용합니다.

근본 원인을 확인합니다: 전원 문제, 열 문제, 진동, 펌웨어 버그. 시스템 로그 및 환경 모니터링을 근거로 사용합니다.

RAID 레벨 및 실패한 디스크 수에 따른 데이터 위험을 평가합니다(RAID 1 또는 5는 1개 장애 허용, RAID 6은 2개 장애 허용). RAID 구성을 근거로 사용합니다.

**지정된 시간 범위 내에서 상관관계를 찾을 수 없는 경우**: 실패한 디스크를 즉시 교체하고, 나머지 디스크가 정상인지 확인하며, 리빌드 중 Node 대피를 고려하고, 디스크 벤더 및 모델의 알려진 문제를 검토하며, 더 탄력적인 RAID 레벨로 업그레이드를 고려합니다.
