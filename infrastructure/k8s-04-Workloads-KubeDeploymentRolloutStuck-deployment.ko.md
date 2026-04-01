---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/04-Workloads/KubeDeploymentRolloutStuck-deployment.md)'
role: SRE / K8s Incident Response
origin: scoutflo
tags:
- capacity
- deployment
- infrastructure
- k8s-deployment
- k8s-namespace
- k8s-pod
- kubedeploymentrolloutstuck
- kubernetes
- pipeline
- sts
- workloads
---

---
title: Kube Deployment Rollout Stuck
weight: 48
categories: [kubernetes, deployment]
---

# Deployment 롤아웃 중단 (KubeDeploymentRolloutStuck)

## 의미

Deployment 롤아웃이 중단되어 진행되지 않는 상태입니다(KubeDeploymentRolloutStuck 알림 발생). 새 Pod가 진행 데드라인 내에 Ready 상태가 될 수 없어 Deployment 완료가 방해됩니다. Deployment의 Progressing Condition이 False로 표시되고, 이전 Pod가 교체되지 않으며, 새 버전이 완전히 배포되지 않습니다. 애플리케이션 업데이트에 영향을 미치며, 새 버전이 배포되지 않고, 롤아웃이 차단되며, 혼합 버전 상태가 존재할 수 있습니다.

## 영향

KubeDeploymentRolloutStuck 알림이 발생하며, Deployment를 완료할 수 없습니다. 새 버전이 부분적으로 또는 전혀 배포되지 않고, 이전 Pod가 계속 실행됩니다. 버전 불일치 가능성이 있으며, 기능 릴리스가 차단되고, 버그 수정이 적용되지 않습니다. CI/CD 파이프라인이 중단되며, 수동 개입이 필요합니다.

## 플레이북

1. namespace `<namespace>`에서 Deployment `<deployment-name>`을 조회하고 롤아웃 상태 및 Condition을 확인합니다.

2. 새 ReplicaSet을 식별하고 Pod가 Ready 상태가 되지 않는 이유를 확인합니다.

3. 새 ReplicaSet의 Pod를 조회하고 상태를 확인합니다(Pending, CrashLoopBackOff, ImagePullBackOff).

4. 실패하는 Pod의 이벤트를 조회하여 구체적인 실패 원인을 파악합니다.

5. 새 Pod에서 Readiness Probe가 실패하는지 확인합니다.

6. 리소스 요청이 클러스터 용량으로 충족될 수 있는지 확인합니다.

7. PodDisruptionBudget이 롤아웃을 차단하는지 확인합니다.

## 진단

새 Pod 실패를 분류하여 분석합니다: CrashLoopBackOff는 애플리케이션 또는 설정 문제를 나타내고, Pending은 리소스 또는 스케줄링 문제를 나타내며, ImagePullBackOff는 이미지 문제를 나타냅니다. Pod 상태를 근거로 사용합니다.

Readiness Probe 설정을 확인하고 Probe가 애플리케이션 시작 시간에 적합한지 검증합니다. Probe 설정과 애플리케이션 시작 메트릭을 근거로 사용합니다.

새 이미지가 올바르고, 접근 가능하며, 기능적인지 이미지 태그와 Pull 상태를 확인하여 검증합니다. 이미지 설정과 Pull 이벤트를 근거로 사용합니다.

새 Pod 스펙과 이전 작동하던 Pod를 비교하여 실패를 유발할 수 있는 설정 변경을 식별합니다. Deployment 리비전 차이를 근거로 사용합니다.

새 Pod가 Ready 상태가 되기 전에 이전 Pod가 종료되는 것을 방해하는 PDB 위반을 확인합니다. PDB 상태와 Eviction 이벤트를 근거로 사용합니다.

지정된 시간 범위 내에서 상관관계를 찾을 수 없는 경우: Deployment를 이전 작동 버전으로 롤백하고, 새 버전 문제를 수정하고, 수정 사항으로 재배포하고, 시작이 정당하게 느린 경우 진행 데드라인을 늘리고, Deployment 전략(Rolling vs Recreate)을 검토합니다.
