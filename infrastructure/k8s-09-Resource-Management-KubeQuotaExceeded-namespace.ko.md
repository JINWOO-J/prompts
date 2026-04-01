---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/09-Resource-Management/KubeQuotaExceeded-namespace.md)'
role: Kubernetes SRE
origin: scoutflo
extract_date: 2026-03-05
tags:
- infrastructure
- k8s-deployment
- k8s-namespace
- k8s-pod
- k8s-service
- kubequotaexceeded
- kubernetes
- management
- namespace
- performance
- resource
- scaling
- sts
---

---
title: Kube Quota Exceeded - Quota 초과
weight: 20
---

# KubeQuotaExceeded

## 의미

Namespace의 리소스 쿼터가 하드 제한을 초과했습니다(KubeQuotaExceeded 알림 트리거). 리소스 사용량(CPU, 메모리, Pod 등)이 구성된 쿼터 최대값에 도달하거나 초과한 것이 원인입니다.

## 영향

KubeQuotaExceeded 알림 발생, Kubernetes에서 리소스 생성 불가, 새 Pod 생성 불가, Deployment 스케일링 실패, 리소스 생성 차단, Namespace 작업 심각하게 제한, 애플리케이션이 수요에 맞게 스케일링 불가, 서비스 저하 또는 불가용. ResourceQuota 리소스에 현재 사용량이 하드 제한을 초과하는 것으로 무기한 표시되며, Namespace 이벤트에 'exceeded quota' 또는 'Forbidden' 오류가 표시됩니다.

## 플레이북

1. namespace `<namespace>`에서 ResourceQuota `<quota-name>`을 describe하여 상태를 확인하고 모든 리소스 유형의 현재 사용량 대비 하드 제한을 확인하여 어떤 쿼터가 초과되었는지 식별합니다.
2. namespace `<namespace>`의 이벤트를 타임스탬프 순으로 조회하여 'exceeded quota', 'Forbidden', 'ResourceQuota' 등 쿼터 관련 오류를 식별합니다.
3. namespace `<namespace>`의 Pod 리소스를 나열하고 리소스 요청을 집계하여 주요 리소스 소비자를 식별합니다.
4. namespace `<namespace>`에서 ResourceQuota `<quota-name>`을 조회하고 리소스 쿼터 구성을 확인하여 쿼터 제한과 범위를 검증합니다.
5. 쿼터 소진을 트리거했을 수 있는 최근 리소스 생성 또는 스케일링 작업을 Deployment 및 HPA 스케일링 이력을 확인하여 검증합니다.
6. namespace `<namespace>`의 모든 리소스를 나열하고 쿼터를 소비하는 미사용 또는 불필요한 리소스를 확인합니다.

## 진단

1. 플레이북의 Namespace 이벤트를 분석하여 쿼터 위반 세부사항을 식별합니다. "exceeded quota" 또는 "Forbidden"을 보여주는 이벤트는 어떤 리소스 유형이 제한을 초과했는지와 얼마나 초과했는지를 지정합니다.

2. 이벤트가 쿼터 초과로 인한 Pod 생성 실패를 나타내면, 어떤 작업이 Pod 생성을 시도했는지 식별합니다. 일반적인 소스: Deployment 스케일업, Job 시작, CronJob 트리거, HPA 레플리카 추가.

3. 이벤트가 CPU 또는 메모리 요청이 쿼터를 초과했음을 나타내면, 플레이북에서 가장 큰 리소스 요청을 가진 Pod를 분석합니다. 실제 사용량보다 요청이 크게 큰 Pod는 과도하게 프로비저닝되어 불필요하게 쿼터를 소비하고 있을 수 있습니다.

4. 쿼터가 최근에 초과된 경우(이벤트에 최근 타임스탬프), 배포 또는 스케일링 이벤트와 상관 분석합니다.

5. 쿼터가 초과되었지만 모든 보이는 Pod가 실행 중이면, Pod 이외의 리소스 유형(PersistentVolumeClaim, Service, ConfigMap 등)이 쿼터 제한될 수 있는지 확인합니다.

6. Namespace에 LimitRange가 구성된 경우, 명시적 리소스 요청이 없는 Pod에 기본값이 할당됩니다. 이 기본값이 필요 이상으로 높아 예상치 못한 쿼터 소비를 유발할 수 있습니다.

7. 쿼터 제한이 합법적인 워크로드 요구에 비해 너무 낮으면, 현재 쿼터 구성을 실제 워크로드 요구사항과 비교합니다. 쿼터를 증가시켜야 하는지 또는 실제 사용 패턴에 기반하여 워크로드 리소스 요청을 적정 크기로 조정해야 하는지 고려합니다.
