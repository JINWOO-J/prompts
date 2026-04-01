---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/04-Workloads/InvalidMemoryCPURequests-workload.md)'
role: SRE / K8s Incident Response
origin: scoutflo
tags:
- capacity
- infrastructure
- invalidmemorycpurequests
- k8s-deployment
- k8s-namespace
- k8s-node
- k8s-pod
- k8s-service
- kubernetes
- sts
- workload
- workloads
---

---
title: Invalid Memory/CPU Requests - Workload
weight: 231
categories:
  - kubernetes
  - workload
---

# 잘못된 Memory/CPU 요청 (InvalidMemoryCPURequests-workload)

## 의미

Pod의 CPU 또는 메모리 요청이나 제한이 Node 또는 namespace 용량을 초과하는 값으로 설정되었거나, 리소스 정책을 위반하는 상태입니다(KubePodPending 알림 발생 가능). Admission 또는 스케줄링이 Pod 설정을 거부합니다. 리소스 사양 오류, 용량 불일치 또는 Quota 위반으로 Pod 스케줄링이 방해됩니다.

## 영향

Pod를 스케줄링할 수 없으며, Deployment가 Pod 생성에 실패합니다. 애플리케이션을 시작할 수 없고, 리소스 검증 오류가 워크로드 배포를 방해합니다. 서비스가 사용 불가능한 상태로 남고, KubePodPending 알림이 발생합니다. Pod가 Pending 상태로 남으며, 리소스 Admission 실패가 발생하고, 스케줄링 제약이 Pod 배치를 방해합니다.

## 플레이북

1. namespace <namespace>에서 deployment <deployment-name>을 describe하여 다음을 확인합니다:
   - 모든 컨테이너의 리소스 요청 및 제한
   - Pod 생성 실패 이유를 보여주는 Condition
   - 리소스 검증 오류 또는 스케줄링 실패를 보여주는 Event

2. namespace <namespace>에서 deployment <deployment-name>의 이벤트를 타임스탬프 순으로 조회하여 리소스 관련 오류 순서를 확인합니다.

3. namespace <namespace>에서 pod <pod-name>을 describe하여 잘못된 리소스 사양과 상세 오류 메시지를 확인합니다.

4. Node를 describe하고 할당된 리소스를 확인하여 현재 Node 용량을 검증합니다.

5. namespace <namespace>에서 ResourceQuota 및 LimitRange 객체를 describe하여 namespace 제약을 확인합니다.

## 진단

1. 플레이북의 Deployment 및 Pod 이벤트를 분석하여 리소스 검증 또는 스케줄링 오류를 파악합니다. 이벤트에 "Insufficient" 오류, "exceeds" 메시지 또는 Admission 거부가 표시되면, 이벤트 타임스탬프와 오류 세부 정보를 사용하여 구체적인 제약을 식별합니다.

2. 이벤트가 Pod 리소스 요청이 Node 용량을 초과함을 나타내면, 플레이북 4단계의 Node 용량을 분석합니다. 단일 Node도 Pod의 리소스 요청을 수용할 수 없으면 요청을 줄이거나 더 큰 Node를 추가합니다.

3. 이벤트가 LimitRange 위반을 나타내면, 플레이북 5단계의 LimitRange 설정을 검사합니다. Pod 요청이 LimitRange의 min/max 제약을 위반하면 namespace 정책에 맞게 요청을 조정합니다.

4. 이벤트가 ResourceQuota 위반을 나타내면, 플레이북 5단계의 Quota 상태를 확인합니다. Pod를 추가하면 namespace Quota 제한을 초과하는 경우 Quota를 늘리거나 기존 워크로드를 줄여야 합니다.

5. 이벤트가 최근 Deployment 수정을 나타내면, 수정 타임스탬프와 오류 발생 시점을 연관시킵니다. 검증 오류 전에 리소스 사양 변경이 발생했다면 최근 변경이 잘못된 값을 도입한 것입니다.

6. 이벤트가 최근 Node 변경을 나타내면, Node 용량이 감소했는지 확인합니다. 오류 전에 Node 제거 또는 크기 조정 이벤트가 발생했다면 클러스터 용량 감소로 이전에 유효했던 요청이 스케줄링 불가능해진 것입니다.

7. 이벤트가 설정 계산 문제를 나타내면, Deployment 스펙의 리소스 요청 값을 확인합니다. 요청이 비합리적으로 큰 경우(예: 100Mi 대신 100Gi 메모리와 같은 오타) 사양 오류를 수정합니다.

**상관관계를 찾을 수 없는 경우**: 검색 범위를 확장하고(1시간→2시간), Deployment 리소스 사양의 계산 오류를 검토하고, namespace 리소스 Quota 제한을 확인하고, Node 할당 가능 리소스의 용량 제약을 검사하고, 리소스 요청이 어떤 Node의 용량도 초과하는지 확인하고, 리소스 정책 위반을 확인하고, 시간에 따른 클러스터 리소스 용량 변화를 검토합니다. 잘못된 리소스 오류는 단일 변경 이벤트에서 즉시 보이지 않는 누적 용량 감소 또는 Quota 제약으로 인해 발생할 수 있습니다.
