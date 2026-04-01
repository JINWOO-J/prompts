---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/09-Resource-Management/KubeQuotaAlmostFull-namespace.md)'
role: Kubernetes SRE
origin: scoutflo
extract_date: 2026-03-05
tags:
- capacity
- infrastructure
- k8s-deployment
- k8s-namespace
- k8s-pod
- kubequotaalmostfull
- management
- namespace
- performance
- resource
- scaling
- sts
---

---
title: Kube Quota Almost Full - Quota 거의 소진
weight: 20
---

# KubeQuotaAlmostFull

## 의미

Namespace의 리소스 쿼터가 제한에 근접하고 있습니다(KubeQuotaAlmostFull 알림 트리거). 리소스 사용량(CPU, 메모리, Pod 등)이 구성된 쿼터 최대값에 가까운 것이 원인입니다.

## 영향

KubeQuotaAlmostFull 알림 발생, 향후 배포 불가 가능, 스케일링 작업 실패 가능, 새 Pod 생성 불가, 리소스 쿼터 사용량이 제한에 근접, Namespace 용량 제약이 심각해짐, 애플리케이션이 수요에 맞게 스케일링 불가. ResourceQuota 리소스에 현재 사용량이 하드 제한에 근접하는 것으로 표시됩니다.

## 플레이북

1. namespace `<namespace>`에서 ResourceQuota `<quota-name>`을 describe하여 상태를 확인하고 모든 리소스 유형의 현재 사용량 대비 하드 제한을 확인합니다.
2. namespace `<namespace>`의 이벤트를 타임스탬프 순으로 조회하여 쿼터 관련 이벤트와 리소스 할당 경고를 식별합니다.
3. namespace `<namespace>`의 Pod 리소스를 나열하고 리소스 요청을 집계하여 주요 리소스 소비자를 식별합니다.
4. namespace `<namespace>`의 지난 24시간 리소스 사용량 추세 메트릭을 조회하여 증가 패턴을 식별합니다.
5. 최근 배포 또는 스케일링 작업이 쿼터 사용량 증가에 기여했는지 Deployment 및 HPA 스케일링 이력을 확인합니다.
6. namespace `<namespace>`의 모든 리소스를 나열하고 정리할 수 있는 미사용 또는 불필요한 리소스를 확인합니다.

## 진단

1. 플레이북의 ResourceQuota 상태를 분석하여 어떤 리소스 유형이 제한에 근접하는지 식별합니다. 각 리소스 유형(cpu, memory, pods 등)의 현재 사용량과 하드 제한을 비교하여 어떤 것이 먼저 소진될지 판단합니다.

2. CPU 또는 메모리 요청이 제한에 근접하면, 플레이북의 Pod 리소스 요청을 분석합니다. 가장 큰 요청을 가진 Pod를 식별하고 해당 요청이 실제 사용량과 일치하는지 평가합니다.

3. Pod 수가 제한에 근접하면, 플레이북에서 실행 중인 Pod를 계산합니다. Pod 수가 필요한 워크로드를 나타내는지 또는 고아 Pod, 완료된 Job, 실패한 Pod를 정리할 수 있는지 판단합니다.

4. 이벤트에 최근 스케일링 활동 또는 배포가 표시되면, 쿼터 증가를 해당 작업과 상관 분석합니다.

5. 명확한 트리거 이벤트 없이 쿼터 사용량이 점진적으로 증가한 경우, 시간에 따른 Namespace 사용량 추세를 조사합니다. 정상적인 워크로드 증가는 용량 계획의 일환으로 주기적인 쿼터 증가가 필요할 수 있습니다.

6. 여러 리소스 유형이 동시에 제한에 근접하면, Namespace에 포괄적인 쿼터 증가가 필요할 수 있습니다.

7. 쿼터 제한이 적절하지만 사용량이 높으면, 워크로드 효율성을 평가합니다. 실제 사용량 기반으로 Pod 리소스 요청을 적정 크기로 조정하면 워크로드 기능을 변경하지 않고 상당한 쿼터 용량을 회수할 수 있습니다.
