---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/09-Resource-Management/KubeQuotaFullyUsed-namespace.md)'
role: Kubernetes SRE
origin: scoutflo
extract_date: 2026-03-05
tags:
- capacity
- infrastructure
- k8s-deployment
- k8s-namespace
- k8s-pod
- k8s-service
- kubequotafullyused
- management
- namespace
- performance
- resource
- scaling
- sts
---

---
title: Kube Quota Fully Used - Quota 완전 소진
weight: 20
---

# KubeQuotaFullyUsed

## 의미

Namespace의 리소스 쿼터가 하드 제한에 도달했습니다(KubeQuotaFullyUsed 알림 트리거). 리소스 사용량(CPU, 메모리, Pod 등)이 구성된 쿼터 최대값에 도달한 것이 원인입니다.

## 영향

KubeQuotaFullyUsed 알림 발생, 새 앱 설치 불가 가능, 리소스 생성 차단, Deployment 스케일링 실패, Namespace가 용량 제한에 도달, 애플리케이션이 수요에 맞게 스케일링 불가, 새 워크로드에 대한 서비스 저하 또는 불가용, 리소스 생성 및 스케일링 작업 완전 차단. ResourceQuota 리소스에 현재 사용량이 하드 제한과 일치하는 것으로 무기한 표시됩니다.

## 플레이북

1. namespace `<namespace>`에서 ResourceQuota `<quota-name>`을 describe하여 상태를 확인하고 모든 리소스 유형의 현재 사용량 대비 하드 제한을 확인하여 어떤 쿼터가 완전히 사용되었는지 식별합니다.
2. namespace `<namespace>`의 이벤트를 타임스탬프 순으로 조회하여 'exceeded quota', 'Forbidden', 'ResourceQuota' 등 쿼터 관련 오류를 식별합니다.
3. namespace `<namespace>`의 Pod 리소스를 나열하고 리소스 요청을 집계하여 주요 리소스 소비자를 식별합니다.
4. namespace `<namespace>`에서 ResourceQuota `<quota-name>`을 조회하고 리소스 쿼터 구성을 확인하여 쿼터 제한과 범위를 검증합니다.
5. 쿼터가 제한에 도달하게 한 최근 리소스 생성 또는 스케일링 작업을 Deployment 및 HPA 스케일링 이력을 확인하여 검증합니다.
6. namespace `<namespace>`의 모든 리소스를 나열하고 쿼터를 소비하는 미사용 또는 불필요한 리소스를 확인합니다.

## 진단

1. 플레이북의 Namespace 이벤트를 분석하여 쿼터 관련 실패를 식별합니다. "exceeded quota" 또는 "Forbidden"을 보여주는 이벤트는 어떤 작업이 쿼터 제한으로 실패했는지 나타냅니다.

2. 이벤트가 Pod 쿼터 도달(Pod 수가 제한)을 나타내면, 플레이북에서 실행 중인 Pod 수를 식별합니다. 이것이 예상 워크로드 크기를 나타내는지 또는 고아 Pod, 실패한 Job, 완료된 Pod가 불필요하게 쿼터를 소비하는지 판단합니다.

3. 이벤트가 CPU 또는 메모리 요청 쿼터 도달을 나타내면, 플레이북의 Pod 리소스 요청을 분석합니다. 불균형적으로 큰 리소스 요청을 가진 Pod를 식별합니다.

4. 이벤트가 HPA 스케일링 활동과 상관되면, 오토스케일러가 레플리카를 추가하려 했지만 쿼터 제한에 도달한 것입니다. 플레이북에서 HPA 상태를 확인하여 현재 대비 원하는 레플리카를 확인합니다.

5. 이벤트가 최근 배포 또는 Job 실행과 상관되면, 해당 새 워크로드가 쿼터 사용량을 제한까지 밀어올린 것입니다.

6. 명확한 트리거 이벤트가 없으면, 점진적 증가를 통해 쿼터가 제한에 도달한 것입니다. 플레이북의 현재 사용량 분석(각 리소스 유형의 사용량 대 하드 제한)을 비교하여 어떤 리소스가 제약되는지 식별합니다.

7. 쿼터가 올바르게 크기 조정되었지만 완전히 사용된 경우, Namespace에 실제로 더 많은 용량이 필요한지 또는 워크로드 리소스 요청이 과도하게 프로비저닝되었는지 평가합니다. 완료된 Job 또는 실패한 Pod를 정리하여 쿼터를 회수할 수 있는지 고려합니다.
